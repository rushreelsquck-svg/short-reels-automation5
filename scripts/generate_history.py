"""
generate_history.py — Vaults of History
Expanded topic pool + curated surprising fact examples to inspire better content.
"""
import json
import os
import random
from pathlib import Path

import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

STATE_SUFFIX = os.environ.get("STATE_SUFFIX", "")
STATE_FILE = Path(__file__).resolve().parent.parent / "state" / f"used_premises{STATE_SUFFIX}.json"

HOOK_FORMULAS = [
    "The [specific surprising fact]. But that's not even the weird part.",
    "The [civilization] [did/had/invented something shocking]. And historians almost missed it.",
    "[Specific counterintuitive fact about a civilization]. Most people have no idea.",
    "In [era], [specific shocking thing happened]. Here's what they never taught you.",
    "[Named event or person] [did something nobody expected]. The reason why is stranger still.",
    "The [civilization] figured out [modern thing] over [X] years ago. Then it was forgotten.",
    "[Specific number or fact that sounds impossible]. This one is real.",
    "Most people think [common belief]. They're completely wrong.",
    "[Civilization] invented [modern thing] — [X] centuries before anyone else.",
    "The real reason [famous historical event] happened will change how you see it.",
]

HIGH_SEARCH_TOPICS = [
    # Ancient world
    "ancient Egypt", "ancient Rome", "ancient Greece", "ancient Sparta",
    "ancient China", "ancient Japan", "ancient India", "ancient Persia",
    "ancient Mesopotamia", "ancient Phoenicia", "ancient Carthage",
    # Empires
    "the Roman Empire", "the Mongol Empire", "the Ottoman Empire",
    "the Byzantine Empire", "the Persian Empire", "the British Empire",
    "the Mughal Empire", "the Holy Roman Empire", "the Macedonian Empire",
    # Medieval and Renaissance
    "medieval Europe", "the Crusades", "the Black Death", "the Renaissance",
    "medieval Japan", "the Silk Road", "medieval China",
    # Pre-Columbian Americas
    "the Aztecs", "the Inca Empire", "the Maya civilization",
    "the Vikings", "ancient Norse mythology",
    # Modern history
    "World War 1", "World War 2", "the Cold War", "the Space Race",
    "the French Revolution", "the American Civil War", "the Russian Revolution",
    "Napoleon Bonaparte", "ancient Africa", "the Samurai",
]

