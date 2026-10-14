PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS series;
DROP TABLE IF EXISTS channels;
DROP TABLE IF EXISTS sheikhs;

-- 1. جدول المشايخ (الـ 16 المعتمدين)
CREATE TABLE sheikhs (
    id TEXT PRIMARY KEY,
    order_no INTEGER NOT NULL,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    photo TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 2. جدول قنوات يوتيوب المرتبطة بالمشايخ (الترتيب حسب الأهمية priority: 1 = الأهم)
CREATE TABLE channels (
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

CREATE INDEX idx_channels_sheikh ON channels(sheikh_id, priority);

-- 3. جدول السلاسل (لكل شيخ قائمة سلاسل)
-- state:
--   'completed' : أتمّ الشيخ شرحها بالكامل
--   'ongoing'   : مستمرة (الشيخ يشرح فيها حالياً)
--   'stopped'   : متوقفة (توقف الشيخ عنها قديماً أو توفي قبل إتمام الكتاب)
CREATE TABLE series (
    id TEXT PRIMARY KEY,
    sheikh_id TEXT NOT NULL REFERENCES sheikhs(id) ON DELETE CASCADE,
    channel_id TEXT REFERENCES channels(id) ON DELETE SET NULL,
    order_no INTEGER NOT NULL DEFAULT 1,
    title TEXT NOT NULL,
    yt_playlist_id TEXT,
    yt_playlist_url TEXT,
    state TEXT NOT NULL DEFAULT 'completed' CHECK (state IN ('completed', 'ongoing', 'stopped')),
    expected_count INTEGER,
    note TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_series_sheikh ON series(sheikh_id, order_no);
CREATE INDEX idx_series_channel ON series(channel_id);

-- 4. جدول الدروس (لكل سلسلة قائمة دروس مرتبة برقم وعنوان ورابط)
CREATE TABLE lessons (
    id TEXT PRIMARY KEY,
    series_id TEXT NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    sheikh_id TEXT NOT NULL REFERENCES sheikhs(id) ON DELETE CASCADE,
    order_no INTEGER NOT NULL,
    title TEXT NOT NULL,
    yt_id TEXT,
    yt_title TEXT,
    yt_url TEXT,
    duration INTEGER,
    has_transcript INTEGER NOT NULL DEFAULT 0,
    has_summary INTEGER NOT NULL DEFAULT 0,
    has_questions INTEGER NOT NULL DEFAULT 0,
    has_challenges INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(series_id, order_no)
);

CREATE INDEX idx_lessons_series ON lessons(series_id, order_no);
CREATE INDEX idx_lessons_sheikh ON lessons(sheikh_id);
CREATE INDEX idx_lessons_yt ON lessons(yt_id);

-- 5. إدخال المشايخ الـ 16 المعتمدين
INSERT INTO sheikhs (id, order_no, name, short_name) VALUES
    ('sayed',    1,  'أحمد السيد',             'أحمد السيد'),
    ('asimi',    2,  'أدهم العاسمي',           'العاسمي'),
    ('bardoni',  3,  'محمد البردوني الحسيمي',  'البردوني'),
    ('jifri',    4,  'الحبيب علي الجفري',      'الجفري'),
    ('hafiz',    5,  'الحبيب عمر بن حفيظ',     'ابن حفيظ'),
    ('gomaa',    6,  'علي جمعة',               'علي جمعة'),
    ('bouti',    7,  'محمد سعيد رمضان البوطي', 'البوطي'),
    ('shaarawy', 8,  'محمد متولي الشعراوي',    'الشعراوي'),
    ('hawwa',    9,  'معاذ سعيد حوى',          'معاذ حوى'),
    ('sariri',   10, 'مولود السريري',          'السريري'),
    ('omari',    11, 'علي محمود العمري',       'العمري'),
    ('hashemi',  12, 'ذاكر الهاشمي',           'ذاكر الهاشمي'),
    ('kamali',   13, 'سعيد الكملي',            'الكملي'),
    ('samarrai', 14, 'فاضل السامرائي',         'السامرائي'),
    ('ayman',    15, 'أيمن عبد الرحيم',        'أيمن عبد الرحيم'),
    ('dedew',    16, 'محمد الحسن الددو',       'الددو'),
    ('alihani',  17, 'علي هاني العقرباوي',     'علي هاني');

-- 6. إدخال القنوات المعتمدة للمشايخ (البردوني والسريري يشتركان في قناة مدرسة تنكرت كقناة أولى أهم من الشخصية)
INSERT INTO channels (id, sheikh_id, priority, yt_channel_id, title, handle, url, note) VALUES
    ('sayed-main',      'sayed',    1, 'UC7AbKZa30XPMInZIsViiBOQ', 'أحمد السيد',                                        '@alsayyed_ah',                'https://www.youtube.com/@alsayyed_ah',                          NULL),
    ('asimi-main',      'asimi',    1, 'UCVD3hjykftErHKRXrQ8rozA', 'الشيخ أدهم العاسمي',                                '@adhmasmi2',                  'https://www.youtube.com/@adhmasmi2',                            'القناة الثانية بعد سرقة الأولى'),
    ('bardoni-shared',  'bardoni',  1, 'UCikKBeXeC90S8NJsoXLr9Ng', 'مدرسة تنكرت العتيقة (مشتركة مع السريري)',           '@مدرسةتنكرتالعتيقة',          'https://www.youtube.com/channel/UCikKBeXeC90S8NJsoXLr9Ng',      'القناة المشتركة الأهم'),
    ('bardoni-personal','bardoni',  2, 'UCZTyYgGeVgGASTQ3cLKVRxw', 'الشيخ محمد البردوني (القناة الشخصية)',              '@Shaykh_Mohammed_AlBardouni', 'https://www.youtube.com/@Shaykh_Mohammed_AlBardouni',           'القناة الشخصية'),
    ('jifri-main',      'jifri',    1, 'UC9AGtdHF1KIrx_ql9INA8cg', 'Habib Ali Aljifri',                                 '@Alhabibali',                 'https://www.youtube.com/user/alhabibalitv',                     NULL),
    ('hafiz-main',      'hafiz',    1, 'UCg4WWlji1lydn6Op8m7tWkw', 'الحبيب عمر بن حفيظ',                                '@HabibOmarCom',               'https://www.youtube.com/@HabibOmarCom',                         NULL),
    ('gomaa-main',      'gomaa',    1, 'UC_Ki0lMY7HUOSKVTAEd3WLA', 'أ.د علي جمعة Dr Ali Gomaa',                         '@DrAliGomaa',                 'https://www.youtube.com/@DrAliGomaa',                           NULL),
    ('bouti-main',      'bouti',    1, 'UC3ZeMI_oHM5-xcmPL2D0Ggg', 'الإمام الشهيد البوطي - نسيم الشام',                 '@naseemalsham1',              'https://www.youtube.com/@naseemalsham1',                        NULL),
    ('shaarawy-main',   'shaarawy', 1, 'UCijSEIUA72pyzSNOf_lx5ng', 'القناة الرسمية لفضيلة الشيخ محمد متولي الشعراوي',    '@alsharawiofficial',          'https://www.youtube.com/@alsharawiofficial',                    NULL),
    ('hawwa-main',      'hawwa',    1, 'UCY4XdkNxYeXbq6dqHbe0Lxg', 'الدكتور معاذ سعيد حوا',                             '@drmoathhawwa',               'https://www.youtube.com/c/drmoathhawwa',                        NULL),
    ('sariri-shared',   'sariri',   1, 'UCikKBeXeC90S8NJsoXLr9Ng', 'مدرسة تنكرت العتيقة (مشتركة مع البردوني)',          '@مدرسةتنكرتالعتيقة',          'https://www.youtube.com/channel/UCikKBeXeC90S8NJsoXLr9Ng',      'القناة المشتركة الأهم'),
    ('sariri-personal', 'sariri',   2, NULL,                       'الشيخ مولود السريري (القناة الشخصية)',              '@assariry',                   'https://www.youtube.com/@assariry',                             'القناة الشخصية'),
    ('omari-main',      'omari',    1, 'UCBZ9mBjX_L5szWixhVrFMdg', 'الدكتور علي محمود العمري',                          '@الدكتورعليمحمودالعمري',       'https://www.youtube.com/channel/UCBZ9mBjX_L5szWixhVrFMdg',      NULL),
    ('hashemi-main',    'hashemi',  1, 'UC2hgUdruvEzm4-sxTWrP2zg', 'فقه النفس / مكاني Makany',                          '@MakanyWorld',                'https://www.youtube.com/channel/UC2hgUdruvEzm4-sxTWrP2zg',      NULL),
    ('kamali-main',     'kamali',   1, 'UCASAOTD6fMPEg8jmO4nPblQ', 'قناة الشيخ سعيد الكملي',                            '@elkamali',                   'https://www.youtube.com/@elkamali',                             NULL),
    ('samarrai-main',   'samarrai', 1, 'UCET_yD8OFwj8m4DptN1bMsQ', 'لمسات بيانية - أ.د. فاضل السامرائي',                '@LamasatBayania',             'https://www.youtube.com/@LamasatBayania',                       NULL),
    ('dedew-main',      'dedew',    1, 'UCifZUETjBgcsFaS-ewfb3YQ', 'القناة الرسمية للشيخ محمد الحسن الددو',              '@dedewiat',                   'https://www.youtube.com/c/dedewiat',                            NULL),
    ('alihani-main',    'alihani',  1, 'UC4hprJdeUpKFnViDsCAYN6g', 'علي هاني العقرباوي',                                '@ali_hani',                   'https://www.youtube.com/@ali_hani',                             NULL);
