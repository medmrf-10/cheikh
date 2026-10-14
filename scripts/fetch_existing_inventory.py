#!/usr/bin/env python3
"""
Builds data/existing_inventory.json by scanning (READ-ONLY):
1. Local /Users/macm1pro/REPOS/hawshat/playlists/lessons/ and transcripts/
2. GitHub repo medmrf-10/ytb catalog.json (via gh api)
Maps every YouTube video ID (yt_id) -> {has_transcript, has_summary, has_questions, sheikh_photo}
"""
import json
import os
import re
import subprocess

OUT_PATH = "/Users/macm1pro/REPOS/cheikh/data/existing_inventory.json"
HAWSHAT_DIR = "/Users/macm1pro/REPOS/hawshat"


def main():
    yt_map = {}  # yt_id -> {"t": bool, "s": bool, "q": bool}

    def mark(vid, t=False, s=False, q=False):
        if not vid or len(str(vid)) != 11:
            return
        rec = yt_map.setdefault(vid, {"t": False, "s": False, "q": False})
        if t:
            rec["t"] = True
        if s:
            rec["s"] = True
        if q:
            rec["q"] = True

    # 1. Scan local hawshat/playlists/data/read/*.json if present
    read_dir = os.path.join(HAWSHAT_DIR, "playlists", "data", "read")
    if os.path.isdir(read_dir):
        for fn in os.listdir(read_dir):
            if not fn.endswith(".json"):
                continue
            fp = os.path.join(read_dir, fn)
            try:
                data = json.load(open(fp, encoding="utf-8"))
                items = data.get("items") or data.get("lessons") or []
                for it in items:
                    vid = it.get("yt") or it.get("id") or it.get("vid")
                    if vid and len(str(vid)) == 11:
                        has_t = bool(it.get("txt") or it.get("rd") or it.get("text"))
                        has_s = bool(it.get("sum") or it.get("sm"))
                        has_q = bool(it.get("qu") or it.get("q"))
                        mark(vid, t=has_t, s=has_s, q=has_q)
            except Exception:
                pass

    # 2. Fetch git tree of medmrf-10/ytb via gh api to see every <NNN>_<vid>.txt / .sum.json / .questions.json
    try:
        proc = subprocess.run(
            ["gh", "api", "repos/medmrf-10/ytb/git/trees/main?recursive=1", "--jq", ".tree[].path"],
            capture_output=True, text=True, timeout=60
        )
        for line in proc.stdout.splitlines():
            p = line.strip()
            # Match <sheikh>/<series>/<NNN>_<vid>.(txt|sum.json|questions.json)
            m = re.search(r"/\d+_([A-Za-z0-9_-]{11})\.(txt|sum\.json|questions\.json)$", p)
            if m:
                vid, ext = m.group(1), m.group(2)
                mark(
                    vid,
                    t=(ext == "txt"),
                    s=(ext == "sum.json"),
                    q=(ext == "questions.json"),
                )
    except Exception as e:
        print(f"Warning: gh api tree scan failed: {e}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    summary = {
        "total_unique_videos_with_assets": len(yt_map),
        "with_transcript": sum(1 for v in yt_map.values() if v["t"]),
        "with_summary": sum(1 for v in yt_map.values() if v["s"]),
        "with_questions": sum(1 for v in yt_map.values() if v["q"]),
        "videos": yt_map,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(
        f"Saved inventory: {summary['total_unique_videos_with_assets']} videos "
        f"(transcripts={summary['with_transcript']}, summaries={summary['with_summary']}, questions={summary['with_questions']})"
    )


if __name__ == "__main__":
    main()