FACT_EXAMPLES = [
    # Egypt
    "Ancient Egyptian workers building the pyramids were paid partly in beer — about 4 to 5 liters a day",
    "Cleopatra was not Egyptian — she was Greek/Macedonian and was the first of her dynasty to even speak Egyptian",
    "Ancient Egyptians used moldy bread as a wound treatment — they unknowingly discovered penicillin 3,000 years early",
    "Cats in ancient Egypt were so sacred that killing one — even accidentally — was punishable by death",
    # Rome
    "Romans used urine as mouthwash — the ammonia actually whitens teeth, and it was so popular they taxed it",
    "Julius Caesar was once kidnapped by pirates — he was so offended by their ransom demand he asked them to raise it",
    "Ancient Rome had fast food restaurants called thermopolia — over 150 have been found in Pompeii alone",
    "Roman gladiators had their own fan merchandise — action figures, lamps, and perfume bottles with their faces on them",
    # Greece
    "Ancient Greek Olympic athletes competed completely naked — the word gymnasium literally means place to be naked",
    "Ancient Greeks had mechanical alarm clocks powered by water — with bells and birds that sang at set times",
    "Spartan warriors were required to steal their own food as part of training — getting caught was the only crime",
    # Vikings
    "Viking helmets had no horns — that image was invented by a 19th-century opera costume designer",
    "Vikings were obsessed with hygiene — combs are the single most common Viking archaeological find",
    "A Viking woman named Gudrid Thorbjarnardottir traveled to North America and back then walked to Rome on a pilgrimage",
    # Mongols
    "Genghis Khan established complete religious freedom across his empire — any religion was allowed and tax-exempt",
    "The Mongol Empire created the world's first international postal system with stations every 25 miles across Asia",
    "0.5 percent of the world's male population today is a direct descendant of Genghis Khan",
    # Medieval
    "Medieval people slept in two separate phases — waking up for an hour in the middle of the night was completely normal",
    "Windows were taxed in medieval England — people bricked up their own windows to avoid paying",
    "Medieval knights at tournaments could surrender and be held for ransom instead of being killed",
    # Americas
    "The Aztecs had mandatory public education for all children including girls — 500 years before most of Europe",
    "The Inca built 25,000 miles of roads without wheels, horses, or iron tools — using only human labor and rope",
    "Inca surgeons performed brain surgery with a 90 percent survival rate — better than American Civil War surgeons 400 years later",
    "The Maya independently invented the concept of zero before Europe had any concept of it",
    # China
    "China had a working civil service exam system 1,400 years before Europe invented bureaucracy",
    "Ancient China had a female emperor — Wu Zetian ruled for 15 years and expanded the empire significantly",
    "The Chinese invented toilet paper in the 6th century but it was reserved only for emperors",
    # WW1 and WW2
    "During WW1, British and German soldiers spontaneously stopped fighting on Christmas Day and played football together",
    "The US military developed bat bombs in WW2 — bats with tiny incendiary devices, intended to burn Japanese cities",
    "Hitler was nominated for the Nobel Peace Prize in 1939 by a Swedish politician who later said it was satirical protest",
    "A Japanese soldier named Hiroo Onoda kept fighting in the Philippine jungle until 1974 — he did not know the war ended in 1945",
    # Space Race and Cold War
    "The USSR sent a dog named Laika to space knowing she could not come back — and lied about it for 45 years",
    "NASA Apollo guidance computers had less processing power than a modern calculator",
    # Myth-busting
    "Napoleon was not short — he was 5 feet 7 inches, average for his era. The myth came from British propaganda",
    "The Great Wall of China is not visible from space — it is too narrow. The myth was printed in a textbook in 1932",
    "Marie Curie was so radioactive that her notebooks are still too dangerous to handle without protective gear",
    "Oxford University is older than the Aztec Empire — teaching began there in 1096, the Aztecs founded Tenochtitlan in 1325",
    # More surprising ones
    "The shortest war in history lasted 38 to 45 minutes — Britain vs Zanzibar in 1896",
    "Ancient Romans had a god specifically for door hinges — Cardea — because Romans took their doors very seriously",
    "Woolly mammoths were still alive when the Great Pyramid was being built in Egypt",
    "The man who invented the lobotomy won the Nobel Prize — in 1949, for a procedure now considered barbaric",
    "Ancient Greek temples were painted in bright colors — the white marble look we associate with antiquity is just the paint fading off",
]


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
        "Avoid these recently-covered topics:\n" + "\n".join(f"- {p}" for p in used_premises[-15:])
        if used_premises else "No prior topics to avoid yet."
    )
    hook_formula = random.choice(HOOK_FORMULAS)
    topic = random.choice(HIGH_SEARCH_TOPICS)
    example_facts = "\n".join(f"- {f}" for f in random.sample(FACT_EXAMPLES, 8))

    system_prompt = f"""You write scripts for a daily YouTube Shorts history channel called Vaults of History.
The channel's biggest problem is viewers swiping away in the first second.
The fix: name the surprising fact IMMEDIATELY. Don't tease — deliver.

CORE STRUCTURE (non-negotiable):

1. HOOK (2 sentences max):
   - Sentence 1: Name ONE specific, genuinely surprising fact immediately.
   - Sentence 2: Open a curiosity gap — give them a reason to keep watching.
   BAD: "Ancient Egypt was stranger than you think..."
   GOOD: "Ancient Egyptian doctors prescribed moldy bread for infected wounds.
          They had no idea why it worked — but they were right."

2. FACTS (3-4 only):
   - Each fact: one sharp sentence. Counterintuitive, specific, verifiable.
   - NOT "Rome was powerful" — INSTEAD "Roman emperors could not legally be
     prosecuted for any crime while they were alive"
   - Build toward closing the hook curiosity gap

3. CLOSE (1 sentence):
   - Resolve the curiosity loop from the hook
   - Satisfying payoff, not a cliff-hanger

TARGET: 25-35 seconds spoken. Shorter and more surprising beats longer and mediocre.

QUALITY BENCHMARK — examples of how surprising and specific your facts should be
(these are real facts — use them as a quality standard, do not copy them directly):
{example_facts}

TITLE: Civilization name + specific claim.
GOOD: "Ancient Rome Had Fast Food Restaurants — 150 Found in One City"
BAD: "Shocking Facts About Rome You Never Knew"

ACCURACY: Every fact must be true and documented. This audience fact-checks.
Never exaggerate. If uncertain, skip it. Original wording only.

VISUAL QUERIES — specific and literal (what would a camera actually film?):
GOOD: "close up Roman mosaic floor ancient ruins"
BAD: "ancient history dramatic"

Hook AND every fact AND the close each need their own visual query.
Call the submit_history_video tool exactly once."""

    HISTORY_TOOL = {
        "name": "submit_history_video",
        "description": "Submit the finished history video.",
        "input_schema": {
            "type": "object",
            "properties": {
                "premise": {"type": "string", "description": "One-sentence topic summary to avoid repeating"},
                "title": {"type": "string", "description": "<=95 chars. Civilization name + specific surprising claim."},
                "description": {"type": "string", "description": "2-3 sentences plus a follow nudge"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "8-12 lowercase tags including civilization name"},
                "hashtags": {"type": "array", "items": {"type": "string"}, "description": "5-8 hashtags, always include #shorts and #history"},
                "hook": {"type": "string", "description": "1-2 sentences: specific fact + curiosity gap. Under 25 words."},
                "hook_visual_query": {"type": "string", "description": "Specific literal stock-footage phrase for hook"},
                "facts": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 4,
                    "items": {
                        "type": "object",
                        "properties": {
                            "narration": {"type": "string", "description": "One sharp sentence. The fact IS the sentence."},
                            "visual_query": {"type": "string", "description": "Specific literal stock-footage phrase"},
                        },
                        "required": ["narration", "visual_query"],
                    },
                },
                "close": {"type": "string", "description": "One sentence closing the curiosity loop from the hook"},
                "close_visual_query": {"type": "string", "description": "Specific literal stock-footage phrase for close"},
            },
            "required": ["premise", "title", "description", "tags", "hashtags",
                         "hook", "hook_visual_query", "facts", "close", "close_visual_query"],
        },
    }

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=system_prompt,
        tools=[HISTORY_TOOL],
        tool_choice={"type": "tool", "name": "submit_history_video"},
        messages=[{
            "role": "user",
            "content": f"""Write today's history video.

{avoid_text}

Suggested topic: {topic}
(Use this or pick a different high-search topic if it was covered recently)

Hook formula to adapt (shape only — fill with a real specific fact for today's topic):
"{hook_formula}"

Name the specific surprising fact in the first sentence.
Target: 25-35 seconds spoken. 3-4 facts maximum.""",
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
