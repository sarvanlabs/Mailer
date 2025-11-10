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