import os
import random
import re
import ssl
import smtplib
import socket
import time
import random
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import requests
import pymysql  # <-- use PyMySQL
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime, timezone

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
import utils
import json, time, hmac, hashlib, base64, secrets


SENDER = "sarvanlabs@mail.sarvanlabs.com"
SENDERNAME = "Sarvan Labs"
REPLYTO = "contact@sarvanlabs.com"

MAX_RATE = 14           # emails per second
MAX_RETRIES = 5         # transient retries
BASE_BACKOFF = 0.5      # seconds (capped below)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

WORDS_BLOCKLIST_IN_ADDRESS = set([
    "ca","fca","cs","mca","legal","roc","fcs","adv"
])

# --------------------
# Reconnecting SMTP wrapper
# --------------------
class ReconnectingSMTP:
    """
    Keeps one SMTP TLS session alive. If the socket drops, it reconnects and retries.
    """
    def __init__(self, host, port, user, pwd, timeout=30):
        self.host = (host or "").strip()
        self.port = int(port)
        self.user = user
        self.pwd = pwd
        self.timeout = timeout
        self.server = None

    def _connect(self):
        if not self.host or self.host.startswith("."):
            raise ValueError(f"Invalid SMTP host '{self.host}'. Set HOST/SES_HOST correctly.")
        srv = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
        try:
            srv.ehlo()
            ctx = ssl.create_default_context()
            srv.starttls(context=ctx)
            srv.ehlo()
            srv.login(self.user, self.pwd)
            srv.noop()
        except Exception:
            try:
                srv.quit()
            except Exception:
                try:
                    srv.close()
                except Exception:
                    pass
            raise
        self.server = srv

    def __enter__(self):
        attempts = 0
        while True:
            try:
                self._connect()
                return self
            except Exception:
                attempts += 1
                if attempts >= 3:
                    raise
                time.sleep(0.5 * attempts)

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.server:
                self.server.quit()
        except Exception:
            try:
                self.server.close()
            except Exception:
                pass
        self.server = None

    def _ensure(self):
        if self.server is None:
            self._connect()

    def send_with_retry(self, sender, to_email, msg, max_retries=5, base_backoff=0.5):
        attempt = 0
        while True:
            try:
                self._ensure()
                self.server.sendmail(sender, [to_email], msg.as_string())
                return
            except Exception as e:
                transient = False
                msg_txt = str(e).lower()
                if isinstance(e, smtplib.SMTPResponseException) and getattr(e, "smtp_code", None) in (421, 451, 454):
                    transient = True
                if isinstance(e, (smtplib.SMTPServerDisconnected,
                                  smtplib.SMTPConnectError,
                                  smtplib.SMTPHeloError,
                                  smtplib.SMTPDataError,
                                  socket.timeout)):
                    transient = True
                if "please run connect() first" in msg_txt:
                    transient = True

                attempt += 1
                try:
                    self._connect()
                except Exception:
                    pass

                if not transient or attempt > max_retries:
                    raise

                backoff = min(base_backoff * (2 ** (attempt - 1)), 8.0)
                time.sleep(backoff + random.uniform(0, 0.2))

# --------------------
# Rate limiter
# --------------------
class RateLimiter:
    def __init__(self, rate_per_sec: int):
        self.rate = rate_per_sec
        self.window_start = time.monotonic()
        self.count = 0
    def wait(self):
        now = time.monotonic()
        elapsed = now - self.window_start
        if elapsed >= 1.0:
            self.window_start = now
            self.count = 0
        if self.count >= self.rate:
            sleep_for = 1.0 - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
            self.window_start = time.monotonic()
            self.count = 0
        self.count += 1

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def make_token(
    email: str,
    secret: str,
    email_type: str | None = None,
    campaign_month: str | None = None,
) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "e": email.lower(),
        "iat": now,
        "nbf": now,
        #"exp": now + 1 * 60,
        "nonce": secrets.token_urlsafe(12),
    }
    if email_type: payload["email_type"] = email_type
    if campaign_month:   payload["campaign_month"] = campaign_month

    head = b64url(json.dumps(header, separators=(",", ":"), ensure_ascii=True).encode())
    body = b64url(json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode())

    signing_input = f"{head}.{body}".encode()
    sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    token = f"{head}.{body}.{b64url(sig)}"
    return token


