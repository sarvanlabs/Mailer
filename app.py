# SPDX-License-Identifier: MIT
###
# This file is part of Sarvan Email Unsubscribe Service and is hosted in AWS lambda service under the name
# "email_unsubscribe_handler". This service handles unsubscribe requests from email links and records them in an S3 bucket.
# 
# ###



import os, json, time, hmac, hashlib, base64, urllib.parse
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from zoneinfo import ZoneInfo 

s3 = boto3.client("s3")

BUCKET = os.environ["BUCKET_NAME"]               # e.g. "sarvanlabs-unsubs-us-east-1"
PREFIX = os.environ.get("KEY_PREFIX", "unsubs/") # e.g. "unsubs/"
HMAC_SECRET = os.environ.get("HMAC_SECRET", "")  # optional: if empty, signature check is skipped

HTML_OK = b"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Unsubscribed &bull; SarvanLabs</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' fill='%231b1f2a'/%3E%3Cpath d='M18 34l8 8 20-20' stroke='%23ffffff' stroke-width='6' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E" />
  <style>
    :root{
      --bg:#0f1220; --bg-soft:#12162a; --card:#151a31; --text:#e7ecff; --muted:#a9b2d6;
      --brand:#6c8bff; --brand-2:#7ee7ff; --ring: rgba(124,139,255,.35);
      --ok:#22c55e; --shadow: 0 10px 30px rgba(0,0,0,.35), 0 2px 10px rgba(108,139,255,.12);
      --radius: 16px;
    }
    @media (prefers-color-scheme: light) {
      :root{
        --bg:#f7f8ff; --bg-soft:#eef1ff; --card:#ffffff; --text:#0c1020; --muted:#4a5677;
        --shadow: 0 8px 24px rgba(18,24,40,.08), 0 2px 8px rgba(18,24,40,.06);
      }
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{
      margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, Helvetica, sans-serif;
      color:var(--text); background: radial-gradient(1200px 800px at 10% 10%, rgba(108,139,255,.20), transparent 40%),
                            radial-gradient(1000px 700px at 100% 0%, rgba(126,231,255,.12), transparent 45%),
                            var(--bg);
      display:flex; align-items:center; justify-content:center; padding:24px;
    }
    .wrap{width:100%; max-width:760px}
    .nav{display:flex; align-items:center; gap:10px; margin:0 auto 16px; justify-content:center; text-decoration:none; color:var(--text);}
    .logo{width:36px; height:36px; display:inline-block; border-radius:10px;
      background: linear-gradient(135deg, var(--brand), var(--brand-2));
      box-shadow: inset 0 0 12px rgba(255,255,255,.25), 0 8px 20px rgba(108,139,255,.3);}
    .brand{font-weight:700; letter-spacing:.3px; font-size:18px}
    .card{background:linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,.00)), var(--card);
      border:1px solid rgba(124,139,255,.14); border-radius:var(--radius); box-shadow:var(--shadow); padding:28px 26px;}
    .hero{display:flex; gap:22px; align-items:center; justify-content:flex-start; margin-bottom:6px;}
    .badge{width:56px; height:56px; border-radius:14px; display:grid; place-items:center;
      background: radial-gradient(120% 120% at 20% 20%, rgba(34,197,94,.35), transparent 55%), rgba(34,197,94,.10);
      border: 1px solid rgba(34,197,94,.35); box-shadow: inset 0 0 14px rgba(34,197,94,.25);}
    .check{width:30px; height:30px}
    h1{margin:0; font-size:28px; line-height:1.15; letter-spacing:.2px}
    p.lead{margin:8px 0 0; color:var(--muted); font-size:16px}
    .panel{margin-top:18px; padding:18px; border-radius:12px; background:var(--bg-soft);
      border:1px dashed rgba(124,139,255,.25); color:var(--muted); font-size:14px;}
    .actions{margin-top:22px; display:flex; gap:12px; flex-wrap:wrap}
    .btn{appearance:none; border:none; cursor:pointer; text-decoration:none; padding:12px 16px; border-radius:12px; font-weight:600; font-size:15px; line-height:1;
      background:linear-gradient(135deg, var(--brand), var(--brand-2)); color:white; box-shadow: 0 6px 20px var(--ring);
      transition: transform .12s ease, box-shadow .12s ease, opacity .2s;}
    .btn:hover{transform: translateY(-1px); box-shadow:0 10px 26px var(--ring)}
    .btn.secondary{background:transparent; color:var(--text); border:1px solid rgba(124,139,255,.35)}
    .footer{margin-top:18px; text-align:center; color:var(--muted); font-size:13px}
    .kbd{font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background:rgba(124,139,255,.15);
      padding:2px 6px; border-radius:6px; border:1px solid rgba(124,139,255,.25); color:var(--text)}
    .sr-only{position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); border:0}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="card" role="status" aria-live="polite">
      <div class="hero">
        <div class="badge" aria-hidden="true">
          <svg class="check" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M20 7L9 18l-5-5" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <h1>You are unsubscribed</h1>
          <p class="lead">We have recorded your request and will not send future promotional emails to this address.</p>
        </div>
      </div>

      <div class="panel">
        Tip: If this was a mistake, reply to any previous email or contact us via the site.
        For your records, you can close this tab now. Press <span class="kbd">Ctrl</span> + <span class="kbd">W</span>.
      </div>
    </section>

    <p class="footer">&copy; <span id="y"></span> Sarvan Labs. All rights reserved.</p>
  </main>

  <script>
    document.getElementById('y').textContent = new Date().getFullYear();
  </script>
