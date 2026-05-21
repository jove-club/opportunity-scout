import anthropic
import json
import os

SYSTEM_PROMPT = """You are an expert business opportunity analyst. You scan Reddit posts to identify genuine business ideas that one person could build using AI tools.

Criteria for a good opportunity:
- Buildable solo using AI (weeks or months, not years)
- Clear recurring revenue model (subscription, marketplace fee, etc.)
- Not heavily regulated (avoid fintech lending, clinical healthcare)
- Real pain felt by many people, not just one person
- AI can make the solution dramatically better or cheaper than what exists

Score each opportunity out of 10 on:
- solo_buildability: Can one person with AI tools realistically build this?
- revenue_potential: Is there an obvious way to charge money sustainably?
- market_size: Are enough people affected for this to be a business?
- ai_leverage: Does AI create a meaningful advantage over existing solutions?

Only include opportunities with an overall score of 7 or above.
Return valid JSON only — no commentary, no markdown fences."""


def analyze_opportunities(posts):
    if not posts:
        return []

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    posts_text = "\n\n---\n\n".join([
        f"Post #{i + 1} [r/{p['subreddit']}] Upvotes: {p['score']} | Comments: {p['num_comments']}\n"
        f"Title: {p['title']}\n"
        f"Body: {p['body']}\n"
        f"URL: {p['url']}"
        for i, p in enumerate(posts[:120])
    ])

    prompt = f"""Here are {min(len(posts), 120)} Reddit posts from this week. Identify the top business opportunities.

{posts_text}

Return a JSON object in exactly this format:
{{
  "opportunities": [
    {{
      "post_url": "the reddit post URL",
      "subreddit": "subreddit name",
      "pain_point": "the problem people are experiencing, in plain English",
      "business_idea": "what you would build — give it a short name",
      "how_to_build": "how one person using AI could build this in weeks or months",
      "revenue_model": "how you make money",
      "why_now": "why this is a timely opportunity",
      "scores": {{
        "solo_buildability": 8,
        "revenue_potential": 7,
        "market_size": 8,
        "ai_leverage": 9,
        "overall": 8
      }}
    }}
  ]
}}

Include up to 10 opportunities, ordered best first. Only include scores of 7+. Return only valid JSON."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=5000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences if model returns them despite instructions
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    try:
        result = json.loads(raw)
        return result.get("opportunities", [])
    except json.JSONDecodeError as e:
        print(f"Failed to parse Claude response: {e}")
        print(f"Raw response:\n{raw[:500]}")
        return []
