# Vaults of History — Daily History Facts Bot

Automatically writes a themed "hidden history" video each day — a hook
opener, 5-7 surprising true historical facts, real stock-footage clips cut
between them (no Ken Burns zoom, this genre wants pace) — and uploads it to
YouTube. Same automation pattern as the other channels, a fully generative
content engine (no real-world news topic feed).

---

## What this actually does (and doesn't do)

- ✅ Picks one era/civilization/theme per video (ancient Rome, WWII, medieval
  Europe, lost civilizations, etc., rotated so it doesn't repeat too often)
  and writes 5-7 genuinely surprising, true historical facts in original wording.
- ✅ Opens with a curiosity hook adapted from a rotating pool of proven
  opener styles — adapted to fit the actual facts, not recited generically.
- ✅ One real stock-footage clip per fact instead of one looping background
  or a static zoomed image.
- ❌ Does **not** invent or exaggerate historical claims — the system prompt
  requires verifiable accuracy and explicitly tells Claude to skip a fact
  rather than use one it isn't confident about. It's also told to flag
  popular myths as myths rather than presenting them as fact. Still worth
  spot-checking outputs periodically — history content draws a skeptical,
  well-informed audience, and credibility is everything in this niche.
- ❌ Does **not** guarantee views, same honest caveat as every channel here.

---

## This one leans harder on Pexels than the news channels

A facts-style countdown with no real footage at all is a much weaker watch
than a 50-second news recap can get away with on a gradient background —
so getting a `PEXELS_API_KEY` set up matters more here. It's still free
(just rate limited), see Step 1. Search terms lean toward historical
locations/reenactment b-roll ("ancient ruins", "medieval castle interior"),
which Pexels has reasonable (if not unlimited) coverage of.

---

## Setup

If you already have a working repo for another channel, reuse
`ANTHROPIC_API_KEY` and `YT_API_KEY` as-is. You'll need a **new**
`YT_REFRESH_TOKEN` for this channel's account, and ideally your own
`PEXELS_API_KEY` if you're running several channels (shared keys hit shared
rate limits).

### Step 1: Pexels API key (strongly recommended for this channel)

Sign up free at [pexels.com/api](https://www.pexels.com/api/), grab the key.

### Step 2: YouTube OAuth

Same as the other channels — if you already have a Google Cloud OAuth app,
reuse `YT_CLIENT_ID`/`YT_CLIENT_SECRET` and just get a new refresh token for
this channel's account:

```powershell
$env:YT_CLIENT_ID = "your-client-id"
$env:YT_CLIENT_SECRET = "your-client-secret"
venv\Scripts\python.exe scripts\get_oauth_token.py
```

Log into *this* channel's Google account when the browser opens.

### Step 3: Anthropic API key

Reuse your existing key, or create one at
[console.anthropic.com](https://console.anthropic.com) → Settings → API Keys.

### Step 4: Push to GitHub and add secrets

New repo, push this folder in, then add these repo secrets:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | from Step 3 |
| `YT_CLIENT_ID` / `YT_CLIENT_SECRET` | from Step 2 |
| `YT_REFRESH_TOKEN` | from Step 2 |
| `PEXELS_API_KEY` | from Step 1 |
| `YT_API_KEY` | optional, for trending-tag enrichment |

### Step 5: Test it

Actions tab → "Vaults of History - Daily Facts" → **Run workflow**. Check
the result in YouTube Studio before trusting the schedule.

---

## Customizing

- **Eras & hook styles**: both live in `scripts/generate_history.py` —
  `HOOK_STYLES` is the rotating opener pool, the system prompt controls
  era variety and fact count.
- **How many facts per video**: the `minItems`/`maxItems` on the `facts`
  array in `generate_history.py`'s tool schema (5-7 by default).
- **Visual pace**: each fact gets its own clip by design. To cut even faster,
  split long facts into two shorter ones rather than changing the video code.
- **How videos go public**: `YT_PRIVACY_STATUS` works exactly like the other
  channels — `scheduled` (default), `unlisted`, or `public`.
