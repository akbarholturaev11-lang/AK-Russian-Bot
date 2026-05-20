import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 1,
    "lesson_code": "HSK1-L01",
    "title": "你好",
    "goal": json.dumps({
        "uz": "Xitoycha salomlashish va uzr so'rashni o'rganing",
        "ru": "Научитесь здороваться и извиняться по-китайски",
        "tj": "Омӯзед, ки чӣ тавр ба забони чинӣ салом гӯед ва узр пурсед",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Birinchi darsda siz xitoycha salomlashishni o'rganasiz. Bu dars 6 ta yangi so'z, 3 ta dialog va asosiy talaffuz qoidalarini o'z ichiga oladi.",
        "ru": "На первом уроке вы научитесь китайским приветствиям. Урок включает 6 новых слов, 3 диалога и основные правила произношения.",
        "tj": "Дар дарси аввал шумо шиносоӣ бо хитоиро меомӯзед. Ин дарс 6 калимаи нав, 3 муколама ва қоидаҳои асосии талаффузро дар бар мегирад.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "你",    "pinyin": "nǐ",        "pos": "pron.",
         "uz": "sen (birlik)",
         "ru": "ты (единственное число)",
         "tj": "ту (яккашумора)"},
        {"no": 2, "zh": "好",    "pinyin": "hǎo",       "pos": "adj.",
         "uz": "yaxshi, ajoyib",
         "ru": "хорошо, хороший",
         "tj": "хуб, олӣ"},
        {"no": 3, "zh": "您",    "pinyin": "nín",       "pos": "pron.",
         "uz": "siz (rasmiy/hurmat)",
         "ru": "вы (вежливая форма)",
         "tj": "шумо (расмӣ/эҳтиромона)"},
        {"no": 4, "zh": "你们",  "pinyin": "nǐmen",     "pos": "pron.",
         "uz": "sizlar (ko'plik)",
         "ru": "вы (множественное число)",
         "tj": "шумоён (ҷамъшумора)"},
        {"no": 5, "zh": "对不起","pinyin": "duìbuqǐ",   "pos": "v.",
         "uz": "kechirasiz, uzr",
         "ru": "извините, прости",
         "tj": "бубахшед, узр"},
        {"no": 6, "zh": "没关系","pinyin": "méi guānxi","pos": "expr.",
         "uz": "hech gap emas, muammo yo'q",
         "ru": "ничего страшного, всё в порядке",
         "tj": "майлаш, мушкиле нест"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Tanishlar uchrashadi",
            "scene_ru": "Знакомые встречаются",
            "scene_tj": "Шиносон вомехӯранд",
            "dialogue": [
                {"speaker": "A", "zh": "你好！", "pinyin": "Nǐ hǎo!",
                 "uz": "Salom!",
                 "ru": "Привет!",
                 "tj": "Салом!"},
                {"speaker": "B", "zh": "你好！", "pinyin": "Nǐ hǎo!",
                 "uz": "Salom!",
                 "ru": "Привет!",
                 "tj": "Салом!"},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Hurmatli salomlashuv",
            "scene_ru": "Официальное приветствие",
            "scene_tj": "Салому алейки расмӣ",
            "dialogue": [
                {"speaker": "A", "zh": "您好！",   "pinyin": "Nín hǎo!",
                 "uz": "Salom (rasmiy)!",
                 "ru": "Здравствуйте!",
                 "tj": "Салом (расмӣ)!"},
                {"speaker": "B", "zh": "你们好！", "pinyin": "Nǐmen hǎo!",
                 "uz": "Hammangizga salom!",
                 "ru": "Здравствуйте все!",
                 "tj": "Ба ҳамаи шумо салом!"},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Kechirim so'rash",
            "scene_ru": "Извинение",
            "scene_tj": "Узрпурсӣ",
            "dialogue": [
                {"speaker": "A", "zh": "对不起！", "pinyin": "Duìbuqǐ!",
                 "uz": "Kechirasiz!",
                 "ru": "Извините!",
                 "tj": "Бубахшед!"},
                {"speaker": "B", "zh": "没关系！", "pinyin": "Méi guānxi!",
                 "uz": "Hech gap emas!",
                 "ru": "Ничего страшного!",
                 "tj": "Майлаш!"},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "四声",
            "title_uz": "To'rt ton",
            "title_ru": "Четыре тона",
            "title_tj": "Чор садо",
            "rule_uz": (
                "Xitoy tilida har bir bo'g'in 4 xil tonda aytiladi:\n"
                "1-ton (—): baland va tekis — mā (ona)\n"
                "2-ton (ˊ): ko'tariluvchi — má (kanop o'simligi)\n"
                "3-ton (ˇ): tushib ko'tariluvchi — mǎ (ot)\n"
                "4-ton (ˋ): tushuvchi — mà (so'kishmoq)\n\n"
                "Ton ma'noni o'zgartiradi!"
            ),
            "rule_ru": (
                "В китайском языке каждый слог произносится в одном из 4 тонов:\n"
                "Тон 1 (—): ровный и высокий — mā (мама)\n"
                "Тон 2 (ˊ): восходящий — má (конопля)\n"
                "Тон 3 (ˇ): нисходяще-восходящий — mǎ (лошадь)\n"
                "Тон 4 (ˋ): нисходящий — mà (ругать)\n\n"
                "Тон меняет смысл слова!"
            ),
            "rule_tj": (
                "Дар забони чинӣ ҳар як ҳиҷо бо яке аз 4 садо гуфта мешавад:\n"
                "Садои 1 (—): баланд ва ҳамвор — mā (модар)\n"
                "Садои 2 (ˊ): боравандаи — má (канабис)\n"
                "Садои 3 (ˇ): поинравандаю боравандаи — mǎ (асп)\n"
                "Садои 4 (ˋ): поинравандаи — mà (дашном додан)\n\n"
                "Садо маъноро тағйир медиҳад!"
            ),
            "examples": [
                {"zh": "妈", "pinyin": "mā",
                 "uz": "ona (1-ton)", "ru": "мама (1-й тон)", "tj": "модар (садои 1)"},
                {"zh": "马", "pinyin": "mǎ",
                 "uz": "ot (3-ton)", "ru": "лошадь (3-й тон)", "tj": "асп (садои 3)"},
                {"zh": "骂", "pinyin": "mà",
                 "uz": "so'kmoq (4-ton)", "ru": "ругать (4-й тон)", "tj": "дашном додан (садои 4)"},
            ]
        },
        {
            "no": 2,
            "title_zh": "变调 (3+3)",
            "title_uz": "Ton o'zgarishi (3+3)",
            "title_ru": "Изменение тона (3+3)",
            "title_tj": "Тағйири садо (3+3)",
            "rule_uz": (
                "Ketma-ket ikkita 3-ton kelganda, birinchisi 2-tonga o'zgaradi.\n"
                "3+3 → 2+3\n"
                "Misol: 你(nǐ) + 好(hǎo) → nī hǎo (lekin yoziladi: nǐ hǎo)"
            ),
            "rule_ru": (
                "Когда два слога 3-го тона идут подряд, первый меняется на 2-й тон.\n"
                "3+3 → 2+3\n"
                "Пример: 你(nǐ) + 好(hǎo) → nī hǎo (но пишется: nǐ hǎo)"
            ),
            "rule_tj": (
                "Вақте ки ду ҳиҷои садои 3 паи ҳам меоянд, аввалӣ ба садои 2 табдил меёбад.\n"
                "3+3 → 2+3\n"
                "Мисол: 你(nǐ) + 好(hǎo) → nī hǎo (аммо навишта мешавад: nǐ hǎo)"
            ),
            "examples": [
                {"zh": "你好", "pinyin": "nī hǎo → nǐ hǎo",
                 "uz": "salom (nǐ hǎo deb yoziladi)", "ru": "привет (пишется nǐ hǎo)", "tj": "салом (навишта мешавад nǐ hǎo)"},
                {"zh": "可以", "pinyin": "ké yǐ → kě yǐ",
                 "uz": "mumkin, bo'ladi", "ru": "можно, разрешено", "tj": "мумкин, иҷозат"},
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
                {"prompt_uz": "salom (norasmiy)", "prompt_ru": "привет (неформально)", "prompt_tj": "салом (ғайрирасмӣ)", "answer": "你好！", "pinyin": "Nǐ hǎo!"},
                {"prompt_uz": "salom (rasmiy)", "prompt_ru": "здравствуйте (официально)", "prompt_tj": "салом (расмӣ)", "answer": "您好！", "pinyin": "Nín hǎo!"},
                {"prompt_uz": "kechirasiz!", "prompt_ru": "извините!", "prompt_tj": "бубахшед!", "answer": "对不起！", "pinyin": "Duìbuqǐ!"},
                {"prompt_uz": "hech gap emas!", "prompt_ru": "ничего страшного!", "prompt_tj": "майлаш!", "answer": "没关系！", "pinyin": "Méi guānxi!"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холиро пур кунед:",
            "items": [
                {"prompt_uz": "A: 你___！  B: 你好！", "prompt_ru": "A: 你___！  B: 你好！", "prompt_tj": "A: 你___！  B: 你好！", "answer": "好", "pinyin": "hǎo"},
                {"prompt_uz": "A: 对不起！  B: ___！", "prompt_ru": "A: 对不起！  B: ___！", "prompt_tj": "A: 对不起！  B: ___！", "answer": "没关系", "pinyin": "méi guānxi"},
                {"prompt_uz": "Bir o'qituvchi ko'p o'quvchilarga: ___好！", "prompt_ru": "Учитель говорит многим ученикам: ___好！", "prompt_tj": "Муаллим ба хонандагони зиёд мегӯяд: ___好！", "answer": "你们", "pinyin": "nǐmen"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["你好！", "您好！", "对不起！", "没关系！"]},
        {"no": 2, "answers": ["好", "没关系", "你们"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib 2 ta dialog yozing:",
            "instruction_ru": "Напишите 2 диалога, используя следующие слова:",
            "instruction_tj": "Бо истифодаи калимаҳои зерин 2 муколама нависед:",
            "words": ["你好", "您好", "对不起", "没关系"],
            "example": "A: 对不起！B: 没关系！",
        },
        {
            "no": 2,
            "instruction_uz": "Tonlarni mashq qiling va baland ovozda ayting:",
            "instruction_ru": "Отработайте тоны и произнесите их вслух:",
            "instruction_tj": "Садоҳоро машқ кунед ва баланд гӯед:",
            "words": [
                {"zh": "妈", "pinyin": "mā", "uz": "ona", "ru": "мама", "tj": "модар"},
                {"zh": "马", "pinyin": "mǎ", "uz": "ot", "ru": "лошадь", "tj": "асп"},
                {"zh": "骂", "pinyin": "mà", "uz": "so'kmoq", "ru": "ругать", "tj": "дашном додан"},
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
