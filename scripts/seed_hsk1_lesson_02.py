import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 2,
    "lesson_code": "HSK1-L02",
    "title": "谢谢你",
    "goal": json.dumps({
        "uz": "Xitoycha minnatdorchilik bildirish va xayrlashishni o'rganing",
        "ru": "Научитесь выражать благодарность и прощаться по-китайски",
        "tj": "Омӯзед, ки чӣ тавр ба забони чинӣ сипосгузорӣ кунед ва хайр гӯед",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Ikkinchi darsda siz xitoycha minnatdorchilik bildirish va xayrlashishni o'rganasiz. 4 ta yangi so'z, 3 ta dialog va neytral ton qoidalari.",
        "ru": "На втором уроке вы научитесь выражать благодарность и прощаться по-китайски. 4 новых слова, 3 диалога и правила нейтрального тона.",
        "tj": "Дар дарси дуюм шумо сипосгузорӣ кардан ва хайр гуфтанро меомӯзед. 4 калимаи нав, 3 муколама ва қоидаҳои садои бетараф.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "谢谢",   "pinyin": "xièxie",  "pos": "v.",
         "uz": "rahmat aytmoq, rahmat",
         "ru": "благодарить, спасибо",
         "tj": "ташаккур гуфтан, раҳмат"},
        {"no": 2, "zh": "不",     "pinyin": "bù",       "pos": "adv.",
         "uz": "yo'q, emas",
         "ru": "нет, не",
         "tj": "не, нест"},
        {"no": 3, "zh": "不客气", "pinyin": "bú kèqi",  "pos": "expr.",
         "uz": "iltimos, muammo yo'q",
         "ru": "пожалуйста, не за что",
         "tj": "хоҳиш мекунам, мушкиле нест"},
        {"no": 4, "zh": "再见",   "pinyin": "zàijiàn",  "pos": "v.",
         "uz": "xayr, ko'rishguncha",
         "ru": "до свидания, пока",
         "tj": "хайр, то дидан"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Yordam uchun rahmat",
            "scene_ru": "Благодарность за помощь",
            "scene_tj": "Ташаккур барои ёрӣ",
            "dialogue": [
                {"speaker": "A", "zh": "谢谢！", "pinyin": "Xièxie!",
                 "uz": "Rahmat!",
                 "ru": "Спасибо!",
                 "tj": "Раҳмат!"},
                {"speaker": "B", "zh": "不谢！", "pinyin": "Bú xiè!",
                 "uz": "Iltimos!",
                 "ru": "Пожалуйста!",
                 "tj": "Хоҳиш мекунам!"},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Rasmiy rahmat",
            "scene_ru": "Официальная благодарность",
            "scene_tj": "Ташаккури расмӣ",
            "dialogue": [
                {"speaker": "A", "zh": "谢谢你！", "pinyin": "Xièxie nǐ!",
                 "uz": "Senga rahmat!",
                 "ru": "Спасибо тебе!",
                 "tj": "Аз ту ташаккур!"},
                {"speaker": "B", "zh": "不客气！", "pinyin": "Bú kèqi!",
                 "uz": "Iltimos (muammo yo'q)!",
                 "ru": "Не за что!",
                 "tj": "Хоҳиш мекунам!"},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Xayrlashuv",
            "scene_ru": "Прощание",
            "scene_tj": "Хайр гуфтан",
            "dialogue": [
                {"speaker": "A", "zh": "再见！", "pinyin": "Zàijiàn!",
                 "uz": "Xayr!",
                 "ru": "До свидания!",
                 "tj": "Хайр!"},
                {"speaker": "B", "zh": "再见！", "pinyin": "Zàijiàn!",
                 "uz": "Xayr!",
                 "ru": "До свидания!",
                 "tj": "Хайр!"},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "不 — inkor yuklamasi",
            "title_uz": "不 — inkor yuklamasi",
            "title_ru": "不 — отрицательная частица",
            "title_tj": "不 — ҳарфи инкорӣ",
            "rule_uz": (
                "不(bù) — inkor yuklamasi (yo'q, emas).\n"
                "Diqqat: 不 4-ton, lekin keyingi bo'g'in ham 4-ton bo'lsa, 2-tonga o'zgaradi.\n"
                "bù + 4-ton → bú + 4-ton\n"
                "Misol: 不客气 → bú kèqi\n"
                "不谢 → bú xiè"
            ),
            "rule_ru": (
                "不(bù) — отрицательная частица (нет, не).\n"
                "Примечание: 不 имеет 4-й тон, но меняется на 2-й перед другим слогом 4-го тона.\n"
                "bù + 4-й тон → bú + 4-й тон\n"
                "Пример: 不客气 → bú kèqi\n"
                "不谢 → bú xiè"
            ),
            "rule_tj": (
                "不(bù) — ҳарфи инкорӣ (не, нест).\n"
                "Диққат: 不 садои 4-ум дорад, аммо агар ҳиҷои баъдӣ ҳам садои 4-ум бошад, ба садои 2-юм иваз мешавад.\n"
                "bù + садои 4 → bú + садои 4\n"
                "Мисол: 不客气 → bú kèqi\n"
                "不谢 → bú xiè"
            ),
            "examples": [
                {"zh": "不谢",   "pinyin": "bú xiè",
                 "uz": "iltimos (so'zma-so'z: rahmat yo'q)", "ru": "пожалуйста (дословно: не благодари)", "tj": "хоҳиш мекунам"},
                {"zh": "不客气", "pinyin": "bú kèqi",
                 "uz": "iltimos, muammo yo'q", "ru": "не за что, пожалуйста", "tj": "хоҳиш мекунам, мушкиле нест"},
                {"zh": "不好",   "pinyin": "bù hǎo",
                 "uz": "yaxshi emas", "ru": "нехорошо, плохо", "tj": "хуб нест"},
            ]
        },
        {
            "no": 2,
            "title_zh": "轻声 — neytral ton",
            "title_uz": "轻声 — neytral ton",
            "title_ru": "轻声 — нейтральный тон",
            "title_tj": "轻声 — садои бетараф",
            "rule_uz": (
                "Xitoy tilida 5-ton ham bor — neytral ton (轻声).\n"
                "U qisqa va engil, ton belgisi yo'q.\n"
                "Ko'pincha qarindoshlik atamalarida uchraydi.\n"
                "Misol: 妈妈(māma), 爸爸(bàba), 爷爷(yéye), 奶奶(nǎinai)"
            ),
            "rule_ru": (
                "В китайском также есть 5-й тон — нейтральный (轻声).\n"
                "Он короткий и лёгкий, без знака тона.\n"
                "Часто встречается в терминах родства.\n"
                "Пример: 妈妈(māma), 爸爸(bàba), 爷爷(yéye), 奶奶(nǎinai)"
            ),
            "rule_tj": (
                "Дар забони чинӣ садои 5-ум ҳам вуҷуд дорад — садои бетараф (轻声).\n"
                "Он кӯтоҳ ва сабук аст, бе нишонаи садо.\n"
                "Бештар дар истилоҳоти хешутаборӣ истифода мешавад.\n"
                "Мисол: 妈妈(māma), 爸爸(bàba), 爷爷(yéye), 奶奶(nǎinai)"
            ),
            "examples": [
                {"zh": "妈妈", "pinyin": "māma",
                 "uz": "ona", "ru": "мама", "tj": "модар"},
                {"zh": "爸爸", "pinyin": "bàba",
                 "uz": "ota", "ru": "папа", "tj": "падар"},
                {"zh": "爷爷", "pinyin": "yéye",
                 "uz": "bobo (otaning otasi)", "ru": "дедушка (по отцу)", "tj": "бобои падарӣ"},
                {"zh": "奶奶", "pinyin": "nǎinai",
                 "uz": "buvi (otaning onasi)", "ru": "бабушка (по отцу)", "tj": "модарбузурги падарӣ"},
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
                {"prompt_uz": "Rahmat!", "prompt_ru": "Спасибо!", "prompt_tj": "Раҳмат!", "answer": "谢谢！", "pinyin": "Xièxie!"},
                {"prompt_uz": "Senga rahmat!", "prompt_ru": "Спасибо тебе!", "prompt_tj": "Аз ту ташаккур!", "answer": "谢谢你！", "pinyin": "Xièxie nǐ!"},
                {"prompt_uz": "Iltimos (muammo yo'q)!", "prompt_ru": "Не за что!", "prompt_tj": "Хоҳиш мекунам!", "answer": "不客气！", "pinyin": "Bú kèqi!"},
                {"prompt_uz": "Xayr!", "prompt_ru": "До свидания!", "prompt_tj": "Хайр!", "answer": "再见！", "pinyin": "Zàijiàn!"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холиро пур кунед:",
            "items": [
                {"prompt_uz": "A: 谢谢你！  B: ___！", "prompt_ru": "A: 谢谢你！  B: ___！", "prompt_tj": "A: 谢谢你！  B: ___！", "answer": "不客气", "pinyin": "bú kèqi"},
                {"prompt_uz": "A: ___！     B: 再见！", "prompt_ru": "A: ___！     B: 再见！", "prompt_tj": "A: ___！     B: 再见！", "answer": "再见", "pinyin": "zàijiàn"},
                {"prompt_uz": "A: 谢谢！    B: ___！", "prompt_ru": "A: 谢谢！    B: ___！", "prompt_tj": "A: 谢谢！    B: ___！", "answer": "不谢", "pinyin": "bú xiè"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["谢谢！", "谢谢你！", "不客气！", "再见！"]},
        {"no": 2, "answers": ["不客气", "再见", "不谢"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib 2 ta to'liq dialog yozing:",
            "instruction_ru": "Напишите 2 полных диалога, используя следующие слова:",
            "instruction_tj": "Бо истифодаи калимаҳои зерин 2 муколамаи пурра нависед:",
            "words": ["谢谢", "不客气", "再见", "你好"],
            "example": "A: 你好！... A: 谢谢！B: 不客气！再见！B: 再见！",
        },
        {
            "no": 2,
            "instruction_uz": "不 ning to'g'ri talaffuzini yozing (bù yoki bú):",
            "instruction_ru": "Напишите правильное произношение 不 (bù или bú):",
            "instruction_tj": "Талаффузи дурусти 不 -ро нависед (bù ё bú):",
            "items": [
                {"prompt_uz": "不好", "prompt_ru": "不好", "prompt_tj": "不好", "answer": "bù hǎo"},
                {"prompt_uz": "不谢", "prompt_ru": "不谢", "prompt_tj": "不谢", "answer": "bú xiè"},
                {"prompt_uz": "不客气", "prompt_ru": "不客气", "prompt_tj": "不客气", "answer": "bú kèqi"},
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
