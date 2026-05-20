import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 5,
    "lesson_code": "HSK1-L05",
    "title": "她女儿今年二十岁",
    "goal": json.dumps({
        "uz": "Yosh va oila a'zolari haqida gapirish, 100 gacha raqamlarni o'rganing",
        "ru": "Говорить о возрасте и членах семьи, выучить числа до 100",
        "tj": "Дар бораи синну сол ва аъзоёни оила гап задан, рақамҳоро то 100 омӯхтан",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Beshinchi darsda siz kimningdir yoshini so'rash va aytish, oila a'zolari sonini gapirish va 100 gacha raqamlarni o'rganasiz. 10 ta yangi so'z, 3 ta dialog.",
        "ru": "На пятом уроке вы научитесь спрашивать и называть возраст, говорить о количестве членов семьи и выучите числа до 100. 10 новых слов, 3 диалога.",
        "tj": "Дар дарси панҷум шумо пурсидан ва гуфтани синну сол, шумораи аъзоёни оиларо омӯхта, рақамҳоро то 100 меомӯзед. 10 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "家",   "pinyin": "jiā",     "pos": "n.",
         "uz": "oila, uy",
         "ru": "семья, дом",
         "tj": "оила, хона"},
        {"no": 2,  "zh": "有",   "pinyin": "yǒu",     "pos": "v.",
         "uz": "bor, ega bo'lmoq",
         "ru": "иметь, есть",
         "tj": "доштан, мавҷуд будан"},
        {"no": 3,  "zh": "口",   "pinyin": "kǒu",     "pos": "m.",
         "uz": "o'lchov so'zi (oila a'zolari uchun)",
         "ru": "счётное слово (для членов семьи)",
         "tj": "калимаи шуморавӣ (барои аъзоёни оила)"},
        {"no": 4,  "zh": "女儿", "pinyin": "nǚ'ér",   "pos": "n.",
         "uz": "qiz farzand",
         "ru": "дочь",
         "tj": "духтар (фарзанд)"},
        {"no": 5,  "zh": "几",   "pinyin": "jǐ",      "pos": "pron.",
         "uz": "nechta (10 tagacha)",
         "ru": "сколько (до 10)",
         "tj": "чанд (то 10)"},
        {"no": 6,  "zh": "岁",   "pinyin": "suì",     "pos": "m.",
         "uz": "yosh (o'lchov so'zi)",
         "ru": "лет (счётное слово для возраста)",
         "tj": "сол (барои синну сол)"},
        {"no": 7,  "zh": "了",   "pinyin": "le",      "pos": "part.",
         "uz": "holat o'zgarishi yuklamasi",
         "ru": "частица изменения состояния",
         "tj": "ҳарфи тағйири ҳолат"},
        {"no": 8,  "zh": "今年", "pinyin": "jīnnián", "pos": "n.",
         "uz": "bu yil",
         "ru": "в этом году",
         "tj": "امسол، ин сол"},
        {"no": 9,  "zh": "多",   "pinyin": "duō",     "pos": "adv.",
         "uz": "ko'p, qancha (daraja)",
         "ru": "много, как (степень)",
         "tj": "зиёд, чӣ қадар (дараҷа)"},
        {"no": 10, "zh": "大",   "pinyin": "dà",      "pos": "adj.",
         "uz": "katta, ulug' (yoshda)",
         "ru": "большой, старший (по возрасту)",
         "tj": "калон, бузург (аз рӯи синну сол)"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Maktabda — oila a'zolari",
            "scene_ru": "В школе — о членах семьи",
            "scene_tj": "Дар мактаб — дар бораи аъзоёни оила",
            "dialogue": [
                {"speaker": "A", "zh": "你家有几口人？",  "pinyin": "Nǐ jiā yǒu jǐ kǒu rén?",
                 "uz": "Sizning oilangizda necha kishi bor?",
                 "ru": "Сколько человек в вашей семье?",
                 "tj": "Дар оилаи шумо чанд нафар аст?"},
                {"speaker": "B", "zh": "我家有三口人。",  "pinyin": "Wǒ jiā yǒu sān kǒu rén.",
                 "uz": "Bizning oilamizda uch kishi bor.",
                 "ru": "В нашей семье трое человек.",
                 "tj": "Дар оилаи мо се нафар аст."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Ofisda — yosh so'rash (bolalar)",
            "scene_ru": "В офисе — спрашиваем возраст (ребёнок)",
            "scene_tj": "Дар идора — пурсидани синну сол (кӯдак)",
            "dialogue": [
                {"speaker": "A", "zh": "你女儿几岁了？",   "pinyin": "Nǐ nǚ'ér jǐ suì le?",
                 "uz": "Qizingiz necha yoshda?",
                 "ru": "Сколько лет вашей дочери?",
                 "tj": "Духтаратон чанд сол дорад?"},
                {"speaker": "B", "zh": "她今年四岁了。",   "pinyin": "Tā jīnnián sì suì le.",
                 "uz": "U bu yil to'rt yoshga to'ldi.",
                 "ru": "Ей в этом году исполнилось четыре года.",
                 "tj": "Вай имсол чор сол шуд."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Ofisda — kattalar yoshi",
            "scene_ru": "В офисе — возраст взрослых",
            "scene_tj": "Дар идора — синну соли калонсолон",
            "dialogue": [
                {"speaker": "A", "zh": "李老师多大了？",       "pinyin": "Lǐ lǎoshī duō dà le?",
                 "uz": "Muallima Li necha yoshda?",
                 "ru": "Сколько лет преподавателю Ли?",
                 "tj": "Муаллима Ли чанд сол дорад?"},
                {"speaker": "B", "zh": "她今年五十岁了。",     "pinyin": "Tā jīnnián wǔshí suì le.",
                 "uz": "U bu yil ellik yoshga kirdi.",
                 "ru": "В этом году ей исполнилось пятьдесят.",
                 "tj": "Вай имсол панҷоҳ сол шуд."},
                {"speaker": "A", "zh": "她女儿呢？",           "pinyin": "Tā nǚ'ér ne?",
                 "uz": "Uning qizi-chi?",
                 "ru": "А её дочь?",
                 "tj": "Духтараш чӣ?"},
                {"speaker": "B", "zh": "她女儿今年二十岁。",   "pinyin": "Tā nǚ'ér jīnnián èrshí suì.",
                 "uz": "Uning qizi bu yil yigirma yoshda.",
                 "ru": "Её дочери в этом году двадцать лет.",
                 "tj": "Духтараш имсол бист сол дорад."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "几 — Necha? (10 gacha)",
            "title_uz": "几 — Necha? (10 gacha)",
            "title_ru": "几 — Сколько? (до 10)",
            "title_tj": "几 — Чанд? (то 10)",
            "rule_uz": (
                "几(jǐ) — 10 dan kichik sonlar uchun so'roq so'zi.\n"
                "Tuzilma: Ega + 有 + 几 + O'lchov so'zi + Ot?\n\n"
                "Misol:\n"
                "你家有几口人？— Sizning oilangizda necha kishi bor?\n"
                "你有几个汉语老师？— Nechta xitoy tili o'qituvchingiz bor?\n"
                "你女儿几岁了？— Qizingiz necha yoshda?"
            ),
            "rule_ru": (
                "几(jǐ) — вопросительное слово для чисел менее 10.\n"
                "Структура: Подлежащее + 有 + 几 + Счётное слово + Существительное?\n\n"
                "Пример:\n"
                "你家有几口人？— Сколько человек в вашей семье?\n"
                "你有几个汉语老师？— Сколько у вас преподавателей китайского?\n"
                "你女儿几岁了？— Сколько лет вашей дочери?"
            ),
            "rule_tj": (
                "几(jǐ) — калимаи саволӣ барои рақамҳои камтар аз 10.\n"
                "Сохтор: Мубтадо + 有 + 几 + Калимаи шуморавӣ + Исм?\n\n"
                "Мисол:\n"
                "你家有几口人？— Дар оилаи шумо чанд нафар аст?\n"
                "你有几个汉语老师？— Шумо чанд муаллими забони чинӣ доред?\n"
                "你女儿几岁了？— Духтаратон чанд сол дорад?"
            ),
            "examples": [
                {"zh": "你家有几口人？",   "pinyin": "Nǐ jiā yǒu jǐ kǒu rén?",
                 "uz": "Sizning oilangizda necha kishi bor?", "ru": "Сколько человек в вашей семье?", "tj": "Дар оилаи шумо чанд нафар аст?"},
                {"zh": "你有几个朋友？",   "pinyin": "Nǐ yǒu jǐ ge péngyou?",
                 "uz": "Nechta do'stingiz bor?", "ru": "Сколько у вас друзей?", "tj": "Шумо чанд дӯст доред?"},
                {"zh": "她有几岁了？",     "pinyin": "Tā yǒu jǐ suì le?",
                 "uz": "U necha yoshda?", "ru": "Сколько ей лет?", "tj": "Вай чанд сол дорад?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "100 gacha raqamlar",
            "title_uz": "100 gacha raqamlar",
            "title_ru": "Числа до 100",
            "title_tj": "Рақамҳо то 100",
            "rule_uz": (
                "1-10: 一yī 二èr 三sān 四sì 五wǔ 六liù 七qī 八bā 九jiǔ 十shí\n\n"
                "O'nliklar:\n"
                "20 = 二十 (èrshí)\n"
                "30 = 三十 (sānshí)\n"
                "50 = 五十 (wǔshí)\n"
                "99 = 九十九 (jiǔshíjiǔ)\n\n"
                "Aralash:\n"
                "23 = 二十三 (èrshísān)\n"
                "56 = 五十六 (wǔshíliù)\n"
                "88 = 八十八 (bāshíbā)"
            ),
            "rule_ru": (
                "1-10: 一yī 二èr 三sān 四sì 五wǔ 六liù 七qī 八bā 九jiǔ 十shí\n\n"
                "Десятки:\n"
                "20 = 二十 (èrshí)\n"
                "30 = 三十 (sānshí)\n"
                "50 = 五十 (wǔshí)\n"
                "99 = 九十九 (jiǔshíjiǔ)\n\n"
                "Составные:\n"
                "23 = 二十三 (èrshísān)\n"
                "56 = 五十六 (wǔshíliù)\n"
                "88 = 八十八 (bāshíbā)"
            ),
            "rule_tj": (
                "1-10: 一yī 二èr 三sān 四sì 五wǔ 六liù 七qī 八bā 九jiǔ 十shí\n\n"
                "Даҳгонаҳо:\n"
                "20 = 二十 (èrshí)\n"
                "30 = 三十 (sānshí)\n"
                "50 = 五十 (wǔshí)\n"
                "99 = 九十九 (jiǔshíjiǔ)\n\n"
                "Омехта:\n"
                "23 = 二十三 (èrshísān)\n"
                "56 = 五十六 (wǔshíliù)\n"
                "88 = 八十八 (bāshíbā)"
            ),
            "examples": [
                {"zh": "二十",   "pinyin": "èrshí",     "uz": "yigirma", "ru": "двадцать", "tj": "бист"},
                {"zh": "五十",   "pinyin": "wǔshí",     "uz": "ellik",   "ru": "пятьдесят", "tj": "панҷоҳ"},
                {"zh": "二十三", "pinyin": "èrshísān",  "uz": "yigirma uch", "ru": "двадцать три", "tj": "бисту се"},
                {"zh": "九十九", "pinyin": "jiǔshíjiǔ", "uz": "to'qson to'qqiz", "ru": "девяносто девять", "tj": "навадуно"},
            ]
        },
        {
            "no": 3,
            "title_zh": "了 — holat o'zgarishi yuklamasi",
            "title_uz": "了 — holat o'zgarishi yuklamasi",
            "title_ru": "了 — частица изменения состояния",
            "title_tj": "了 — ҳарфи тағйири ҳолат",
            "rule_uz": (
                "了(le) — gap oxiriga qo'yilsa, yangi holat yoki o'zgarishni bildiradi.\n\n"
                "Misol:\n"
                "她今年五十岁了。— U bu yil ellik yoshga kirdi (yangi holat).\n"
                "我女儿四岁了。— Qizim to'rt yoshga to'ldi.\n\n"
                "多大了？— Necha yoshga kirdingiz? (yosh so'rash)"
            ),
            "rule_ru": (
                "了(le) — ставится в конце предложения, указывая на новое состояние или изменение.\n\n"
                "Пример:\n"
                "她今年五十岁了。— В этом году ей исполнилось пятьдесят (новое состояние).\n"
                "我女儿四岁了。— Моей дочери исполнилось четыре.\n\n"
                "多大了？— Сколько вам лет? (спрашиваем возраст)"
            ),
            "rule_tj": (
                "了(le) — дар охири ҷумла ҳолати нав ё тағйирро нишон медиҳад.\n\n"
                "Мисол:\n"
                "她今年五十岁了。— Вай имсол панҷоҳ сол шуд (ҳолати нав).\n"
                "我女儿四岁了。— Духтарам чор сол шуд.\n\n"
                "多大了？— Шумо чанд сол шудед? (пурсидани синну сол)"
            ),
            "examples": [
                {"zh": "她今年二十岁了。", "pinyin": "Tā jīnnián èrshí suì le.",
                 "uz": "U bu yil yigirma yoshga kirdi.", "ru": "В этом году ей исполнилось двадцать.", "tj": "Вай имсол бист сол шуд."},
                {"zh": "他五十岁了。",     "pinyin": "Tā wǔshí suì le.",
                 "uz": "U ellik yoshga kirdi.", "ru": "Ему исполнилось пятьдесят.", "tj": "Вай панҷоҳ сол шуд."},
                {"zh": "你多大了？",       "pinyin": "Nǐ duō dà le?",
                 "uz": "Siz necha yoshdasiz?", "ru": "Сколько вам лет?", "tj": "Шумо чанд сол доред?"},
            ]
        },
        {
            "no": 4,
            "title_zh": "多大 vs 几岁 — yosh so'rash",
            "title_uz": "多大 vs 几岁 — yosh so'rash",
            "title_ru": "多大 vs 几岁 — спрашиваем возраст",
            "title_tj": "多大 vs 几岁 — пурсидани синну сол",
            "rule_uz": (
                "多大(duō dà) — kattalar yoshini so'rash uchun.\n"
                "几岁(jǐ suì) — bolalar yoshini so'rash uchun (10 gacha).\n\n"
                "Kattalar: 你多大了？— Siz necha yoshdasiz?\n"
                "Bolalar: 你女儿几岁了？— Qizingiz necha yoshda?"
            ),
            "rule_ru": (
                "多大(duō dà) — спрашиваем возраст взрослых.\n"
                "几岁(jǐ suì) — спрашиваем возраст детей (до 10).\n\n"
                "Взрослые: 你多大了？— Сколько вам лет?\n"
                "Дети: 你女儿几岁了？— Сколько лет вашей дочери?"
            ),
            "rule_tj": (
                "多大(duō dà) — пурсидани синну соли калонсолон.\n"
                "几岁(jǐ suì) — пурсидани синну соли кӯдакон (то 10).\n\n"
                "Калонсолон: 你多大了？— Шумо чанд сол доред?\n"
                "Кӯдакон: 你女儿几岁了？— Духтаратон чанд сол дорад?"
            ),
            "examples": [
                {"zh": "你多大了？",     "pinyin": "Nǐ duō dà le?",
                 "uz": "Siz necha yoshdasiz? (kattalar)", "ru": "Сколько вам лет? (взрослые)", "tj": "Шумо чанд сол доред? (калонсолон)"},
                {"zh": "她女儿几岁了？", "pinyin": "Tā nǚ'ér jǐ suì le?",
                 "uz": "Uning qizi necha yoshda? (bola)", "ru": "Сколько лет её дочери? (ребёнок)", "tj": "Духтараш чанд сол дорад? (кӯдак)"},
            ]
        },
    ], ensure_ascii=False),

    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "numbers",
            "instruction_uz": "Raqamlarni xitoycha yozing:",
            "instruction_ru": "Напишите числа по-китайски:",
            "instruction_tj": "Рақамҳоро ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "25", "prompt_ru": "25", "prompt_tj": "25", "answer": "二十五",   "pinyin": "èrshíwǔ"},
                {"prompt_uz": "38", "prompt_ru": "38", "prompt_tj": "38", "answer": "三十八",   "pinyin": "sānshíbā"},
                {"prompt_uz": "50", "prompt_ru": "50", "prompt_tj": "50", "answer": "五十",     "pinyin": "wǔshí"},
                {"prompt_uz": "99", "prompt_ru": "99", "prompt_tj": "99", "answer": "九十九",   "pinyin": "jiǔshíjiǔ"},
                {"prompt_uz": "100", "prompt_ru": "100", "prompt_tj": "100", "answer": "一百",  "pinyin": "yìbǎi"},
            ]
        },
        {
            "no": 2,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagilarni xitoycha yozing:",
            "instruction_ru": "Напишите по-китайски:",
            "instruction_tj": "Ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "Sizning oilangizda necha kishi bor?", "prompt_ru": "Сколько человек в вашей семье?", "prompt_tj": "Дар оилаи шумо чанд нафар аст?", "answer": "你家有几口人？", "pinyin": "Nǐ jiā yǒu jǐ kǒu rén?"},
                {"prompt_uz": "Bizning oilamizda besh kishi bor.", "prompt_ru": "В нашей семье пятеро.", "prompt_tj": "Дар оилаи мо панҷ нафар аст.", "answer": "我家有五口人。", "pinyin": "Wǒ jiā yǒu wǔ kǒu rén."},
                {"prompt_uz": "Siz necha yoshdasiz?", "prompt_ru": "Сколько вам лет?", "prompt_tj": "Шумо чанд сол доред?", "answer": "你多大了？", "pinyin": "Nǐ duō dà le?"},
                {"prompt_uz": "U bu yil yigirma yoshda.", "prompt_ru": "В этом году ей двадцать лет.", "prompt_tj": "Вай имсол бист сол дорад.", "answer": "她今年二十岁了。", "pinyin": "Tā jīnnián èrshí suì le."},
            ]
        },
        {
            "no": 3,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холиро пур кунед:",
            "items": [
                {"prompt_uz": "你家___几口人？", "prompt_ru": "你家___几口人？", "prompt_tj": "你家___几口人？", "answer": "有", "pinyin": "yǒu"},
                {"prompt_uz": "李老师今年五十___了。", "prompt_ru": "李老师今年五十___了。", "prompt_tj": "李老师今年五十___了。", "answer": "岁", "pinyin": "suì"},
                {"prompt_uz": "你女儿___岁了？", "prompt_ru": "你女儿___岁了？", "prompt_tj": "你女儿___岁了？", "answer": "几", "pinyin": "jǐ"},
                {"prompt_uz": "李老师___大了？", "prompt_ru": "李老师___大了？", "prompt_tj": "李老师___大了？", "answer": "多", "pinyin": "duō"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["二十五", "三十八", "五十", "九十九", "一百"]},
        {"no": 2, "answers": ["你家有几口人？", "我家有五口人。", "你多大了？", "她今年二十岁了。"]},
        {"no": 3, "answers": ["有", "岁", "几", "多"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "O'z oilangiz haqida 3-4 ta gap yozing:",
            "instruction_ru": "Напишите 3-4 предложения о своей семье:",
            "instruction_tj": "Дар бораи оилаи худатон 3-4 ҷумла нависед:",
            "template": "我家有___口人。我今年___岁了。我___有女儿/儿子。",
            "words": ["家", "有", "口", "岁", "今年", "了"],
        },
        {
            "no": 2,
            "instruction_uz": "Raqamlarni xitoycha yozing:",
            "instruction_ru": "Напишите числа по-китайски:",
            "instruction_tj": "Рақамҳоро ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "17", "prompt_ru": "17", "prompt_tj": "17", "answer": "十七"},
                {"prompt_uz": "43", "prompt_ru": "43", "prompt_tj": "43", "answer": "四十三"},
                {"prompt_uz": "68", "prompt_ru": "68", "prompt_tj": "68", "answer": "六十八"},
                {"prompt_uz": "100", "prompt_ru": "100", "prompt_tj": "100", "answer": "一百"},
            ]
        }
    ], ensure_ascii=False),

    "is_active": True,
}


async def seed():
    async with SessionLocal() as session:
        result = await session.execute(
            select(CourseLesson).where(CourseLesson.lesson_code == LESSON["lesson_code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in LESSON.items():
                setattr(existing, key, value)
            await session.commit()
            print(f"✅ Lesson {LESSON['lesson_code']} — {LESSON['title']} updated.")
        else:
            lesson = CourseLesson(**LESSON)
            session.add(lesson)
            await session.commit()
            print(f"✅ Lesson {LESSON['lesson_code']} — {LESSON['title']} created.")


if __name__ == "__main__":
    asyncio.run(seed())
