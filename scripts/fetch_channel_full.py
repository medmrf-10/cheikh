#!/usr/bin/env python3
"""
Ultra-Fast Pure InnerTube Full Channel Fetcher (Zero yt-dlp subprocess overhead, Persistent Keep-Alive TLS):
1. Resolves channel_id (UC...) if not provided.
2. Uses YouTube InnerTube API (browseId=UC..., params=EglwbGF5bGlzdHPyBgQKAkIA) + continuations to get ALL playlists.
3. Uses persistent thread-local HTTPSConnection("www.youtube.com") with automatic retry to fetch all videos
   inside every playlist (VLPL...) + all videos in the channel's Uploads playlist (VLUU...).
4. Any uploaded video not in any playlist is placed in the channel's "غير مصنف" (unclassified) playlist.
"""
import argparse
import concurrent.futures
import gzip
import http.client
import json
import os
import re
import sys
import threading
import time

CLIENT_CTX = {
    "client": {
        "clientName": "WEB",
        "clientVersion": "2.20260904.01.00",
        "hl": "ar",
        "gl": "SA",
    }
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip",
    "Accept-Language": "ar,en;q=0.9",
    "Connection": "keep-alive",
}

_tls = threading.local()


def get_conn() -> http.client.HTTPSConnection:
    conn = getattr(_tls, "conn", None)
    if conn is None:
        conn = http.client.HTTPSConnection("www.youtube.com", timeout=25)
        _tls.conn = conn
    return conn


def reset_conn():
    conn = getattr(_tls, "conn", None)
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
    _tls.conn = None


def innertube_post(payload: dict, retries: int = 4) -> dict:
    body = json.dumps({"context": CLIENT_CTX, **payload}).encode("utf-8")
    last_err = None
    for attempt in range(retries):
        try:
            conn = get_conn()
            conn.request("POST", "/youtubei/v1/browse?prettyPrint=false", body=body, headers=HEADERS)
            resp = conn.getresponse()
            raw = resp.read()
            if resp.getheader("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            if resp.status != 200:
                reset_conn()
                raise RuntimeError(f"HTTP {resp.status}")
            return json.loads(raw.decode("utf-8", "ignore"))
        except Exception as e:
            last_err = e
            reset_conn()
            time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"innertube_post failed after {retries} retries: {last_err}")


def get_text(node) -> str:
    if not node:
        return ""
    if isinstance(node, str):
        return node
    if "content" in node and isinstance(node["content"], str):
        return node["content"]
    if "simpleText" in node:
        return node["simpleText"]
    if "runs" in node:
        return "".join(r.get("text", "") for r in node["runs"])
    return ""


def parse_hms(s: str) -> int | None:
    if not s:
        return None
    m = re.search(r"(\d+:)?\d+:\d+", s)
    if not m:
        return None
    parts = [int(p) for p in m.group(0).split(":") if p.isdigit()]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return None


def parse_channel_playlists_and_cont(data: dict):
    """Extract playlist items (lockupViewModel / gridPlaylistRenderer) and continuation tokens."""
    pls = []
    conts = []

    def walk(node):
        if isinstance(node, dict):
            if "lockupViewModel" in node:
                lvm = node["lockupViewModel"]
                cid = lvm.get("contentId")
                if cid and str(cid).startswith("PL"):
                    title = get_text(lvm.get("metadata", {}).get("lockupMetadataViewModel", {}).get("title"))
                    pls.append({
                        "playlist_id": cid,
                        "title": title,
                        "url": f"https://www.youtube.com/playlist?list={cid}",
                    })
                    return
            for k in ("gridPlaylistRenderer", "playlistRenderer"):
                if k in node:
                    pr = node[k]
                    pid = pr.get("playlistId")
                    if pid and str(pid).startswith("PL"):
                        pls.append({
                            "playlist_id": pid,
                            "title": get_text(pr.get("title")),
                            "url": f"https://www.youtube.com/playlist?list={pid}",
                        })
                        return
            if "continuationCommand" in node and isinstance(node["continuationCommand"], dict):
                tok = node["continuationCommand"].get("token")
                if isinstance(tok, str) and tok and tok not in conts:
                    conts.append(tok)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for it in node:
                walk(it)

    walk(data)
    return pls, conts


