"""
generate_history.py
Generates a fully original "hidden history / history secrets" script — no
external source, fully generative. Each video opens with a curiosity hook
(sampled from a pool of proven viral opener styles) then runs through
several short, genuinely surprising, true historical facts, one per scene,
ending with a subscribe nudge.

Same accuracy requirement as a facts channel needs: every claim must be true
and verifiable, never invented or exaggerated for effect — history content
draws a particularly skeptical, well-informed audience, and a single wrong
date or invented anecdote can sink a channel's credibility fast.

Tracks recent eras/topics in state so the rotating subject matter (ancient
Rome, WWII, medieval Europe, lost civilizations, etc.) doesn't repeat too often.
"""
import json
import os
import random
from pathlib import Path

import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

STATE_SUFFIX = os.environ.get("STATE_SUFFIX", "")
STATE_FILE = Path(__file__).resolve().parent.parent / "state" / f"used_premises{STATE_SUFFIX}.json"

# A rotating pool of proven curiosity-driven opener styles. The data shows
# "Was Stranger/More Advanced Than You Think" style titles are outperforming
# others — these hook styles reflect that. One gets sampled per video and
# given to Claude as inspiration, adapted naturally to fit the actual theme.
HOOK_STYLES = [
    "was stranger than you think...",
    "was darker than history books let on...",
    "was more advanced than we give them credit for...",
    "hid something historians are still debating...",
    "had a secret most people never hear about...",
    "did something that still shocks researchers today...",
    "was built on a mystery nobody has fully solved...",
    "collapsed for a reason that sounds impossible...",
    "had technology that shouldn't have existed yet...",
    "was stranger, darker, and more fascinating than you were taught...",
]

# Civilizations and eras with high YouTube search volume — prioritized so
# the algorithm has more existing audience interest to tap into.
HIGH_SEARCH_TOPICS = [
    "ancient Egypt", "ancient Rome", "ancient Greece", "Vikings",
    "medieval Europe", "the Mongol Empire", "ancient China", "the Aztecs",
    "the Inca Empire", "ancient Mesopotamia", "the Ottoman Empire",
    "ancient Japan", "the Byzantine Empire", "ancient Maya", "WWII",
    "the Roman Empire", "ancient Sparta", "the Persian Empire",
]

SYSTEM_PROMPT = """You write scripts for a daily YouTube Shorts channel called Vaults of History,
sharing genuinely surprising, true, well-documented historical facts and stories.

Title strategy (important for discovery):
- Your best-performing titles follow the pattern "[Civilization/Era] Was [Surprising Claim]" —
  e.g. "Ancient Egypt Was Stranger Than You Think" or "The Mongol Empire Was More Brutal Than
  History Books Admit." Lead the title with the civilization or era name so it shows up in
  search results for people already interested in that topic, then follow with a curiosity hook.
- Prioritize high-search civilizations and eras: ancient Egypt, Rome, Greece, Vikings, Mongols,
  Aztecs, Incas, medieval Europe, WWII, Sparta, Persia, Japan, China, Ottoman Empire, Maya.
  These have existing audiences actively searching — a strong video on them gets amplified faster
  than an equally strong video on an obscure topic.
- The hook example you're given is a sentence fragment (e.g. "was stranger than you think") —
  write the full hook line naturally adapting it to today's specific civilization/theme.

Hard rules:
- Every fact must be true and based on the real historical record — never invent, exaggerate, or
  embellish a date, figure, or event. If you're not confident something is accurate, don't use it.
  This audience is skeptical and well-informed; a single fabricated "fact" damages credibility fast.
- Avoid widely-debunked pop-history myths (presenting them as true) — if a popular claim is actually
  a myth, either skip it or explicitly frame it as "the myth vs. what really happened."
- All wording must be entirely original — write your own explanation of each fact in your own words,
  never lightly reskin a specific list or article you've seen elsewhere.
- Pick ONE era, civilization, or theme for the whole video so it feels cohesive. Vary it day to day.
- Open with a short, punchy hook line naturally incorporating the hook example you're given.
- Then 5-7 facts, each 1-2 sentences, each genuinely surprising — not things most people already know.
- Close with a one-line "follow for more" nudge.
- Written for narration: short sentences, no headers, no bullet points, dramatic but not breathless.
- For the hook AND each fact, pick a short visually-literal phrase a stock-footage search engine
  could find real b-roll for (e.g. "ancient roman ruins", "medieval castle interior", "old world map",
  "historical battlefield reenactment") — name the literal thing a camera would see, never abstract.
  The hook needs its own visual cue just like every fact does — never leave it out.
- Call the submit_history_video tool exactly once."""

