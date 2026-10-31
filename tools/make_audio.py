#!/usr/bin/env python3
"""Turn a Rain City Homers script into a finished MP3.

Usage: make_audio.py <script.txt> <out.mp3>

Script format: "CAL: text" / "RUSTY: text" lines, "[SEGMENT name]" markers,
"#" comment lines. Tries Microsoft Edge neural voices first, falls back to
Kokoro (local, open-source) if Edge is unreachable.
"""
import asyncio
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

EDGE_VOICES = {"CAL": "en-US-AndrewMultilingualNeural", "RUSTY": "en-US-BrianMultilingualNeural"}
KOKORO_VOICES = {"CAL": "am_michael", "RUSTY": "am_puck"}
SR = 24000
if os.path.exists("/root/.ccr/ca-bundle.crt"):
    os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")


def parse(script_path):
    items = []
    for raw in Path(script_path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"\[SEGMENT\s+(\w+)\]", line)
        if m:
            items.append(("SEGMENT", m.group(1)))
            continue
        m = re.match(r"(CAL|RUSTY):\s*(.+)", line)
        if m:
            items.append((m.group(1), m.group(2)))
    return items


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def to_wav(src, dst):
    run(["ffmpeg", "-y", "-i", str(src), "-ar", str(SR), "-ac", "1", str(dst)])


def make_silence(dst, seconds):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(seconds), str(dst)])


def make_sting(dst):
    # Short three-note rising chime used between segments.
    notes = [(523.25, 0.16), (659.25, 0.16), (783.99, 0.45)]
    parts = []
    for i, (f, d) in enumerate(notes):
        p = Path(dst).with_name(f"note{i}.wav")
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency={f}:duration={d}:sample_rate={SR}",
             "-af", f"volume=0.25,afade=t=out:st={d*0.5}:d={d*0.5}", "-ac", "1", str(p)])
        parts.append(p)
    concat(parts, dst)


def concat(files, dst):
    lst = Path(dst).with_suffix(".txt")
    lst.write_text("".join(f"file '{f}'\n" for f in files))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst)])


async def edge_tts_line(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate="+6%", proxy=os.environ.get("HTTPS_PROXY")).save(str(out))


async def edge_batch(lines, work, parallel=6):
    """Voice every line concurrently, with a timeout and retries per line."""
    sem = asyncio.Semaphore(parallel)
    done = 0

    async def one(i, who, text):
        nonlocal done
        out = work / f"{i:04d}.mp3"
        async with sem:
            for attempt in range(5):
                try:
                    await asyncio.wait_for(edge_tts_line(text, EDGE_VOICES[who], out), timeout=45)
                    if out.stat().st_size > 0:
                        break
                except Exception as e:
                    if attempt == 4:
                        raise RuntimeError(f"line {i} failed: {e}")
                    await asyncio.sleep(2 * (attempt + 1))
        done += 1
        if done % 10 == 0 or done == len(lines):
            print(f"  voiced {done}/{len(lines)}", flush=True)

    await asyncio.gather(*(one(i, w, t) for i, w, t in lines))


def edge_available():
    try:
        import edge_tts  # noqa: F401
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "probe.mp3"
            asyncio.run(edge_tts_line("Test.", EDGE_VOICES["CAL"], out))
            return out.stat().st_size > 0
    except Exception:
        return False


_kokoro = None


def kokoro_line(text, voice, out):
    global _kokoro
    import soundfile as sf
    from kokoro import KPipeline
    import numpy as np
    if _kokoro is None:
        _kokoro = KPipeline(lang_code="a")
    chunks = [audio for _, _, audio in _kokoro(text, voice=voice, speed=1.05)]
    sf.write(str(out), np.concatenate(chunks), SR)


def main(script_path, out_mp3):
    items = parse(script_path)
    use_edge = edge_available()
    print(f"voice engine: {'edge' if use_edge else 'kokoro'}; {len(items)} items")
    work = Path(tempfile.mkdtemp(prefix="rch_"))
    gap = work / "gap.wav"
    make_silence(gap, 0.35)
    sting = work / "sting.wav"
    make_sting(sting)
    pad = work / "pad.wav"
    make_silence(pad, 0.6)

    lines = [(i, who, text) for i, (who, text) in enumerate(items) if who != "SEGMENT"]
    if use_edge:
        asyncio.run(edge_batch(lines, work))
    seq = []
    for i, (who, text) in enumerate(items):
        if who == "SEGMENT":
            seq += [pad, sting, pad]
            continue
        wav = work / f"{i:04d}.wav"
        if use_edge:
            to_wav(work / f"{i:04d}.mp3", wav)
        else:
            raw = work / f"{i:04d}_raw.wav"
            kokoro_line(text, KOKORO_VOICES[who], raw)
            to_wav(raw, wav)
        seq += [wav, gap]

    full = work / "full.wav"
    concat(seq, full)
    # Podcast loudness standard (-16 LUFS), mono 96 kbps MP3.
    run(["ffmpeg", "-y", "-i", str(full), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-ac", "1", "-ar", "44100", "-b:a", "96k", str(out_mp3)])
    print(f"wrote {out_mp3}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