def discover_channel_playlists(channel_id: str) -> tuple[list[dict], str | None]:
    """Discover all playlists on a channel via InnerTube browse."""
    all_pls = []
    seen = set()
    channel_title = None
    data = innertube_post({"browseId": channel_id, "params": "EglwbGF5bGlzdHPyBgQKAkIA"})
    # Try to grab channel title from header/metadata
    channel_title = (
        data.get("metadata", {}).get("channelMetadataRenderer", {}).get("title")
        or get_text(data.get("header", {}).get("c4TabbedHeaderRenderer", {}).get("title"))
    )
    pls, conts = parse_channel_playlists_and_cont(data)
    for p in pls:
        if p["playlist_id"] not in seen:
            seen.add(p["playlist_id"])
            all_pls.append(p)
    used = set()
    page = 1
    while conts and page < 30:
        tok = next((t for t in conts if t not in used), None)
        if not tok:
            break
        used.add(tok)
        page += 1
        data = innertube_post({"continuation": tok})
        pls, conts = parse_channel_playlists_and_cont(data)
        added = 0
        for p in pls:
            if p["playlist_id"] not in seen:
                seen.add(p["playlist_id"])
                all_pls.append(p)
                added += 1
        if added == 0:
            break
    return all_pls, channel_title


def parse_playlist_videos_and_cont(data: dict):
    """Extract video items (lockupViewModel or playlistVideoRenderer) and continuation token(s)."""
    videos = []
    continuations = []

    def walk(node):
        if isinstance(node, dict):
            if "lockupViewModel" in node:
                lvm = node["lockupViewModel"]
                if lvm.get("contentType") == "LOCKUP_CONTENT_TYPE_VIDEO" or (
                    lvm.get("contentId") and len(str(lvm.get("contentId"))) == 11
                ):
                    vid = lvm.get("contentId")
                    meta = lvm.get("metadata", {}).get("lockupMetadataViewModel", {})
                    title = get_text(meta.get("title"))
                    dur = None
                    overlays = (
                        lvm.get("contentImage", {})
                        .get("thumbnailViewModel", {})
                        .get("overlays", [])
                    )
                    for ov in overlays:
                        badges = ov.get("thumbnailBottomOverlayViewModel", {}).get("badges", [])
                        for b in badges:
                            t = b.get("thumbnailBadgeViewModel", {}).get("text", "")
                            d_sec = parse_hms(t)
                            if d_sec is not None:
                                dur = d_sec
                                break
                    videos.append({
                        "yt_id": vid,
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "duration": dur,
                    })
                    return
            if "playlistVideoRenderer" in node:
                pvr = node["playlistVideoRenderer"]
                vid = pvr.get("videoId")
                if vid:
                    title = get_text(pvr.get("title"))
                    dur_str = pvr.get("lengthSeconds")
                    dur = int(dur_str) if dur_str and str(dur_str).isdigit() else parse_hms(get_text(pvr.get("lengthText")))
                    videos.append({
                        "yt_id": vid,
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "duration": dur,
                    })
                    return
            if "continuationCommand" in node and isinstance(node["continuationCommand"], dict):
                tok = node["continuationCommand"].get("token")
                if isinstance(tok, str) and tok and tok not in continuations:
                    continuations.append(tok)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for it in node:
                walk(it)

    walk(data)
    return videos, continuations


def fetch_playlist_all_videos(playlist_id: str, max_pages: int = 50) -> list[dict]:
    """Fetch all videos inside a playlist (PL... or UU...) via InnerTube browse + continuations."""
    all_vids = []
    seen = set()
    try:
        data = innertube_post({"browseId": f"VL{playlist_id}"})
        vids, conts = parse_playlist_videos_and_cont(data)
        for v in vids:
            if v["yt_id"] not in seen:
                seen.add(v["yt_id"])
                all_vids.append(v)
        page = 1
        used_tokens = set()
        while conts and page < max_pages:
            tok = next((t for t in conts if t not in used_tokens), None)
            if not tok:
                break
            used_tokens.add(tok)
            page += 1
            data = innertube_post({"continuation": tok})
            vids, conts = parse_playlist_videos_and_cont(data)
            added = 0
            for v in vids:
                if v["yt_id"] not in seen:
                    seen.add(v["yt_id"])
                    all_vids.append(v)
                    added += 1
            if added == 0:
                break
    except Exception as e:
        sys.stderr.write(f"Warning fetching playlist {playlist_id}: {e}\n")

    for i, v in enumerate(all_vids, 1):
        v["order_no"] = i
    return all_vids


