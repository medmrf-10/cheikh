#!/usr/bin/env python3
"""
Imports all data/full_channels/*.json + data/existing_inventory.json into:
1. SQLite database: data/cheikh.db (sheikhs, channels, series, lessons)
2. Static PWA JSONs: data/catalog.json + data/series/<series_id>.json
3. Analytical Markdown report: docs/ANALYSIS_REPORT.md
"""
import glob
import json
import os
import re
import sqlite3
from collections import defaultdict

BASE_DIR = "/Users/macm1pro/REPOS/cheikh"
DB_PATH = os.path.join(BASE_DIR, "data", "cheikh.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "data", "schema.sql")
INV_PATH = os.path.join(BASE_DIR, "data", "existing_inventory.json")
FULL_DIR = os.path.join(BASE_DIR, "data", "full_channels")
SERIES_OUT_DIR = os.path.join(BASE_DIR, "data", "series")
CATALOG_OUT = os.path.join(BASE_DIR, "data", "catalog.json")
REPORT_OUT = os.path.join(BASE_DIR, "docs", "ANALYSIS_REPORT.md")

SHEIKH_PHOTOS = {
    "sayed": "https://medmrf-10.github.io/hawshat/playlists/img/ahmed-alsayed.jpg",
    "asimi": "https://medmrf-10.github.io/hawshat/playlists/img/adham-alasimi.jpg",
    "bardoni": "https://medmrf-10.github.io/hawshat/playlists/img/bardouni-husaymi.jpg",
    "jifri": "https://medmrf-10.github.io/hawshat/playlists/img/habib-ali-aljifri.jpg",
    "hafiz": "https://medmrf-10.github.io/hawshat/playlists/img/habib-omar-ibn-hafiz.jpg",
    "gomaa": "https://medmrf-10.github.io/hawshat/playlists/img/ali-gomaa.jpg",
    "bouti": "https://medmrf-10.github.io/hawshat/playlists/img/said-bouti.jpg",
    "shaarawy": "https://medmrf-10.github.io/hawshat/playlists/img/sharawi.jpg",
    "hawwa": "https://medmrf-10.github.io/hawshat/playlists/img/maath-hawa.jpg",
    "sariri": "https://medmrf-10.github.io/hawshat/playlists/img/mouloud-sariri.jpg",
    "omari": "https://medmrf-10.github.io/hawshat/playlists/img/ali-mahmoud-alomari.jpg",
    "hashemi": "https://medmrf-10.github.io/hawshat/playlists/img/dhaker-alhashimi.jpg",
    "kamali": "https://medmrf-10.github.io/hawshat/playlists/img/said-kamali.jpg",
    "samarrai": "https://medmrf-10.github.io/hawshat/playlists/img/fadhel-samarrai.jpg",
    "ayman": "https://medmrf-10.github.io/hawshat/playlists/img/ayman-abdelrahim.jpg",
    "dedew": "https://medmrf-10.github.io/hawshat/playlists/img/daddo.jpg",
    "alihani": "https://yt3.googleusercontent.com/dNA40wR5QtnNoK1ilEriqsLa16RdGAXBgN-dXxDQzF0CxP5ET9itcRC4gjPRPL99kuHFsO4ApA=s900-c-k-c0x00ffffff-no-rj",
}

ARABIC_ORDS = {
    "الأول": 1, "الاول": 1, "الأولى": 1, "الاولى": 1,
    "الثاني": 2, "الثانية": 2,
    "الثالث": 3, "الثالثة": 3,
    "الرابع": 4, "الرابعة": 4,
    "الخامس": 5, "الخامسة": 5,
    "السادس": 6, "السادسة": 6,
    "السابع": 7, "السابعة": 7,
    "الثامن": 8, "الثامنة": 8,
    "التاسع": 9, "التاسعة": 9,
    "العاشر": 10, "العاشرة": 10,
}

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def extract_episode_number(title: str) -> int | None:
    if not title:
        return None
    t = title.translate(ARABIC_DIGITS)
    # Explicit patterns like: الدرس (12) / المجلس 12 / الحلقة 12 / ( 12 ) / [12] / - 12 -
    pats = [
        r"(?:الدرس|درس|المجلس|مجلس|الحلقة|حلقة|المحاضرة|محاضرة|لقاء|اللقاء)\s*[:\-–—\(\[\{]*\s*(\d{1,4})\b",
        r"^\s*[\(\[\{]?\s*(\d{1,4})\s*[\)\]\}\-–—:]",
        r"[\(\[\{]\s*(\d{1,4})\s*[\)\]\}]",
        r"(?:رقم|#)\s*(\d{1,4})\b",
    ]
    for p in pats:
        m = re.search(p, t)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 1500 and not (1400 <= n <= 1450) and not (1970 <= n <= 2030):
                return n
    for word, num in ARABIC_ORDS.items():
        if re.search(r"\b" + word + r"\b", t):
            return num
    return None


def attribute_tankert_owner(title: str, videos: list[dict]) -> str:
    """Attribute a playlist or video on Tankert shared channel to 'bardoni' or 'sariri'."""
    combined = (title or "") + " " + " ".join((v.get("title") or "") for v in videos[:25])
    if "البردوني" in combined or "الحسيمي" in combined:
        return "bardoni"
    if "السريري" in combined or "مولود" in combined:
        return "sariri"
    bardoni_kw = ["الأشموني", "الاشموني", "اليوسي", "السنوسي", "السجاعي", "الأجهوري", "الاجهوري", "لامية العرب", "آداب البحث", "اداب البحث", "السلم المنورق", "أم البراهين", "ام البراهين"]
    sariri_kw = ["مختصر خليل", "جمع الجوامع", "تحفة الحكام", "الزقاقية", "ابن عاشر", "الموطأ", "القواعد الفقهية", "بداية المجتهد", "التسهيل"]
    for kw in bardoni_kw:
        if kw in combined:
            return "bardoni"
    for kw in sariri_kw:
        if kw in combined:
            return "sariri"
    return "sariri"


def classify_playlist_kind(title: str, videos: list[dict]) -> str:
    t = title or ""
    if any(w in t for w in ("مقتطفات", "فوائد", "شذرات", "درر", "لطائف", "قصيرة", "مقاطع", "تأملات قصيرة", "ومضات", "خواطر قصيرة", "Shorts")):
        return "مقتطفات وفوائد"
    if any(w in t for w in ("خطب", "خطبة", "مواعظ", "موعظة")):
        return "خطب ومواعظ"
    if any(w in t for w in ("فتاوى", "فتوى", "أسئلة", "سؤال وجواب", "لقاء", "لقاءات", "حوار", "ندوة", "برنامج")):
        return "فتاوى ولقاءات"
    return "شرح / سلسلة علمية"


FINAL_LESSON_PAT = re.compile(
    r"(?:الدرس|المجلس|الحلقة|المحاضرة|اللقاء)\s*(?:الأخير|الاخير|الأخيرة|الاخيرة|الختامي|الختامية)"
    r"|ختام\s+(?:شرح|سلسلة|كتاب|دروس|مجالس)"
    r"|تم\s+بحمد\s+الله"
)


def analyze_playlist(title: str, videos: list[dict]) -> tuple[str, int | None, str]:
    """
    Returns (state, expected_count, note) for a playlist.
    state in ('completed', 'ongoing', 'stopped')
    """
    n = len(videos)
    if n == 0:
        return "stopped", 0, "قائمة فارغة على يوتيوب"

    kind = classify_playlist_kind(title, videos)
    nums = []
    for v in videos:
        vt = v.get("title") or ""
        ep = extract_episode_number(vt)
        if ep is not None:
            nums.append(ep)

    # Check only the boundary videos (first 2 and last 2, in case playlist is ordered asc or desc)
    boundary_videos = videos[:2] + videos[-2:] if n > 4 else videos
    has_final_marker = any(bool(FINAL_LESSON_PAT.search(v.get("title") or "")) for v in boundary_videos)

    max_ep = max(nums) if nums else None
    # Filter out anomalous max_ep if only a few videos matched a huge number while n is small
    if max_ep and max_ep > n * 3 and len(nums) < max(3, n // 2):
        max_ep = None

    if kind == "مقتطفات وفوائد":
        expected = n
        state = "completed"
        return state, expected, f"تصنيف: {kind}"

    if max_ep and max_ep >= n and len(nums) >= max(2, n // 3):
        expected = max_ep
    else:
        expected = n

    missing_cnt = max(0, expected - n)
    if has_final_marker:
        state = "completed"
    elif missing_cnt > max(5, expected // 3):
        state = "stopped"
    else:
        state = "completed"

    notes = [f"تصنيف: {kind}"]
    if max_ep and missing_cnt > 0:
        notes.append(f"أعلى رقم درس مرصود ({max_ep}) مقابل ({n}) فيديو متاح (فرق {missing_cnt})")
    if has_final_marker:
        notes.append("يوجد درس ختامي صريح")
    return state, expected, " · ".join(notes) if notes else None



def main():
    inv = {"videos": {}}
    if os.path.exists(INV_PATH):
        inv = json.load(open(INV_PATH, encoding="utf-8"))
    inv_vids = inv.get("videos", {})

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())

    # Update photos on sheikhs
    for sid, photo in SHEIKH_PHOTOS.items():
        conn.execute("UPDATE sheikhs SET photo = ? WHERE id = ?", (photo, sid))

    channel_files = sorted(glob.glob(os.path.join(FULL_DIR, "*.json")))
    sheikh_order_counter = defaultdict(int)
    seen_series_ids = set()

    for fp in channel_files:
        cdata = json.load(open(fp, encoding="utf-8"))
        ch_key = cdata["channel_key"]
        default_sheikh = cdata["sheikh_id"]
        ch_id = cdata.get("channel_id")

        # Update yt_channel_id in channels table if resolved
        if ch_id:
            if ch_key == "tankert-shared":
                conn.execute("UPDATE channels SET yt_channel_id = ? WHERE id IN ('bardoni-shared', 'sariri-shared')", (ch_id,))
            else:
                conn.execute("UPDATE channels SET yt_channel_id = ? WHERE id = ? OR sheikh_id = ? AND yt_channel_id IS NULL", (ch_id, ch_key, default_sheikh))

        # Process playlists
        for pl in cdata.get("playlists", []):
            pid = pl["playlist_id"]
            ptitle = (pl.get("title") or "").strip() or pid
            purl = pl.get("url") or f"https://www.youtube.com/playlist?list={pid}"
            vids = pl.get("videos") or []

            if ch_key == "tankert-shared":
                owner = attribute_tankert_owner(ptitle, vids)
                db_channel_id = "bardoni-shared" if owner == "bardoni" else "sariri-shared"
            elif ch_key == "bardoni-personal":
                owner = "bardoni"
                db_channel_id = "bardoni-personal"
            elif ch_key == "sariri-personal":
                owner = "sariri"
                db_channel_id = "sariri-personal"
            else:
                owner = default_sheikh
                db_channel_id = ch_key

            series_id = pid if pid not in seen_series_ids else f"{owner}__{pid}"
            seen_series_ids.add(series_id)
            sheikh_order_counter[owner] += 1
            s_order = sheikh_order_counter[owner]

            state, expected_count, note = analyze_playlist(ptitle, vids)
            conn.execute(
                """
                INSERT INTO series (id, sheikh_id, channel_id, order_no, title, yt_playlist_id, yt_playlist_url, state, expected_count, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (series_id, owner, db_channel_id, s_order, ptitle, pid, purl, state, expected_count, note),
            )

            for idx, v in enumerate(vids, 1):
                vid = v["yt_id"]
                l_id = f"{series_id}__{idx:04d}__{vid}"
                vtitle = (v.get("title") or "").strip() or f"الدرس {idx}"
                vurl = v.get("url") or f"https://www.youtube.com/watch?v={vid}"
                dur = v.get("duration")
                assets = inv_vids.get(vid, {})
                has_t = 1 if assets.get("t") else 0
                has_s = 1 if assets.get("s") else 0
                has_q = 1 if assets.get("q") else 0
                conn.execute(
                    """
                    INSERT INTO lessons (id, series_id, sheikh_id, order_no, title, yt_id, yt_title, yt_url, duration, has_transcript, has_summary, has_questions, has_challenges)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """,
                    (l_id, series_id, owner, idx, vtitle, vid, vtitle, vurl, dur, has_t, has_s, has_q),
                )

        # Process unclassified videos ("غير مصنف")
        uncl = cdata.get("unclassified_playlist", {}).get("videos") or []
        if uncl:
            if ch_key == "tankert-shared":
                # Split unclassified videos on shared channel between Bardoni and Sariri
                by_owner = {"bardoni": [], "sariri": []}
                for v in uncl:
                    ow = attribute_tankert_owner(v.get("title") or "", [v])
                    by_owner[ow].append(v)
                for ow, ovids in by_owner.items():
                    if not ovids:
                        continue
                    db_ch = "bardoni-shared" if ow == "bardoni" else "sariri-shared"
                    sid = f"{ow}__tankert_unclassified"
                    sheikh_order_counter[ow] += 1
                    conn.execute(
                        """
                        INSERT INTO series (id, sheikh_id, channel_id, order_no, title, yt_playlist_id, yt_playlist_url, state, expected_count, note)
                        VALUES (?, ?, ?, ?, ?, NULL, NULL, 'ongoing', ?, 'فيديوهات منشورة في القناة المشتركة خارج قوائم التشغيل')
                        """,
                        (sid, ow, db_ch, sheikh_order_counter[ow], "غير مصنف (قناة مدرسة تنكرت)", len(ovids)),
                    )
                    for idx, v in enumerate(ovids, 1):
                        vid = v["yt_id"]
                        l_id = f"{sid}__{idx:04d}__{vid}"
                        vtitle = (v.get("title") or "").strip() or f"فيديو {idx}"
                        vurl = v.get("url") or f"https://www.youtube.com/watch?v={vid}"
                        dur = v.get("duration")
                        assets = inv_vids.get(vid, {})
                        conn.execute(
                            """
                            INSERT INTO lessons (id, series_id, sheikh_id, order_no, title, yt_id, yt_title, yt_url, duration, has_transcript, has_summary, has_questions, has_challenges)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                            """,
                            (
                                l_id, sid, ow, idx, vtitle, vid, vtitle, vurl, dur,
                                1 if assets.get("t") else 0,
                                1 if assets.get("s") else 0,
                                1 if assets.get("q") else 0,
                            ),
                        )
            else:
                owner = default_sheikh
                db_ch = ch_key
                sid = f"{ch_key}__unclassified"
                sheikh_order_counter[owner] += 1
                label = "غير مصنف" if ch_key.endswith("-main") else f"غير مصنف ({ch_key})"
                conn.execute(
                    """
                    INSERT INTO series (id, sheikh_id, channel_id, order_no, title, yt_playlist_id, yt_playlist_url, state, expected_count, note)
                    VALUES (?, ?, ?, ?, ?, NULL, NULL, 'ongoing', ?, 'فيديوهات منشورة في القناة ولم تُدرج في أي قائمة تشغيل')
                    """,
                    (sid, owner, db_ch, sheikh_order_counter[owner], label, len(uncl)),
                )
                for idx, v in enumerate(uncl, 1):
                    vid = v["yt_id"]
                    l_id = f"{sid}__{idx:04d}__{vid}"
                    vtitle = (v.get("title") or "").strip() or f"فيديو {idx}"
                    vurl = v.get("url") or f"https://www.youtube.com/watch?v={vid}"
                    dur = v.get("duration")
                    assets = inv_vids.get(vid, {})
                    conn.execute(
                        """
                        INSERT INTO lessons (id, series_id, sheikh_id, order_no, title, yt_id, yt_title, yt_url, duration, has_transcript, has_summary, has_questions, has_challenges)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        """,
                        (
                            l_id, sid, owner, idx, vtitle, vid, vtitle, vurl, dur,
                            1 if assets.get("t") else 0,
                            1 if assets.get("s") else 0,
                            1 if assets.get("q") else 0,
                        ),
                    )

    conn.commit()

    # Export data/catalog.json and data/series/<series_id>.json
    os.makedirs(SERIES_OUT_DIR, exist_ok=True)
    sheikhs_out = []
    sheikh_rows = conn.execute("SELECT * FROM sheikhs ORDER BY order_no").fetchall()

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
            is_uncl = sr["yt_playlist_id"] is None
            act = sr["actual_count"]
            total_lessons += act
            if is_uncl:
                unclassified_lessons += act
            else:
                total_playlist_lessons += act
            total_transcribed += sr["transcribed_count"]
            total_summaries += sr["summary_count"]
            total_questions += sr["questions_count"]
            total_dur += sr["total_duration"]

            s_item = {
                "id": s_id,
                "order_no": sr["order_no"],
                "title": sr["title"],
                "channel_id": sr["channel_id"],
                "yt_playlist_id": sr["yt_playlist_id"],
                "yt_playlist_url": sr["yt_playlist_url"],
                "is_unclassified": is_uncl,
                "state": sr["state"],
                "expected_count": sr["expected_count"],
                "actual_count": act,
                "transcribed_count": sr["transcribed_count"],
                "summary_count": sr["summary_count"],
                "questions_count": sr["questions_count"],
                "total_duration": sr["total_duration"],
                "note": sr["note"],
            }
            series_list.append(s_item)

            # Write per-series lessons JSON
            l_rows = conn.execute(
                "SELECT order_no, title, yt_id, yt_url, duration, has_transcript, has_summary, has_questions, has_challenges FROM lessons WHERE series_id = ? ORDER BY order_no",
                (s_id,),
            ).fetchall()
            with open(os.path.join(SERIES_OUT_DIR, f"{s_id}.json"), "w", encoding="utf-8") as sf:
                json.dump(
                    {
                        "series": s_item,
                        "lessons": [dict(r) for r in l_rows],
                    },
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

    catalog = {
        "v": 1,
        "totals": {
            "sheikhs": len(sheikhs_out),
            "playlists": sum(s["playlists_count"] for s in sheikhs_out),
            "playlist_lessons": sum(s["playlist_lessons_count"] for s in sheikhs_out),
            "unclassified_lessons": sum(s["unclassified_lessons"] if "unclassified_lessons" in s else s["unclassified_count"] for s in sheikhs_out),
            "total_lessons": sum(s["total_lessons"] for s in sheikhs_out),
            "transcribed": sum(s["transcribed_count"] for s in sheikhs_out),
            "summaries": sum(s["summary_count"] for s in sheikhs_out),
            "questions": sum(s["questions_count"] for s in sheikhs_out),
        },
        "sheikhs": sheikhs_out,
    }
    with open(CATALOG_OUT, "w", encoding="utf-8") as cf:
        json.dump(catalog, cf, ensure_ascii=False, indent=2)

    # Generate docs/ANALYSIS_REPORT.md
    os.makedirs(os.path.dirname(REPORT_OUT), exist_ok=True)
    lines = [
        "# التقرير الشامل لجرد وتحليل قنوات المشايخ الـ 16 (`cheikh.db`)",
        "",
        "## 1. الإجماليات العامة",
        f"- **عدد المشايخ المعتمدين:** {catalog['totals']['sheikhs']} شيخاً (15 عبر قنوات يوتيوب + أيمن عبد الرحيم مؤجل المحتوى).",
        f"- **إجمالي قوائم التشغيل (`Playlists`):** {catalog['totals']['playlists']:,} قائمة.",
        f"- **إجمالي الدروس داخل القوائم:** {catalog['totals']['playlist_lessons']:,} فيديو.",
        f"- **إجمالي الفيديوهات في «غير مصنف» (خارج القوائم):** {catalog['totals']['unclassified_lessons']:,} فيديو.",
        f"- **المجموع الكلي للفيديوهات المحفوظة في جدول `lessons`:** {catalog['totals']['total_lessons']:,} درس/فيديو.",
        f"- **المفرّغ منها سابقاً (`has_transcript = 1`):** {catalog['totals']['transcribed']:,} درس.",
        f"- **المتوفر له ملخص (`has_summary = 1`):** {catalog['totals']['summaries']:,} درس.",
        f"- **المتوفر له أسئلة (`has_questions = 1`):** {catalog['totals']['questions']:,} درس.",
        "",
        "---",
        "",
        "## 2. جدول المشايخ الـ 16 بالتفصيل",
        "",
        "| # | الشيخ | المعرّف | القوائم | دروس القوائم | غير مصنف | الإجمالي | المفرّغ سابقاً | الملخصات | الأسئلة | الساعات |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in sheikhs_out:
        hrs = round(s["total_duration"] / 3600, 1)
        lines.append(
            f"| {s['order_no']} | {s['name']} | `{s['id']}` | {s['playlists_count']:,} | "
            f"{s['playlist_lessons_count']:,} | {s['unclassified_count']:,} | **{s['total_lessons']:,}** | "
            f"{s['transcribed_count']:,} | {s['summary_count']:,} | {s['questions_count']:,} | {hrs:,} |"
        )

    lines.extend(["", "---", "", "## 3. أبرز السلاسل والتحليل لكل شيخ", ""])
    for s in sheikhs_out:
        lines.append(f"### {s['order_no']}. {s['name']} (`{s['id']}`)")
        if not s["series"]:
            lines.append("- *مؤجل المحتوى حالياً بأمر المالك.*")
            lines.append("")
            continue
        lines.append(
            f"- **القوائم:** {s['playlists_count']} قائمة ({s['playlist_lessons_count']:,} درس) · "
            f"**غير مصنف:** {s['unclassified_count']:,} فيديو · **المفرّغ:** {s['transcribed_count']:,}"
        )
        top_sr = [x for x in s["series"] if not x["is_unclassified"]]
        top_sr.sort(key=lambda x: (x["transcribed_count"], x["actual_count"]), reverse=True)
        if top_sr:
            lines.append("")
            lines.append("| السلسلة | الحالة | المفترض | الفعلي | المفرّغ | ملاحظة |")
            lines.append("|---|---|---:|---:|---:|---|")
            for sr in top_sr[:12]:
                safe_title = (sr["title"] or "").replace("|", "·")
                safe_note = (sr["note"] or "—").replace("|", "·")
                lines.append(
                    f"| {safe_title} | `{sr['state']}` | {sr['expected_count'] or '—'} | "
                    f"{sr['actual_count']} | {sr['transcribed_count']} | {safe_note} |"
                )
        lines.append("")

    with open(REPORT_OUT, "w", encoding="utf-8") as rf:
        rf.write("\n".join(lines))

    print(
        f"DB & Catalog built: {catalog['totals']['playlists']} playlists, "
        f"{catalog['totals']['total_lessons']} lessons ({catalog['totals']['unclassified_lessons']} unclassified), "
        f"{catalog['totals']['transcribed']} transcribed."
    )


if __name__ == "__main__":
    main()
