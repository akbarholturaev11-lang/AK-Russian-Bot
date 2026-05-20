import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 4,
    "lesson_code": "HSK2-L04",
    "title": "这个工作是他帮我介绍的",
    "goal": json.dumps({
        "uz": "O'tgan hodisalarning vaqti, joyi va usulini ta'kidlab gapira olish; '是……的' qolipini, 给 old ko'makchisini va 已经 ravishini o'zlashtirish.",
        "ru": "Научиться делать акцент на времени, месте и способе совершения прошедшего действия; освоить конструкцию 是……的, предлог 给 и наречие 已经.",
        "tj": "Таъкид кардан ба вақт, ҷой ва усули амали гузашта; азхудкунии конструксияи 是……的, пешоянди 给 ва зарфи 已经.",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Bu darsda o'tgan voqealarni aniq tushuntirishni o'rganamiz: kim qildi, qachon qildi, qayerda qildi. Tug'ilgan kun, telefon suhbati, sport va ish mavzularida suhbat qilasiz. Asosiy grammatik mavzular: '是……的' qolipida ta'kidlash, 给 old ko'makchisi va 已经 ravishi.",
        "ru": "На этом уроке мы учимся точно объяснять прошедшие события: кто сделал, когда сделал, где сделал. Вы будете говорить о дне рождения, телефонном разговоре, спорте и работе. Основные грамматические темы: выделение с помощью 是……的, предлог 给 и наречие 已经.",
        "tj": "Дар ин дарс мо ёд мегирем, ки рӯйдодҳои гузаштаро дақиқ шарҳ диҳем: кӣ кард, кай кард, дар куҷо кард. Шумо дар бораи таваллуд, сӯҳбати телефонӣ, варзиш ва кор гап мезанед. Мавзӯҳои асосии грамматикӣ: таъкид бо 是……的, пешоянди 给 ва зарфи 已经.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "生日",  "pinyin": "shēngrì",  "pos": "n.",    "uz": "tug'ilgan kun",                           "ru": "день рождения",                   "tj": "рӯзи таваллуд"},
        {"no": 2,  "zh": "快乐",  "pinyin": "kuàilè",   "pos": "adj.", "uz": "baxtli, xursand",                         "ru": "счастливый, радостный",           "tj": "хушбахт, шод"},
        {"no": 3,  "zh": "给",    "pinyin": "gěi",       "pos": "prep.", "uz": "uchun, ga (kimgadir berish yoki yo'naltirish)", "ru": "для, кому (давать или направлять)", "tj": "барои, ба (додан ё равона кардан)"},
        {"no": 4,  "zh": "接",    "pinyin": "jiē",       "pos": "v.",    "uz": "qabul qilmoq, olmoq; telefonga javob bermoq", "ru": "принимать, получать; отвечать на телефон", "tj": "қабул кардан; ба телефон ҷавоб додан"},
        {"no": 5,  "zh": "晚上",  "pinyin": "wǎnshang", "pos": "n.",    "uz": "kecha, kechqurun",                        "ru": "вечер, вечером",                  "tj": "шом, шабонгоҳ"},
        {"no": 6,  "zh": "问",    "pinyin": "wèn",       "pos": "v.",    "uz": "so'ramoq",                                "ru": "спрашивать",                      "tj": "пурсидан"},
        {"no": 7,  "zh": "非常",  "pinyin": "fēicháng", "pos": "adv.", "uz": "juda, nihoyatda",                         "ru": "очень, чрезвычайно",              "tj": "хеле, бағоят"},
        {"no": 8,  "zh": "开始",  "pinyin": "kāishǐ",   "pos": "v.",    "uz": "boshlamoq, boshlanmoq",                  "ru": "начинать, начинаться",            "tj": "оғоз кардан, шурӯъ кардан"},
        {"no": 9,  "zh": "已经",  "pinyin": "yǐjīng",   "pos": "adv.", "uz": "allaqachon, avvaldan",                    "ru": "уже",                             "tj": "аллакай, пешакӣ"},
        {"no": 10, "zh": "长",    "pinyin": "cháng",     "pos": "adj.", "uz": "uzun; (vaqt) uzoq",                       "ru": "длинный; (о времени) долгий",     "tj": "дароз; (вақт) тӯлонӣ"},
        {"no": 11, "zh": "两",    "pinyin": "liǎng",     "pos": "num.", "uz": "ikki (ko'makchi bilan birga ishlatiladi)", "ru": "два (используется со счётным словом)", "tj": "ду (бо воҳид истифода мешавад)"},
        {"no": 12, "zh": "帮",    "pinyin": "bāng",      "pos": "v.",    "uz": "yordam bermoq",                           "ru": "помогать",                        "tj": "кӯмак кардан"},
        {"no": 13, "zh": "介绍",  "pinyin": "jièshào",  "pos": "v.",    "uz": "tanishtirmoq, tavsiya qilmoq",           "ru": "знакомить, представлять; рекомендовать", "tj": "шинос кардан; тавсия додан"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Darsxonada",
            "scene_ru": "В классе",
            "scene_tj": "Дар синфхона",
            "dialogue": [
                {"speaker": "A", "zh": "生日快乐！这是送给你的！", "pinyin": "Shēngrì kuàilè! Zhè shì sòng gěi nǐ de!", "uz": "Tug'ilgan kuning bilan! Bu senga sovg'a!", "ru": "С днём рождения! Это тебе подарок!", "tj": "Рӯзи таваллудат муборак! Ин барои ту тӯҳфа аст!"},
                {"speaker": "B", "zh": "是什么？是一本书吗？", "pinyin": "Shì shénme? Shì yì běn shū ma?", "uz": "Bu nima? Kitobmi?", "ru": "Что это? Книга?", "tj": "Ин чист? Китоб аст?"},
                {"speaker": "A", "zh": "对，这本书是我写给你的。", "pinyin": "Duì, zhè běn shū shì wǒ xiě gěi nǐ de.", "uz": "Ha, bu kitobni men sen uchun yozdim.", "ru": "Да, эту книгу я написал для тебя.", "tj": "Бале, ин китобро ман барои ту навиштам."},
                {"speaker": "B", "zh": "太谢谢你了！", "pinyin": "Tài xièxie nǐ le!", "uz": "Juda rahmat!", "ru": "Огромное спасибо!", "tj": "Хеле ташаккур!"},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "早上有你一个电话。", "pinyin": "Zǎoshang yǒu nǐ yí ge diànhuà.", "uz": "Ertalab seni bir kishi qo'ng'iroq qildi.", "ru": "Утром тебе звонили.", "tj": "Субҳ ба ту як нафар занг зад."},
                {"speaker": "B", "zh": "电话是谁打的？", "pinyin": "Diànhuà shì shéi dǎ de?", "uz": "Telefon kimdan edi?", "ru": "Кто звонил?", "tj": "Занг аз кӣ буд?"},
                {"speaker": "A", "zh": "不知道，是儿子接的。", "pinyin": "Bù zhīdào, shì érzi jiē de.", "uz": "Bilmadim, o'g'lim qabul qildi.", "ru": "Не знаю, трубку взял сын.", "tj": "Намедонам, писарам ҷавоб дод."},
                {"speaker": "B", "zh": "好，晚上我问一下儿子。", "pinyin": "Hǎo, wǎnshang wǒ wèn yíxià érzi.", "uz": "Yaxshi, kechqurun o'g'limdan so'rayman.", "ru": "Хорошо, вечером спрошу у сына.", "tj": "Хуб, шом аз писарам мепурсам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Sport maydonchasida",
            "scene_ru": "На спортивной площадке",
            "scene_tj": "Дар майдони варзишӣ",
            "dialogue": [
                {"speaker": "A", "zh": "你喜欢踢足球吗？", "pinyin": "Nǐ xǐhuan tī zúqiú ma?", "uz": "Futbol o'ynashni yaxshi ko'rasanmi?", "ru": "Тебе нравится играть в футбол?", "tj": "Оё ту футбол бозӣ кардан ро дӯст медорӣ?"},
                {"speaker": "B", "zh": "非常喜欢。", "pinyin": "Fēicháng xǐhuan.", "uz": "Juda yaxshi ko'raman.", "ru": "Очень нравится.", "tj": "Хеле дӯст медорам."},
                {"speaker": "A", "zh": "你是什么时候开始踢足球的？", "pinyin": "Nǐ shì shénme shíhou kāishǐ tī zúqiú de?", "uz": "Sen qachon futbol o'ynashni boshlagansan?", "ru": "Когда ты начал играть в футбол?", "tj": "Ту кай футбол бозӣ карданро оғоз кардӣ?"},
                {"speaker": "B", "zh": "我十一岁的时候开始踢足球，已经踢了十年了。", "pinyin": "Wǒ shíyī suì de shíhou kāishǐ tī zúqiú, yǐjīng tī le shí nián le.", "uz": "Men o'n bir yoshimda futbol o'ynashni boshladim, allaqachon o'n yil bo'ldi.", "ru": "Я начал играть в футбол в одиннадцать лет, уже прошло десять лет.", "tj": "Ман дар синни ёздаҳсолагӣ футбол бозӣ карданро оғоз кардам, аллакай даҳ сол шудааст."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Kompaniyada",
            "scene_ru": "В компании",
            "scene_tj": "Дар ширкат",
            "dialogue": [
                {"speaker": "A", "zh": "你在这儿工作多长时间了？", "pinyin": "Nǐ zài zhèr gōngzuò duō cháng shíjiān le?", "uz": "Bu yerda qancha vaqtdan beri ishlayapsan?", "ru": "Сколько времени ты здесь работаешь?", "tj": "Ту аз кай инҷо кор мекунӣ?"},
                {"speaker": "B", "zh": "已经两年多了，我是2011年来的。", "pinyin": "Yǐjīng liǎng nián duō le, wǒ shì èr líng yī yī nián lái de.", "uz": "Allaqachon ikki yildan oshdi, men 2011-yilda kelgan edim.", "ru": "Уже больше двух лет, я приехал в 2011 году.", "tj": "Аллакай зиёда аз ду сол, ман соли 2011 омадам."},
                {"speaker": "A", "zh": "你认识谢先生吗？", "pinyin": "Nǐ rènshi Xiè xiānsheng ma?", "uz": "Xie janobini tanaysanmi?", "ru": "Вы знакомы с господином Се?", "tj": "Оё шумо ҷаноби Ксиеро мешиносед?"},
                {"speaker": "B", "zh": "认识，我们是大学同学，这个工作是他帮我介绍的。", "pinyin": "Rènshi, wǒmen shì dàxué tóngxué, zhège gōngzuò shì tā bāng wǒ jièshào de.", "uz": "Ha, biz universitetda bir guruhda o'qiganmiz, bu ishni u menga tavsiya qilgan edi.", "ru": "Знаком, мы однокурсники в университете, именно он порекомендовал мне эту работу.", "tj": "Мешиносам, мо дар донишгоҳ ҳамгурӯҳ будем, ӯ ин корро ба ман тавсия кард."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "“是……的”句：强调施事",
            "title_uz": "'是……的' qolipi: ta'kidlash",
            "title_ru": "Конструкция 是……的: выделение",
            "title_tj": "Конструксияи 是……的: таъкид",
            "rule_uz": "'是……的' qolipida o'tgan hodisaning vaqti, joyi yoki usuli ta'kidlanadi. Gap tuzilishi: 是 + ta'kidlanadigan ma'lumot + fe'l + 的. Bu qolip hodisaning o'zi emas, balki uning qanday, qachon yoki kim tomonidan bajarilgani muhim bo'lganda ishlatiladi.",
            "rule_ru": "Конструкция 是……的 подчёркивает время, место или способ совершения прошедшего действия. Структура: 是 + выделяемая информация + глагол + 的. Используется, когда важен не сам факт действия, а то как, когда или кем оно было выполнено.",
            "rule_tj": "Конструксияи 是……的 вақт, ҷой ё усули амали гузаштаро таъкид мекунад. Сохтор: 是 + маълумоти таъкидшаванда + феъл + 的. Вақте истифода мешавад, ки на худи амал, балки чӣ тавр, кай ё аз ҷониби кӣ иҷро шудани он муҳим аст.",
            "examples": [
                {"zh": "这个工作是他帮我介绍的。", "pinyin": "Zhège gōngzuò shì tā bāng wǒ jièshào de.", "uz": "Bu ishni u menga tavsiya qilgan edi.", "ru": "Именно он порекомендовал мне эту работу.", "tj": "Ин корро ӯ ба ман тавсия кард."},
                {"zh": "我是2011年来的。", "pinyin": "Wǒ shì èr líng yī yī nián lái de.", "uz": "Men 2011-yilda kelgan edim.", "ru": "Я приехал именно в 2011 году.", "tj": "Ман маҳз соли 2011 омадам."},
            ]
        },
        {
            "no": 2,
            "title_zh": "表示时间：……的时候",
            "title_uz": "Vaqtni ifodalash: ……的时候",
            "title_ru": "Выражение времени: ……的时候",
            "title_tj": "Ифодаи вақт: ……的时候",
            "rule_uz": "'……的时候' qolipida biror ish yuz bergan vaqt ko'rsatiladi. O'zbek tilidagi '……paytida, ……vaqtida' iborasiga to'g'ri keladi.",
            "rule_ru": "Конструкция ……的时候 указывает на момент, когда произошло действие. Соответствует русскому «когда…, в то время как…».",
            "rule_tj": "Конструксияи ……的时候 вақти вуқӯи амалро нишон медиҳад. Ба ибораи тоҷикии '……вақте ки, дар вақти……' мувофиқ аст.",
            "examples": [
                {"zh": "我十一岁的时候开始踢足球。", "pinyin": "Wǒ shíyī suì de shíhou kāishǐ tī zúqiú.", "uz": "Men o'n bir yoshimda futbol o'ynashni boshladim.", "ru": "Я начал играть в футбол, когда мне было одиннадцать лет.", "tj": "Ман дар синни ёздаҳсолагӣ футбол бозӣ карданро оғоз кардам."},
                {"zh": "刚结婚的时候，每天都很浪漫。", "pinyin": "Gāng jiéhūn de shíhou, měitiān dōu hěn làngmàn.", "uz": "Yangi turmush qurgan paytimizda har kun romantik edi.", "ru": "Когда мы только поженились, каждый день был романтичным.", "tj": "Вақте ки тоза издивоҷ кардем, ҳар рӯз романтикӣ буд."},
            ]
        },
        {
            "no": 3,
            "title_zh": "时间副词“已经”",
            "title_uz": "Vaqt ravishi '已经'",
            "title_ru": "Наречие времени 已经",
            "title_tj": "Зарфи вақт 已经",
            "rule_uz": "'已经' ravishi 'allaqachon' ma'nosini beradi. U fe'ldan oldin keladi va ko'pincha '了' bilan birga ishlatiladi. Biror harakatning avvalroq bajarilganini ta'kidlaydi.",
            "rule_ru": "Наречие 已经 означает «уже». Ставится перед глаголом и часто используется в связке с 了. Подчёркивает, что действие совершилось ранее.",
            "rule_tj": "Зарфи 已经 маънои 'аллакай' дорад. Пеш аз феъл меояд ва аксар бо 了 дар якҷоягӣ истифода мешавад. Таъкид мекунад, ки амал пешак иҷро шудааст.",
            "examples": [
                {"zh": "已经踢了十年了。", "pinyin": "Yǐjīng tī le shí nián le.", "uz": "Allaqachon o'n yil bo'ldi.", "ru": "Уже прошло десять лет.", "tj": "Аллакай даҳ сол шудааст."},
                {"zh": "我已经吃饭了。", "pinyin": "Wǒ yǐjīng chīfàn le.", "uz": "Men allaqachon ovqatlandim.", "ru": "Я уже поел.", "tj": "Ман аллакай хӯрок хӯрдам."},
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
                {"prompt_uz": "tug'ilgan kun", "prompt_ru": "день рождения", "prompt_tj": "рӯзи таваллуд", "answer": "生日", "pinyin": "shēngrì"},
                {"prompt_uz": "yordam bermoq", "prompt_ru": "помогать", "prompt_tj": "кӯмак кардан", "answer": "帮", "pinyin": "bāng"},
                {"prompt_uz": "tanishtirmoq", "prompt_ru": "знакомить, рекомендовать", "prompt_tj": "шинос кардан", "answer": "介绍", "pinyin": "jièshào"},
                {"prompt_uz": "boshlamoq", "prompt_ru": "начинать", "prompt_tj": "оғоз кардан", "answer": "开始", "pinyin": "kāishǐ"},
                {"prompt_uz": "allaqachon", "prompt_ru": "уже", "prompt_tj": "аллакай", "answer": "已经", "pinyin": "yǐjīng"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (是……的、已经、给、非常、的时候):",
            "instruction_ru": "Вставьте подходящее слово (是……的、已经、给、非常、的时候):",
            "instruction_tj": "Калимаи мувофиқро нависед (是……的、已经、给、非常、的时候):",
            "items": [
                {"prompt_uz": "这本书______我写______你______。", "answer": "是 / 给 / 的", "pinyin": "shì / gěi / de"},
                {"prompt_uz": "我______来这儿两年多了。", "answer": "已经", "pinyin": "yǐjīng"},
                {"prompt_uz": "我十一岁______，开始踢足球。", "answer": "的时候", "pinyin": "de shíhou"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_uzbek",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на узбекский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони ӯзбекӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "这个工作是他帮我介绍的。", "answer": "Bu ishni u menga tavsiya qilgan edi.", "pinyin": "Zhège gōngzuò shì tā bāng wǒ jièshào de."},
                {"prompt_uz": "我已经踢了十年足球了。", "answer": "Men allaqachon o'n yil futbol o'ynayapman.", "pinyin": "Wǒ yǐjīng tī le shí nián zúqiú le."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["生日", "帮", "介绍", "开始", "已经"]},
        {"no": 2, "answers": ["是 / 给 / 的", "已经", "的时候"]},
        {"no": 3, "answers": ["Bu ishni u menga tavsiya qilgan edi.", "Men allaqachon o'n yil futbol o'ynayapman."]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'是……的' qolipidan foydalanib 4 ta gap tuzing. Har bir gapda vaqt, joy yoki shaxsni ta'kidlang.",
            "instruction_ru": "Составьте 4 предложения с конструкцией 是……的. В каждом предложении выделите время, место или лицо.",
            "instruction_tj": "Бо конструксияи 是……的 чор ҷумла тартиб диҳед. Дар ҳар ҷумла вақт, ҷой ё шахсро таъкид кунед.",
            "words": ["是……来的", "是……买的", "是……帮……介绍的", "是……开始的"],
            "example": "这件衣服是我在北京买的。",
        },
        {
            "no": 2,
            "instruction_uz": "O'zingiz haqingizda 5-6 gapdan iborat kichik matn yozing. 已经, 的时候, 非常 so'zlarini ishlating.",
            "instruction_ru": "Напишите небольшой текст из 5–6 предложений о себе. Используйте слова 已经, 的时候, 非常.",
            "instruction_tj": "Матни хурде аз 5-6 ҷумла дар бораи худ нависед. Калимаҳои 已经, 的时候, 非常 -ро истифода баред.",
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