def resolve_channel_id(url: str) -> str | None:
    m = re.search(r"channel/(UC[\w-]{22})", url)
    if m:
        return m.group(1)
    path = re.sub(r"^https?://(www\.)?youtube\.com", "", url) or "/"
    for attempt in range(3):
        try:
            conn = get_conn()
            conn.request("GET", path, headers={"User-Agent": HEADERS["User-Agent"], "Accept-Encoding": "gzip"})
            resp = conn.getresponse()
            raw = resp.read()
            if resp.getheader("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            html = raw.decode("utf-8", "ignore")
            for pat in (
                r'"externalId"\s*:\s*"(UC[\w-]{22})"',
                r'"channelId"\s*:\s*"(UC[\w-]{22})"',
                r'channel/(UC[\w-]{22})',
            ):
                mm = re.search(pat, html)
                if mm:
                    return mm.group(1)
        except Exception:
            reset_conn()
            time.sleep(0.4)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel-key", required=True)
    ap.add_argument("--sheikh-id", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--channel-id", default=None)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--max-upload-pages", type=int, default=80, help="Max 100-video pages for channel uploads")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    detected_channel_id = args.channel_id or resolve_channel_id(args.url)
    if not detected_channel_id:
        raise RuntimeError(f"Could not resolve UC channel_id for {args.url}")

    # 1. Discover all playlists on the channel via pure InnerTube
    playlists, detected_channel_title = discover_channel_playlists(detected_channel_id)

    # 2. Fetch all videos inside every playlist concurrently with persistent keep-alive connections
    pl_videos_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_playlist_all_videos, pl["playlist_id"], 50): pl["playlist_id"] for pl in playlists}
        for fut in concurrent.futures.as_completed(futs):
            pid = futs[fut]
            pl_videos_map[pid] = fut.result()

    in_any_playlist = set()
    for idx, pl in enumerate(playlists, 1):
        vids = pl_videos_map.get(pl["playlist_id"], [])
        pl["order_no"] = idx
        pl["video_count"] = len(vids)
        pl["total_duration_sec"] = sum(v.get("duration") or 0 for v in vids)
        pl["videos"] = vids
        for v in vids:
            in_any_playlist.add(v["yt_id"])

    # 3. Fetch channel's Uploads playlist (UU...) to find unclassified videos
    uu_id = "UU" + detected_channel_id[2:]
    uploads = fetch_playlist_all_videos(uu_id, max_pages=args.max_upload_pages)
    unclassified = []
    for v in uploads:
        if v["yt_id"] not in in_any_playlist:
            unclassified.append(dict(v))
    for i, v in enumerate(unclassified, 1):
        v["order_no"] = i

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    result = {
        "channel_key": args.channel_key,
        "sheikh_id": args.sheikh_id,
        "channel_id": detected_channel_id,
        "channel_title": detected_channel_title,
        "source_url": args.url,
        "total_playlists": len(playlists),
        "total_playlist_videos": sum(pl["video_count"] for pl in playlists),
        "unique_playlist_videos": len(in_any_playlist),
        "total_channel_uploads_scanned": len(uploads),
        "unclassified_count": len(unclassified),
        "playlists": playlists,
        "unclassified_playlist": {
            "playlist_id": f"{args.channel_key}__unclassified",
            "title": "غير مصنف",
            "video_count": len(unclassified),
            "total_duration_sec": sum(v.get("duration") or 0 for v in unclassified),
            "videos": unclassified,
        },
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(
        f"OK {args.channel_key}: {len(playlists)} playlists ({sum(pl['video_count'] for pl in playlists)} items, "
        f"{len(in_any_playlist)} unique) + {len(unclassified)} unclassified (out of {len(uploads)} uploads) -> {args.out}"
    )


if __name__ == "__main__":
    main()