def fetch_emails(start_date, end_date, engine=None):
    """
    Pull companies with incorporation date in [start_date, end_date).
    """
    try:
        condition = f"""cmn.Class_of_Company = 'Private' 
        and cmn.Whether_Listed_or_not = 'Unlisted'
        and cmn.Paid_up_Capital_Rs < 2000000
        and cmn.is_unsubscribed = 0
        and cmn.Date_of_Incorporation >= '{start_date}' AND cmn.Date_of_Incorporation < '{end_date}'
        and cmn.Company_Name not like '%technology%';"""
        DB_QUERY_FETCH_EMAILS = f"""SELECT cmn.Company_Name, 
        cmn.Email_Id, 
        cmn.is_unsubscribed
        from company_master_new cmn where {condition}"""
        print("DB_QUERY_FETCH_EMAILS ::: ",DB_QUERY_FETCH_EMAILS)
        return pd.read_sql(DB_QUERY_FETCH_EMAILS, con=engine)
    except Exception as e:
        print(f"Error fetching emails: {e}")
        

def is_valid_email(addr: str) -> bool:
    return bool(addr) and EMAIL_REGEX.match(addr) is not None

def build_message(to_email: str, subject: str, body: str) -> MIMEMultipart:
    msg = MIMEMultipart('alternative')
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = to_email
    msg['Subject'] = subject.strip()
    msg['Date'] = email.utils.formatdate(localtime=False, usegmt=True)
    msg['Message-ID'] = email.utils.make_msgid(domain=SENDER.split("@")[-1])
    msg['Reply-To'] = email.utils.formataddr((SENDERNAME, REPLYTO))
    msg.add_header('X-SES-CONFIGURATION-SET', "noreply")
    msg.add_header('X-SES-MESSAGE-TAGS', "noreply=null")
    msg['List-Unsubscribe'] = f"<mailto:{SENDER}?subject=Unsubscribe>"
    # msg.attach(MIMEText(body, "plain", "utf-8"))
    msg.attach(MIMEText(body, "html", "utf-8"))
    return msg


def get_connection():
    sm = utils.SecretCache(region="us-east-1")
    db_creds = sm.get("MySQL_local")
    DB_HOST = db_creds.get("host")
    DB_USER = db_creds.get("user")
    DB_PASSWORD = db_creds.get("password")
    DB_DATABASE_NAME = db_creds.get("database")
    print("Establishing database connection...")
    print(f"DB Host: {DB_HOST}, DB User: {DB_USER}, DB Name: {DB_DATABASE_NAME}")
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE_NAME
    )
    return connection


# --------------------
# Email HTML
# --------------------

def render_text(recipient_name, company_name, unsub_url):
    return f"""\
    Hi {recipient_name},

    I’m reaching out from Sarvan Labs, where we help businesses achieve more with AI-powered automation.

    Our solutions are designed to reduce operational costs, improve productivity, and accelerate outcomes — enabling teams to focus on what truly drives growth.

    By integrating AI into your existing processes, organizations often see:

        1. Up to 50% cost reduction

        2. Significant time savings

        3. Smarter decision-making through AI insights

If your team is spending time on repetitive steps, we can help automate those processes so you save cost and deliver faster—without disrupting how your people already work. 

You can reach us via Whatsapp on +91-8218842490 or simply reply to this email or visit us at https://www.sarvanlabs.com to learn more.

Best Regards,
Sarvan Labs

To Unsubscribe: {unsub_url}"""

def render_html_simple(recipient_name, company_name, unsub_url):
    return f"""\
<!doctype html>
<html>
<body style="margin:0;padding:14px;font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#111; font-size:14px; line-height:1.45;">
    <div style="max-width:700px;white-space:pre-wrap;">
        <p>Hi {recipient_name},</p>

        <p>I’m reaching out from Sarvan Labs, where we help businesses achieve more with AI-powered automation.</p>

        <p>Our solutions are designed to reduce operational costs, improve productivity, and accelerate outcomes — enabling teams to focus on what truly drives growth.</p

        <p>By integrating AI into your existing processes, organizations often see:</p>
        <ol>
            <li>Up to 50% cost reduction</li>

            <li>Significant time savings</li>
            
            <li>Smarter decision-making through AI insights</li>
        </ol>
        <p>If your team is spending time on repetitive steps, we can help automate those processes so you save cost and deliver faster—without disrupting how your people already work.</p>

        <div class="cta">
            <p>
            You can reach us via WhatsApp at <a class="textlink" href="https://wa.me/918218842490">+91-8218842490</a>, simply reply to this email, or visit us at
            <a class="textlink" href="https://www.sarvanlabs.com">sarvanlabs.com</a> to learn more.
            </p>
        </div>

        <p class="footer">
            Best Regards,<br/>
        <strong>Sarvan Labs</strong>
        </p>

        <hr/>

To Unsubscribe: <a href="{unsub_url}" style="color:#0a66c2;text-decoration:underline;">Unsubscribe</a>
    </div>
</body>
</html>
"""


