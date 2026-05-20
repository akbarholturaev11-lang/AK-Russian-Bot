import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 15,
    "lesson_code": "HSK1-L15",
    "title": "我是坐飞机来的",
    "goal": json.dumps({"uz": "是……的 konstruktsiyasi — vaqt, joy va usulni ta'kidlash", "ru": "Конструкция 是……的 — выделение времени, места и способа действия", "tj": "Сохтори 是……的 — таъкиди вақт, ҷой ва усули амал"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "O'n beshinchi — oxirgi darsda 是……的 konstruktsiyasini ishlatib, biror harakatning qachon, qayerda va qanday bajarilganini ta'kidlashni o'rganasiz. 9 ta yangi so'z, 3 ta suhbat.", "ru": "В пятнадцатом — финальном — уроке вы научитесь использовать конструкцию 是……的, чтобы подчеркнуть, когда, где и как было совершено действие. 9 новых слов, 3 диалога.", "tj": "Дар дарси понздаҳум — дарси охирӣ — шумо ёд мегиред, ки чӣ гуна сохтори 是……的-ро барои таъкид кардани вақт, ҷой ва усули амал истифода барем. 9 калимаи нав, 3 муколама."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "认识",  "pinyin": "rènshi",   "pos": "v.",   "uz": "tanish bo'lmoq, uchrashmoq",     "ru": "знать, познакомиться",          "tj": "шинохтан, шинос шудан"},
        {"no": 2, "zh": "年",    "pinyin": "nián",     "pos": "n.",   "uz": "yil",                            "ru": "год",                           "tj": "сол"},
        {"no": 3, "zh": "大学",  "pinyin": "dàxué",    "pos": "n.",   "uz": "universitet, oliy ta'lim muassasasi", "ru": "университет, вуз",           "tj": "донишгоҳ"},
        {"no": 4, "zh": "饭店",  "pinyin": "fàndiàn",  "pos": "n.",   "uz": "restoran, mehmonxona",            "ru": "ресторан, гостиница",           "tj": "тарабхона, меҳмонхона"},
        {"no": 5, "zh": "出租车","pinyin": "chūzūchē", "pos": "n.",   "uz": "taksi",                          "ru": "такси",                         "tj": "таксӣ"},
        {"no": 6, "zh": "一起",  "pinyin": "yīqǐ",     "pos": "adv.", "uz": "birga",                          "ru": "вместе",                        "tj": "якҷоя"},
        {"no": 7, "zh": "高兴",  "pinyin": "gāoxìng",  "pos": "adj.", "uz": "xursand, shod",                  "ru": "рад, доволен",                  "tj": "хурсанд, шод"},
        {"no": 8, "zh": "听",    "pinyin": "tīng",     "pos": "v.",   "uz": "eshitmoq, tinglаmoq",            "ru": "слушать, слышать",              "tj": "шунидан, гӯш кардан"},
        {"no": 9, "zh": "飞机",  "pinyin": "fēijī",    "pos": "n.",   "uz": "samolyot",                       "ru": "самолёт",                       "tj": "ҳавопаймо"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Dasturxon yonida — qachon va qayerda tanishdingiz",
            "scene_ru": "За столом — когда и где познакомились",
            "scene_tj": "Дар сари дастурхон — кай ва дар куҷо шинос шудед",
            "dialogue": [
                {"speaker": "A", "zh": "你和李小姐是什么时候认识的？",    "pinyin": "Nǐ hé Lǐ xiǎojiě shì shénme shíhou rènshi de?",    "uz": "Siz Xonim Li bilan qachon tanishdingiz?",                 "ru": "Когда вы познакомились с мисс Ли?",                          "tj": "Шумо бо хонум Ли кай шинос шудед?"},
                {"speaker": "B", "zh": "我们是2011年9月认识的。",        "pinyin": "Wǒmen shì èr líng yī yī nián jiǔ yuè rènshi de.",  "uz": "Biz 2011-yilning sentabrida tanishdik.",                  "ru": "Мы познакомились в сентябре 2011 года.",                     "tj": "Мо дар моҳи сентябри соли 2011 шинос шудем."},
                {"speaker": "A", "zh": "你们在哪儿认识的？",             "pinyin": "Nǐmen zài nǎr rènshi de?",                         "uz": "Siz ikkovingiz qayerda tanishdingiz?",                    "ru": "Где вы двое познакомились?",                                 "tj": "Шумо дуто дар куҷо шинос шудед?"},
                {"speaker": "B", "zh": "我们是在学校认识的，她是我大学同学。","pinyin": "Wǒmen shì zài xuéxiào rènshi de, tā shì wǒ dàxué tóngxué.", "uz": "Biz maktabda tanishdik, u mening universitetdosh do'stim.", "ru": "Мы познакомились в школе; она моя однокурсница.",            "tj": "Мо дар мактаб шинос шудем, вай ҳамдарси донишгоҳии ман аст."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Mehmonxona oldida — qanday keldingiz",
            "scene_ru": "Перед гостиницей — как добрались",
            "scene_tj": "Дар назди меҳмонхона — чӣ гуна омадед",
            "dialogue": [
                {"speaker": "A", "zh": "你们是怎么来饭店的？",          "pinyin": "Nǐmen shì zěnme lái fàndiàn de?",                "uz": "Siz restoranga qanday keldingiz?",                         "ru": "Как вы добрались до ресторана?",                            "tj": "Шумо ба тарабхона чӣ гуна омадед?"},
                {"speaker": "B", "zh": "我们是坐出租车来的。",          "pinyin": "Wǒmen shì zuò chūzūchē lái de.",               "uz": "Biz taksi bilan keldik.",                                  "ru": "Мы приехали на такси.",                                     "tj": "Мо бо таксӣ омадем."},
                {"speaker": "A", "zh": "李先生呢？",                    "pinyin": "Lǐ xiānsheng ne?",                             "uz": "Janob Li-chi?",                                            "ru": "А господин Ли?",                                           "tj": "Ҷаноб Ли чӣ?"},
                {"speaker": "B", "zh": "他是和朋友一起开车来的。",      "pinyin": "Tā shì hé péngyou yīqǐ kāi chē lái de.",       "uz": "U do'sti bilan birga mashina haydab keldi.",               "ru": "Он приехал вместе с другом на машине.",                     "tj": "Вай бо дӯсташ якҷоя бо мошин омад."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Kompaniyada — samolyot bilan kelding",
            "scene_ru": "В компании — прилетел на самолёте",
            "scene_tj": "Дар ширкат — бо ҳавопаймо омадед",
            "dialogue": [
                {"speaker": "A", "zh": "很高兴认识您！李小姐。",          "pinyin": "Hěn gāoxìng rènshi nín! Lǐ xiǎojiě.",          "uz": "Siz bilan tanishganimdan juda xursandman, Xonim Li!",     "ru": "Очень рад познакомиться с вами, мисс Ли!",                  "tj": "Аз шиноси бо шумо бисёр хурсандам, хонум Ли!"},
                {"speaker": "B", "zh": "认识你我也很高兴！",             "pinyin": "Rènshi nǐ wǒ yě hěn gāoxìng!",                "uz": "Siz bilan tanishganimdan men ham juda xursandman!",        "ru": "Мне тоже очень приятно познакомиться с вами!",              "tj": "Аз шиноси бо шумо ман ҳам бисёр хурсандам!"},
                {"speaker": "A", "zh": "听张先生说，您是坐飞机来北京的？","pinyin": "Tīng Zhāng xiānsheng shuō, nín shì zuò fēijī lái Běijīng de?", "uz": "Janob Jan aytishicha, siz Pekinga samolyot bilan kelgansiz?", "ru": "Господин Чжан сказал, что вы прилетели в Пекин на самолёте?", "tj": "Ҷаноб Чжан гуфт, ки шумо ба Пекин бо ҳавопаймо омадед?"},
                {"speaker": "B", "zh": "是的。",                        "pinyin": "Shì de.",                                      "uz": "Ha, to'g'ri.",                                             "ru": "Да, именно.",                                              "tj": "Бале, дуруст."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "是……的 — Vaqt, joy va usulni ta'kidlash",
            "title_uz": "是……的 konstruktsiyasi — vaqt, joy va usulni ta'kidlash",
            "title_ru": "Конструкция 是……的 — выделение времени, места и способа",
            "title_tj": "Сохтори 是……的 — таъкиди вақт, ҷой ва усул",
            "rule_uz": (
                "是……的 konstruktsiyasi allaqachon sodir bo'lgan harakatning "
                "vaqti, joyi yoki usulini ta'kidlash uchun ishlatiladi.\n\n"
                "Tuzilishi:\n"
                "Ega + 是 + [Vaqt/Joy/Usul] + Fe'l + 的\n\n"
                "Vaqtni ta'kidlash:\n"
                "我们是2011年认识的。— Biz 2011-yilda tanishdik.\n\n"
                "Joyni ta'kidlash:\n"
                "我们是在学校认识的。— Biz maktabda tanishdik.\n\n"
                "Usulni ta'kidlash:\n"
                "我是坐飞机来的。— Men samolyot bilan keldim.\n\n"
                "Inkor: 不是……的\n"
                "我不是坐出租车来的。— Men taksi bilan kelmaganman."
            ),
            "rule_ru": (
                "Конструкция 是……的 используется для выделения времени, "
                "места или способа уже совершённого действия.\n\n"
                "Структура:\n"
                "Подлежащее + 是 + [Время/Место/Способ] + Глагол + 的\n\n"
                "Выделение времени:\n"
                "我们是2011年认识的。— Мы познакомились в 2011 году.\n\n"
                "Выделение места:\n"
                "我们是在学校认识的。— Мы познакомились в школе.\n\n"
                "Выделение способа:\n"
                "我是坐飞机来的。— Я прилетел на самолёте.\n\n"
                "Отрицание: 不是……的\n"
                "我不是坐出租车来的。— Я не приехал на такси."
            ),
            "rule_tj": (
                "Сохтори 是……的 барои таъкид кардани вақт, ҷой ё усули "
                "амали аллакай анҷомёфта истифода мешавад.\n\n"
                "Сохтор:\n"
                "Мубтадо + 是 + [Вақт/Ҷой/Усул] + Феъл + 的\n\n"
                "Таъкиди вақт:\n"
                "我们是2011年认识的。— Мо дар соли 2011 шинос шудем.\n\n"
                "Таъкиди ҷой:\n"
                "我们是在学校认识的。— Мо дар мактаб шинос шудем.\n\n"
                "Таъкиди усул:\n"
                "我是坐飞机来的。— Ман бо ҳавопаймо омадам.\n\n"
                "Инкор: 不是……的\n"
                "我不是坐出租车来的。— Ман бо таксӣ наомадам."
            ),
            "examples": [
                {"zh": "我们是2011年认识的。",   "pinyin": "Wǒmen shì èr líng yī yī nián rènshi de.",   "uz": "Biz 2011-yilda tanishdik.",                "ru": "Мы познакомились в 2011 году.",             "tj": "Мо дар соли 2011 шинос шудем."},
                {"zh": "我是坐飞机来的。",        "pinyin": "Wǒ shì zuò fēijī lái de.",                 "uz": "Men samolyot bilan keldim.",               "ru": "Я прилетел на самолёте.",                   "tj": "Ман бо ҳавопаймо омадам."},
                {"zh": "她是在北京买的。",        "pinyin": "Tā shì zài Běijīng mǎi de.",               "uz": "U uni Pekinda sotib oldi.",                "ru": "Она купила это в Пекине.",                  "tj": "Вай онро дар Пекин харид."},
                {"zh": "我们不是坐出租车来的。",  "pinyin": "Wǒmen bú shì zuò chūzūchē lái de.",        "uz": "Biz taksi bilan kelmaganmiz.",             "ru": "Мы не приехали на такси.",                  "tj": "Мо бо таксӣ наомадем."},
            ]
        },
        {
            "no": 2,
            "title_zh": "日期的表达(2) — To'liq sana ifodalash",
            "title_uz": "To'liq sana ifodalash (2)",
            "title_ru": "Выражение полной даты (2)",
            "title_tj": "Ифодаи санаи пурра (2)",
            "rule_uz": (
                "Xitoy tilida to'liq sana eng kattadan eng kichigiga qadar ifodalanadi:\n"
                "Yil + Oy + Kun + Haftaning kuni\n\n"
                "Yilni o'qish: har bir raqam alohida o'qiladi\n"
                "2011 → 二零一一年 (èr líng yī yī nián)\n"
                "2024 → 二零二四年 (èr líng èr sì nián)\n\n"
                "To'liq misol:\n"
                "2011年9月10号，星期三\n"
                "2011-yil, sentabr, 10-chi, chorshanba"
            ),
            "rule_ru": (
                "В китайском языке полная дата выражается от большего к меньшему:\n"
                "Год + Месяц + День + День недели\n\n"
                "Чтение года: каждая цифра читается отдельно\n"
                "2011 → 二零一一年 (èr líng yī yī nián)\n"
                "2024 → 二零二四年 (èr líng èr sì nián)\n\n"
                "Полный пример:\n"
                "2011年9月10号，星期三\n"
                "2011 год, сентябрь, 10-е, среда"
            ),
            "rule_tj": (
                "Дар забони чинӣ санаи пурра аз калон ба хурд ифода мешавад:\n"
                "Сол + Моҳ + Рӯз + Рӯзи ҳафта\n\n"
                "Хондани сол: ҳар рақам алоҳида хонда мешавад\n"
                "2011 → 二零一一年 (èr líng yī yī nián)\n"
                "2024 → 二零二四年 (èr líng èr sì nián)\n\n"
                "Мисоли пурра:\n"
                "2011年9月10号，星期三\n"
                "Соли 2011, сентябр, 10-ум, чоршанбе"
            ),
            "examples": [
                {"zh": "2011年9月认识的",     "pinyin": "èr líng yī yī nián jiǔ yuè rènshi de", "uz": "2011-yilning sentabrida tanishgan",      "ru": "познакомились в сентябре 2011 года",    "tj": "дар моҳи сентябри соли 2011 шинос шудем"},
                {"zh": "今天是2024年4月26号。","pinyin": "Jīntiān shì èr líng èr sì nián sì yuè èrshíliù hào.", "uz": "Bugun 2024-yilning 26-apreli.", "ru": "Сегодня 26 апреля 2024 года.",   "tj": "Имрӯз 26-уми апрели соли 2024 аст."},
            ]
        },
    ], ensure_ascii=False),

    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Xitoycha yozing (是……的 ishlatib):",
            "instruction_ru": "Напишите по-китайски (используя 是……的):",
            "instruction_tj": "Бо хатти чинӣ нависед (бо истифода аз 是……的):",
            "items": [
                {"prompt_uz": "Biz 2011-yilda tanishdik.",           "prompt_ru": "Мы познакомились в 2011 году.",          "prompt_tj": "Мо дар соли 2011 шинос шудем.",        "answer": "我们是2011年认识的。",       "pinyin": "Wǒmen shì èr líng yī yī nián rènshi de."},
                {"prompt_uz": "Men samolyot bilan keldim.",           "prompt_ru": "Я прилетел на самолёте.",               "prompt_tj": "Ман бо ҳавопаймо омадам.",             "answer": "我是坐飞机来的。",           "pinyin": "Wǒ shì zuò fēijī lái de."},
                {"prompt_uz": "Restoranga qanday keldingiz?",         "prompt_ru": "Как вы добрались до ресторана?",        "prompt_tj": "Шумо ба тарабхона чӣ гуна омадед?",   "answer": "你是怎么来饭店的？",         "pinyin": "Nǐ shì zěnme lái fàndiàn de?"},
                {"prompt_uz": "Biz taksi bilan keldik.",              "prompt_ru": "Мы приехали на такси.",                 "prompt_tj": "Мо бо таксӣ омадем.",                 "answer": "我们是坐出租车来的。",       "pinyin": "Wǒmen shì zuò chūzūchē lái de."},
                {"prompt_uz": "U do'sti bilan birga keldi.",          "prompt_ru": "Он пришёл вместе с другом.",            "prompt_tj": "Вай бо дӯсташ якҷоя омад.",           "answer": "他是和朋友一起来的。",       "pinyin": "Tā shì hé péngyou yīqǐ lái de."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "你们___什么时候认识的？",    "prompt_ru": "你们___什么时候认识的？",    "prompt_tj": "你们___什么时候认识的？",    "answer": "是",   "pinyin": "shì"},
                {"prompt_uz": "我是坐飞机来___。",          "prompt_ru": "我是坐飞机来___。",          "prompt_tj": "我是坐飞机来___。",          "answer": "的",   "pinyin": "de"},
                {"prompt_uz": "他们是___学校认识的。",      "prompt_ru": "他们是___学校认识的。",      "prompt_tj": "他们是___学校认识的。",      "answer": "在",   "pinyin": "zài"},
                {"prompt_uz": "我不___坐出租车来的。",      "prompt_ru": "我不___坐出租车来的。",      "prompt_tj": "我不___坐出租车来的。",      "answer": "是",   "pinyin": "shì"},
            ]
        },
        {
            "no": 3,
            "type": "emphasis",
            "instruction_uz": "是……的 yordamida ta'kidlang:",
            "instruction_ru": "Выделите с помощью 是……的:",
            "instruction_tj": "Бо ёрии 是……的 таъкид кунед:",
            "items": [
                {"prompt_uz": "我坐飞机来。(usulni ta'kidlang)",      "prompt_ru": "我坐飞机来。(выделить способ)",      "prompt_tj": "我坐飞机来。(усулро таъкид кунед)",    "answer": "我是坐飞机来的。",         "pinyin": "Wǒ shì zuò fēijī lái de."},
                {"prompt_uz": "他们在北京认识。(joyni ta'kidlang)",   "prompt_ru": "他们在北京认识。(выделить место)",   "prompt_tj": "他们在北京认识。(ҷойро таъкид кунед)", "answer": "他们是在北京认识的。",     "pinyin": "Tāmen shì zài Běijīng rènshi de."},
                {"prompt_uz": "我2011年来中国。(vaqtni ta'kidlang)",  "prompt_ru": "我2011年来中国。(выделить время)",   "prompt_tj": "我2011年来中国。(вақтро таъкид кунед)","answer": "我是2011年来中国的。",     "pinyin": "Wǒ shì èr líng yī yī nián lái Zhōngguó de."},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["我们是2011年认识的。", "我是坐飞机来的。", "你是怎么来饭店的？", "我们是坐出租车来的。", "他是和朋友一起来的。"]},
        {"no": 2, "answers": ["是", "的", "在", "是"]},
        {"no": 3, "answers": ["我是坐飞机来的。", "他们是在北京认识的。", "我是2011年来中国的。"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "O'zingiz haqingizda 是……的 ishlatib 4 ta gap yozing:",
            "instruction_ru": "Напишите 4 предложения о себе, используя 是……的:",
            "instruction_tj": "Дар бораи худ бо истифода аз 是……的 4 ҷумла нависед:",
            "template": "我是___年___的。我是在___认识___的。我是坐___来___的。",
            "words": ["是", "的", "在", "年", "坐", "飞机", "出租车", "认识"],
        },
        {
            "no": 2,
            "instruction_uz": "Do'stingizga 是……的 ishlatib savol bering:",
            "instruction_ru": "Задайте другу вопросы, используя 是……的:",
            "instruction_tj": "Ба дӯстатон бо истифода аз 是……的 савол диҳед:",
            "items": [
                {"prompt_uz": "Siz ikkovingiz qachon tanishdingiz?",  "prompt_ru": "Когда вы двое познакомились?",   "prompt_tj": "Шумо дуто кай шинос шудед?",      "example": "你们是什么时候认识的？"},
                {"prompt_uz": "Siz qayerda tanishdingiz?",            "prompt_ru": "Где вы познакомились?",          "prompt_tj": "Шумо дар куҷо шинос шудед?",      "example": "你们是在哪儿认识的？"},
                {"prompt_uz": "U qanday keldi?",                      "prompt_ru": "Как он добрался?",               "prompt_tj": "Вай чӣ гуна омад?",               "example": "他是怎么来的？"},
            ]
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
