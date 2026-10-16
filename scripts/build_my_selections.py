#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يبني data/my_selections.json (فهرس خفيف لاختياراتك) من cheikh-selected.json.
يُشغَّل: python3 scripts/build_my_selections.py
المخرَج يُستخدمه زر «⭐ رؤية اختياراتي» في الواجهة.
"""
import json, os, datetime, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "cheikh-selected.json")
CAT = os.path.join(ROOT, "data", "catalog_curated.json")
OUT = os.path.join(ROOT, "data", "my_selections.json")

sel = json.load(open(SRC, encoding="utf-8"))
sh_list = sel.get("sheikhs") or []

def pick(d, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return default

sheikhs = []
ids = []
for sh in sh_list:
    sid = pick(sh, "sheikh_id", "id")
    srs = sh.get("series") or []
    s_out = []
    for sr in srs:
        rid = pick(sr, "id", "series_id")
        ids.append(rid)
        s_out.append({
            "id": rid,
            "order_no": sr.get("order_no"),
            "title": pick(sr, "title", "name"),
            "state": sr.get("state"),
            "lessons": sr.get("actual_count") or sr.get("lessons_count"),
            "transcribed": sr.get("transcribed_count"),
            "summary": sr.get("summary_count"),
            "questions": sr.get("questions_count"),
            "missing": sr.get("missing_count"),
            "duration": sr.get("total_duration"),
            "yt_playlist_id": sr.get("yt_playlist_id"),
        })
    sheikhs.append({
        "id": sid,
        "name": pick(sh, "sheikh_name", "name"),
        "short_name": pick(sh, "sheikh_short", "short_name", default=pick(sh, "sheikh_name", "name")),
        "order_no": sh.get("order_no"),
        "series_count": len(s_out),
        "series": s_out,
    })

# تقاطع مع الفهرس (catalog_curated.json) — لنعرف ما سيظهر فعلاً في الواجهة
cat_ids = set()
if os.path.exists(CAT):
    cat = json.load(open(CAT, encoding="utf-8"))
    for sh in cat.get("sheikhs", []):
        for sr in (sh.get("series") or []):
            cat_ids.add(sr.get("id"))

in_cat = [i for i in ids if i in cat_ids]
not_in_cat = [i for i in ids if i not in cat_ids]

# الأرقام تُحسب من السلاسل نفسها (نفس ما تحسبه الواجهة) حتى لا تتناقض مع العرض
_sum_lessons = sum(int(sr.get("lessons") or 0) for sh in sheikhs for sr in sh["series"])
_sum_dur = sum(int(sr.get("duration") or 0) for sh in sheikhs for sr in sh["series"])
_src_t = sel.get("totals") or {}

out = {
    "v": 1,
    "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "source": "cheikh-selected.json",
    "source_exported_at": sel.get("exported_at"),
    "totals": {
        "sheikhs_count": len(sheikhs),
        "series_count": len(ids),
        "lessons_count": _sum_lessons,
        "total_hours": round(_sum_dur / 3600.0, 1),
    },
    "source_reported": {
        "lessons_count": sel.get("lessons_count") or _src_t.get("lessons_count"),
        "total_hours": sel.get("total_hours") or _src_t.get("total_hours"),
        "selected_series_ids": len(sel.get("selected_series_ids") or []),
    },
    "in_catalog": len(in_cat),
    "missing_from_catalog": sorted(not_in_cat),
    "sheikhs": sheikhs,
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

print("كُتب:", OUT, os.path.getsize(OUT), "بايت")
print("مشايخ:", len(sheikhs), "| سلاسل:", len(ids))
print("موجودة في الفهرس:", len(in_cat), "| غير موجودة:", len(not_in_cat), not_in_cat[:15])
if len(sel.get("selected_series_ids") or []) != len(ids):
    print("تنبيه: selected_series_ids =", len(sel.get("selected_series_ids") or []), "≠", len(ids))
