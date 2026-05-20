import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 2,
    "lesson_code": "HSK2-L02",
    "title": "我每天六点起床",
    "goal": json.dumps({
        "uz": "Kundalik hayot tartibi, sog'liq va jismoniy faoliyat haqida gapira olish; 是不是 savol qolipini, 每 olmoshini va 多 so'roq olmoshini o'zlashtirish.",
        "ru": "Научиться говорить о распорядке дня, здоровье и физической активности; освоить вопросный шаблон 是不是, местоимение 每 и вопросительное местоимение 多.",
        "tj": "Гуфтугӯ дар бораи тартиби рӯзона, саломатӣ ва фаъолияти ҷисмонӣ; азхудкунии шакли саволии 是不是, ҷонишини 每 ва ҷонишини саволии 多.",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Bu darsda sog'liq va sport bilan shug'ullanish mavzusi o'rganiladi. Siz ertalabki yugurish, kun tartibi va kasalxonadan chiqish haqida gaplasha olasiz. Asosiy grammatik mavzular: '是不是' bilan savol tuzish, 每 olmoshi va 多 so'roq olmoshi.",
        "ru": "На этом уроке изучается тема здоровья и занятий спортом. Вы сможете говорить об утренней пробежке, распорядке дня и выписке из больницы. Основные грамматические темы: вопрос с 是不是, местоимение 每 и вопросительное местоимение 多.",
        "tj": "Дар ин дарс мавзӯи саломатӣ ва машғул шудан бо варзиш омӯхта мешавад. Шумо метавонед дар бораи давидани субҳгоҳӣ, тартиби рӯз ва баромадан аз беморхона сӯҳбат кунед. Мавзӯҳои асосии грамматикӣ: савол бо 是不是, ҷонишини 每 ва ҷонишини саволии 多.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "生病",  "pinyin": "shēngbìng",  "pos": "v.",    "uz": "kasal bo'lmoq",                     "ru": "заболевать, болеть",               "tj": "бемор шудан, касал шудан"},
        {"no": 2,  "zh": "每",    "pinyin": "měi",         "pos": "pron.", "uz": "har (bir), har qaysi",              "ru": "каждый",                           "tj": "ҳар (як), ҳар кадом"},
        {"no": 3,  "zh": "早上",  "pinyin": "zǎoshang",    "pos": "n.",    "uz": "ertalab",                           "ru": "утро, утром",                      "tj": "субҳ, субҳгоҳ"},
        {"no": 4,  "zh": "跑步",  "pinyin": "pǎobù",       "pos": "v.",    "uz": "yugurmoq, chopmoq",                 "ru": "бегать, бежать",                   "tj": "давидан"},
        {"no": 5,  "zh": "起床",  "pinyin": "qǐchuáng",    "pos": "v.",    "uz": "o'rnidan turmoq, uyg'onmoq",        "ru": "вставать с постели",               "tj": "аз хоб хестан"},
        {"no": 6,  "zh": "药",    "pinyin": "yào",          "pos": "n.",    "uz": "dori, doridarmon",                  "ru": "лекарство",                        "tj": "дору"},
        {"no": 7,  "zh": "身体",  "pinyin": "shēntǐ",      "pos": "n.",    "uz": "tana, jism; sog'liq",               "ru": "тело; здоровье",                   "tj": "ҷисм; саломатӣ"},
        {"no": 8,  "zh": "出院",  "pinyin": "chūyuàn",     "pos": "v.",    "uz": "kasalxonadan chiqmoq",              "ru": "выписаться из больницы",           "tj": "аз беморхона баромадан"},
        {"no": 9,  "zh": "出",    "pinyin": "chū",          "pos": "v.",    "uz": "chiqmoq",                           "ru": "выходить, выезжать",               "tj": "баромадан, берун шудан"},
        {"no": 10, "zh": "高",    "pinyin": "gāo",          "pos": "adj.", "uz": "baland, bo'yi baland",              "ru": "высокий",                          "tj": "баланд, дарозқад"},
        {"no": 11, "zh": "米",    "pinyin": "mǐ",           "pos": "m.",   "uz": "metr (o'lchov birligi)",            "ru": "метр (единица измерения)",         "tj": "метр (воҳиди андоза)"},
        {"no": 12, "zh": "知道",  "pinyin": "zhīdào",      "pos": "v.",    "uz": "bilmoq",                            "ru": "знать",                            "tj": "донистан"},
        {"no": 13, "zh": "休息",  "pinyin": "xiūxi",       "pos": "v.",    "uz": "dam olmoq",                         "ru": "отдыхать",                         "tj": "истироҳат кардан"},
        {"no": 14, "zh": "忙",    "pinyin": "máng",         "pos": "adj.", "uz": "band, ishi ko'p",                   "ru": "занятый, загруженный",             "tj": "банд, серкор"},
        {"no": 15, "zh": "时间",  "pinyin": "shíjiān",     "pos": "n.",    "uz": "vaqt",                              "ru": "время",                            "tj": "вақт"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Sport maydonchasida",
            "scene_ru": "На спортивной площадке",
            "scene_tj": "Дар майдони варзишӣ",
            "dialogue": [
                {"speaker": "A", "zh": "你很少生病，是不是喜欢运动？", "pinyin": "Nǐ hěn shǎo shēngbìng, shì bú shì xǐhuan yùndòng?", "uz": "Sen kamdan-kam kasal bo'lasan, sport qilishni yaxshi ko'rasanmi?", "ru": "Ты редко болеешь, ты любишь спорт?", "tj": "Ту кам касал мешавӣ, оё варзишро дӯст медорӣ?"},
                {"speaker": "B", "zh": "是啊，我每天早上都要出去跑步。", "pinyin": "Shì a, wǒ měitiān zǎoshang dōu yào chūqù pǎobù.", "uz": "Ha, men har kuni ertalab tashqariga chiqib yuguraman.", "ru": "Да, я каждое утро выхожу бегать.", "tj": "Бале, ман ҳар субҳ берун мебароям ва медавам."},
                {"speaker": "A", "zh": "你每天几点起床？", "pinyin": "Nǐ měitiān jǐ diǎn qǐchuáng?", "uz": "Sen har kuni soat nechada turasan?", "ru": "В котором часу ты каждый день встаёшь?", "tj": "Ту ҳар рӯз соати чанд аз хоб мехезӣ?"},
                {"speaker": "B", "zh": "我每天六点起床。", "pinyin": "Wǒ měitiān liù diǎn qǐchuáng.", "uz": "Men har kuni soat oltida turaman.", "ru": "Я каждый день встаю в шесть часов.", "tj": "Ман ҳар рӯз соати шаш аз хоб мехезам."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Kasalxonada",
            "scene_ru": "В больнице",
            "scene_tj": "Дар беморхона",
            "dialogue": [
                {"speaker": "A", "zh": "吃药了吗？现在身体怎么样？", "pinyin": "Chī yào le ma? Xiànzài shēntǐ zěnmeyàng?", "uz": "Dori ichdingmi? Hozir sog'liqing qanday?", "ru": "Ты принял лекарство? Как сейчас самочувствие?", "tj": "Оё дору хӯрдӣ? Ҳоло саломатиат чӣ тавр аст?"},
                {"speaker": "B", "zh": "吃了。现在好多了。", "pinyin": "Chī le. Xiànzài hǎo duō le.", "uz": "Ichdim. Hozir ancha yaxshi.", "ru": "Принял. Сейчас намного лучше.", "tj": "Хӯрдам. Ҳоло хеле беҳтар шудам."},
                {"speaker": "A", "zh": "什么时候能出院？", "pinyin": "Shénme shíhou néng chūyuàn?", "uz": "Qachon kasalxonadan chiqasiz?", "ru": "Когда вы сможете выписаться?", "tj": "Кай аз беморхона баромада метавонед?"},
                {"speaker": "B", "zh": "医生说下个星期。", "pinyin": "Yīshēng shuō xià ge xīngqī.", "uz": "Shifokor keyingi haftada, dedi.", "ru": "Врач сказал — на следующей неделе.", "tj": "Духтур гуфт ҳафтаи оянда."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Sport maydonchasida",
            "scene_ru": "На площадке",
            "scene_tj": "Дар майдончаи варзишӣ",
            "dialogue": [
                {"speaker": "A", "zh": "大卫今年多大？", "pinyin": "Dàwèi jīnnián duō dà?", "uz": "Devid bu yil necha yoshda?", "ru": "Сколько лет Дэвиду в этом году?", "tj": "Дэвид имсол чанд сола шудааст?"},
                {"speaker": "B", "zh": "二十多岁。", "pinyin": "Èrshí duō suì.", "uz": "Yigirma yoshdan oshgan.", "ru": "Больше двадцати лет.", "tj": "Зиёда аз бист сол."},
                {"speaker": "A", "zh": "他多高？", "pinyin": "Tā duō gāo?", "uz": "Uning bo'yi qancha?", "ru": "Какой у него рост?", "tj": "Қади ӯ чанд аст?"},
                {"speaker": "B", "zh": "一米八几。", "pinyin": "Yì mǐ bā jǐ.", "uz": "Bir metr saksoni bir necha santimetr.", "ru": "Метр восемьдесят с чем-то.", "tj": "Як метру ҳаштоду чанд."},
                {"speaker": "A", "zh": "你怎么知道这么多啊？", "pinyin": "Nǐ zěnme zhīdào zhème duō a?", "uz": "Sen bularni qanday bilasan?", "ru": "Откуда ты так много знаешь?", "tj": "Чӣ тавр ин қадар медонӣ?"},
                {"speaker": "B", "zh": "他是我同学。", "pinyin": "Tā shì wǒ tóngxué.", "uz": "U mening sinfдошim.", "ru": "Он мой однокурсник.", "tj": "Ӯ ҳамсинфи ман аст."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Xonada",
            "scene_ru": "В комнате",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "张老师星期六也不休息啊？", "pinyin": "Zhāng lǎoshī xīngqīliù yě bù xiūxi a?", "uz": "Zhang o'qituvchi shanba kuni ham dam olmaydi, shundaymi?", "ru": "Учитель Чжан и в субботу не отдыхает?", "tj": "Муаллим Чжан рӯзи шанбе ҳам истироҳат намекунад?"},
                {"speaker": "B", "zh": "是啊，他这几天很忙，没有时间休息。", "pinyin": "Shì a, tā zhè jǐ tiān hěn máng, méiyǒu shíjiān xiūxi.", "uz": "Ha, u bu bir necha kunda juda band, dam olishga vaqti yo'q.", "ru": "Да, он эти несколько дней очень занят, нет времени отдыхать.", "tj": "Бале, ӯ ин чанд рӯз хеле банд аст, вақт барои истироҳат надорад."},
                {"speaker": "A", "zh": "那会很累吧？", "pinyin": "Nà huì hěn lèi ba?", "uz": "U holda juda charchagan bo'lsa kerak?", "ru": "Наверное, он очень устаёт?", "tj": "Пас ӯ хеле хаста мешавад?"},
                {"speaker": "B", "zh": "他每天回来都很累。", "pinyin": "Tā měitiān huílái dōu hěn lèi.", "uz": "U har kuni qaytib kelganida juda charchagan bo'ladi.", "ru": "Он каждый день возвращается очень усталым.", "tj": "Ӯ ҳар рӯз хеле хаста бармегардад."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "用“是不是”的问句",
            "title_uz": "'是不是' bilan savol gaplari",
            "title_ru": "Вопросы с 是不是",
            "title_tj": "Саволҳо бо 是不是",
            "rule_uz": "'是不是' bilan tuzilgan savol gaplari. Bu qolip orqali biror narsa haqida taxmin qilib so'raladi. '是不是' gap boshida yoki o'rtasida kelishi mumkin. Javob 'shunday' yoki 'yo'q' shaklida bo'ladi.",
            "rule_ru": "Вопросы, построенные с 是不是. С помощью этого шаблона задаётся вопрос-предположение. 是不是 может стоять в начале или середине предложения. Ответ — «да» или «нет».",
            "rule_tj": "Саволҳое, ки бо 是不是 сохта мешаванд. Тавассути ин қолиб гумонии чизе пурсида мешавад. 是不是 метавонад дар аввал ё миёнаи ҷумла биояд. Ҷавоб бо 'бале' ё 'не' дода мешавад.",
            "examples": [
                {"zh": "你是不是喜欢运动？", "pinyin": "Nǐ shì bú shì xǐhuan yùndòng?", "uz": "Sen sportni yaxshi ko'rasanmi?", "ru": "Ты любишь спорт?", "tj": "Оё ту варзишро дӯст медорӣ?"},
                {"zh": "他是不是你的朋友？", "pinyin": "Tā shì bú shì nǐ de péngyou?", "uz": "U sening do'stingmi?", "ru": "Он твой друг?", "tj": "Оё ӯ дӯсти туст?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "代词“每”",
            "title_uz": "'每' olmoshi",
            "title_ru": "Местоимение 每",
            "title_tj": "Ҷонишини 每",
            "rule_uz": "'每' olmoshi 'har, har qaysi' ma'nosini beradi. U otdan oldin qo'llaniladi va ko'pincha 都 bilan birga ishlatiladi.",
            "rule_ru": "Местоимение 每 означает «каждый». Ставится перед существительным и часто используется в связке с 都.",
            "rule_tj": "Ҷонишини 每 маънои 'ҳар' дорад. Пеш аз исм меояд ва аксар бо 都 дар якҷоягӣ истифода мешавад.",
            "examples": [
                {"zh": "我每天早上都要跑步。", "pinyin": "Wǒ měitiān zǎoshang dōu yào pǎobù.", "uz": "Men har kuni ertalab yuguraman.", "ru": "Я каждое утро бегаю.", "tj": "Ман ҳар субҳ медавам."},
                {"zh": "每个学生都有书。", "pinyin": "Měi ge xuésheng dōu yǒu shū.", "uz": "Har bir talabaning kitobi bor.", "ru": "У каждого студента есть книга.", "tj": "Ҳар донишҷӯ китоб дорад."},
            ]
        },
        {
            "no": 3,
            "title_zh": "疑问代词“多”",
            "title_uz": "'多' so'roq olmoshi",
            "title_ru": "Вопросительное местоимение 多",
            "title_tj": "Ҷонишини саволии 多",
            "rule_uz": "'多' so'roq olmoshi sifat oldidan kelib 'qancha, nechog'liq' ma'nosini beradi. Odatda o'lchov yoki miqdor so'rashda ishlatiladi.",
            "rule_ru": "Вопросительное местоимение 多 ставится перед прилагательным и означает «насколько, какой». Используется для вопросов об измерениях или величинах.",
            "rule_tj": "Ҷонишини саволии 多 пеш аз сифат меояд ва маънои 'чӣ қадар, чанд' дорад. Барои пурсидан дар бораи андоза ё миқдор истифода мешавад.",
            "examples": [
                {"zh": "你多高？", "pinyin": "Nǐ duō gāo?", "uz": "Sening bo'ying qancha?", "ru": "Какой у тебя рост?", "tj": "Қади ту чанд аст?"},
                {"zh": "他今年多大？", "pinyin": "Tā jīnnián duō dà?", "uz": "U bu yil necha yoshda?", "ru": "Сколько ему лет в этом году?", "tj": "Ӯ имсол чанд сола аст?"},
            ]
        },
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
            "instruction_ru": "Напишите китайский эквивалент следующих слов:",
            "instruction_tj": "Калимаҳои зеринро ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "kasal bo'lmoq", "prompt_ru": "заболевать, болеть", "prompt_tj": "бемор шудан", "answer": "生病", "pinyin": "shēngbìng"},
                {"prompt_uz": "yugurmoq", "prompt_ru": "бегать", "prompt_tj": "давидан", "answer": "跑步", "pinyin": "pǎobù"},
                {"prompt_uz": "dam olmoq", "prompt_ru": "отдыхать", "prompt_tj": "истироҳат кардан", "answer": "休息", "pinyin": "xiūxi"},
                {"prompt_uz": "dori", "prompt_ru": "лекарство", "prompt_tj": "дору", "answer": "药", "pinyin": "yào"},
                {"prompt_uz": "vaqt", "prompt_ru": "время", "prompt_tj": "вақт", "answer": "时间", "pinyin": "shíjiān"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (每、多、是不是、知道、休息):",
            "instruction_ru": "Вставьте подходящее слово (每、多、是不是、知道、休息):",
            "instruction_tj": "Калимаи мувофиқро нависед (每、多、是不是、知道、休息):",
            "items": [
                {"prompt_uz": "你______喜欢运动？", "answer": "是不是", "pinyin": "shì bú shì"},
                {"prompt_uz": "我______天早上都跑步。", "answer": "每", "pinyin": "měi"},
                {"prompt_uz": "他______高？一米八几。", "answer": "多", "pinyin": "duō"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_uzbek",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на узбекский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони ӯзбекӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "我每天六点起床。", "answer": "Men har kuni soat oltida turaman.", "pinyin": "Wǒ měitiān liù diǎn qǐchuáng."},
                {"prompt_uz": "他这几天很忙，没有时间休息。", "answer": "U bu bir necha kunda juda band, dam olishga vaqti yo'q.", "pinyin": "Tā zhè jǐ tiān hěn máng, méiyǒu shíjiān xiūxi."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["生病", "跑步", "休息", "药", "时间"]},
        {"no": 2, "answers": ["是不是", "每", "多"]},
        {"no": 3, "answers": ["Men har kuni soat oltida turaman.", "U bu bir necha kunda juda band, dam olishga vaqti yo'q."]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib 3 ta gap tuzing:",
            "instruction_ru": "Составьте 3 предложения, используя следующие слова:",
            "instruction_tj": "Бо истифода аз калимаҳои зерин 3 ҷумла тартиб диҳед:",
            "words": ["每", "早上", "跑步", "起床", "休息"],
            "example": "我每天早上六点起床，然后出去跑步。",
        },
        {
            "no": 2,
            "instruction_uz": "'是不是' va '多' qoliplaridan foydalanib 4 ta savol gapi yozing. Ulardan 2 tasida sog'liq, 2 tasida kun tartibi haqida so'rang.",
            "instruction_ru": "Напишите 4 вопросительных предложения, используя 是不是 и 多. В 2 из них спросите о здоровье, в 2 — о распорядке дня.",
            "instruction_tj": "Бо истифода аз 是不是 ва 多 чор ҷумлаи саволӣ нависед. Дар 2-тои онҳо дар бораи саломатӣ, дар 2-тои дигар дар бораи тартиби рӯз бипурсед.",
        },
    ], ensure_ascii=False),
    "review_json": "[]",
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
