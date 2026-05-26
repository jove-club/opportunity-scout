import os
import resend
from datetime import datetime

resend.api_key = os.environ["RESEND_API_KEY"]

CONFIDENCE_COLORS = {
    "High":   {"bg": "#22c55e22", "text": "#22c55e"},
    "Medium": {"bg": "#f59e0b22", "text": "#f59e0b"},
    "Low":    {"bg": "#6b7a9922", "text": "#6b7a99"},
}


def _confidence_badge(confidence):
    c = CONFIDENCE_COLORS.get(confidence, CONFIDENCE_COLORS["Low"])
    return (
        f'<span style="background:{c["bg"]};color:{c["text"]};'
        f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;'
        f'text-transform:uppercase;letter-spacing:1px;">'
        f'{confidence} confidence</span>'
    )


def _subreddit_tags(subreddits):
    tags = "".join(
        f'<span style="background:#f0f0f0;color:#555;font-size:11px;padding:2px 8px;'
        f'border-radius:12px;font-family:monospace;margin-right:4px;">r/{s}</span>'
        for s in subreddits
    )
    return tags


def _build_observation_card(obs):
    counter = obs.get("counter_signals")
    counter_block = (
        f'<div style="background:#fff8f0;border-left:3px solid #f59e0b;padding:10px 14px;'
        f'border-radius:0 6px 6px 0;margin-top:12px;">'
        f'<span style="color:#92400e;font-size:11px;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:1px;">Counter-signal</span>'
        f'<p style="color:#78350f;font-size:13px;margin:4px 0 0 0;">{counter}</p>'
        f'</div>'
    ) if counter and counter != "null" and counter is not None else ""

    relevance = obs.get("jove_relevance")
    relevance_block = (
        f'<div style="background:#f0f4ff;border-left:3px solid #3b82f6;padding:10px 14px;'
        f'border-radius:0 6px 6px 0;margin-top:12px;">'
        f'<span style="color:#1e40af;font-size:11px;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:1px;">Jove relevance</span>'
        f'<p style="color:#1e3a8a;font-size:13px;margin:4px 0 0 0;">{relevance}</p>'
        f'</div>'
    ) if relevance and relevance != "null" and relevance is not None else ""

    post_count = obs.get("post_count", "?")
    confidence = obs.get("confidence", "Low")
    url = obs.get("example_post_url", "")

    return f"""
    <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;padding:22px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
            <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
                {_subreddit_tags(obs.get("subreddits", []))}
            </div>
            {_confidence_badge(confidence)}
        </div>

        <h2 style="color:#111827;font-size:17px;font-weight:700;margin:0 0 4px 0;line-height:1.4;">{obs['topic']}</h2>
        <p style="color:#6b7280;font-size:12px;margin:0 0 12px 0;">Based on {post_count} post{'s' if post_count != 1 else ''} this week</p>

        <p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 4px 0;">{obs['what_people_are_saying']}</p>

        {counter_block}
        {relevance_block}

        <div style="margin-top:14px;">
            <a href="{url}" style="color:#6b7280;font-size:12px;text-decoration:none;">View example post &rarr;</a>
        </div>
    </div>
    """


def _build_html(observations, absent_signals):
    date_str = datetime.now().strftime("%-d %B %Y")
    cards = "".join(_build_observation_card(obs) for obs in observations)
    count = len(observations)

    absent_items = "".join(
        f'<li style="color:#6b7280;font-size:14px;margin-bottom:8px;">{s}</li>'
        for s in absent_signals
    )
    absent_block = f"""
    <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:20px;margin-top:24px;">
        <h3 style="color:#374151;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin:0 0 12px 0;">
            What we didn't see this week
        </h3>
        <ul style="margin:0;padding-left:18px;">
            {absent_items}
        </ul>
    </div>
    """ if absent_signals else ""

    empty = '<p style="color:#6b7280;text-align:center;padding:40px 0;">No posts collected this week.</p>'

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,sans-serif;">
<div style="max-width:660px;margin:0 auto;padding:32px 16px;">

    <div style="margin-bottom:32px;">
        <p style="font-size:12px;color:#9ca3af;text-transform:uppercase;letter-spacing:2px;margin:0 0 6px 0;">Jove Club &mdash; {date_str}</p>
        <h1 style="color:#111827;font-size:28px;font-weight:800;margin:0 0 4px 0;letter-spacing:-0.5px;">Weekly Outdoor Research Brief</h1>
        <p style="color:#6b7280;font-size:14px;margin:0;">{count} topic{'s' if count != 1 else ''} observed across Reddit this week</p>
    </div>

    {cards if observations else empty}

    {absent_block}

    <div style="margin-top:32px;padding-top:20px;border-top:1px solid #e5e7eb;">
        <p style="color:#d1d5db;font-size:11px;margin:0;">Powered by Reddit RSS + Claude &middot; Every Saturday morning &middot; Posts are real; interpretations are Claude's</p>
    </div>
</div>
</body>
</html>"""


def send_digest(observations, absent_signals):
    html = _build_html(observations, absent_signals)
    count = len(observations)
    subject = f"Jove Research Brief — {count} topic{'s' if count != 1 else ''} this week ({datetime.now().strftime('%-d %b')})"

    resend.Emails.send({
        "from": "Jove Research <ideas@thejoveclub.com>",
        "to": [os.environ["DIGEST_EMAIL"]],
        "subject": subject,
        "html": html,
    })

    print(f"Jove digest sent: {count} observations")
