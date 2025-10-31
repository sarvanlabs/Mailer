MARKETING_TYPE_HTML_BASED_EMAIL = f"""\
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
        <a class="btn" href="mailto:contact@sarvanlabs.com?subject=Automation%20opportunity%20at%20{company_name}" target="_blank" rel="noopener">Reply via Email</a>
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