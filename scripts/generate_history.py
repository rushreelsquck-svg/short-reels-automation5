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

# A rotating pool of proven curiosity-driven opener styles, picked for this
# specific genre. One gets sampled and handed to Claude as inspiration for
# THIS video's hook line — adapted naturally, not recited verbatim.
HOOK_STYLES = [
    "If you're seeing this, you're about to learn something they never taught you in school...",
    "You won't believe this actually happened...", "This will change how you see history...",
    "No one talks about this but...", "Historians don't like talking about this one...",
    "The secret nobody shares (but I will)...", "This is the part of history they skip...",
    "This feels illegal to know...", "Stop scrolling, you need to hear this...",
    "What nobody tells you about...", "Here's something most people don't know...",
    "This was buried for a reason...",
]

SYSTEM_PROMPT = """You write scripts for a daily YouTube Shorts channel called Vaults of History,
sharing genuinely surprising, true, well-documented historical facts and stories.

Hard rules:
- Every fact must be true and based on the real historical record — never invent, exaggerate, or
  embellish a date, figure, or event. If you're not confident something is accurate, don't use it.
  This audience is skeptical and well-informed; a single fabricated "fact" damages credibility fast.
- Avoid widely-debunked pop-history myths (presenting them as true) — if a popular claim is actually
  a myth, either skip it or explicitly frame it as "the myth vs. what really happened."
- All wording must be entirely original — write your own explanation of each fact in your own words,
  never lightly reskin a specific list or article you've seen elsewhere.
- Pick ONE era, civilization, or theme for the whole video (e.g. ancient Rome, WWII, medieval Europe,
  lost civilizations, exploration age, ancient Egypt) so it feels cohesive. Vary it day to day.
- Open with a short, punchy hook line in the spirit of the example styles you're given — adapt one
  naturally to fit this video's actual theme, don't recite it generically.
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
                        "visual_query": {"type": "string", "description": "Concrete, literal stock-footage search phrase for this fact"},
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
    sample_hooks = "\n".join(f"- {h}" for h in random.sample(HOOK_STYLES, 4))

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[HISTORY_TOOL],
        tool_choice={"type": "tool", "name": "submit_history_video"},
        messages=[{
            "role": "user",
            "content": f"Write today's history video.\n\n{avoid_text}\n\nSome example hook styles for inspiration (adapt, don't recite verbatim):\n{sample_hooks}",
        }],
    )

    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    video = dict(tool_use_block.input)

    if not any(h.lower() == "#shorts" for h in video.get("hashtags", [])):
        video.setdefault("hashtags", []).append("#shorts")

    _save_used_premise(video["premise"])
    return video


if __name__ == "__main__":
    print(json.dumps(generate_history_video(), indent=2))
