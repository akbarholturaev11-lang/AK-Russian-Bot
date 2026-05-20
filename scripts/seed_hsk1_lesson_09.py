import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 9,
    "lesson_code": "HSK1-L09",
    "title": "你儿子在哪儿工作",
    "goal": json.dumps({
        "uz": "Joylashuv va ish joyi haqida so'rash, fe'l va predlog 在",
        "ru": "Спрашивать о местонахождении и месте работы, глагол и предлог 在",
        "tj": "Пурсидан дар бораи ҷойгиршавӣ ва ҷои кор, феъл ва пешояндаи 在",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "To'qqizinchi darsda siz kimdir qayerda ekanligini, qaerda ishlashimizni va 在 ning ikki ishlatilishini o'rganasiz. 14 ta yangi so'z, 3 ta dialog.",
        "ru": "В девятом уроке вы научитесь спрашивать, где кто-то находится, где мы работаем, и узнаете два применения 在. 14 новых слов, 3 диалога.",
        "tj": "Дар дарси нӯҳум шумо ёд мегиред, ки кӣ дар куҷо аст, дар куҷо кор мекунем ва ду истифодаи 在 -ро. 14 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "小",   "pinyin": "xiǎo",     "pos": "adj.",
         "uz": "kichik, mayda",
         "ru": "маленький, небольшой",
         "tj": "хурд, майда"},
        {"no": 2,  "zh": "猫",   "pinyin": "māo",      "pos": "n.",
         "uz": "mushuk",
         "ru": "кошка",
         "tj": "гурба"},
        {"no": 3,  "zh": "在",   "pinyin": "zài",      "pos": "v./prep.",
         "uz": "joylashmoq / -da, -da (joy ko'rsatgich)",
         "ru": "находиться / в, на (показатель места)",
         "tj": "будан / дар (нишондиҳандаи ҷой)"},
        {"no": 4,  "zh": "哪儿", "pinyin": "nǎr",      "pos": "pron.",
         "uz": "qayerda",
         "ru": "где",
         "tj": "куҷо"},
        {"no": 5,  "zh": "狗",   "pinyin": "gǒu",      "pos": "n.",
         "uz": "it",
         "ru": "собака",
         "tj": "саг"},
        {"no": 6,  "zh": "椅子", "pinyin": "yǐzi",     "pos": "n.",
         "uz": "stul",
         "ru": "стул",
         "tj": "курсӣ"},
        {"no": 7,  "zh": "下面", "pinyin": "xiàmian",  "pos": "n.",
         "uz": "pastda, ostida",
         "ru": "внизу, под",
         "tj": "дар поён, зери"},
        {"no": 8,  "zh": "工作", "pinyin": "gōngzuò",  "pos": "v./n.",
         "uz": "ishlash / ish, mehnat",
         "ru": "работать / работа",
         "tj": "кор кардан / кор"},
        {"no": 9,  "zh": "儿子", "pinyin": "érzi",     "pos": "n.",
         "uz": "o'g'il",
         "ru": "сын",
         "tj": "писар"},
        {"no": 10, "zh": "医院", "pinyin": "yīyuàn",   "pos": "n.",
         "uz": "kasalxona",
         "ru": "больница",
         "tj": "беморхона"},
        {"no": 11, "zh": "医生", "pinyin": "yīshēng",  "pos": "n.",
         "uz": "shifokor",
         "ru": "врач",
         "tj": "духтур"},
        {"no": 12, "zh": "爸爸", "pinyin": "bàba",     "pos": "n.",
         "uz": "ota, dada",
         "ru": "папа, отец",
         "tj": "бобо, падар"},
        {"no": 13, "zh": "家",   "pinyin": "jiā",      "pos": "n.",
         "uz": "uy, oila",
         "ru": "дом, семья",
         "tj": "хона, оила"},
        {"no": 14, "zh": "那儿", "pinyin": "nàr",      "pos": "pron.",
         "uz": "u yerda, ana o'sha yerda",
         "ru": "там, вон там",
         "tj": "он ҷо, дар он ҷо"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Uyda — mushuk va it qayerda",
            "scene_ru": "Дома — где кошка и собака",
            "scene_tj": "Дар хона — гурба ва саг куҷост",
            "dialogue": [
                {"speaker": "A", "zh": "小猫在哪儿？",          "pinyin": "Xiǎo māo zài nǎr?",
                 "uz": "Mushuk qayerda?",
                 "ru": "Где кошка?",
                 "tj": "Гурба куҷост?"},
                {"speaker": "B", "zh": "小猫在那儿。",          "pinyin": "Xiǎo māo zài nàr.",
                 "uz": "Mushuk u yerda.",
                 "ru": "Кошка вон там.",
                 "tj": "Гурба он ҷост."},
                {"speaker": "A", "zh": "小狗在哪儿？",          "pinyin": "Xiǎo gǒu zài nǎr?",
                 "uz": "It qayerda?",
                 "ru": "Где собака?",
                 "tj": "Саг куҷост?"},
                {"speaker": "B", "zh": "小狗在椅子下面。",      "pinyin": "Xiǎo gǒu zài yǐzi xiàmian.",
                 "uz": "It stulning ostida.",
                 "ru": "Собака под стулом.",
                 "tj": "Саг зери курсӣ аст."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Temir yo'l stansiyasida — ish joyi",
            "scene_ru": "На вокзале — место работы",
            "scene_tj": "Дар истгоҳи роҳи оҳан — ҷои кор",
            "dialogue": [
                {"speaker": "A", "zh": "你在哪儿工作？",              "pinyin": "Nǐ zài nǎr gōngzuò?",
                 "uz": "Siz qaerda ishlaysiz?",
                 "ru": "Где вы работаете?",
                 "tj": "Шумо дар куҷо кор мекунед?"},
                {"speaker": "B", "zh": "我在学校工作。",              "pinyin": "Wǒ zài xuéxiào gōngzuò.",
                 "uz": "Men maktabda ishlaymen.",
                 "ru": "Я работаю в школе.",
                 "tj": "Ман дар мактаб кор мекунам."},
                {"speaker": "A", "zh": "你儿子在哪儿工作？",          "pinyin": "Nǐ érzi zài nǎr gōngzuò?",
                 "uz": "Sizning o'g'lingiz qaerda ishlaydi?",
                 "ru": "Где работает ваш сын?",
                 "tj": "Писари шумо дар куҷо кор мекунад?"},
                {"speaker": "B", "zh": "我儿子在医院工作，他是医生。", "pinyin": "Wǒ érzi zài yīyuàn gōngzuò, tā shì yīshēng.",
                 "uz": "O'g'lim kasalxonada ishlaydi, u shifokor.",
                 "ru": "Мой сын работает в больнице — он врач.",
                 "tj": "Писарам дар беморхона кор мекунад, ӯ духтур аст."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Telefonda — ota qayerda",
            "scene_ru": "По телефону — где папа",
            "scene_tj": "Аз телефон — падар куҷост",
            "dialogue": [
                {"speaker": "A", "zh": "你爸爸在家吗？",    "pinyin": "Nǐ bàba zài jiā ma?",
                 "uz": "Otangiz uyda ekanmi?",
                 "ru": "Ваш папа дома?",
                 "tj": "Падари шумо дар хона аст?"},
                {"speaker": "B", "zh": "不在家。",          "pinyin": "Bú zài jiā.",
                 "uz": "Uyda yo'q.",
                 "ru": "Нет, не дома.",
                 "tj": "Дар хона нест."},
                {"speaker": "A", "zh": "他在哪儿呢？",      "pinyin": "Tā zài nǎr ne?",
                 "uz": "Xo'sh, u qayerda?",
                 "ru": "Тогда где же он?",
                 "tj": "Пас ӯ куҷост?"},
                {"speaker": "B", "zh": "他在医院。",        "pinyin": "Tā zài yīyuàn.",
                 "uz": "U kasalxonada.",
                 "ru": "Он в больнице.",
                 "tj": "Ӯ дар беморхона аст."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "动词 在",
            "title_uz": "Fe'l 在 (joylashuv)",
            "title_ru": "Глагол 在 (местонахождение)",
            "title_tj": "Феъли 在 (ҷойгиршавӣ)",
            "rule_uz": (
                "在(zài) — fe'l sifatida biror narsa yoki kishining qayerda ekanligini bildiradi.\n"
                "Tuzilish: Ega + 在 + Joy\n\n"
                "Inkor: Ega + 不在 + Joy\n"
                "爸爸不在家。— Ota uyda emas."
            ),
            "rule_ru": (
                "在(zài) — как глагол указывает, где находится кто-то или что-то.\n"
                "Структура: Подлежащее + 在 + Место\n\n"
                "Отрицание: Подлежащее + 不在 + Место\n"
                "爸爸不在家。— Папа не дома."
            ),
            "rule_tj": (
                "在(zài) — ҳамчун феъл нишон медиҳад, ки чизе ё касе дар куҷо аст.\n"
                "Сохтор: Муб. + 在 + Ҷой\n\n"
                "Инкор: Муб. + 不在 + Ҷой\n"
                "爸爸不在家。— Падар дар хона нест."
            ),
            "examples": [
                {"zh": "小猫在那儿。",   "pinyin": "Xiǎo māo zài nàr.",
                 "uz": "Mushuk u yerda.", "ru": "Кошка вон там.", "tj": "Гурба он ҷост."},
                {"zh": "我朋友在学校。", "pinyin": "Wǒ péngyou zài xuéxiào.",
                 "uz": "Do'stim maktabda.", "ru": "Мой друг в школе.", "tj": "Дӯстам дар мактаб аст."},
                {"zh": "爸爸不在家。",   "pinyin": "Bàba bú zài jiā.",
                 "uz": "Ota uyda emas.", "ru": "Папа не дома.", "tj": "Падар дар хона нест."},
            ]
        },
        {
            "no": 2,
            "title_zh": "哪儿 — jo'ylashuv so'roq olmoshi",
            "title_uz": "哪儿 — joylashuv so'roq olmoshi",
            "title_ru": "哪儿 — вопросительное местоимение места",
            "title_tj": "哪儿 — зарфи истифсори ҷой",
            "rule_uz": (
                "哪儿(nǎr) — joylashuvni so'rash uchun ishlatiladigan so'roq so'zi.\n"
                "Tuzilish: Ega + 在 + 哪儿?\n\n"
                "Misol:\n"
                "小猫在哪儿？— Mushuk qayerda?\n"
                "你在哪儿工作？— Siz qaerda ishlaysiz?\n"
                "他在哪儿呢？— Xo'sh, u qayerda?"
            ),
            "rule_ru": (
                "哪儿(nǎr) — вопросительное слово для уточнения места.\n"
                "Структура: Подлежащее + 在 + 哪儿?\n\n"
                "Пример:\n"
                "小猫在哪儿？— Где кошка?\n"
                "你在哪儿工作？— Где вы работаете?\n"
                "他在哪儿呢？— Где же он?"
            ),
            "rule_tj": (
                "哪儿(nǎr) — калимаи суол барои пурсидани ҷой.\n"
                "Сохтор: Муб. + 在 + 哪儿?\n\n"
                "Намуна:\n"
                "小猫在哪儿？— Гурба куҷост?\n"
                "你在哪儿工作？— Шумо дар куҷо кор мекунед?\n"
                "他在哪儿呢？— Пас ӯ куҷост?"
            ),
            "examples": [
                {"zh": "你在哪儿工作？",  "pinyin": "Nǐ zài nǎr gōngzuò?",
                 "uz": "Siz qaerda ishlaysiz?", "ru": "Где вы работаете?", "tj": "Шумо дар куҷо кор мекунед?"},
                {"zh": "小狗在哪儿？",    "pinyin": "Xiǎo gǒu zài nǎr?",
                 "uz": "It qayerda?", "ru": "Где собака?", "tj": "Саг куҷост?"},
                {"zh": "他爸爸在哪儿呢？","pinyin": "Tā bàba zài nǎr ne?",
                 "uz": "Uning otasi qayerda?", "ru": "Где же его папа?", "tj": "Падари ӯ куҷост?"},
            ]
        },
        {
            "no": 3,
            "title_zh": "介词 在",
            "title_uz": "Predlog 在 (joy bildiradi)",
            "title_ru": "Предлог 在 (указывает место действия)",
            "title_tj": "Пешоянди 在 (ҷойи амал)",
            "rule_uz": (
                "在(zài) — predlog sifatida fe'ldan oldin kelib, harakatning qayerda sodir bo'lishini bildiradi.\n"
                "Tuzilish: Ega + 在 + Joy + Fe'l\n\n"
                "Farq:\n"
                "她在医院。(Fe'l 在) — U kasalxonada.\n"
                "她在医院工作。(Predlog 在) — U kasalxonada ishlaydi."
            ),
            "rule_ru": (
                "在(zài) — как предлог стоит перед глаголом и указывает место действия.\n"
                "Структура: Подлежащее + 在 + Место + Глагол\n\n"
                "Разница:\n"
                "她在医院。(Глагол 在) — Она в больнице.\n"
                "她在医院工作。(Предлог 在) — Она работает в больнице."
            ),
            "rule_tj": (
                "在(zài) — ҳамчун пешоянд пеш аз феъл меояд ва ҷойи амалро нишон медиҳад.\n"
                "Сохтор: Муб. + 在 + Ҷой + Феъл\n\n"
                "Фарқ:\n"
                "她在医院。(Феъли 在) — Ӯ дар беморхона аст.\n"
                "她在医院工作。(Пешоянди 在) — Ӯ дар беморхона кор мекунад."
            ),
            "examples": [
                {"zh": "我儿子在医院工作。", "pinyin": "Wǒ érzi zài yīyuàn gōngzuò.",
                 "uz": "O'g'lim kasalxonada ishlaydi.", "ru": "Мой сын работает в больнице.", "tj": "Писарам дар беморхона кор мекунад."},
                {"zh": "他们在学校看书。",   "pinyin": "Tāmen zài xuéxiào kàn shū.",
                 "uz": "Ular maktabda kitob o'qiydi.", "ru": "Они читают в школе.", "tj": "Онҳо дар мактаб китоб мехонанд."},
                {"zh": "我在家喝茶。",       "pinyin": "Wǒ zài jiā hē chá.",
                 "uz": "Men uyda choy ichaman.", "ru": "Я пью чай дома.", "tj": "Ман дар хона чой менӯшам."},
            ]
        },
    ], ensure_ascii=False),

    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagilarni xitoycha yozing:",
            "instruction_ru": "Напишите по-китайски:",
            "instruction_tj": "Ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "Mushuk qayerda?",            "prompt_ru": "Где кошка?",                    "prompt_tj": "Гурба куҷост?",            "answer": "小猫在哪儿？",       "pinyin": "Xiǎo māo zài nǎr?"},
                {"prompt_uz": "It stulning ostida.",         "prompt_ru": "Собака под стулом.",            "prompt_tj": "Саг зери курсӣ аст.",       "answer": "小狗在椅子下面。",   "pinyin": "Xiǎo gǒu zài yǐzi xiàmian."},
                {"prompt_uz": "Siz qaerda ishlaysiz?",       "prompt_ru": "Где вы работаете?",            "prompt_tj": "Шумо дар куҷо кор мекунед?","answer": "你在哪儿工作？",     "pinyin": "Nǐ zài nǎr gōngzuò?"},
                {"prompt_uz": "O'g'lim kasalxonada ishlaydi.","prompt_ru": "Мой сын работает в больнице.","prompt_tj": "Писарам дар беморхона кор мекунад.","answer": "我儿子在医院工作。", "pinyin": "Wǒ érzi zài yīyuàn gōngzuò."},
                {"prompt_uz": "Otangiz uyda ekanmi?",        "prompt_ru": "Ваш папа дома?",               "prompt_tj": "Падари шумо дар хона аст?", "answer": "你爸爸在家吗？",     "pinyin": "Nǐ bàba zài jiā ma?"},
                {"prompt_uz": "Uyda yo'q, u kasalxonada.",   "prompt_ru": "Не дома — он в больнице.",     "prompt_tj": "Дар хона нест, ӯ дар беморхона аст.", "answer": "不在家，他在医院。",  "pinyin": "Bú zài jiā, tā zài yīyuàn."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холигиро пур кунед:",
            "items": [
                {"prompt": "小猫___那儿。",              "answer": "在",   "pinyin": "zài"},
                {"prompt": "你___哪儿工作？",            "answer": "在",   "pinyin": "zài"},
                {"prompt": "小狗在椅子___面。",          "answer": "下",   "pinyin": "xià"},
                {"prompt": "我儿子在医院___，他是医生。", "answer": "工作", "pinyin": "gōngzuò"},
            ]
        },
        {
            "no": 3,
            "type": "make_sentence",
            "instruction_uz": "Berilgan so'zlardan gap tuzing:",
            "instruction_ru": "Составьте предложение из данных слов:",
            "instruction_tj": "Аз калимаҳои дода шуда ҷумла созед:",
            "items": [
                {"words": ["在", "医院", "工作", "我妈妈"],        "answer": "我妈妈在医院工作。",  "pinyin": "Wǒ māma zài yīyuàn gōngzuò."},
                {"words": ["哪儿", "在", "小猫", "？"],            "answer": "小猫在哪儿？",        "pinyin": "Xiǎo māo zài nǎr?"},
                {"words": ["在", "家", "不", "爸爸"],              "answer": "爸爸不在家。",        "pinyin": "Bàba bú zài jiā."},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["小猫在哪儿？", "小狗在椅子下面。", "你在哪儿工作？", "我儿子在医院工作。", "你爸爸在家吗？", "不在家，他在医院。"]},
        {"no": 2, "answers": ["在", "在", "下", "工作"]},
        {"no": 3, "answers": ["我妈妈在医院工作。", "小猫在哪儿？", "爸爸不在家。"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Oila a'zolaringiz haqida 4 ta gap yozing (qayerda ishlaydi/qayerda):",
            "instruction_ru": "Напишите 4 предложения о членах своей семьи (где работают/находятся):",
            "instruction_tj": "4 ҷумла дар бораи аъзоёни оилаатон нависед (дар куҷо кор мекунанд/ҷойгиранд):",
            "words": ["在", "工作", "医院", "学校", "家", "商店"],
            "example": "我___在___工作/在___。",
        },
        {
            "no": 2,
            "instruction_uz": "Savollarga javob bering:",
            "instruction_ru": "Ответьте на вопросы:",
            "instruction_tj": "Ба саволҳо ҷавоб диҳед:",
            "items": [
                {"prompt": "你在哪儿工作/学习？",
                 "hint_uz": "Qaerda ishlaysiz yoki o'qiysiz?",
                 "hint_ru": "Где вы работаете или учитесь?",
                 "hint_tj": "Шумо дар куҷо кор мекунед ё мехонед?"},
                {"prompt": "你爸爸在哪儿工作？",
                 "hint_uz": "Otangiz qaerda ishlaydi?",
                 "hint_ru": "Где работает ваш папа?",
                 "hint_tj": "Падари шумо дар куҷо кор мекунад?"},
                {"prompt": "你现在在哪儿？",
                 "hint_uz": "Hozir qayerdasiz?",
                 "hint_ru": "Где вы сейчас?",
                 "hint_tj": "Шумо ҳоло куҷоед?"},
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
