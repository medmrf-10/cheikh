#!/usr/bin/env python3
"""Build Three-Tier Architecture, 10 Educational Ladders, and 12 Sermon Production Categories for all 681 selected series."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELECTED_PATH = ROOT / "cheikh-selected.json"
LADDERS_JSON_PATH = ROOT / "cheikh-ladders.json"
LADDERS_MD_PATH = ROOT / "سلالم_التعليم_ومصفوفة_الخطب.md"

# The 51 Mandatory Foundational Core Series (النظام الأول: النواة التأصيلية الصلبة)
TIER1_CORE_IDS = {
    # 1. المدخل المعرفي ومنهجية الطلب وفقه السنن (8)
    "hawwa__adab_talib_ilm",
    "kamali__s018",
    "ayman__s009",
    "ayman__s010",
    "bouti__s024",
    "sayed__s059",
    "gomaa__s044",
    "sariri__s030",
    # 2. العقيدة الإسلامية وعلم الكلام (5)
    "bardoni__s001",
    "bardoni__s003",
    "bardoni__s002",
    "bouti__s021",
    "omari__s001",
    # 3. الفقه المالكي والقواعد الفقهية والفرائض (5)
    "sariri__s003",
    "dedew__dawrat_faraid",
    "bardoni__s006",
    "bardoni__s007",
    "sariri__s004",
    # 4. أصول الفقه ومقاصد الشريعة (6)
    "sariri__s017",
    "sariri__s007",
    "sariri__s014",
    "bardoni__s008",
    "sariri__s011",
    "sariri__s021",
    # 5. النحو والإعراب (3)
    "alihani__s003",
    "alihani__s011",
    "bardoni__s009",
    # 6. الصرف والاشتقاق (4)
    "sariri__s027",
    "alihani__s022",
    "alihani__s025",
    "alihani__s026",
    # 7. البلاغة والبيان (4)
    "alihani__s030",
    "bardoni__s013",
    "bardoni__s012",
    "alihani__s034",
    # 8. علوم الآلة العقلية — المنطق والوضع وآداب البحث (4)
    "omari__s009",
    "bardoni__s014",
    "bardoni__s017",
    "bardoni__s015",
    # 9. علوم القرآن وأصول التفسير ومقاصد السور (5)
    "alihani__tibyan",
    "alihani__s040",
    "sayed__s022",
    "bouti__s002",
    "dedew__sharh_ikleel",
    # 10. الحديث النبوي ومصطلحه وفقه السيرة والتزكية (7)
    "asimi__s011",
    "sayed__s005",
    "hawwa__bidayat_hidayah",
    "asimi__s012",
    "bouti__s030",
    "asimi__s013",
    "hafiz__arbain_usul_din",
}

# Tier 2 Reference & Comparative Commentaries (النظام الثاني: الخزانة المرجعية التحقيقية)
TIER2_REFERENCE_IDS = {
    # Parallel Creed & Kalam & Philosophy
    "asimi__s007", "asimi__s008", "asimi__s009",
    "omari__s002", "omari__s004", "omari__s005", "omari__s012", "omari__s013", "omari__s014", "omari__s015", "omari__s016", "omari__s017",
    "bardoni__s004", "bardoni__s019", "bardoni__s020", "bardoni__s021",
    "dedew__sharh_manzouma_adoudiya", "bouti__s022", "gomaa__s027", "gomaa__s028",
    # Parallel Arabic Grammar, Morphology, Rhetoric, Literature
    "alihani__s001", "alihani__s005", "alihani__s006", "alihani__s007", "alihani__s008", "alihani__s009",
    "alihani__s010", "alihani__s013", "alihani__s014", "alihani__s015", "alihani__s016", "alihani__s018", "alihani__s019",
    "alihani__s021", "alihani__s023", "alihani__s024", "alihani__s027",
    "alihani__s029", "alihani__s031", "alihani__s032", "alihani__s033", "alihani__s035", "alihani__s036", "alihani__s037", "alihani__s038",
    "alihani__s042", "alihani__s043", "alihani__s044", "alihani__s045", "alihani__s046", "alihani__s049", "alihani__s050",
    "bardoni__s010",
    "asimi__s025", "asimi__s026", "asimi__s029", "asimi__s030", "asimi__s031", "asimi__s032",
    "sariri__s024", "sariri__s025",
    "dedew__sharh_jazariya", "dedew__sharh_muallaqat_imru_alqais",
    "kamali__s017", "kamali__s019", "kamali__s020",
    "ayman__s013", "ayman__s014", "ayman__s015",
    # Parallel Logic & Categories
    "bardoni__s016", "omari__s010", "omari__s011", "asimi__s033", "asimi__s034", "asimi__s035",
    # Parallel Hadith Sciences & Large Hadith Commentaries
    "sayed__s001", "sayed__s002", "sayed__s003", "sayed__s004", "sayed__s008", "sayed__s010", "sayed__s011", "sayed__s012", "sayed__s013", "sayed__s014", "sayed__s047", "sayed__s050", "sayed__s052", "sayed__s053",
    "dedew__mukhtasar_bukhari", "dedew__sharh_bukhari", "dedew__sharh_maalim_sunnah", "dedew__sharh_taqreeb_asaneed", "dedew__kursi_arbaeen_nawawiya",
    "kamali__s001", "kamali__s002", "kamali__s003", "kamali__s006",
    "hafiz__muwatta", "hafiz__kashf_ghumma", "hafiz__bulugh_maram", "hafiz__adhkar_nawawi",
    "bouti__s020", "jifri__s007", "gomaa__s019", "gomaa__s022", "gomaa__s024", "gomaa__s025", "gomaa__s026",
    "asimi__s014",
    # Parallel Fiqh & Usul & Maqasid Encyclopedias
    "sariri__s001", "sariri__s002", "sariri__s006", "sariri__s008", "sariri__s009", "sariri__s010", "sariri__s012", "sariri__s013", "sariri__s015", "sariri__s016", "sariri__s019", "sariri__s020", "sariri__s022", "sariri__s044", "sariri__s046", "sariri__s048",
    "dedew__sharh_miftah_wusool", "dedew__sharh_waraqat", "dedew__dawrat_maratib_dalala_kuwait", "dedew__dawrat_tahara_salah", "dedew__fiqh_muamalat", "dedew__ahkam_siyam_series", "dedew__dawrat_sinaat_fatwa_nawazil", "dedew__madakhil_uloom_manhajiya",
    "kamali__s004", "kamali__s005", "kamali__s029",
    "asimi__s015", "asimi__s016", "asimi__s017", "asimi__s020", "asimi__s021", "asimi__s022",
    "hawwa__ibadat2_ikhtiyar", "hawwa__ahwal_shakhsiyah_quduri", "hawwa__fiqh_ahadith_ahkam", "hawwa__usool_fiqh_1", "hawwa__usool_ifta_isad_mufti",
    "gomaa__s001", "gomaa__s002", "gomaa__s004", "gomaa__s005", "gomaa__s006", "gomaa__s007", "gomaa__s008", "gomaa__s052", "gomaa__s053", "gomaa__s054", "gomaa__s080", "gomaa__s083", "gomaa__s084",
    "hafiz__fawaid_thaminah", "hafiz__sullam_tawfiq", "hafiz__muqaddimat_majmu", "hafiz__risala_jamia", "hafiz__ahkam_muamalat_hajj",
    "bouti__s031", "bouti__s042", "bouti__s046", "sayed__s016",
    # Analytical Tafsir Encyclopedias
    "bouti__s001", "asimi__s001", "asimi__s002", "asimi__s003",
    "gomaa__s030", "gomaa__s031", "gomaa__s032", "gomaa__s033", "gomaa__s034", "gomaa__s035",
    "hafiz__tafsir_monday", "hafiz__tafsir_ramadan",
    "samarrai__s064", "samarrai__s065", "samarrai__s066",
}


def get_architectural_tier(sid: str, sh_id: str) -> tuple[int, str]:
    if sid in TIER1_CORE_IDS:
        return (1, "النظام الأول: النواة التأصيلية الصلبة (السلم الدراسي الإلزامي)")
    if sid in TIER2_REFERENCE_IDS or (sh_id == "shaarawy" and sid <= "shaarawy__s063"):
        return (2, "النظام الثاني: الخزانة المرجعية التحقيقية (شروح المقارنة والموسوعات العلمية)")
    return (3, "النظام الثالث: مصنع الإنتاج الوعظي والخطابي المسجدي (المنجم التطبيقي للخطب والدروس)")


def classify_series(s: dict, sheikh_id: str, sheikh_name: str):
    sid = s["id"]
    num = s.get("order_no") or 1

    # --- BARDONI ---
    if sheikh_id == "bardoni":
        if sid in ("bardoni__s001", "bardoni__s003"):
            return (2, 1, "المستوى الأول: التأسيسي", 2)
        if sid == "bardoni__s002":
            return (2, 2, "المستوى الثاني: المتوسط", 2)
        if sid in ("bardoni__s004", "bardoni__s019", "bardoni__s020", "bardoni__s021"):
            return (2, 3, "المستوى الثالث: التحقيق الكلامي والمناظرات العقدية", 9)
        if sid == "bardoni__s006":
            return (3, 2, "المستوى الثاني: المتوسط (شرح الرسالة)", 12)
        if sid == "bardoni__s007":
            return (3, 3, "المستوى الثالث: المتقدم (القواعد الفقهية للزقاق)", 12)
        if sid == "bardoni__s008":
            return (4, 2, "المستوى الثاني: المتوسط (مراقي السعود)", 12)
        if sid in ("bardoni__s009", "bardoni__s010"):
            return (5, 3, "المستوى الثالث: المتقدم (شروح ألفية ابن مالك)", 10)
        if sid in ("bardoni__s012", "bardoni__s013"):
            return (7, 2, "المستوى الثاني: المتوسط (الجوهر المكنون ونظم الاستعارة)", 10)
        if sid in ("bardoni__s014", "bardoni__s015", "bardoni__s016", "bardoni__s017"):
            return (8, 3, "المستوى الثاني والثالث: المنطق والمقولات والوضع وآداب البحث", 9)

    # --- SARIRI ---
    if sheikh_id == "sariri":
        if sid == "sariri__s003":
            return (3, 1, "المستوى الأول: التأسيسي (أسهل المسالك)", 12)
        if sid in ("sariri__s002", "sariri__s004"):
            return (3, 2, "المستوى الثاني: الصناعة الفقهية والشرح الكبير لأبواب المواسم", 12)
        if sid == "sariri__s001":
            return (3, 3, "المستوى الثالث: المتقدم (شرح مختصر خليل)", 12)
        if sid in ("sariri__s007", "sariri__s008", "sariri__s017", "sariri__s019", "sariri__s020"):
            return (4, 1, "المستوى الأول: التأسيسي (الورقات ومعالم النظر)", 12)
        if sid in ("sariri__s010", "sariri__s012", "sariri__s013", "sariri__s014", "sariri__s015", "sariri__s016"):
            return (4, 2, "المستوى الثاني: المتوسط (إيصال السالك والضروري ومرتقى الوصول)", 12)
        if sid in ("sariri__s006", "sariri__s009", "sariri__s011", "sariri__s021", "sariri__s022", "sariri__s048"):
            return (4, 3, "المستوى الثالث: المتقدم (جمع الجوامع ومراقي السعود ومفتاح الوصول والمقاصد)", 12)
        if sid == "sariri__s027":
            return (6, 1, "المستوى الأول: التأسيسي (الصرف الصغير)", 10)
        if sid in ("sariri__s024", "sariri__s025"):
            return (7, 3, "المستوى الثالث: تحصيل الملكة الأدبية والبيانية (مقامات الحريري والكامل للمبرد)", 10)
        if sid in ("sariri__s031", "sariri__s033", "sariri__s034", "sariri__s035", "sariri__s036", "sariri__s038"):
            return (2, 3, "المستوى الثالث: التحصين العقدي والفكري ونقد العلمانية والتنوير", 9)
        if sid == "sariri__s039":
            return (2, 2, "المستوى الثاني: أحوال الاحتضار والدار الآخرة", 11)
        if sid == "sariri__s041":
            return (3, 2, "المستوى الثاني: فقه بناء الأسرة في الإسلام", 6)
        if sid in ("sariri__s030", "sariri__s037", "sariri__s044"):
            return (1, 3, "المستوى الثالث: فلسفة التشريع وبناء الملكة الفقهية", 8)
        if sid in ("sariri__s043", "sariri__s046"):
            return (3, 2, "المستوى التطبيقي: الخطب المنبرية والفتاوى", 12)

    # --- ALIHANI ---
    if sheikh_id == "alihani":
        if 1 <= num <= 6:
            return (5, 1, "المستوى الأول: التأسيسي (مبادئ العربية والآجرومية ومتممتها)", 10)
        if 7 <= num <= 13:
            return (5, 2, "المستوى الثاني: المتوسط (إعراب جزء عم وملحة الإعراب والقطر وموصل الطلاب)", 10)
        if 14 <= num <= 19:
            return (5, 3, "المستوى الثالث: المتقدم (شروح الألفية والتسهيل والدر المصون)", 10)
        if 20 <= num <= 23:
            return (6, 1, "المستوى الأول: التأسيسي (الأمثلة والبناء والمقصود)", 10)
        if 24 <= num <= 26:
            return (6, 2, "المستوى الثاني: المتوسط (تصريف العزي والإعلال والإبدال)", 10)
        if num in (27, 28):
            return (6, 3, "المستوى الثالث: المتقدم (شذا العرف في فن الصرف)", 10)
        if 29 <= num <= 34:
            return (7, 1, "المستوى الأول: التأسيسي (تحفة الإخوان والبلاغة الواضحة ودروس البلاغة والسمرقندية)", 10)
        if 35 <= num <= 38:
            return (7, 3, "المستوى الثالث: المتقدم (المنهاج الواضح ودورة البلاغة القرآنية)", 10)
        if num in (39, 40, 42, 44, 48, 51, 52):
            return (9, 1, "المستوى الأول: علوم القرآن ومقاصد السور وأصول التفسير وآداب التلاوة", 10)
        if num in (43, 45, 46, 47):
            return (9, 3, "المستوى الثالث: التفسير التحليلي والبياني (تفسير النسفي ولطائف البقرة)", 10)
        if num in (49, 50):
            return (3, 1, "المستوى الأول: فقه العبادات والمواريث", 12)

    # --- SHAARAWY ---
    if sheikh_id == "shaarawy":
        if sid in ("shaarawy__s061", "shaarawy__s062", "shaarawy__s063"):
            return (9, 1, "المستوى الأول: مقدمات التفسير وسورة الفاتحة وإعجاز القرآن", 10)
        if sid == "shaarawy__s060":
            return (9, 1, "المستوى الأول: تفسير جزء عم وقصار المفصل", 10)
        if sid in ("shaarawy__s086", "shaarawy__s087"):
            return (9, 2, "المستوى الثاني: موسوعة قصص الأنبياء والقصص القرآني", 3)
        if sid in ("shaarawy__s088", "shaarawy__s090"):
            return (10, 2, "المستوى الثاني: السيرة النبوية ووصايا الرسول صلى الله عليه وسلم", 4)
        if sid == "shaarawy__s094":
            return (3, 2, "المستوى الثاني: فقه ومقاصد الحج وخطب عرفة", 11)
        if sid in ("shaarawy__s089", "shaarawy__s091", "shaarawy__s092", "shaarawy__s097", "shaarawy__s098", "shaarawy__s100"):
            return (10, 2, "المستوى التطبيقي: الخواطر الإيمانية والفتاوى وعلاج الكبائر", 1)
        return (9, 2, "المستوى الثاني: التفسير الإيماني والبياني للقرآن الكريم (البقرة إلى الممتحنة)", 10)

    # --- SAMARRAI ---
    if sheikh_id == "samarrai":
        if sid == "samarrai__s003":
            return (2, 2, "المستوى الثاني: براهين النبوة من الإعجاز البياني", 9)
        if sid == "samarrai__s009":
            return (5, 3, "المستوى الثالث: مميزات العربية ومعاني النحو", 10)
        if sid == "samarrai__s010":
            return (9, 2, "المستوى الثاني: اللمسات البيانية في آيات الصيام", 11)
        if sid == "samarrai__s011":
            return (9, 2, "المستوى الثاني: اللمسات البيانية في قصة موسى والقصص القرآني", 3)
        return (7, 3, "المستوى الثالث: الإعجاز البياني واللمسات البلاغية في سور القرآن", 10)

    # --- OMARI ---
    if sheikh_id == "omari":
        if sid in ("omari__s009", "omari__s010", "omari__s011", "omari__s012"):
            return (8, 1, "المستوى الأول والثاني: السلم المنورق وإيساغوجي ومعيار العلم", 9)
        if sid in ("omari__s002", "omari__s003", "omari__s004", "omari__s005"):
            return (2, 2, "المستوى الثاني: المتوسط (أم البراهين والعقائد النسفية واعتقاد القشيرية)", 2)
        if sid == "omari__s001":
            return (2, 3, "المستوى الثالث: المتقدم (الاقتصاد في الاعتقاد للغزالي)", 2)
        if sid == "omari__s007":
            return (10, 1, "المستوى الأول: التزكية وآداب سلوك المريد", 1)
        return (2, 3, "المستوى الثالث: نقد الفلسفة الحديثة وفلسفة الدين وعلم الكلام", 9)

    # --- BOUTI ---
    if sheikh_id == "bouti":
        if sid == "bouti__s001":
            return (9, 3, "المستوى الثالث: التفسير التحليلي والتربوي للقرآن الكريم", 10)
        if sid == "bouti__s002":
            return (9, 1, "المستوى الأول: علوم القرآن ودراساته التطبيقية", 10)
        if sid in ("bouti__s003", "bouti__s016", "bouti__s018"):
            return (9, 2, "المستوى الثاني: إعجاز القرآن الكريم ودفع الشبهات عنه", 9)
        if sid in ("bouti__s004", "bouti__s005", "bouti__s006", "bouti__s007", "bouti__s008", "bouti__s009", "bouti__s010", "bouti__s011", "bouti__s012", "bouti__s013", "bouti__s014", "bouti__s015"):
            if sid == "bouti__s007":
                return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 3)
            if sid in ("bouti__s010", "bouti__s011"):
                return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 4)
            if sid == "bouti__s006":
                return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 5)
            if sid == "bouti__s008":
                return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 8)
            return (9, 2, "المستوى الثاني: التدبر الموضوعي للقرآن الكريم", 1)
        if sid == "bouti__s020":
            return (10, 2, "المستوى الثاني: شروح السنة الجامعة (رياض الصالحين)", 5)
        if sid == "bouti__s022":
            return (2, 1, "المستوى الأول: التأسيسي", 2)
        if sid == "bouti__s021":
            return (2, 2, "المستوى الثاني: المتوسط (كبرى اليقينيات الكونية)", 2)
        if sid in ("bouti__s023", "bouti__s026", "bouti__s027", "bouti__s028", "bouti__s062"):
            return (2, 3, "المستوى الثالث: تفنيد الشبهات المعاصرة والمناظرات الفكرية", 9)
        if sid in ("bouti__s024", "bouti__s047"):
            return (1, 2, "المستوى الثاني: فقه السنن الإلهية ومنهج الدعوة", 8)
        if sid == "bouti__s025":
            return (2, 2, "المستوى الثاني: الإيمان باليوم الآخر (رحلة الخلود)", 11)
        if sid == "bouti__s030":
            return (10, 2, "المستوى الثاني: فقه السيرة النبوية والخلافة الراشدة", 4)
        if sid in ("bouti__s031", "bouti__s042", "bouti__s043", "bouti__s046"):
            return (4, 2, "المستوى الثاني: تاريخ التشريع وفقه الجهاد وتحرير المسائل", 8)
        if sid in ("bouti__s033", "bouti__s034", "bouti__s035"):
            return (10, 3, "المستوى الثالث: شروح الحكم العطائية والتزكية والمواعظ", 1)
        if sid == "bouti__s036":
            return (10, 2, "المستوى الثاني: الطب الروحي والنفسي (علاج الكآبة)", 7)
        if sid == "bouti__s049":
            return (10, 1, "المستوى الأول: ترسيخ التربية الدينية والأسرة", 6)
        if sid in ("bouti__s053", "bouti__s054", "bouti__s055", "bouti__s056", "bouti__s057", "bouti__s058", "bouti__s059", "bouti__s060", "bouti__s061"):
            return (10, 3, "المستوى التطبيقي: الخطب المنبرية", 12)

    # --- ASIMI ---
    if sheikh_id == "asimi":
        if sid in ("asimi__s001", "asimi__s002", "asimi__s003", "asimi__s005"):
            return (9, 2, "المستوى الثاني: التفسير التحليلي والتدبر القرآني (البقرة وآل عمران والنساء والكهف)", 10)
        if sid == "asimi__s006":
            return (9, 2, "المستوى الثاني: سلسلة القصص القرآني الكاملة", 3)
        if sid in ("asimi__s007", "asimi__s008", "asimi__s009", "asimi__s010"):
            return (2, 1, "المستوى الأول: التأسيسي (مقدمات السنوسي وصغرى الصغرى)", 2)
        if sid in ("asimi__s011", "asimi__s012", "asimi__s013"):
            return (10, 2, "المستوى الأول إلى الثالث: السلم المتكامل في مصطلح الحديث وعلومه", 12)
        if sid in ("asimi__s014", "asimi__s040"):
            return (10, 2, "المستوى الثاني: تراجم الأئمة الأعلام ومكانتهم الحديثية", 4)
        if sid in ("asimi__s015", "asimi__s016", "asimi__s017"):
            return (3, 2, "المستوى الأول إلى الثالث: الفقه المقارن (نور الإيضاح والقدوري واللباب)", 12)
        if sid in ("asimi__s020", "asimi__s021", "asimi__s022"):
            return (4, 1, "المستوى الأول والثاني: مبادئ الأصول والخلاصة وأصول الشاشي", 12)
        if sid in ("asimi__s025", "asimi__s026"):
            return (5, 2, "المستوى الثاني والثالث: شرح قطر الندى وشرح ابن عقيل", 10)
        if sid in ("asimi__s029", "asimi__s030"):
            return (6, 2, "المستوى الأول والثالث: عنوان الظرف وشذا العرف في الصرف", 10)
        if sid in ("asimi__s031", "asimi__s032"):
            return (7, 2, "المستوى الأول والثاني: دروس البلاغة وجواهر البلاغة", 10)
        if sid in ("asimi__s033", "asimi__s034", "asimi__s035"):
            return (8, 1, "المستوى الأول: التأسيسي (السلم والمفتاح وإيساغوجي)", 9)
        if sid in ("asimi__s036", "asimi__s037", "asimi__s038", "asimi__s039"):
            return (10, 2, "المستوى الثاني: السيرة النبوية التفصيلية وسير الخلفاء الراشدين", 4)
        if sid in ("asimi__s041", "asimi__s042", "asimi__s043", "asimi__s044", "asimi__s046"):
            return (10, 2, "المستوى الثاني: التزكية وأعمال القلوب ومداواة النفوس", 1)
        if sid == "asimi__s045":
            return (2, 1, "المستوى الأول: الإيمان بالدار الآخرة", 11)
        if sid == "asimi__s048":
            return (2, 1, "المستوى الأول: فقه أسماء الله الحسنى", 2)
        if sid in ("asimi__s051", "asimi__s052", "asimi__s053"):
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
        if sid in ("hawwa__adab_talib_ilm", "hawwa__ijazat_duat", "hawwa__sawaid_bina"):
            return (1, 1, "المستوى الأول: آداب طالب العلم وإعداد الدعاة وبناء الهوية", 6)
        if sid in ("hawwa__ibadat2_ikhtiyar", "hawwa__ahwal_shakhsiyah_quduri", "hawwa__fiqh_ahadith_ahkam"):
            return (3, 2, "المستوى الثاني: الفقه المقارن وفقه أحاديث الأحكام", 12)
        if sid in ("hawwa__usool_fiqh_1", "hawwa__usool_ifta_isad_mufti"):
            return (4, 2, "المستوى الثاني: أصول الفقه وأصول الإفتاء ورسم المفتي", 12)
        if sid == "hawwa__islah_iqtisadi":
            return (3, 2, "المستوى الثاني: الفقه الاقتصادي والإصلاح المالي", 5)
        if sid in ("hawwa__tazkiyat_lisan", "hawwa__adab_ammah"):
            return (10, 1, "المستوى الأول: الآداب الشرعية وتزكية اللسان", 5)
        return (10, 2, "المستوى الثاني: السلم المتكامل في التزكية والسلوك", 1)

    # --- HAFIZ ---
    if sheikh_id == "hafiz":
        if sid in ("hafiz__muwatta", "hafiz__kashf_ghumma", "hafiz__bulugh_maram", "hafiz__adhkar_nawawi"):
            return (10, 3, "المستوى الثالث: شروح الحديث المسندة (الموطأ وكشف الغمة وبلوغ المرام والأذكار)", 12)
        if sid in ("hafiz__tafsir_monday", "hafiz__tafsir_ramadan", "hafiz__tafsir_fatiha_qisar"):
            return (9, 2, "المستوى الأول والثاني: مجالس التفسير وتدبر الآيات البينات", 10)
        if sid == "hafiz__qasas_haqq":
            return (9, 2, "المستوى الثاني: قصص الأنبياء في القرآن الكريم", 3)
        if sid in ("hafiz__sullam_tawfiq", "hafiz__sifat_salat_muqarrabin", "hafiz__fawaid_thaminah", "hafiz__risala_jamia", "hafiz__ahkam_muamalat_hajj", "hafiz__muqaddimat_majmu"):
            return (3, 1, "المستوى الأول والثاني: فقه العبادات والمعاملات وأسرار الصلاة", 11)
        if sid in ("hafiz__adab_mutaallim", "hafiz__tadhkirat_sami"):
            return (1, 1, "المستوى الأول: آداب العالم والمتعلم وآفات العلم", 6)
        if sid in ("hafiz__adab_fid_din", "hafiz__khuluquna", "hafiz__silat_aqrabin"):
            return (10, 1, "المستوى الأول: الآداب النبوية وبناء الخلق وصلة الأرحام", 5)
        if sid in ("hafiz__jawalan_ruh_rusul", "hafiz__bahjat_mahafil", "hafiz__nafais_seerah", "hafiz__mafahim_sahhaha"):
            return (10, 2, "المستوى الثاني: السيرة النبوية والشمائل ورسل النبي صلى الله عليه وسلم", 4)
        return (10, 3, "المستوى الثالث: أمهات كتب التزكية والسلوك (الإحياء والأربعين والحكم والمكاتبات)", 1)

    # --- JIFRI ---
    if sheikh_id == "jifri":
        if sid in ("jifri__s018", "jifri__s019", "jifri__s020", "jifri__s023", "jifri__s028"):
            return (2, 2, "المستوى الثاني: تثبيت اليقين ومعالجة الشك والإلحاد", 9)
        if sid == "jifri__s007":
            return (10, 2, "المستوى الثاني: مجالس صحيح البخاري (كتاب الصوم وقيام رمضان)", 11)
        if sid in ("jifri__s021", "jifri__s022", "jifri__s024", "jifri__s025"):
            return (10, 1, "المستوى الأول: الأخلاق المحمدية وإتقان العمل والإنسانية قبل التدين", 5)
        if sid in ("jifri__s026", "jifri__s027"):
            return (10, 1, "المستوى الأول: هدي السيرة في الأسرة والزواج وتربية الأبناء", 6)
        if sid in ("jifri__s013", "jifri__s029", "jifri__s030", "jifri__s036", "jifri__s044", "jifri__s045"):
            return (1, 2, "المستوى الثاني: الفكر الدعوي والحوار المعرفي والندوات العلمية", 8)
        return (10, 2, "المستوى الثاني: أصول السلوك والتزكية (قبس النور المبين وأيها المريد والحكم)", 1)

    # --- GOMAA ---
    if sheikh_id == "gomaa":
        if sid in ("gomaa__s001", "gomaa__s002", "gomaa__s004", "gomaa__s052", "gomaa__s053", "gomaa__s054", "gomaa__s080"):
            return (3, 2, "المستوى الثاني: الفقه المقارن والقواعد الفقهية والأشباه والنظائر وتاريخ التشريع", 12)
        if sid in ("gomaa__s005", "gomaa__s006", "gomaa__s007", "gomaa__s008"):
            return (4, 2, "المستوى الثاني: أصول الفقه وتخريج الفروع على الأصول والرسالة للشافعي", 12)
        if sid in ("gomaa__s019", "gomaa__s022", "gomaa__s024", "gomaa__s025", "gomaa__s026"):
            return (10, 2, "المستوى الثاني: شروح الشفا والأربعين النووية والبخاري ومسند أحمد", 4)
        if sid in ("gomaa__s027", "gomaa__s028", "gomaa__s066"):
            return (2, 1, "المستوى الأول: الخريدة البهية وعقيدة العوام وأسماء الله الحسنى", 2)
        if sid in ("gomaa__s030", "gomaa__s031", "gomaa__s032", "gomaa__s033", "gomaa__s034", "gomaa__s035", "gomaa__s037", "gomaa__s038"):
            return (9, 2, "المستوى الثاني: تفسير القرآن الكريم (مقدمة التفسير والفاتحة إلى المائدة)", 10)
        if sid in ("gomaa__s043", "gomaa__s044", "gomaa__s083", "gomaa__s084"):
            return (1, 2, "المستوى الثاني: النموذج المعرفي الإسلامي ومكونات العقل المسلم والمدخل إلى التراث", 9)
        if sid in ("gomaa__s039", "gomaa__s040", "gomaa__s041", "gomaa__s042", "gomaa__s047", "gomaa__s049", "gomaa__s050", "gomaa__s055"):
            return (2, 2, "المستوى الثاني: الحوار الشبابي وتفنيد التشدد والشبهات", 9)
        if sid in ("gomaa__s009", "gomaa__s010", "gomaa__s011", "gomaa__s012", "gomaa__s013", "gomaa__s014", "gomaa__s016", "gomaa__s017", "gomaa__s051", "gomaa__s056", "gomaa__s057", "gomaa__s058", "gomaa__s059", "gomaa__s060", "gomaa__s061", "gomaa__s062"):
            return (10, 2, "المستوى الثاني والثالث: شروح الإحياء والحكم العطائية والرسالة القشيرية ومنازل السائرين", 1)
        if sid in ("gomaa__s048", "gomaa__s063", "gomaa__s064", "gomaa__s078"):
            return (10, 1, "المستوى الأول: فقه الدعاء النبوي والمبشرات والرحمات", 11)
        if sid in ("gomaa__s045", "gomaa__s067", "gomaa__s068", "gomaa__s070", "gomaa__s071", "gomaa__s072", "gomaa__s073", "gomaa__s074", "gomaa__s075", "gomaa__s076"):
            return (10, 2, "المستوى الثاني: السيرة النبوية والشمائل ومناقب الصحابة والأئمة والمجددين", 4)
        return (3, 2, "المستوى التطبيقي: الفتاوى المعاصرة والمجالس العامة", 12)

    # --- SAYED ---
    if sheikh_id == "sayed":
        if sid in ("sayed__s001", "sayed__s002", "sayed__s003", "sayed__s004", "sayed__s005", "sayed__s083"):
            return (10, 1, "المستوى الأول والثاني: حفظ وفهم السنة النبوية (المنهاج ورياض الصالحين والجمع بين الصحيحين)", 5)
        if sid in ("sayed__s008", "sayed__s010", "sayed__s011", "sayed__s012", "sayed__s013", "sayed__s014", "sayed__s047", "sayed__s050", "sayed__s052", "sayed__s053"):
            return (10, 3, "المستوى الثاني والثالث: علوم الحديث والعلل ومناهج المحدثين وحجية السنة", 9)
        if sid == "sayed__s016":
            return (3, 3, "المستوى الثالث: السياسة الشرعية وفقه الأحكام السلطانية", 8)
        if sid == "sayed__s058":
            return (7, 2, "المستوى الثاني: تنمية القوة البيانية (دلائل الإعجاز للجرجاني أنموذجاً)", 10)
        if sid == "sayed__s073":
            return (10, 2, "المستوى الثاني: التأصيل المنهجي لقضايا المرأة والأسرة", 6)
        if sid in ("sayed__s015", "sayed__s065", "sayed__s066", "sayed__s067", "sayed__s082", "sayed__s087", "sayed__s112"):
            return (10, 2, "المستوى الثاني: التزكية وأعمال القلوب ومقاصد مدارج السالكين", 1)
        if sid in ("sayed__s021", "sayed__s029", "sayed__s030", "sayed__s031", "sayed__s088"):
            return (9, 2, "المستوى الثاني: قصص الأنبياء وأولو العزم في القرآن الكريم", 3)
        if sid in ("sayed__s022", "sayed__s023", "sayed__s024", "sayed__s025", "sayed__s026", "sayed__s027", "sayed__s028", "sayed__s032", "sayed__s033"):
            return (9, 1, "المستوى الأول: مقاصد السور والتدبر المنهجي للقرآن الكريم", 10)
        if sid in ("sayed__s035", "sayed__s036", "sayed__s037", "sayed__s038", "sayed__s040", "sayed__s041", "sayed__s042", "sayed__s043", "sayed__s046", "sayed__s089", "sayed__s090", "sayed__s091", "sayed__s092"):
            return (10, 1, "المستوى الأول والثاني: السيرة النبوية والخلافة الراشدة والتاريخ الإسلامي", 4)
        if sid in ("sayed__s054", "sayed__s074", "sayed__s075", "sayed__s076", "sayed__s077", "sayed__s078", "sayed__s079", "sayed__s081"):
            return (2, 2, "المستوى الأول والثاني: البناء العقدي وصناعة المحاور ومعالجة الشبهات الفكرية", 9)
        if sid in ("sayed__s051", "sayed__s055", "sayed__s056", "sayed__s057", "sayed__s084", "sayed__s085", "sayed__s093", "sayed__s109"):
            return (1, 1, "المستوى الأول: مداخل العلوم الشرعية ومنهجية الطلب والتفكير الناقد", 6)
        if sid in ("sayed__s017", "sayed__s059", "sayed__s060", "sayed__s061", "sayed__s062", "sayed__s063", "sayed__s064", "sayed__s072", "sayed__s113"):
            return (1, 2, "المستوى الثاني: فقه الإصلاح والسنن الإلهية وقضايا الأمة وبيت المقدس", 8)
        return (1, 1, "المستوى الأول: بناء الجيل الصاعد والشباب ومعالجة التفاهة", 6)

    # --- DEDEW ---
    if sheikh_id == "dedew":
        if sid == "dedew__sharh_ikleel":
            return (9, 3, "المستوى الثالث: استنباط الأحكام واللطائف من القرآن (الإكليل للسيوطي)", 10)
        if sid == "dedew__sharh_jazariya":
            return (9, 1, "المستوى الأول: التجويد وعلوم الأداء القرآني (المقدمة الجزرية)", 10)
        if sid == "dedew__majalis_qiyam_ramadan_full":
            return (9, 2, "المستوى الثاني: مجالس التدبر والتعليق على المقروء في قيام رمضان", 11)
        if sid in ("dedew__mukhtasar_bukhari", "dedew__sharh_bukhari", "dedew__sharh_maalim_sunnah", "dedew__sharh_taqreeb_asaneed", "dedew__kursi_arbaeen_nawawiya"):
            return (10, 3, "المستوى الثالث: شروح البخاري ومعالم السنة وتقريب الأسانيد والأربعين", 12)
        if sid == "dedew__ahadith_fitan_malihim":
            return (10, 2, "المستوى الثاني: فقه أحاديث الفتن والملاحم وأشراط الساعة", 8)
        if sid == "dedew__sharh_manzouma_adoudiya":
            return (2, 1, "المستوى الأول: المنظومة العدودية في العقيدة", 2)
        if sid in ("dedew__sharh_waraqat", "dedew__sharh_miftah_wusool", "dedew__dawrat_maratib_dalala_kuwait"):
            return (4, 1, "المستوى الأول والثاني: الورقات ومفتاح الوصول ومراتب الدلالة", 12)
        if sid in ("dedew__dawrat_tahara_salah", "dedew__fiqh_muamalat", "dedew__dawrat_faraid", "dedew__ahkam_siyam_series", "dedew__dawrat_sinaat_fatwa_nawazil"):
            return (3, 1, "المستوى الأول والثاني: دورات فقه العبادات والمعاملات والفرائض وصناعة الفتوى", 12)
        if sid in ("dedew__sharh_akhlaq_wa_siyar", "dedew__sharh_jami_adab", "dedew__sharh_maharim_lisan", "dedew__barnamaj_fadail"):
            return (10, 2, "المستوى الثاني: مداواة النفوس والآداب الشرعية ومحارم اللسان والفضائل", 5)
        if sid == "dedew__sharh_muallaqat_imru_alqais":
            return (7, 3, "المستوى الثالث: الأدب العربي القديم والشواهد اللغوية", 10)
        if sid == "dedew__madakhil_uloom_manhajiya":
            return (1, 1, "المستوى الأول: مداخل العلوم الشرعية ومنهجية الطلب وتاريخ المذهب المالكي", 6)
        if sid in ("dedew__barnamaj_qissat_nuh", "dedew__barnamaj_abu_bashariya_adam", "dedew__barnamaj_ahsan_alqasas"):
            return (9, 2, "المستوى الثاني: قصص الأنبياء وأحسن القصص في القرآن الكريم", 3)
        if sid in ("dedew__seerah_qadaya_s1", "dedew__seerah_qadaya_s2", "dedew__barnamaj_misk_alkhitam"):
            return (10, 2, "المستوى الثاني: السيرة النبوية وقضايا الأمة", 4)
        return (3, 2, "المستوى الثاني: برامج معالم ومفاهيم والسياسة الشرعية وفقه الأمة", 8)

    # --- KAMALI ---
    if sheikh_id == "kamali":
        if sid in ("kamali__s001", "kamali__s002", "kamali__s003", "kamali__s006"):
            return (10, 3, "المستوى الثالث: مجالس موطأ الإمام مالك والأربعين للمنذري ورياض الصالحين", 12)
        if sid in ("kamali__s004", "kamali__s005", "kamali__s029"):
            return (3, 2, "المستوى الثاني: شرح رسالة ابن أبي زيد القيرواني ومباحث الفقه المالكي", 12)
        if sid in ("kamali__s007", "kamali__s008", "kamali__s009", "kamali__s010", "kamali__s011", "kamali__s012", "kamali__s013", "kamali__s015"):
            return (9, 2, "المستوى الثاني: التفسير التحليلي والوعظي والأدبي للسور", 10)
        if sid in ("kamali__s017", "kamali__s019", "kamali__s020"):
            return (7, 2, "المستوى الثاني: شروح القصائد الأدبية والحكمية (لامية العرب وابن الوردي وعنوان الحكم)", 5)
        if sid == "kamali__s018":
            return (1, 1, "المستوى الأول: شرح تائية الألبيري في الأدب وطلب العلم", 6)
        if sid in ("kamali__s016", "kamali__s021", "kamali__s022", "kamali__s023", "kamali__s024", "kamali__s030"):
            return (10, 2, "المستوى الثاني: سيرة الحبيب صلى الله عليه وسلم وشمائله وسيرة الإمام مالك والصحابة", 4)
        return (10, 2, "المستوى التطبيقي: المحاضرات الوعظية والعلمية الجامعة", 1)

    # --- HASHEMI ---
    if sheikh_id == "hashemi":
        if sid in ("hashemi__s010", "hashemi__s011", "hashemi__s012", "hashemi__s013", "hashemi__s014", "hashemi__s015", "hashemi__s016", "hashemi__s020"):
            return (1, 2, "المستوى الثاني: فقه الأسرة والزواج وتربية الأبناء وفقه المرأة", 6)
        if sid in ("hashemi__s017", "hashemi__s018", "hashemi__s019", "hashemi__s022"):
            return (9, 2, "المستوى الثاني: المجالس الرمضانية القرآنية في تدبر القرآن وفقه النفس", 10)
        if sid in ("hashemi__s021", "hashemi__s027", "hashemi__s030"):
            return (9, 2, "المستوى الثاني: فقه النفس في القصص القرآني (يوسف والكهف ومريم وطه ولوط)", 3)
        if sid == "hashemi__s035":
            return (10, 2, "المستوى الثاني: فقه السيرة والتربية النفسية في غزوة تبوك", 4)
        if sid in ("hashemi__s036", "hashemi__s045", "hashemi__s046"):
            return (2, 2, "المستوى الثاني: فقه التفكير والعقل وفقه نفس الإلحاد والمدخلات الإعلامية", 9)
        if sid in ("hashemi__s002", "hashemi__s009", "hashemi__s038"):
            return (10, 2, "المستوى الثاني: فقه الإخلاص والعبودية وعمل اليوم والليلة", 1)
        return (1, 2, "المستوى الثاني: أصول فقه النفس الإنسانية والعلاج المعرفي والروحي", 7)

    # --- AYMAN ---
    if sheikh_id == "ayman":
        if sid in ("ayman__s002", "ayman__s003", "ayman__s004", "ayman__s005", "ayman__s009", "ayman__s010", "ayman__s011", "ayman__s028", "ayman__s029"):
            return (1, 1, "المستوى الأول والثاني: تأسيس وعي المسلم المعاصر وخارطة العلوم", 8)
        if sid in ("ayman__s013", "ayman__s014", "ayman__s015", "ayman__s016"):
            return (5, 1, "المستوى الأول: الوعي اللغوي ومدخل علوم العربية والجذور القرآنية", 10)
        if sid == "ayman__s017":
            return (1, 1, "المستوى الأول: مدخل إلى علم النفس", 7)
        if sid == "ayman__s018":
            return (1, 1, "المستوى الأول: دورة البيت المسلم", 6)
        return (10, 1, "المستوى الأول: مدخل دراسة التاريخ والسيرة والخلفاء والدول", 4)

    return (1, 1, "المستوى العام", 12)


LADDER_NAMES = {
    1: "السلم الأول: المدخل المعرفي ومنهجية الطلب وفقه السنن والإصلاح",
    2: "السلم الثاني: العقيدة الإسلامية وعلم الكلام ومناقشة الشبهات",
    3: "السلم الثالث: الفقه المالكي والفقه المقارن والقواعد الفقهية وفقه النوازل",
    4: "السلم الرابع: أصول الفقه ومقاصد الشريعة وتاريخ التشريع",
    5: "السلم الخامس: علوم اللغة العربية — النحو والإعراب",
    6: "السلم السادس: علوم اللغة العربية — الصرف والاشتقاق",
    7: "السلم السابع: علوم اللغة العربية — البلاغة والبيان القرآني والأدب",
    8: "السلم الثامن: علوم الآلة العقلية — المنطق والمقولات والوضع وآداب البحث والمناظرة",
    9: "السلم التاسع: التفسير وعلوم القرآن ومقاصد السور",
    10: "السلم العاشر: الحديث النبوي ومصطلحه والسيرة والتاريخ والتزكية والسلوك",
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
    9: "الفئة التاسعة: دفع الشبهات المعاصرة والتحصين الفكري والعقدي (مادة الرد على الإلحاد والتشدد)",
    10: "الفئة العاشرة: التفسير واللمسات البيانية ومقاصد السور (المنجم القرآني لتحضير الخطب والدروس)",
    11: "الفئة الحادية عشرة: المواسم الإيمانية والدار الآخرة وفقه الدعاء (مادة رمضان والحج ومواعظ الآخرة)",
    12: "الفئة الثانية عشرة: النماذج التطبيقية للخطب المنبرية والفتاوى والتأصيل الفقهي والحديثي (مدرسة الأداء الخطابي والإفتائي)",
}

TIER_NAMES = {
    1: "النظام الأول: النواة التأصيلية الصلبة (السلم الدراسي الإلزامي — متن واحد محكم لكل طبقة في العلوم العشرة)",
    2: "النظام الثاني: الخزانة المرجعية التحقيقية (شروح المقارنة والموسوعات العلمية للرجوع بالباب والمسألة)",
    3: "النظام الثالث: مصنع الإنتاج الوعظي والخطابي المسجدي (المنجم التطبيقي لتحضير الخطب والدروس الأسبوعية)",
}


def clean_arabic_title(text: str) -> str:
    cleaned = (
        text.replace("(Our Traits)", "")
        .replace("(FHD)", "بالجودة العالية")
        .replace(" - مترجم للإنجليزية", "")
        .replace(" (البرنامج الرمضاني - مترجم للإنجليزية)", "")
        .replace("قناة CBC - ", "")
        .replace("CBC", "")
    )
    cleaned = re.sub(r"[A-Za-z]+", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def main():
    data = json.load(open(SELECTED_PATH, encoding="utf-8"))

    tiers = {k: {"id": k, "name": v, "series": [], "lessons_count": 0, "total_hours": 0.0} for k, v in TIER_NAMES.items()}
    ladders = {k: {"id": k, "name": v, "series": [], "lessons_count": 0, "total_hours": 0.0} for k, v in LADDER_NAMES.items()}
    sermon_cats = {k: {"id": k, "name": v, "series": [], "lessons_count": 0, "total_hours": 0.0} for k, v in SERMON_CAT_NAMES.items()}

    for sh in data["sheikhs"]:
        sh_id = sh["sheikh_id"]
        sh_name = sh["sheikh_name"]
        for s in sh["series"]:
            tier_id, tier_name = get_architectural_tier(s["id"], sh_id)
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
                "architectural_tier_id": tier_id,
                "architectural_tier_name": tier_name,
                "level_no": lvl_no,
                "level_name": lvl_name,
                "ladder_id": lid,
                "ladder_name": LADDER_NAMES[lid],
                "sermon_category_id": scat_id,
                "sermon_category_name": SERMON_CAT_NAMES[scat_id],
            }
            tiers[tier_id]["series"].append(entry)
            tiers[tier_id]["lessons_count"] += ac
            tiers[tier_id]["total_hours"] = round(tiers[tier_id]["total_hours"] + hrs, 1)

            ladders[lid]["series"].append(entry)
            ladders[lid]["lessons_count"] += ac
            ladders[lid]["total_hours"] = round(ladders[lid]["total_hours"] + hrs, 1)

            sermon_cats[scat_id]["series"].append(entry)
            sermon_cats[scat_id]["lessons_count"] += ac
            sermon_cats[scat_id]["total_hours"] = round(sermon_cats[scat_id]["total_hours"] + hrs, 1)

    for tid in tiers:
        tiers[tid]["series"].sort(key=lambda x: (x["ladder_id"], x["level_no"], x["sheikh_name"], x["order_in_sheikh"] or 0))
        tiers[tid]["series_count"] = len(tiers[tid]["series"])

    for lid in ladders:
        ladders[lid]["series"].sort(key=lambda x: (x["architectural_tier_id"], x["level_no"], x["sheikh_name"], x["order_in_sheikh"] or 0))
        ladders[lid]["series_count"] = len(ladders[lid]["series"])

    for cid in sermon_cats:
        sermon_cats[cid]["series"].sort(key=lambda x: (x["sheikh_name"], x["order_in_sheikh"] or 0))
        sermon_cats[cid]["series_count"] = len(sermon_cats[cid]["series"])

    out_json = {
        "totals": data["totals"],
        "architectural_tiers": list(tiers.values()),
        "educational_ladders": list(ladders.values()),
        "sermon_categories": list(sermon_cats.values()),
    }
    with open(LADDERS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(out_json, f, ensure_ascii=False, indent=2)

    # Build Master Markdown Guide (Pure Arabic, Zero English, Zero Backticks)
    arch_doc = Path("/tmp/sermon_production_architecture.md").read_text(encoding="utf-8")

    lines = []
    lines.append(arch_doc.strip())
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## القسم السابع: الإحصاء الشامل للنسخة الاحترافية الموسعة (681 سلسلة — 27867 درساً — 18030.9 ساعة)")
    lines.append("")
    lines.append("### أولاً: توزيع الموسوعة المختارة على الأنظمة المعمارية الثلاثة")
    lines.append("")
    lines.append("| رقم النظام | اسم النظام المعماري | عدد السلاسل | عدد الدروس | مجموع الساعات |")
    lines.append("| :---: | :--- | :---: | :---: | :---: |")
    for tid, tobj in tiers.items():
        lines.append(f"| {tid} | {tobj['name']} | {tobj['series_count']} | {tobj['lessons_count']} | {tobj['total_hours']:.1f} |")
    lines.append("")
    lines.append("### ثانياً: جدول خلاصة السلالم التعليمية العشرة الشاملة (النواة + الخزانة + الروافد)")
    lines.append("")
    lines.append("| رقم السلم | اسم السلم التعليمي | عدد السلاسل | عدد الدروس | مجموع الساعات |")
    lines.append("| :---: | :--- | :---: | :---: | :---: |")
    for lid, lobj in ladders.items():
        lines.append(f"| {lid} | {lobj['name']} | {lobj['series_count']} | {lobj['lessons_count']} | {lobj['total_hours']:.1f} |")
    lines.append("")
    lines.append("### ثالثاً: جدول خلاصة فئات إنتاج الدروس الوعظية والخطب المسجدية (12 فئة)")
    lines.append("")
    lines.append("| رقم الفئة | فئة الإنتاج الوعظي والخطابي | عدد السلاسل | عدد الدروس | مجموع الساعات |")
    lines.append("| :---: | :--- | :---: | :---: | :---: |")
    for cid, cobj in sermon_cats.items():
        lines.append(f"| {cid} | {cobj['name']} | {cobj['series_count']} | {cobj['lessons_count']} | {cobj['total_hours']:.1f} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## القسم الثامن: الفهرس التفصيلي الكامل للسلالم التعليمية العشرة (681 سلسلة)")
    lines.append("")
    for lid, lobj in ladders.items():
        lines.append(f"### {lobj['name']} ({lobj['series_count']} سلسلة — {lobj['lessons_count']} درساً — {lobj['total_hours']:.1f} ساعة)")
        lines.append("")
        lines.append("| الترتيب | النظام المعماري | المستوى | الشيخ | رقم السلسلة عند الشيخ | عنوان السلسلة | الدروس | الساعات |")
        lines.append("| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: |")
        for idx, item in enumerate(lobj["series"], 1):
            clean_title = clean_arabic_title(item["title"])
            short_tier = "النواة الإلزامية" if item["architectural_tier_id"] == 1 else ("الخزانة المرجعية" if item["architectural_tier_id"] == 2 else "المصنع الوعظي")
            lines.append(f"| {idx} | {short_tier} | {item['level_name']} | {item['sheikh_name']} | {item['order_in_sheikh']} | {clean_title} | {item['lessons_count']} | {item['hours']:.1f} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## القسم التاسع: الفهرس التفصيلي الكامل لمصفوفة إنتاج الدروس الوعظية والخطب المسجدية (12 فئة)")
    lines.append("")
    for cid, cobj in sermon_cats.items():
        lines.append(f"### {cobj['name']} ({cobj['series_count']} سلسلة — {cobj['lessons_count']} درساً — {cobj['total_hours']:.1f} ساعة)")
        lines.append("")
        lines.append("| الترتيب | الشيخ | رقم السلسلة عند الشيخ | عنوان السلسلة | الدروس | الساعات |")
        lines.append("| :---: | :--- | :---: | :--- | :---: | :---: |")
        for idx, item in enumerate(cobj["series"], 1):
            clean_title = clean_arabic_title(item["title"])
            lines.append(f"| {idx} | {item['sheikh_name']} | {item['order_in_sheikh']} | {clean_title} | {item['lessons_count']} | {item['hours']:.1f} |")
        lines.append("")

    full_md = "\n".join(lines) + "\n"
    LADDERS_MD_PATH.write_text(full_md, encoding="utf-8")

    print("Successfully built cheikh-ladders.json and سلالم_التعليم_ومصفوفة_الخطب.md")
    for tid, tobj in tiers.items():
        print(f"Tier {tid}: {tobj['series_count']:3d} series | {tobj['lessons_count']:5d} lessons | {tobj['total_hours']:7.1f}h | {tobj['name']}")
    print("---")
    for lid, lobj in ladders.items():
        print(f"Ladder {lid:2d}: {lobj['series_count']:3d} series | {lobj['lessons_count']:5d} lessons | {lobj['total_hours']:7.1f}h | {lobj['name']}")
    print("---")
    for cid, cobj in sermon_cats.items():
        print(f"Sermon {cid:2d}: {cobj['series_count']:3d} series | {cobj['lessons_count']:5d} lessons | {cobj['total_hours']:7.1f}h | {cobj['name']}")


if __name__ == "__main__":
    main()
