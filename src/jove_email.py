import os
import resend
from datetime import datetime

resend.api_key = os.environ["RESEND_API_KEY"]

DIFFICULTY_COLORS = {
    "Beginner": "#22c55e",
    "Intermediate": "#3b82f6",
    "Challenge": "#f59e0b",
    "Expedition": "#ef4444",
}


def _difficulty_badge(difficulty):
    color = DIFFICULTY_COLORS.get(difficulty, "#6b7a99")
    return f'<span style="background:{color}22;color:{color};font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;text-transform:uppercase;letter-spacing:1px;">{difficulty}</span>'


def _score_color(score):
    if score >= 9:
        return "#22c55e"
    if score >= 7:
        return "#f59e0b"
    return "#ef4444"


def _build_trip_card(idea):
    score = idea["scores"]["overall"]
    color = _score_color(score)
    return f"""
    <div style="background:#1a2035;border:1px solid #2d3557;border-radius:14px;padding:28px;margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">
            <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                <span style="background:#2d3557;color:#8892b0;font-size:12px;padding:4px 12px;border-radius:20px;font-family:monospace;">r/{idea['subreddit']}</span>
                {_difficulty_badge(idea.get('difficulty', ''))}
            </div>
            <span style="background:{color}22;color:{color};font-size:15px;font-weight:700;padding:4px 14px;border-radius:20px;">{score}/10</span>
        </div>

        <h2 style="color:#ffffff;font-size:21px;font-weight:700;margin:0 0 6px 0;line-height:1.3;">{idea['idea_name']}</h2>
        <p style="color:#7b8ab8;font-size:13px;margin:0 0 18px 0;">📍 {idea.get('location', 'Location TBC')}</p>

        <table style="width:100%;border-collapse:collapse;">
            <tr>
                <td style="padding:10px 0;border-bottom:1px solid #2d3557;vertical-align:top;width:32%;">
                    <span style="color:#DDA01D;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">What people want</span>
                </td>
                <td style="padding:10px 0 10px 16px;border-bottom:1px solid #2d3557;vertical-align:top;">
                    <span style="color:#c8d0e8;font-size:14px;">{idea['what_people_want']}</span>
                </td>
            </tr>
            <tr>
                <td style="padding:10px 0;border-bottom:1px solid #2d3557;vertical-align:top;">
                    <span style="color:#DDA01D;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Why Jove</span>
                </td>
                <td style="padding:10px 0 10px 16px;border-bottom:1px solid #2d3557;vertical-align:top;">
                    <span style="color:#c8d0e8;font-size:14px;">{idea['why_interesting_for_jove']}</span>
                </td>
            </tr>
            <tr>
                <td style="padding:10px 0;vertical-align:top;">
                    <span style="color:#DDA01D;font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Gap in market</span>
                </td>
                <td style="padding:10px 0 0 16px;vertical-align:top;">
                    <span style="color:#c8d0e8;font-size:14px;">{idea['gap_in_market']}</span>
                </td>
            </tr>
        </table>

        <div style="margin-top:18px;padding-top:18px;border-top:1px solid #2d3557;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div style="color:#4a5580;font-size:12px;">
                Excitement&nbsp;<strong style="color:#6b7a99;">{idea['scores']['excitement']}</strong>&nbsp;&nbsp;
                Jove fit&nbsp;<strong style="color:#6b7a99;">{idea['scores']['jove_fit']}</strong>&nbsp;&nbsp;
                Feasibility&nbsp;<strong style="color:#6b7a99;">{idea['scores']['feasibility']}</strong>&nbsp;&nbsp;
                Gap&nbsp;<strong style="color:#6b7a99;">{idea['scores']['gap']}</strong>
            </div>
            <a href="{idea['post_url']}" style="color:#DDA01D;font-size:13px;text-decoration:none;font-weight:600;">View post &rarr;</a>
        </div>
    </div>
    """


def _build_html(trip_ideas, trends):
    date_str = datetime.now().strftime("%-d %B %Y")
    cards = "".join(_build_trip_card(idea) for idea in trip_ideas)

    trend_items = "".join(
        f'<li style="color:#c8d0e8;font-size:14px;margin-bottom:8px;padding-left:4px;">{t}</li>'
        for t in trends
    )
    trends_block = f"""
    <div style="background:#151825;border:1px solid #2d3557;border-radius:14px;padding:24px;margin-bottom:32px;">
        <h3 style="color:#DDA01D;font-size:13px;text-transform:uppercase;letter-spacing:1px;font-weight:600;margin:0 0 16px 0;">What the outdoor crowd is talking about this week</h3>
        <ul style="margin:0;padding-left:20px;">
            {trend_items}
        </ul>
    </div>
    """ if trends else ""

    empty = '<p style="color:#6b7a99;text-align:center;padding:40px 0;">Nothing strong surfaced this week. Check back next Saturday.</p>'

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0d1020;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,sans-serif;">
<div style="max-width:680px;margin:0 auto;padding:40px 20px;">

    <div style="text-align:center;margin-bottom:48px;">
        <div style="font-size:13px;color:#4a5580;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;">Jove Club Research &mdash; {date_str}</div>
        <h1 style="color:#ffffff;font-size:34px;font-weight:800;margin:0 0 4px 0;letter-spacing:-1px;">Trip Intelligence</h1>
        <p style="color:#DDA01D;font-size:15px;margin:0;font-weight:500;">What the outdoor crowd wants this week</p>
    </div>

    {trends_block}

    {cards if trip_ideas else empty}

    <div style="text-align:center;margin-top:48px;padding-top:32px;border-top:1px solid #1a2035;">
        <p style="color:#2d3557;font-size:12px;margin:0;">Jove Club &middot; Powered by Reddit + Claude &middot; Every Saturday morning</p>
    </div>
</div>
</body>
</html>"""


def send_digest(trip_ideas, trends):
    html = _build_html(trip_ideas, trends)
    count = len(trip_ideas)
    subject = f"Jove Trip Intelligence — {count} idea{'s' if count != 1 else ''} this week ({datetime.now().strftime('%-d %b')})"

    resend.Emails.send({
        "from": "Jove Trip Intel <ideas@thejoveclub.com>",
        "to": [os.environ["DIGEST_EMAIL"]],
        "subject": subject,
        "html": html,
    })

    print(f"Jove digest sent: {count} trip ideas, {len(trends)} trends")
