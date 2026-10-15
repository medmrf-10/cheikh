#!/usr/bin/env python3
"""Build Educational Ladders and Sermon Production Categories for all selected series."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELECTED_PATH = ROOT / "cheikh-selected.json"
LADDERS_JSON_PATH = ROOT / "cheikh-ladders.json"
LADDERS_MD_PATH = ROOT / "سلالم_التعليم_ومصفوفة_الخطب.md"


def classify_series(s: dict, sheikh_id: str, sheikh_name: str):
    sid = s["id"]
    title = s.get("title") or s.get("name") or ""

    # Returns (ladder_id, level_no, level_name, sermon_cat_id)
    # Ladders (1..10):
    # 1: المدخل المعرفي ومنهجية الطلب وتأسيس الوعي
    # 2: العقيدة الإسلامية وعلم الكلام ومناقشة الشبهات
    # 3: الفقه المالكي والقواعد الفقهية وفقه النوازل
    # 4: أصول الفقه ومقاصد الشريعة وصناعة التفقه
    # 5: علوم اللغة العربية — النحو والإعراب
    # 6: علوم اللغة العربية — الصرف والاشتقاق
    # 7: علوم اللغة العربية — البلاغة والبيان
    # 8: علوم الآلة العقلية — المنطق والوضع وآداب البحث
    # 9: التفسير وعلوم القرآن ومقاصد السور
    # 10: الحديث النبوي والسيرة والتاريخ والتزكية

    # Sermon Categories (1..12):
    # 1: التزكية وأعمال القلوب ومداواة النفوس
    # 2: أسماء الله الحسنى وتعظيم الخالق وحقائق الإيمان
    # 3: القصص القرآني وقصص الأنبياء والعبر
    # 4: السيرة النبوية والشمائل والصحابة والقدوات
    # 5: الأخلاق المحمدية والآداب الاجتماعية وإتقان العمل
    # 6: فقه الأسرة والتربية ومخاطبة الشباب والجيل الصاعد
    # 7: فقه النفس الإنسانية والعلاج المعرفي والروحي
    # 8: السنن الإلهية وفقه الإصلاح والفتن وقضايا الأمة
    # 9: دفع الشبهات المعاصرة والتحصين الفكري
    # 10: اللمسات البيانية واللطائف التدبرية لتحضير الخطب القرآنية
    # 11: المواسم الإيمانية والدار الآخرة والدعاء والمناجاة
    # 12: النماذج التطبيقية للخطب المنبرية والفتاوى ومجالس العلم

    # --- BARDONI ---
    if sheikh_id == "bardoni":
        if sid in ("bardoni__s001", "bardoni__s003"):
            return (2, 1, "المستوى الأول: التأسيسي", 2)
        if sid == "bardoni__s002":
            return (2, 2, "المستوى الثاني: المتوسط", 2)
        if sid == "bardoni__s006":
            return (3, 1, "المستوى الأول: التأسيسي", 12)
        if sid == "bardoni__s007":
            return (3, 2, "المستوى الثاني: المتوسط (القواعد الفقهية)", 12)
        if sid == "bardoni__s008":
            return (4, 2, "المستوى الثاني: المتوسط", 12)
        if sid == "bardoni__s009":
            return (5, 2, "المستوى الثاني: المتوسط", 10)
        if sid == "bardoni__s010":
            return (5, 3, "المستوى الثالث: المتقدم", 10)
        if sid in ("bardoni__s012", "bardoni__s013"):
            return (7, 2, "المستوى الثاني: المتوسط", 10)
        if sid in ("bardoni__s014", "bardoni__s015", "bardoni__s017"):
            return (8, 2, "المستوى الثاني: المتوسط والمتقدم", 9)

    # --- SARIRI ---
    if sheikh_id == "sariri":
        if sid == "sariri__s003":
            return (3, 1, "المستوى الأول: التأسيسي", 12)
        if sid == "sariri__s004":
            return (3, 2, "المستوى الثاني: المتوسط (الصناعة الفقهية)", 12)
        if sid == "sariri__s001":
            return (3, 3, "المستوى الثالث: المتقدم (مختصر خليل)", 12)
        if sid in ("sariri__s007", "sariri__s017", "sariri__s018", "sariri__s019"):
            return (4, 1, "المستوى الأول: التأسيسي", 12)
        if sid in ("sariri__s010", "sariri__s012", "sariri__s014", "sariri__s015", "sariri__s016"):
            return (4, 2, "المستوى الثاني: المتوسط", 12)
        if sid in ("sariri__s006", "sariri__s009", "sariri__s011", "sariri__s021"):
            return (4, 3, "المستوى الثالث: المتقدم", 12)
        if sid in ("sariri__s030", "sariri__s032", "sariri__s044"):
            return (1, 3, "المستوى الثالث: فلسفة التشريع وبناء الملكة", 8)
        if sid in ("sariri__s043", "sariri__s046"):
            return (3, 2, "المستوى التطبيقي: الخطب والفتاوى", 12)

    # --- ALIHANI ---
    if sheikh_id == "alihani":
        num = s.get("order_no") or 1
        if 1 <= num <= 6:
            return (5, 1, "المستوى الأول: التأسيسي (المبادئ والآجرومية ومتممتها)", 10)
        if 7 <= num <= 13:
            return (5, 2, "المستوى الثاني: المتوسط (ملحة الإعراب والقطر وموصل الطلاب)", 10)
        if 14 <= num <= 19:
            return (5, 3, "المستوى الثالث: المتقدم (شروح الألفية والتسهيل والدر المصون)", 10)
        if 20 <= num <= 23:
            return (6, 1, "المستوى الأول: التأسيسي (الأمثلة والبناء والمقصود)", 10)
        if 24 <= num <= 26:
            return (6, 2, "المستوى الثاني: المتوسط (تصريف العزي والإعلال والإبدال)", 10)
        if num in (27, 28):
            return (6, 3, "المستوى الثالث: المتقدم (شذا العرف والمراجعات)", 10)
        if 29 <= num <= 34:
            return (7, 1, "المستوى الأول: التأسيسي (تحفة الإخوان والبلاغة الواضحة ودروس البلاغة والسمرقندية)", 10)
        if 35 <= num <= 38:
            return (7, 3, "المستوى الثالث: المتقدم (المنهاج الواضح ودورة البلاغة القرآنية)", 10)
        if num in (39, 40, 42, 44, 48, 51, 52):
            return (9, 1, "المستوى الأول: علوم القرآن ومقاصد السور وأصول التفسير", 10)
        if num in (43, 45, 46, 47):
            return (9, 3, "المستوى الثالث: التفسير التحليلي والبياني (تفسير النسفي ولطائف البقرة)", 10)
        if num in (49, 50):
            return (3, 1, "المستوى الأول: فقه العبادات والمواريث", 12)

    # --- SHAARAWY ---
    if sheikh_id == "shaarawy":
        if sid in ("shaarawy__s061", "shaarawy__s062"):
            return (9, 1, "المستوى الأول: مقدمات التفسير وسورة الفاتحة", 10)
        if sid == "shaarawy__s060":
            return (9, 1, "المستوى الأول: تفسير جزء عم وقصار المفصل", 10)
        return (9, 2, "المستوى الثاني: التفسير الإيماني والبياني للقرآن الكريم (البقرة إلى الممتحنة)", 10)

    # --- SAMARRAI ---
    if sheikh_id == "samarrai":
        return (7, 3, "المستوى الثالث: الإعجاز البياني في القرآن الكريم", 10)

    # --- OMARI ---
    if sheikh_id == "omari":
        if sid in ("omari__s009", "omari__s010", "omari__s011"):
            return (8, 1, "المستوى الأول: التأسيسي (السلم المنورق وإيساغوجي)", 9)
        if sid in ("omari__s002", "omari__s003", "omari__s004", "omari__s005"):
            return (2, 2, "المستوى الثاني: المتوسط (أم البراهين والعقائد النسفية)", 2)
        if sid == "omari__s001":
            return (2, 3, "المستوى الثالث: المتقدم (الاقتصاد في الاعتقاد للغزالي)", 2)
        if sid == "omari__s007":
            return (10, 1, "المستوى الأول: التزكية وآداب السلوك", 1)
        return (2, 3, "المستوى الثالث: نقد الفلسفة الحديثة وفلسفة الدين", 9)

    # --- BOUTI ---
    if sheikh_id == "bouti":
        if sid == "bouti__s002":
            return (9, 1, "المستوى الأول: علوم القرآن ودراساته التطبيقية", 10)
        if sid in ("bouti__s003", "bouti__s016", "bouti__s018"):
            return (9, 2, "المستوى الثاني: إعجاز القرآن الكريم ودفع الشبهات عنه", 9)
        if sid in ("bouti__s004", "bouti__s005", "bouti__s006", "bouti__s007", "bouti__s008", "bouti__s009", "bouti__s010", "bouti__s011", "bouti__s012", "bouti__s013", "bouti__s014", "bouti__s015"):
            if sid == "bouti__s007":
                return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 3)
            if sid in ("bouti__s006", "bouti__s010", "bouti__s011"):
                return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 4)
            if sid == "bouti__s008":
                return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 8)
            return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 1)
        if sid == "bouti__s020":
            return (10, 2, "المستوى الثاني: شروح السنة الجامعة (رياض الصالحين)", 5)
        if sid == "bouti__s022":
            return (2, 1, "المستوى الأول: التأسيسي", 2)
        if sid == "bouti__s021":
            return (2, 2, "المستوى الثاني: المتوسط (كبرى اليقينيات الكونية)", 2)
        if sid in ("bouti__s023", "bouti__s026", "bouti__s027"):
            return (2, 3, "المستوى الثالث: تفنيد الشبهات المعاصرة وقضايا الساعة", 9)
        if sid == "bouti__s024":
            return (1, 2, "المستوى الثاني: فقه السنن الإلهية", 8)
        if sid == "bouti__s025":
            return (2, 2, "المستوى الثاني: الإيمان باليوم الآخر", 11)
        if sid == "bouti__s030":
            return (10, 2, "المستوى الثاني: فقه السيرة النبوية والخلافة الراشدة", 4)
        if sid in ("bouti__s031", "bouti__s042"):
            return (4, 2, "المستوى الثاني: تاريخ التشريع وفقه الجهاد", 8)
        if sid == "bouti__s033":
            return (10, 3, "المستوى الثالث: شروح الحكم العطائية والتزكية", 1)
        if sid == "bouti__s036":
            return (10, 2, "المستوى الثاني: الطب الروحي والنفسي", 7)
        if sid in ("bouti__s053", "bouti__s054", "bouti__s055", "bouti__s056", "bouti__s057", "bouti__s058", "bouti__s059", "bouti__s060", "bouti__s061"):
            return (10, 3, "المستوى التطبيقي: الخطب المنبرية", 12)

    # --- ASIMI ---
    if sheikh_id == "asimi":
        if sid == "asimi__s005":
            return (9, 2, "المستوى الثاني: التدبر القرآني", 10)
        if sid in ("asimi__s007", "asimi__s008", "asimi__s009", "asimi__s010"):
            return (2, 1, "المستوى الأول: التأسيسي (مقدمات السنوسي وصغرى الصغرى)", 2)
        if sid == "asimi__s014":
            return (10, 2, "المستوى الثاني: تراجم الأئمة ومكانتهم الحديثية", 4)
        if sid in ("asimi__s033", "asimi__s034", "asimi__s035"):
            return (8, 1, "المستوى الأول: التأسيسي (السلم والمفتاح وإيساغوجي)", 9)
        if sid in ("asimi__s036", "asimi__s037", "asimi__s038", "asimi__s039"):
            return (10, 2, "المستوى الثاني: السيرة النبوية التفصيلية وسير الخلفاء", 4)
        if sid in ("asimi__s041", "asimi__s042", "asimi__s043", "asimi__s044"):
            return (10, 2, "المستوى الثاني: التزكية وأعمال القلوب", 1)
        if sid == "asimi__s045":
            return (2, 1, "المستوى الأول: الإيمان بالدار الآخرة", 11)
        if sid == "asimi__s048":
            return (2, 1, "المستوى الأول: فقه أسماء الله الحسنى", 2)
        if sid in ("asimi__s051", "asimi__s052"):
            return (10, 3, "المستوى التطبيقي: الخطب المنبرية", 12)

    # --- HAWWA ---
    if sheikh_id == "hawwa":
        if sid == "hawwa__asma_allah_husna":
            return (2, 2, "المستوى الثاني: فقه أسماء الله الحسنى", 2)
        if sid in ("hawwa__khuluq_azim", "hawwa__shamail_nabi", "hawwa__muhammad_rasulullah"):
            return (10, 1, "المستوى الأول: الشمائل والأخلاق النبوية", 4)
        if sid in ("hawwa__hayat_zawjiyah", "hawwa__ya_ibni", "hawwa__ya_binti"):
            return (10, 1, "المستوى الأول: فقه الأسرة وتربية الأبناء", 6)
        if sid == "hawwa__tahayya_ramadan":
            return (10, 1, "المستوى الأول: المواسم الإيمانية", 11)
        if sid == "hawwa__adab_talib_ilm":
            return (1, 1, "المستوى الأول: آداب طالب العلم", 6)
        if sid == "hawwa__islah_iqtisadi":
            return (3, 2, "المستوى الثاني: الفقه الاقتصادي والإصلاح المالي", 5)
        if sid in ("hawwa__tazkiyat_lisan", "hawwa__adab_ammah"):
            return (10, 1, "المستوى الأول: الآداب الشرعية وتزكية اللسان", 5)
        return (10, 2, "المستوى الثاني: السلم المتكامل في التزكية والسلوك", 1)

    # --- HAFIZ ---
    if sheikh_id == "hafiz":
        if sid == "hafiz__muwatta":
            return (10, 3, "المستوى الثالث: شروح الحديث المسندة (موطأ الإمام مالك)", 12)
        if sid == "hafiz__tafsir_fatiha_qisar":
            return (9, 1, "المستوى الأول: تفسير الفاتحة وقصار السور", 10)
        if sid == "hafiz__qasas_haqq":
            return (9, 2, "المستوى الثاني: قصص الأنبياء في القرآن الكريم", 3)
        if sid in ("hafiz__sullam_tawfiq", "hafiz__sifat_salat_muqarrabin"):
            return (3, 1, "المستوى الأول: فقه العبادات وأسرار الصلاة", 11)
        if sid in ("hafiz__adab_fid_din", "hafiz__khuluquna"):
            return (10, 1, "المستوى الأول: الآداب النبوية وبناء الخلق", 5)
        return (10, 3, "المستوى الثالث: أمهات كتب التزكية والسلوك (الأربعين للغزالي والمكاتبات)", 1)

    # --- JIFRI ---
    if sheikh_id == "jifri":
        if sid in ("jifri__s018", "jifri__s019", "jifri__s020", "jifri__s023", "jifri__s028"):
            return (2, 2, "المستوى الثاني: تثبيت اليقين ومعالجة الشك والإلحاد", 9)
        if sid in ("jifri__s022", "jifri__s024", "jifri__s025"):
            return (10, 1, "المستوى الأول: الأخلاق المحمدية وإتقان العمل", 5)
        if sid == "jifri__s026":
            return (10, 1, "المستوى الأول: هدي السيرة في الأسرة والتربية", 6)
        if sid in ("jifri__s029", "jifri__s044", "jifri__s045"):
            return (1, 2, "المستوى الثاني: فقه الدعوة والحوار الفكري", 8)
        return (10, 2, "المستوى الثاني: أصول السلوك والتزكية (أيها المريد وسبيل الادكار)", 1)

    # --- GOMAA ---
    if sheikh_id == "gomaa":
        if sid == "gomaa__s008":
            return (4, 1, "المستوى الأول: مدخل أصول الفقه ونظرياته", 12)
        if sid in ("gomaa__s043", "gomaa__s044", "gomaa__s083", "gomaa__s084"):
            return (1, 2, "المستوى الثاني: النموذج المعرفي الإسلامي والمدخل إلى التراث", 9)
        if sid in ("gomaa__s039", "gomaa__s040", "gomaa__s041", "gomaa__s042", "gomaa__s047", "gomaa__s049", "gomaa__s050"):
            return (2, 2, "المستوى الثاني: الحوار الشبابي وتفنيد التشدد والشبهات", 9)
        if sid == "gomaa__s066":
            return (2, 1, "المستوى الأول: شرح أسماء الله الحسنى والتخلق بها", 2)
        if sid in ("gomaa__s012", "gomaa__s057", "gomaa__s059", "gomaa__s060"):
            return (10, 2, "المستوى الثاني: التزكية والسلوك وتراجم الأولياء", 1)
        if sid in ("gomaa__s048", "gomaa__s063", "gomaa__s078"):
            return (10, 1, "المستوى الأول: فقه الدعاء والمبشرات والرحمات", 11)
        if sid in ("gomaa__s045", "gomaa__s067", "gomaa__s068", "gomaa__s073"):
            return (10, 2, "المستوى الثاني: السيرة النبوية ومناقب الصحابة والأئمة", 4)
        return (3, 2, "المستوى التطبيقي: الفتاوى المعاصرة والمجالس العامة", 12)

    # --- SAYED ---
    if sheikh_id == "sayed":
        if sid in ("sayed__s005", "sayed__s006", "sayed__s083"):
            return (10, 1, "المستوى الأول: حفظ وفهم السنة النبوية الجامعة", 5)
        if sid in ("sayed__s015", "sayed__s065", "sayed__s066", "sayed__s067", "sayed__s082", "sayed__s087", "sayed__s112"):
            return (10, 2, "المستوى الثاني: التزكية وأعمال القلوب ومقاصد مدارج السالكين", 1)
        if sid == "sayed__s021":
            return (9, 2, "المستوى الثاني: قصص الأنبياء في القرآن", 3)
        if sid in ("sayed__s022", "sayed__s023", "sayed__s024", "sayed__s025", "sayed__s026", "sayed__s027", "sayed__s028", "sayed__s032", "sayed__s033"):
            return (9, 1, "المستوى الأول: مقاصد السور والتدبر المنهجي للقرآن", 10)
        if sid in ("sayed__s036", "sayed__s037", "sayed__s038", "sayed__s040", "sayed__s041", "sayed__s042", "sayed__s043", "sayed__s088", "sayed__s089", "sayed__s090", "sayed__s091", "sayed__s092"):
            return (10, 1, "المستوى الأول: السيرة النبوية والخلافة الراشدة والتاريخ الإسلامي", 4)
        if sid in ("sayed__s054", "sayed__s074", "sayed__s075", "sayed__s081", "sayed__s103"):
            return (2, 1, "المستوى الأول: البناء العقدي ونقد الفكر الغربي والحديث", 9)
        if sid in ("sayed__s055", "sayed__s056", "sayed__s084", "sayed__s085", "sayed__s093", "sayed__s109"):
            return (1, 1, "المستوى الأول: منهجية الطلب والتفكير الناقد وأبجديات العلوم", 6)
        if sid in ("sayed__s017", "sayed__s059", "sayed__s060", "sayed__s061", "sayed__s062", "sayed__s063", "sayed__s064", "sayed__s072", "sayed__s113"):
            return (1, 2, "المستوى الثاني: فقه الإصلاح والسنن الإلهية وقضايا الأمة", 8)
        return (1, 1, "المستوى الأول: بناء الجيل الصاعد والشباب", 6)

    # --- DEDEW ---
    if sheikh_id == "dedew":
        if sid == "dedew__sharh_manzouma_adoudiya":
            return (2, 1, "المستوى الأول: المنظومة العدودية في العقيدة", 2)
        if sid in ("dedew__sharh_waraqat", "dedew__sharh_miftah_wusool", "dedew__dawrat_maratib_dalala_kuwait"):
            return (4, 1, "المستوى الأول والثاني: الورقات ومفتاح الوصول ومراتب الدلالة", 12)
        if sid in ("dedew__dawrat_tahara_salah", "dedew__fiqh_muamalat", "dedew__dawrat_faraid", "dedew__ahkam_siyam_series"):
            return (3, 1, "المستوى الأول: دورات فقه العبادات والمعاملات والفرائض", 12)
        if sid == "dedew__sharh_akhlaq_wa_siyar":
            return (10, 2, "المستوى الثاني: مداواة النفوس والأخلاق والسير لابن حزم", 5)
        if sid in ("dedew__barnamaj_qissat_nuh", "dedew__barnamaj_abu_bashariya_adam"):
            return (9, 2, "المستوى الثاني: قصص الأنبياء في القرآن الكريم", 3)
        return (3, 2, "المستوى الثاني: برامج معالم ومفاهيم الفقهية والفكرية", 8)

    # --- KAMALI ---
    if sheikh_id == "kamali":
        return (9, 2, "المستوى الثاني: التفسير التحليلي والوعظي للسور", 10)

    # --- HASHEMI ---
    if sheikh_id == "hashemi":
        return (1, 2, "المستوى الثاني: فقه النفس والتربية المعرفية", 7)

    # --- AYMAN ---
    if sheikh_id == "ayman":
        if sid in ("ayman__s003", "ayman__s006", "ayman__s009", "ayman__s010", "ayman__s011", "ayman__s028", "ayman__s029"):
            return (1, 1, "المستوى الأول: تأسيس وعي المسلم المعاصر وخارطة العلوم", 8)
        if sid in ("ayman__s013", "ayman__s014"):
            return (5, 1, "المستوى الأول: الوعي اللغوي ومدخل علوم العربية", 10)
        if sid == "ayman__s017":
            return (1, 1, "المستوى الأول: مدخل إلى علم النفس", 7)
        if sid == "ayman__s018":
            return (1, 1, "المستوى الأول: دورة البيت المسلم", 6)
        return (10, 1, "المستوى الأول: مدخل دراسة التاريخ والسيرة والخلفاء والدول", 4)

    return (1, 1, "المستوى العام", 12)


LADDER_NAMES = {
    1: "السلم الأول: المدخل المعرفي ومنهجية الطلب وفقه السنن والإصلاح",
    2: "السلم الثاني: العقيدة الإسلامية وعلم الكلام ومناقشة الشبهات",
    3: "السلم الثالث: الفقه المالكي والقواعد الفقهية وفقه النوازل",
    4: "السلم الرابع: أصول الفقه ومقاصد الشريعة وتاريخ التشريع",
    5: "السلم الخامس: علوم اللغة العربية — النحو والإعراب",
    6: "السلم السادس: علوم اللغة العربية — الصرف والاشتقاق",
    7: "السلم السابع: علوم اللغة العربية — البلاغة والبيان القرآني",
    8: "السلم الثامن: علوم الآلة العقلية — المنطق والوضع وآداب البحث والمناظرة",
    9: "السلم التاسع: التفسير وعلوم القرآن ومقاصد السور",
    10: "السلم العاشر: الحديث النبوي والسيرة والتاريخ والتزكية والسلوك",
}

SERMON_CAT_NAMES = {
    1: "الفئة الأولى: التزكية وأعمال القلوب ومداواة أمراض النفوس (مادة دروس الرقائق والسلوك)",
    2: "الفئة الثانية: أسماء الله الحسنى وتعظيم الخالق وحقائق الإيمان (مادة الخطب العقدية والإيمانية)",
    3: "الفئة الثالثة: القصص القرآني وقصص الأنبياء والعبر (مادة السرد القصصي المنبري)",
    4: "الفئة الرابعة: السيرة النبوية والشمائل والصحابة والتاريخ (مادة خطب القدوات والمناسبات)",
    5: "الفئة الخامسة: الأخلاق المحمدية والآداب الاجتماعية وإتقان العمل (مادة خطب الأخلاق والمعاملات)",
    6: "الفئة السادسة: فقه الأسرة والتربية ومخاطبة الشباب والجيل الصاعد (مادة دروس الأسرة والشباب)",
    7: "الفئة السابعة: فقه النفس الإنسانية والعلاج المعرفي للكآبة والغفلة (مادة الإرشاد النفسي والروحي)",
    8: "الفئة الثامنة: السنن الإلهية وفقه الإصلاح والفتن وقضايا الأمة (مادة خطب الوعي والبصيرة)",
    9: "الفئة التاسعة: دفع الشبهات المعاصرة والتحصين الفكري (مادة الرد على الإلحاد والتشدد)",
    10: "الفئة العاشرة: التفسير واللمسات البيانية ومقاصد السور (المنجم القرآني لتحضير الخطب والدروس)",
    11: "الفئة الحادية عشرة: المواسم الإيمانية والدار الآخرة وفقه الدعاء (مادة رمضان والحج ومواعظ الآخرة)",
    12: "الفئة الثانية عشرة: النماذج التطبيقية للخطب المنبرية والفتاوى والتأصيل الفقهي (مدرسة الأداء الخطابي والإفتائي)",
}


def main():
    data = json.load(open(SELECTED_PATH, encoding="utf-8"))

    ladders = {k: {"id": k, "name": v, "series": [], "lessons_count": 0, "total_hours": 0.0} for k, v in LADDER_NAMES.items()}
    sermon_cats = {k: {"id": k, "name": v, "series": [], "lessons_count": 0, "total_hours": 0.0} for k, v in SERMON_CAT_NAMES.items()}

    for sh in data["sheikhs"]:
        sh_id = sh["sheikh_id"]
        sh_name = sh["sheikh_name"]
        for s in sh["series"]:
            lid, lvl_no, lvl_name, scat_id = classify_series(s, sh_id, sh_name)
            ac = s.get("actual_count") or len(s.get("lessons", []))
            hrs = round((s.get("total_duration") or 0) / 3600.0, 1)
            entry = {
                "series_id": s["id"],
                "sheikh_id": sh_id,
                "sheikh_name": sh_name,
                "order_in_sheikh": s.get("order_no"),
                "title": s.get("title") or s.get("name"),
                "state": s.get("state") or "completed",
                "lessons_count": ac,
                "hours": hrs,
                "level_no": lvl_no,
                "level_name": lvl_name,
                "ladder_id": lid,
                "ladder_name": LADDER_NAMES[lid],
                "sermon_category_id": scat_id,
                "sermon_category_name": SERMON_CAT_NAMES[scat_id],
            }
            ladders[lid]["series"].append(entry)
            ladders[lid]["lessons_count"] += ac
            ladders[lid]["total_hours"] = round(ladders[lid]["total_hours"] + hrs, 1)

            sermon_cats[scat_id]["series"].append(entry)
            sermon_cats[scat_id]["lessons_count"] += ac
            sermon_cats[scat_id]["total_hours"] = round(sermon_cats[scat_id]["total_hours"] + hrs, 1)

    for lid in ladders:
        ladders[lid]["series"].sort(key=lambda x: (x["level_no"], x["sheikh_name"], x["order_in_sheikh"] or 0))
        ladders[lid]["series_count"] = len(ladders[lid]["series"])

    for cid in sermon_cats:
        sermon_cats[cid]["series"].sort(key=lambda x: (x["sheikh_name"], x["order_in_sheikh"] or 0))
        sermon_cats[cid]["series_count"] = len(sermon_cats[cid]["series"])

    out_json = {
        "totals": data["totals"],
        "educational_ladders": list(ladders.values()),
        "sermon_categories": list(sermon_cats.values()),
    }
    with open(LADDERS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(out_json, f, ensure_ascii=False, indent=2)

    # Build Markdown Guide (Pure Arabic, Zero English)
    lines = []
    lines.append("# دليل السلالم التعليمية ومصفوفة إنتاج الدروس الوعظية والخطب المسجدية")
    lines.append("")
    lines.append("يضم هذا الدليل تصنيفاً منهجياً شاملاً لجميع السلاسل المختارة (410 سلاسل، 18994 درساً، 12582.4 ساعة لسبعة عشر شيخاً)، موزعة على مسارين متكاملين:")
    lines.append("- المسار الأول: السلالم التعليمية التأصيلية العشرة (مرتبة حسب مستويات التدرج العلمي: التأسيسي، فالمتوسط، فالمتقدم).")
    lines.append("- المسار الثاني: مصفوفة إنتاج الدروس الوعظية والخطب المسجدية (اثنتا عشرة فئة موضوعية تطبيقية للخطيب والواعظ والمربي).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## أولاً: جدول خلاصة السلالم التعليمية العشرة")
    lines.append("")
    lines.append("| رقم السلم | اسم السلم التعليمي | عدد السلاسل | عدد الدروس | مجموع الساعات |")
    lines.append("| :---: | :--- | :---: | :---: | :---: |")
    for lid, lobj in ladders.items():
        lines.append(f"| {lid} | {lobj['name']} | {lobj['series_count']} | {lobj['lessons_count']} | {lobj['total_hours']:.1f} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ثانياً: جدول خلاصة فئات إنتاج الدروس الوعظية والخطب المسجدية (12 فئة)")
    lines.append("")
    lines.append("| رقم الفئة | فئة الإنتاج الوعظي والخطابي | عدد السلاسل | عدد الدروس | مجموع الساعات |")
    lines.append("| :---: | :--- | :---: | :---: | :---: |")
    for cid, cobj in sermon_cats.items():
        lines.append(f"| {cid} | {cobj['name']} | {cobj['series_count']} | {cobj['lessons_count']} | {cobj['total_hours']:.1f} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ثالثاً: التفصيل الكامل للسلالم التعليمية العشرة (410 سلاسل)")
    lines.append("")
    for lid, lobj in ladders.items():
        lines.append(f"### {lobj['name']} ({lobj['series_count']} سلسلة — {lobj['lessons_count']} درساً — {lobj['total_hours']:.1f} ساعة)")
        lines.append("")
        lines.append("| الترتيب | المستوى | الشيخ | رقم السلسلة عند الشيخ | عنوان السلسلة | الدروس | الساعات |")
        lines.append("| :---: | :--- | :--- | :---: | :--- | :---: | :---: |")
        for idx, item in enumerate(lobj["series"], 1):
            clean_title = item["title"].replace("(Our Traits)", "").replace(" - مترجم للإنجليزية", "").replace(" (البرنامج الرمضاني - مترجم للإنجليزية)", "").replace("قناة CBC - ", "")
            lines.append(f"| {idx} | {item['level_name']} | {item['sheikh_name']} | {item['order_in_sheikh']} | {clean_title} | {item['lessons_count']} | {item['hours']:.1f} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## رابعاً: التفصيل الكامل لمصفوفة إنتاج الدروس الوعظية والخطب المسجدية (12 فئة)")
    lines.append("")
    for cid, cobj in sermon_cats.items():
        lines.append(f"### {cobj['name']} ({cobj['series_count']} سلسلة — {cobj['lessons_count']} درساً — {cobj['total_hours']:.1f} ساعة)")
        lines.append("")
        lines.append("| الترتيب | الشيخ | رقم السلسلة عند الشيخ | عنوان السلسلة | الدروس | الساعات |")
        lines.append("| :---: | :--- | :---: | :--- | :---: | :---: |")
        for idx, item in enumerate(cobj["series"], 1):
            clean_title = item["title"].replace("(Our Traits)", "").replace(" - مترجم للإنجليزية", "").replace(" (البرنامج الرمضاني - مترجم للإنجليزية)", "").replace("قناة CBC - ", "")
            lines.append(f"| {idx} | {item['sheikh_name']} | {item['order_in_sheikh']} | {clean_title} | {item['lessons_count']} | {item['hours']:.1f} |")
        lines.append("")

    with open(LADDERS_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("Successfully built cheikh-ladders.json and سلالم_التعليم_ومصفوفة_الخطب.md")
    for lid, lobj in ladders.items():
        print(f"Ladder {lid:2d}: {lobj['series_count']:3d} series | {lobj['lessons_count']:5d} lessons | {lobj['total_hours']:7.1f}h | {lobj['name']}")
    print("---")
    for cid, cobj in sermon_cats.items():
        print(f"Sermon {cid:2d}: {cobj['series_count']:3d} series | {cobj['lessons_count']:5d} lessons | {cobj['total_hours']:7.1f}h | {cobj['name']}")


if __name__ == "__main__":
    main()