HISTORY_TOOL = {
    "name": "submit_history_video",
    "description": "Submit the finished history video: hook, facts with visual cues, and upload metadata.",
    "input_schema": {
        "type": "object",
        "properties": {
            "premise": {"type": "string", "description": "One-sentence summary of this video's era/theme, used only to avoid repeating the same theme too often"},
            "title": {"type": "string", "description": "<=95 characters, curiosity-driven, accurate to the content"},
            "description": {"type": "string", "description": "2-3 sentences plus a follow nudge"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "8-12 lowercase tags relevant to this video's era/theme"},
            "hashtags": {"type": "array", "items": {"type": "string"}, "description": "5-8 hashtags starting with #, always include #shorts"},
            "hook": {"type": "string", "description": "The opening hook line, 1 short sentence"},
            "hook_visual_query": {"type": "string", "description": "Concrete, literal stock-footage search phrase for the hook itself"},
            "facts": {
                "type": "array",
                "minItems": 5,
                "maxItems": 7,
                "items": {
                    "type": "object",
                    "properties": {
                        "narration": {"type": "string", "description": "1-2 sentences for this historical fact"},
                        "visual_query": {"type": "string", "description": "Specific 4-7 word stock-footage search phrase that precisely matches this fact"},
                    },
                    "required": ["narration", "visual_query"],
                },
            },
        },
        "required": ["premise", "title", "description", "tags", "hashtags", "hook", "hook_visual_query", "facts"],
    },
}


def _load_used_premises():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return []


def _save_used_premise(premise):
    used = _load_used_premises()
    used.append(premise)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(used[-60:], indent=2))


def generate_history_video() -> dict:
    used_premises = _load_used_premises()
    avoid_text = (
        "Avoid these recent eras/themes — pick a different one:\n" + "\n".join(f"- {p}" for p in used_premises[-15:])
        if used_premises else "No prior themes to avoid yet."
    )
    # Pick a random hook style and a high-search topic suggestion
    hook_sample = random.choice(HOOK_STYLES)
    topic_suggestion = random.choice(HIGH_SEARCH_TOPICS)

    user_prompt = f"""Write today's history video.

{avoid_text}

Suggested topic (you can use this or pick a different high-search civilization/era if it was covered recently): {topic_suggestion}

Hook style to adapt for the opening line (this is a sentence fragment — work it into a natural full sentence matching the topic):
"{hook_sample}"

Example of how to use this: if the topic is "ancient Rome" and the hook fragment is "was stranger than you think", a good opening hook line might be: "Ancient Rome was far stranger than history class ever let on." Adapt it naturally — don't recite it verbatim."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[HISTORY_TOOL],
        tool_choice={"type": "tool", "name": "submit_history_video"},
        messages=[{"role": "user", "content": user_prompt}],
    )

    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    video = dict(tool_use_block.input)

    if not any(h.lower() == "#shorts" for h in video.get("hashtags", [])):
        video.setdefault("hashtags", []).append("#shorts")

    _save_used_premise(video["premise"])
    return video


if __name__ == "__main__":
    print(json.dumps(generate_history_video(), indent=2))