</body>
</html>"""

HTML_BAD = b"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Invalid request &bull; SarvanLabs</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <style>
    :root{
      --bg:#0f1220; --bg-soft:#12162a; --card:#151a31; --text:#e7ecff; --muted:#a9b2d6;
      --brand:#6c8bff; --brand-2:#7ee7ff; --ring: rgba(124,139,255,.35);
      --warn:#f97316; --shadow: 0 10px 30px rgba(0,0,0,.35), 0 2px 10px rgba(108,139,255,.12);
      --radius: 16px;
    }
    @media (prefers-color-scheme: light) {
      :root{
        --bg:#f7f8ff; --bg-soft:#eef1ff; --card:#ffffff; --text:#0c1020; --muted:#4a5677;
        --shadow: 0 8px 24px rgba(18,24,40,.08), 0 2px 8px rgba(18,24,40,.06);
      }
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{
      margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, Helvetica, sans-serif;
      color:var(--text); background: radial-gradient(1200px 800px at 10% 10%, rgba(108,139,255,.20), transparent 40%),
                         radial-gradient(1000px 700px at 100% 0%, rgba(126,231,255,.12), transparent 45%),
                         var(--bg);
      display:flex; align-items:center; justify-content:center; padding:24px;
    }
    .wrap{width:100%; max-width:760px}
    .nav{display:flex; align-items:center; gap:10px; margin:0 auto 16px; justify-content:center; text-decoration:none; color:var(--text);}
    .logo{width:36px; height:36px; display:inline-block; border-radius:10px;
      background: linear-gradient(135deg, var(--brand), var(--brand-2));
      box-shadow: inset 0 0 12px rgba(255,255,255,.25), 0 8px 20px rgba(108,139,255,.3);}
    .brand{font-weight:700; letter-spacing:.3px; font-size:18px}
    .card{background:linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,.00)), var(--card);
      border:1px solid rgba(124,139,255,.14); border-radius:var(--radius); box-shadow:var(--shadow); padding:28px 26px;}
    .hero{display:flex; gap:22px; align-items:center; justify-content:flex-start; margin-bottom:6px;}
    .badge{width:56px; height:56px; border-radius:14px; display:grid; place-items:center;
      background: radial-gradient(120% 120% at 20% 20%, rgba(249,115,22,.35), transparent 55%), rgba(249,115,22,.10);
      border: 1px solid rgba(249,115,22,.45); box-shadow: inset 0 0 14px rgba(249,115,22,.25);}
    .icon{width:30px; height:30px}
    h1{margin:0; font-size:28px; line-height:1.15; letter-spacing:.2px}
    p.lead{margin:8px 0 0; color:var(--muted); font-size:16px}
    .panel{margin-top:18px; padding:18px; border-radius:12px; background:var(--bg-soft);
      border:1px dashed rgba(124,139,255,.25); color:var(--muted); font-size:14px;}
    .actions{margin-top:22px; display:flex; gap:12px; flex-wrap:wrap}
    .btn{appearance:none; border:none; cursor:pointer; text-decoration:none; padding:12px 16px; border-radius:12px; font-weight:600; font-size:15px; line-height:1;
      background:linear-gradient(135deg, var(--brand), var(--brand-2)); color:white; box-shadow: 0 6px 20px var(--ring);
      transition: transform .12s ease, box-shadow .12s ease, opacity .2s;}
    .btn:hover{transform: translateY(-1px); box-shadow:0 10px 26px var(--ring)}
    .btn.secondary{background:transparent; color:var(--text); border:1px solid rgba(124,139,255,.35)}
    .footer{margin-top:18px; text-align:center; color:var(--muted); font-size:13px}
    .kbd{font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background:rgba(124,139,255,.15);
      padding:2px 6px; border-radius:6px; border:1px solid rgba(124,139,255,.25); color:var(--text)}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="card" role="status" aria-live="polite">
      <div class="hero">
        <div class="badge" aria-hidden="true">
          <svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 8v5" stroke="white" stroke-width="2.5" stroke-linecap="round"></path>
            <circle cx="12" cy="16.5" r="1.25" fill="white"></circle>
            <circle cx="12" cy="12" r="9" stroke="white" stroke-width="1.5" fill="none"></circle>
          </svg>
        </div>
        <div>
          <h1>Invalid or expired link</h1>
          <p class="lead">We could not verify this unsubscribe request. The link may be malformed, expired, or already used.</p>
        </div>
      </div>

      <div class="panel">
        Tip: Try clicking the unsubscribe link again from the latest email, or contact us for help.
      </div>
    </section>

    <p class="footer">&copy; <span id="y"></span> Sarvan Labs. All rights reserved.</p>
  </main>

  <script>
    document.getElementById('y').textContent = new Date().getFullYear();
  </script>
</body>
</html>"""


