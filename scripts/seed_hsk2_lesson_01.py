import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 1,
    "lesson_code": "HSK2-L01",
    "title": "九月去北京旅游最好",
    "goal": json.dumps({
        "uz": "Sayohat, sport va kundalik hayot mavzularida suhbat qurish; 要, 最 va taxminiy sonlarni ishlatishni o'rganish.",
        "ru": "Научиться вести беседу о путешествиях, спорте и повседневной жизни; освоить вспомогательный глагол 要, наречие степени 最 и приблизительные числа.",
        "tj": "Гуфтугӯ дар мавзӯи сафар, варзиш ва ҳаёти рӯзмарра; омӯхтани феъли ёрдамии 要, зарфи дараҷаи 最 ва рақамҳои тахминӣ.",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": (
            "Bu darsda siz sayohat rejalari, sport va kundalik turmush haqida gaplashishni o'rganasiz. "
            "Asosiy grammatik mavzular: yordamchi fe'l 要, daraja ravishi 最, va taxminiy sonlar (几, 多). "
            "13 ta yangi so'z va 4 ta jonli dialog o'rganiladi."
        ),
        "ru": (
            "На этом уроке вы научитесь говорить о планах путешествия, спорте и повседневной жизни. "
            "Основные грамматические темы: вспомогательный глагол 要, наречие степени 最 и приблизительные числа (几, 多). "
            "Изучается 13 новых слов и 4 живых диалога."
        ),
        "tj": (
            "Дар ин дарс шумо ёд мегиред, ки дар бораи нақшаҳои сафар, варзиш ва ҳаёти рӯзмарра сӯҳбат кунед. "
            "Мавзӯҳои асосии грамматикӣ: феъли ёрдамии 要, зарфи дараҷаи 最 ва рақамҳои тахминӣ (几, 多). "
            "13 калимаи нав ва 4 мукотиба омӯхта мешавад."
        ),
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "旅游",   "pinyin": "lǚyóu",       "pos": "v.",           "uz": "sayohat qilmoq",                          "ru": "путешествовать",                             "tj": "сафар кардан"},
        {"no": 2,  "zh": "觉得",   "pinyin": "juéde",        "pos": "v.",           "uz": "deb o'ylash, his qilish",                 "ru": "думать, считать, чувствовать",               "tj": "фикр кардан, ҳис кардан"},
        {"no": 3,  "zh": "最",     "pinyin": "zuì",          "pos": "adv.",         "uz": "eng, juda",                               "ru": "самый, наиболее",                            "tj": "аз ҳама, бештар"},
        {"no": 4,  "zh": "为什么", "pinyin": "wèi shénme",   "pos": "conj./adv.",   "uz": "nega, nima uchun",                        "ru": "почему, зачем",                              "tj": "чаро, барои чӣ"},
        {"no": 5,  "zh": "也",     "pinyin": "yě",           "pos": "adv.",         "uz": "ham",                                     "ru": "тоже, также",                                "tj": "ҳам"},
        {"no": 6,  "zh": "运动",   "pinyin": "yùndòng",      "pos": "n./v.",        "uz": "sport; sport qilmoq",                     "ru": "спорт; заниматься спортом",                  "tj": "варзиш; варзиш кардан"},
        {"no": 7,  "zh": "踢足球", "pinyin": "tī zúqiú",     "pos": "v.",           "uz": "futbol o'ynamoq",                         "ru": "играть в футбол",                            "tj": "футбол бозӣ кардан"},
        {"no": 8,  "zh": "一起",   "pinyin": "yìqǐ",         "pos": "adv.",         "uz": "birga, birgalikda",                       "ru": "вместе",                                     "tj": "якҷо, бо ҳам"},
        {"no": 9,  "zh": "要",     "pinyin": "yào",          "pos": "aux.",         "uz": "kerak, xohlamoq, bormoqchi",              "ru": "нужно, хотеть, собираться",                  "tj": "лозим, хостан, қасд доштан"},
        {"no": 10, "zh": "新",     "pinyin": "xīn",          "pos": "adj.",         "uz": "yangi",                                   "ru": "новый",                                      "tj": "нав"},
        {"no": 11, "zh": "它",     "pinyin": "tā",           "pos": "pron.",        "uz": "u (hayvon yoki narsa haqida)",            "ru": "оно, он/она (о животных и предметах)",       "tj": "он/он (дар бораи ҳайвон ё чиз)"},
        {"no": 12, "zh": "眼睛",   "pinyin": "yǎnjing",      "pos": "n.",           "uz": "ko'z",                                    "ru": "глаза",                                      "tj": "чашм"},
        {"no": 13, "zh": "花花",   "pinyin": "Huāhua",       "pos": "proper noun",  "uz": "Huahua (mushuk ismi)",                    "ru": "Хуахуа (кличка кошки)",                      "tj": "Хуахуа (номи гурба)"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Maktabda",
            "scene_ru": "В школе",
            "scene_tj": "Дар мактаб",
            "dialogue": [
                {"speaker": "A", "zh": "我想去北京旅游，你觉得什么时候去最好？", "pinyin": "Wǒ xiǎng qù Běijīng lǚyóu, nǐ juéde shénme shíhou qù zuì hǎo?", "uz": "Men Pekinga sayohat qilmoqchiman, sen qachon borish eng yaxshi deb o'ylaysan?", "ru": "Я хочу поехать в Пекин, как ты думаешь, когда лучше всего ехать?", "tj": "Ман мехоҳам ба Пекин сафар кунам, ба назари ту кай рафтан беҳтар аст?"},
                {"speaker": "B", "zh": "九月去北京旅游最好。",                     "pinyin": "Jiǔ yuè qù Běijīng lǚyóu zuì hǎo.",                              "uz": "Sent'abrda Pekinga sayohat qilish eng yaxshi.", "ru": "Лучше всего ехать в Пекин в сентябре.", "tj": "Дар моҳи сентябр сафар ба Пекин аз ҳама беҳтар аст."},
                {"speaker": "A", "zh": "为什么？",                               "pinyin": "Wèi shénme?",                                                      "uz": "Nega?", "ru": "Почему?", "tj": "Чаро?"},
                {"speaker": "B", "zh": "九月的北京天气不冷也不热。",               "pinyin": "Jiǔ yuè de Běijīng tiānqì bù lěng yě bú rè.",                     "uz": "Sent'abrda Pekingning ob-havosi sovuq ham emas, issiq ham emas.", "ru": "В сентябре в Пекине погода ни холодная, ни жаркая.", "tj": "Дар моҳи сентябр ҳавои Пекин на сард аст ва на гарм."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Suratlarni ko'rib",
            "scene_ru": "Рассматривая фотографии",
            "scene_tj": "Дар хонандани аксҳо",
            "dialogue": [
                {"speaker": "A", "zh": "你喜欢什么运动？",           "pinyin": "Nǐ xǐhuan shénme yùndòng?",            "uz": "Sen qanday sportni yaxshi ko'rasan?", "ru": "Какой спорт ты любишь?", "tj": "Ту кадом варзишро дӯст медорӣ?"},
                {"speaker": "B", "zh": "我最喜欢踢足球。",           "pinyin": "Wǒ zuì xǐhuan tī zúqiú.",              "uz": "Men futbol o'ynashni eng ko'p yaxshi ko'raman.", "ru": "Больше всего я люблю играть в футбол.", "tj": "Ман аз ҳама бештар футбол бозӣ кардан ро дӯст медорам."},
                {"speaker": "A", "zh": "下午我们一起去踢足球吧。",   "pinyin": "Xiàwǔ wǒmen yìqǐ qù tī zúqiú ba.",    "uz": "Tushdan keyin birga futbol o'ynamizmi?", "ru": "Давай после обеда вместе поиграем в футбол.", "tj": "Баъд аз нисфирӯзӣ биёед якҷо футбол бозем."},
                {"speaker": "B", "zh": "好啊！",                     "pinyin": "Hǎo a!",                               "uz": "Ha, albatta!", "ru": "Конечно!", "tj": "Хуб, бале!"},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "我们要不要买几个新的椅子？",  "pinyin": "Wǒmen yào bú yào mǎi jǐ ge xīn de yǐzi?", "uz": "Bir nechta yangi stul sotib olishimiz kerakmi?", "ru": "Нам купить несколько новых стульев?", "tj": "Мо бояд чанд курсии нав харем?"},
                {"speaker": "B", "zh": "好啊。什么时候去买？",        "pinyin": "Hǎo a. Shénme shíhou qù mǎi?",            "uz": "Ha. Qachon boramiz?", "ru": "Хорошо. Когда пойдём покупать?", "tj": "Хуб. Кай меравем харидан?"},
                {"speaker": "A", "zh": "明天下午怎么样？",            "pinyin": "Míngtiān xiàwǔ zěnmeyàng?",              "uz": "Ertaga tushdan keyin qanday?", "ru": "Как насчёт завтра после обеда?", "tj": "Фардо баъд аз нисфирӯзӣ чӣ тавр?"},
                {"speaker": "A", "zh": "你明天几点能回来？",          "pinyin": "Nǐ míngtiān jǐ diǎn néng huílái?",        "uz": "Ertaga sen necha da qaytib kelolasan?", "ru": "В котором часу ты завтра сможешь вернуться?", "tj": "Ту фардо соати чанд метавонӣ баргардӣ?"},
                {"speaker": "B", "zh": "三点多。",                   "pinyin": "Sān diǎn duō.",                           "uz": "Uchdan keyin (taxminan).", "ru": "Около трёх (чуть после).", "tj": "Каме баъд аз соати се."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "桌子下面有个猫。",                 "pinyin": "Zhuōzi xiàmiàn yǒu ge māo.",                             "uz": "Stol ostida mushuk bor.", "ru": "Под столом есть кошка.", "tj": "Зери мӯия як гурба аст."},
                {"speaker": "B", "zh": "那是我的猫，它叫花花。",           "pinyin": "Nà shì wǒ de māo, tā jiào Huāhua.",                     "uz": "Bu mening mushugim, u Huahua deb ataladi.", "ru": "Это моя кошка, её зовут Хуахуа.", "tj": "Ин гурбаи ман аст, номаш Хуахуа аст."},
                {"speaker": "A", "zh": "它很漂亮。",                       "pinyin": "Tā hěn piàoliang.",                                      "uz": "U juda chiroyli.", "ru": "Она очень красивая.", "tj": "Вай хеле зебо аст."},
                {"speaker": "B", "zh": "是啊，我觉得它的眼睛最漂亮。",     "pinyin": "Shì a, wǒ juéde tā de yǎnjing zuì piàoliang.",           "uz": "Ha, menimcha uning ko'zlari eng chiroyli.", "ru": "Да, я думаю, что её глаза самые красивые.", "tj": "Бале, ба назари ман чашмонаш аз ҳама зеботаранд."},
                {"speaker": "A", "zh": "它多大了？",                       "pinyin": "Tā duō dà le?",                                          "uz": "U qancha yoshda?", "ru": "Сколько ей лет?", "tj": "Вай чанд сол дорад?"},
                {"speaker": "B", "zh": "六个多月。",                       "pinyin": "Liù ge duō yuè.",                                        "uz": "Olti oydan ziyod.", "ru": "Больше шести месяцев.", "tj": "Зиёда аз шаш моҳ."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "助动词：要",
            "title_uz": "Yordamchi fe'l: 要",
            "title_ru": "Вспомогательный глагол: 要",
            "title_tj": "Феъли ёрдамӣ: 要",
            "rule_uz": (
                "'要' (yào) - istak yoki zaruriyatni bildiruvchi yordamchi fe'l. "
                "Fe'ldan oldin kelib, 'xohlamoq / bormoqchi / kerak' ma'nolarini beradi. "
                "Inkor shakli: 不要 (buyruq) yoki 不想 (istamaslik)."
            ),
            "rule_ru": (
                "'要' (yào) — вспомогательный глагол, выражающий желание или необходимость. "
                "Ставится перед основным глаголом, означает «хотеть / собираться / нужно». "
                "Отрицание: 不要 (запрет) или 不想 (нежелание)."
            ),
            "rule_tj": (
                "'要' (yào) — феъли ёрдамии ифодакунандаи хоҳиш ё зарурат. "
                "Пеш аз феъли асосӣ меояд ва маънои 'хостан / қасд доштан / лозим' дорад. "
                "Шакли инкорӣ: 不要 (манъ) ё 不想 (нахостан)."
            ),
            "examples": [
                {"zh": "我要去北京旅游。",       "pinyin": "Wǒ yào qù Běijīng lǚyóu.",    "uz": "Men Pekinga sayohat qilmoqchiman.", "ru": "Я собираюсь поехать в Пекин.", "tj": "Ман мехоҳам ба Пекин сафар кунам."},
                {"zh": "我们要不要买新椅子？",   "pinyin": "Wǒmen yào bú yào mǎi xīn yǐzi?", "uz": "Yangi stul sotib olishimiz kerakmi?", "ru": "Нам купить новые стулья?", "tj": "Мо бояд курсии нав харем?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "程度副词：最",
            "title_uz": "Daraja ravishi: 最",
            "title_ru": "Наречие степени: 最",
            "title_tj": "Зарфи дараҷа: 最",
            "rule_uz": (
                "'最' (zuì) - 'eng' ma'nosini beruvchi daraja ravishi. "
                "Sifat yoki fe'ldan oldin kelib, eng yuqori darajani bildiradi."
            ),
            "rule_ru": (
                "'最' (zuì) — наречие степени, означающее «самый, наиболее». "
                "Ставится перед прилагательным или глаголом и обозначает наивысшую степень."
            ),
            "rule_tj": (
                "'最' (zuì) — зарфи дараҷа бо маънои 'аз ҳама, бештар'. "
                "Пеш аз сифат ё феъл меояд ва дараҷаи аълоро ифода мекунад."
            ),
            "examples": [
                {"zh": "九月去北京旅游最好。",   "pinyin": "Jiǔ yuè qù Běijīng lǚyóu zuì hǎo.", "uz": "Pekinga sent'abrda borish eng yaxshi.", "ru": "Лучше всего ехать в Пекин в сентябре.", "tj": "Дар моҳи сентябр сафар ба Пекин аз ҳама беҳтар аст."},
                {"zh": "我最喜欢踢足球。",       "pinyin": "Wǒ zuì xǐhuan tī zúqiú.",           "uz": "Men eng ko'p futbol o'ynashni yaxshi ko'raman.", "ru": "Больше всего я люблю играть в футбол.", "tj": "Ман аз ҳама бештар футбол бозӣ кардан ро дӯст медорам."},
            ]
        },
        {
            "no": 3,
            "title_zh": "概数的表达：几、多",
            "title_uz": "Taxminiy sonlar: 几、多",
            "title_ru": "Приблизительные числа: 几、多",
            "title_tj": "Рақамҳои тахминӣ: 几、多",
            "rule_uz": (
                "Taxminiy sonni ifodalash usullari:\n"
                "• 几 (jǐ) — 'bir nechta' (odatda 10 gacha), noaniq miqdor.\n"
                "• 多 (duō) — son + ölçü + 多 shaklida 'dan ko'proq, ziyod' ma'nosini beradi."
            ),
            "rule_ru": (
                "Способы выражения приблизительного числа:\n"
                "• 几 (jǐ) — «несколько» (обычно до 10), неопределённое количество.\n"
                "• 多 (duō) — после числа + счётного слова означает «с лишним, больше»."
            ),
            "rule_tj": (
                "Усулҳои ифодаи рақамҳои тахминӣ:\n"
                "• 几 (jǐ) — 'чанд' (одатан то 10), миқдори номуайян.\n"
                "• 多 (duō) — баъд аз рақам + воҳид маънои 'зиёда аз, бештар' дорад."
            ),
            "examples": [
                {"zh": "这里有几个杯子。",   "pinyin": "Zhèlǐ yǒu jǐ ge bēizi.",  "uz": "Bu yerda bir nechta qadah bor.", "ru": "Здесь есть несколько стаканов.", "tj": "Инҷо чанд косача вуҷуд дорад."},
                {"zh": "它六个多月了。",     "pinyin": "Tā liù ge duō yuè le.",    "uz": "U olti oydan ziyod bo'ldi.", "ru": "Ей уже больше шести месяцев.", "tj": "Вай зиёда аз шаш моҳ шудааст."},
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
                {"prompt_uz": "sayohat qilmoq",    "prompt_ru": "путешествовать",    "prompt_tj": "сафар кардан",     "answer": "旅游",   "pinyin": "lǚyóu"},
                {"prompt_uz": "eng, juda",          "prompt_ru": "самый, наиболее",   "prompt_tj": "аз ҳама, бештар", "answer": "最",     "pinyin": "zuì"},
                {"prompt_uz": "birga, birgalikda",  "prompt_ru": "вместе",            "prompt_tj": "якҷо, бо ҳам",    "answer": "一起",   "pinyin": "yìqǐ"},
                {"prompt_uz": "ko'z",               "prompt_ru": "глаза",             "prompt_tj": "чашм",            "answer": "眼睛",   "pinyin": "yǎnjing"},
                {"prompt_uz": "yangi",              "prompt_ru": "новый",             "prompt_tj": "нав",             "answer": "新",     "pinyin": "xīn"},
            ]
        },
        {
            "no": 2,
            "type": "translate_to_uzbek",
            "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
            "instruction_ru": "Напишите узбекский эквивалент следующих слов:",
            "instruction_tj": "Маъноро ба забони ӯзбекӣ нависед:",
            "items": [
                {"prompt_uz": "觉得",   "answer": "deb o'ylash, his qilish", "pinyin": "juéde"},
                {"prompt_uz": "运动",   "answer": "sport; sport qilmoq",     "pinyin": "yùndòng"},
                {"prompt_uz": "它",     "answer": "u (hayvon/narsa uchun)",  "pinyin": "tā"},
                {"prompt_uz": "为什么", "answer": "nega, nima uchun",        "pinyin": "wèi shénme"},
            ]
        },
        {
            "no": 3,
            "type": "fill_blank",
            "instruction_uz": "Mos so'zni tanlang (要、最、也、几、一起):",
            "instruction_ru": "Выберите подходящее слово (要、最、也、几、一起):",
            "instruction_tj": "Калимаи мувофиқро интихоб кунед (要、最、也、几、一起):",
            "items": [
                {"prompt_uz": "九月的北京天气不冷___不热。",           "answer": "也",   "pinyin": "yě"},
                {"prompt_uz": "我___去北京旅游。",                    "answer": "要",   "pinyin": "yào"},
                {"prompt_uz": "下午我们___去踢足球吧。",              "answer": "一起", "pinyin": "yìqǐ"},
                {"prompt_uz": "我___喜欢踢足球。",                   "answer": "最",   "pinyin": "zuì"},
                {"prompt_uz": "这里有___个杯子，哪个是你的？",        "answer": "几",   "pinyin": "jǐ"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["旅游", "最", "一起", "眼睛", "新"]},
        {"no": 2, "answers": ["deb o'ylash, his qilish", "sport; sport qilmoq", "u (hayvon/narsa uchun)", "nega, nima uchun"]},
        {"no": 3, "answers": ["也", "要", "一起", "最", "几"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib 3 ta gap tuzing:",
            "instruction_ru": "Составьте 3 предложения, используя следующие слова:",
            "instruction_tj": "Бо истифода аз калимаҳои зерин 3 ҷумла тартиб диҳед:",
            "words": ["旅游", "最", "一起", "运动"],
            "example": "我觉得九月去北京旅游最好，我们一起去吧！",
        },
        {
            "no": 2,
            "instruction_uz": "5-6 gapdan iborat kichik matn yozing: 'Sevimli sportim va uni qachon, kim bilan qilishim haqida'.",
            "instruction_ru": "Напишите небольшой текст из 5–6 предложений: «О моём любимом спорте, когда и с кем я им занимаюсь».",
            "instruction_tj": "Матни хурде аз 5-6 ҷумла нависед: «Дар бораи варзиши дӯстдоштаи ман, кай ва бо кӣ машғул мешавам».",
            "topic_uz": "我最喜欢的运动",
            "topic_ru": "Мой любимый вид спорта",
            "topic_tj": "Варзиши дӯстдоштаи ман",
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
