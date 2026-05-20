import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 11,
    "lesson_code": "HSK1-L11",
    "title": "现在几点",
    "goal": json.dumps({
        "uz": "Vaqtni aytish va so'rash, vaqt ravishi, 前 so'zi",
        "ru": "Говорить и спрашивать о времени, временные наречия, слово 前",
        "tj": "Гуфтан ва пурсидани вақт, зарфҳои вақт, калимаи 前",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "O'n birinchi darsda siz vaqtni aytishni, vaqt ravishlarini va 前 so'zi bilan vaqtni ifodalashni o'rganasiz. 11 ta yangi so'z, 3 ta dialog.",
        "ru": "В одиннадцатом уроке вы научитесь говорить о времени, использовать временные наречия и выражать время с помощью слова 前. 11 новых слов, 3 диалога.",
        "tj": "Дар дарси ёздаҳум шумо ёд мегиред, ки вақтро чӣ тавр гӯед, зарфҳои вақтро истифода баред ва вақтро бо калимаи 前 баён кунед. 11 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "现在", "pinyin": "xiànzài",  "pos": "n.",
         "uz": "hozir, shu vaqtda",
         "ru": "сейчас, в данный момент",
         "tj": "ҳоло, дар ин лаҳза"},
        {"no": 2,  "zh": "点",   "pinyin": "diǎn",     "pos": "m.",
         "uz": "soat (soat uchun o'lchov so'zi)",
         "ru": "час (счётное слово для часов)",
         "tj": "соат (вақт)"},
        {"no": 3,  "zh": "分",   "pinyin": "fēn",      "pos": "m.",
         "uz": "daqiqa",
         "ru": "минута",
         "tj": "дақиқа"},
        {"no": 4,  "zh": "中午", "pinyin": "zhōngwǔ",  "pos": "n.",
         "uz": "tush, yarim kun",
         "ru": "полдень",
         "tj": "нисфирӯзӣ, нимрӯз"},
        {"no": 5,  "zh": "吃饭", "pinyin": "chī fàn",  "pos": "v.",
         "uz": "ovqat yemoq, ovqatlanmoq",
         "ru": "есть, обедать",
         "tj": "хӯрдан, хӯрок хӯрдан"},
        {"no": 6,  "zh": "时候", "pinyin": "shíhou",   "pos": "n.",
         "uz": "vaqt, lahza",
         "ru": "время, момент",
         "tj": "вақт, лаҳза"},
        {"no": 7,  "zh": "回",   "pinyin": "huí",      "pos": "v.",
         "uz": "qaytmoq, orqaga kelmoq",
         "ru": "возвращаться",
         "tj": "баргаштан, бозгашт"},
        {"no": 8,  "zh": "我们", "pinyin": "wǒmen",    "pos": "pron.",
         "uz": "biz",
         "ru": "мы",
         "tj": "мо"},
        {"no": 9,  "zh": "电影", "pinyin": "diànyǐng", "pos": "n.",
         "uz": "kino, film",
         "ru": "кино, фильм",
         "tj": "кино, филм"},
        {"no": 10, "zh": "住",   "pinyin": "zhù",      "pos": "v.",
         "uz": "yashash, turar joy",
         "ru": "жить, проживать",
         "tj": "зиндагӣ кардан, истиқомат кардан"},
        {"no": 11, "zh": "前",   "pinyin": "qián",     "pos": "n.",
         "uz": "oldin, avval",
         "ru": "до, перед",
         "tj": "пеш аз, қабл аз"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Kutubxonada — soat so'rash",
            "scene_ru": "В библиотеке — спрашивают время",
            "scene_tj": "Дар китобхона — пурсидани вақт",
            "dialogue": [
                {"speaker": "A", "zh": "现在几点？",    "pinyin": "Xiànzài jǐ diǎn?",
                 "uz": "Hozir soat necha?",
                 "ru": "Сколько сейчас времени?",
                 "tj": "Ҳоло соат чанд аст?"},
                {"speaker": "B", "zh": "现在十点十分。", "pinyin": "Xiànzài shí diǎn shí fēn.",
                 "uz": "Hozir soat o'nda o'n daqiqa.",
                 "ru": "Сейчас десять минут одиннадцатого.",
                 "tj": "Ҳоло соат даҳ ва даҳ дақиқа аст."},
                {"speaker": "A", "zh": "中午几点吃饭？", "pinyin": "Zhōngwǔ jǐ diǎn chī fàn?",
                 "uz": "Tushda soat nechada ovqatlanasiz?",
                 "ru": "В котором часу вы обедаете?",
                 "tj": "Нисфирӯзӣ соат чанд хӯрок мехӯред?"},
                {"speaker": "B", "zh": "十二点吃饭。",  "pinyin": "Shí'èr diǎn chī fàn.",
                 "uz": "Soat o'n ikkida ovqatlanamiz.",
                 "ru": "Мы обедаем в двенадцать.",
                 "tj": "Мо соат дувоздаҳ хӯрок мехӯрем."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Uyda — otani kutish",
            "scene_ru": "Дома — ждут папу",
            "scene_tj": "Дар хона — интизори падар",
            "dialogue": [
                {"speaker": "A", "zh": "爸爸什么时候回家？",   "pinyin": "Bàba shénme shíhou huí jiā?",
                 "uz": "Dada qachon uyga qaytadi?",
                 "ru": "Когда папа придёт домой?",
                 "tj": "Падар кай ба хона бармегардад?"},
                {"speaker": "B", "zh": "下午五点。",           "pinyin": "Xiàwǔ wǔ diǎn.",
                 "uz": "Tushdan keyin soat beshda.",
                 "ru": "В пять часов вечера.",
                 "tj": "Соати панҷи баъдазнисфирӯзӣ."},
                {"speaker": "A", "zh": "我们什么时候去看电影？","pinyin": "Wǒmen shénme shíhou qù kàn diànyǐng?",
                 "uz": "Biz qachon kinoga boramiz?",
                 "ru": "Когда мы идём в кино?",
                 "tj": "Мо кай ба кино меравем?"},
                {"speaker": "B", "zh": "六点三十分。",         "pinyin": "Liù diǎn sānshí fēn.",
                 "uz": "Soat olti yarimda.",
                 "ru": "В половине седьмого.",
                 "tj": "Соати шаш ва си дақиқа."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Uyda — Pekin safari rejasi",
            "scene_ru": "Дома — план поездки в Пекин",
            "scene_tj": "Дар хона — нақшаи сафар ба Пекин",
            "dialogue": [
                {"speaker": "A", "zh": "我星期一去北京。",          "pinyin": "Wǒ xīngqī yī qù Běijīng.",
                 "uz": "Men dushanba kuni Pekinga boraman.",
                 "ru": "Я еду в Пекин в понедельник.",
                 "tj": "Ман рӯзи душанбе ба Пекин меравам."},
                {"speaker": "B", "zh": "你想在北京住几天？",        "pinyin": "Nǐ xiǎng zài Běijīng zhù jǐ tiān?",
                 "uz": "Pekinda necha kun qolmoqchisiz?",
                 "ru": "Сколько дней вы планируете пробыть в Пекине?",
                 "tj": "Шумо мехоҳед чанд рӯз дар Пекин бимонед?"},
                {"speaker": "A", "zh": "住三天。",                  "pinyin": "Zhù sān tiān.",
                 "uz": "Uch kun.",
                 "ru": "Три дня.",
                 "tj": "Се рӯз."},
                {"speaker": "B", "zh": "星期五前能回家吗？",        "pinyin": "Xīngqī wǔ qián néng huí jiā ma?",
                 "uz": "Juma kunidan oldin uyga qayta olasizmi?",
                 "ru": "Вы сможете вернуться домой до пятницы?",
                 "tj": "Шумо метавонед пеш аз ҷумъа ба хона баргардед?"},
                {"speaker": "A", "zh": "能。",                      "pinyin": "Néng.",
                 "uz": "Ha, qila olaman.",
                 "ru": "Да, смогу.",
                 "tj": "Ҳа, метавонам."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "时间的表达",
            "title_uz": "Vaqtni ifodalash",
            "title_ru": "Выражение времени",
            "title_tj": "Баёни вақт",
            "rule_uz": (
                "Soat: 点(diǎn)\n"
                "Daqiqa: 分(fēn)\n"
                "Tuzilish: N点 yoki N点M分\n\n"
                "9:00 → 九点\n"
                "10:10 → 十点十分\n"
                "5:30 → 五点三十分\n"
                "2:05 → 两点零五分\n\n"
                "Kun qismlari:\n"
                "上午 shàngwǔ — ertalab (AM)\n"
                "中午 zhōngwǔ — tush\n"
                "下午 xiàwǔ — tushdan keyin (PM)\n\n"
                "Eslatma: 2:00 → 两点 (liǎng diǎn), 二点 emas!"
            ),
            "rule_ru": (
                "Час: 点(diǎn)\n"
                "Минута: 分(fēn)\n"
                "Структура: N点 или N点M分\n\n"
                "9:00 → 九点\n"
                "10:10 → 十点十分\n"
                "5:30 → 五点三十分\n"
                "2:05 → 两点零五分\n\n"
                "Части суток:\n"
                "上午 shàngwǔ — утро (AM)\n"
                "中午 zhōngwǔ — полдень\n"
                "下午 xiàwǔ — послеполудень (PM)\n\n"
                "Внимание: 2:00 → 两点 (liǎng diǎn), не 二点!"
            ),
            "rule_tj": (
                "Соат: 点(diǎn)\n"
                "Дақиқа: 分(fēn)\n"
                "Сохтор: N点 ё N点M分\n\n"
                "9:00 → 九点\n"
                "10:10 → 十点十分\n"
                "5:30 → 五点三十分\n"
                "2:05 → 两点零五分\n\n"
                "Қисмҳои шабонарӯз:\n"
                "上午 shàngwǔ — субҳ (AM)\n"
                "中午 zhōngwǔ — нисфирӯзӣ\n"
                "下午 xiàwǔ — баъдазнисфирӯзӣ (PM)\n\n"
                "Эзоҳ: 2:00 → 两点 (liǎng diǎn), на 二点!"
            ),
            "examples": [
                {"zh": "现在九点。",       "pinyin": "Xiànzài jiǔ diǎn.",
                 "uz": "Hozir soat to'qqiz.", "ru": "Сейчас девять часов.", "tj": "Ҳоло соат нӯҳ аст."},
                {"zh": "下午三点十分。",   "pinyin": "Xiàwǔ sān diǎn shí fēn.",
                 "uz": "Tushdan keyin soat uch o'nda.", "ru": "Десять минут четвёртого дня.", "tj": "Баъдазнисфирӯзӣ соати се ва даҳ дақиқа."},
                {"zh": "上午两点半。",     "pinyin": "Shàngwǔ liǎng diǎn bàn.",
                 "uz": "Ertalab soat ikki yarim.", "ru": "Половина третьего утра.", "tj": "Субҳ соати ду ва ним."},
            ]
        },
        {
            "no": 2,
            "title_zh": "时间词做状语",
            "title_uz": "Vaqt ravishi",
            "title_ru": "Временное наречие",
            "title_tj": "Зарфи вақт",
            "rule_uz": (
                "Vaqt so'zi gapda ravish vazifasini bajarishi mumkin.\n"
                "U odatda egadan keyin yoki egadan oldin keladi.\n\n"
                "1-tuzilish: Ega + Vaqt + Fe'l\n"
                "妈妈六点做饭。— Onam soat oltida ovqat pishiradi.\n\n"
                "2-tuzilish: Vaqt + Ega + Fe'l\n"
                "中午十二点我们吃饭。— Biz tushda soat o'n ikkida ovqatlanamiz.\n\n"
                "Savol: 什么时候 — qachon?"
            ),
            "rule_ru": (
                "Слово времени может служить наречием в предложении.\n"
                "Обычно стоит после подлежащего или перед ним.\n\n"
                "Структура 1: Подлежащее + Время + Глагол\n"
                "妈妈六点做饭。— Мама готовит в шесть.\n\n"
                "Структура 2: Время + Подлежащее + Глагол\n"
                "中午十二点我们吃饭。— В полдень в двенадцать мы обедаем.\n\n"
                "Вопрос: 什么时候 — когда?"
            ),
            "rule_tj": (
                "Калимаи вақт дар ҷумла метавонад зарф бошад.\n"
                "Одатан баъд аз мубтадо ё пеш аз он меояд.\n\n"
                "Сохтори 1: Муб. + Вақт + Феъл\n"
                "妈妈六点做饭。— Модар соати шаш хӯрок мепазад.\n\n"
                "Сохтори 2: Вақт + Муб. + Феъл\n"
                "中午十二点我们吃饭。— Мо нисфирӯзӣ соати дувоздаҳ хӯрок мехӯрем.\n\n"
                "Савол: 什么时候 — кай?"
            ),
            "examples": [
                {"zh": "他们六点吃饭。",       "pinyin": "Tāmen liù diǎn chī fàn.",
                 "uz": "Ular soat oltida ovqatlanadi.", "ru": "Они едят в шесть часов.", "tj": "Онҳо соати шаш хӯрок мехӯранд."},
                {"zh": "我星期一去北京。",     "pinyin": "Wǒ xīngqī yī qù Běijīng.",
                 "uz": "Men dushanba kuni Pekinga boraman.", "ru": "Я еду в Пекин в понедельник.", "tj": "Ман рӯзи душанбе ба Пекин меравам."},
                {"zh": "你什么时候回家？",     "pinyin": "Nǐ shénme shíhou huí jiā?",
                 "uz": "Qachon uyga qaytasiz?", "ru": "Когда вы идёте домой?", "tj": "Шумо кай ба хона бармегардед?"},
            ]
        },
        {
            "no": 3,
            "title_zh": "名词 前",
            "title_uz": "前 vaqt belgisi",
            "title_ru": "前 — временной маркер",
            "title_tj": "前 — нишонаи вақт",
            "rule_uz": (
                "前(qián) — muayyan voqeadan oldingi vaqtni bildiradi.\n\n"
                "三天前 — uch kun oldin\n"
                "一个星期前 — bir hafta oldin\n"
                "四点前 — soat to'rtdan oldin\n"
                "星期五前 — juma kunidan oldin\n\n"
                "Misol:\n"
                "星期五前能回家吗？— Juma kunidan oldin uyga qayta olasizmi?\n"
                "八点前去学校。— Soat sakkizdan oldin maktabga boring."
            ),
            "rule_ru": (
                "前(qián) — указывает на момент времени до определённого события.\n\n"
                "三天前 — три дня назад\n"
                "一个星期前 — одну неделю назад\n"
                "四点前 — до четырёх часов\n"
                "星期五前 — до пятницы\n\n"
                "Пример:\n"
                "星期五前能回家吗？— Вы сможете вернуться домой до пятницы?\n"
                "八点前去学校。— Идите в школу до восьми."
            ),
            "rule_tj": (
                "前(qián) — лаҳзаи вақтро пеш аз рӯйдоди муайян нишон медиҳад.\n\n"
                "三天前 — се рӯз пеш\n"
                "一个星期前 — як ҳафта пеш\n"
                "四点前 — пеш аз соати чор\n"
                "星期五前 — пеш аз ҷумъа\n\n"
                "Намуна:\n"
                "星期五前能回家吗？— Шумо метавонед пеш аз ҷумъа ба хона баргардед?\n"
                "八点前去学校。— Пеш аз соати ҳашт ба мактаб равед."
            ),
            "examples": [
                {"zh": "星期五前能回家吗？", "pinyin": "Xīngqī wǔ qián néng huí jiā ma?",
                 "uz": "Juma kunidan oldin uyga qayta olasizmi?", "ru": "Сможете вернуться домой до пятницы?", "tj": "Метавонед пеш аз ҷумъа ба хона баргардед?"},
                {"zh": "三天前我在北京。",   "pinyin": "Sān tiān qián wǒ zài Běijīng.",
                 "uz": "Uch kun oldin men Pekinda edim.", "ru": "Три дня назад я был в Пекине.", "tj": "Се рӯз пеш ман дар Пекин будам."},
                {"zh": "八点前来。",         "pinyin": "Bā diǎn qián lái.",
                 "uz": "Soat sakkizdan oldin keling.", "ru": "Приходите до восьми.", "tj": "Пеш аз соати ҳашт биёед."},
            ]
        },
    ], ensure_ascii=False),

    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "time_writing",
            "instruction_uz": "Vaqtni xitoycha yozing:",
            "instruction_ru": "Напишите время по-китайски:",
            "instruction_tj": "Вақтро ба хитоӣ нависед:",
            "items": [
                {"prompt": "9:00",    "answer": "九点",          "pinyin": "jiǔ diǎn"},
                {"prompt": "2:00",    "answer": "两点",          "pinyin": "liǎng diǎn"},
                {"prompt": "10:10",   "answer": "十点十分",      "pinyin": "shí diǎn shí fēn"},
                {"prompt": "6:30",    "answer": "六点三十分",    "pinyin": "liù diǎn sānshí fēn"},
                {"prompt": "15:15",   "answer": "下午三点十五分","pinyin": "xiàwǔ sān diǎn shíwǔ fēn"},
            ]
        },
        {
            "no": 2,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagilarni xitoycha yozing:",
            "instruction_ru": "Напишите по-китайски:",
            "instruction_tj": "Ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "Hozir soat necha?",                    "prompt_ru": "Сколько сейчас времени?",              "prompt_tj": "Ҳоло соат чанд аст?",                    "answer": "现在几点？",            "pinyin": "Xiànzài jǐ diǎn?"},
                {"prompt_uz": "Biz qachon kinoga boramiz?",            "prompt_ru": "Когда мы идём в кино?",                "prompt_tj": "Мо кай ба кино меравем?",                 "answer": "我们什么时候去看电影？", "pinyin": "Wǒmen shénme shíhou qù kàn diànyǐng?"},
                {"prompt_uz": "Juma kunidan oldin uyga qayta olasizmi?","prompt_ru": "Сможете вернуться домой до пятницы?","prompt_tj": "Метавонед пеш аз ҷумъа ба хона баргардед?","answer": "星期五前能回家吗？",    "pinyin": "Xīngqī wǔ qián néng huí jiā ma?"},
                {"prompt_uz": "Men Pekinda uch kun qolaman.",           "prompt_ru": "Я пробуду в Пекине три дня.",          "prompt_tj": "Ман се рӯз дар Пекин мемонам.",           "answer": "我在北京住三天。",      "pinyin": "Wǒ zài Běijīng zhù sān tiān."},
            ]
        },
        {
            "no": 3,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холигиро пур кунед:",
            "items": [
                {"prompt": "现在___点___分？",           "answer": "几/几",    "pinyin": "jǐ/jǐ"},
                {"prompt": "爸爸什么___回家？",          "answer": "时候",     "pinyin": "shíhou"},
                {"prompt": "星期五___能回家吗？",        "answer": "前",       "pinyin": "qián"},
                {"prompt": "我___一去北京。",            "answer": "星期",     "pinyin": "xīngqī"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["九点", "两点", "十点十分", "六点三十分", "下午三点十五分"]},
        {"no": 2, "answers": ["现在几点？", "我们什么时候去看电影？", "星期五前能回家吗？", "我在北京住三天。"]},
        {"no": 3, "answers": ["几/几", "时候", "前", "星期"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Kunlik jadvalingizni yozing (vaqt + faoliyat):",
            "instruction_ru": "Напишите свой распорядок дня (время + деятельность):",
            "instruction_tj": "Ҷадвали рӯзонаи худро нависед (вақт + фаъолият):",
            "words": ["点", "分", "吃饭", "去", "回家", "看书", "工作"],
            "example": "上午___点我___。中午___点我___。下午___点我___。",
        },
        {
            "no": 2,
            "instruction_uz": "Savollarga javob bering:",
            "instruction_ru": "Ответьте на вопросы:",
            "instruction_tj": "Ба саволҳо ҷавоб диҳед:",
            "items": [
                {"prompt": "现在几点？",
                 "hint_uz": "Hozirgi vaqtni ayting",
                 "hint_ru": "Скажите текущее время",
                 "hint_tj": "Вақти ҳозираро гӯед"},
                {"prompt": "你几点吃饭？",
                 "hint_uz": "Soat nechada ovqatlanasiz?",
                 "hint_ru": "В котором часу вы едите?",
                 "hint_tj": "Шумо соат чанд хӯрок мехӯред?"},
                {"prompt": "你什么时候回家？",
                 "hint_uz": "Qachon uyga qaytasiz?",
                 "hint_ru": "Когда вы идёте домой?",
                 "hint_tj": "Шумо кай ба хона бармегардед?"},
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
            print(f"Updated Lesson {LESSON['lesson_code']} — {LESSON['title']}.")
        else:
            lesson = CourseLesson(**LESSON)
            session.add(lesson)
            await session.commit()
            print(f"Created Lesson {LESSON['lesson_code']} — {LESSON['title']}.")


if __name__ == "__main__":
    asyncio.run(seed())
