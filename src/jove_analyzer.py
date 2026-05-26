import anthropic
import json
import os

SYSTEM_PROMPT = """You are a research analyst for Jove Club — a London-based outdoor adventure club that runs guided trips for fit, ambitious amateurs. Think hiking, scrambling, mountaineering, and multi-day expeditions in places like Snowdonia, the Lake District, Scottish Highlands, and the Alps.

Jove Club's audience: London professionals, 25-40, fit but not elite, looking for real challenge and adventure with good people. NOT stag dos. NOT tourist day hikes. NOT extreme solo alpinism.

Jove Club's current trips range from:
- Beginner: Lake District weekend (~£330)
- Challenge: Welsh 3000s, Peak District (£395)
- Harder: Scottish Highlands multi-day (£1,100-£1,150)
- Social/alpine: Austrian Alps

You're scanning Reddit to find:
1. Trips or challenges people are talking about wanting to do but can't find organised options for
2. Routes or destinations generating excitement and questions
3. Training goals people are working towards (could inform Jove's training offer)
4. Frustrations with existing adventure companies or guided trips
5. Trends in what the fit-amateur outdoor crowd is chasing right now

Score each idea on:
- excitement: How much buzz/desire is there around this?
- jove_fit: How well does it match Jove Club's audience and format?
- feasibility: Could Jove realistically run this as a guided small-group trip?
- gap: Is there a clear gap — i.e. people want this but struggle to find it organised?

Only surface ideas scoring 7+ overall. Return valid JSON only."""


def analyze_trips(posts):
    if not posts:
        return []

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    posts_text = "\n\n---\n\n".join([
        f"Post #{i + 1} [r/{p['subreddit']}]\n"
        f"Title: {p['title']}\n"
        f"Body: {p['body']}\n"
        f"URL: {p['url']}"
        for i, p in enumerate(posts[:120])
    ])

    prompt = f"""Here are {min(len(posts), 120)} Reddit posts from this week across outdoor, hiking, running, mountaineering and UK subreddits.

{posts_text}

Identify the top trip ideas and market insights for Jove Club. Return a JSON object:
{{
  "trip_ideas": [
    {{
      "post_url": "the reddit post URL",
      "subreddit": "subreddit name",
      "idea_name": "short punchy name for the trip or trend",
      "what_people_want": "what the post reveals people are after, in plain English",
      "why_interesting_for_jove": "why this is relevant to Jove Club specifically",
      "location": "where this would take place (be specific if possible)",
      "difficulty": "Beginner / Intermediate / Challenge / Expedition",
      "gap_in_market": "what organised options are missing or frustrating people",
      "scores": {{
        "excitement": 8,
        "jove_fit": 9,
        "feasibility": 7,
        "gap": 8,
        "overall": 8
      }}
    }}
  ],
  "trends": [
    "One-line observation about what the outdoor/adventure crowd is talking about this week"
  ]
}}

Include up to 8 trip ideas and up to 5 trend observations. Only include scores of 7+. Return only valid JSON."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=5000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    try:
        result = json.loads(raw)
        trip_ideas = result.get("trip_ideas", [])
        # Strip r/ prefix if Claude included it in the subreddit field
        for idea in trip_ideas:
            idea["subreddit"] = idea.get("subreddit", "").lstrip("r/")
        return trip_ideas, result.get("trends", [])
    except json.JSONDecodeError as e:
        print(f"Failed to parse Claude response: {e}")
        print(f"Raw response:\n{raw[:500]}")
        return [], []
