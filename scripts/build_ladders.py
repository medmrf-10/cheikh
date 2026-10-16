#!/usr/bin/env python3
"""Build Three-Tier Architecture, 11 Linear Educational Ladders, and 12 Sermon Production Categories for all 728 selected series."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELECTED_PATH = ROOT / "cheikh-selected.json"
LADDERS_JSON_PATH = ROOT / "cheikh-ladders.json"
LADDERS_MD_PATH = ROOT / "سلالم_التعليم_ومصفوفة_الخطب.md"

# النظام الأول: المسار التأسيسي والمنهجي الشخصي لطالب العلم (شاملاً الورد اليومي للعربية كاملًا عند العقرباوي والورد اليومي للتزكية عند أصحاب الحال الأربعة)
TIER1_CORE_IDS = {
    # 1. سلم التزكية الشخصية لطالب العلم (أصحاب الحال الأربعة حصراً: البوطي + الحبيب عمر + الحبيب علي الجفري + السريري)
    "bouti__s015",
    "bouti__s033",
    "bouti__s034",
    "bouti__s035",
    "bouti__s025",
    "jifri__s001",
    "jifri__s002",
    "jifri__s005",
    "hafiz__arbain_usul_din",
    "hafiz__qabas_nur_mubin",
    "hafiz__hikam_ataiyah",
    "hafiz__risalat_muawanah",
    "hafiz__mamlakat_qalb",
    "hafiz__khuluquna",
    "hafiz__irshadat_suluk",
    "hafiz__idah_asrar",
    "hafiz__kibrit_ahmar_2",
    "sariri__s040",
    "sariri__s042",
    "sariri__s043",
    # 2. سلم اللغة العربية الكامل (منهج الشيخ علي هاني العقرباوي كاملًا بلا حذف - 37 سلسلة متدرجة حلزونياً)
    "alihani__s001", "alihani__s002", "alihani__s003", "alihani__s004", "alihani__s005", "alihani__s006", "alihani__s007",
    "alihani__s008", "alihani__s009", "alihani__s010", "alihani__s011", "alihani__s012", "alihani__s013", "alihani__s014",
    "alihani__s015", "alihani__s016", "alihani__s017", "alihani__s018", "alihani__s019",
    "alihani__s020", "alihani__s021", "alihani__s022", "alihani__s023", "alihani__s024", "alihani__s025", "alihani__s026", "alihani__s027",
    "alihani__s029", "alihani__s030", "alihani__s031", "alihani__s032", "alihani__s033", "alihani__s034", "alihani__s035", "alihani__s036", "alihani__s037", "alihani__s038",
    # 3. سلم العقيدة الإسلامية وعلم الكلام البرهاني (البردوني + البوطي + العمري)
    "bardoni__s001",
    "bardoni__s003",
    "bardoni__s002",
    "bouti__s022",
    "bouti__s021",
    "omari__s003",
    "bardoni__s004",
    "omari__s001",
    # 4. سلم علوم الآلة العقلية (المنطق والمقولات والوضع والبحث والمناظرة ونظرية المعرفة)
    "omari__s009",
    "omari__s010",
    "omari__s011",
    "bardoni__s014",
    "bardoni__s015",
    "bardoni__s017",
    "bardoni__s016",
    "sariri__s032",
    "omari__s012",
    # 5. سلم الفقه المالكي المتدرج والقواعد الفقهية (الرسالة -> أسهل المسالك -> المنهج المنتخب والصناعة -> خليل والشرح الكبير)
    "bardoni__s006",
    "sariri__s003",
    "bardoni__s007",
    "sariri__s004",
    "sariri__s002",
    "sariri__s001",
    # 6. سلم أصول الفقه وتخريج الفروع على الأصول (منفصل تماماً عن المقاصد — السريري والبردوني)
    "sariri__s017",
    "sariri__s018",
    "sariri__s007",
    "sariri__s008",
    "sariri__s014",
    "sariri__s012",
    "sariri__s013",
    "sariri__s010",
    "sariri__s011",
    "sariri__s009",
    "bardoni__s008",
    "sariri__s015",
    "sariri__s006",
    "sariri__s019",
    # 7. سلم مقاصد الشريعة وفلسفة التشريع (مستقل تماماً عن أصول الفقه — السريري والبوطي)
    "sariri__s022",
    "sariri__s030",
    "sariri__s037",
    "sariri__s044",
    "bouti__s031",
    "sariri__s021",
    # 8. سلم التفسير وعلوم القرآن والبيان القرآني (الأركان الأربعة: العقرباوي + البوطي + السامرائي + الشعراوي)
    "alihani__s048",
    "bouti__s002",
    "alihani__s044",
    "alihani__s039",
    "alihani__s040",
    "alihani__s042",
    "samarrai__s008",
    "samarrai__s004",
    "samarrai__s005",
    "samarrai__s066",
    "bouti__s001",
    "alihani__s045",
    "alihani__s046",
    # 9. سلم علوم الحديث ومصطلحه وعلله
    "asimi__s011",
    "asimi__s012",
    "asimi__s013",
    "sayed__s012",
    "sayed__s014",
    # 10. سلم شروح متون السنة النبوية وفقه الحديث والشمائل
    "dedew__kursi_arbaeen_nawawiya",
    "kamali__s003",
    "hafiz__bulugh_maram",
    "dedew__sharh_taqreeb_asaneed",
    "kamali__s001",
    "kamali__s002",
    "hafiz__muwatta",
    "dedew__mukhtasar_bukhari",
    "dedew__sharh_bukhari",
    # 11. سلم فقه السيرة النبوية والسنن الإلهية وفقه النفس والوعي الحضاري
    "bouti__s030",
    "kamali__s021",
    "bouti__s024",
    "hashemi__s010",
    "ayman__s009",
    "ayman__s010",
}

TIER2_REFERENCE_IDS = {
    # Creed & Kalam & Philosophy
    "asimi__s007", "asimi__s008", "asimi__s009",
    "omari__s002", "omari__s004", "omari__s005", "omari__s013", "omari__s014", "omari__s015", "omari__s016", "omari__s017",
    "bardoni__s019", "bardoni__s020", "bardoni__s021",
    "dedew__sharh_manzouma_adoudiya", "gomaa__s027", "gomaa__s028",
    "sariri__s031", "sariri__s033", "sariri__s034", "sariri__s035", "sariri__s036", "sariri__s038",
    # Parallel Arabic & Literature
    "bardoni__s009", "bardoni__s010", "bardoni__s012", "bardoni__s013",
    "sariri__s024", "sariri__s025", "sariri__s027",
    "dedew__sharh_jazariya", "dedew__sharh_muallaqat_imru_alqais",
    "kamali__s017", "kamali__s018", "kamali__s019", "kamali__s020",
    "ayman__s013", "ayman__s014", "ayman__s015", "ayman__s016",
    "samarrai__s009", "sayed__s058",
    # Parallel Logic
    "asimi__s033", "asimi__s034", "asimi__s035",
    # Parallel Fiqh & Usul & Maqasid
    "sariri__s016", "sariri__s020", "sariri__s041", "sariri__s046", "sariri__s048",
    "alihani__s049", "alihani__s050",
    "dedew__sharh_miftah_wusool", "dedew__sharh_waraqat", "dedew__dawrat_maratib_dalala_kuwait",
    "dedew__madakhil_uloom_manhajiya",
    "asimi__s015", "asimi__s016", "asimi__s017", "asimi__s020", "asimi__s021", "asimi__s022",
    "hawwa__ibadat2_ikhtiyar", "hawwa__ahwal_shakhsiyah_quduri", "hawwa__fiqh_ahadith_ahkam", "hawwa__usool_fiqh_1", "hawwa__usool_ifta_isad_mufti",
    "gomaa__s001", "gomaa__s002", "gomaa__s004", "gomaa__s005", "gomaa__s006", "gomaa__s007", "gomaa__s008", "gomaa__s052", "gomaa__s053", "gomaa__s054", "gomaa__s080", "gomaa__s083", "gomaa__s084",
    "hafiz__fawaid_thaminah", "hafiz__sullam_tawfiq", "hafiz__muqaddimat_majmu", "hafiz__risala_jamia", "hafiz__ahkam_muamalat_hajj",
    "bouti__s042", "bouti__s043", "bouti__s046", "sayed__s016",
    # Parallel Tafsir & Bayan
    "alihani__s043", "alihani__s051", "alihani__s052",
    "asimi__s001", "asimi__s002", "asimi__s003", "asimi__s005",
    "gomaa__s030", "gomaa__s031", "gomaa__s032", "gomaa__s033", "gomaa__s034", "gomaa__s035", "gomaa__s037", "gomaa__s038",
    "hafiz__tafsir_monday", "hafiz__tafsir_ramadan", "hafiz__tafsir_fatiha_qisar",
    "dedew__sharh_ikleel",
    # Parallel Hadith Sciences & Commentaries
    "sayed__s001", "sayed__s002", "sayed__s003", "sayed__s004", "sayed__s005", "sayed__s008", "sayed__s010", "sayed__s011", "sayed__s013", "sayed__s047", "sayed__s050", "sayed__s052", "sayed__s053", "sayed__s083",
    "dedew__sharh_maalim_sunnah",
    "kamali__s006",
    "hafiz__kashf_ghumma", "hafiz__adhkar_nawawi",
    "bouti__s020", "jifri__s007", "gomaa__s019", "gomaa__s022", "gomaa__s024", "gomaa__s025", "gomaa__s026",
    "asimi__s014",
}


def get_architectural_tier(sid: str, sh_id: str) -> tuple[int, str]:
    if sid in TIER1_CORE_IDS:
        return (1, "النظام الأول: النواة المنهجية والورد اليومي لطالب العلم (التدرج الخطي الصارم كتاباً بعد كتاب)")
    if sid in TIER2_REFERENCE_IDS or (sh_id == "shaarawy" and sid <= "shaarawy__s063") or (sh_id == "samarrai"):
        return (2, "النظام الثاني: الخزانة المرجعية التحقيقية والتفسيرية (شروح المقارنة والموسوعات العلمية)")
    return (3, "النظام الثالث: مصنع الإنتاج الوعظي والخطابي المسجدي (المنجم التطبيقي للخطب والدروس)")


def classify_series(s: dict, sheikh_id: str, sheikh_name: str):
    """
    Returns (ladder_id [1..11], level_no [1..6], level_name, sermon_cat_id [1..12])
    Ladders:
      1: سلم التزكية الشخصية لطالب العلم («الحال قبل المقال» — الورد اليومي الثابت)
      2: سلم اللغة العربية الكامل — النحو والصرف والبلاغة والإعراب (الورد اليومي الثابت)
      3: سلم العقيدة الإسلامية وعلم الكلام البرهاني ومناقشة الشبهات
      4: سلم علوم الآلة العقلية — المنطق والمقولات والوضع وآداب البحث ونظرية المعرفة
      5: سلم الفقه المالكي المتدرج والقواعد الفقهية وفقه النوازل
      6: سلم أصول الفقه وتخريج الفروع على الأصول (منفصل تماماً عن المقاصد)
      7: سلم مقاصد الشريعة وفلسفة التشريع وتاريخه (مستقل تماماً عن أصول الفقه)
      8: سلم التفسير وعلوم القرآن والبيان القرآني (العقرباوي + البوطي + السامرائي + الشعراوي)
      9: سلم علوم الحديث ومصطلحه وعلله والجرح والتعديل
      10: سلم متون السنة النبوية وفقه الحديث المقارن والشمائل
      11: سلم فقه السيرة النبوية والسنن الإلهية وفقه النفس والوعي الحضاري
    """
    sid = s["id"]
    num = s.get("order_no") or 1

    # --- ALIHANI ---
    if sheikh_id == "alihani":
        if sid in ("alihani__s001", "alihani__s002", "alihani__s020", "alihani__s021", "alihani__s003", "alihani__s004", "alihani__s005", "alihani__s022", "alihani__s006", "alihani__s007"):
            return (2, 1, "المرحلة الأولى: التأسيس المتدرج في النحو والصرف وإعراب جزء عم (الخطوات ١ إلى ١٠)", 10)
        if sid in ("alihani__s023", "alihani__s008", "alihani__s009", "alihani__s024", "alihani__s025", "alihani__s010", "alihani__s011", "alihani__s012", "alihani__s013", "alihani__s026", "alihani__s029", "alihani__s030", "alihani__s031", "alihani__s032"):
            return (2, 2, "المرحلة الثانية: التمكين المتوسط في القطر وموصل الطلاب والعزي وتأسيس البلاغة (الخطوات ١١ إلى ٢٤)", 10)
        if sid in ("alihani__s027", "alihani__s033", "alihani__s034", "alihani__s014", "alihani__s017", "alihani__s015", "alihani__s016", "alihani__s035", "alihani__s036", "alihani__s037", "alihani__s018", "alihani__s038", "alihani__s019"):
            return (2, 3, "المرحلة الثالثة: التحقيق العالي في شروح الألفية الأربعة والتسهيل والدر المصون (الخطوات ٢٥ إلى ٣٧)", 10)
        if sid in ("alihani__s048", "alihani__s044", "alihani__s039", "alihani__s040", "alihani__s042"):
            return (8, 1, "المرحلة الأولى: آداب التلقي وعلوم القرآن وقانون التفسير ومقاصد السور", 10)
        if sid in ("alihani__s043", "alihani__s051", "alihani__s052"):
            return (8, 2, "المرحلة الثانية: اللطائف البيانية والمناسبات القرآنية", 10)
        if sid in ("alihani__s045", "alihani__s046"):
            return (8, 4, "المرحلة الرابعة: ذروة الصناعة التفسيرية التحقيقية (شرح مدارك التنزيل للنسفي)", 10)
        if sid in ("alihani__s049", "alihani__s050"):
            return (5, 1, "المرحلة التأسيسية: فقه العبادات والمواريث", 12)

    # --- BARDONI ---
    if sheikh_id == "bardoni":
        if sid in ("bardoni__s001", "bardoni__s003"):
            return (3, 1, "المستوى الأول: التأسيس الأولي (مقدمات السنوسي ومنظومة الأجهوري)", 2)
        if sid == "bardoni__s002":
            return (3, 2, "المستوى الثاني: المتون المتوسطة (شرح أم البراهين للسنوسي)", 2)
        if sid in ("bardoni__s004", "bardoni__s019", "bardoni__s020", "bardoni__s021"):
            return (3, 3, "المستوى الثالث: التحقيق الكلامي المتقدم (حواشي اليوسي على الكبرى والمناظرات)", 9)
        if sid == "bardoni__s006":
            return (5, 3, "الدرجة الثالثة في الفقه المالكي: شرح رسالة ابن أبي زيد القيرواني", 12)
        if sid == "bardoni__s007":
            return (5, 5, "الدرجة الخامسة في الفقه المالكي: القواعد الفقهية (شرح المنهج المنتخب للزقاق)", 12)
        if sid == "bardoni__s008":
            return (6, 2, "المرحلة الثانية في أصول الفقه: شرح مراقي السعود للشنقيطي", 12)
        if sid in ("bardoni__s009", "bardoni__s010", "bardoni__s012", "bardoni__s013"):
            return (2, 3, "الخزانة المرجعية المغربية في الألفية والأشموني والجوهر المكنون ونظم الاستعارة", 10)
        if sid in ("bardoni__s014", "bardoni__s015", "bardoni__s016", "bardoni__s017"):
            return (4, 2, "المرحلة الثانية والثالثة: حاشية البناني على السلم والمقولات والوضع والمناظرة", 9)

    # --- SARIRI ---
    if sheikh_id == "sariri":
        if sid == "sariri__s003":
            return (5, 4, "الدرجة الرابعة في الفقه المالكي: شرح نظم أسهل المسالك لمحمد البشار", 12)
        if sid == "sariri__s004":
            return (5, 5, "الدرجة الخامسة في الفقه المالكي: سلسلة الصناعة الفقهية وبناء الملكة", 12)
        if sid in ("sariri__s001", "sariri__s002"):
            return (5, 6, "الدرجة السادسة (الذروة): شرح مختصر خليل والشرح الكبير للدردير", 12)
        if sid in ("sariri__s041", "sariri__s046", "sariri__s048"):
            return (5, 5, "التطبيقات الفقهية والإفتائية وفقه الأسرة", 12)
        if sid in ("sariri__s017", "sariri__s018", "sariri__s007", "sariri__s008", "sariri__s014", "sariri__s012", "sariri__s013"):
            return (6, 1, "المرحلة الأولى في أصول الفقه: المداخل التصورية والورقات وإيصال السالك والضروري لابن رشد", 12)
        if sid in ("sariri__s010", "sariri__s011", "sariri__s009", "sariri__s015", "sariri__s016"):
            return (6, 2, "المرحلة الثانية في أصول الفقه: مفتاح الوصول للتلمساني ونيل السول ونشر البنود على مراقي السعود", 12)
        if sid in ("sariri__s006", "sariri__s019", "sariri__s020"):
            return (6, 3, "المرحلة الثالثة في أصول الفقه: شرح جمع الجوامع للسبكي والإحكام للآمدي", 12)
        if sid in ("sariri__s021", "sariri__s022", "sariri__s030", "sariri__s037", "sariri__s044"):
            return (7, 1, "سلم مقاصد الشريعة وفلسفة التشريع: العقيدة الفقهية ومحاورة المقاصديين والموافقات للشاطبي", 8)
        if sid == "sariri__s023":
            return (10, 2, "الدرجة الثانية في متون السنة: شرح إحكام الأحكام شرح عمدة الأحكام لابن دقيق العيد", 12)
        if sid in ("sariri__s040", "sariri__s042", "sariri__s043"):
            return (1, 2, "المرحلة الثانية في التزكية الشخصية: صدق الشعور ومحاسبة الفكر قبل السلوك والأحوال جوهر الأعمال", 1)
        if sid == "sariri__s032":
            return (4, 3, "المرحلة الثالثة في آلة النظر: عقيدتنا في المعرفة البشرية", 9)
        if sid in ("sariri__s024", "sariri__s025", "sariri__s027"):
            return (2, 3, "الخزانة الأدبية والصرفية: الصرف الصغير ومقامات الحريري والكامل للمبرد", 10)
        if sid in ("sariri__s031", "sariri__s033", "sariri__s034", "sariri__s035", "sariri__s036", "sariri__s038", "sariri__s039"):
            return (3, 3, "المستوى الثالث في العقيدة والفكر: نقض العلمانية والتنوير وأحوال الآخرة", 9)

    # --- BOUTI ---
    if sheikh_id == "bouti":
        if sid in ("bouti__s015", "bouti__s033", "bouti__s034", "bouti__s035", "bouti__s025"):
            return (1, 1, "سلم التزكية الشخصية عند أصحاب الحال: التزكية في القرآن والحكم العطائية وفي سبيل التزكية", 1)
        if sid == "bouti__s022":
            return (3, 1, "المستوى الأول في العقيدة: دورة مختصرة في العقيدة الإسلامية", 2)
        if sid == "bouti__s021":
            return (3, 2, "المستوى الثاني في العقيدة: شرح كتاب كبرى اليقينيات الكونية", 2)
        if sid in ("bouti__s023", "bouti__s026", "bouti__s027", "bouti__s028", "bouti__s062"):
            return (3, 3, "المستوى الثالث في العقيدة والفكر: يغالطونك إذ يقولون والإسلام في ميزان العلم والمناظرات", 9)
        if sid in ("bouti__s031", "bouti__s042", "bouti__s043", "bouti__s046"):
            return (7, 2, "سلم مقاصد الشريعة وفلسفة التشريع: محاضرات في تاريخ التشريع وضوابط المصلحة", 8)
        if sid == "bouti__s002":
            return (8, 1, "المرحلة الأولى في علوم القرآن: من روائع القرآن الكريم ودراسات قرآنية", 10)
        if sid in ("bouti__s003", "bouti__s004", "bouti__s005", "bouti__s006", "bouti__s007", "bouti__s008", "bouti__s009", "bouti__s010", "bouti__s011", "bouti__s012", "bouti__s013", "bouti__s014", "bouti__s016", "bouti__s018"):
            return (8, 2, "المرحلة الثانية في التفسير الموضوعي وإعجاز القرآن الكريم", 10)
        if sid == "bouti__s001":
            return (8, 3, "المرحلة الثالثة في التفسير: التفسير التحليلي التربوي للقرآن الكريم", 10)
        if sid == "bouti__s020":
            return (10, 1, "الدرجة الأولى في متون السنة الجامعة: شرح رياض الصالحين للإمام النووي", 5)
        if sid in ("bouti__s024", "bouti__s030", "bouti__s036", "bouti__s047", "bouti__s049"):
            return (11, 1, "سلم فقه السيرة النبوية والسنن الإلهية والتربية", 4)
        return (11, 3, "المصنع المنبري التطبيقي: خطب الجمعة للعلامة البوطي", 12)

    # --- HAFIZ ---
    if sheikh_id == "hafiz":
        if sid in ("hafiz__arbain_usul_din", "hafiz__qabas_nur_mubin", "hafiz__hikam_ataiyah", "hafiz__risalat_muawanah", "hafiz__mamlakat_qalb", "hafiz__khuluquna", "hafiz__irshadat_suluk", "hafiz__idah_asrar", "hafiz__kibrit_ahmar_2", "hafiz__mukatabat", "hafiz__ihya_ulum_din", "hafiz__minhaj_abidin", "hafiz__bidayat_hidayah", "hafiz__ayyuha_walad", "hafiz__nasaih_diniyah", "hafiz__fusul_ilmiyah", "hafiz__daawat_tammah", "hafiz__sabil_iddikhar", "hafiz__adab_suluk_murid"):
            return (1, 1, "سلم التزكية الشخصية عند أصحاب الحال: مملكة القلب والمعاونة وقبس النور المبين والحكم وإيضاح الأسرار", 1)
        if sid in ("hafiz__muwatta", "hafiz__kashf_ghumma", "hafiz__bulugh_maram", "hafiz__adhkar_nawawi"):
            return (10, 4, "الدرجة الثالثة والرابعة في متون السنة: مجالس موطأ الإمام مالك وكشف الغمة وبلوغ المرام والأذكار", 12)
        if sid in ("hafiz__tafsir_monday", "hafiz__tafsir_ramadan", "hafiz__tafsir_fatiha_qisar", "hafiz__qasas_haqq"):
            return (8, 3, "الخزانة التفسيرية التدبرية والقصص القرآني", 10)
        if sid in ("hafiz__sullam_tawfiq", "hafiz__sifat_salat_muqarrabin", "hafiz__fawaid_thaminah", "hafiz__risala_jamia", "hafiz__ahkam_muamalat_hajj", "hafiz__muqaddimat_majmu"):
            return (5, 2, "الخزانة الفقهية المقارنة وأسرار العبادات", 11)
        return (11, 2, "سلم السيرة النبوية والشمائل وآداب العالم والمتعلم", 4)

    # --- JIFRI ---
    if sheikh_id == "jifri":
        if sid in ("jifri__s001", "jifri__s002", "jifri__s005", "jifri__s006", "jifri__s008", "jifri__s009", "jifri__s010", "jifri__s011", "jifri__s012", "jifri__s014", "jifri__s015", "jifri__s016"):
            return (1, 1, "سلم التزكية الشخصية عند أصحاب الحال: مجالس قبس النور المبين وأيها المريد والحكم العطائية", 1)
        if sid == "jifri__s007":
            return (10, 5, "الدرجة الخامسة في متون السنة: مجالس صحيح البخاري", 11)
        if sid in ("jifri__s018", "jifri__s019", "jifri__s020", "jifri__s023", "jifri__s028"):
            return (3, 2, "تثبيت اليقين ومعالجة الشك والإلحاد", 9)
        return (11, 2, "الأخلاق المحمدية وفقه الأسرة والحوار المعرفي", 5)

    # --- SAMARRAI ---
    if sheikh_id == "samarrai":
        if sid == "samarrai__s003":
            return (3, 2, "براهين النبوة من الإعجاز البياني", 9)
        if sid == "samarrai__s009":
            return (2, 3, "مميزات العربية ومعاني النحو", 10)
        if sid in ("samarrai__s001", "samarrai__s004", "samarrai__s005", "samarrai__s006", "samarrai__s007", "samarrai__s008", "samarrai__s010", "samarrai__s011", "samarrai__s066"):
            return (8, 2, "المرحلة الثانية في التفسير البياني: أسرار البيان وتناسب الفواتح والخواتيم وموسوعة الفروق اللغوية", 10)
        return (8, 3, "المرحلة الثالثة في التفسير البياني: اللمسات البيانية التحليلية في سور القرآن الكريم", 10)

    # --- SHAARAWY ---
    if sheikh_id == "shaarawy":
        if sid in ("shaarawy__s060", "shaarawy__s061", "shaarawy__s062", "shaarawy__s063"):
            return (8, 3, "المرحلة الثالثة في التفسير: مقدمات التفسير والفاتحة وجزء عم وإعجاز القرآن للإمام الشعراوي", 10)
        if sid in ("shaarawy__s086", "shaarawy__s087"):
            return (8, 2, "المرحلة الثانية: موسوعة قصص الأنبياء والقصص القرآني للإمام الشعراوي", 3)
        if sid in ("shaarawy__s088", "shaarawy__s090"):
            return (11, 1, "السيرة النبوية ووصايا الرسول صلى الله عليه وسلم", 4)
        if sid == "shaarawy__s094":
            return (5, 2, "فقه ومقاصد الحج وخطب عرفة", 11)
        if sid in ("shaarawy__s089", "shaarawy__s091", "shaarawy__s092", "shaarawy__s097", "shaarawy__s098", "shaarawy__s100"):
            return (11, 3, "الخواطر الإيمانية والفتاوى وعلاج الكبائر", 1)
        return (8, 3, "المرحلة الثالثة في التفسير: خواطر الإمام الشعراوي في سور القرآن الكريم (من البقرة إلى الممتحنة)", 10)

    # --- OMARI ---
    if sheikh_id == "omari":
        if sid in ("omari__s009", "omari__s010", "omari__s011", "omari__s012"):
            return (4, 1, "المرحلة الأولى والثانية في آلة النظر: إيضاح المبهم على السلم وإيساغوجي ومعيار العلم", 9)
        if sid in ("omari__s002", "omari__s003", "omari__s004", "omari__s005"):
            return (3, 2, "المستوى الثاني والثالث في الكلام: مقدمة العقائد النسفية وأم البراهين واعتقاد القشيرية", 2)
        if sid == "omari__s001":
            return (3, 3, "المستوى الثالث في الكلام: شرح الاقتصاد في الاعتقاد لحجة الإسلام الغزالي", 2)
        return (3, 3, "المستوى الخامس في الكلام الجديد: نقد الفلسفة الحديثة وفلسفة الدين", 9)

    # --- KAMALI ---
    if sheikh_id == "kamali":
        if sid in ("kamali__s001", "kamali__s002", "kamali__s003", "kamali__s006"):
            return (10, 4, "الدرجة الأولى والرابعة في متون السنة: مجالس موطأ الإمام مالك والأربعين للمنذري", 12)
        if sid in ("kamali__s004", "kamali__s005", "kamali__s029"):
            return (5, 3, "الدرجة الثالثة في الفقه المالكي: شرح رسالة ابن أبي زيد القيرواني ومباحث الفقه المالكي", 12)
        if sid in ("kamali__s007", "kamali__s008", "kamali__s009", "kamali__s010", "kamali__s011", "kamali__s012", "kamali__s013", "kamali__s015"):
            return (8, 3, "التفسير التحليلي والوعظي والأدبي للسور", 10)
        if sid in ("kamali__s017", "kamali__s018", "kamali__s019", "kamali__s020"):
            return (2, 3, "الخزانة الأدبية والحكمية: لامية العرب وتائية الألبيري ولامية ابن الوردي وعنوان الحكم", 5)
        return (11, 1, "سيرة الحبيب صلى الله عليه وسلم وشمائله وسيرة الإمام مالك والصحابة", 4)

    # --- DEDEW ---
    if sheikh_id == "dedew":
        if sid == "dedew__sharh_ibn_ashir":
            return (5, 2, "الدرجة الثانية في الفقه المالكي: شرح نظم ابن عاشر (المرشد المعين)", 12)
        if sid in ("dedew__dawrat_tahara_salah", "dedew__fiqh_muamalat", "dedew__dawrat_faraid", "dedew__ahkam_siyam_series", "dedew__dawrat_sinaat_fatwa_nawazil"):
            return (5, 5, "دورات فقه العبادات والمعاملات والفرائض وصناعة الفتوى عند المالكية", 12)
        if sid in ("dedew__sharh_waraqat", "dedew__sharh_miftah_wusool", "dedew__dawrat_maratib_dalala_kuwait"):
            return (6, 2, "الخزانة الشنقيطية في أصول الفقه: الورقات ومفتاح الوصول ومراتب الدلالة", 12)
        if sid == "dedew__sharh_muwafaqat":
            return (7, 3, "سلم مقاصد الشريعة: مجالس شرح الموافقات للشاطبي", 8)
        if sid in ("dedew__sharh_ikleel", "dedew__sharh_jazariya", "dedew__majalis_qiyam_ramadan_full", "dedew__barnamaj_qissat_nuh", "dedew__barnamaj_abu_bashariya_adam", "dedew__barnamaj_ahsan_alqasas"):
            return (8, 3, "علوم الأداء القرآني واستنباط التنزيل (الإكليل للسيوطي) والقصص القرآني", 10)
        if sid in ("dedew__mukhtasar_bukhari", "dedew__sharh_bukhari", "dedew__sharh_maalim_sunnah", "dedew__sharh_taqreeb_asaneed", "dedew__kursi_arbaeen_nawawiya", "dedew__sharh_umdat_ahkam", "dedew__ahadith_fitan_malihim"):
            return (10, 3, "سلم متون السنة النبوية: تقريب الأسانيد وعمدة الأحكام والأربعين وصحيح البخاري ومعالم السنة", 12)
        if sid == "dedew__sharh_manzouma_adoudiya":
            return (3, 1, "المنظومة العدودية في العقيدة", 2)
        if sid == "dedew__sharh_muallaqat_imru_alqais":
            return (2, 3, "الأدب العربي القديم والشواهد اللغوية", 10)
        return (11, 2, "مداخل العلوم الشرعية والسيرة النبوية والآداب الشرعية وفقه الأمة", 8)

    # --- ASIMI ---
    if sheikh_id == "asimi":
        if sid in ("asimi__s011", "asimi__s012", "asimi__s013"):
            return (9, 1, "سلم علوم الحديث ومصطلحه: المنظومة البيقونية وتيسير علوم الحديث ونزهة النظر لابن حجر", 12)
        if sid in ("asimi__s001", "asimi__s002", "asimi__s003", "asimi__s005", "asimi__s006"):
            return (8, 2, "التفسير التحليلي والتدبر القرآني وسلسلة القصص القرآني الكاملة", 3)
        if sid in ("asimi__s007", "asimi__s008", "asimi__s009", "asimi__s010", "asimi__s045", "asimi__s048"):
            return (3, 1, "الخزانة العقدية التأسيسية وفقه أسماء الله الحسنى والدار الآخرة", 2)
        if sid in ("asimi__s015", "asimi__s016", "asimi__s017"):
            return (5, 3, "الخزانة الفقهية المقارنة (نور الإيضاح والقدوري واللباب)", 12)
        if sid in ("asimi__s020", "asimi__s021", "asimi__s022"):
            return (6, 1, "الخزانة الأصولية التأسيسية (مبادئ الأصول والخلاصة وأصول الشاشي)", 12)
        if sid in ("asimi__s033", "asimi__s034", "asimi__s035"):
            return (4, 1, "الخزانة المنطقية التأسيسية (السلم والمفتاح وإيساغوجي)", 9)
        return (11, 2, "السيرة النبوية وتراجم الأئمة الأعلام والرقائق والخطب المنبرية", 4)

    # --- HAWWA ---
    if sheikh_id == "hawwa":
        if sid == "hawwa__asma_allah_husna":
            return (3, 1, "فقه أسماء الله الحسنى", 2)
        if sid in ("hawwa__ibadat2_ikhtiyar", "hawwa__ahwal_shakhsiyah_quduri", "hawwa__fiqh_ahadith_ahkam", "hawwa__islah_iqtisadi"):
            return (5, 3, "الخزانة الفقهية المقارنة وفقه أحاديث الأحكام والإصلاح المالي", 12)
        if sid in ("hawwa__usool_fiqh_1", "hawwa__usool_ifta_isad_mufti"):
            return (6, 2, "أصول الفقه وأصول الإفتاء ورسم المفتي", 12)
        return (11, 1, "آداب طالب العلم والشمائل النبوية وفقه الأسرة والرقائق المسجدية", 6)

    # --- GOMAA ---
    if sheikh_id == "gomaa":
        if sid in ("gomaa__s001", "gomaa__s002", "gomaa__s004", "gomaa__s052", "gomaa__s053", "gomaa__s054"):
            return (5, 5, "الخزانة الفقهية المقارنة والقواعد الفقهية والأشباه والنظائر", 12)
        if sid in ("gomaa__s005", "gomaa__s006", "gomaa__s007", "gomaa__s008"):
            return (6, 2, "الخزانة الأصولية المقارنة وتخريج الفروع على الأصول والرسالة للشافعي", 12)
        if sid == "gomaa__s080":
            return (7, 2, "تاريخ التشريع الإسلامي وفلسفته", 8)
        if sid in ("gomaa__s019", "gomaa__s022", "gomaa__s024", "gomaa__s025", "gomaa__s026"):
            return (10, 5, "شروح الشفا بتعريف حقوق المصطفى والأربعين النووية والبخاري ومسند أحمد", 4)
        if sid in ("gomaa__s027", "gomaa__s028", "gomaa__s066", "gomaa__s039", "gomaa__s040", "gomaa__s041", "gomaa__s042", "gomaa__s047", "gomaa__s049", "gomaa__s050", "gomaa__s055"):
            return (3, 1, "الخريدة البهية وعقيدة العوام والحوار الشبابي وتفنيد التشدد والشبهات", 9)
        if sid in ("gomaa__s030", "gomaa__s031", "gomaa__s032", "gomaa__s033", "gomaa__s034", "gomaa__s035", "gomaa__s037", "gomaa__s038"):
            return (8, 2, "مقدمة التفسير وتفسير السور من الفاتحة إلى المائدة", 10)
        return (11, 2, "النموذج المعرفي الإسلامي والسيرة النبوية والرقائق والفتاوى", 8)

    # --- SAYED ---
    if sheikh_id == "sayed":
        if sid in ("sayed__s008", "sayed__s010", "sayed__s011", "sayed__s012", "sayed__s013", "sayed__s014", "sayed__s047", "sayed__s050", "sayed__s052", "sayed__s053"):
            return (9, 2, "مداخل علوم الحديث والعلل ومناهج المحدثين وحجية السنة", 9)
        if sid in ("sayed__s001", "sayed__s002", "sayed__s003", "sayed__s004", "sayed__s005", "sayed__s083"):
            return (10, 1, "حفظ وفهم السنة النبوية والجمع بين الصحيحين", 5)
        if sid == "sayed__s058":
            return (2, 3, "تنمية القوة البيانية (دلائل الإعجاز للجرجاني أنموذجاً)", 10)
        if sid in ("sayed__s021", "sayed__s022", "sayed__s023", "sayed__s024", "sayed__s025", "sayed__s026", "sayed__s027", "sayed__s028", "sayed__s029", "sayed__s030", "sayed__s031", "sayed__s032", "sayed__s033", "sayed__s088"):
            return (8, 2, "مقاصد السور والقصص القرآني والتدبر المنهجي", 3)
        if sid in ("sayed__s054", "sayed__s074", "sayed__s075", "sayed__s076", "sayed__s077", "sayed__s078", "sayed__s079", "sayed__s081"):
            return (3, 2, "صناعة المحاور ومعالجة الشبهات الفكرية", 9)
        return (11, 2, "فقه السيرة والسنن الإلهية وبناء الجيل الصاعد", 6)

    # --- HASHEMI ---
    if sheikh_id == "hashemi":
        if sid in ("hashemi__s017", "hashemi__s018", "hashemi__s019", "hashemi__s021", "hashemi__s022", "hashemi__s027", "hashemi__s030"):
            return (8, 2, "المجالس الرمضانية القرآنية وفقه النفس في القصص القرآني", 7)
        if sid in ("hashemi__s036", "hashemi__s045", "hashemi__s046"):
            return (3, 2, "فقه التفكير والعقل وفقه نفس الإلحاد والمدخلات الإعلامية", 9)
        return (11, 2, "فقه النفس الإنسانية وألف باء التربية والعلاج المعرفي والروحي", 7)

    # --- AYMAN ---
    if sheikh_id == "ayman":
        if sid in ("ayman__s013", "ayman__s014", "ayman__s015", "ayman__s016"):
            return (2, 1, "الوعي اللغوي ومدخل علوم العربية", 10)
        return (11, 1, "تأسيس وعي المسلم المعاصر وخارطة العلوم والتاريخ والبيت المسلم", 8)

    return (11, 1, "المستوى العام", 12)


LADDER_NAMES = {
    1: "السلم الأول: التزكية الشخصية لطالب العلم («الحال قبل المقال» — الورد اليومي الثابت عند أصحاب الحال الأربعة: البوطي والحبيب عمر والحبيب علي الجفري والسريري)",
    2: "السلم الثاني: اللغة العربية الكامل — النحو والصرف والبلاغة والإعراب القرآني (الورد اليومي الثابت — منهج الشيخ علي هاني العقرباوي كاملاً متوجاً بشيخ البلاغيين محمد محمد أبو موسى)",
    3: "السلم الثالث: العقيدة الإسلامية وعلم الكلام البرهاني ومناقشة الشبهات (البردوني + البوطي + سعيد فودة + العمري + السريري)",
    4: "السلم الرابع: علوم الآلة العقلية — المنطق والمقولات والوضع وآداب البحث والمناظرة ونظرية المعرفة (البردوني + سعيد فودة + العمري + السريري)",
    5: "السلم الخامس: الفقه المالكي المتدرج والقواعد الفقهية وفقه النوازل (الأخضري ثم ابن عاشر ثم الرسالة ثم أسهل المسالك ثم المنهج المنتخب والصناعة ثم مختصر خليل والشرح الكبير)",
    6: "السلم السادس: أصول الفقه وتخريج الفروع على الأصول (منفصل تماماً عن المقاصد — السريري + البردوني)",
    7: "السلم السابع: مقاصد الشريعة وفلسفة التشريع وتاريخه (مستقل تماماً عن أصول الفقه — السريري + البوطي)",
    8: "السلم الثامن: التفسير وعلوم القرآن والبيان القرآني (الأركان الأربعة متكاملة: العقرباوي + البوطي + السامرائي + الشعراوي + كرسي ابن عطية للبحياوي)",
    9: "السلم التاسع: علوم الحديث ومصطلحه وعلله والجرح والتعديل (أحمد معبد عبد الكريم + نور الدين عتر + محمد عوامة + عبد الفتاح أبو غدة + العاسمي)",
    10: "السلم العاشر: متون السنة النبوية وفقه الحديث المقارن والشمائل (الكملي + البحياوي + الحبيب عمر + السريري + الددو + البوطي + المطيعي + سعد جاويش + الفاسي الفهري)",
    11: "السلم الحادي عشر: فقه السيرة النبوية والسنن الإلهية وفقه النفس والوعي الحضاري (البوطي + الكملي + العاسمي + الهاشمي + أيمن عبد الرحيم + أحمد السيد)",
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
    1: "النظام الأول: النواة المنهجية والورد اليومي لطالب العلم (التدرج الخطي الصارم كتاباً بعد كتاب في العلوم الإلزامية والتزكية الشخصية والعربية الكاملة)",
    2: "النظام الثاني: الخزانة المرجعية التحقيقية والتفسيرية (شروح المقارنة والموسوعات العلمية والتفسيرية للرجوع بالباب والسورة والمسألة)",
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

    print("Successfully built cheikh-ladders.json")
    for tid, tobj in tiers.items():
        print(f"Tier {tid}: {tobj['series_count']:3d} series | {tobj['lessons_count']:5d} lessons | {tobj['total_hours']:7.1f}h | {tobj['name']}")
    print("---")
    for lid, lobj in ladders.items():
        print(f"Ladder {lid:2d}: {lobj['series_count']:3d} series | {lobj['lessons_count']:5d} lessons | {lobj['total_hours']:7.1f}h | {lobj['name']}")


if __name__ == "__main__":
    main()
