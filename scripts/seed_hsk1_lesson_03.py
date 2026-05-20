import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 3,
    "lesson_code": "HSK1-L03",
    "title": "你叫什么名字",
    "goal": json.dumps({
        "uz": "Xitoycha ismingizni, millatingizni va kasbingizni aytishni o'rganing",
        "ru": "Научитесь называть своё имя, национальность и профессию по-китайски",
        "tj": "Омӯзед, ки чӣ тавр исм, миллат ва касби худро ба забони чинӣ гӯед",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Uchinchi darsda siz xitoycha ismingizni, millatingizni va kasbingizni aytishni o'rganasiz. 9 ta yangi so'z, 3 ta dialog va 是-gaplar grammatikasi.",
        "ru": "На третьем уроке вы научитесь называть своё имя, национальность и профессию по-китайски. 9 новых слов, 3 диалога и грамматика предложений с 是.",
        "tj": "Дар дарси сеюм шумо исм, миллат ва касби худро ба забони чинӣ гуфтанро меомӯзед. 9 калимаи нав, 3 муколама ва грамматикаи ҷумлаҳои 是.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "叫",   "pinyin": "jiào",     "pos": "v.",
         "uz": "nomlanmoq, chaqirmoq",
         "ru": "называться, звать",
         "tj": "номида шудан, даъват кардан"},
        {"no": 2, "zh": "什么", "pinyin": "shénme",   "pos": "pron.",
         "uz": "nima, qaysi",
         "ru": "что, какой",
         "tj": "чӣ, кадом"},
        {"no": 3, "zh": "名字", "pinyin": "míngzi",   "pos": "n.",
         "uz": "ism",
         "ru": "имя",
         "tj": "ном, исм"},
        {"no": 4, "zh": "我",   "pinyin": "wǒ",       "pos": "pron.",
         "uz": "men",
         "ru": "я, меня",
         "tj": "ман"},
        {"no": 5, "zh": "是",   "pinyin": "shì",      "pos": "v.",
         "uz": "bo'lmoq (=)",
         "ru": "быть, являться (=)",
         "tj": "будан (=)"},
        {"no": 6, "zh": "老师", "pinyin": "lǎoshī",   "pos": "n.",
         "uz": "o'qituvchi, muallim",
         "ru": "учитель, преподаватель",
         "tj": "муаллим, омӯзгор"},
        {"no": 7, "zh": "吗",   "pinyin": "ma",       "pos": "part.",
         "uz": "so'roq yuklamasi",
         "ru": "вопросительная частица",
         "tj": "ҳарфи саволӣ"},
        {"no": 8, "zh": "学生", "pinyin": "xuésheng", "pos": "n.",
         "uz": "o'quvchi, talaba",
         "ru": "ученик, студент",
         "tj": "хонанда, донишҷӯ"},
        {"no": 9, "zh": "人",   "pinyin": "rén",      "pos": "n.",
         "uz": "inson, odam",
         "ru": "человек, люди",
         "tj": "одам, инсон"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Maktabda — ism so'rash",
            "scene_ru": "В школе — спрашиваем имя",
            "scene_tj": "Дар мактаб — пурсидани ном",
            "dialogue": [
                {"speaker": "A", "zh": "你叫什么名字？",  "pinyin": "Nǐ jiào shénme míngzi?",
                 "uz": "Ismingiz nima?",
                 "ru": "Как вас зовут?",
                 "tj": "Номи шумо чист?"},
                {"speaker": "B", "zh": "我叫李月。",      "pinyin": "Wǒ jiào Lǐ Yuè.",
                 "uz": "Mening ismim Li Yue.",
                 "ru": "Меня зовут Ли Юэ.",
                 "tj": "Номи ман Ли Юэ аст."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Sinfda — kasb so'rash",
            "scene_ru": "В классе — спрашиваем профессию",
            "scene_tj": "Дар синф — пурсидани касб",
            "dialogue": [
                {"speaker": "A", "zh": "你是老师吗？",          "pinyin": "Nǐ shì lǎoshī ma?",
                 "uz": "Siz o'qituvchimisiz?",
                 "ru": "Вы учитель?",
                 "tj": "Оё шумо муаллим ҳастед?"},
                {"speaker": "B", "zh": "我不是老师，我是学生。", "pinyin": "Wǒ bú shì lǎoshī, wǒ shì xuésheng.",
                 "uz": "Men o'qituvchi emasman, men talabaman.",
                 "ru": "Я не учитель, я студент.",
                 "tj": "Ман муаллим нестам, ман донишҷӯ ҳастам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Maktabda — millat so'rash",
            "scene_ru": "В школе — спрашиваем национальность",
            "scene_tj": "Дар мактаб — пурсидани миллат",
            "dialogue": [
                {"speaker": "A", "zh": "你是中国人吗？",           "pinyin": "Nǐ shì Zhōngguó rén ma?",
                 "uz": "Siz xitoylikmisiz?",
                 "ru": "Вы китаец/китаянка?",
                 "tj": "Оё шумо хитоӣ ҳастед?"},
                {"speaker": "B", "zh": "我不是中国人，我是美国人。", "pinyin": "Wǒ bú shì Zhōngguó rén, wǒ shì Měiguó rén.",
                 "uz": "Men xitoylik emasman, men amerikalikman.",
                 "ru": "Я не китаец, я американец.",
                 "tj": "Ман хитоӣ нестам, ман амрикоӣ ҳастам."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "是字句",
            "title_uz": "是 bilan tuzilgan gap",
            "title_ru": "Предложения с 是",
            "title_tj": "Ҷумлаҳо бо 是",
            "rule_uz": (
                "是(shì) — tenglikni ifodalaydi (= bo'lmoq).\n"
                "Tuzilma: Ega + 是 + Ot/Ot birikmasi\n"
                "Inkor: Ega + 不是 + Ot/Ot birikmasi\n\n"
                "Misol:\n"
                "我是老师。— Men o'qituvchiman.\n"
                "我不是老师。— Men o'qituvchi emasman.\n"
                "李月是中国人。— Li Yue xitoylik."
            ),
            "rule_ru": (
                "是(shì) — выражает равенство (= являться).\n"
                "Структура: Подлежащее + 是 + Существительное/Именная группа\n"
                "Отрицание: Подлежащее + 不是 + Существительное/Именная группа\n\n"
                "Пример:\n"
                "我是老师。— Я учитель.\n"
                "我不是老师。— Я не учитель.\n"
                "李月是中国人。— Ли Юэ китаянка."
            ),
            "rule_tj": (
                "是(shì) — баробариро ифода мекунад (= будан).\n"
                "Сохтор: Мубтадо + 是 + Исм/Гурӯҳи исмӣ\n"
                "Инкор: Мубтадо + 不是 + Исм/Гурӯҳи исмӣ\n\n"
                "Мисол:\n"
                "我是老师。— Ман муаллим ҳастам.\n"
                "我不是老师。— Ман муаллим нестам.\n"
                "李月是中国人。— Ли Юэ хитоӣ аст."
            ),
            "examples": [
                {"zh": "我是学生。",     "pinyin": "Wǒ shì xuésheng.",
                 "uz": "Men talabaman.", "ru": "Я студент.", "tj": "Ман донишҷӯ ҳастам."},
                {"zh": "我不是老师。",   "pinyin": "Wǒ bú shì lǎoshī.",
                 "uz": "Men o'qituvchi emasman.", "ru": "Я не учитель.", "tj": "Ман муаллим нестам."},
                {"zh": "她是中国人。",   "pinyin": "Tā shì Zhōngguó rén.",
                 "uz": "U xitoylik (ayol).", "ru": "Она китаянка.", "tj": "Вай хитоӣ аст (зан)."},
            ]
        },
        {
            "no": 2,
            "title_zh": "吗 — so'roq gapi",
            "title_uz": "吗 — so'roq yuklamasi",
            "title_ru": "吗 — вопросительная частица",
            "title_tj": "吗 — ҳарфи саволӣ",
            "rule_uz": (
                "吗(ma) — gap oxiriga qo'yilsa, uni ha/yo'q savoliga aylantiradi.\n"
                "Tuzilma: Gap + 吗？\n\n"
                "Misol:\n"
                "你是老师。→ 你是老师吗？\n"
                "Siz o'qituvchisiz. → Siz o'qituvchimisiz?\n\n"
                "Javob: 是 (ha) yoki 不是 (yo'q)"
            ),
            "rule_ru": (
                "吗(ma) — ставится в конце предложения, превращая его в вопрос «да/нет».\n"
                "Структура: Утверждение + 吗？\n\n"
                "Пример:\n"
                "你是老师。→ 你是老师吗？\n"
                "Ты учитель. → Ты учитель?\n\n"
                "Ответ: 是 (да) или 不是 (нет)"
            ),
            "rule_tj": (
                "吗(ma) — дар охири ҷумла гузошта, онро ба савол «бале/не» табдил медиҳад.\n"
                "Сохтор: Изҳор + 吗？\n\n"
                "Мисол:\n"
                "你是老师。→ 你是老师吗？\n"
                "Шумо муаллим ҳастед. → Оё шумо муаллим ҳастед?\n\n"
                "Ҷавоб: 是 (бале) ё 不是 (не)"
            ),
            "examples": [
                {"zh": "你是学生吗？",   "pinyin": "Nǐ shì xuésheng ma?",
                 "uz": "Siz talabamisisz?", "ru": "Вы студент?", "tj": "Оё шумо донишҷӯ ҳастед?"},
                {"zh": "你是美国人吗？", "pinyin": "Nǐ shì Měiguó rén ma?",
                 "uz": "Siz amerikalikmisiniz?", "ru": "Вы американец?", "tj": "Оё шумо амрикоӣ ҳастед?"},
                {"zh": "你叫李月吗？",   "pinyin": "Nǐ jiào Lǐ Yuè ma?",
                 "uz": "Ismingiz Li Yuemi?", "ru": "Вас зовут Ли Юэ?", "tj": "Оё номи шумо Ли Юэ аст?"},
            ]
        },
        {
            "no": 3,
            "title_zh": "什么 — so'roq olmoshi",
            "title_uz": "什么 — so'roq olmoshi",
            "title_ru": "什么 — вопросительное местоимение",
            "title_tj": "什么 — ҷонишини саволӣ",
            "rule_uz": (
                "什么(shénme) — 'nima', 'qaysi' ma'nosini bildiradi.\n"
                "Oxiriga 吗 qo'shmang — 什么 o'zi savolni ifodalaydi.\n\n"
                "Misol:\n"
                "你叫什么名字？— Ismingiz nima?\n"
                "这是什么？— Bu nima?\n"
                "你是什么人？— Siz kimsiz?"
            ),
            "rule_ru": (
                "什么(shénme) — означает «что», «какой».\n"
                "Не добавляйте 吗 в конце — 什么 само делает предложение вопросительным.\n\n"
                "Пример:\n"
                "你叫什么名字？— Как вас зовут?\n"
                "这是什么？— Что это?\n"
                "你是什么人？— Кто вы?"
            ),
            "rule_tj": (
                "什么(shénme) — маънои «чӣ», «кадом» дорад.\n"
                "吗 -ро дар охир илова накунед — 什么 худ ҷумларо саволӣ мекунад.\n\n"
                "Мисол:\n"
                "你叫什么名字？— Номи шумо чист?\n"
                "这是什么？— Ин чист?\n"
                "你是什么人？— Шумо кӣ ҳастед?"
            ),
            "examples": [
                {"zh": "你叫什么名字？", "pinyin": "Nǐ jiào shénme míngzi?",
                 "uz": "Ismingiz nima?", "ru": "Как вас зовут?", "tj": "Номи шумо чист?"},
                {"zh": "这是什么？",     "pinyin": "Zhè shì shénme?",
                 "uz": "Bu nima?", "ru": "Что это?", "tj": "Ин чист?"},
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
                {"prompt_uz": "Ismingiz nima?", "prompt_ru": "Как вас зовут?", "prompt_tj": "Номи шумо чист?", "answer": "你叫什么名字？", "pinyin": "Nǐ jiào shénme míngzi?"},
                {"prompt_uz": "Mening ismim Van Fan.", "prompt_ru": "Меня зовут Ван Фан.", "prompt_tj": "Номи ман Ван Фан аст.", "answer": "我叫王芳。", "pinyin": "Wǒ jiào Wáng Fāng."},
                {"prompt_uz": "Siz o'qituvchimisiz?", "prompt_ru": "Вы учитель?", "prompt_tj": "Оё шумо муаллим ҳастед?", "answer": "你是老师吗？", "pinyin": "Nǐ shì lǎoshī ma?"},
                {"prompt_uz": "Men talabaman.", "prompt_ru": "Я студент.", "prompt_tj": "Ман донишҷӯ ҳастам.", "answer": "我是学生。", "pinyin": "Wǒ shì xuésheng."},
                {"prompt_uz": "Men xitoylik emasman, men amerikalikman.", "prompt_ru": "Я не китаец, я американец.", "prompt_tj": "Ман хитоӣ нестам, ман амрикоӣ ҳастам.", "answer": "我不是中国人，我是美国人。", "pinyin": "Wǒ bú shì Zhōngguó rén, wǒ shì Měiguó rén."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холиро пур кунед:",
            "items": [
                {"prompt_uz": "A: 你叫___名字？  B: 我叫李月。", "prompt_ru": "A: 你叫___名字？  B: 我叫李月。", "prompt_tj": "A: 你叫___名字？  B: 我叫李月。", "answer": "什么", "pinyin": "shénme"},
                {"prompt_uz": "A: 你___老师吗？  B: 是，我是老师。", "prompt_ru": "A: 你___老师吗？  B: 是，我是老师。", "prompt_tj": "A: 你___老师吗？  B: 是，我是老师。", "answer": "是", "pinyin": "shì"},
                {"prompt_uz": "A: 你是中国人___？ B: 不是，我是美国人。", "prompt_ru": "A: 你是中国人___？ B: 不是，我是美国人。", "prompt_tj": "A: 你是中国人___？ B: 不是，我是美国人。", "answer": "吗", "pinyin": "ma"},
                {"prompt_uz": "我不___老师，我是学生。", "prompt_ru": "我不___老师，我是学生。", "prompt_tj": "我不___老师，我是学生。", "answer": "是", "pinyin": "shì"},
            ]
        },
        {
            "no": 3,
            "type": "make_question",
            "instruction_uz": "吗 yordamida savol tuzing:",
            "instruction_ru": "Превратите в вопрос с помощью 吗:",
            "instruction_tj": "Бо ёрии 吗 саволе созед:",
            "items": [
                {"prompt_uz": "你是学生。", "prompt_ru": "你是学生。", "prompt_tj": "你是学生。", "answer": "你是学生吗？", "pinyin": "Nǐ shì xuésheng ma?"},
                {"prompt_uz": "他是中国人。", "prompt_ru": "他是中国人。", "prompt_tj": "他是中国人。", "answer": "他是中国人吗？", "pinyin": "Tā shì Zhōngguó rén ma?"},
                {"prompt_uz": "她叫李月。", "prompt_ru": "她叫李月。", "prompt_tj": "她叫李月。", "answer": "她叫李月吗？", "pinyin": "Tā jiào Lǐ Yuè ma?"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["你叫什么名字？", "我叫王芳。", "你是老师吗？", "我是学生。", "我不是中国人，我是美国人。"]},
        {"no": 2, "answers": ["什么", "是", "吗", "是"]},
        {"no": 3, "answers": ["你是学生吗？", "他是中国人吗？", "她叫李月吗？"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "O'zingiz haqingizda 3 ta gap yozing (ism, millat, kasb):",
            "instruction_ru": "Напишите 3 предложения о себе (имя, национальность, профессия):",
            "instruction_tj": "Дар бораи худатон 3 ҷумла нависед (исм, миллат, касб):",
            "example": "我叫___。我是___人。我是___。",
            "words": ["叫", "是", "不是", "老师", "学生", "中国人", "美国人"],
        },
        {
            "no": 2,
            "instruction_uz": "Quyidagi gaplarni 吗 yordamida savol jumlaga aylantiring:",
            "instruction_ru": "Превратите следующие предложения в вопросы с 吗:",
            "instruction_tj": "Ҷумлаҳои зеринро бо 吗 ба савол табдил диҳед:",
            "items": [
                {"prompt_uz": "你是老师。", "prompt_ru": "你是老师。", "prompt_tj": "你是老师。", "answer": "你是老师吗？"},
                {"prompt_uz": "他叫大卫。", "prompt_ru": "他叫大卫。", "prompt_tj": "他叫大卫。", "answer": "他叫大卫吗？"},
                {"prompt_uz": "她是美国人。", "prompt_ru": "她是美国人。", "prompt_tj": "她是美国人。", "answer": "她是美国人吗？"},
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
