import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 10,
    "lesson_code": "HSK3-L10",
    "title": json.dumps({"zh": "数学比历史难多了", "uz": "Matematika tarixdan ancha qiyin", "ru": "Математика намного сложнее истории", "tj": "Математика аз таърих хеле душвортар аст"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "Aniq taqqoslash iboralarini o'rganish: B dan A qiyin/oson, taxminiy sonlar", "ru": "Изучить точные сравнения: A намного сложнее B, приблизительные числа", "tj": "Омӯхтани муқоисаҳои дақиқ: A аз B хеле душвортар, рақамҳои тахминӣ"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda 'A比B+Adj+多了' aniq taqqoslash tuzilmasi, 'A不如B' va taxminiy sonlarni (数词+多/几) o'rganamiz.", "ru": "В этом уроке мы изучим точное сравнение 'A比B+Adj+多了', конструкцию 'A不如B' и приблизительные числа (数词+多/几).", "tj": "Дар ин дарс мо сохтори муқоисаи дақиқи 'A比B+Adj+多了', сохтори 'A不如B' ва рақамҳои тахминӣ (数词+多/几)-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "数学", "pinyin": "shùxué", "pos": "n", "uz": "matematika", "ru": "математика", "tj": "математика"},
        {"no": 2, "zh": "历史", "pinyin": "lìshǐ", "pos": "n", "uz": "tarix", "ru": "история", "tj": "таърих"},
        {"no": 3, "zh": "物理", "pinyin": "wùlǐ", "pos": "n", "uz": "fizika", "ru": "физика", "tj": "физика"},
        {"no": 4, "zh": "化学", "pinyin": "huàxué", "pos": "n", "uz": "kimyo", "ru": "химия", "tj": "химия"},
        {"no": 5, "zh": "成绩", "pinyin": "chéngjì", "pos": "n", "uz": "natija, baho", "ru": "результат, оценка", "tj": "натиҷа, баҳо"},
        {"no": 6, "zh": "考试", "pinyin": "kǎoshì", "pos": "n/v", "uz": "imtihon; imtihon bermoq", "ru": "экзамен; сдавать экзамен", "tj": "имтиҳон; имтиҳон додан"},
        {"no": 7, "zh": "及格", "pinyin": "jígé", "pos": "v", "uz": "o'tmoq (imtihondan)", "ru": "сдать (экзамен)", "tj": "гузаштан (аз имтиҳон)"},
        {"no": 8, "zh": "满分", "pinyin": "mǎnfēn", "pos": "n", "uz": "to'liq ball (100 ball)", "ru": "полный балл (100 очков)", "tj": "балли пурра (100 балл)"},
        {"no": 9, "zh": "多", "pinyin": "duō", "pos": "suf", "uz": "dan ko'p (taxminiy)", "ru": "с лишним (приблизительно)", "tj": "бештар (тахминан)"},
        {"no": 10, "zh": "几", "pinyin": "jǐ", "pos": "num", "uz": "bir necha, taxminan", "ru": "несколько, около", "tj": "чанд, тахминан"},
        {"no": 11, "zh": "不如", "pinyin": "bùrú", "pos": "v", "uz": "yomonroq; qodir emas", "ru": "хуже, не так хорош, как", "tj": "камтар, монанд нест"},
        {"no": 12, "zh": "重要", "pinyin": "zhòngyào", "pos": "adj", "uz": "muhim, ahamiyatli", "ru": "важный, значительный", "tj": "муҳим, аҳамиятнок"},
        {"no": 13, "zh": "复习", "pinyin": "fùxí", "pos": "v", "uz": "takrorlamoq, o'rganilganlarni ko'rmoq", "ru": "повторять, готовиться", "tj": "такрор кардан, омодагӣ дидан"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Imtihon oldidan suhbat", "ru": "Разговор перед экзаменом", "tj": "Суҳбат пеш аз имтиҳон"},
            "dialogue": [
                {"speaker": "A", "zh": "你最近在复习什么？", "pinyin": "Nǐ zuìjìn zài fùxí shénme?", "uz": "Siz yaqinda nimani takrorlamoqdasiz?", "ru": "Что ты сейчас повторяешь?", "tj": "Шумо охирон чиро такрор мекунед?"},
                {"speaker": "B", "zh": "数学，数学比历史难多了！", "pinyin": "Shùxué, shùxué bǐ lìshǐ nán duō le!", "uz": "Matematika, matematika tarixdan ancha qiyin!", "ru": "Математику, математика намного сложнее истории!", "tj": "Математика, математика аз таърих хеле душвортар аст!"},
                {"speaker": "A", "zh": "你数学成绩怎么样？", "pinyin": "Nǐ shùxué chéngjì zěnme yàng?", "uz": "Matematika baholaringiz qanday?", "ru": "Как у тебя оценки по математике?", "tj": "Баҳоҳои математикаи шумо чӣ тавр аст?"},
                {"speaker": "B", "zh": "不太好，上次考了六十多分，没及格。", "pinyin": "Bú tài hǎo, shàng cì kǎo le liùshí duō fēn, méi jígé.", "uz": "Yaxshi emas, o'tgan safar oltmishdan ko'proq ball oldim, o'tolmadim.", "ru": "Не очень, в прошлый раз набрал больше шестидесяти, но не сдал.", "tj": "На хуб, дафъаи гузашта шасту чанд балл гирифтам, нагузаштам."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Fanlarni taqqoslash", "ru": "Сравнение предметов", "tj": "Муқоисаи фанҳо"},
            "dialogue": [
                {"speaker": "A", "zh": "物理比化学难吗？", "pinyin": "Wùlǐ bǐ huàxué nán ma?", "uz": "Fizika kimyodan qiyinroqmi?", "ru": "Физика сложнее химии?", "tj": "Оё физика аз химия душвортар аст?"},
                {"speaker": "B", "zh": "物理不如化学难，但都需要复习。", "pinyin": "Wùlǐ bùrú huàxué nán, dàn dōu xūyào fùxí.", "uz": "Fizika kimyo kadar qiyin emas, lekin ikkalasi ham takrorlanishi kerak.", "ru": "Физика не такая сложная, как химия, но обе требуют повторения.", "tj": "Физика ба монанди химия душвор нест, аммо ҳарду такрор мехоҳанд."},
                {"speaker": "A", "zh": "历史需要记几百个年代，很难！", "pinyin": "Lìshǐ xūyào jì jǐ bǎi gè niándài, hěn nán!", "uz": "Tarix uchun bir necha yuz yilni eslab qolish kerak, juda qiyin!", "ru": "В истории нужно запомнить несколько сотен дат, это очень сложно!", "tj": "Дар таърих чанд садсолаи таърихро ёд кардан лозим аст, хеле душвор!"},
                {"speaker": "B", "zh": "是的，历史比数学还难！", "pinyin": "Shì de, lìshǐ bǐ shùxué hái nán!", "uz": "Ha, tarix matematikadan ham qiyin!", "ru": "Да, история ещё сложнее математики!", "tj": "Ҳа, таърих аз математика ҳам душвортар аст!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "To'liq ball olish haqida", "ru": "О полном балле", "tj": "Дар бораи балли пурра"},
            "dialogue": [
                {"speaker": "A", "zh": "你上次数学考了多少分？", "pinyin": "Nǐ shàng cì shùxué kǎo le duōshǎo fēn?", "uz": "O'tgan safar matematikadan necha ball oldingiz?", "ru": "Сколько ты набрал по математике в прошлый раз?", "tj": "Дафъаи гузашта аз математика чанд балл гирифтед?"},
                {"speaker": "B", "zh": "九十多分，差一点儿满分！", "pinyin": "Jiǔshí duō fēn, chà yīdiǎnr mǎnfēn!", "uz": "To'qson dan ortiq ball, to'liq ballga oz qoldi!", "ru": "Больше девяноста, совсем чуть-чуть до полного балла!", "tj": "Наваду чанд балл, каме ба балли пурра монда!"},
                {"speaker": "A", "zh": "太棒了！你比我好多了！", "pinyin": "Tài bàng le! Nǐ bǐ wǒ hǎo duō le!", "uz": "Zo'r! Siz mendan ancha yaxshisiz!", "ru": "Отлично! Ты намного лучше меня!", "tj": "Олӣ! Шумо аз ман хеле беҳтаред!"},
                {"speaker": "B", "zh": "不，你不如你自己认为的那么差！", "pinyin": "Bù, nǐ bùrú nǐ zìjǐ rènwéi de nàme chà!", "uz": "Yo'q, siz o'zingiz o'ylaganchalik yomon emassiz!", "ru": "Нет, ты не такой плохой, каким себя считаешь!", "tj": "Не, шумо ба монанди он чизе ки худатон фикр мекунед бад нестед!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Imtihonga tayyorlanish rejasi", "ru": "План подготовки к экзамену", "tj": "Нақшаи омодагӣ ба имтиҳон"},
            "dialogue": [
                {"speaker": "A", "zh": "考试还有几天？", "pinyin": "Kǎoshì hái yǒu jǐ tiān?", "uz": "Imtihonga necha kun qoldi?", "ru": "Сколько дней осталось до экзамена?", "tj": "То имтиҳон чанд рӯз монда?"},
                {"speaker": "B", "zh": "还有十多天，时间不多了！", "pinyin": "Hái yǒu shí duō tiān, shíjiān bù duō le!", "uz": "O'n kundan ortiq qoldi, vaqt ko'p emas!", "ru": "Больше десяти дней, времени осталось немного!", "tj": "Даҳу чанд рӯз монда, вақт зиёд нест!"},
                {"speaker": "A", "zh": "重要的内容一定要仔细复习。", "pinyin": "Zhòngyào de nèiróng yīdìng yào zǐxì fùxí.", "uz": "Muhim mavzularni albatta diqqat bilan takrorlamoq kerak.", "ru": "Важные темы обязательно нужно внимательно повторить.", "tj": "Мавзӯҳои муҳимро ҳатман бодиққат такрор кардан лозим аст."},
                {"speaker": "B", "zh": "好，数学比历史重要，先复习数学！", "pinyin": "Hǎo, shùxué bǐ lìshǐ zhòngyào, xiān fùxí shùxué!", "uz": "Yaxshi, matematika tarixdan muhimroq, avval matematikani takrorlaymiz!", "ru": "Ладно, математика важнее истории, сначала повторим математику!", "tj": "Хуб, математика аз таърих муҳимтар аст, аввал математикаро такрор мекунем!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "比较句②：A比B + 形容词 + 多了",
            "title_uz": "Taqqoslash②: A B dan + sifat + ancha",
            "title_ru": "Сравнение②: A намного + прилагательное + чем B",
            "title_tj": "Муқоиса②: A аз B + сифат + хеле",
            "rule_uz": "'A比B+Adj+多了' — A ning B dan ancha farqli ekanini ta'kidlaydi. '多了' yoki '得多' = ancha, juda ko'p. Oddiy 'A比B+Adj' dan kuchliroq ifoda.",
            "rule_ru": "'A比B+Adj+多了' подчёркивает, что разница между A и B очень велика. '多了' или '得多' = намного. Это более сильное выражение, чем обычное 'A比B+Adj'.",
            "rule_tj": "'A比B+Adj+多了' таъкид мекунад, ки фарқи байни A ва B хеле бузург аст. '多了' ё '得多' = хеле. Ин аз 'A比B+Adj'-и оддӣ ифодаи қавитар аст.",
            "examples": [
                {"zh": "数学比历史难多了！", "pinyin": "Shùxué bǐ lìshǐ nán duō le!", "uz": "Matematika tarixdan ancha qiyin!", "ru": "Математика намного сложнее истории!", "tj": "Математика аз таърих хеле душвортар аст!"},
                {"zh": "你比我好多了！", "pinyin": "Nǐ bǐ wǒ hǎo duō le!", "uz": "Siz mendan ancha yaxshisiz!", "ru": "Ты намного лучше меня!", "tj": "Шумо аз ман хеле беҳтаред!"}
            ]
        },
        {
            "no": 2,
            "title_zh": "概数①：数词 + 多 / 几",
            "title_uz": "Taxminiy sonlar①: son + 多 / 几",
            "title_ru": "Приблизительные числа①: число + 多 / 几",
            "title_tj": "Рақамҳои тахминӣ①: рақам + 多 / 几",
            "rule_uz": "'数词+多' = shu sondan ko'proq (masalan: 三十多 = 30 dan ortiq). '几+量词' = bir necha (masalan: 几天 = bir necha kun, 几百 = bir necha yuz). Ikkalasi ham aniq bo'lmagan miqdorni bildiradi.",
            "rule_ru": "'数词+多' = больше указанного числа (например: 三十多 = больше тридцати). '几+счётное слово' = несколько (например: 几天 = несколько дней, 几百 = несколько сотен). Оба выражают неточное количество.",
            "rule_tj": "'数词+多' = аз рақами зикршуда бештар (масалан: 三十多 = аз сӣ бештар). '几+ададӣ' = чанд (масалан: 几天 = чанд рӯз, 几百 = чанд сад). Ҳарду миқдори ғайридақиқро ифода мекунанд.",
            "examples": [
                {"zh": "我考了九十多分。", "pinyin": "Wǒ kǎo le jiǔshí duō fēn.", "uz": "Men to'qson dan ortiq ball oldim.", "ru": "Я набрал больше девяноста баллов.", "tj": "Ман наваду чанд балл гирифтам."},
                {"zh": "历史需要记几百个年代。", "pinyin": "Lìshǐ xūyào jì jǐ bǎi gè niándài.", "uz": "Tarix uchun bir necha yuz yilni eslab qolish kerak.", "ru": "В истории нужно запомнить несколько сотен дат.", "tj": "Дар таърих чанд садсолаи таърихро ёд кардан лозим аст."}
            ]
        },
        {
            "no": 3,
            "title_zh": "A不如B（+ 形容词）",
            "title_uz": "A B kadar + sifat emas (A B dan yomonroq)",
            "title_ru": "A не так хорош, как B (A хуже B)",
            "title_tj": "A ба монанди B нест (A аз B камтар)",
            "rule_uz": "'A不如B' = A B kadar yaxshi emas, A B dan yomonroq. Sifat bilan: 'A不如B+Adj'. 'A没有B那么+Adj' bilan sinonim.",
            "rule_ru": "'A不如B' = A не так хорош, как B, A хуже B. С прилагательным: 'A不如B+Adj'. Синоним 'A没有B那么+Adj'.",
            "rule_tj": "'A不如B' = A ба монанди B хуб нест, A аз B камтар. Бо сифат: 'A不如B+Adj'. Ҳаммаъно бо 'A没有B那么+Adj'.",
            "examples": [
                {"zh": "物理不如化学难。", "pinyin": "Wùlǐ bùrú huàxué nán.", "uz": "Fizika kimyo kadar qiyin emas.", "ru": "Физика не такая сложная, как химия.", "tj": "Физика ба монанди химия душвор нест."},
                {"zh": "今天的天气不如昨天好。", "pinyin": "Jīntiān de tiānqì bùrú zuótiān hǎo.", "uz": "Bugungi havo kechagidek yaxshi emas.", "ru": "Сегодняшняя погода не такая хорошая, как вчера.", "tj": "Ҳавои имрӯза ба монанди дирӯзии хуб нест."}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Matematika tarixdan ancha qiyin!", "ru": "Математика намного сложнее истории!", "tj": "Математика аз таърих хеле душвортар аст!"},
                {"no": 2, "uz": "Men to'qson dan ortiq ball oldim.", "ru": "Я набрал больше девяноста баллов.", "tj": "Ман наваду чанд балл гирифтам."},
                {"no": 3, "uz": "Fizika kimyo kadar qiyin emas.", "ru": "Физика не такая сложная, как химия.", "tj": "Физика ба монанди химия душвор нест."},
                {"no": 4, "uz": "Bugungi havo kechagidek yaxshi emas.", "ru": "Сегодняшняя погода не такая хорошая, как вчера.", "tj": "Ҳавои имрӯза ба монанди дирӯзии хуб нест."},
                {"no": 5, "uz": "Siz mendan ancha yaxshisiz!", "ru": "Ты намного лучше меня!", "tj": "Шумо аз ман хеле беҳтаред!"}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "数学比历史难___了！", "sentence_uz": "Matematika tarixdan ancha ___!", "sentence_ru": "Математика намного ___ истории!", "sentence_tj": "Математика аз таърих хеле ___!", "hint": "多"},
                {"no": 2, "sentence_zh": "我考了六十___分，没及格。", "sentence_uz": "Men oltmish ___ ball oldim, o'tolmadim.", "sentence_ru": "Я набрал больше шестидесяти ___, не сдал.", "sentence_tj": "Ман шасту ___ балл гирифтам, нагузаштам.", "hint": "多"},
                {"no": 3, "sentence_zh": "物理不___化学难。", "sentence_uz": "Fizika kimyo kadar qiyin ___.", "sentence_ru": "Физика не ___ сложная, как химия.", "sentence_tj": "Физика ба монанди химия ___ нест.", "hint": "如"},
                {"no": 4, "sentence_zh": "历史需要记___百个年代。", "sentence_uz": "Tarix uchun bir necha ___ yilni eslab qolish kerak.", "sentence_ru": "В истории нужно запомнить несколько ___ дат.", "sentence_tj": "Дар таърих ___ садсолаи таърихро ёд кардан лозим аст.", "hint": "几"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "你不如你自己认为的那么差！", "pinyin": "Nǐ bùrú nǐ zìjǐ rènwéi de nàme chà!"},
                {"no": 2, "zh": "考试还有十多天，重要内容要仔细复习。", "pinyin": "Kǎoshì hái yǒu shí duō tiān, zhòngyào nèiróng yào zǐxì fùxí."}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "数学比历史难多了！"},
                {"no": 2, "zh": "我考了九十多分。"},
                {"no": 3, "zh": "物理不如化学难。"},
                {"no": 4, "zh": "今天的天气不如昨天好。"},
                {"no": 5, "zh": "你比我好多了！"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "多"},
                {"no": 2, "answer": "多"},
                {"no": 3, "answer": "如"},
                {"no": 4, "answer": "几"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Siz o'zingiz o'ylaganchalik yomon emassiz!", "ru": "Ты не такой плохой, каким себя считаешь!", "tj": "Шумо ба монанди он чизе ки худатон фикр мекунед бад нестед!"},
                {"no": 2, "uz": "Imtihonga o'n kundan ortiq qoldi, muhim mavzularni diqqat bilan takrorlamoq kerak.", "ru": "До экзамена больше десяти дней, важные темы нужно тщательно повторить.", "tj": "То имтиҳон даҳу чанд рӯз монда, мавзӯҳои муҳимро бодиққат такрор кардан лозим аст."}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'A比B+Adj+多了' va 'A不如B' tuzilmalaridan foydalanib, o'z sevimli fanlari haqida 4 ta taqqoslash jumla yozing.", "ru": "Напишите 4 сравнительных предложения о своих любимых предметах, используя 'A比B+Adj+多了' и 'A不如B'.", "tj": "4 ҷумлаи муқоисавӣ дар бораи фанҳои дӯстдоштаатон бо 'A比B+Adj+多了' ва 'A不如B' нависед."},
        {"task_no": 2, "uz": "Taxminiy sonlarni (数词+多 va 几) ishlatib, 3 ta jumla yozing: miqdor, vaqt yoki masofa haqida.", "ru": "Напишите 3 предложения с приблизительными числами (数词+多 и 几) о количестве, времени или расстоянии.", "tj": "3 ҷумла бо рақамҳои тахминӣ (数词+多 ва 几) дар бораи миқдор, вақт ё масофа нависед."}
    ], ensure_ascii=False),
    "is_active": True
}

async def upsert_lesson():
    async with SessionLocal() as session:
        result = await session.execute(
            select(CourseLesson).where(CourseLesson.lesson_code == LESSON["lesson_code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in LESSON.items():
                setattr(existing, key, value)
            print(f"updated: {LESSON['lesson_code']}")
        else:
            session.add(CourseLesson(**LESSON))
            print(f"inserted: {LESSON['lesson_code']}")
        await session.commit()


if __name__ == "__main__":
    asyncio.run(upsert_lesson())
