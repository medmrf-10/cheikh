#!/usr/bin/env python3
"""Rebuild cheikh-selected.json from a list of selected series IDs."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "data" / "catalog_curated.json"
SERIES_DIR = ROOT / "data" / "series_curated"
OUT_PATH = ROOT / "cheikh-selected.json"


def build_selected(selected_ids: list[str]):
    cat = json.load(open(CATALOG_PATH, encoding="utf-8"))
    sel_set = set(selected_ids)

    ordered_ids = []
    sheikhs_out = []
    series_out = []

    tot_lessons = 0
    tot_transcribed = 0
    tot_dur = 0

    for sh in cat.get("sheikhs", []):
        sh_id = sh["id"]
        sh_name = sh["name"]
        sh_series = []
        sh_lessons = 0
        sh_trans = 0

        for s in sh.get("series", []):
            sid = s["id"]
            if sid not in sel_set:
                continue
            ordered_ids.append(sid)
            s_copy = dict(s)
            s_file = SERIES_DIR / f"{sid}.json"
            if s_file.exists():
                s_detail = json.load(open(s_file, encoding="utf-8"))
                s_copy["lessons"] = s_detail.get("lessons", [])
            else:
                s_copy["lessons"] = []

            sh_series.append(s_copy)
            series_out.append(s_copy)

            ac = s_copy.get("actual_count") or len(s_copy["lessons"])
            tc = s_copy.get("transcribed_count") or 0
            dur = s_copy.get("total_duration") or 0

            sh_lessons += ac
            sh_trans += tc
            tot_lessons += ac
            tot_transcribed += tc
            tot_dur += dur

        if sh_series:
            sheikhs_out.append(
                {
                    "sheikh_id": sh_id,
                    "sheikh_name": sh_name,
                    "series_count": len(sh_series),
                    "lessons_count": sh_lessons,
                    "transcribed_count": sh_trans,
                    "series": sh_series,
                }
            )

    payload = {
        "exported_at": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "db_mode": "curated",
        "include_lessons": True,
        "totals": {
            "sheikhs_count": len(sheikhs_out),
            "series_count": len(series_out),
            "lessons_count": tot_lessons,
            "transcribed_count": tot_transcribed,
            "pending_transcript_count": tot_lessons - tot_transcribed,
            "total_duration_seconds": tot_dur,
            "total_hours": round(tot_dur / 3600.0, 1),
        },
        "selected_series_ids": ordered_ids,
        "sheikhs": sheikhs_out,
        "series": series_out,
    }

    json.dump(
        payload,
        open(OUT_PATH, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )
    print(json.dumps(payload["totals"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    ids = sys.argv[1:]
    build_selected(ids)
