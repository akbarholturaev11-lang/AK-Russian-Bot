import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 9,
    "lesson_code": "HSK2-L09",
    "title": "题太多，我没做完",
    "goal": json.dumps({"uz": "Natija fe'llari, 'cóng' old ko'makchisi va 'dì' tartib ko'rsatkichi yordamida gaplar tuzishni o'rganish.", "ru": "Научиться строить предложения с результативными глаголами, предлогом 'cóng' и порядковым показателем 'dì'.", "tj": "Омӯзиши тартиб додани ҷумлаҳо бо феълҳои натиҷавӣ, пешоянди 'cóng' ва нишондиҳандаи тартиби 'dì'."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda biz xato qilish, biror narsani boshlamoq va tartib ifodalash bilan bog'liq so'zlarni o'rganamiz. Telefon suhbati, maktab va ish hayotidan olingan voqealar orqali natija bildiruvchi fe'l qo'shimchalaridan foydalanishni mashq qilamiz. Shuningdek, 'cóng' (dan/boshlab) va 'dì' (tartib ko'rsatkichi) kabi muhim grammatik qurilmalarni o'zlashtiramiz.", "ru": "В этом уроке мы изучаем слова, связанные с ошибками, началом чего-либо и выражением порядка. Практикуем использование результативных суффиксов глаголов через телефонный разговор, школьные и рабочие ситуации. Также осваиваем важные грамматические конструкции: 'cóng' (от/начиная с) и 'dì' (порядковый показатель).", "tj": "Дар ин дарс мо калимаҳои марбут ба хато кардан, оғоз кардан ва ифодаи тартибро меомӯзем. Истифодаи суффиксҳои феъли натиҷавиро тавассути муколамаи телефонӣ, ҳодисаҳои мактабӣ ва корӣ машқ мекунем. Инчунин сохторҳои муҳими грамматикии 'cóng' (аз/аз ибтидои) ва 'dì' (нишондиҳандаи тартиб)-ро аз бар мекунем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "错",   "pinyin": "cuò",      "pos": "adj.",  "uz": "xato, noto'g'ri",                  "ru": "неправильный, ошибочный",            "tj": "хато, нодуруст"},
        {"no": 2,  "zh": "从",   "pinyin": "cóng",     "pos": "prep.", "uz": "dan, boshlab (joy yoki vaqt)",     "ru": "от, с, начиная с (место или время)", "tj": "аз, аз ибтидои (ҷой ё вақт)"},
        {"no": 3,  "zh": "跳舞", "pinyin": "tiàowǔ",   "pos": "v.",    "uz": "raqs tushmoq",                     "ru": "танцевать",                          "tj": "рақс кардан"},
        {"no": 4,  "zh": "第一", "pinyin": "dìyī",     "pos": "num.",  "uz": "birinchi",                         "ru": "первый",                             "tj": "аввалин, якум"},
        {"no": 5,  "zh": "希望", "pinyin": "xīwàng",   "pos": "v.",    "uz": "umid qilmoq, xohlamoq",            "ru": "надеяться, желать",                  "tj": "умед доштан, орзу кардан"},
        {"no": 6,  "zh": "问题", "pinyin": "wèntí",    "pos": "n.",    "uz": "savol, muammo",                    "ru": "вопрос, проблема",                   "tj": "савол, мушкил"},
        {"no": 7,  "zh": "欢迎", "pinyin": "huānyíng", "pos": "v.",    "uz": "xush kelibsiz, kutib olmoq",       "ru": "добро пожаловать, приветствовать",   "tj": "хуш омадед, пешвоз гирифтан"},
        {"no": 8,  "zh": "上班", "pinyin": "shàngbān", "pos": "v.",    "uz": "ishga bormoq, ishlamoq",           "ru": "идти на работу, работать",           "tj": "ба кор рафтан, кор кардан"},
        {"no": 9,  "zh": "懂",   "pinyin": "dǒng",     "pos": "v.",    "uz": "tushunmoq",                        "ru": "понимать",                           "tj": "фаҳмидан"},
        {"no": 10, "zh": "完",   "pinyin": "wán",       "pos": "v.",    "uz": "tugamoq, tamomlamoq",              "ru": "заканчивать, завершать",             "tj": "тамом кардан, ба охир расидан"},
        {"no": 11, "zh": "题",   "pinyin": "tí",        "pos": "n.",    "uz": "savol, topshiriq, masala",         "ru": "вопрос, задание, задача",            "tj": "савол, супориш, масъала"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Telefon qo'ng'iroqi",
            "scene_ru": "Телефонный разговор",
            "scene_tj": "Занги телефон",
            "dialogue": [
                {"speaker": "A", "zh": "你好！请问张欢在吗？", "pinyin": "Nǐ hǎo! Qǐngwèn Zhāng Huān zài ma?", "uz": "Salom! Iltimos, Chjan Xuan bormi?", "ru": "Здравствуйте! Скажите, Чжан Хуань здесь?", "tj": "Салом! Лутфан, Чжан Хуан ҳаст?"},
                {"speaker": "B", "zh": "你打错了，我们这儿没有叫张欢的。", "pinyin": "Nǐ dǎ cuò le, wǒmen zhèr méiyǒu jiào Zhāng Huān de.", "uz": "Siz xato raqamga terdingiz, bizda Chjan Xuan ismli odam yo'q.", "ru": "Вы набрали неправильный номер, у нас нет человека по имени Чжан Хуань.", "tj": "Шумо рақами хато зададед, дар ин ҷо Чжан Хуан нест."},
                {"speaker": "A", "zh": "对不起。", "pinyin": "Duìbuqǐ.", "uz": "Kechirasiz.", "ru": "Извините.", "tj": "Бубахшед."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Maktabda",
            "scene_ru": "В школе",
            "scene_tj": "Дар мактаб",
            "dialogue": [
                {"speaker": "A", "zh": "您从几岁开始学跳舞？", "pinyin": "Nín cóng jǐ suì kāishǐ xué tiàowǔ?", "uz": "Siz necha yoshdan raqs o'rganishni boshladingiz?", "ru": "С какого возраста вы начали учиться танцевать?", "tj": "Шумо аз чанд солагӣ рақс омӯхтанро оғоз кардед?"},
                {"speaker": "B", "zh": "我第一次跳舞是在七岁的时候。", "pinyin": "Wǒ dì yī cì tiàowǔ shì zài qī suì de shíhou.", "uz": "Men birinchi marta etti yoshimda raqs tushganman.", "ru": "Я впервые станцевал в семь лет.", "tj": "Ман бори аввал дар ҳафт солагӣ рақс кардам."},
                {"speaker": "A", "zh": "我女儿今年七岁了。我希望她能跟您学跳舞，可以吗？", "pinyin": "Wǒ nǚ'ér jīnnián qī suì le. Wǒ xīwàng tā néng gēn nín xué tiàowǔ, kěyǐ ma?", "uz": "Mening qizim bu yil etti yoshga kirdi. Umid qilamanki u sizdan raqs o'rgansa bo'ladimi?", "ru": "Моей дочери в этом году исполнилось семь лет. Я надеюсь, она сможет учиться танцевать у вас, можно?", "tj": "Духтарам имсол ҳафт сола шуд. Умедворам, ки вай метавонад назди шумо рақс ёд гирад, мумкин?"},
                {"speaker": "B", "zh": "没问题，非常欢迎。", "pinyin": "Méi wèntí, fēicháng huānyíng.", "uz": "Muammo yo'q, juda xush kelibsiz.", "ru": "Нет проблем, очень рады.", "tj": "Мушкил нест, хуш омадед."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "你知道吗？大卫找到工作了。", "pinyin": "Nǐ zhīdào ma? Dàwèi zhǎodào gōngzuò le.", "uz": "Bilasizmi? Devid ish topdi.", "ru": "Знаешь? Дэвид нашёл работу.", "tj": "Медонӣ? Дэвид кор ёфт."},
                {"speaker": "B", "zh": "太好了！他从什么时候开始上班？", "pinyin": "Tài hǎo le! Tā cóng shénme shíhou kāishǐ shàngbān?", "uz": "Juda yaxshi! U qachondan boshlab ishga chiqadi?", "ru": "Отлично! С какого времени он начнёт работать?", "tj": "Аъло! Вай аз кай кор мекунад?"},
                {"speaker": "A", "zh": "从下个星期一开始。", "pinyin": "Cóng xià ge xīngqīyī kāishǐ.", "uz": "Kelasi dushanba kundan boshlab.", "ru": "С ближайшего понедельника.", "tj": "Аз душанбаи оянда."},
                {"speaker": "B", "zh": "这是他的第一个工作，希望他能喜欢。", "pinyin": "Zhè shì tā de dì yī ge gōngzuò, xīwàng tā néng xǐhuan.", "uz": "Bu uning birinchi ishi, umid qilamanki yoqadi.", "ru": "Это его первая работа, надеюсь, ему понравится.", "tj": "Ин кори аввалинаш аст, умедворам, ки писандаш ояд."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Darsxonada",
            "scene_ru": "В классе",
            "scene_tj": "Дар синфхона",
            "dialogue": [
                {"speaker": "A", "zh": "昨天的考试怎么样？你都听懂了吗？", "pinyin": "Zuótiān de kǎoshì zěnmeyàng? Nǐ dōu tīngdǒng le ma?", "uz": "Kechagi imtihon qanday o'tdi? Hamma narsani eshitib tushundingizmi?", "ru": "Как вчерашний экзамен? Ты всё понял на слух?", "tj": "Имтиҳони дирӯз чӣ тавр гузашт? Оё ту ҳама чизро шунида фаҳмидӣ?"},
                {"speaker": "B", "zh": "听懂了。", "pinyin": "Tīngdǒng le.", "uz": "Eshitib tushundim.", "ru": "Всё понял на слух.", "tj": "Шунида фаҳмидам."},
                {"speaker": "A", "zh": "你都做完了没有？", "pinyin": "Nǐ dōu zuòwán le méiyǒu?", "uz": "Hammasini bajardingizmi?", "ru": "Ты всё выполнил?", "tj": "Оё ту ҳамаро иҷро кардӣ?"},
                {"speaker": "B", "zh": "题太多，我没做完。", "pinyin": "Tí tài duō, wǒ méi zuòwán.", "uz": "Savollar juda ko'p edi, men tamomlab ulgurmadim.", "ru": "Заданий было слишком много, я не успел сделать всё.", "tj": "Саволҳо бисёр буданд, ман нарасидам тамом кунам."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "结果补语",
            "title_uz": "Natija to'ldiruvchisi (结果补语)",
            "title_ru": "Результативное дополнение (结果补语)",
            "title_tj": "Пуркунандаи натиҷавӣ (结果补语)",
            "rule_uz": (
                "Natija to'ldiruvchisi (结果补语) fe'ldan keyin qo'shilib, harakatning natijasini bildiradi.\n"
                "Masalan: 听懂 (eshitib tushunmoq), 做完 (tamomlamoq), 找到 (topmoq).\n"
                "Inkor shaklida 没 yoki 没有 ishlatiladi: 没做完 (tamomlaolmadim)."
            ),
            "rule_ru": (
                "Результативное дополнение (结果补语) добавляется после глагола и выражает результат действия.\n"
                "Например: 听懂 (услышать и понять), 做完 (закончить), 找到 (найти).\n"
                "В отрицании используется 没 или 没有: 没做完 (не успел закончить)."
            ),
            "rule_tj": (
                "Пуркунандаи натиҷавӣ (结果补语) баъд аз феъл илова мешавад ва натиҷаи амалро нишон медиҳад.\n"
                "Масалан: 听懂 (шунида фаҳмидан), 做完 (тамом кардан), 找到 (ёфтан).\n"
                "Дар инкор 没 ё 没有 истифода мешавад: 没做完 (нарасидам тамом кунам)."
            ),
            "examples": [
                {"zh": "我听懂了。", "pinyin": "Wǒ tīngdǒng le.", "uz": "Men eshitib tushundim.", "ru": "Я понял на слух.", "tj": "Ман шунида фаҳмидам."},
                {"zh": "题太多，我没做完。", "pinyin": "Tí tài duō, wǒ méi zuòwán.", "uz": "Savollar ko'p edi, men tamomlaolmadim.", "ru": "Заданий было много, я не успел закончить.", "tj": "Саволҳо зиёд буданд, ман нарасидам тамом кунам."},
            ]
        },
        {
            "no": 2,
            "title_zh": '介词"从"',
            "title_uz": "Old ko'makchi 从 (dan, boshlab)",
            "title_ru": "Предлог 从 (от, с, начиная с)",
            "title_tj": "Пешоянди 从 (аз, аз ибтидои)",
            "rule_uz": (
                "'从' old ko'makchisi joy yoki vaqtni bildiradi va 'dan/boshlab' ma'nosini beradi.\n"
                "Odatda 'cóng … kāishǐ' (…dan boshlab) yoki 'cóng … dào …' (…dan …gacha) ko'rinishida ishlatiladi."
            ),
            "rule_ru": (
                "Предлог '从' обозначает место или время и означает 'от/с/начиная с'.\n"
                "Обычно используется в форме 'cóng … kāishǐ' (начиная с …) или 'cóng … dào …' (от … до …)."
            ),
            "rule_tj": (
                "Пешоянди '从' ҷой ё вақтро нишон медиҳад ва маъноии 'аз/аз ибтидои'-ро медиҳад.\n"
                "Одатан дар шакли 'cóng … kāishǐ' (аз … оғоз) ё 'cóng … dào …' (аз … то …) истифода мешавад."
            ),
            "examples": [
                {"zh": "他从下个星期一开始上班。", "pinyin": "Tā cóng xià ge xīngqīyī kāishǐ shàngbān.", "uz": "U kelasi dushanba kundan boshlab ishga chiqadi.", "ru": "Он начнёт работать с ближайшего понедельника.", "tj": "Вай аз душанбаи оянда кор мекунад."},
                {"zh": "您从几岁开始学跳舞？", "pinyin": "Nín cóng jǐ suì kāishǐ xué tiàowǔ?", "uz": "Siz necha yoshdan raqs o'rganishni boshladingiz?", "ru": "С какого возраста вы начали учиться танцевать?", "tj": "Шумо аз чанд солагӣ рақс омӯхтанро оғоз кардед?"},
            ]
        },
        {
            "no": 3,
            "title_zh": '"第"表示顺序',
            "title_uz": "Tartib ko'rsatkichi 第 (birinchi, ikkinchi...)",
            "title_ru": "Порядковый показатель 第 (первый, второй...)",
            "title_tj": "Нишондиҳандаи тартиби 第 (аввалин, дуввум...)",
            "rule_uz": (
                "'第' prefiksi raqamlardan oldin qo'yilib tartib sonlarini hosil qiladi:\n"
                "第一 (birinchi), 第二 (ikkinchi) va h.k.\n"
                "Bu inglizcha '-th' qo'shimchasiga o'xshaydi.\n"
                "Odiy sanoq sonlardan farqli ravishda narsa-predmetning tartibini bildiradi."
            ),
            "rule_ru": (
                "Префикс '第' перед числами образует порядковые числительные:\n"
                "第一 (первый), 第二 (второй) и т.д.\n"
                "Аналог английского суффикса '-th'.\n"
                "В отличие от количественных числительных, обозначает порядок предметов."
            ),
            "rule_tj": (
                "Пешванди '第' пеш аз ададҳо ададҳои тартибиро месозад:\n"
                "第一 (якум/аввалин), 第二 (дуввум) ва ғ.\n"
                "Ба суффикси '-um' дар тоҷикӣ монанд аст.\n"
                "Дар фарқ аз ададҳои шуморавӣ, тартиби ашёро нишон медиҳад."
            ),
            "examples": [
                {"zh": "这是他的第一个工作。", "pinyin": "Zhè shì tā de dì yī ge gōngzuò.", "uz": "Bu uning birinchi ishi.", "ru": "Это его первая работа.", "tj": "Ин кори аввалинаш аст."},
                {"zh": "我第一次跳舞是在七岁的时候。", "pinyin": "Wǒ dì yī cì tiàowǔ shì zài qī suì de shíhou.", "uz": "Men birinchi marta etti yoshimda raqs tushganman.", "ru": "Я впервые танцевал в семь лет.", "tj": "Ман бори аввал дар ҳафт солагӣ рақс кардам."},
            ]
        },
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
            "instruction_ru": "Напишите по-китайски следующие слова:",
            "instruction_tj": "Калимаҳои зеринро бо хатти чинӣ нависед:",
            "items": [
                {"prompt_uz": "xato",          "prompt_ru": "неправильный",  "prompt_tj": "хато",               "answer": "错",   "pinyin": "cuò"},
                {"prompt_uz": "raqs tushmoq",  "prompt_ru": "танцевать",     "prompt_tj": "рақс кардан",        "answer": "跳舞", "pinyin": "tiàowǔ"},
                {"prompt_uz": "birinchi",       "prompt_ru": "первый",        "prompt_tj": "якум/аввалин",       "answer": "第一", "pinyin": "dìyī"},
                {"prompt_uz": "umid qilmoq",   "prompt_ru": "надеяться",     "prompt_tj": "умед доштан",        "answer": "希望", "pinyin": "xīwàng"},
                {"prompt_uz": "tushunmoq",     "prompt_ru": "понимать",      "prompt_tj": "фаҳмидан",           "answer": "懂",   "pinyin": "dǒng"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "衣服你洗了___有？（没）", "prompt_ru": "衣服你洗了___有？（没）", "prompt_tj": "衣服你洗了___有？（没）", "answer": "没", "pinyin": "méi"},
                {"prompt_uz": "作业太多了，我还没做___。（完）", "prompt_ru": "作业太多了，我还没做___。（完）", "prompt_tj": "作业太多了，我还没做___。（完）", "answer": "完", "pinyin": "wán"},
                {"prompt_uz": "___八点到十二点，她们都在上班。（从）", "prompt_ru": "___八点到十二点，她们都在上班。（从）", "prompt_tj": "___八点到十二点，她们都在上班。（从）", "answer": "从", "pinyin": "cóng"},
                {"prompt_uz": "我___一次去北京。（第）", "prompt_ru": "我___一次去北京。（第）", "prompt_tj": "我___一次去北京。（第）", "answer": "第", "pinyin": "dì"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "题太多，我没做完。", "prompt_ru": "题太多，我没做完。", "prompt_tj": "题太多，我没做完。", "answer": "Savollar juda ko'p edi, men tamomlaolmadim.", "pinyin": "Tí tài duō, wǒ méi zuòwán."},
                {"prompt_uz": "他从下个星期一开始上班。", "prompt_ru": "他从下个星期一开始上班。", "prompt_tj": "他从下个星期一开始上班。", "answer": "U kelasi dushanba kundan boshlab ishga chiqadi.", "pinyin": "Tā cóng xià ge xīngqīyī kāishǐ shàngbān."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["错", "跳舞", "第一", "希望", "懂"]},
        {"no": 2, "answers": ["没", "完", "从", "第"]},
        {"no": 3, "answers": [
            "Savollar juda ko'p edi, men tamomlaolmadim.",
            "U kelasi dushanba kundan boshlab ishga chiqadi.",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib har biridan bitta jumla tuzing: 从, 第一, 做完, 听懂",
            "instruction_ru": "Составьте по одному предложению с каждым из следующих слов: 从, 第一, 做完, 听懂",
            "instruction_tj": "Бо ҳар яке аз калимаҳои зерин як ҷумла тартиб диҳед: 从, 第一, 做完, 听懂",
            "words": ["从", "第一", "做完", "听懂"],
            "example": "我从七岁开始学汉语。",
        },
        {
            "no": 2,
            "instruction_uz": "O'zingiz haqingizda yozing: birinchi marta xitoy tilini qachon o'rganishni boshladingiz va bu siz uchun qanday edi.",
            "instruction_ru": "Напишите о себе: когда вы впервые начали учить китайский язык и каково это было для вас.",
            "instruction_tj": "Дар бораи худ нависед: аввалин бор кай забони чинӣ омӯхтанро оғоз кардед ва барои шумо ин чӣ гуна буд.",
            "topic_uz": "Men birinchi marta xitoy tilini o'rganganim",
            "topic_ru": "Как я впервые начал учить китайский",
            "topic_tj": "Бори аввале ки ман забони чинӣ омӯхтам",
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
