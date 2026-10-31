# Rain City Homers — Producer Guide

This file is the show bible. Every scheduled run reads it and follows it exactly.

## The show
- **Name:** Rain City Homers
- **Hosts:** two voices, written as a conversation.
  - **CAL** — the numbers guy. Calm, dry, cites efficiency stats, EPA, KenPom, splits. Still a homer, just a careful one. Keeps Rusty honest.
  - **RUSTY** — the fired-up fan. 12th Man to the bone, treats every Zags win like a title, makes the Cougar jokes, leaves out the inconvenient stat until Cal brings it up.
- **Tone:** unapologetic homers, **fact-based**, light humor. Every number and claim must be verified. Opinions and predictions are fine; invented facts are not.
- **No persistent segments.** Each episode stands alone. No running pick records, no callbacks that require earlier episodes.

## Teams, in priority order
1. Gonzaga men's basketball — on air, always call them **"the Zags."** Not "Gonzaga," not "the Bulldogs," not "Gonzaga basketball."
2. Seattle Seahawks
3. Seattle Mariners
4. Washington Huskies football — **football only.** Never cover other UW sports (no Husky hoops, etc.).

Weight airtime by season. In-season teams get recaps **and analysis** (why it happened, what it means, what to watch). Out-of-season teams get a short segment only when there is real news (trades, signings, coaching, injuries, portal/recruiting). If there's nothing, skip the team with one line.

## National block (5–8 minutes, end of show)
Include, in this order of importance:
1. National stories that touch our teams (conference races, rivals, polls, NFC West, AL West, CFP/bracketology).
2. The biggest league-wide headlines (NFL, MLB, college basketball, college football).
3. The biggest broader sports stories (NBA, NHL, golf, tennis, soccer, Olympics, etc.).

## Schedule & episode types
- **Monday 5:00 AM Eastern — Weekend Recap:** results and analysis from the weekend + week-ahead look.
- **Friday 5:00 AM Eastern — Weekend Preview:** matchups, injuries, lines, keys to the game, a prediction from each host.
- Slow weeks (byes, dead periods): publish only one episode that week (skip Friday) and keep it short.
- **Length:** usually 20–30 minutes (~3,000–4,500 words). Up to 45 minutes (~6,500 words) only in very heavy weeks. Never pad.

## Research rules
- Use firecrawl_search / firecrawl_scrape (direct web fetches are blocked in this environment) and WebSearch.
- Prefer primary sources: gozags.com, seahawks.com, mlb.com/mariners, gohuskies.com, pro-football-reference.com, ESPN, AP, Seattle Times, Spokesman-Review.
- Double-check scores, records, stats and dates. If sources conflict or a fact can't be confirmed, leave it out or have a host say it's unconfirmed.
- Game times: say Pacific first, then Eastern.

## Script format (tools/make_audio.py parses this)
- Lines start with `CAL:` or `RUSTY:`, one turn per line, blank line between turns.
- `[SEGMENT name]` lines insert a short chime. Use: intro, gonzaga, seahawks, mariners, huskies, national, outro (skip unused ones; order teams by what's in season and newsworthy).
- Write for the ear: spell out numbers and scores the way people say them ("twenty to three"), no abbreviations like "vs." or "No.", no URLs, no emoji, no parentheses.
- Open with a quick hello and the rundown; close with a quick recap and "This has been Rain City Homers."

## Production steps (each run)
1. Research (see rules above).
2. Write `scripts/YYYY-MM-DD-<type>.txt`.
3. `python3 tools/make_audio.py scripts/<file>.txt episodes/YYYY-MM-DD-<type>.mp3`
4. Add an entry to `episodes.json` (file, title, 1–3 sentence description, RFC 2822 pub_date, duration_sec from ffprobe).
5. `python3 tools/build_feed.py .` (also prunes to the newest 10 episodes).
6. Commit and push to `main`. GitHub Pages publishes the feed.

## Voices
- Primary: Microsoft Edge neural voices via `edge-tts` (CAL = en-US-AndrewMultilingualNeural, RUSTY = en-US-BrianMultilingualNeural). Needs `pip install edge-tts` and the HTTPS proxy (handled in make_audio.py).
- Fallback: Kokoro (open-source, local) if Edge is unreachable.
