#!/usr/bin/env python3
"""refresh_transcripts.py — يجعل علم «مفرَّغ» (has_transcript) مطابقًا للملفات الحقيقية.

المصدر: data/transcripts_index.json (فهرس يُبنى من مستودعات التفريغ: ytb + hawshat).
المطابقة: بمعرّف يوتيوب (vid) أولاً، ثم بالعنوان المطبَّع (تامّاً أو بأول 30 حرفًا).
الاستعمال:
    python3 scripts/refresh_transcripts.py            # معاينة فقط
    python3 scripts/refresh_transcripts.py --apply    # كتابة التغييرات في القاعدة
    python3 scripts/refresh_transcripts.py --apply --export   # + إعادة تصدير ملفات الموقع
"""
import json, os, re, sqlite3, sys, unicodedata, collections
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "curated.db")
IDX = os.path.join(ROOT, "data", "transcripts_index.json")

TASH = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")

def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = TASH.sub("", s)
    for a, b in (("ـ", ""), ("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"), ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي")):
        s = s.replace(a, b)
    s = re.sub(r"[^\w\u0600-\u06ff]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^\d+[\s_\-–|]*", "", s)


def load_index():
    d = json.load(open(IDX, encoding="utf-8"))
    by_id = set(d.get("by_id") or [])
    titles = set(d.get("titles") or [])
    full, pref = set(), set()
    for t in titles:
        full.add(t)
        if len(t) >= 25:
            pref.add(t[:30])
    return by_id, full, pref


def main():
    apply = "--apply" in sys.argv
    export = "--export" in sys.argv
    by_id, full, pref = load_index()
    print(f"فهرس التفريغ: {len(by_id)} معرّف · {len(full)} عنوان")

    con = sqlite3.connect(DB)
    cur = con.cursor()
    rows = cur.execute(
        "SELECT id, sheikh_id, series_id, yt_id, COALESCE(yt_title, title), has_transcript FROM lessons"
    ).fetchall()

    def matched(vid, title):
        if vid and str(vid).strip() in by_id:
            return True
        t = norm(title)
        if len(t) >= 12 and t in full:
            return True
        return len(t) >= 25 and t[:30] in pref

    up, down = [], []
    per = collections.defaultdict(lambda: [0, 0, 0])
    for lid, sh, sid, vid, title, flag in rows:
        m = matched(vid, title)
        a = per[sh]
        a[0] += 1
        a[1] += 1 if flag else 0
        a[2] += 1 if m else 0
        if m and not flag:
            up.append(lid)
        elif flag and not m:
            down.append(lid)

    print(f"دروس القاعدة: {len(rows)} | العلم الحالي: {sum(1 for r in rows if r[5])} | الحقيقي: {sum(v[2] for v in per.values())}")
    print(f"يرتفع 0→1: {len(up)} | يهبط 1→0: {len(down)}")
    for sh, (t, c, n) in sorted(per.items(), key=lambda x: -x[1][2])[:20]:
        print(f"   {sh:<12} {t:>6} | حالي {c:>5} | حقيقي {n:>5}")

    if apply:
        cur.executemany("UPDATE lessons SET has_transcript = 1 WHERE id = ?", [(i,) for i in up])
        cur.executemany("UPDATE lessons SET has_transcript = 0 WHERE id = ?", [(i,) for i in down])
        con.commit()
        total = cur.execute("SELECT SUM(has_transcript) FROM lessons").fetchone()[0]
        print(f"طُبِّق: +{len(up)} / -{len(down)} | مجموع العلم الآن: {total}")
        log = os.path.join(ROOT, "data", f"refresh_transcripts_{datetime.now():%Y%m%d_%H%M}.json")
        json.dump({"up": up, "down": down, "total": total}, open(log, "w"), ensure_ascii=False)
        print("سجل:", log)
        if export:
            sys.path.insert(0, os.path.join(ROOT, "scripts"))
            import curated_tools as ct
            ct.export_web_catalog()
            print("أُعيد تصدير catalog_curated.json + series_curated/")
    con.close()


if __name__ == "__main__":
    main()
