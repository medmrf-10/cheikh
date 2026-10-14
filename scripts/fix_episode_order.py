#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixes episode ordering across all affected series in `data/curated_sheikhs/*.json`
and adds the 2 remaining MP3 episodes (235, 241) from Archive.org `LmsatEpisodesHD`
into `samarrai__s065`.
"""
import json
import os
import re
from pathlib import Path

BASE_DIR = Path("/Users/macm1pro/REPOS/cheikh")
CURATED_DIR = BASE_DIR / "data" / "curated_sheikhs"
ARCHIVE_MAP_JSON = Path("/tmp/archive_files_map.json")

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_ar(s: str) -> str:
    s = s.translate(ARABIC_DIGITS)
    s = re.sub(r"[\u064B-\u065F\u0670\u0640\u200b\u200c\u200d\u200e\u200f\ufeff]", "", s)
    return s


def parse_arabic_ordinal_phrase(text: str) -> int | None:
    t = normalize_ar(text)
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
    candidates = [m.group(1) for m in matches]
    for cand in candidates:
        cand = re.split(r"[:\|\-–—\(\[\{«\"/]", cand)[0]
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
                u_val = units_map[m_teen.group(1)]
                return h_val + 10 + u_val
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


def extract_gregorian_date(title: str) -> tuple[int, int, int] | None:
    t = normalize_ar(title)
    # Match YYYY-MM-DD or YYYY / MM / DD or YYYY MM DD
    m = re.search(r"\b(20\d{2})\s*[\-/\s]\s*(\d{1,2})\s*[\-/\s]\s*(\d{1,2})\b", t)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return (y, mo, d)
    # Match DD-MM-YYYY or DD / MM / YYYY
    m = re.search(r"\b(\d{1,2})\s*[\-/]\s*(\d{1,2})\s*[\-/]\s*(20\d{2})\b", t)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return (y, mo, d)
    return None


HIJRI_MONTHS = {
    "محرم": 1,
    "صفر الخير": 2, "صفر": 2,
    "ربيع الأنوار": 3, "ربيع الانوار": 3, "ربيع الأول": 3, "ربيع الاول": 3, "ربيع أول": 3, "ربيع اول": 3,
    "ربيع الثاني": 4, "ربيع الآخر": 4, "ربيع الاخر": 4, "ربيع ثاني": 4,
    "جمادى الأولى": 5, "جمادى الاولى": 5, "جمادي الأولى": 5, "جمادي الاولى": 5, "جمادى اولى": 5,
    "جمادى الآخرة": 6, "جمادى الاخرة": 6, "جمادى الثانية": 6, "جمادي الآخرة": 6, "جمادي الثانية": 6,
    "رجب": 7,
    "شعبان": 8,
    "رمضان": 9,
    "شوال": 10,
    "ذو القعدة": 11, "ذي القعدة": 11,
    "ذو الحجة": 12, "ذي الحجة": 12,
}


def extract_hijri_date(title: str) -> tuple[int, int, int] | None:
    t = normalize_ar(title)
    # Check named months with year
    for m_name, m_num in sorted(HIJRI_MONTHS.items(), key=lambda x: -len(x[0])):
        pat = r"\b(\d{1,2})\s+#?" + re.escape(m_name) + r"\s+(144\d)\b"
        m = re.search(pat, t)
        if m:
            return (int(m.group(2)), m_num, int(m.group(1)))
    # Check numeric DD/MM/144X or DD-MM-144X
    m = re.search(r"\b(\d{1,2})\s*[\-/]\s*(\d{1,2})\s*[\-/]\s*(144\d)\b", t)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 30:
            return (y, mo, d)
    # Special case: "3 ربيع الثاني" without year in hafiz__muwatta (which is 1443)
    for m_name, m_num in sorted(HIJRI_MONTHS.items(), key=lambda x: -len(x[0])):
        pat = r"\b(\d{1,2})\s+#?" + re.escape(m_name) + r"(?:\b|$)"
        m = re.search(pat, t)
        if m:
            return (1443, m_num, int(m.group(1)))
    return None


def fix_asimi(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "asimi__s036":
            # Sort by leading (N)
            def key_s036(item):
                idx, l = item
                t = normalize_ar(l["title"])
                m = re.match(r"^\s*\((\d+)\)", t)
                return (int(m.group(1)) if m else 9999, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s036)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
        elif sid == "asimi__s040":
            # Move Imam Bukhari (2), (3), (4) to right before the 7 Bukhari clips
            bukhari_numbered = []
            bukhari_clips = []
            others = []
            for l in s["lessons"]:
                t = normalize_ar(l["title"])
                if "البخاري" in t:
                    if re.search(r"\(\d+\)", t):
                        bukhari_numbered.append(l)
                    else:
                        bukhari_clips.append(l)
                else:
                    others.append(l)
            bukhari_numbered.sort(key=lambda l: int(re.search(r"\((\d+)\)", normalize_ar(l["title"])).group(1)))
            s["lessons"] = others + bukhari_numbered + bukhari_clips
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
    return fixed


def fix_bouti(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "bouti__s065":
            # Swap last two lessons (7-How do you ask... and 6- Every inward...)
            lessons = s["lessons"]
            if len(lessons) >= 19 and lessons[-2]["title"].startswith("7-") and lessons[-1]["title"].startswith("6-"):
                lessons[-2], lessons[-1] = lessons[-1], lessons[-2]
                fixed.append(f"{sid} ({len(lessons)} lessons)")
        elif sid == "bouti__s067":
            lessons = s["lessons"]
            # 1) Sort "Sur la voie de la purification" lessons by leading number
            idxs_pur = [j for j, l in enumerate(lessons) if "Sur la voie de la purification" in l["title"]]
            if idxs_pur:
                block_pur = [lessons[j] for j in idxs_pur]
                block_pur.sort(key=lambda l: int(m.group(1)) if (m := re.search(r"(\d+)", l["title"])) else 99)
                for j, b in zip(idxs_pur, block_pur):
                    lessons[j] = b
            # 2) Sort "[Ep.1] INTERPRÉTATION SCIENTIFIQUE ... P.X/6" in ascending order of P.X/6
            idxs_sci = [j for j, l in enumerate(lessons) if "INTERPRÉTATION SCIENTIFIQUE" in l["title"]]
            if idxs_sci:
                block_sci = [lessons[j] for j in idxs_sci]
                block_sci.sort(key=lambda l: int(m.group(1)) if (m := re.search(r"P\.(\d+)/6", l["title"])) else 99)
                for j, b in zip(idxs_sci, block_sci):
                    lessons[j] = b
            fixed.append(f"{sid} ({len(lessons)} lessons)")
        elif sid == "bouti__s072":
            lessons = s["lessons"]
            # Sort the "وصايا الشهيد لأمة التوحيد" block (lessons 9..15) in ascending order
            idxs = [i for i, l in enumerate(lessons) if "وصايا الشهيد لأمة التوحيد" in l["title"]]
            if idxs:
                block = [lessons[i] for i in idxs]
                block.sort(key=lambda l: int(m.group(1)) if (m := re.match(r"^\s*(\d+)", normalize_ar(l["title"]))) else 99)
                for i, b in zip(idxs, block):
                    lessons[i] = b
                fixed.append(f"{sid} ({len(lessons)} lessons)")
    return fixed


def fix_dedew(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "dedew__barnamaj_maalim_s3":
            def key_maalim_s3(item):
                idx, l = item
                t = normalize_ar(l["title"])
                if "promo" in t.lower() or "برومو" in t:
                    return (999, idx)
                ep = parse_arabic_ordinal_phrase(t)
                if ep is None:
                    m = re.search(r"\((\d+)\)", t)
                    if m:
                        ep = int(m.group(1))
                return (ep if ep is not None else 998, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_maalim_s3)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
    return fixed


def fix_gomaa(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "gomaa__s001":
            def key_s001(item):
                idx, l = item
                ep = parse_arabic_ordinal_phrase(l["title"])
                return (ep if ep is not None else 999, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s001)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s004":
            # Group 1: المجلس الأول .. الخامس (1-5)
            # Group 2: الأشباه والنظائر | حـ 1 .. 9
            # Group 3: المجلس (10) .. (13)
            g1, g2, g3 = [], [], []
            for idx, l in enumerate(s["lessons"]):
                t = normalize_ar(l["title"])
                m_par = re.search(r"\((\d+)\)", t)
                m_ha = re.search(r"ح\s*(\d+)", t)
                if m_par:
                    g3.append((int(m_par.group(1)), idx, l))
                elif m_ha:
                    g2.append((int(m_ha.group(1)), idx, l))
                else:
                    ep = parse_arabic_ordinal_phrase(t) or idx
                    g1.append((ep, idx, l))
            g1.sort()
            g2.sort()
            g3.sort()
            s["lessons"] = [l for _, _, l in (g1 + g2 + g3)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s006":
            # Separate "الدرس الأول..السادس" from "المجلس الأول..الرابع"
            g_dars, g_majlis = [], []
            for idx, l in enumerate(s["lessons"]):
                t = normalize_ar(l["title"])
                ep = parse_arabic_ordinal_phrase(t) or 99
                if "الدرس" in t:
                    g_dars.append((ep, idx, l))
                else:
                    g_majlis.append((ep, idx, l))
            g_dars.sort()
            g_majlis.sort()
            s["lessons"] = [l for _, _, l in (g_dars + g_majlis)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s010":
            # Move "موعظة المؤمنين | كتاب أسرار الصلاة ومهماتها مقدمة" right after الدرس الخامس,
            # and ensure الدرس السادس (الجزء الأول) comes before الدرس السادس (الجزء الثاني).
            lessons = s["lessons"]
            seen_yids = set()
            deduped = []
            for l in lessons:
                yid = l.get("yt_id")
                if yid not in seen_yids:
                    seen_yids.add(yid)
                    deduped.append(l)
            intro_salaat = None
            rest = []
            for l in deduped:
                if "كتاب أسرار الصلاة ومهماتها مقدمة" in l["title"]:
                    intro_salaat = l
                else:
                    rest.append(l)
            # Swap الجزء الثاني and الجزء الأول of الدرس السادس if reversed
            for i in range(len(rest) - 1):
                if "الدرس السادس (الجزء الثاني)" in rest[i]["title"] and "الدرس السادس (الجزء الأول)" in rest[i + 1]["title"]:
                    rest[i], rest[i + 1] = rest[i + 1], rest[i]
            if intro_salaat:
                new_lessons = []
                for l in rest:
                    new_lessons.append(l)
                    if "الدرس الخامس |" in l["title"]:
                        new_lessons.append(intro_salaat)
                s["lessons"] = new_lessons
            else:
                s["lessons"] = rest
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s017":
            # Separate:
            # 1) المجلس الأول .. السابع
            # 2) الدرس 01 .. 07
            # 3) بيان اعتقاد (1) .. (2)
            # 4) Other clips
            g_majlis, g_dars, g_itiqad, g_other = [], [], [], []
            for idx, l in enumerate(s["lessons"]):
                t = normalize_ar(l["title"])
                if "المجلس" in t:
                    ep = parse_arabic_ordinal_phrase(t) or 99
                    g_majlis.append((ep, idx, l))
                elif "الدرس" in t:
                    m = re.search(r"الدرس\s*(\d+)", t)
                    ep = int(m.group(1)) if m else 99
                    g_dars.append((ep, idx, l))
                elif "بيان اعتقاد" in t:
                    m = re.search(r"\((\d+)\)", t)
                    ep = int(m.group(1)) if m else 99
                    g_itiqad.append((ep, idx, l))
                else:
                    g_other.append((idx, l))
            g_majlis.sort()
            g_dars.sort()
            g_itiqad.sort()
            s["lessons"] = (
                [l for _, _, l in g_majlis]
                + [l for _, _, l in g_dars]
                + [l for _, _, l in g_itiqad]
                + [l for _, l in g_other]
            )
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s019":
            # Sort by date (2009-10-04, 2009-10-31 ج1, 2009-10-31 ج2, 2009-11-07, 2009-11-20, 2009-12-12)
            def key_s019(item):
                idx, l = item
                dt = extract_gregorian_date(l["title"]) or (9999, 12, 31)
                return (dt, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s019)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s050":
            def key_s050(item):
                idx, l = item
                dt = extract_gregorian_date(l["title"])
                return (0, dt, idx) if dt else (1, (9999, 12, 31), idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s050)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s057":
            # Move الذكر 2 جـ1 and الذكر 2 جـ2 to Episode 17 (between Episode 16 الذكر جـ 1 and Episode 18 الذكر جـ 3)
            def key_s057(item):
                idx, l = item
                t = normalize_ar(l["title"])
                if "قريبا" in t or "برومو" in t:
                    return (999, 0, idx)
                if "الذكر 2 ج1" in t or "الذكر 2 جـ1" in l["title"]:
                    return (17, 1, idx)
                if "الذكر 2 ج2" in t or "الذكر 2 جـ2" in l["title"]:
                    return (17, 2, idx)
                m = re.search(r"(?:ح|الحلقة)\s*(\d+)", t)
                if m:
                    return (int(m.group(1)), 0, idx)
                ep = parse_arabic_ordinal_phrase(t)
                if ep is not None:
                    return (ep, 0, idx)
                return (998, 0, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s057)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s073":
            def key_s073(item):
                idx, l = item
                ep = parse_arabic_ordinal_phrase(l["title"])
                return (ep if ep is not None else 999, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s073)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s091":
            # First: لقاء الجمعة 1..10
            # Second: All dated episodes sorted chronologically by Gregorian date
            # Third: Undated episodes
            g_num, g_dated, g_undated = [], [], []
            for idx, l in enumerate(s["lessons"]):
                t = normalize_ar(l["title"])
                m_num = re.search(r"لقاء الجمعة\s*(\d+)", t)
                dt = extract_gregorian_date(t)
                if m_num and not dt:
                    g_num.append((int(m_num.group(1)), idx, l))
                elif dt:
                    g_dated.append((dt, idx, l))
                else:
                    g_undated.append((idx, l))
            g_num.sort()
            g_dated.sort()
            s["lessons"] = (
                [l for _, _, l in g_num]
                + [l for _, _, l in g_dated]
                + [l for _, l in g_undated]
            )
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "gomaa__s094":
            # Group numbered "اللقاء العام <ordinal>" together in ascending order
            # (keep positions 1..7 which are dated 2013/2014 lessons, then numbered اللقاء العام 4..13, then remaining)
            lessons = s["lessons"]
            numbered_liqaa = []
            others = []
            for idx, l in enumerate(lessons):
                t = normalize_ar(l["title"])
                if "اللقاء العام" in t:
                    ep = parse_arabic_ordinal_phrase(t)
                    sub = 0
                    m_sub = re.search(r"ج\s*(\d+)", t)
                    if m_sub:
                        sub = int(m_sub.group(1))
                    if ep is not None:
                        numbered_liqaa.append((ep, sub, idx, l))
                        continue
                others.append(l)
            numbered_liqaa.sort()
            # Insert numbered_liqaa at index 7 (where اللقاء العام العاشر originally stood)
            s["lessons"] = others[:7] + [l for _, _, _, l in numbered_liqaa] + others[7:]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
    return fixed


def fix_hafiz(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "hafiz__aqd_mithaq":
            def key_aqd(item):
                idx, l = item
                m = re.search(r"\((\d+)\)", normalize_ar(l["title"]))
                return (int(m.group(1)) if m else 999, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_aqd)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "hafiz__kibrit_ahmar_tazkiah":
            def key_kibrit(item):
                idx, l = item
                t = normalize_ar(l["title"])
                m = re.search(r"\b(\d{1,2})\b", t)
                if m:
                    return (0, int(m.group(1)), idx)
                ep = parse_arabic_ordinal_phrase(t)
                if ep is not None:
                    return (0, ep, idx)
                return (1, 999, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_kibrit)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "hafiz__muwatta":
            lessons = s["lessons"]
            by_id = {l["yt_id"]: l for l in lessons}
            used_ids = set()

            # 2) Assign synthetic Hijri dates to the 18 undated chapter lessons in Part 2 so they sort into exact chapter place
            part2_synthetic_dates = {
                "NwiHmsaT4HA": (1442, 8, 19, 1),  # باب غسل المحرم (after 18 شعبان 1442 كتاب الحج)
                "fsqLXjP4Z2U": (1442, 8, 19, 2),  # باب مواقيت الإهلال
                "5Pyznw9R884": (1443, 1, 9, 1),   # كتاب الجهاد - باب ما جاء في الخيل
                "ErwkrhX1wSg": (1443, 2, 2, 1),   # كتاب الضحايا باب الشركة في الضحايا
                "FmhEmXd-t9c": (1443, 2, 2, 2),   # كتاب الضحايا - باب الضحية عما في بطن المرأة
                "3c5C4gdpSkM": (1443, 4, 4, 1),   # باب نكاح المحلل
                "VfR4nLscUlc": (1443, 4, 4, 2),   # باب ما لا يجمع بينه من النساء
                "FtBT_waQN84": (1443, 4, 8, 1),   # باب نكاح الأمة على الحرة
                "BLBIAyDlwyo": (1443, 5, 26, 1),  # كتاب الطلاق - باب عدة أم الولد (typo 26-6 -> 26-5)
                "pTvgPvz_c3k": (1443, 5, 1, 1),   # باب طلاق المريض
                "07nucE_5BpQ": (1443, 5, 8, 1),   # كتاب الطلاق - باب ما جاء في الأقراء
                "BXWuW_vkyc8": (1443, 5, 8, 2),   # كتاب الطلاق - باب ما جاء في عدة المرأة في بيتها
                "5p2qAfmF5EM": (1443, 5, 21, 1),  # كتاب الرضاع
                "SIwJT7k90EE": (1443, 6, 25, 1),  # كتاب البيوع - باب العينة
                "Ju85SCOAuDY": (1443, 7, 10, 1),  # باب ما يكره من بيع الطعام إلى أجل
                "uGpI0sh4z4s": (1443, 7, 10, 2),  # كتاب البيوع - باب السلفة في الطعام
                "OVaITGJYD0Y": (1443, 6, 18, 1),  # باب بيع النحاس والحديد
                "sjQ5A9xJmKA": (1443, 11, 29, 1), # كتاب الأقضية: باب القضاء فيمن هلك وله دين
            }

            # 3) Assign synthetic episode numbers to the undated chapter lessons in Part 3 (-403- to -534-)
            part3_synthetic_eps = {
                "T_k67IO0b6I": (417, 1),  # الوصية والعتق
                "SJUz0Aa0TXM": (453, 1),  # كتاب العقول (الديات)
                "8qPqoM54I-o": (453, 2),  # كتاب العقول 2
                "eu-x3M73z1s": (473, 1),  # كتاب القسامة
                "hMXB0qWcPbE": (475, 1),  # كتاب الجامع
                "C2T2ngtVwfo": (501, 1),  # كتاب جامع ما جاء في الطعام والشراب
                "ONGKGe4FB5k": (517, 1),  # باب ما جاء في الرؤيا
                "7IJ5cHlXL4M": (520, 1),  # باب ما جاء في السلام
                "ovxP4Pm_z8E": (534, 1),
                "YJMeF04dMrM": (534, 2),
                "9u4a4iagqsg": (534, 3),
                "e2R4Wsam-nY": (534, 4),
                "C6qmxW5Ml9g": (534, 5),
                "Tl-3Hq0Griw": (534, 6),
                "3anebsP7F5Q": (535, 0),  # مجلس ختم دروس موطأ الإمام مالك (الإجازة)
            }

            part1_early_base = []
            for l in lessons:
                yid = l["yt_id"]
                if yid in ("kqIjAogupL0", "H8fvGuvY3hg", "e2EP0nlId60", "2ogwHhnnvw0", "AQ8DNvvEh10"):
                    continue
                if yid in part2_synthetic_dates or yid in part3_synthetic_eps:
                    continue
                t = normalize_ar(l["title"])
                if re.search(r"-\s*(\d{3})\s*-", t) or extract_hijri_date(t):
                    continue
                part1_early_base.append(l)

            part1 = []
            for wid in ("kqIjAogupL0", "H8fvGuvY3hg"):
                if wid in by_id:
                    part1.append(by_id[wid])
                    used_ids.add(wid)
            for l in part1_early_base:
                part1.append(l)
                used_ids.add(l["yt_id"])
                if l["yt_id"] == "Tl5tGr-G1f0":
                    for jid in ("e2EP0nlId60", "2ogwHhnnvw0"):
                        if jid in by_id and jid not in used_ids:
                            part1.append(by_id[jid])
                            used_ids.add(jid)
                elif l["yt_id"] == "6yXersK15cw":
                    if "AQ8DNvvEh10" in by_id and "AQ8DNvvEh10" not in used_ids:
                        part1.append(by_id["AQ8DNvvEh10"])
                        used_ids.add("AQ8DNvvEh10")

            part2_items = []
            part3_items = []

            for idx, l in enumerate(lessons):
                yid = l["yt_id"]
                if yid in used_ids:
                    continue
                t = normalize_ar(l["title"])
                m_ep = re.search(r"-\s*(\d{3})\s*-", t)
                if m_ep:
                    ep_num = int(m_ep.group(1))
                    part3_items.append((ep_num, 0, idx, l))
                    used_ids.add(yid)
                elif yid in part3_synthetic_eps:
                    ep_num, sub = part3_synthetic_eps[yid]
                    part3_items.append((ep_num, sub, idx, l))
                    used_ids.add(yid)
                elif yid in part2_synthetic_dates:
                    y, mo, d, sub = part2_synthetic_dates[yid]
                    part2_items.append(((y, mo, d), sub, idx, l))
                    used_ids.add(yid)
                else:
                    hdate = extract_hijri_date(t)
                    if hdate:
                        part2_items.append((hdate, 0, idx, l))
                        used_ids.add(yid)
                    else:
                        # Fallback to end of part 3 before khatm
                        part3_items.append((534, 9, idx, l))
                        used_ids.add(yid)

            part2_items.sort()
            part3_items.sort()

            new_lessons = (
                part1
                + [l for _, _, _, l in part2_items]
                + [l for _, _, _, l in part3_items]
            )
            assert len(new_lessons) == len(lessons), f"Mismatch in hafiz__muwatta count: {len(new_lessons)} vs {len(lessons)}"
            s["lessons"] = new_lessons
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
    return fixed


def fix_hashemi(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "hashemi__s055":
            def key_s055(item):
                idx, l = item
                t = normalize_ar(l["title"])
                m = re.search(r"ونفس\s*(\d+)", t)
                return (int(m.group(1)) if m else 999, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s055)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
    return fixed


def fix_jifri(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "jifri__s001":
            def key_jifri_s001(item):
                idx, l = item
                yid = l.get("yt_id")
                t = normalize_ar(l["title"])
                # 0Su3QqUQUVw is Episode 78 (published between 77 and 79)
                if yid == "0Su3QqUQUVw":
                    return (78, 0, idx)
                sub = 0
                m_sub = re.search(r"ج\s*(\d+)", t)
                if m_sub:
                    sub = int(m_sub.group(1))
                # Explicit رقم: N or الدرس N or (N)
                m = re.search(r"(?:الدرس|درس|رقم)\s*[:\-–—\(\[\{#]*\s*(\d{1,3})\b", t)
                if m:
                    return (int(m.group(1)), sub, idx)
                m = re.search(r"\((\d{1,3})\)", t)
                if m:
                    return (int(m.group(1)), sub, idx)
                ep = parse_arabic_ordinal_phrase(t)
                if ep is not None:
                    return (ep, sub, idx)
                return (999, sub, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_jifri_s001)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "jifri__s025":
            def key_jifri_s025(item):
                idx, l = item
                t = normalize_ar(l["title"])
                if "الأخيرة" in t or "الاخيرة" in t:
                    return (30, 0, idx)
                # Check sub-clip (X-Y)
                m_sub = re.search(r"\((\d+)\s*-\s*(\d+)\)", t)
                if m_sub:
                    return (int(m_sub.group(1)), int(m_sub.group(2)), idx)
                # Main episode: "حلقة X:" or "(X)" or "الشجرة الطيبة X -"
                m = re.search(r"(?:حلقة|الحلقة)\s*(\d+)", t)
                if m:
                    return (int(m.group(1)), 0, idx)
                m = re.search(r"\((\d+)\)", t)
                if m:
                    return (int(m.group(1)), 0, idx)
                m = re.search(r"الشجرة الطيبة\s*(\d+)", t)
                if m:
                    return (int(m.group(1)), 0, idx)
                return (999, 0, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_jifri_s025)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "jifri__s026":
            def key_jifri_s026(item):
                idx, l = item
                t = normalize_ar(l["title"])
                sub = 0
                m_sub = re.search(r"ج\s*(\d+)", t)
                if m_sub:
                    sub = int(m_sub.group(1))
                # Leading number "13:"
                m = re.match(r"^\s*(\d+)\s*:", t)
                if m:
                    return (int(m.group(1)), sub, idx)
                # "حلقة 2:" or "حياتنا (10)" or "حياتنا 19"
                m = re.search(r"(?:حلقة|الحلقة|حياتنا)\s*[\(\[]?\s*(\d+)", t)
                if m:
                    return (int(m.group(1)), sub, idx)
                return (999, sub, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_jifri_s026)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
    return fixed


def fix_kamali(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "kamali__s023":
            def key_kamali_s023(item):
                idx, l = item
                t = normalize_ar(l["title"])
                m = re.search(r"الحلقة\s*(\d+)", t)
                return (int(m.group(1)) if m else 999, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_kamali_s023)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
    return fixed


def fix_samarrai(data: dict) -> list[str]:
    fixed = []
    ar_map = json.loads(ARCHIVE_MAP_JSON.read_text(encoding="utf-8")) if ARCHIVE_MAP_JSON.exists() else {}
    lmsat_files = {}
    for f in ar_map.get("LmsatEpisodesHD", []):
        m = re.search(r"\(\s*0*(\d+)\s*\)", f.get("name", ""))
        if m:
            ep_n = int(m.group(1))
            # Prefer mp4 if both exist, otherwise mp3
            if ep_n not in lmsat_files or f["name"].lower().endswith(".mp4"):
                lmsat_files[ep_n] = f

    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "samarrai__s065":
            lessons = s["lessons"]
            existing_ids = {l.get("yt_id") for l in lessons}
            for ep_n in (235, 241):
                aid = f"archive__samarrai__s065__ep{ep_n:03d}"
                if aid not in existing_ids and ep_n in lmsat_files:
                    f = lmsat_files[ep_n]
                    lessons.append({
                        "yt_id": aid,
                        "title": f"{f['title']} [صوت مستدرك من أرشيف الإنترنت]",
                        "yt_url": f["url"],
                        "duration": f["duration"],
                    })
                    existing_ids.add(aid)

            def key_s065(item):
                idx, l = item
                t = normalize_ar(l["title"])
                m = re.search(r"\(\s*0*(\d+)\s*\)", t)
                if m:
                    return (0, int(m.group(1)), idx)
                return (1, 9999, idx)

            s["lessons"] = [l for _, l in sorted(enumerate(lessons), key=key_s065)]
            s["expected_count"] = len(s["lessons"])
            fixed.append(f"{sid} ({len(s['lessons'])} lessons, 1..254 contiguous)")
    return fixed


def fix_sayed(data: dict) -> list[str]:
    fixed = []
    for s in data.get("series", []):
        sid = s.get("id")
        if sid == "sayed__s092":
            # Two 5-part sub-series:
            # 1) "شخصيات 01..05" (without "وقدوات")
            # 2) "شخصيات وقدوات 1..5"
            def key_s092(item):
                idx, l = item
                t = normalize_ar(l["title"])
                sub_series = 2 if "شخصيات وقدوات" in t else 1
                m = re.search(r"شخصيات(?:\s+وقدوات)?\s*[\(\[]?\s*0*(\d+)", t)
                ep = int(m.group(1)) if m else 99
                return (sub_series, ep, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s092)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")

        elif sid == "sayed__s098":
            def key_s098(item):
                idx, l = item
                t = normalize_ar(l["title"])
                m = re.search(r"الجيل الصاعد\s*[\(\[]?\s*0*(\d+)", t)
                ep = int(m.group(1)) if m else 99
                return (ep, idx)
            s["lessons"] = [l for _, l in sorted(enumerate(s["lessons"]), key=key_s098)]
            fixed.append(f"{sid} ({len(s['lessons'])} lessons)")
    return fixed


FIXERS = {
    "asimi": fix_asimi,
    "bouti": fix_bouti,
    "dedew": fix_dedew,
    "gomaa": fix_gomaa,
    "hafiz": fix_hafiz,
    "hashemi": fix_hashemi,
    "jifri": fix_jifri,
    "kamali": fix_kamali,
    "samarrai": fix_samarrai,
    "sayed": fix_sayed,
}


def main():
    import subprocess
    modified_sheikhs = []
    for sh, fixer in sorted(FIXERS.items()):
        p = CURATED_DIR / f"{sh}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        fixed_list = fixer(data)
        if fixed_list:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            modified_sheikhs.append(sh)
            print(f"[FIXED] {sh}.json: {', '.join(fixed_list)}")
    print(f"\nTotal sheikhs updated: {len(modified_sheikhs)} -> {modified_sheikhs}")
    for sh in modified_sheikhs:
        subprocess.run(["python3", "scripts/curated_tools.py", "import-sheikh", sh], cwd=str(BASE_DIR), check=True)
    subprocess.run(["python3", "scripts/curated_tools.py", "export-web"], cwd=str(BASE_DIR), check=True)


if __name__ == "__main__":
    main()