HTML_ERR = b"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Server error - SarvanLabs</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <style>
    :root{
      --bg:#0f1220; --bg-soft:#12162a; --card:#151a31; --text:#e7ecff; --muted:#a9b2d6;
      --brand:#6c8bff; --brand-2:#7ee7ff; --ring: rgba(124,139,255,.35);
      --error:#ef4444; --shadow: 0 10px 30px rgba(0,0,0,.35), 0 2px 10px rgba(108,139,255,.12);
      --radius: 16px;
    }
    @media (prefers-color-scheme: light) {
      :root{
        --bg:#f7f8ff; --bg-soft:#eef1ff; --card:#ffffff; --text:#0c1020; --muted:#4a5677;
        --shadow: 0 8px 24px rgba(18,24,40,.08), 0 2px 8px rgba(18,24,40,.06);
      }
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{
      margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, Helvetica, sans-serif;
      color:var(--text); background: radial-gradient(1200px 800px at 10% 10%, rgba(108,139,255,.20), transparent 40%),
                         radial-gradient(1000px 700px at 100% 0%, rgba(126,231,255,.12), transparent 45%),
                         var(--bg);
      display:flex; align-items:center; justify-content:center; padding:24px;
    }
    .wrap{width:100%; max-width:760px}
    .nav{display:flex; align-items:center; gap:10px; margin:0 auto 16px; justify-content:center; text-decoration:none; color:var(--text);}
    .logo{width:36px; height:36px; display:inline-block; border-radius:10px;
      background: linear-gradient(135deg, var(--brand), var(--brand-2));
      box-shadow: inset 0 0 12px rgba(255,255,255,.25), 0 8px 20px rgba(108,139,255,.3);}
    .brand{font-weight:700; letter-spacing:.3px; font-size:18px}
    .card{background:linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,.00)), var(--card);
      border:1px solid rgba(124,139,255,.14); border-radius:var(--radius); box-shadow:var(--shadow); padding:28px 26px;}
    .hero{display:flex; gap:22px; align-items:center; justify-content:flex-start; margin-bottom:6px;}
    .badge{width:56px; height:56px; border-radius:14px; display:grid; place-items:center;
      background: radial-gradient(120% 120% at 20% 20%, rgba(239,68,68,.35), transparent 55%), rgba(239,68,68,.10);
      border: 1px solid rgba(239,68,68,.45); box-shadow: inset 0 0 14px rgba(239,68,68,.25);}
    .icon{width:30px; height:30px}
    h1{margin:0; font-size:28px; line-height:1.15; letter-spacing:.2px}
    p.lead{margin:8px 0 0; color:var(--muted); font-size:16px}
    .panel{margin-top:18px; padding:18px; border-radius:12px; background:var(--bg-soft);
      border:1px dashed rgba(124,139,255,.25); color:var(--muted); font-size:14px;}
    .actions{margin-top:22px; display:flex; gap:12px; flex-wrap:wrap}
    .btn{appearance:none; border:none; cursor:pointer; text-decoration:none; padding:12px 16px; border-radius:12px; font-weight:600; font-size:15px; line-height:1;
      background:linear-gradient(135deg, var(--brand), var(--brand-2)); color:white; box-shadow: 0 6px 20px var(--ring);
      transition: transform .12s ease, box-shadow .12s ease, opacity .2s;}
    .btn:hover{transform: translateY(-1px); box-shadow:0 10px 26px var(--ring)}
    .btn.secondary{background:transparent; color:var(--text); border:1px solid rgba(124,139,255,.35)}
    .footer{margin-top:18px; text-align:center; color:var(--muted); font-size:13px}
    .kbd{font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background:rgba(124,139,255,.15);
      padding:2px 6px; border-radius:6px; border:1px solid rgba(124,139,255,.25); color:var(--text)}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="card" role="status" aria-live="polite">
      <div class="hero">
        <div class="badge" aria-hidden="true">
          <svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 8v5" stroke="white" stroke-width="2.5" stroke-linecap="round"></path>
            <circle cx="12" cy="16.5" r="1.25" fill="white"></circle>
            <circle cx="12" cy="12" r="9" stroke="white" stroke-width="1.5" fill="none"></circle>
          </svg>
        </div>
        <div>
          <h1>Something went wrong</h1>
          <p class="lead">Please try again in about 30 minutes. If the problem persists, contact support.</p>
        </div>
      </div>

      <div class="panel">
        Tip: You can return to the site or reach out to our team for assistance.
      </div>
    </section>

    <p class="footer">&copy; <span id="y"></span> Sarvan Labs. All rights reserved.</p>
  </main>

  <script>
    /* no scripts needed for error page */
  </script>
