import anthropic
import json
import os

SYSTEM_PROMPT = """You are an objective market research analyst. You read Reddit posts and report what you actually observe — nothing more, nothing less.

Your job is NOT to find opportunities or validate ideas. Your job is to accurately describe what people are saying, how many posts touch on a topic, and how strong the signal is.

Rules:
- Separate observation from inference. "Posts show X" is an observation. "This means Jove should do Y" is an inference — flag it clearly as such, or leave it out.
- Be honest about weak signals. If only one post mentions something, say so. Don't amplify it.
- Include counter-signals. If posts suggest people prefer doing something solo, say that.
- Do not be a hype machine. Your value is accuracy, not enthusiasm.
- Confidence is based on post count: Low = 1-2 posts, Medium = 3-6 posts, High = 7+ posts.

Context (for relevance assessment only — do not let it bias your observations):
Jove Club runs guided outdoor adventure trips for fit London professionals (25-40). Trips range from Lake District weekends to Scottish Highlands expeditions and Alpine social trips. They also offer training and coaching."""


def analyze_trips(posts):
    if not posts:
        return [], []

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

Read these posts carefully and report what you actually observe. Group related posts into topics.

Return a JSON object in exactly this format:
{{
  "observations": [
    {{
      "topic": "Short descriptive topic name (not a sales pitch)",
      "what_people_are_saying": "Factual 2-3 sentence summary of what posts actually say. Quote or closely paraphrase where possible. Do not editorialize.",
      "post_count": 4,
      "confidence": "Medium",
      "subreddits": ["HikingUK", "CasualUK"],
      "example_post_url": "URL of the most representative post",
      "counter_signals": "Any posts that suggest the opposite, or reasons to be cautious about this signal. Write null if none.",
      "jove_relevance": "One neutral sentence on whether this touches Jove's market — or null if it doesn't."
    }}
  ],
  "absent_signals": [
    "Something you might have expected to see but didn't — notable absences or gaps in what people are talking about"
  ]
}}

Include 6-10 observations. Order by confidence (High first). Include at least 2-3 absent_signals. Return only valid JSON."""

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
        observations = result.get("observations", [])
        for obs in observations:
            obs["subreddits"] = [s.lstrip("r/") for s in obs.get("subreddits", [])]
        return observations, result.get("absent_signals", [])
    except json.JSONDecodeError as e:
        print(f"Failed to parse Claude response: {e}")
        print(f"Raw response:\n{raw[:500]}")
        return [], []
