import os
import resend
from datetime import datetime

resend.api_key = os.environ["RESEND_API_KEY"]


def _score_color(score):
    if score >= 9:
        return "#22c55e"
    if score >= 7:
        return "#f59e0b"
    return "#ef4444"


def _build_card(opp, index):
    score = opp["scores"]["overall"]
    color = _score_color(score)
    return f"""
    <div style="background:#1e2130;border:1px solid #2d3148;border-radius:14px;padding:28px;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <span style="background:#2d3148;color:#8892b0;font-size:12px;padding:4px 12px;border-radius:20px;font-family:monospace;">r/{opp['subreddit']}</span>
            <span style="background:{color}22;color:{color};font-size:15px;font-weight:700;padding:4px 14px;border-radius:20px;">
                {score}/10
            </span>
        </div>

        <h2 style="color:#ffffff;font-size:22px;font-weight:700;margin:0 0 10px 0;line-height:1.3;">
            {opp['business_idea']}
        </h2>
        <p style="color:#6b7a99;font-size:14px;font-style:italic;margin:0 0 20px 0;border-left:3px solid #DDA01D;padding-left:12px;">
            "{opp['pain_point']}"
        </p>

        <table style="width:100%;border-collapse:collapse;">
            <tr>
                <td style="padding:10px 0;border-bottom:1px solid #2d3148;vertical-align:top;width:30%;">
                    <span style="color:#DDA01D;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">How to build it</span>
                </td>
                <td style="padding:10px 0 10px 16px;border-bottom:1px solid #2d3148;vertical-align:top;">
                    <span style="color:#c8d0e0;font-size:14px;">{opp['how_to_build']}</span>
                </td>
            </tr>
            <tr>
                <td style="padding:10px 0;border-bottom:1px solid #2d3148;vertical-align:top;">
                    <span style="color:#DDA01D;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Revenue model</span>
                </td>
                <td style="padding:10px 0 10px 16px;border-bottom:1px solid #2d3148;vertical-align:top;">
                    <span style="color:#c8d0e0;font-size:14px;">{opp['revenue_model']}</span>
                </td>
            </tr>
            <tr>
                <td style="padding:10px 0;vertical-align:top;">
                    <span style="color:#DDA01D;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Why now</span>
                </td>
                <td style="padding:10px 0 0 16px;vertical-align:top;">
                    <span style="color:#c8d0e0;font-size:14px;">{opp['why_now']}</span>
                </td>
            </tr>
        </table>

        <div style="margin-top:18px;padding-top:18px;border-top:1px solid #2d3148;display:flex;justify-content:space-between;align-items:center;">
            <div style="color:#4a5370;font-size:12px;">
                Solo&nbsp;<strong style="color:#6b7a99;">{opp['scores']['solo_buildability']}</strong>&nbsp;&nbsp;
                Revenue&nbsp;<strong style="color:#6b7a99;">{opp['scores']['revenue_potential']}</strong>&nbsp;&nbsp;
                Market&nbsp;<strong style="color:#6b7a99;">{opp['scores']['market_size']}</strong>&nbsp;&nbsp;
                AI&nbsp;<strong style="color:#6b7a99;">{opp['scores']['ai_leverage']}</strong>
            </div>
            <a href="{opp['post_url']}" style="color:#DDA01D;font-size:13px;text-decoration:none;font-weight:600;">
                View post &rarr;
            </a>
        </div>
    </div>
    """


def _build_html(opportunities):
    date_str = datetime.now().strftime("%-d %B %Y")
    cards = "".join(_build_card(opp, i) for i, opp in enumerate(opportunities))
    count = len(opportunities)

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0d0f1a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,sans-serif;">
<div style="max-width:680px;margin:0 auto;padding:40px 20px;">

    <div style="text-align:center;margin-bottom:48px;">
        <div style="font-size:13px;color:#4a5370;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;">Weekly Digest &mdash; {date_str}</div>
        <h1 style="color:#DDA01D;font-size:36px;font-weight:800;margin:0 0 8px 0;letter-spacing:-1px;">Opportunity Scout</h1>
        <p style="color:#4a5370;font-size:15px;margin:0;">{count} idea{"s" if count != 1 else ""} scored 7+ this week</p>
    </div>

    {cards if opportunities else '<p style="color:#6b7a99;text-align:center;padding:40px 0;">No strong opportunities found this week. Check back next Sunday.</p>'}

    <div style="text-align:center;margin-top:48px;padding-top:32px;border-top:1px solid #1e2130;">
        <p style="color:#2d3148;font-size:12px;margin:0;">Powered by Reddit + Claude &middot; Runs every Sunday morning</p>
    </div>
</div>
</body>
</html>"""


def send_digest(opportunities):
    html = _build_html(opportunities)
    count = len(opportunities)
    subject = f"Opportunity Scout — {count} idea{'s' if count != 1 else ''} this week ({datetime.now().strftime('%-d %b')})"

    resend.Emails.send({
        "from": f"Opportunity Scout <ideas@thejoveclub.com>",
        "to": [os.environ["DIGEST_EMAIL"]],
        "subject": subject,
        "html": html,
    })

    print(f"Digest sent: {count} opportunities")