def render_html(recipient_name, company_name, unsub_url):
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sarvan Labs — AI Automation, Security, DevOps & Engineering Enablement</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    .container {{ max-width: 680px; margin: 0 auto; font-family: -apple-system, system-ui, Segoe UI, Roboto, Arial, sans-serif; color: #0f172a; line-height: 1.6; }}
    .card {{ background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; }}
    .btn {{ display: inline-block; padding: 12px 18px; border-radius: 10px; text-decoration: none; background: #111827; color: #ffffff; }}
    .muted {{ color: #6b7280; font-size: 12px; }}
    .pill {{ display: inline-block; padding: 4px 10px; border: 1px solid #e5e7eb; border-radius: 999px; margin-right: 6px; font-size: 12px; color: #374151; }}
    ul {{ padding-left: 18px; margin: 0 0 14px 0; }}
    hr {{ border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
  </style>
</head>
<body style="background:#f8fafc; padding: 24px;">
  <div class="container">
    <div class="card">
      <p>Hi {recipient_name},</p>

      <p><strong>Sarvan Labs</strong> helps teams to eliminate manual work and accelerate delivery using practical <strong>AI automation</strong>, strong <strong>security foundations</strong>, and robust <strong>DevOps & engineering enablement</strong>. Our productized services plug into your existing tools and start creating impact quickly.</p>

      <p><span class="pill">AI Automation </span><span class="pill">Security </span><span class="pill">DevOps </span><span class="pill">Engineering Enablement </span></p>
      <h2 style="margin:16px 0 8px;">Our Expertise</h2>
      <h3 style="margin:16px 0 8px;">AI Automation</h3>
      <ul>
        <li><strong>AI Assistants & Agentic Workflows</strong> — inbox triage, proposal drafts, lead qualification, customer support, SOP copilots.</li>
        <li><strong>Document &amp; Data Automation</strong> — parse PDFs/Excel/emails, build secure search/RAG over your knowledge base.</li>
        <li><strong>Code &amp; PR Review Bots</strong> — summaries, risk flags, quality checks to speed up reviews.</li>
        <li><strong>Meeting Notes &amp; Actions</strong> — automatic summaries, owners, and task pushes to your tools.</li>
      </ul>

      <h3 style="margin:16px 0 8px;">Security Architecture</h3>
      <ul>
        <li><strong>Identity &amp; Access</strong> — least-privilege IAM, secrets management, key rotation, safe data boundaries.</li>
        <li><strong>App &amp; Data Guardrails</strong> — prompt hardening, PII handling, allow/deny domains, full auditability.</li>
        <li><strong>Compliance-ready Controls</strong> — logging, evidence capture, and policy enforcement by default.</li>
      </ul>

      <h3 style="margin:16px 0 8px;">DevOps & Engineering Enablement</h3>
      <ul>
        <li><strong>CI/CD Acceleration</strong> — faster pipelines, quality gates, safe rollouts/rollbacks.</li>
        <li><strong>Kubernetes &amp; GitOps</strong> — sane defaults with Helm/ArgoCD, cost controls, environment parity.</li>
        <li><strong>Observability</strong> — SLOs, dashboards, alert hygiene, and golden signals you can trust.</li>
      </ul>

      <h3 style="margin:16px 0 8px;">How we work</h3>
      <ul>
        <li><strong>Fast start</strong> — identify a high-impact workflow and deliver the first automation quickly.</li>
        <li><strong>Integrate, not replace</strong> — connect with email, spreadsheets, chat, CRM/ERP, and your existing stack.</li>
        <li><strong>Measure outcomes</strong> — hours saved, errors reduced, faster cycle times, and clear ROI.</li>
        <li><strong>Ongoing improvements</strong> — iterate based on usage data and feedback.</li>
      </ul>

      <p>If your team is spending time on repetitive steps or copy-paste work, we can help automate those processes so you save cost and deliver faster—without disrupting how your people already work.</p>
      <p style="margin: 18px 0;">
        <a class="btn" href="https://wa.me/{918218842490}?text=Hi%20Sarvan%20Labs,%20I%27d%20like%20to%20learn%20how%20you%20can%20help%20us%20automate%20our%20workflows.%20From%20{company_name}" target="_blank" rel="noopener">Contact Us (WhatsApp)</a>
        &nbsp;&nbsp;
        <a class="btn" href="mailto:contact@sarvanlabs.com?subject=Lets Connect | SarvanLabs | {company_name}" target="_blank" rel="noopener">Reply via Email</a>
        &nbsp;&nbsp;
        <a class="btn" href="https://www.sarvanlabs.com" target="_blank" rel="noopener">Visit sarvanlabs.com</a>
      </p>
      <hr>
      <p class="muted">
        Sarvan Labs — AI Automation, Security, DevOps &amp; Engineering Enablement<br>
        Website: <a href="https://www.sarvanlabs.com" target="_blank" rel="noopener">www.sarvanlabs.com</a>
      </p>

      <p class="muted">
        To stop receiving these emails, you can <a href="{unsub_url}" target="_blank" rel="noopener">unsubscribe here</a>.
      </p>
    </div>
  </div>
</body>
</html>
"""


def send_email_to_company(row, smtp: "ReconnectingSMTP", limiter, blocked_emails_lower):
    emailid_raw = row.get("Email_Id", "")
    emailid = emailid_raw.strip()
    if not is_valid_email(emailid):
        return "skip_invalid"

    email_in_lower = emailid.lower()
    if email_in_lower in blocked_emails_lower:
        return "skip_blocked"

    if any(word in email_in_lower for word in WORDS_BLOCKLIST_IN_ADDRESS):
        return "skip_block_word"
    
    sm = utils.SecretCache(region="us-east-1")
    hmac_secret = sm.get("HMAC_SECRET").get("hmac")
    token = make_token(
                email_in_lower, hmac_secret,
                email_type="bulk_campaign",
                campaign_month="oct_2025",
            )
    link = f"https://unsubscribe.sarvanlabs.com/unsubscribe?e={token}"

    subjects = [
        "Cut Costs and Boost Productivity — The Smarter Way",
        "AI That Works for You — Save Time, Reduce Costs",
        "Work Smarter, Not Harder: Automate with AI",
        "Your Next Competitive Edge: AI Automation",
        "Achieve More in Less Time with AI-Powered Automation",
        "Unlock Growth Through Smart AI Automation",
        "Discover How AI Can Supercharge Your Business Efficiency",
        "Transform Your Business Efficiency with AI Automation",
        "Faster Operations, Lower Costs — Powered by AI",
        "See What AI Automation Can Do for Your Business",
    ]
    subject = random.choice(subjects)
    # body = render_html(row.get("Company_Name", ""), row.get("Company_Name", ""),link)
    body = render_html_simple(row.get("Company_Name", ""), row.get("Company_Name", ""),link)
    msg = build_message(emailid, subject, body)

    limiter.wait()  # pace to 14/sec
    try:
        print(f"Sending to {emailid}...")
        smtp.send_with_retry(SENDER, emailid, msg)
        return "sent"
    except Exception as e:
        print(f"Failed to send to {emailid}: {e}")
        return "failed"

def main(startdate, enddate):
    print("Starting run")
    conn = get_connection()

    df_emails = df = pd.DataFrame(
    [{"Company_Name": "abc", "Email_Id": "sarthakvashisth@outlook.com"}],
    columns=["Company_Name", "Email_Id"]) 
    # df_emails = fetch_emails(startdate,enddate,engine=conn)
    print(df_emails)
    limiter = RateLimiter(MAX_RATE)

    seen = set()
    sent = skipped = failed = 0
    sm = utils.SecretCache(region="us-east-1")
    smtp_creds = sm.get("SMTP_Creds")
    HOST = smtp_creds.get("HOST")
    PORT = int(smtp_creds.get("PORT"))
    USERNAME_SMTP = smtp_creds.get("USERNAME_SMTP")
    PASSWORD_SMTP = smtp_creds.get("PASSWORD_SMTP")
    print(f"SMTP Host: {HOST}, Port: {PORT}, Username: {USERNAME_SMTP}")
    with ReconnectingSMTP(HOST, PORT, USERNAME_SMTP, PASSWORD_SMTP) as smtp:
        for _, row in df_emails.iterrows():
            emailid = (row.get("Email_Id", "") or "").strip().lower()
            if not emailid or emailid in seen:
                skipped += 1
                continue
            status = send_email_to_company(row, smtp, limiter, "")
            if status == "sent":
                sent += 1
            elif status.startswith("skip"):
                skipped += 1
            else:
                failed += 1
            seen.add(emailid)

    print(f"Done. Sent={sent}, Skipped={skipped}, Failed={failed}")


if __name__ == "__main__":
    main("2023-01-15", "2023-01-20")