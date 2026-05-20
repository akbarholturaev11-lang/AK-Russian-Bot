import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 10,
    "lesson_code": "HSK1-L10",
    "title": "我能坐这儿吗",
    "goal": json.dumps({
        "uz": "Joylashuvni ifodalash, 有-gaplar, modal fe'l 能 va bog'lovchi 和",
        "ru": "Выражение местонахождения, предложения с 有, модальный глагол 能 и союз 和",
        "tj": "Баёни ҷойгиршавӣ, ҷумлаҳои 有, феъли модалии 能 ва пайвандаки 和",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "O'ninchi darsda siz narsalar qayerda ekanligini aytishni, 有 bilan mavjudlikni ifodalashni, 能 modal fe'lini va 和 bog'lovchisini o'rganasiz. 12 ta yangi so'z, 3 ta dialog.",
        "ru": "В десятом уроке вы научитесь говорить, где находятся вещи, выражать существование с 有, использовать модальный глагол 能 и союз 和. 12 новых слов, 3 диалога.",
        "tj": "Дар дарси даҳум шумо ёд мегиред, ки чизҳо дар куҷоянд, бо 有 мавҷудиятро баён кунед, феъли модалии 能 ва пайвандаки 和 -ро истифода баред. 12 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "桌子", "pinyin": "zhuōzi",   "pos": "n.",
         "uz": "stol, parta",
         "ru": "стол",
         "tj": "мӣз"},
        {"no": 2,  "zh": "上",   "pinyin": "shàng",    "pos": "n.",
         "uz": "ustida, tepasida",
         "ru": "сверху, на",
         "tj": "болои, дар болои"},
        {"no": 3,  "zh": "电脑", "pinyin": "diànnǎo",  "pos": "n.",
         "uz": "kompyuter",
         "ru": "компьютер",
         "tj": "компютер"},
        {"no": 4,  "zh": "和",   "pinyin": "hé",       "pos": "conj.",
         "uz": "va, bilan",
         "ru": "и, с",
         "tj": "ва, бо"},
        {"no": 5,  "zh": "本",   "pinyin": "běn",      "pos": "m.",
         "uz": "dona (kitob uchun o'lchov so'zi)",
         "ru": "штука (счётное слово для книг)",
         "tj": "адад (барои китоб)"},
        {"no": 6,  "zh": "里",   "pinyin": "lǐ",       "pos": "n.",
         "uz": "ichida",
         "ru": "внутри, в",
         "tj": "дарун, дохили"},
        {"no": 7,  "zh": "前面", "pinyin": "qiánmiàn", "pos": "n.",
         "uz": "oldinida, oldida",
         "ru": "спереди, перед",
         "tj": "пеш, пешаш"},
        {"no": 8,  "zh": "后面", "pinyin": "hòumiàn",  "pos": "n.",
         "uz": "orqasida, ketida",
         "ru": "сзади, за",
         "tj": "қафо, паси"},
        {"no": 9,  "zh": "这儿", "pinyin": "zhèr",     "pos": "pron.",
         "uz": "bu yerda, shu yerda",
         "ru": "здесь, тут",
         "tj": "ин ҷо, ин ҷост"},
        {"no": 10, "zh": "没有", "pinyin": "méiyǒu",   "pos": "adv.",
         "uz": "yo'q, mavjud emas",
         "ru": "нет, не имеется",
         "tj": "не, нест"},
        {"no": 11, "zh": "能",   "pinyin": "néng",     "pos": "mod.",
         "uz": "mumkin, qodir (ruxsat/imkoniyat)",
         "ru": "можно, мочь (способность/разрешение)",
         "tj": "тавонистан, мумкин (иҷозат/қобилият)"},
        {"no": 12, "zh": "坐",   "pinyin": "zuò",      "pos": "v.",
         "uz": "o'tirmoq",
         "ru": "сидеть, садиться",
         "tj": "нишастан"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Ofisda — stol ustida nima bor",
            "scene_ru": "В офисе — что на столе",
            "scene_tj": "Дар идора — болои мӣз чӣ аст",
            "dialogue": [
                {"speaker": "A", "zh": "桌子上有什么？",           "pinyin": "Zhuōzi shàng yǒu shénme?",
                 "uz": "Stol ustida nima bor?",
                 "ru": "Что на столе?",
                 "tj": "Болои мӣз чӣ аст?"},
                {"speaker": "B", "zh": "桌子上有一个电脑和一本书。", "pinyin": "Zhuōzi shàng yǒu yī gè diànnǎo hé yī běn shū.",
                 "uz": "Stol ustida bitta kompyuter va bitta kitob bor.",
                 "ru": "На столе стоит компьютер и лежит книга.",
                 "tj": "Болои мӣз як компютер ва як китоб аст."},
                {"speaker": "A", "zh": "杯子在哪儿？",             "pinyin": "Bēizi zài nǎr?",
                 "uz": "Piyola qayerda?",
                 "ru": "Где стакан?",
                 "tj": "Пиёла куҷост?"},
                {"speaker": "B", "zh": "杯子在桌子里。",           "pinyin": "Bēizi zài zhuōzi lǐ.",
                 "uz": "Piyola stol ichida.",
                 "ru": "Стакан внутри стола.",
                 "tj": "Пиёла дохили мӣз аст."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Sport zalda — oldida va orqasida kim",
            "scene_ru": "В спортзале — кто спереди и сзади",
            "scene_tj": "Дар варзишгоҳ — пеш ва қафо кӣ аст",
            "dialogue": [
                {"speaker": "A", "zh": "前面那个人叫什么名字？",         "pinyin": "Qiánmiàn nàge rén jiào shénme míngzi?",
                 "uz": "Oldidagi odam nomi nima?",
                 "ru": "Как зовут человека спереди?",
                 "tj": "Номи одами пешаш чист?"},
                {"speaker": "B", "zh": "她叫王方，在医院工作。",         "pinyin": "Tā jiào Wáng Fāng, zài yīyuàn gōngzuò.",
                 "uz": "Uning ismi Van Fan, kasalxonada ishlaydi.",
                 "ru": "Её зовут Ван Фан — она работает в больнице.",
                 "tj": "Номаш Ван Фан аст, дар беморхона кор мекунад."},
                {"speaker": "A", "zh": "后面那个人呢？他叫什么名字？",   "pinyin": "Hòumiàn nàge rén ne? Tā jiào shénme míngzi?",
                 "uz": "Orqasidagi odam-chi? Uning ismi nima?",
                 "ru": "А человек сзади? Как его зовут?",
                 "tj": "Одами қафоаш чӣ? Номаш чист?"},
                {"speaker": "B", "zh": "他叫谢朋，在商店工作。",         "pinyin": "Tā jiào Xiè Péng, zài shāngdiàn gōngzuò.",
                 "uz": "Uning ismi She Pen, do'konda ishlaydi.",
                 "ru": "Его зовут Се Пэн — он работает в магазине.",
                 "tj": "Номаш Ше Пен аст, дар дӯкон кор мекунад."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Kutubxonada — o'tirish so'rash",
            "scene_ru": "В библиотеке — просьба сесть",
            "scene_tj": "Дар китобхона — хоҳиши нишастан",
            "dialogue": [
                {"speaker": "A", "zh": "这儿有人吗？",   "pinyin": "Zhèr yǒu rén ma?",
                 "uz": "Bu yerda kimdir o'tiribdimi?",
                 "ru": "Здесь кто-то сидит?",
                 "tj": "Ин ҷо касе нишастаст?"},
                {"speaker": "B", "zh": "没有。",         "pinyin": "Méiyǒu.",
                 "uz": "Yo'q.",
                 "ru": "Нет.",
                 "tj": "Не."},
                {"speaker": "A", "zh": "我能坐这儿吗？", "pinyin": "Wǒ néng zuò zhèr ma?",
                 "uz": "Men bu yerga o'tirsam bo'ladimi?",
                 "ru": "Можно мне здесь сесть?",
                 "tj": "Ман метавонам ин ҷо нишинам?"},
                {"speaker": "B", "zh": "请坐。",         "pinyin": "Qǐng zuò.",
                 "uz": "Marhamat, o'tiring.",
                 "ru": "Пожалуйста, садитесь.",
                 "tj": "Хоҳиш мекунам, биниш."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "有字句",
            "title_uz": "有 gapi (mavjudlik)",
            "title_ru": "Предложения с 有 (существование)",
            "title_tj": "Ҷумлаи 有 (мавҷудият)",
            "rule_uz": (
                "有(yǒu) — biror joyda narsa yoki kishining borligini bildiradi.\n"
                "Tuzilish: Joy + 有 + Narsa/Kishi\n\n"
                "Inkor: 没有 (méiyǒu)\n"
                "椅子下面没有小狗。— Stul ostida it yo'q.\n"
                "这儿有人吗？ — 没有。— Bu yerda kimdir bormi? — Yo'q."
            ),
            "rule_ru": (
                "有(yǒu) — указывает на существование чего-то/кого-то в определённом месте.\n"
                "Структура: Место + 有 + Предмет/Человек\n\n"
                "Отрицание: 没有 (méiyǒu)\n"
                "椅子下面没有小狗。— Под стулом нет собаки.\n"
                "这儿有人吗？ — 没有。— Здесь кто-то есть? — Нет."
            ),
            "rule_tj": (
                "有(yǒu) — мавҷудияти чизе ё касеро дар ҷои муайян нишон медиҳад.\n"
                "Сохтор: Ҷой + 有 + Чиз/Кас\n\n"
                "Инкор: 没有 (méiyǒu)\n"
                "椅子下面没有小狗。— Зери курсӣ саг нест.\n"
                "这儿有人吗？ — 没有。— Ин ҷо кас ҳаст? — Не."
            ),
            "examples": [
                {"zh": "桌子上有一个电脑。",   "pinyin": "Zhuōzi shàng yǒu yī gè diànnǎo.",
                 "uz": "Stol ustida bitta kompyuter bor.", "ru": "На столе стоит компьютер.", "tj": "Болои мӣз як компютер аст."},
                {"zh": "学校里没有商店。",     "pinyin": "Xuéxiào lǐ méiyǒu shāngdiàn.",
                 "uz": "Maktabda do'kon yo'q.", "ru": "В школе нет магазина.", "tj": "Дар мактаб дӯкон нест."},
                {"zh": "这儿有人吗？",         "pinyin": "Zhèr yǒu rén ma?",
                 "uz": "Bu yerda kimdir bormi?", "ru": "Здесь кто-то есть?", "tj": "Ин ҷо кас ҳаст?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "连词 和",
            "title_uz": "Bog'lovchi 和",
            "title_ru": "Союз 和",
            "title_tj": "Пайвандаки 和",
            "rule_uz": (
                "和(hé) — ikki ot yoki olmoshni birlashtiradi ('va', 'bilan').\n"
                "Tuzilish: Ot1 + 和 + Ot2\n\n"
                "Eslatma: 和 faqat ot va olmoshlarni bog'laydi —\n"
                "fe'l va gaplarni bog'lay olmaydi."
            ),
            "rule_ru": (
                "和(hé) — соединяет два существительных или местоимения ('и', 'с').\n"
                "Структура: Сущ1 + 和 + Сущ2\n\n"
                "Примечание: 和 соединяет только существительные и местоимения —\n"
                "глаголы и предложения оно не соединяет."
            ),
            "rule_tj": (
                "和(hé) — ду исм ё ҷонишинро мепайвандад ('ва', 'бо').\n"
                "Сохтор: Исм1 + 和 + Исм2\n\n"
                "Эзоҳ: 和 танҳо исмҳо ва ҷонишинҳоро мепайвандад —\n"
                "феълҳо ва ҷумлаҳоро пайвандакӣ карда наметавонад."
            ),
            "examples": [
                {"zh": "电脑和书",               "pinyin": "diànnǎo hé shū",
                 "uz": "kompyuter va kitob", "ru": "компьютер и книга", "tj": "компютер ва китоб"},
                {"zh": "爸爸和妈妈",             "pinyin": "bàba hé māma",
                 "uz": "ota va ona", "ru": "папа и мама", "tj": "падар ва модар"},
                {"zh": "我有一个中国朋友和一个美国朋友。", "pinyin": "Wǒ yǒu yī gè Zhōngguó péngyou hé yī gè Měiguó péngyou.",
                 "uz": "Mening bitta xitoy do'stim va bitta amerikalik do'stim bor.", "ru": "У меня есть один китайский друг и один американский друг.", "tj": "Ман як дӯсти чинӣ ва як дӯсти амрикоӣ дорам."},
            ]
        },
        {
            "no": 3,
            "title_zh": "能愿动词 能",
            "title_uz": "Modal fe'l 能",
            "title_ru": "Модальный глагол 能",
            "title_tj": "Феъли модалии 能",
            "rule_uz": (
                "能(néng) — imkoniyat yoki ruxsatni bildiradi.\n"
                "Tuzilish: Ega + 能 + Fe'l\n\n"
                "能 va 会 farqi:\n"
                "会 — o'rganib orttirgan mahorat (biladi)\n"
                "能 — sharoitga asoslangan imkoniyat/ruxsat (qila oladi/mumkin)"
            ),
            "rule_ru": (
                "能(néng) — выражает способность или разрешение.\n"
                "Структура: Подлежащее + 能 + Глагол\n\n"
                "Разница 能 и 会:\n"
                "会 — умение, приобретённое в результате обучения\n"
                "能 — возможность/разрешение в зависимости от обстоятельств"
            ),
            "rule_tj": (
                "能(néng) — қобилият ё иҷозатро баён мекунад.\n"
                "Сохтор: Муб. + 能 + Феъл\n\n"
                "Фарқи 能 ва 会:\n"
                "会 — маҳорати аз омӯзиш ба даст омада\n"
                "能 — имконият/иҷозат вобаста ба шароит"
            ),
            "examples": [
                {"zh": "我能坐这儿吗？",       "pinyin": "Wǒ néng zuò zhèr ma?",
                 "uz": "Men bu yerga o'tirsam bo'ladimi?", "ru": "Можно мне здесь сесть?", "tj": "Ман метавонам ин ҷо нишинам?"},
                {"zh": "你能在这儿工作吗？",   "pinyin": "Nǐ néng zài zhèr gōngzuò ma?",
                 "uz": "Siz bu yerda ishlay olasizmi?", "ru": "Вы можете здесь работать?", "tj": "Шумо метавонед ин ҷо кор кунед?"},
                {"zh": "明天你能去商店吗？",   "pinyin": "Míngtiān nǐ néng qù shāngdiàn ma?",
                 "uz": "Ertaga do'konga bora olasizmi?", "ru": "Вы можете завтра пойти в магазин?", "tj": "Фардо шумо метавонед ба дӯкон равед?"},
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
                {"prompt_uz": "Stol ustida nima bor?",             "prompt_ru": "Что на столе?",                       "prompt_tj": "Болои мӣз чӣ аст?",             "answer": "桌子上有什么？",             "pinyin": "Zhuōzi shàng yǒu shénme?"},
                {"prompt_uz": "Stol ustida bitta kitob va bitta kompyuter bor.", "prompt_ru": "На столе книга и компьютер.", "prompt_tj": "Болои мӣз як китоб ва як компютер аст.", "answer": "桌子上有一本书和一个电脑。", "pinyin": "Zhuōzi shàng yǒu yī běn shū hé yī gè diànnǎo."},
                {"prompt_uz": "Bu yerda kimdir o'tiribdimi?",       "prompt_ru": "Здесь кто-то сидит?",                 "prompt_tj": "Ин ҷо касе нишастаст?",          "answer": "这儿有人吗？",               "pinyin": "Zhèr yǒu rén ma?"},
                {"prompt_uz": "Men bu yerga o'tirsam bo'ladimi?",   "prompt_ru": "Можно мне здесь сесть?",              "prompt_tj": "Ман метавонам ин ҷо нишинам?",   "answer": "我能坐这儿吗？",             "pinyin": "Wǒ néng zuò zhèr ma?"},
                {"prompt_uz": "Marhamat, o'tiring.",                "prompt_ru": "Пожалуйста, садитесь.",               "prompt_tj": "Хоҳиш мекунам, биниш.",         "answer": "请坐。",                     "pinyin": "Qǐng zuò."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холигиро пур кунед:",
            "items": [
                {"prompt": "桌子上___一个电脑和一本书。", "answer": "有",   "pinyin": "yǒu"},
                {"prompt": "这儿有人吗？___。",          "answer": "没有", "pinyin": "méiyǒu"},
                {"prompt": "我___坐这儿吗？",             "answer": "能",   "pinyin": "néng"},
                {"prompt": "桌子上有电脑___书。",         "answer": "和",   "pinyin": "hé"},
            ]
        },
        {
            "no": 3,
            "type": "location",
            "instruction_uz": "Qayerda ekanligini ayting (上/里/下面/前面/后面):",
            "instruction_ru": "Скажите, где это находится (上/里/下面/前面/后面):",
            "instruction_tj": "Бигӯед дар куҷост (上/里/下面/前面/后面):",
            "items": [
                {"prompt_uz": "Kitob — stol ustida",        "prompt_ru": "Книга — на столе",           "prompt_tj": "Китоб — болои мӣз",          "answer": "书在桌子上。",     "pinyin": "Shū zài zhuōzi shàng."},
                {"prompt_uz": "It — stul ostida",           "prompt_ru": "Собака — под стулом",        "prompt_tj": "Саг — зери курсӣ",           "answer": "狗在椅子下面。",  "pinyin": "Gǒu zài yǐzi xiàmian."},
                {"prompt_uz": "Kompyuter — stol ichida",    "prompt_ru": "Компьютер — внутри стола",   "prompt_tj": "Компютер — дохили мӣз",      "answer": "电脑在桌子里。",  "pinyin": "Diànnǎo zài zhuōzi lǐ."},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["桌子上有什么？", "桌子上有一本书和一个电脑。", "这儿有人吗？", "我能坐这儿吗？", "请坐。"]},
        {"no": 2, "answers": ["有", "没有", "能", "和"]},
        {"no": 3, "answers": ["书在桌子上。", "狗在椅子下面。", "电脑在桌子里。"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Xonangiz haqida 4 ta gap yozing (有 dan foydalanib):",
            "instruction_ru": "Напишите 4 предложения о своей комнате (используя 有):",
            "instruction_tj": "4 ҷумла дар бораи хонаатон нависед (бо 有):",
            "words": ["有", "没有", "上", "里", "下面", "电脑", "书", "杯子"],
            "example": "我的桌子上有___。桌子里有___。椅子___有___。",
        },
        {
            "no": 2,
            "instruction_uz": "能 dan foydalanib 3 ta savol tuzing va javob bering:",
            "instruction_ru": "Напишите 3 вопроса с 能 и ответьте на них:",
            "instruction_tj": "3 савол бо 能 нависед ва ба онҳо ҷавоб диҳед:",
            "example": "A: 我能坐这儿吗？ B: 请坐。/ 对不起，不能。",
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
