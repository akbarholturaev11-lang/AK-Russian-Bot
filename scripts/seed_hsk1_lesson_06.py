import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 6,
    "lesson_code": "HSK1-L06",
    "title": "我会说汉语",
    "goal": json.dumps({
        "uz": "Modal fe'l 会 yordamida qobiliyat va mahorat haqida gapirish",
        "ru": "Говорить о способностях и умениях с помощью модального глагола 会",
        "tj": "Дар бораи қобилият ва маҳорат бо ёрии феъли модалии 会 гап задан",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Oltinchi darsda siz modal fe'l 会 yordamida qobiliyatlarni ifodalash, sifat kesimli gaplar va 怎么 so'roq so'zini o'rganasiz. 12 ta yangi so'z, 3 ta dialog.",
        "ru": "На шестом уроке вы научитесь выражать способности с модальным глаголом 会, строить предложения с прилагательными в роли сказуемого и использовать вопросительное слово 怎么. 12 новых слов, 3 диалога.",
        "tj": "Дар дарси шашум шумо ифодаи қобилиятро бо феъли модалии 会, ҷумлаҳо бо сифати хабарӣ ва калимаи саволии 怎么 -ро меомӯзед. 12 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "会",   "pinyin": "huì",    "pos": "mod.",
         "uz": "qila olmoq (o'rganish orqali)",
         "ru": "мочь, уметь (через обучение)",
         "tj": "тавонистан (тавассути омӯзиш)"},
        {"no": 2,  "zh": "说",   "pinyin": "shuō",   "pos": "v.",
         "uz": "gapirmoq, aytmoq",
         "ru": "говорить, сказать",
         "tj": "гап задан, гуфтан"},
        {"no": 3,  "zh": "妈妈", "pinyin": "māma",   "pos": "n.",
         "uz": "ona, onaxon",
         "ru": "мама",
         "tj": "модар, модарҷон"},
        {"no": 4,  "zh": "菜",   "pinyin": "cài",    "pos": "n.",
         "uz": "taom, sabzavot",
         "ru": "блюдо, овощ",
         "tj": "хӯрок, сабзавот"},
        {"no": 5,  "zh": "很",   "pinyin": "hěn",    "pos": "adv.",
         "uz": "juda, ancha",
         "ru": "очень, довольно",
         "tj": "хеле, басо"},
        {"no": 6,  "zh": "好吃", "pinyin": "hǎochī", "pos": "adj.",
         "uz": "mazali, lazzatli",
         "ru": "вкусный, аппетитный",
         "tj": "болаззат, хуштаъм"},
        {"no": 7,  "zh": "做",   "pinyin": "zuò",    "pos": "v.",
         "uz": "qilmoq, tayyorlamoq",
         "ru": "делать, готовить",
         "tj": "кардан, тайёр кардан"},
        {"no": 8,  "zh": "写",   "pinyin": "xiě",    "pos": "v.",
         "uz": "yozmoq",
         "ru": "писать",
         "tj": "навиштан"},
        {"no": 9,  "zh": "汉字", "pinyin": "Hànzì",  "pos": "n.",
         "uz": "xitoy ierogliflari",
         "ru": "китайские иероглифы",
         "tj": "иероглифҳои чинӣ"},
        {"no": 10, "zh": "字",   "pinyin": "zì",     "pos": "n.",
         "uz": "belgi, harf, ieroglif",
         "ru": "иероглиф, буква, знак",
         "tj": "аломат, ҳарф, иероглиф"},
        {"no": 11, "zh": "怎么", "pinyin": "zěnme",  "pos": "pron.",
         "uz": "qanday, qay yo'l bilan",
         "ru": "как, каким образом",
         "tj": "чӣ тавр, ба кадом роҳ"},
        {"no": 12, "zh": "读",   "pinyin": "dú",     "pos": "v.",
         "uz": "o'qimoq (baland ovozda)",
         "ru": "читать (вслух)",
         "tj": "хондан (баланд)"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Maktabda — xitoy tilida gapirish",
            "scene_ru": "В школе — разговор на китайском",
            "scene_tj": "Дар мактаб — гуфтугӯ ба забони чинӣ",
            "dialogue": [
                {"speaker": "A", "zh": "你会说汉语吗？",    "pinyin": "Nǐ huì shuō Hànyǔ ma?",
                 "uz": "Siz xitoycha gapira olasizmi?",
                 "ru": "Вы умеете говорить по-китайски?",
                 "tj": "Оё шумо метавонед ба забони чинӣ гап бизанед?"},
                {"speaker": "B", "zh": "我会说汉语。",      "pinyin": "Wǒ huì shuō Hànyǔ.",
                 "uz": "Men xitoycha gapira olaman.",
                 "ru": "Я умею говорить по-китайски.",
                 "tj": "Ман метавонам ба забони чинӣ гап бизанам."},
                {"speaker": "A", "zh": "你妈妈会说汉语吗？", "pinyin": "Nǐ māma huì shuō Hànyǔ ma?",
                 "uz": "Onangi xitoycha gapira oladimi?",
                 "ru": "Ваша мама умеет говорить по-китайски?",
                 "tj": "Оё модаратон метавонад ба забони чинӣ гап бизанад?"},
                {"speaker": "B", "zh": "她不会说。",        "pinyin": "Tā bú huì shuō.",
                 "uz": "U gapira olmaydi.",
                 "ru": "Она не умеет говорить.",
                 "tj": "Вай наметавонад гап бизанад."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Oshxonada — xitoy taomi",
            "scene_ru": "На кухне — китайская еда",
            "scene_tj": "Дар ошхона — хӯроки чинӣ",
            "dialogue": [
                {"speaker": "A", "zh": "中国菜好吃吗？",    "pinyin": "Zhōngguó cài hǎochī ma?",
                 "uz": "Xitoy taomlari mazalimi?",
                 "ru": "Китайская еда вкусная?",
                 "tj": "Оё хӯроки чинӣ болаззат аст?"},
                {"speaker": "B", "zh": "中国菜很好吃。",    "pinyin": "Zhōngguó cài hěn hǎochī.",
                 "uz": "Xitoy taomlari juda mazali.",
                 "ru": "Китайская еда очень вкусная.",
                 "tj": "Хӯроки чинӣ хеле болаззат аст."},
                {"speaker": "A", "zh": "你会做中国菜吗？",  "pinyin": "Nǐ huì zuò Zhōngguó cài ma?",
                 "uz": "Siz xitoy taomlarini tayyorlay olasizmi?",
                 "ru": "Вы умеете готовить китайскую еду?",
                 "tj": "Оё шумо метавонед хӯроки чинӣ тайёр кунед?"},
                {"speaker": "B", "zh": "我不会做。",        "pinyin": "Wǒ bú huì zuò.",
                 "uz": "Men tayyorlay olmayman.",
                 "ru": "Я не умею готовить.",
                 "tj": "Ман наметавонам тайёр кунам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Kutubxonada — xitoy yozuvi",
            "scene_ru": "В библиотеке — китайские иероглифы",
            "scene_tj": "Дар китобхона — иероглифҳои чинӣ",
            "dialogue": [
                {"speaker": "A", "zh": "你会写汉字吗？",              "pinyin": "Nǐ huì xiě Hànzì ma?",
                 "uz": "Siz xitoy ierogliflarini yoza olasizmi?",
                 "ru": "Вы умеете писать иероглифы?",
                 "tj": "Оё шумо метавонед иероглифҳои чинӣ нависед?"},
                {"speaker": "B", "zh": "我会写。",                    "pinyin": "Wǒ huì xiě.",
                 "uz": "Men yoza olaman.",
                 "ru": "Я умею писать.",
                 "tj": "Ман метавонам нависам."},
                {"speaker": "A", "zh": "这个字怎么写？",              "pinyin": "Zhège zì zěnme xiě?",
                 "uz": "Bu ieroglif qanday yoziladi?",
                 "ru": "Как пишется этот иероглиф?",
                 "tj": "Ин иероглиф чӣ тавр навишта мешавад?"},
                {"speaker": "B", "zh": "对不起，这个字我会读，不会写。", "pinyin": "Duìbuqǐ, zhège zì wǒ huì dú, bú huì xiě.",
                 "uz": "Kechirasiz, bu ieroglifni o'qiy olaman, lekin yoza olmayman.",
                 "ru": "Извините, этот иероглиф я умею читать, но не умею писать.",
                 "tj": "Бубахшед, ин иероглифро ман метавонам бихонам, аммо навишта наметавонам."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "能愿动词 会",
            "title_uz": "Modal fe'l 会",
            "title_ru": "Модальный глагол 会",
            "title_tj": "Феъли модалии 会",
            "rule_uz": (
                "会(huì) — o'rganish orqali erishilgan qobiliyatni ifodalaydi.\n"
                "Tuzilma: Ega + (不)会 + Fe'l\n\n"
                "Tasdiq: 我会说汉语。— Men xitoycha gapira olaman.\n"
                "Inkor: 我不会做中国菜。— Men xitoy taomini tayyorlay olmayman.\n"
                "Savol: 你会写汉字吗？— Siz xitoy ierogliflarini yoza olasizmi?\n\n"
                "Eslatma: Inkorda 不会, ha/yo'q savolda 吗 ishlatiladi."
            ),
            "rule_ru": (
                "会(huì) — выражает способность, приобретённую через обучение.\n"
                "Структура: Подлежащее + (不)会 + Глагол\n\n"
                "Утверждение: 我会说汉语。— Я умею говорить по-китайски.\n"
                "Отрицание: 我不会做中国菜。— Я не умею готовить китайскую еду.\n"
                "Вопрос: 你会写汉字吗？— Вы умеете писать иероглифы?\n\n"
                "Примечание: для отрицания 不会, для вопроса — 吗."
            ),
            "rule_tj": (
                "会(huì) — қобилияти аз тариқи омӯзиш ба даст овардашударо ифода мекунад.\n"
                "Сохтор: Мубтадо + (不)会 + Феъл\n\n"
                "Тасдиқ: 我会说汉语。— Ман метавонам ба забони чинӣ гап бизанам.\n"
                "Инкор: 我不会做中国菜。— Ман наметавонам хӯроки чинӣ тайёр кунам.\n"
                "Савол: 你会写汉字吗？— Оё шумо метавонед иероглифҳо нависед?\n\n"
                "Эзоҳ: Барои инкор 不会, барои савол — 吗 истифода мешавад."
            ),
            "examples": [
                {"zh": "我会说汉语。",     "pinyin": "Wǒ huì shuō Hànyǔ.",
                 "uz": "Men xitoycha gapira olaman.", "ru": "Я умею говорить по-китайски.", "tj": "Ман метавонам ба забони чинӣ гап бизанам."},
                {"zh": "她不会做中国菜。", "pinyin": "Tā bú huì zuò Zhōngguó cài.",
                 "uz": "U xitoy taomini tayyorlay olmaydi.", "ru": "Она не умеет готовить китайскую еду.", "tj": "Вай наметавонад хӯроки чинӣ тайёр кунад."},
                {"zh": "你会写汉字吗？",   "pinyin": "Nǐ huì xiě Hànzì ma?",
                 "uz": "Siz xitoy ierogliflarini yoza olasizmi?", "ru": "Вы умеете писать иероглифы?", "tj": "Оё шумо метавонед иероглифҳо нависед?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "形容词谓语句",
            "title_uz": "Sifat kesimli gap",
            "title_ru": "Предложение с прилагательным-сказуемым",
            "title_tj": "Ҷумла бо сифати хабарӣ",
            "rule_uz": (
                "Sifat kesimli gap: Ega + 很/不 + Sifat\n\n"
                "Xitoy tilida sifat gap kesimi bo'la oladi.\n"
                "Tasdiq gaplarda odatda 很(hěn) ishlatiladi:\n"
                "中国菜很好吃。— Xitoy taomlari juda mazali.\n\n"
                "Inkor gaplarda 不 ishlatiladi (很 shart emas):\n"
                "我妈妈的汉语不好。— Onamning xitoy tili yaxshi emas.\n\n"
                "Eslatma: 很 ko'pincha grammatik talab sifatida ishlatiladi."
            ),
            "rule_ru": (
                "Предложение с прилагательным: Подлежащее + 很/不 + Прилагательное\n\n"
                "В китайском языке прилагательное может быть сказуемым.\n"
                "В утвердительных предложениях обычно используется 很(hěn):\n"
                "中国菜很好吃。— Китайская еда очень вкусная.\n\n"
                "В отрицательных предложениях используется 不 (很 не нужен):\n"
                "我妈妈的汉语不好。— Китайский мамы нехороший.\n\n"
                "Примечание: 很 часто семантически слабый, нужен по грамматике."
            ),
            "rule_tj": (
                "Ҷумла бо сифати хабарӣ: Мубтадо + 很/不 + Сифат\n\n"
                "Дар забони чинӣ сифат метавонад хабар бошад.\n"
                "Дар ҷумлаҳои тасдиқӣ одатан 很(hěn) истифода мешавад:\n"
                "中国菜很好吃。— Хӯроки чинӣ хеле болаззат аст.\n\n"
                "Дар ҷумлаҳои инкорӣ 不 истифода мешавад (很 лозим нест):\n"
                "我妈妈的汉语不好。— Забони чинии модарам хуб нест.\n\n"
                "Эзоҳ: 很 аксар аз рӯи талаботи грамматикӣ истифода мешавад."
            ),
            "examples": [
                {"zh": "中国菜很好吃。",     "pinyin": "Zhōngguó cài hěn hǎochī.",
                 "uz": "Xitoy taomlari juda mazali.", "ru": "Китайская еда очень вкусная.", "tj": "Хӯроки чинӣ хеле болаззат аст."},
                {"zh": "她的汉语很好。",     "pinyin": "Tā de Hànyǔ hěn hǎo.",
                 "uz": "Uning xitoy tili juda yaxshi.", "ru": "Её китайский очень хороший.", "tj": "Забони чинии вай хеле хуб аст."},
                {"zh": "我妈妈的汉语不好。", "pinyin": "Wǒ māma de Hànyǔ bù hǎo.",
                 "uz": "Onamning xitoy tili yaxshi emas.", "ru": "Китайский мамы нехороший.", "tj": "Забони чинии модарам хуб нест."},
            ]
        },
        {
            "no": 3,
            "title_zh": "怎么 — qanday so'roq olmoshi",
            "title_uz": "怎么 — qanday so'roq olmoshi",
            "title_ru": "怎么 — вопросительное наречие",
            "title_tj": "怎么 — ҷонишини саволии тарзӣ",
            "rule_uz": (
                "怎么(zěnme) — fe'l oldiga qo'yilib, harakat usulini so'raydi.\n"
                "Tuzilma: Ega + 怎么 + Fe'l?\n\n"
                "Misol:\n"
                "这个字怎么写？— Bu ieroglif qanday yoziladi?\n"
                "这个字怎么读？— Bu ieroglif qanday o'qiladi?\n"
                "中国菜怎么做？— Xitoy taomini qanday tayyorlash kerak?"
            ),
            "rule_ru": (
                "怎么(zěnme) — ставится перед глаголом, спрашивает о способе действия.\n"
                "Структура: Подлежащее + 怎么 + Глагол?\n\n"
                "Пример:\n"
                "这个字怎么写？— Как пишется этот иероглиф?\n"
                "这个字怎么读？— Как читается этот иероглиф?\n"
                "中国菜怎么做？— Как готовить китайскую еду?"
            ),
            "rule_tj": (
                "怎么(zěnme) — пеш аз феъл гузошта, тарзи амалро мепурсад.\n"
                "Сохтор: Мубтадо + 怎么 + Феъл?\n\n"
                "Мисол:\n"
                "这个字怎么写？— Ин иероглиф чӣ тавр навишта мешавад?\n"
                "这个字怎么读？— Ин иероглиф чӣ тавр хонда мешавад?\n"
                "中国菜怎么做？— Хӯроки чинӣ чӣ тавр тайёр карда мешавад?"
            ),
            "examples": [
                {"zh": "这个字怎么写？", "pinyin": "Zhège zì zěnme xiě?",
                 "uz": "Bu ieroglif qanday yoziladi?", "ru": "Как пишется этот иероглиф?", "tj": "Ин иероглиф чӣ тавр навишта мешавад?"},
                {"zh": "这个字怎么读？", "pinyin": "Zhège zì zěnme dú?",
                 "uz": "Bu ieroglif qanday o'qiladi?", "ru": "Как читается этот иероглиф?", "tj": "Ин иероглиф чӣ тавр хонда мешавад?"},
                {"zh": "汉语怎么说？",   "pinyin": "Hànyǔ zěnme shuō?",
                 "uz": "Bu xitoycha qanday aytiladi?", "ru": "Как это сказать по-китайски?", "tj": "Ин ба забони чинӣ чӣ тавр гуфта мешавад?"},
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
                {"prompt_uz": "Siz xitoycha gapira olasizmi?", "prompt_ru": "Вы умеете говорить по-китайски?", "prompt_tj": "Оё шумо метавонед ба забони чинӣ гап бизанед?", "answer": "你会说汉语吗？", "pinyin": "Nǐ huì shuō Hànyǔ ma?"},
                {"prompt_uz": "Men xitoycha gapira olaman.", "prompt_ru": "Я умею говорить по-китайски.", "prompt_tj": "Ман метавонам ба забони чинӣ гап бизанам.", "answer": "我会说汉语。", "pinyin": "Wǒ huì shuō Hànyǔ."},
                {"prompt_uz": "Xitoy taomlari juda mazali.", "prompt_ru": "Китайская еда очень вкусная.", "prompt_tj": "Хӯроки чинӣ хеле болаззат аст.", "answer": "中国菜很好吃。", "pinyin": "Zhōngguó cài hěn hǎochī."},
                {"prompt_uz": "Men xitoy taomini tayyorlay olmayman.", "prompt_ru": "Я не умею готовить китайскую еду.", "prompt_tj": "Ман наметавонам хӯроки чинӣ тайёр кунам.", "answer": "我不会做中国菜。", "pinyin": "Wǒ bú huì zuò Zhōngguó cài."},
                {"prompt_uz": "Bu ieroglif qanday yoziladi?", "prompt_ru": "Как пишется этот иероглиф?", "prompt_tj": "Ин иероглиф чӣ тавр навишта мешавад?", "answer": "这个字怎么写？", "pinyin": "Zhège zì zěnme xiě?"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холиро пур кунед:",
            "items": [
                {"prompt_uz": "你___说汉语吗？", "prompt_ru": "你___说汉语吗？", "prompt_tj": "你___说汉语吗？", "answer": "会", "pinyin": "huì"},
                {"prompt_uz": "中国菜___好吃。", "prompt_ru": "中国菜___好吃。", "prompt_tj": "中国菜___好吃。", "answer": "很", "pinyin": "hěn"},
                {"prompt_uz": "这个字___写？",   "prompt_ru": "这个字___写？",   "prompt_tj": "这个字___写？",   "answer": "怎么", "pinyin": "zěnme"},
                {"prompt_uz": "我会___，不会___。", "prompt_ru": "我会___，不会___。", "prompt_tj": "我会___，不会___。", "answer": "读/写", "pinyin": "dú/xiě"},
            ]
        },
        {
            "no": 3,
            "type": "make_negative",
            "instruction_uz": "Inkorda gapga aylantiring:",
            "instruction_ru": "Превратите в отрицательное предложение:",
            "instruction_tj": "Ба ҷумлаи инкорӣ табдил диҳед:",
            "items": [
                {"prompt_uz": "我会说汉语。", "prompt_ru": "我会说汉语。", "prompt_tj": "我会说汉语。", "answer": "我不会说汉语。", "pinyin": "Wǒ bú huì shuō Hànyǔ."},
                {"prompt_uz": "中国菜很好吃。", "prompt_ru": "中国菜很好吃。", "prompt_tj": "中国菜很好吃。", "answer": "中国菜不好吃。", "pinyin": "Zhōngguó cài bù hǎochī."},
                {"prompt_uz": "她会写汉字。", "prompt_ru": "她会写汉字。", "prompt_tj": "她会写汉字。", "answer": "她不会写汉字。", "pinyin": "Tā bú huì xiě Hànzì."},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["你会说汉语吗？", "我会说汉语。", "中国菜很好吃。", "我不会做中国菜。", "这个字怎么写？"]},
        {"no": 2, "answers": ["会", "很", "怎么", "读/写"]},
        {"no": 3, "answers": ["我不会说汉语。", "中国菜不好吃。", "她不会写汉字。"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "O'zingiz haqingizda 4 ta gap yozing (nima qila olasiz/olmaysiz):",
            "instruction_ru": "Напишите 4 предложения о себе (что умеете/не умеете делать):",
            "instruction_tj": "Дар бораи худатон 4 ҷумла нависед (чӣ метавонед/наметавонед кунед):",
            "template": "我会___。我不会___。我___会___吗？",
            "words": ["会", "不会", "说", "写", "做", "读", "汉语", "汉字", "中国菜"],
        },
        {
            "no": 2,
            "instruction_uz": "Savollarga javob bering:",
            "instruction_ru": "Ответьте на вопросы:",
            "instruction_tj": "Ба саволҳо ҷавоб диҳед:",
            "items": [
                {"prompt_uz": "你会说汉语吗？", "prompt_ru": "你会说汉语吗？", "prompt_tj": "你会说汉语吗？",
                 "hint_uz": "Ha yoki yo'q, to'liq gap bilan", "hint_ru": "Да или нет, полным предложением", "hint_tj": "Бале ё не, бо ҷумлаи пурра"},
                {"prompt_uz": "中国菜好吃吗？", "prompt_ru": "中国菜好吃吗？", "prompt_tj": "中国菜好吃吗？",
                 "hint_uz": "O'z fikringizni bildiring", "hint_ru": "Поделитесь своим мнением", "hint_tj": "Фикри худро баён кунед"},
                {"prompt_uz": "这个字怎么写？(好)", "prompt_ru": "这个字怎么写？(好)", "prompt_tj": "这个字怎么写？(好)",
                 "hint_uz": "好 ieroglifini qanday yozishni tasvirlab bering", "hint_ru": "Опишите, как пишется иероглиф 好", "tj": "Тавсиф диҳед, ки иероглифи 好 чӣ тавр навишта мешавад"},
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
