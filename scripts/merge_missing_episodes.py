#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merges all newly discovered YouTube episodes and Archive.org episodes from
`data/missing_episodes_found.json` + `/tmp/archive_files_map.json` into
`data/curated_sheikhs/<sheikh_id>.json`, then re-imports the updated sheikhs
into `data/curated.db` and re-exports `data/catalog_curated.json`.
"""
import json
import os
import re
import subprocess
from collections import defaultdict

BASE_DIR = "/Users/macm1pro/REPOS/cheikh"
FOUND_JSON = os.path.join(BASE_DIR, "data", "missing_episodes_found.json")
ARCHIVE_MAP_JSON = "/tmp/archive_files_map.json"
CURATED_DIR = os.path.join(BASE_DIR, "data", "curated_sheikhs")

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
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
    "الحادي عشر": 11, "الحادية عشرة": 11,
    "الثاني عشر": 12, "الثانية عشرة": 12,
    "الثالث عشر": 13, "الثالثة عشرة": 13,
    "الرابع عشر": 14, "الرابعة عشرة": 14, "الرابعة عشر": 14,
    "الخامس عشر": 15, "الخامسة عشرة": 15,
    "السادس عشر": 16, "السادسة عشرة": 16,
    "السابع عشر": 17, "السابعة عشرة": 17,
    "الثامن عشر": 18, "الثامنة عشرة": 18,
    "التاسع عشر": 19, "التاسعة عشرة": 19,
    "العشرون": 20, "العشرين": 20,
}


def parse_hms(s) -> int | None:
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return int(s)
    s = str(s).strip()
    if s.isdigit():
        return int(s)
    m = re.search(r"(\d+:)?\d+:\d+", s)
    if not m:
        return None
    parts = [int(p) for p in m.group(0).split(":")]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return None


def parse_arabic_ordinal_phrase(text: str) -> int | None:
    t = text.translate(ARABIC_DIGITS)
    t = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", t)
    t_norm = re.sub(r"[أإآ]", "ا", t)

    units_map = {
        "الحادي": 1, "الحادية": 1, "واحد": 1, "الواحد": 1, "الواحدة": 1, "اول": 1, "الاول": 1, "الاولى": 1,
        "الثاني": 2, "الثانية": 2, "اثنان": 2, "اثنين": 2,
        "الثالث": 3, "الثالثة": 3, "ثلاث": 3, "ثلاثة": 3,
        "الرابع": 4, "الرابعة": 4, "اربع": 4, "اربعة": 4,
        "الخامس": 5, "الخامسة": 5, "خمس": 5, "خمسة": 5,
        "السادس": 6, "السادسة": 6, "ست": 6, "ستة": 6,
        "السابع": 7, "السابعة": 7, "سبع": 7, "سبعة": 7,
        "الثامن": 8, "الثامنة": 8, "ثمان": 8, "ثمانية": 8,
        "التاسع": 9, "التاسعة": 9, "تسع": 9, "تسعة": 9,
    }
    tens_map = {
        "العاشر": 10, "العاشرة": 10, "عشر": 10, "عشرة": 10,
        "العشرون": 20, "العشرين": 20, "عشرون": 20, "عشرين": 20,
        "الثلاثون": 30, "الثلاثين": 30, "ثلاثون": 30, "ثلاثين": 30,
        "الاربعون": 40, "الاربعين": 40, "اربعون": 40, "اربعين": 40,
        "الخمسون": 50, "الخمسين": 50, "خمسون": 50, "خمسين": 50,
        "الستون": 60, "الستين": 60, "ستون": 60, "ستين": 60,
        "السبعون": 70, "السبعين": 70, "سبعون": 70, "سبعين": 70,
        "الثمانون": 80, "الثمانين": 80, "ثمانون": 80, "ثمانين": 80,
        "التسعون": 90, "التسعين": 90, "تسعون": 90, "تسعين": 90,
    }
    hundreds_map = {
        "المائة": 100, "المئة": 100, "مائة": 100, "مئة": 100,
        "المائتين": 200, "المائتان": 200, "المئتين": 200, "المئتان": 200, "مائتين": 200, "مائتان": 200,
        "الثلاثمائة": 300, "ثلاثمائة": 300, "الثلاث مائة": 300, "ثلاث مائة": 300, "الثلاثمئة": 300,
        "الاربعمائة": 400, "اربعمائة": 400, "الاربع مائة": 400,
        "الخمسمائة": 500, "خمسمائة": 500,
    }

    matches = list(re.finditer(
        r"(?:^|\b)(?:الحلقة|الدرس|المجلس|اللقاء|المحاضرة|الجزء|لقاء|درس|مجلس|حلقة)\s+(?:العام\s+)?(.{3,55})",
        t_norm
    ))
    for m in matches:
        cand = re.split(r"[:\|\-–—\(\[\{«\"/]", m.group(1))[0]
        h_val = 0
        for hk, hv in sorted(hundreds_map.items(), key=lambda x: -len(x[0])):
            if re.search(r"(?:^|\s|و)" + re.escape(hk) + r"(?:\b|$)", cand):
                h_val = hv
                break
        t_val = 0
        for tk, tv in sorted(tens_map.items(), key=lambda x: -len(x[0])):
            if tv >= 20 and re.search(r"(?:^|\s|و)" + re.escape(tk) + r"(?:\b|$)", cand):
                t_val = tv
                break
        if t_val == 0:
            m_teen = re.search(
                r"(?:^|\s|و)(الحادي|الحادية|الثاني|الثانية|الثالث|الثالثة|الرابع|الرابعة|الخامس|الخامسة|السادس|السادسة|السابع|السابعة|الثامن|الثامنة|التاسع|التاسعة)\s+(عشر|عشرة)(?:\b|$)",
                cand
            )
            if m_teen:
                return h_val + 10 + units_map[m_teen.group(1)]
            if re.search(r"(?:^|\s|و)(العاشر|العاشرة)(?:\b|$)", cand):
                return h_val + 10
        u_val = 0
        for uk, uv in sorted(units_map.items(), key=lambda x: -len(x[0])):
            if re.search(r"(?:^|\s|و)" + re.escape(uk) + r"(?:\b|$)", cand):
                u_val = uv
                break
        total = h_val + t_val + u_val
        if total > 0:
            return total
    return None


def extract_ep_num(title: str, max_valid: int = 1500) -> int | None:
    if not title:
        return None
    t = title.translate(ARABIC_DIGITS)
    pats = [
        r"^\s*[\(\[\{]?\s*(\d{1,4})\s*[\)\]\}\-–—:]",
        r"(?:^|[\s\|\-–—\(\[\{👈])(?:الدرس|درس|المجلس|مجلس|الحلقة|حلقة|المحاضرة|محاضرة|لقاء|اللقاء|الجزء|رقم|ح)\s*(?:رقم\s*)?[:\-–—\(\[\{#]*\s*(\d{1,4})\b",
        r"(?:^|[\s\|\-–—\(\[\{])ج\s*[:\-–—\(\[\{#]*\s*(\d{1,4})\b",
        r"[\(\[\{]\s*(\d{1,4})\s*[\)\]\}]",
        r"#\s*(\d{1,4})\b",
        r"\b(\d{1,3})\s*$",
    ]
    for p in pats:
        m = re.search(p, t)
        if m:
            n = int(m.group(1))
            if 1 <= n <= max_valid and not (1400 <= n <= 1450) and not (1970 <= n <= 2030):
                return n
    ord_n = parse_arabic_ordinal_phrase(t)
    if ord_n is not None and 1 <= ord_n <= max_valid:
        return ord_n
    for word, num in sorted(ARABIC_ORDS.items(), key=lambda x: -len(x[0])):
        if word in t:
            return num
    return None


def sort_lessons_by_episode(lessons: list[dict], max_valid: int = 1500) -> list[dict]:
    """Sort lessons cleanly by extracted episode number when available, preserving relative order."""
    indexed = []
    for idx, l in enumerate(lessons):
        ep = l.get("_ep_hint")
        if not isinstance(ep, int):
            ep = extract_ep_num(l.get("title", ""), max_valid=max_valid)
        indexed.append((ep if ep is not None else 999999, idx, l))
    # Only sort by ep if at least half the lessons have an extracted episode number
    with_ep = sum(1 for x in indexed if x[0] != 999999)
    if with_ep >= max(2, len(lessons) // 2):
        indexed.sort(key=lambda x: (x[0], x[1]))
    out = []
    for _, _, l in indexed:
        l.pop("_ep_hint", None)
        out.append(l)
    return out


def main():
    found_data = json.load(open(FOUND_JSON, encoding="utf-8"))
    ar_map = json.load(open(ARCHIVE_MAP_JSON, encoding="utf-8")) if os.path.exists(ARCHIVE_MAP_JSON) else {}

    # Index Archive.org collections by episode number
    # 1. all-ahmed-sayed
    sayed_ar_by_prefix = {}
    for f in ar_map.get("all-ahmed-sayed", []):
        m = re.match(r"^(\d{3})\.", f["name"])
        if m:
            sayed_ar_by_prefix[int(m.group(1))] = f

    # 2. Dr.Alboty_RiyadAlsalheen
    bouti_riyad_ar = {}
    for f in ar_map.get("Dr.Alboty_RiyadAlsalheen", []):
        m = re.match(r"^(\d{3,4})-", f["name"])
        if m:
            bouti_riyad_ar[int(m.group(1))] = f

    # 3. 3ulumQuranButi (63 MP4 videos)
    bouti_ulum_ar = {}
    for f in ar_map.get("3ulumQuranButi", []):
        m = re.match(r"^(\d{1,2})-", f["name"])
        if m:
            bouti_ulum_ar[int(m.group(1))] = f

    # 4. Aqeeda28 (54 MP3 files)
    bouti_aqeeda_ar = {}
    for f in ar_map.get("Aqeeda28", []):
        m = re.search(r"\((\d+)\)", f["name"])
        if m:
            bouti_aqeeda_ar[int(m.group(1))] = f

    # 5. we-Nafs (23 MP4 files)
    hashemi_nafs_ar = {}
    for f in ar_map.get("we-Nafs", []):
        m = re.search(r"Nafs-0*(\d+)\.mp4", f["name"])
        if m:
            hashemi_nafs_ar[int(m.group(1))] = f

    # 6. al-mowataa_All (240 MP4 files) + char7.elmowata2 (263 MP3 titles)
    kamali_mowataa_mp4 = {}
    for f in ar_map.get("al-mowataa_All", []):
        m = re.search(r"\((\d+)\)\.mp4$", f["name"])
        if m:
            kamali_mowataa_mp4[int(m.group(1))] = f
    kamali_mowataa_titles = {}
    for f in ar_map.get("char7.elmowata2", []):
        m = re.match(r"^0*(\d+)\.mp3$", f["name"])
        if m:
            kamali_mowataa_titles[int(m.group(1))] = f["title"]

    # 7. LmsatEpisodesHD (MP4 and MP3 files for episodes 1..334)
    samarrai_lmsat_mp4 = {}
    for f in ar_map.get("LmsatEpisodesHD", []):
        if f["name"].lower().endswith((".mp4", ".mp3")):
            m = re.search(r"\(\s*0*(\d+)\s*\)", f["name"])
            if m:
                ep_n = int(m.group(1))
                if ep_n not in samarrai_lmsat_mp4 or f["name"].lower().endswith(".mp4"):
                    samarrai_lmsat_mp4[ep_n] = f

    # Group series_results by sheikh_id
    by_sheikh = defaultdict(list)
    for sr_res in found_data["series_results"]:
        by_sheikh[sr_res["sheikh_id"]].append(sr_res)

    modified_sheikhs = set()
    total_yt_added = 0
    total_ar_added = 0
    total_rounding_fixed = 0

    for sheikh_id, sr_results in by_sheikh.items():
        sh_path = os.path.join(CURATED_DIR, f"{sheikh_id}.json")
        if not os.path.exists(sh_path):
            continue
        sh_data = json.load(open(sh_path, encoding="utf-8"))
        series_map = {
            (s.get("id") or f"{sheikh_id}__s{idx:03d}"): s
            for idx, s in enumerate(sh_data.get("series", []), 1)
        }

        # Track all existing yt_ids across this sheikh to never violate UNIQUE(sheikh_id, yt_id)
        existing_yt_ids = set()
        for s in sh_data.get("series", []):
            for l in s.get("lessons", []):
                if l.get("yt_id"):
                    existing_yt_ids.add(l["yt_id"])

        for res in sr_results:
            sid = res["series_id"]
            sr = series_map.get(sid)
            if not sr:
                continue

            status = res["status"]
            lessons = sr.get("lessons", [])
            added_here_yt = 0
            added_here_ar = 0

            # 1. Add newly discovered YouTube videos (excluding full-series merged duplicates if individual episodes exist)
            yt_candidates = [v for v in res.get("found_youtube_videos", []) if not v.get("in_db")]
            for v in yt_candidates:
                ep_str = str(v.get("episode_number", ""))
                # Skip merged multi-episode videos if we already have the individual episodes
                if "مدمج" in ep_str or "نسخة ثانية" in ep_str:
                    continue
                vid = v.get("yt_id")
                if not vid or vid in existing_yt_ids:
                    continue
                existing_yt_ids.add(vid)
                ep_int = int(ep_str) if ep_str.isdigit() else extract_ep_num(v.get("title", ""))
                lessons.append({
                    "yt_id": vid,
                    "title": v.get("title") or f"الدرس {ep_str}",
                    "yt_url": v.get("yt_url") or f"https://www.youtube.com/watch?v={vid}",
                    "duration": parse_hms(v.get("duration")),
                    "_ep_hint": ep_int,
                })
                added_here_yt += 1
                total_yt_added += 1

            # 2. Add Archive.org episodes for specific series where episodes are missing from YouTube
            if sid == "sayed__s047" and 20 in sayed_ar_by_prefix:
                f = sayed_ar_by_prefix[20]
                aid = "archive__sayed__s047__ep05"
                if aid not in existing_yt_ids:
                    existing_yt_ids.add(aid)
                    lessons.append({
                        "yt_id": aid,
                        "title": "دورة في علم الحديث على منهج المتقدمين | ج5 | اتصال الإسناد (1) [مستدرك من أرشيف الإنترنت]",
                        "yt_url": f["url"],
                        "duration": f["duration"],
                        "_ep_hint": 5,
                    })
                    added_here_ar += 1
                    total_ar_added += 1

            elif sid == "sayed__s092" and 382 in sayed_ar_by_prefix:
                f = sayed_ar_by_prefix[382]
                aid = "archive__sayed__s092__ep03"
                if aid not in existing_yt_ids:
                    existing_yt_ids.add(aid)
                    lessons.append({
                        "yt_id": aid,
                        "title": "أبجديات الثقافة للجيل | ابن العربي | شخصيات وقدوات (3) [مستدرك من أرشيف الإنترنت]",
                        "yt_url": f["url"],
                        "duration": f["duration"],
                        "_ep_hint": 8,
                    })
                    added_here_ar += 1
                    total_ar_added += 1

            elif sid == "sayed__s098" and 253 in sayed_ar_by_prefix:
                f = sayed_ar_by_prefix[253]
                aid = "archive__sayed__s098__ep05"
                if aid not in existing_yt_ids:
                    existing_yt_ids.add(aid)
                    lessons.append({
                        "yt_id": aid,
                        "title": "إلى الجيل الصاعد (5) | تحدي الشهوة والحب والزواج [مستدرك من أرشيف الإنترنت]",
                        "yt_url": f["url"],
                        "duration": f["duration"],
                        "_ep_hint": 5,
                    })
                    added_here_ar += 1
                    total_ar_added += 1

            elif sid == "bouti__s020" and 965 in bouti_riyad_ar:
                f = bouti_riyad_ar[965]
                aid = "archive__bouti__s020__ep965"
                if aid not in existing_yt_ids:
                    existing_yt_ids.add(aid)
                    lessons.append({
                        "yt_id": aid,
                        "title": "965 - شرح رياض الصالحين | كراهة تفضيل الوالد بعض أولاده على بعض في الهبة [مستدرك من أرشيف الإنترنت]",
                        "yt_url": f["url"],
                        "duration": f["duration"],
                        "_ep_hint": 965,
                    })
                    added_here_ar += 1
                    total_ar_added += 1

            elif sid == "bouti__s033":
                hikam_missing = [
                    (48, "الحكم العطائية للعلامة البوطي | الدرس 48 - الحكمة 30 و31 [مستدرك من أرشيف الإنترنت]", "https://archive.org/download/AlHekamAlataeiah/048.mp3"),
                    (179, "الحكم العطائية للعلامة البوطي | الدرس 179 - الحكمة 153 [مستدرك من أرشيف الإنترنت]", "https://archive.org/download/AlHekamAlataeiah2/179.mp3"),
                    (304, "الحكم العطائية للعلامة البوطي | الدرس 304 - المناجاة 27 و28 [مستدرك من أرشيف الإنترنت]", "https://archive.org/download/AlHekamAlataeiah2/304.mp3"),
                ]
                for ep_n, h_title, h_url in hikam_missing:
                    aid = f"archive__bouti__s033__ep{ep_n:03d}"
                    if aid not in existing_yt_ids:
                        existing_yt_ids.add(aid)
                        lessons.append({
                            "yt_id": aid,
                            "title": h_title,
                            "yt_url": h_url,
                            "duration": 2700,
                            "_ep_hint": ep_n,
                        })
                        added_here_ar += 1
                        total_ar_added += 1

            elif sid == "bouti__s071" and bouti_ulum_ar:
                present_eps = {extract_ep_num(l["title"]) for l in lessons if extract_ep_num(l["title"]) is not None}
                for ep_n, f in sorted(bouti_ulum_ar.items()):
                    if ep_n not in present_eps:
                        aid = f"archive__bouti__s071__ep{ep_n:02d}"
                        if aid not in existing_yt_ids:
                            existing_yt_ids.add(aid)
                            lessons.append({
                                "yt_id": aid,
                                "title": f"{f['title']} [فيديو مستدرك من أرشيف الإنترنت]",
                                "yt_url": f["url"],
                                "duration": f["duration"],
                                "_ep_hint": ep_n,
                            })
                            added_here_ar += 1
                            total_ar_added += 1

            elif sid == "bouti__s069" and bouti_aqeeda_ar:
                present_eps = {extract_ep_num(l["title"]) for l in lessons if extract_ep_num(l["title"]) is not None}
                for ep_n in range(1, 49):
                    if ep_n not in present_eps and ep_n in bouti_aqeeda_ar:
                        f = bouti_aqeeda_ar[ep_n]
                        aid = f"archive__bouti__s069__ep{ep_n:02d}"
                        if aid not in existing_yt_ids:
                            existing_yt_ids.add(aid)
                            lessons.append({
                                "yt_id": aid,
                                "title": f"شرح كتاب كبرى اليقينيات الكونية - الدرس ({ep_n}) [مستدرك من أرشيف الإنترنت]",
                                "yt_url": f["url"],
                                "duration": f["duration"],
                                "_ep_hint": ep_n,
                            })
                            added_here_ar += 1
                            total_ar_added += 1

            elif sid == "hashemi__s054" and 19 in hashemi_nafs_ar:
                f = hashemi_nafs_ar[19]
                aid = "archive__hashemi__s054__ep18"
                if aid not in existing_yt_ids:
                    existing_yt_ids.add(aid)
                    lessons.append({
                        "yt_id": aid,
                        "title": "برنامج ونفس | الحلقة (18): فقه الوضوء والطهارة والغسل [فيديو مستدرك من أرشيف الإنترنت]",
                        "yt_url": f["url"],
                        "duration": f["duration"],
                        "_ep_hint": 18,
                    })
                    added_here_ar += 1
                    total_ar_added += 1

            elif sid == "kamali__s001" and kamali_mowataa_mp4:
                present_eps = {
                    l.get("_ep_hint") or extract_ep_num(l["title"])
                    for l in lessons
                    if (l.get("_ep_hint") or extract_ep_num(l["title"])) is not None
                }
                for ep_n in range(1, 195):
                    if ep_n not in present_eps and ep_n in kamali_mowataa_mp4:
                        f = kamali_mowataa_mp4[ep_n]
                        sub_t = kamali_mowataa_titles.get(ep_n, "")
                        sub_str = f" — {sub_t}" if sub_t else ""
                        aid = f"archive__kamali__s001__ep{ep_n:03d}"
                        if aid not in existing_yt_ids:
                            existing_yt_ids.add(aid)
                            lessons.append({
                                "yt_id": aid,
                                "title": f"شرح موطأ الإمام مالك - المجلس ({ep_n}){sub_str} [فيديو مستدرك من أرشيف الإنترنت]",
                                "yt_url": f["url"],
                                "duration": f["duration"],
                                "_ep_hint": ep_n,
                            })
                            added_here_ar += 1
                            total_ar_added += 1

            elif sid == "samarrai__s065" and samarrai_lmsat_mp4:
                present_eps = {
                    l.get("_ep_hint") or extract_ep_num(l["title"])
                    for l in lessons
                    if (l.get("_ep_hint") or extract_ep_num(l["title"])) is not None
                }
                for ep_n in range(1, 255):
                    if ep_n not in present_eps and ep_n in samarrai_lmsat_mp4:
                        f = samarrai_lmsat_mp4[ep_n]
                        aid = f"archive__samarrai__s065__ep{ep_n:03d}"
                        if aid not in existing_yt_ids:
                            existing_yt_ids.add(aid)
                            lessons.append({
                                "yt_id": aid,
                                "title": f"{f['title']} [فيديو مستدرك من أرشيف الإنترنت]",
                                "yt_url": f["url"],
                                "duration": f["duration"],
                                "_ep_hint": ep_n,
                            })
                            added_here_ar += 1
                            total_ar_added += 1

            # Sort lessons if we added anything
            if added_here_yt > 0 or added_here_ar > 0:
                sr["lessons"] = sort_lessons_by_episode(lessons, max_valid=max(1500, sr.get("expected_count") or 0))
                modified_sheikhs.add(sheikh_id)

            # Update expected_count and note
            new_actual = len(sr["lessons"])
            if status in ("rounding_estimate_no_missing", "numbering_skip_confirmed", "found_complete"):
                if sr.get("expected_count") != new_actual:
                    sr["expected_count"] = new_actual
                    total_rounding_fixed += 1
                    modified_sheikhs.add(sheikh_id)
                if status == "found_complete" and sr.get("state") == "stopped":
                    sr["state"] = "completed"
            elif new_actual > (sr.get("expected_count") or 0):
                sr["expected_count"] = new_actual
                modified_sheikhs.add(sheikh_id)

            if added_here_yt > 0 or added_here_ar > 0 or status == "numbering_skip_confirmed":
                parts = []
                if added_here_yt > 0:
                    parts.append(f"تم استدراك {added_here_yt} حلقة من قنوات يوتيوب أخرى")
                if added_here_ar > 0:
                    parts.append(f"تم استدراك {added_here_ar} حلقة من أرشيف الإنترنت (Archive.org)")
                if status == "numbering_skip_confirmed":
                    parts.append(res.get("resolution_summary", ""))
                suffix = " · ".join(p for p in parts if p)
                if suffix and suffix not in (sr.get("note") or ""):
                    sr["note"] = ((sr.get("note") or "").rstrip(" .") + " — " + suffix).strip(" —")
                    modified_sheikhs.add(sheikh_id)

        if sheikh_id in modified_sheikhs:
            with open(sh_path, "w", encoding="utf-8") as f:
                json.dump(sh_data, f, ensure_ascii=False, indent=2)

    print(
        f"Updated {len(modified_sheikhs)} sheikh JSON files: "
        f"+{total_yt_added} YouTube episodes, +{total_ar_added} Archive.org episodes, "
        f"{total_rounding_fixed} series expected_count synchronized."
    )

    for sh_id in sorted(modified_sheikhs):
        subprocess.run(["python3", "scripts/curated_tools.py", "import-sheikh", sh_id], cwd=BASE_DIR, check=True)


if __name__ == "__main__":
    main()
