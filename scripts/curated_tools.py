#!/usr/bin/env python3
"""
Tools for managing the new curated database (`data/curated.db`) and exporting
both `curated.db` and `cheikh.db` (raw YouTube DB) to the local web interface.

Usage:
  python3 scripts/curated_tools.py init
  python3 scripts/curated_tools.py dump-sheikh <sheikh_id>
  python3 scripts/curated_tools.py import-sheikh <sheikh_id>
  python3 scripts/curated_tools.py export-web
"""
import fcntl
import glob
import json
import os
import sqlite3
import sys
from collections import defaultdict

BASE_DIR = "/Users/macm1pro/REPOS/cheikh"
RAW_DB = os.path.join(BASE_DIR, "data", "cheikh.db")
CURATED_DB = os.path.join(BASE_DIR, "data", "curated.db")
INV_PATH = os.path.join(BASE_DIR, "data", "existing_inventory.json")
CURATED_JSON_DIR = os.path.join(BASE_DIR, "data", "curated_sheikhs")
LOCK_FILE = os.path.join(BASE_DIR, "data", ".curated.lock")

CURATED_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sheikhs (
    id TEXT PRIMARY KEY,
    order_no INTEGER NOT NULL,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    photo TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS channels (
    id TEXT PRIMARY KEY,
    sheikh_id TEXT NOT NULL REFERENCES sheikhs(id) ON DELETE CASCADE,
    priority INTEGER NOT NULL DEFAULT 1,
    yt_channel_id TEXT,
    title TEXT,
    handle TEXT,
    url TEXT NOT NULL,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_cur_channels_sheikh ON channels(sheikh_id, priority);

CREATE TABLE IF NOT EXISTS series (
    id TEXT PRIMARY KEY,
    sheikh_id TEXT NOT NULL REFERENCES sheikhs(id) ON DELETE CASCADE,
    order_no INTEGER NOT NULL DEFAULT 1,
    title TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'شرح علمي',
    state TEXT NOT NULL DEFAULT 'completed' CHECK (state IN ('completed', 'ongoing', 'stopped')),
    expected_count INTEGER,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_cur_series_sheikh ON series(sheikh_id, order_no);

CREATE TABLE IF NOT EXISTS lessons (
    id TEXT PRIMARY KEY,
    series_id TEXT NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    sheikh_id TEXT NOT NULL REFERENCES sheikhs(id) ON DELETE CASCADE,
    order_no INTEGER NOT NULL,
    display_no TEXT,
    is_child INTEGER NOT NULL DEFAULT 0,
    parent_yt_id TEXT,
    title TEXT NOT NULL,
    yt_id TEXT NOT NULL,
    yt_title TEXT,
    yt_url TEXT NOT NULL,
    duration INTEGER,
    has_transcript INTEGER NOT NULL DEFAULT 0,
    has_summary INTEGER NOT NULL DEFAULT 0,
    has_questions INTEGER NOT NULL DEFAULT 0,
    has_challenges INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(series_id, order_no),
    UNIQUE(sheikh_id, yt_id)
);

CREATE INDEX IF NOT EXISTS idx_cur_lessons_series ON lessons(series_id, order_no);
CREATE INDEX IF NOT EXISTS idx_cur_lessons_sheikh ON lessons(sheikh_id);
CREATE INDEX IF NOT EXISTS idx_cur_lessons_yt ON lessons(yt_id);
"""


def _ensure_lesson_columns(conn: sqlite3.Connection):
    cols = {r[1] for r in conn.execute("PRAGMA table_info(lessons)").fetchall()}
    if "display_no" not in cols:
        conn.execute("ALTER TABLE lessons ADD COLUMN display_no TEXT")
    if "is_child" not in cols:
        conn.execute("ALTER TABLE lessons ADD COLUMN is_child INTEGER NOT NULL DEFAULT 0")
    if "parent_yt_id" not in cols:
        conn.execute("ALTER TABLE lessons ADD COLUMN parent_yt_id TEXT")


def init_curated_db():
    os.makedirs(CURATED_JSON_DIR, exist_ok=True)
    raw = sqlite3.connect(RAW_DB)
    cur = sqlite3.connect(CURATED_DB, timeout=60.0)
    cur.executescript("DROP TABLE IF EXISTS lessons; DROP TABLE IF EXISTS series;")
    cur.executescript(CURATED_SCHEMA)
    for r in raw.execute("SELECT id, order_no, name, short_name, photo FROM sheikhs"):
        cur.execute(
            "INSERT OR REPLACE INTO sheikhs (id, order_no, name, short_name, photo) VALUES (?,?,?,?,?)",
            r,
        )
    for r in raw.execute("SELECT id, sheikh_id, priority, yt_channel_id, title, handle, url, note FROM channels"):
        cur.execute(
            "INSERT OR REPLACE INTO channels (id, sheikh_id, priority, yt_channel_id, title, handle, url, note) VALUES (?,?,?,?,?,?,?,?)",
            r,
        )
    cur.commit()
    cur.close()
    raw.close()
    print("curated.db initialized with sheikhs and channels.")


def dump_sheikh_for_analysis(sheikh_id: str):
    """
    Exports a clean workspace file `data/curated_sheikhs/<sheikh_id>_raw.json`
    containing all raw playlists and all unique videos (with the list of raw playlists
    each video appeared in) from `data/cheikh.db` so the subagent can inspect every
    title and construct the curated series.
    """
    os.makedirs(CURATED_JSON_DIR, exist_ok=True)
    raw = sqlite3.connect(RAW_DB)
    raw.row_factory = sqlite3.Row

    sh = raw.execute("SELECT * FROM sheikhs WHERE id = ?", (sheikh_id,)).fetchone()
    if not sh:
        raise SystemExit(f"Unknown sheikh_id: {sheikh_id}")

    raw_series = raw.execute(
        "SELECT id, order_no, title, yt_playlist_id, state, expected_count, note FROM series WHERE sheikh_id = ? ORDER BY order_no",
        (sheikh_id,),
    ).fetchall()

    raw_lessons = raw.execute(
        "SELECT series_id, order_no, title, yt_id, yt_url, duration, has_transcript, has_summary, has_questions FROM lessons WHERE sheikh_id = ? ORDER BY series_id, order_no",
        (sheikh_id,),
    ).fetchall()

    series_map = {r["id"]: dict(r) for r in raw_series}
    for s in series_map.values():
        s["videos"] = []

    unique_videos = {}
    for l in raw_lessons:
        vid = l["yt_id"]
        sid = l["series_id"]
        stitle = series_map[sid]["title"] if sid in series_map else sid
        is_uncl = series_map[sid]["yt_playlist_id"] is None if sid in series_map else False
        if sid in series_map:
            series_map[sid]["videos"].append({
                "pos": l["order_no"],
                "yt_id": vid,
                "title": l["title"],
                "duration": l["duration"],
            })
        if vid not in unique_videos:
            unique_videos[vid] = {
                "yt_id": vid,
                "title": l["title"],
                "yt_url": l["yt_url"],
                "duration": l["duration"],
                "has_transcript": l["has_transcript"],
                "has_summary": l["has_summary"],
                "has_questions": l["has_questions"],
                "appearances": [],
            }
        unique_videos[vid]["appearances"].append({
            "raw_series_id": sid,
            "raw_series_title": stitle,
            "pos": l["order_no"],
            "is_unclassified": is_uncl,
        })

    out_path = os.path.join(CURATED_JSON_DIR, f"{sheikh_id}_raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "sheikh": dict(sh),
                "raw_playlists_count": sum(1 for s in series_map.values() if s["yt_playlist_id"] is not None),
                "unique_videos_count": len(unique_videos),
                "raw_series": list(series_map.values()),
                "unique_videos": list(unique_videos.values()),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"Wrote {out_path}: {len(series_map)} raw series, {len(unique_videos)} unique videos.")


def import_curated_sheikh(sheikh_id: str):
    """
    Imports `data/curated_sheikhs/<sheikh_id>.json` into `data/curated.db` safely under a file lock,
    and updates the web catalog JSONs.
    """
    in_path = os.path.join(CURATED_JSON_DIR, f"{sheikh_id}.json")
    if not os.path.exists(in_path):
        raise SystemExit(f"Missing curated file: {in_path}")

    data = json.load(open(in_path, encoding="utf-8"))
    series_list = data.get("series", [])

    inv = {"videos": {}}
    if os.path.exists(INV_PATH):
        inv = json.load(open(INV_PATH, encoding="utf-8"))
    inv_vids = inv.get("videos", {})

    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            raw = sqlite3.connect(RAW_DB)
            raw_vids = {}
            for r in raw.execute(
                "SELECT yt_id, yt_title, yt_url, duration FROM lessons WHERE sheikh_id = ?",
                (sheikh_id,),
            ):
                if r[0] not in raw_vids:
                    raw_vids[r[0]] = {"yt_title": r[1], "yt_url": r[2], "duration": r[3]}
            raw.close()

            cur = sqlite3.connect(CURATED_DB, timeout=60.0)
            cur.execute("PRAGMA foreign_keys = ON")
            cur.executescript(CURATED_SCHEMA)
            _ensure_lesson_columns(cur)

            # Clear old curated rows for this sheikh
            cur.execute("DELETE FROM lessons WHERE sheikh_id = ?", (sheikh_id,))
            cur.execute("DELETE FROM series WHERE sheikh_id = ?", (sheikh_id,))

            seen_vids = set()
            total_inserted_lessons = 0
            for s_idx, sr in enumerate(series_list, 1):
                s_id = sr.get("id") or f"{sheikh_id}__s{s_idx:03d}"
                s_title = (sr.get("title") or "").strip()
                if not s_title:
                    continue
                s_cat = (sr.get("category") or "شرح علمي").strip()
                s_state = sr.get("state") or "completed"
                if s_state not in ("completed", "ongoing", "stopped"):
                    s_state = "completed"
                lessons = sr.get("lessons") or []

                # Flatten any nested `children` while preserving parent-child linkage
                flat_entries = []
                last_main_vid = None
                for l in lessons:
                    vid = l.get("yt_id")
                    if not vid or vid in seen_vids:
                        continue
                    seen_vids.add(vid)
                    is_ch = bool(l.get("is_child"))
                    parent_vid = l.get("parent_yt_id") or (last_main_vid if is_ch else None)
                    if not is_ch:
                        last_main_vid = vid
                    flat_entries.append((l, is_ch, parent_vid))
                    for ch in (l.get("children") or []):
                        ch_vid = ch.get("yt_id")
                        if not ch_vid or ch_vid in seen_vids:
                            continue
                        seen_vids.add(ch_vid)
                        flat_entries.append((ch, True, vid))

                if not flat_entries:
                    continue

                exp_cnt = sr.get("expected_count")
                if not isinstance(exp_cnt, int) or exp_cnt < len(flat_entries):
                    exp_cnt = len(flat_entries)
                s_note = sr.get("note")

                cur.execute(
                    """
                    INSERT INTO series (id, sheikh_id, order_no, title, category, state, expected_count, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (s_id, sheikh_id, s_idx, s_title, s_cat, s_state, exp_cnt, s_note),
                )

                main_num = 0
                for l_idx, (l, is_ch, parent_vid) in enumerate(flat_entries, 1):
                    vid = l["yt_id"]
                    rinfo = raw_vids.get(vid, {})
                    l_title = (l.get("title") or rinfo.get("yt_title") or f"الدرس {l_idx}").strip()
                    yt_title = rinfo.get("yt_title") or l_title
                    yt_url = l.get("yt_url") or rinfo.get("yt_url") or f"https://www.youtube.com/watch?v={vid}"
                    dur = l.get("duration") if l.get("duration") is not None else rinfo.get("duration")
                    assets = inv_vids.get(vid, {})
                    has_t = 1 if assets.get("t") else 0
                    has_s = 1 if assets.get("s") else 0
                    has_q = 1 if assets.get("q") else 0

                    if is_ch:
                        explicit_sub = l.get("display_no") or l.get("sub_no") or l.get("ep_no")
                        disp_no = str(explicit_sub).strip() if explicit_sub is not None else "تتمة"
                    else:
                        explicit_ep = l.get("display_no") if l.get("display_no") is not None else l.get("ep_no")
                        if explicit_ep is not None and str(explicit_ep).strip() != "":
                            disp_no = str(explicit_ep).strip()
                            if disp_no.isdigit() and int(disp_no) > 0:
                                main_num = int(disp_no)
                        else:
                            main_num += 1
                            disp_no = str(main_num)

                    l_id = f"{s_id}__{l_idx:04d}__{vid}"
                    cur.execute(
                        """
                        INSERT INTO lessons (id, series_id, sheikh_id, order_no, display_no, is_child, parent_yt_id, title, yt_id, yt_title, yt_url, duration, has_transcript, has_summary, has_questions, has_challenges)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        """,
                        (l_id, s_id, sheikh_id, l_idx, disp_no, 1 if is_ch else 0, parent_vid, l_title, vid, yt_title, yt_url, dur, has_t, has_s, has_q),
                    )
                    total_inserted_lessons += 1

            cur.commit()
            cur.close()
            print(
                f"[{sheikh_id}] Imported into curated.db: {len(series_list)} series, "
                f"{total_inserted_lessons} unique lessons (out of {len(raw_vids)} unique raw videos)."
            )
            export_web_catalog()
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def _export_single_db(db_path: str, catalog_out: str, series_dir: str, is_curated: bool):
    os.makedirs(series_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if is_curated:
        _ensure_lesson_columns(conn)

    sheikh_rows = conn.execute("SELECT * FROM sheikhs ORDER BY order_no").fetchall()
    sheikhs_out = []

    for sh in sheikh_rows:
        sid = sh["id"]
        ch_rows = conn.execute("SELECT * FROM channels WHERE sheikh_id = ? ORDER BY priority", (sid,)).fetchall()
        sr_rows = conn.execute(
            """
            SELECT s.*,
                   COUNT(l.id) AS actual_count,
                   COALESCE(SUM(l.duration), 0) AS total_duration,
                   COALESCE(SUM(l.has_transcript), 0) AS transcribed_count,
                   COALESCE(SUM(l.has_summary), 0) AS summary_count,
                   COALESCE(SUM(l.has_questions), 0) AS questions_count
            FROM series s
            LEFT JOIN lessons l ON l.series_id = s.id
            WHERE s.sheikh_id = ?
            GROUP BY s.id
            ORDER BY s.order_no
            """,
            (sid,),
        ).fetchall()

        series_list = []
        total_lessons = 0
        total_playlist_lessons = 0
        unclassified_lessons = 0
        total_transcribed = 0
        total_summaries = 0
        total_questions = 0
        total_dur = 0

        for sr in sr_rows:
            s_id = sr["id"]
            sr_dict = dict(sr)
            if is_curated:
                is_uncl = "غير مصنف" in sr_dict["title"]
                yt_pl_id = None
                yt_pl_url = None
            else:
                is_uncl = sr_dict.get("yt_playlist_id") is None
                yt_pl_id = sr_dict.get("yt_playlist_id")
                yt_pl_url = sr_dict.get("yt_playlist_url")

            act = sr_dict["actual_count"]
            exp = sr_dict["expected_count"] or act
            missing_cnt = max(0, exp - act)
            avg_dur = round(sr_dict["total_duration"] / act) if act > 0 else 0

            total_lessons += act
            if is_uncl:
                unclassified_lessons += act
            else:
                total_playlist_lessons += act
            total_transcribed += sr_dict["transcribed_count"]
            total_summaries += sr_dict["summary_count"]
            total_questions += sr_dict["questions_count"]
            total_dur += sr_dict["total_duration"]

            s_item = {
                "id": s_id,
                "sheikh_id": sid,
                "sheikh_name": sh["name"],
                "sheikh_short": sh["short_name"],
                "order_no": sr_dict["order_no"],
                "title": sr_dict["title"],
                "yt_playlist_id": yt_pl_id,
                "yt_playlist_url": yt_pl_url,
                "is_unclassified": is_uncl,
                "state": sr_dict["state"],
                "expected_count": exp,
                "actual_count": act,
                "missing_count": missing_cnt,
                "transcribed_count": sr_dict["transcribed_count"],
                "summary_count": sr_dict["summary_count"],
                "questions_count": sr_dict["questions_count"],
                "total_duration": sr_dict["total_duration"],
                "avg_duration": avg_dur,
                "note": sr_dict["note"],
            }
            series_list.append(s_item)

            if is_curated:
                l_rows = conn.execute(
                    "SELECT order_no, display_no, is_child, parent_yt_id, title, yt_id, yt_title, yt_url, duration, has_transcript, has_summary, has_questions, has_challenges FROM lessons WHERE series_id = ? ORDER BY order_no",
                    (s_id,),
                ).fetchall()
            else:
                l_rows = conn.execute(
                    "SELECT order_no, title, yt_id, yt_title, yt_url, duration, has_transcript, has_summary, has_questions, has_challenges FROM lessons WHERE series_id = ? ORDER BY order_no",
                    (s_id,),
                ).fetchall()
            with open(os.path.join(series_dir, f"{s_id}.json"), "w", encoding="utf-8") as sf:
                json.dump(
                    {"series": s_item, "lessons": [dict(r) for r in l_rows]},
                    sf,
                    ensure_ascii=False,
                )

        sheikhs_out.append({
            "id": sid,
            "order_no": sh["order_no"],
            "name": sh["name"],
            "short_name": sh["short_name"],
            "photo": sh["photo"],
            "channels": [dict(c) for c in ch_rows],
            "playlists_count": sum(1 for x in series_list if not x["is_unclassified"]),
            "series_count": len(series_list),
            "playlist_lessons_count": total_playlist_lessons,
            "unclassified_count": unclassified_lessons,
            "total_lessons": total_lessons,
            "transcribed_count": total_transcribed,
            "summary_count": total_summaries,
            "questions_count": total_questions,
            "total_duration": total_dur,
            "series": series_list,
        })

    conn.close()
    catalog = {
        "v": 2,
        "mode": "curated" if is_curated else "raw",
        "totals": {
            "sheikhs": len(sheikhs_out),
            "curated_sheikhs": sum(1 for s in sheikhs_out if s["total_lessons"] > 0),
            "playlists": sum(s["playlists_count"] for s in sheikhs_out),
            "playlist_lessons": sum(s["playlist_lessons_count"] for s in sheikhs_out),
            "unclassified_lessons": sum(s["unclassified_count"] for s in sheikhs_out),
            "total_lessons": sum(s["total_lessons"] for s in sheikhs_out),
            "transcribed": sum(s["transcribed_count"] for s in sheikhs_out),
            "summaries": sum(s["summary_count"] for s in sheikhs_out),
            "questions": sum(s["questions_count"] for s in sheikhs_out),
        },
        "sheikhs": sheikhs_out,
    }
    tmp_out = catalog_out + ".tmp"
    with open(tmp_out, "w", encoding="utf-8") as cf:
        json.dump(catalog, cf, ensure_ascii=False, indent=2)
    os.replace(tmp_out, catalog_out)


def export_web_catalog(force_raw: bool = False):
    _export_single_db(
        CURATED_DB,
        os.path.join(BASE_DIR, "data", "catalog_curated.json"),
        os.path.join(BASE_DIR, "data", "series_curated"),
        is_curated=True,
    )
    if force_raw or not os.path.exists(os.path.join(BASE_DIR, "data", "catalog_raw.json")):
        _export_single_db(
            RAW_DB,
            os.path.join(BASE_DIR, "data", "catalog_raw.json"),
            os.path.join(BASE_DIR, "data", "series_raw"),
            is_curated=False,
        )


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "init"
    if cmd == "init":
        init_curated_db()
        for sid in ("sayed", "asimi", "bardoni", "jifri", "hafiz", "gomaa", "bouti", "shaarawy", "hawwa", "sariri", "omari", "hashemi", "kamali", "samarrai", "dedew"):
            dump_sheikh_for_analysis(sid)
        export_web_catalog(force_raw=True)
    elif cmd == "dump-sheikh":
        dump_sheikh_for_analysis(sys.argv[2])
    elif cmd == "import-sheikh":
        import_curated_sheikh(sys.argv[2])
    elif cmd == "export-web":
        export_web_catalog(force_raw=True)
        print("Exported both catalog_curated.json and catalog_raw.json with rich metadata.")