</body>
</html>"""

# def _verify_signature(email: str, signature: str) -> bool:
#     if not HMAC_SECRET:
#         return True  # signature enforcement disabled
#     mac = hmac.new(HMAC_SECRET.encode("utf-8"), msg=email.encode("utf-8"), digestmod=hashlib.sha256)
#     expected = base64.urlsafe_b64encode(mac.digest()).decode("utf-8").rstrip("=")
#     return hmac.compare_digest(expected, signature or "")

def _ok(body_bytes: bytes, content_type="text/html"):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            "Cache-Control": "no-store",
            "Access-Control-Allow-Origin": "*",
        },
        "body": body_bytes.decode("utf-8"),
        "isBase64Encoded": False,
    }

def _bad(body_bytes: bytes):
    return {
        "statusCode": 400,
        "headers": {
            "Content-Type": "text/html",
            "Cache-Control": "no-store",
            "Access-Control-Allow-Origin": "*",
        },
        "body": body_bytes.decode("utf-8"),
        "isBase64Encoded": False,
    }

def _resp(code, body_bytes):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "text/html",
            "Cache-Control": "no-store",
            "Access-Control-Allow-Origin": "*",
        },
        "body": body_bytes.decode("utf-8"),
        "isBase64Encoded": False,
    }

def b64url_to_bytes(s: str) -> bytes:
    s += "=" * ((4 - len(s) % 4) % 4)  # pad
    return base64.urlsafe_b64decode(s.encode())

def verify_token(token: str, secret: str):
    """
    Returns dict payload if valid; otherwise None.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        head_b  = b64url_to_bytes(parts[0])
        body_b  = b64url_to_bytes(parts[1])
        sig_in  = b64url_to_bytes(parts[2])

        header = json.loads(head_b.decode("utf-8"))
        if header.get("alg") != "HS256":  # only support HS256
            return None

        signing_input = f"{parts[0]}.{parts[1]}".encode()
        sig_exp = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(sig_exp, sig_in):
            return None

        payload = json.loads(body_b.decode("utf-8"))
        now = int(time.time())
        if payload.get("nbf", 0) > now: return None
        if payload.get("exp", 0) < now: return None

        return payload
    except Exception:
        return _resp(500, HTML_ERR)

