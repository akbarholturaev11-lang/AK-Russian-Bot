import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 4,
    "lesson_code": "HSK1-L04",
    "title": "她是我的汉语老师",
    "goal": json.dumps({
        "uz": "Uchinchi shaxslar haqida gapirish, 的 bilan egalikni ifodalash va 谁/哪 so'roq so'zlarini ishlatish",
        "ru": "Говорить о третьих лицах, выражать принадлежность с 的 и использовать вопросительные слова 谁/哪",
        "tj": "Дар бораи шахсони сеюм гап задан, ифодаи моликият бо 的 ва истифодаи калимаҳои саволии 谁/哪",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "To'rtinchi darsda siz uchinchi shaxslar (u/unlar) haqida gapirish, 的 yuklamasi orqali egalikni ifodalash va 谁/哪 so'roq so'zlarini ishlatishni o'rganasiz. 10 ta yangi so'z, 3 ta dialog.",
        "ru": "На четвёртом уроке вы научитесь говорить о третьих лицах (он/она), выражать принадлежность с помощью частицы 的 и использовать вопросительные слова 谁/哪. 10 новых слов, 3 диалога.",
        "tj": "Дар дарси чорум шумо дар бораи шахсони сеюм (вай/ӯ) гап задан, ифодаи моликият бо ёрии ҳарфи 的 ва истифодаи калимаҳои саволии 谁/哪 -ро меомӯзед. 10 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "她",   "pinyin": "tā",      "pos": "pron.",
         "uz": "u (ayol)",
         "ru": "она",
         "tj": "вай (зан)"},
        {"no": 2,  "zh": "谁",   "pinyin": "shéi",    "pos": "pron.",
         "uz": "kim",
         "ru": "кто",
         "tj": "кӣ"},
        {"no": 3,  "zh": "的",   "pinyin": "de",      "pos": "part.",
         "uz": "ning (egalik yuklamasi)",
         "ru": "-'s (показатель принадлежности)",
         "tj": "и, -и (ҳарфи моликият)"},
        {"no": 4,  "zh": "汉语", "pinyin": "Hànyǔ",   "pos": "n.",
         "uz": "xitoy tili",
         "ru": "китайский язык",
         "tj": "забони чинӣ"},
        {"no": 5,  "zh": "哪",   "pinyin": "nǎ",      "pos": "pron.",
         "uz": "qaysi, qayerdan",
         "ru": "который, откуда",
         "tj": "кадом, аз куҷо"},
        {"no": 6,  "zh": "国",   "pinyin": "guó",     "pos": "n.",
         "uz": "davlat, mamlakat",
         "ru": "страна, государство",
         "tj": "кишвар, давлат"},
        {"no": 7,  "zh": "呢",   "pinyin": "ne",      "pos": "part.",
         "uz": "xo'sh, -chi (qaytarma savol)",
         "ru": "а, ну а (уточняющий вопрос)",
         "tj": "чӣ (савол бозгашт)"},
        {"no": 8,  "zh": "他",   "pinyin": "tā",      "pos": "pron.",
         "uz": "u (erkak)",
         "ru": "он",
         "tj": "вай (мард)"},
        {"no": 9,  "zh": "同学", "pinyin": "tóngxué", "pos": "n.",
         "uz": "sinfdosh, o'rtoq",
         "ru": "одноклассник, однокурсник",
         "tj": "ҳамсинф, ҳамдарс"},
        {"no": 10, "zh": "朋友", "pinyin": "péngyou", "pos": "n.",
         "uz": "do'st",
         "ru": "друг, подруга",
         "tj": "дӯст"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Sinfda — o'qituvchi haqida",
            "scene_ru": "В классе — о преподавателе",
            "scene_tj": "Дар синф — дар бораи муаллим",
            "dialogue": [
                {"speaker": "A", "zh": "她是谁？",              "pinyin": "Tā shì shéi?",
                 "uz": "U kim?",
                 "ru": "Кто она?",
                 "tj": "Вай кӣ аст?"},
                {"speaker": "B", "zh": "她是我的汉语老师，她叫李月。", "pinyin": "Tā shì wǒ de Hànyǔ lǎoshī, tā jiào Lǐ Yuè.",
                 "uz": "U mening xitoy tili o'qituvchim, uning ismi Li Yue.",
                 "ru": "Она моя преподаватель китайского, её зовут Ли Юэ.",
                 "tj": "Вай муаллимаи забони чинии ман аст, номаш Ли Юэ аст."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Kutubxonada — millat so'rash",
            "scene_ru": "В библиотеке — спрашиваем о национальности",
            "scene_tj": "Дар китобхона — пурсидани миллат",
            "dialogue": [
                {"speaker": "A", "zh": "你是哪国人？",    "pinyin": "Nǐ shì nǎ guó rén?",
                 "uz": "Siz qaysi mamlakatdansiz?",
                 "ru": "Вы из какой страны?",
                 "tj": "Шумо аз кадом кишвар ҳастед?"},
                {"speaker": "B", "zh": "我是美国人。你呢？","pinyin": "Wǒ shì Měiguó rén. Nǐ ne?",
                 "uz": "Men amerikalikman. Siz-chi?",
                 "ru": "Я американец. А вы?",
                 "tj": "Ман амрикоӣ ҳастам. Шумо чӣ?"},
                {"speaker": "A", "zh": "我是中国人。",    "pinyin": "Wǒ shì Zhōngguó rén.",
                 "uz": "Men xitoylikman.",
                 "ru": "Я китаец.",
                 "tj": "Ман хитоӣ ҳастам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Fotoda — do'st va sinfdosh",
            "scene_ru": "На фото — друг и одноклассник",
            "scene_tj": "Дар акс — дӯст ва ҳамсинф",
            "dialogue": [
                {"speaker": "A", "zh": "他是谁？",                "pinyin": "Tā shì shéi?",
                 "uz": "U kim?",
                 "ru": "Кто он?",
                 "tj": "Вай кӣ аст?"},
                {"speaker": "B", "zh": "他是我同学。",             "pinyin": "Tā shì wǒ tóngxué.",
                 "uz": "U mening sinfdoshim.",
                 "ru": "Он мой одноклассник.",
                 "tj": "Вай ҳамсинфи ман аст."},
                {"speaker": "A", "zh": "她呢？她是你同学吗？",     "pinyin": "Tā ne? Tā shì nǐ tóngxué ma?",
                 "uz": "U-chi? U ham sening sinfdoshing?",
                 "ru": "А она? Она тоже твой одноклассник?",
                 "tj": "Вай чӣ? Оё вай ҳам ҳамсинфи ту аст?"},
                {"speaker": "B", "zh": "她不是我同学，她是我朋友。","pinyin": "Tā bú shì wǒ tóngxué, tā shì wǒ péngyou.",
                 "uz": "U mening sinfdoshim emas, u mening do'stim.",
                 "ru": "Она не моя одноклассница, она моя подруга.",
                 "tj": "Вай ҳамсинфи ман нест, вай дӯсти ман аст."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "结构助词 的",
            "title_uz": "的 — egalik yuklamasi",
            "title_ru": "的 — показатель принадлежности",
            "title_tj": "的 — ҳарфи моликият",
            "rule_uz": (
                "的(de) — egalikni yoki bog'liqlikni ifodalaydi.\n"
                "Tuzilma: Ot/Olmosh + 的 + Ot\n\n"
                "Misol:\n"
                "我的老师 — mening o'qituvchim\n"
                "她的朋友 — uning do'sti\n\n"
                "Eslatma: Qarindoshlik va shaxsiy otlar oldida 的 tushirilishi mumkin:\n"
                "我(的)老师 ✓ — mening o'qituvchim\n"
                "我(的)朋友 ✓ — mening do'stim"
            ),
            "rule_ru": (
                "的(de) — выражает принадлежность или ассоциацию.\n"
                "Структура: Существительное/Местоимение + 的 + Существительное\n\n"
                "Пример:\n"
                "我的老师 — мой учитель\n"
                "她的朋友 — её подруга\n\n"
                "Примечание: 的 может опускаться перед терминами родства и личными существительными:\n"
                "我(的)老师 ✓ — мой учитель\n"
                "我(的)朋友 ✓ — мой друг"
            ),
            "rule_tj": (
                "的(de) — моликият ё алоқаро ифода мекунад.\n"
                "Сохтор: Исм/Ҷонишин + 的 + Исм\n\n"
                "Мисол:\n"
                "我的老师 — муаллими ман\n"
                "她的朋友 — дӯсти вай\n\n"
                "Эзоҳ: 的 пеш аз истилоҳоти хешутаборӣ ва исмҳои шахсӣ метавонад ҳазф шавад:\n"
                "我(的)老师 ✓ — муаллими ман\n"
                "我(的)朋友 ✓ — дӯсти ман"
            ),
            "examples": [
                {"zh": "我的汉语老师",   "pinyin": "wǒ de Hànyǔ lǎoshī",
                 "uz": "mening xitoy tili o'qituvchim", "ru": "мой преподаватель китайского", "tj": "муаллими забони чинии ман"},
                {"zh": "他的同学",       "pinyin": "tā de tóngxué",
                 "uz": "uning sinfdoshi", "ru": "его одноклассник", "tj": "ҳамсинфи вай"},
                {"zh": "你的朋友",       "pinyin": "nǐ de péngyou",
                 "uz": "sening do'sting", "ru": "твой друг", "tj": "дӯсти ту"},
            ]
        },
        {
            "no": 2,
            "title_zh": "谁 — kim so'roq olmoshi",
            "title_uz": "谁 — 'kim' so'roq olmoshi",
            "title_ru": "谁 — вопросительное местоимение «кто»",
            "title_tj": "谁 — ҷонишини саволии «кӣ»",
            "rule_uz": (
                "谁(shéi) — 'kim?' ma'nosini bildiradi.\n"
                "Gap ega yoki to'ldiruvchi bo'lib kelishi mumkin.\n\n"
                "Misol:\n"
                "她是谁？— U kim?\n"
                "谁是老师？— Kim o'qituvchi?\n"
                "他是谁的朋友？— U kimning do'sti?"
            ),
            "rule_ru": (
                "谁(shéi) — означает «кто?».\n"
                "Может выступать подлежащим или дополнением.\n\n"
                "Пример:\n"
                "她是谁？— Кто она?\n"
                "谁是老师？— Кто учитель?\n"
                "他是谁的朋友？— Чей он друг?"
            ),
            "rule_tj": (
                "谁(shéi) — маънои «кӣ?» дорад.\n"
                "Метавонад мубтадо ё пуркунанда бошад.\n\n"
                "Мисол:\n"
                "她是谁？— Вай кӣ аст?\n"
                "谁是老师？— Кӣ муаллим аст?\n"
                "他是谁的朋友？— Дӯсти кӣ аст вай?"
            ),
            "examples": [
                {"zh": "她是谁？",       "pinyin": "Tā shì shéi?",
                 "uz": "U kim?", "ru": "Кто она?", "tj": "Вай кӣ аст?"},
                {"zh": "谁是你的老师？", "pinyin": "Shéi shì nǐ de lǎoshī?",
                 "uz": "Kim sening o'qituvching?", "ru": "Кто твой учитель?", "tj": "Кӣ муаллими ту аст?"},
                {"zh": "他是谁的同学？", "pinyin": "Tā shì shéi de tóngxué?",
                 "uz": "U kimning sinfdoshi?", "ru": "Чей он одноклассник?", "tj": "Ҳамсинфи кӣ аст вай?"},
            ]
        },
        {
            "no": 3,
            "title_zh": "呢 — qaytarma savol yuklamasi",
            "title_uz": "呢 — qaytarma savol yuklamasi",
            "title_ru": "呢 — уточняющая частица",
            "title_tj": "呢 — ҳарфи савол бозгашт",
            "rule_uz": (
                "呢(ne) — oldingi gapda tilga olingan mavzu bo'yicha so'rashda ishlatiladi.\n"
                "Tuzilma: ...A... B呢？ (B-chi?)\n\n"
                "Misol:\n"
                "我是美国人。你呢？\n"
                "Men amerikalikman. Siz-chi?\n\n"
                "她叫李月。他呢？\n"
                "Uning ismi Li Yue. U-chi?"
            ),
            "rule_ru": (
                "呢(ne) — используется для вопроса о той же теме, упомянутой в предыдущем предложении.\n"
                "Структура: ...A... B呢？ (А как насчёт B?)\n\n"
                "Пример:\n"
                "我是美国人。你呢？\n"
                "Я американец. А вы?\n\n"
                "她叫李月。他呢？\n"
                "Её зовут Ли Юэ. А его?"
            ),
            "rule_tj": (
                "呢(ne) — барои пурсидан дар бораи мавзӯи қаблан зикршуда истифода мешавад.\n"
                "Сохтор: ...A... B呢？ (Чӣ дар бораи B?)\n\n"
                "Мисол:\n"
                "我是美国人。你呢？\n"
                "Ман амрикоӣ ҳастам. Шумо чӣ?\n\n"
                "她叫李月。他呢？\n"
                "Номаш Ли Юэ аст. Вай чӣ?"
            ),
            "examples": [
                {"zh": "我是学生。你呢？",  "pinyin": "Wǒ shì xuésheng. Nǐ ne?",
                 "uz": "Men talabaman. Siz-chi?", "ru": "Я студент. А вы?", "tj": "Ман донишҷӯ ҳастам. Шумо чӣ?"},
                {"zh": "她是中国人。他呢？","pinyin": "Tā shì Zhōngguó rén. Tā ne?",
                 "uz": "U xitoylik. U-chi?", "ru": "Она китаянка. А он?", "tj": "Вай хитоӣ аст. Вай чӣ?"},
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
                {"prompt_uz": "U kim (ayol)?", "prompt_ru": "Кто она?", "prompt_tj": "Вай кӣ аст (зан)?", "answer": "她是谁？", "pinyin": "Tā shì shéi?"},
                {"prompt_uz": "U mening xitoy tili o'qituvchim.", "prompt_ru": "Она моя преподаватель китайского.", "prompt_tj": "Вай муаллимаи забони чинии ман аст.", "answer": "她是我的汉语老师。", "pinyin": "Tā shì wǒ de Hànyǔ lǎoshī."},
                {"prompt_uz": "Siz qaysi mamlakatdansiz?", "prompt_ru": "Вы из какой страны?", "prompt_tj": "Шумо аз кадом кишвар ҳастед?", "answer": "你是哪国人？", "pinyin": "Nǐ shì nǎ guó rén?"},
                {"prompt_uz": "Men amerikalikman. Siz-chi?", "prompt_ru": "Я американец. А вы?", "prompt_tj": "Ман амрикоӣ ҳастам. Шумо чӣ?", "answer": "我是美国人。你呢？", "pinyin": "Wǒ shì Měiguó rén. Nǐ ne?"},
                {"prompt_uz": "U mening sinfdoshim emas, u mening do'stim.", "prompt_ru": "Он не мой одноклассник, он мой друг.", "prompt_tj": "Вай ҳамсинфи ман нест, вай дӯсти ман аст.", "answer": "他不是我同学，他是我朋友。", "pinyin": "Tā bú shì wǒ tóngxué, tā shì wǒ péngyou."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холиро пур кунед:",
            "items": [
                {"prompt_uz": "她是我___汉语老师。", "prompt_ru": "她是我___汉语老师。", "prompt_tj": "她是我___汉语老师。", "answer": "的", "pinyin": "de"},
                {"prompt_uz": "A: 他是___？  B: 他是我同学。", "prompt_ru": "A: 他是___？  B: 他是我同学。", "prompt_tj": "A: 他是___？  B: 他是我同学。", "answer": "谁", "pinyin": "shéi"},
                {"prompt_uz": "我是中国人。你___？", "prompt_ru": "我是中国人。你___？", "prompt_tj": "我是中国人。你___？", "answer": "呢", "pinyin": "ne"},
                {"prompt_uz": "你是___国人？", "prompt_ru": "你是___国人？", "prompt_tj": "你是___国人？", "answer": "哪", "pinyin": "nǎ"},
            ]
        },
        {
            "no": 3,
            "type": "make_sentence",
            "instruction_uz": "Berilgan so'zlardan gap tuzing:",
            "instruction_ru": "Составьте предложение из данных слов:",
            "instruction_tj": "Аз калимаҳои додашуда ҷумла созед:",
            "items": [
                {"words": ["她", "是", "我", "的", "朋友"], "answer": "她是我的朋友。", "pinyin": "Tā shì wǒ de péngyou."},
                {"words": ["他", "哪", "是", "国", "人"],   "answer": "他是哪国人？",   "pinyin": "Tā shì nǎ guó rén?"},
                {"words": ["谁", "你", "老师", "是", "的"], "answer": "谁是你的老师？", "pinyin": "Shéi shì nǐ de lǎoshī?"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["她是谁？", "她是我的汉语老师。", "你是哪国人？", "我是美国人。你呢？", "他不是我同学，他是我朋友。"]},
        {"no": 2, "answers": ["的", "谁", "呢", "哪"]},
        {"no": 3, "answers": ["她是我的朋友。", "他是哪国人？", "谁是你的老师？"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Do'stingiz haqida 4 ta gap yozing:",
            "instruction_ru": "Напишите 4 предложения о друге:",
            "instruction_tj": "Дар бораи дӯстатон 4 ҷумла нависед:",
            "template": "他/她叫___。他/她是___人。他/她是我的___。他/她是不是___？",
            "words": ["的", "同学", "朋友", "老师", "汉语老师"],
        },
        {
            "no": 2,
            "instruction_uz": "Quyidagi savollarga javob bering:",
            "instruction_ru": "Ответьте на следующие вопросы:",
            "instruction_tj": "Ба саволҳои зерин ҷавоб диҳед:",
            "items": [
                {"prompt_uz": "你的汉语老师是哪国人？", "prompt_ru": "你的汉语老师是哪国人？", "prompt_tj": "你的汉语老师是哪国人？",
                 "hint_uz": "Xitoy tili o'qituvchingiz qaysi mamlakatdan?", "hint_ru": "Из какой страны ваш преподаватель китайского?", "hint_tj": "Муаллими забони чинии шумо аз кадом кишвар аст?"},
                {"prompt_uz": "你的朋友叫什么名字？", "prompt_ru": "你的朋友叫什么名字？", "prompt_tj": "你的朋友叫什么名字？",
                 "hint_uz": "Do'stingizning ismi nima?", "hint_ru": "Как зовут вашего друга?", "hint_tj": "Дӯсти шумо чӣ ном дорад?"},
                {"prompt_uz": "他/她是你的同学吗？", "prompt_ru": "他/她是你的同学吗？", "prompt_tj": "他/她是你的同学吗？",
                 "hint_uz": "U sening sinfdoshing?", "hint_ru": "Он/она ваш одноклассник?", "hint_tj": "Оё вай ҳамсинфи шумо аст?"},
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
