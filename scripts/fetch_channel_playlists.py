#!/usr/bin/env python3
"""
Fetches all playlists for a given YouTube channel URL and extracts:
- playlist_id
- title
- url
- video_count (never null: uses en-US badge parsing + pageHeaderViewModel + fallback flat-playlist count)
Saves output to data/raw_playlists/<channel_key>.json
"""
import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import urllib.request

HEADERS_EN = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_counts_from_channel_page(playlists_url: str) -> dict:
    """Extract {playlist_id: video_count} from initial /playlists HTML using en-US badges."""
    counts = {}
    try:
        req = urllib.request.Request(playlists_url + "?hl=en", headers=HEADERS_EN)
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        m = re.search(r"var ytInitialData = (\{.*?\});</script>", html)
        if not m:
            return counts
        data = json.loads(m.group(1))

        def walk(node):
            if isinstance(node, dict):
                if "lockupViewModel" in node:
                    lvm = node["lockupViewModel"]
                    cid = lvm.get("contentId")
                    if cid and cid.startswith("PL"):
                        s = json.dumps(lvm, ensure_ascii=False)
                        m_cnt = re.search(r'"(?:text|content)"\s*:\s*"(\d[\d,]*)\s*(?:videos?|episodes?)"', s, re.I)
                        if m_cnt:
                            counts[cid] = int(m_cnt.group(1).replace(",", ""))
                for k in ("gridPlaylistRenderer", "playlistRenderer"):
                    if k in node:
                        pr = node[k]
                        pid = pr.get("playlistId")
                        if pid:
                            vc = pr.get("videoCount") or pr.get("videoCountShortText", {}).get("simpleText")
                            if vc and re.search(r"\d+", str(vc)):
                                counts[pid] = int(re.sub(r"[^\d]", "", str(vc)))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(data)
    except Exception as e:
        sys.stderr.write(f"Warning: initial page count parse failed: {e}\n")
    return counts


def fetch_playlist_video_count(playlist_id: str) -> int | None:
    """Fetch exact video count for a single playlist from its webpage header (en-US)."""
    url = f"https://www.youtube.com/playlist?list={playlist_id}&hl=en"
    try:
        req = urllib.request.Request(url, headers=HEADERS_EN)
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
        m = re.search(r"var ytInitialData = (\{.*?\});</script>", html)
        if m:
            s = m.group(1)
            patterns = [
                r'"(?:text|content)"\s*:\s*"([\d,]+)\s*videos?"',
                r'"numVideosText"\s*:\s*\{\s*"runs"\s*:\s*\[\s*\{\s*"text"\s*:\s*"([\d,]+)"',
                r'"videoCountText"\s*:\s*\{\s*"runs"\s*:\s*\[\s*\{\s*"text"\s*:\s*"([\d,]+)"',
                r'"stats"\s*:\s*\[\s*\{\s*"runs"\s*:\s*\[\s*\{\s*"text"\s*:\s*"([\d,]+)"',
            ]
            for pat in patterns:
                mm = re.search(pat, s, re.I)
                if mm:
                    digits = re.sub(r"[^\d]", "", mm.group(1))
                    if digits:
                        return int(digits)
    except Exception:
        pass
    # Fallback: count via yt-dlp --flat-playlist --print id
    try:
        p = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "id", f"https://www.youtube.com/playlist?list={playlist_id}"],
            capture_output=True, text=True, timeout=60
        )
        lines = [x.strip() for x in p.stdout.splitlines() if x.strip()]
        if lines:
            return len(lines)
    except Exception:
        pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel-key", required=True)
    ap.add_argument("--sheikh-id", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    base_url = args.url.rstrip("/")
    playlists_url = base_url if base_url.endswith("/playlists") else f"{base_url}/playlists"

    # 1. Run yt-dlp --flat-playlist --dump-json on /playlists
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", playlists_url]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    raw_items = []
    seen = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        pid = obj.get("id")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        raw_items.append({
            "playlist_id": pid,
            "title": obj.get("title") or "",
            "url": obj.get("url") or f"https://www.youtube.com/playlist?list={pid}",
            "channel_id": obj.get("playlist_channel_id") or obj.get("channel_id"),
            "channel_title": obj.get("playlist_channel") or obj.get("playlist_uploader"),
        })

    # 2. Get video counts from initial /playlists page (en-US)
    counts = extract_counts_from_channel_page(playlists_url)

    # 3. For any playlist missing video_count, fetch concurrently
    missing = [it["playlist_id"] for it in raw_items if it["playlist_id"] not in counts]
    if missing:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(fetch_playlist_video_count, pid): pid for pid in missing}
            for fut in concurrent.futures.as_completed(futs):
                pid = futs[fut]
                cnt = fut.result()
                if cnt is not None:
                    counts[pid] = cnt

    for idx, it in enumerate(raw_items, 1):
        it["order_no"] = idx
        it["video_count"] = counts.get(it["playlist_id"])

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    result = {
        "channel_key": args.channel_key,
        "sheikh_id": args.sheikh_id,
        "source_url": args.url,
        "playlists_url": playlists_url,
        "total_playlists": len(raw_items),
        "total_videos_reported": sum(it["video_count"] or 0 for it in raw_items),
        "playlists": raw_items,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK {args.channel_key}: {len(raw_items)} playlists, {result['total_videos_reported']} videos -> {args.out}")


if __name__ == "__main__":
    main()