def handler(event, context):
    try:
        # Accept both GET querystring and POST JSON body
        email = None
        qs = event.get("queryStringParameters") or {}
        print("Query_paras::: ",qs)
        if "e" in qs:
            e = qs.get("e")

        # POST JSON {"email": "...", "signature": "..."}
        # if not email and event.get("body"):
        #     body = event["body"]
        #     if event.get("isBase64Encoded"):
        #         import base64 as b64
        #         body = b64.b64decode(body).decode("utf-8")
        #     try:
        #         payload = json.loads(body)
        #         email = payload.get("email")
        #         sig = payload.get("signature")
        #     except Exception:
        #         pass

        if not e:
            return _resp(HTML_BAD)

        payload = verify_token(e, HMAC_SECRET)  # HMAC_SECRET from env
        if not payload:
          return _resp(400, HTML_BAD)

        email = payload.get("e")
        if not email or "@" not in email:
          return _resp(400, HTML_BAD)

        # --- compute day-wise object key ---
        # Example: unsubs/20251023/unsubscribed_emails.json
        day = time.strftime("%Y%m%d", time.gmtime())
        OBJECT_KEY = f"{PREFIX}/unsubscribed_emails.json"
        # -----------------------------------

        dt_utc = datetime.now(timezone.utc)
        dt_ist = dt_utc.astimezone(ZoneInfo("Asia/Kolkata"))
        dt_ist_str = dt_ist.strftime("%Y-%m-%dT%H:%M:%S%z")
        # now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        rc = event.get("requestContext") or {}
        http = rc.get("http") or {}
        ip = http.get("sourceIp") or (rc.get("identity") or {}).get("sourceIp")
        hdrs = event.get("headers") or {}
        ua = hdrs.get("user-agent") or hdrs.get("User-Agent")

        # Try to fetch today's list (JSON array)
        unsubscribes = []
        try:
            resp = s3.get_object(Bucket=BUCKET, Key=OBJECT_KEY)
            body_bytes = resp["Body"].read()
            if body_bytes:
                unsubscribes = json.loads(body_bytes.decode("utf-8"))
                if not isinstance(unsubscribes, list):
                    # if somehow file is corrupt, reset to list
                    unsubscribes = []
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code == "NoSuchKey":
                # first unsubscribe of the day; start a new list
                unsubscribes = []
            else:
                print("S3 get_object error:", repr(e))
                return _resp(500, HTML_ERR)


        record = {
            "email": email,
            "unsubscribed": True,
            "timestamp": dt_ist_str,
            "source": "unsubscribe_email_link",
            "ip": ip,
            "user_agent": ua,
            "email_type": payload.get("email_type"),
            "campaign_month": payload.get("campaign_month")
        }
        # Append new unsubscribe
        unsubscribes.append(record)

        s3.put_object(
            Bucket=BUCKET,
            Key=OBJECT_KEY,
            Body=json.dumps(unsubscribes, indent=2).encode("utf-8"),
            ContentType="application/json",
            ServerSideEncryption="AES256",
            Metadata={"type": "unsubscribe"}
        )

        return _ok(HTML_OK)
    except Exception as ex:
        # Log the full stack to CloudWatch so you can see it
        print("ERROR:", str(ex))
        print(traceback.format_exc())
        return _resp(500, HTML_ERR)
