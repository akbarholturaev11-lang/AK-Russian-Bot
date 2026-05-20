import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 7,
    "lesson_code": "HSK1-L07",
    "title": "今天几号",
    "goal": json.dumps({"uz": "Sanalar, haftaning kunlari va ketma-ket fe'l gaplarini o'rganish", "ru": "Изучение дат, дней недели и предложений с последовательными глаголами", "tj": "Омӯзиши санаҳо, рӯзҳои ҳафта ва ҷумлаҳо бо феъли пайдарпай"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Ettinchi darsda bugungi sanani, haftaning kunlarini va 去+joy+harakat konstruktsiyasini o'rganasiz. 12 ta yangi so'z, 3 ta suhbat.", "ru": "В седьмом уроке вы научитесь называть сегодняшнюю дату, дни недели и конструкцию 去+место+действие. 12 новых слов, 3 диалога.", "tj": "Дар дарси ҳафтум шумо санаи имрӯзро, рӯзҳои ҳафтаро ва сохтори 去+ҷой+амалро меомӯзед. 12 калимаи нав, 3 муколама."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "请",   "pinyin": "qǐng",    "pos": "v.",   "uz": "iltimos, marhamat",         "ru": "пожалуйста, разрешите спросить", "tj": "лутфан, иҷозат диҳед"},
        {"no": 2,  "zh": "问",   "pinyin": "wèn",     "pos": "v.",   "uz": "so'ramoq",                  "ru": "спрашивать",                     "tj": "пурсидан"},
        {"no": 3,  "zh": "今天", "pinyin": "jīntiān", "pos": "n.",   "uz": "bugun",                     "ru": "сегодня",                        "tj": "имрӯз"},
        {"no": 4,  "zh": "号",   "pinyin": "hào",     "pos": "n.",   "uz": "oy kuni (sana)",            "ru": "число (день месяца)",            "tj": "рӯзи моҳ (сана)"},
        {"no": 5,  "zh": "月",   "pinyin": "yuè",     "pos": "n.",   "uz": "oy (yanvar, fevral va h.k.)","ru": "месяц (январь, февраль и т.д.)", "tj": "моҳ (январ, феврал ва ғ.)"},
        {"no": 6,  "zh": "星期", "pinyin": "xīngqī",  "pos": "n.",   "uz": "hafta, haftaning kuni",     "ru": "неделя, день недели",            "tj": "ҳафта, рӯзи ҳафта"},
        {"no": 7,  "zh": "昨天", "pinyin": "zuótiān", "pos": "n.",   "uz": "kecha",                     "ru": "вчера",                          "tj": "дирӯз"},
        {"no": 8,  "zh": "明天", "pinyin": "míngtiān","pos": "n.",   "uz": "ertaga",                    "ru": "завтра",                         "tj": "фардо"},
        {"no": 9,  "zh": "去",   "pinyin": "qù",      "pos": "v.",   "uz": "bormoq",                    "ru": "идти, ехать",                    "tj": "рафтан"},
        {"no": 10, "zh": "学校", "pinyin": "xuéxiào", "pos": "n.",   "uz": "maktab",                    "ru": "школа",                          "tj": "мактаб"},
        {"no": 11, "zh": "看",   "pinyin": "kàn",     "pos": "v.",   "uz": "qaramoq, ko'rmoq, o'qimoq", "ru": "смотреть, читать",               "tj": "нигоҳ кардан, хондан"},
        {"no": 12, "zh": "书",   "pinyin": "shū",     "pos": "n.",   "uz": "kitob",                     "ru": "книга",                          "tj": "китоб"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Bankda — bugungi sana",
            "scene_ru": "В банке — сегодняшняя дата",
            "scene_tj": "Дар бонк — санаи имрӯз",
            "dialogue": [
                {"speaker": "A", "zh": "请问，今天几号？",  "pinyin": "Qǐngwèn, jīntiān jǐ hào?",  "uz": "Kechirasiz, bugun nechanchi sana?",    "ru": "Извините, какое сегодня число?",        "tj": "Бубахшед, имрӯз чанди сана аст?"},
                {"speaker": "B", "zh": "今天9月1号。",     "pinyin": "Jīntiān jiǔ yuè yī hào.",   "uz": "Bugun 1-sentabr.",                     "ru": "Сегодня 1 сентября.",                   "tj": "Имрӯз 1-уми сентябр аст."},
                {"speaker": "A", "zh": "今天星期几？",      "pinyin": "Jīntiān xīngqī jǐ?",        "uz": "Bugun haftaning nechanchi kuni?",      "ru": "Какой сегодня день недели?",            "tj": "Имрӯз кадом рӯзи ҳафта аст?"},
                {"speaker": "B", "zh": "星期三。",          "pinyin": "Xīngqī sān.",                "uz": "Chorshanba.",                          "ru": "Среда.",                                "tj": "Чоршанбе."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Taqvimga qarab — kecha va ertaga",
            "scene_ru": "По календарю — вчера и завтра",
            "scene_tj": "Тибқи тақвим — дирӯз ва фардо",
            "dialogue": [
                {"speaker": "A", "zh": "昨天是几月几号？",         "pinyin": "Zuótiān shì jǐ yuè jǐ hào?",          "uz": "Kecha nechanchi oy, nechanchi sana edi?",      "ru": "Какое число какого месяца было вчера?",             "tj": "Дирӯз чанди моҳ ва чанди сана буд?"},
                {"speaker": "B", "zh": "昨天是8月31号，星期二。",  "pinyin": "Zuótiān shì bā yuè sānshíyī hào, xīngqī èr.", "uz": "Kecha 31-avgust, seshanba edi.",          "ru": "Вчера было 31 августа, вторник.",                  "tj": "Дирӯз 31-уми август, сешанбе буд."},
                {"speaker": "A", "zh": "明天呢？",                 "pinyin": "Míngtiān ne?",                         "uz": "Ertaga-chi?",                                  "ru": "А завтра?",                                        "tj": "Фардо чӣ?"},
                {"speaker": "B", "zh": "明天是9月2号，星期四。",   "pinyin": "Míngtiān shì jiǔ yuè èr hào, xīngqī sì.", "uz": "Ertaga 2-sentabr, payshanba.",              "ru": "Завтра 2 сентября, четверг.",                      "tj": "Фардо 2-юми сентябр, панҷшанбе аст."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Qahvaxonada — ertangi reja",
            "scene_ru": "В кафе — планы на завтра",
            "scene_tj": "Дар қаҳвахона — нақшаи фардо",
            "dialogue": [
                {"speaker": "A", "zh": "明天星期六，你去学校吗？",  "pinyin": "Míngtiān xīngqī liù, nǐ qù xuéxiào ma?", "uz": "Ertaga shanba — maktabga borасанmi?",   "ru": "Завтра суббота — ты идёшь в школу?",       "tj": "Фардо шанбе — ту ба мактаб меравӣ?"},
                {"speaker": "B", "zh": "我去学校。",               "pinyin": "Wǒ qù xuéxiào.",                        "uz": "Men maktabga boraman.",                  "ru": "Я иду в школу.",                           "tj": "Ман ба мактаб мераваm."},
                {"speaker": "A", "zh": "你去学校做什么？",          "pinyin": "Nǐ qù xuéxiào zuò shénme?",            "uz": "Maktabga nima qilgani borasan?",         "ru": "Зачем ты идёшь в школу?",                  "tj": "Ту ба мактаб барои чӣ меравӣ?"},
                {"speaker": "B", "zh": "我去学校看书。",            "pinyin": "Wǒ qù xuéxiào kàn shū.",               "uz": "Men maktabga kitob o'qigani boraman.",  "ru": "Я иду в школу читать книги.",              "tj": "Ман ба мактаб рафта китоб мехонам."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "日期的表达 — Sana ifodalash",
            "title_uz": "Sanani ifodalash",
            "title_ru": "Выражение даты",
            "title_tj": "Ифодаи сана",
            "rule_uz": (
                "Xitoy tilida sanalar eng kattadan eng kichigiga qadar ifodalanadi:\n"
                "Yil → Oy → Kun → Haftaning kuni\n\n"
                "Oy: 一月 (yanvar) ~ 十二月 (dekabr)\n"
                "Kun: 1号 (1-chi) ~ 31号 (31-chi)\n\n"
                "Haftaning kunlari:\n"
                "星期一 Dushanba\n"
                "星期二 Seshanba\n"
                "星期三 Chorshanba\n"
                "星期四 Payshanba\n"
                "星期五 Juma\n"
                "星期六 Shanba\n"
                "星期日/星期天 Yakshanba\n\n"
                "Misol: 9月1号，星期三 — 1-sentabr, chorshanba"
            ),
            "rule_ru": (
                "В китайском языке даты выражаются от большего к меньшему:\n"
                "Год → Месяц → День → День недели\n\n"
                "Месяц: 一月 (январь) ~ 十二月 (декабрь)\n"
                "День: 1号 (1-е) ~ 31号 (31-е)\n\n"
                "Дни недели:\n"
                "星期一 Понедельник\n"
                "星期二 Вторник\n"
                "星期三 Среда\n"
                "星期四 Четверг\n"
                "星期五 Пятница\n"
                "星期六 Суббота\n"
                "星期日/星期天 Воскресенье\n\n"
                "Пример: 9月1号，星期三 — 1 сентября, среда"
            ),
            "rule_tj": (
                "Дар забони чинӣ санаҳо аз калон ба хурд ифода мешаванд:\n"
                "Сол → Моҳ → Рӯз → Рӯзи ҳафта\n\n"
                "Моҳ: 一月 (январ) ~ 十二月 (декабр)\n"
                "Рӯз: 1号 (1-ум) ~ 31号 (31-ум)\n\n"
                "Рӯзҳои ҳафта:\n"
                "星期一 Душанбе\n"
                "星期二 Сешанбе\n"
                "星期三 Чоршанбе\n"
                "星期四 Панҷшанбе\n"
                "星期五 Ҷумъа\n"
                "星期六 Шанбе\n"
                "星期日/星期天 Якшанбе\n\n"
                "Мисол: 9月1号，星期三 — 1-уми сентябр, чоршанбе"
            ),
            "examples": [
                {"zh": "今天9月1号，星期三。",  "pinyin": "Jīntiān jiǔ yuè yī hào, xīngqī sān.", "uz": "Bugun 1-sentabr, chorshanba.",         "ru": "Сегодня 1 сентября, среда.",           "tj": "Имрӯз 1-уми сентябр, чоршанбе."},
                {"zh": "明天星期六。",          "pinyin": "Míngtiān xīngqī liù.",                "uz": "Ertaga shanba.",                       "ru": "Завтра суббота.",                      "tj": "Фардо шанбе аст."},
                {"zh": "昨天8月31号。",         "pinyin": "Zuótiān bā yuè sānshíyī hào.",        "uz": "Kecha 31-avgust edi.",                 "ru": "Вчера было 31 августа.",               "tj": "Дирӯз 31-уми август буд."},
            ]
        },
        {
            "no": 2,
            "title_zh": "名词谓语句 — Ot kesimli gap",
            "title_uz": "Ot kesimli gap",
            "title_ru": "Предложение с именным сказуемым",
            "title_tj": "Ҷумлаи бо исми хабар",
            "rule_uz": (
                "Ot yoki raqam kesim bo'lib kela oladi (是 talab etilmaydi).\n"
                "Ko'pincha yosh, sana va vaqtni ifodalashda ishlatiladi.\n\n"
                "Misol:\n"
                "今天9月1号。— Bugun 1-sentabr. (9月1号 — ot kesim)\n"
                "明天星期三。— Ertaga chorshanba.\n"
                "我的汉语老师33岁。— Mening xitoy tili o'qituvchim 33 yoshda."
            ),
            "rule_ru": (
                "Существительное или числительное может выступать сказуемым (是 не требуется).\n"
                "Часто используется для выражения возраста, дат и времени.\n\n"
                "Пример:\n"
                "今天9月1号。— Сегодня 1 сентября. (9月1号 — именное сказуемое)\n"
                "明天星期三。— Завтра среда.\n"
                "我的汉语老师33岁。— Моему учителю китайского 33 года."
            ),
            "rule_tj": (
                "Исм ё рақам метавонад хабар бошад (是 лозим нест).\n"
                "Аксар вақт барои ифодаи синну сол, сана ва вақт истифода мешавад.\n\n"
                "Мисол:\n"
                "今天9月1号。— Имрӯз 1-уми сентябр аст. (9月1号 — хабари исмӣ)\n"
                "明天星期三。— Фардо чоршанбе аст.\n"
                "我的汉语老师33岁。— Устоди забони чинии ман 33 сола аст."
            ),
            "examples": [
                {"zh": "今天9月1号。",   "pinyin": "Jīntiān jiǔ yuè yī hào.",  "uz": "Bugun 1-sentabr.",               "ru": "Сегодня 1 сентября.",            "tj": "Имрӯз 1-уми сентябр аст."},
                {"zh": "明天星期三。",   "pinyin": "Míngtiān xīngqī sān.",     "uz": "Ertaga chorshanba.",             "ru": "Завтра среда.",                  "tj": "Фардо чоршанбе аст."},
                {"zh": "她今年二十岁。", "pinyin": "Tā jīnnián èrshí suì.",    "uz": "U bu yil yigirma yoshda.",       "ru": "Ей в этом году двадцать лет.",   "tj": "Вай имсол бист сола аст."},
            ]
        },
        {
            "no": 3,
            "title_zh": "连动句 — 去+joy+nima qilish",
            "title_uz": "Ketma-ket fe'l gapi: 去+joy+harakat",
            "title_ru": "Последовательный глагольный оборот: 去+место+действие",
            "title_tj": "Ҷумлаи пайдарпайи феълӣ: 去+ҷой+амал",
            "rule_uz": (
                "Ketma-ket fe'l gap: birinchi harakat ikkinchisining maqsadini bildiradi.\n"
                "Tuzilishi: Ega + 去 + Joy + Fe'l + To'ldiruvchi\n\n"
                "Misol:\n"
                "我去学校看书。— Men maktabga kitob o'qigani boraman.\n"
                "我去中国学习汉语。— Men Xitoyga xitoy tili o'rganishga boraman.\n\n"
                "Savol: 你去哪儿做什么？— Qayerga va nima qilgani borasan?"
            ),
            "rule_ru": (
                "Последовательный глагольный оборот: первое действие выражает цель второго.\n"
                "Структура: Подлежащее + 去 + Место + Глагол + Дополнение\n\n"
                "Пример:\n"
                "我去学校看书。— Я иду в школу читать.\n"
                "我去中国学习汉语。— Я еду в Китай учить китайский.\n\n"
                "Вопрос: 你去哪儿做什么？— Куда ты идёшь и что будешь делать?"
            ),
            "rule_tj": (
                "Ҷумлаи пайдарпайи феълӣ: амали аввал мақсади дуввумро ифода мекунад.\n"
                "Сохтор: Мубтадо + 去 + Ҷой + Феъл + Пуркунанда\n\n"
                "Мисол:\n"
                "我去学校看书。— Ман ба мактаб рафта китоб мехонам.\n"
                "我去中国学习汉语。— Ман ба Чин рафта забони чинӣ меомӯзам.\n\n"
                "Савол: 你去哪儿做什么？— Ту ба куҷо рафта чӣ мекунӣ?"
            ),
            "examples": [
                {"zh": "我去学校看书。",     "pinyin": "Wǒ qù xuéxiào kàn shū.",        "uz": "Men maktabga kitob o'qigani boraman.",          "ru": "Я иду в школу читать.",                "tj": "Ман ба мактаб рафта китоб мехонам."},
                {"zh": "她去学校学汉语。",   "pinyin": "Tā qù xuéxiào xué Hànyǔ.",     "uz": "U maktabga xitoy tili o'rganishga boradi.",     "ru": "Она идёт в школу учить китайский.",    "tj": "Вай ба мактаб рафта забони чинӣ меомӯзад."},
                {"zh": "你去哪儿做什么？",   "pinyin": "Nǐ qù nǎr zuò shénme?",        "uz": "Qayerga va nima qilgani borasan?",              "ru": "Куда ты идёшь и что будешь делать?",   "tj": "Ту ба куҷо рафта чӣ мекунӣ?"},
            ]
        },
    ], ensure_ascii=False),

    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "date_writing",
            "instruction_uz": "Xitoycha yozing:",
            "instruction_ru": "Напишите по-китайски:",
            "instruction_tj": "Бо хатти чинӣ нависед:",
            "items": [
                {"prompt_uz": "3-mart, dushanba",              "prompt_ru": "3 марта, понедельник",              "prompt_tj": "3-юми март, душанбе",              "answer": "3月3号，星期一",    "pinyin": "sān yuè sān hào, xīngqī yī"},
                {"prompt_uz": "15-may, juma",                  "prompt_ru": "15 мая, пятница",                  "prompt_tj": "15-уми май, ҷумъа",               "answer": "5月15号，星期五",   "pinyin": "wǔ yuè shíwǔ hào, xīngqī wǔ"},
                {"prompt_uz": "31-dekabr, yakshanba",          "prompt_ru": "31 декабря, воскресенье",          "prompt_tj": "31-уми декабр, якшанбе",          "answer": "12月31号，星期日",  "pinyin": "shí'èr yuè sānshíyī hào, xīngqīrì"},
                {"prompt_uz": "Bugun nechanchi sana?",         "prompt_ru": "Какое сегодня число?",             "prompt_tj": "Имрӯз чанди сана аст?",           "answer": "今天几号？",        "pinyin": "Jīntiān jǐ hào?"},
                {"prompt_uz": "Bugun haftaning nechanchi kuni?","prompt_ru": "Какой сегодня день недели?",      "prompt_tj": "Имрӯз кадом рӯзи ҳафта аст?",    "answer": "今天星期几？",      "pinyin": "Jīntiān xīngqī jǐ?"},
            ]
        },
        {
            "no": 2,
            "type": "translate_to_chinese",
            "instruction_uz": "Xitoycha yozing:",
            "instruction_ru": "Напишите по-китайски:",
            "instruction_tj": "Бо хатти чинӣ нависед:",
            "items": [
                {"prompt_uz": "Kechirasiz, bugun nechanchi sana?",          "prompt_ru": "Извините, какое сегодня число?",              "prompt_tj": "Бубахшед, имрӯз чанди сана аст?",          "answer": "请问，今天几号？",       "pinyin": "Qǐngwèn, jīntiān jǐ hào?"},
                {"prompt_uz": "Ertaga shanba — maktabga borasanmi?",        "prompt_ru": "Завтра суббота — ты идёшь в школу?",          "prompt_tj": "Фардо шанбе — ту ба мактаб меравӣ?",      "answer": "明天星期六，你去学校吗？", "pinyin": "Míngtiān xīngqī liù, nǐ qù xuéxiào ma?"},
                {"prompt_uz": "Men maktabga kitob o'qigani boraman.",       "prompt_ru": "Я иду в школу читать.",                       "prompt_tj": "Ман ба мактаб рафта китоб мехонам.",       "answer": "我去学校看书。",         "pinyin": "Wǒ qù xuéxiào kàn shū."},
            ]
        },
        {
            "no": 3,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "今天___月___号，___期___。",        "prompt_ru": "今天___月___号，___期___。",        "prompt_tj": "今天___月___号，___期___。",        "answer": "bugungi sanani yozing", "pinyin": "today's date"},
                {"prompt_uz": "我___学校___书。",                  "prompt_ru": "我___学校___书。",                  "prompt_tj": "我___学校___书。",                  "answer": "去/看",              "pinyin": "qù/kàn"},
                {"prompt_uz": "___天是9月2号，星期四。",           "prompt_ru": "___天是9月2号，星期四。",           "prompt_tj": "___天是9月2号，星期四。",           "answer": "明",                 "pinyin": "míng"},
                {"prompt_uz": "请___，今天星期几？",               "prompt_ru": "请___，今天星期几？",               "prompt_tj": "请___，今天星期几？",               "answer": "问",                 "pinyin": "wèn"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["3月3号，星期一", "5月15号，星期五", "12月31号，星期日", "今天几号？", "今天星期几？"]},
        {"no": 2, "answers": ["请问，今天几号？", "明天星期六，你去学校吗？", "我去学校看书。"]},
        {"no": 3, "answers": ["bugungi sana", "去/看", "明", "问"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Bugungi, kechagi va ertagi sanani yozing:",
            "instruction_ru": "Напишите сегодняшнюю, вчерашнюю и завтрашнюю даты:",
            "instruction_tj": "Санаи имрӯз, дирӯз ва фардоро нависед:",
            "template": "昨天是___月___号，星期___。今天是___月___号，星期___。明天是___月___号，星期___。",
        },
        {
            "no": 2,
            "instruction_uz": "Ertangi rejalarni yozing (去+joy+harakat ishlatib):",
            "instruction_ru": "Напишите планы на завтра (используя 去+место+действие):",
            "instruction_tj": "Нақшаи фардоро нависед (истифода аз 去+ҷой+амал):",
            "example": "明天我去___。",
            "words": ["去", "学校", "看书", "说汉语", "做中国菜"],
        }
    ], ensure_ascii=False),

    "is_active": True,
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
