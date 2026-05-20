import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 8,
    "lesson_code": "HSK1-L08",
    "title": "我想喝茶",
    "goal": json.dumps({"uz": "Istak bildirish, narx so'rash va o'lchov so'zlarini o'rganish", "ru": "Выражение желаний, спрашивание цены и изучение счётных слов", "tj": "Ифодаи орзуҳо, пурсидани нарх ва омӯзиши калимаҳои шуморавӣ"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Sakkizinchi darsda 想 modal fe'li yordamida istak bildirish, narx so'rash (多少钱?) va 个/口 o'lchov so'zlarini o'rganasiz. 15 ta yangi so'z, 3 ta suhbat.", "ru": "В восьмом уроке вы научитесь выражать желания с помощью модального глагола 想, спрашивать о цене (多少钱?) и использовать счётные слова 个/口. 15 новых слов, 3 диалога.", "tj": "Дар дарси ҳаштум шумо бо ёрии феъли модалии 想 орзуро ифода мекунед, нархро мепурсед (多少钱?) ва калимаҳои шуморавии 个/口-ро меомӯзед. 15 калимаи нав, 3 муколама."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "想",   "pinyin": "xiǎng",    "pos": "mod.", "uz": "xohlamoq, istаmoq",              "ru": "хотеть, желать",                       "tj": "хостан, орзу доштан"},
        {"no": 2,  "zh": "喝",   "pinyin": "hē",       "pos": "v.",   "uz": "ichmoq",                         "ru": "пить",                                 "tj": "нӯшидан"},
        {"no": 3,  "zh": "茶",   "pinyin": "chá",      "pos": "n.",   "uz": "choy",                           "ru": "чай",                                  "tj": "чой"},
        {"no": 4,  "zh": "吃",   "pinyin": "chī",      "pos": "v.",   "uz": "yemoq",                          "ru": "есть, кушать",                         "tj": "хӯрдан"},
        {"no": 5,  "zh": "米饭", "pinyin": "mǐfàn",    "pos": "n.",   "uz": "guruch, pishirilgan guruch",      "ru": "рис, варёный рис",                     "tj": "биринҷ, биринҷи пухта"},
        {"no": 6,  "zh": "下午", "pinyin": "xiàwǔ",    "pos": "n.",   "uz": "tushdan keyin",                  "ru": "после полудня, вторая половина дня",   "tj": "баъд аз нисфирӯзӣ"},
        {"no": 7,  "zh": "商店", "pinyin": "shāngdiàn","pos": "n.",   "uz": "do'kon, magazin",                "ru": "магазин",                              "tj": "мағоза, дӯкон"},
        {"no": 8,  "zh": "买",   "pinyin": "mǎi",      "pos": "v.",   "uz": "sotib olmoq",                    "ru": "покупать",                             "tj": "харидан"},
        {"no": 9,  "zh": "个",   "pinyin": "gè",       "pos": "m.",   "uz": "umumiy o'lchov so'z (dona/birlik)","ru": "общее счётное слово (штука/единица)",  "tj": "калимаи шуморавии умумӣ (дона/воҳид)"},
        {"no": 10, "zh": "杯子", "pinyin": "bēizi",    "pos": "n.",   "uz": "stakan, piyola",                 "ru": "стакан, кружка",                       "tj": "косаи пиёла"},
        {"no": 11, "zh": "这",   "pinyin": "zhè",      "pos": "pron.","uz": "bu (ko'rsatish olmoshi)",         "ru": "этот, это (указательное местоимение)", "tj": "ин (исми ишора)"},
        {"no": 12, "zh": "多少", "pinyin": "duōshao",  "pos": "pron.","uz": "qancha, nechta (10 dan ortiq)",  "ru": "сколько (больше 10)",                  "tj": "чанд (аз 10 зиёд)"},
        {"no": 13, "zh": "钱",   "pinyin": "qián",     "pos": "n.",   "uz": "pul",                            "ru": "деньги",                               "tj": "пул"},
        {"no": 14, "zh": "块",   "pinyin": "kuài",     "pos": "m.",   "uz": "yuan (so'zlashuv)",              "ru": "юань (разговорный)",                   "tj": "юан (забони гуфтугӯӣ)"},
        {"no": 15, "zh": "那",   "pinyin": "nà",       "pos": "pron.","uz": "u, o'sha (ko'rsatish olmoshi)",   "ru": "тот, та (указательное местоимение)",   "tj": "он, он (исми ишора)"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Restoranda — nima ichish/yeyish",
            "scene_ru": "В ресторане — что пить/есть",
            "scene_tj": "Дар тарабхона — чӣ нӯшидан/хӯрдан",
            "dialogue": [
                {"speaker": "A", "zh": "你想喝什么？",  "pinyin": "Nǐ xiǎng hē shénme?",  "uz": "Nima ichmoqchisiz?",          "ru": "Что вы хотите выпить?",            "tj": "Шумо чӣ нӯшидан мехоҳед?"},
                {"speaker": "B", "zh": "我想喝茶。",    "pinyin": "Wǒ xiǎng hē chá.",     "uz": "Men choy ichmoqchiman.",      "ru": "Я хочу выпить чай.",               "tj": "Ман чой нӯшидан мехоҳам."},
                {"speaker": "A", "zh": "你想吃什么？",  "pinyin": "Nǐ xiǎng chī shénme?", "uz": "Nima yemoqchisiz?",           "ru": "Что вы хотите поесть?",            "tj": "Шумо чӣ хӯрдан мехоҳед?"},
                {"speaker": "B", "zh": "我想吃米饭。",  "pinyin": "Wǒ xiǎng chī mǐfàn.",  "uz": "Men guruch yemoqchiman.",     "ru": "Я хочу поесть риса.",              "tj": "Ман биринҷ хӯрдан мехоҳам."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Mehmonxonada — tushdan keyingi reja",
            "scene_ru": "В гостинице — планы на вторую половину дня",
            "scene_tj": "Дар меҳмонхона — нақшаи баъд аз нисфирӯзӣ",
            "dialogue": [
                {"speaker": "A", "zh": "下午你想做什么？",   "pinyin": "Xiàwǔ nǐ xiǎng zuò shénme?",   "uz": "Tushdan keyin nima qilmoqchisiz?",        "ru": "Что вы хотите делать во второй половине дня?", "tj": "Баъд аз нисфирӯзӣ чӣ кардан мехоҳед?"},
                {"speaker": "B", "zh": "下午我想去商店。",   "pinyin": "Xiàwǔ wǒ xiǎng qù shāngdiàn.", "uz": "Tushdan keyin do'konga bormoqchiman.",    "ru": "После полудня я хочу сходить в магазин.",     "tj": "Баъд аз нисфирӯзӣ ба мағоза рафтан мехоҳам."},
                {"speaker": "A", "zh": "你想买什么？",       "pinyin": "Nǐ xiǎng mǎi shénme?",         "uz": "Nima sotib olmoqchisiz?",                 "ru": "Что вы хотите купить?",                       "tj": "Шумо чӣ харидан мехоҳед?"},
                {"speaker": "B", "zh": "我想买一个杯子。",   "pinyin": "Wǒ xiǎng mǎi yī gè bēizi.",    "uz": "Bir dona piyola sotib olmoqchiman.",      "ru": "Я хочу купить одну кружку.",                  "tj": "Ман як дона пиёла харидан мехоҳам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Do'konda — narx so'rash",
            "scene_ru": "В магазине — спрашиваем цену",
            "scene_tj": "Дар мағоза — пурсидани нарх",
            "dialogue": [
                {"speaker": "A", "zh": "你好！这个杯子多少钱？",  "pinyin": "Nǐ hǎo! Zhège bēizi duōshao qián?", "uz": "Salom! Bu piyola qancha turadi?",         "ru": "Здравствуйте! Сколько стоит этот стакан?",  "tj": "Салом! Ин пиёла чанд пул аст?"},
                {"speaker": "B", "zh": "28块。",                  "pinyin": "Èrshíbā kuài.",                     "uz": "28 yuan.",                                "ru": "28 юаней.",                                 "tj": "28 юан."},
                {"speaker": "A", "zh": "那个杯子多少钱？",        "pinyin": "Nàge bēizi duōshao qián?",          "uz": "U piyola qancha turadi?",                 "ru": "Сколько стоит тот стакан?",                 "tj": "Он пиёла чанд пул аст?"},
                {"speaker": "B", "zh": "那个杯子18块钱。",        "pinyin": "Nàge bēizi shíbā kuài qián.",       "uz": "U piyola 18 yuan.",                       "ru": "Тот стакан стоит 18 юаней.",                "tj": "Он пиёла 18 юан аст."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "能愿动词 想 — Modal fe'l 想",
            "title_uz": "Modal fe'l 想 (xohlamoq)",
            "title_ru": "Модальный глагол 想 (хотеть)",
            "title_tj": "Феъли модалии 想 (хостан)",
            "rule_uz": (
                "想 (xiǎng) — istak yoki niyatni bildiradi.\n"
                "Tuzilishi: Ega + 想 + Fe'l + To'ldiruvchi\n\n"
                "Tasdiq: 我想喝茶。— Men choy ichmoqchiman.\n"
                "Savol: 你想做什么？— Nima qilmoqchisiz?\n\n"
                "想 va 会:\n"
                "我想说汉语。— Men xitoycha gapirmoqchiman (istak).\n"
                "我会说汉语。— Men xitoycha gapira olaman (qobiliyat)."
            ),
            "rule_ru": (
                "想 (xiǎng) — выражает желание или намерение.\n"
                "Структура: Подлежащее + 想 + Глагол + Дополнение\n\n"
                "Утверждение: 我想喝茶。— Я хочу выпить чай.\n"
                "Вопрос: 你想做什么？— Что вы хотите делать?\n\n"
                "想 и 会:\n"
                "我想说汉语。— Я хочу говорить по-китайски (желание).\n"
                "我会说汉语。— Я умею говорить по-китайски (способность)."
            ),
            "rule_tj": (
                "想 (xiǎng) — орзу ё ниятро ифода мекунад.\n"
                "Сохтор: Мубтадо + 想 + Феъл + Пуркунанда\n\n"
                "Тасдиқ: 我想喝茶。— Ман чой нӯшидан мехоҳам.\n"
                "Савол: 你想做什么？— Шумо чӣ кардан мехоҳед?\n\n"
                "想 ва 会:\n"
                "我想说汉语。— Ман забони чинӣ гап задан мехоҳам (орзу).\n"
                "我会说汉语。— Ман забони чинӣ гап зада метавонам (тавоноӣ)."
            ),
            "examples": [
                {"zh": "我想喝茶。",         "pinyin": "Wǒ xiǎng hē chá.",           "uz": "Men choy ichmoqchiman.",                      "ru": "Я хочу выпить чай.",                          "tj": "Ман чой нӯшидан мехоҳам."},
                {"zh": "她想去学校看书。",   "pinyin": "Tā xiǎng qù xuéxiào kàn shū.", "uz": "U maktabga kitob o'qigani bormoqchi.",      "ru": "Она хочет пойти в школу почитать.",           "tj": "Вай мехоҳад ба мактаб рафта китоб хонад."},
                {"zh": "你想买什么？",       "pinyin": "Nǐ xiǎng mǎi shénme?",       "uz": "Nima sotib olmoqchisiz?",                     "ru": "Что вы хотите купить?",                       "tj": "Шумо чӣ харидан мехоҳед?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "多少 — Qancha so'rog'i (10+)",
            "title_uz": "多少 — Miqdor savoli (10 dan ortiq)",
            "title_ru": "多少 — Вопрос о количестве (больше 10)",
            "title_tj": "多少 — Савол дар бораи миқдор (аз 10 зиёд)",
            "rule_uz": (
                "多少 (duōshao) — 10 dan ortiq sonlar uchun savol so'zi.\n"
                "Eslatma: 几 (jǐ) 10 gacha, 多少 (duōshao) 10 dan ortiq.\n\n"
                "Narx so'rash: ……多少钱？\n"
                "这个杯子多少钱？— Bu piyola qancha turadi?\n\n"
                "Miqdor so'rash:\n"
                "你们学校有多少学生？— Maktabingizda nechta o'quvchi bor?\n"
                "你有多少钱？— Sizda qancha pul bor?"
            ),
            "rule_ru": (
                "多少 (duōshao) — вопросительное слово для чисел больше 10.\n"
                "Примечание: 几 (jǐ) для чисел до 10; 多少 (duōshao) для чисел больше 10.\n\n"
                "Спросить цену: ……多少钱？\n"
                "这个杯子多少钱？— Сколько стоит этот стакан?\n\n"
                "Спросить количество:\n"
                "你们学校有多少学生？— Сколько учеников в вашей школе?\n"
                "你有多少钱？— Сколько у вас денег?"
            ),
            "rule_tj": (
                "多少 (duōshao) — калимаи саволии барои ададҳои аз 10 зиёд.\n"
                "Қайд: 几 (jǐ) барои ададҳо то 10; 多少 (duōshao) барои аз 10 зиёд.\n\n"
                "Пурсидани нарх: ……多少钱？\n"
                "这个杯子多少钱？— Ин пиёла чанд пул аст?\n\n"
                "Пурсидани миқдор:\n"
                "你们学校有多少学生？— Дар мактаби шумо чанд нафар шогирд аст?\n"
                "你有多少钱？— Шумо чанд пул доред?"
            ),
            "examples": [
                {"zh": "这个杯子多少钱？",   "pinyin": "Zhège bēizi duōshao qián?",    "uz": "Bu piyola qancha turadi?",                    "ru": "Сколько стоит этот стакан?",                  "tj": "Ин пиёла чанд пул аст?"},
                {"zh": "你家有多少口人？",   "pinyin": "Nǐ jiā yǒu duōshao kǒu rén?", "uz": "Sizning oilangizda nechta kishi bor?",        "ru": "Сколько человек в вашей семье?",              "tj": "Дар оилаи шумо чанд нафар аст?"},
                {"zh": "一个苹果多少钱？",   "pinyin": "Yī gè píngguǒ duōshao qián?", "uz": "Bitta olma qancha turadi?",                   "ru": "Сколько стоит одно яблоко?",                 "tj": "Як дона себ чанд пул аст?"},
            ]
        },
        {
            "no": 3,
            "title_zh": "量词 个/口 — O'lchov so'zlar",
            "title_uz": "O'lchov so'zlar 个/口",
            "title_ru": "Счётные слова 个/口",
            "title_tj": "Калимаҳои шуморавӣ 个/口",
            "rule_uz": (
                "Xitoy tilida son va otning orasida o'lchov so'z kerak.\n\n"
                "个 (gè) — eng umumiy o'lchov so'z:\n"
                "一个杯子 — bir piyola\n"
                "三个学生 — uch o'quvchi\n"
                "两个老师 — ikki o'qituvchi\n\n"
                "口 (kǒu) — oila a'zolari uchun:\n"
                "三口人 — uch kishilik oila\n"
                "六口人 — olti kishilik oila"
            ),
            "rule_ru": (
                "В китайском языке между числом и существительным необходимо счётное слово.\n\n"
                "个 (gè) — наиболее общее счётное слово:\n"
                "一个杯子 — один стакан\n"
                "三个学生 — три ученика\n"
                "两个老师 — два учителя\n\n"
                "口 (kǒu) — для членов семьи:\n"
                "三口人 — семья из трёх человек\n"
                "六口人 — семья из шести человек"
            ),
            "rule_tj": (
                "Дар забони чинӣ байни адад ва исм калимаи шуморавӣ лозим аст.\n\n"
                "个 (gè) — умумитарин калимаи шуморавӣ:\n"
                "一个杯子 — як дона пиёла\n"
                "三个学生 — се нафар шогирд\n"
                "两个老师 — ду нафар устод\n\n"
                "口 (kǒu) — барои аъзоёни оила:\n"
                "三口人 — оилаи се нафара\n"
                "六口人 — оилаи шаш нафара"
            ),
            "examples": [
                {"zh": "一个杯子",   "pinyin": "yī gè bēizi",    "uz": "bir piyola",            "ru": "один стакан",               "tj": "як дона пиёла"},
                {"zh": "五个学生",   "pinyin": "wǔ gè xuésheng", "uz": "besh o'quvchi",          "ru": "пять учеников",             "tj": "панҷ нафар шогирд"},
                {"zh": "三口人",     "pinyin": "sān kǒu rén",    "uz": "uch kishilik oila",      "ru": "семья из трёх человек",     "tj": "оилаи се нафара"},
            ]
        },
        {
            "no": 4,
            "title_zh": "钱数的表达 — Pul miqdori",
            "title_uz": "Pul miqdorini ifodalash",
            "title_ru": "Выражение денежных сумм",
            "title_tj": "Ифодаи маблағи пул",
            "rule_uz": (
                "Xitoy valyutasi: 人民币 (Renminbi, RMB)\n"
                "Rasmiy: 元 (yuán)\n"
                "So'zlashuv: 块 (kuài)\n\n"
                "Misol:\n"
                "28块 = 28元 — 28 yuan\n"
                "18块钱 — 18 yuan (so'zlashuv shakli)\n\n"
                "这个杯子多少钱？— Bu piyola qancha turadi?\n"
                "28块。— 28 yuan."
            ),
            "rule_ru": (
                "Китайская валюта: 人民币 (Жэньминьби, RMB)\n"
                "Официально: 元 (yuán)\n"
                "Разговорно: 块 (kuài)\n\n"
                "Пример:\n"
                "28块 = 28元 — 28 юаней\n"
                "18块钱 — 18 юаней (разговорная форма)\n\n"
                "这个杯子多少钱？— Сколько стоит этот стакан?\n"
                "28块。— 28 юаней."
            ),
            "rule_tj": (
                "Асъори чинӣ: 人民币 (Жэньминьби, RMB)\n"
                "Расмӣ: 元 (yuán)\n"
                "Гуфтугӯӣ: 块 (kuài)\n\n"
                "Мисол:\n"
                "28块 = 28元 — 28 юан\n"
                "18块钱 — 18 юан (шакли гуфтугӯӣ)\n\n"
                "这个杯子多少钱？— Ин пиёла чанд пул аст?\n"
                "28块。— 28 юан."
            ),
            "examples": [
                {"zh": "这个多少钱？",  "pinyin": "Zhège duōshao qián?", "uz": "Bu qancha turadi?",        "ru": "Сколько это стоит?",         "tj": "Ин чанд пул аст?"},
                {"zh": "28块钱。",     "pinyin": "Èrshíbā kuài qián.",  "uz": "28 yuan.",                 "ru": "28 юаней.",                  "tj": "28 юан."},
                {"zh": "一百块。",     "pinyin": "Yìbǎi kuài.",         "uz": "100 yuan.",                "ru": "100 юаней.",                 "tj": "100 юан."},
            ]
        },
    ], ensure_ascii=False),

    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Xitoycha yozing:",
            "instruction_ru": "Напишите по-китайски:",
            "instruction_tj": "Бо хатти чинӣ нависед:",
            "items": [
                {"prompt_uz": "Nima ichmoqchisiz?",                      "prompt_ru": "Что вы хотите выпить?",                   "prompt_tj": "Шумо чӣ нӯшидан мехоҳед?",                "answer": "你想喝什么？",      "pinyin": "Nǐ xiǎng hē shénme?"},
                {"prompt_uz": "Men choy ichmoqchiman.",                   "prompt_ru": "Я хочу выпить чай.",                      "prompt_tj": "Ман чой нӯшидан мехоҳам.",                 "answer": "我想喝茶。",        "pinyin": "Wǒ xiǎng hē chá."},
                {"prompt_uz": "Bu piyola qancha turadi?",                 "prompt_ru": "Сколько стоит этот стакан?",              "prompt_tj": "Ин пиёла чанд пул аст?",                   "answer": "这个杯子多少钱？",  "pinyin": "Zhège bēizi duōshao qián?"},
                {"prompt_uz": "28 yuan.",                                  "prompt_ru": "28 юаней.",                               "prompt_tj": "28 юан.",                                  "answer": "28块钱。",          "pinyin": "Èrshíbā kuài qián."},
                {"prompt_uz": "Tushdan keyin do'konga bormoqchiman.",     "prompt_ru": "После полудня я хочу сходить в магазин.", "prompt_tj": "Баъд аз нисфирӯзӣ ба мағоза рафтан мехоҳам.", "answer": "下午我想去商店。",  "pinyin": "Xiàwǔ wǒ xiǎng qù shāngdiàn."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "你___喝什么？",              "prompt_ru": "你___喝什么？",              "prompt_tj": "你___喝什么？",              "answer": "想",    "pinyin": "xiǎng"},
                {"prompt_uz": "这___杯子多少钱？",          "prompt_ru": "这___杯子多少钱？",          "prompt_tj": "这___杯子多少钱？",          "answer": "个",    "pinyin": "gè"},
                {"prompt_uz": "___个杯子18块___。",         "prompt_ru": "___个杯子18块___。",         "prompt_tj": "___个杯子18块___。",         "answer": "那/钱", "pinyin": "nà/qián"},
                {"prompt_uz": "我想买___个杯子。",          "prompt_ru": "我想买___个杯子。",          "prompt_tj": "我想买___个杯子。",          "answer": "一",    "pinyin": "yī"},
            ]
        },
        {
            "no": 3,
            "type": "price_dialogue",
            "instruction_uz": "Narx haqida so'rang va javob bering:",
            "instruction_ru": "Спросите о цене и ответьте:",
            "instruction_tj": "Дар бораи нарх бипурсед ва ҷавоб диҳед:",
            "items": [
                {"prompt_uz": "苹果(olma) — 5块/та",  "prompt_ru": "苹果(яблоко) — 5块/шт",  "prompt_tj": "苹果(себ) — 5块/дона",  "answer": "五块钱。"},
                {"prompt_uz": "书(kitob) — 35块",      "prompt_ru": "书(книга) — 35块",        "prompt_tj": "书(китоб) — 35块",      "answer": "三十五块钱。"},
                {"prompt_uz": "茶(choy) — 18块",       "prompt_ru": "茶(чай) — 18块",          "prompt_tj": "茶(чой) — 18块",        "answer": "十八块钱。"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["你想喝什么？", "我想喝茶。", "这个杯子多少钱？", "28块钱。", "下午我想去商店。"]},
        {"no": 2, "answers": ["想", "个", "那/钱", "一"]},
        {"no": 3, "answers": ["五块钱。", "三十五块钱。", "十八块钱。"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Bugungi rejalarni yozing (想 ishlatib, 3-4 gap):",
            "instruction_ru": "Напишите планы на сегодня (используя 想, 3–4 предложения):",
            "instruction_tj": "Нақшаи имрӯзро нависед (бо истифода аз 想, 3-4 ҷумла):",
            "template": "今天下午我想___。我想___。我想买___。",
            "words": ["想", "喝", "吃", "去", "买", "茶", "米饭", "杯子"],
        },
        {
            "no": 2,
            "instruction_uz": "Do'konda narx so'rash haqida suhbat yozing (4 satr):",
            "instruction_ru": "Напишите диалог о ценах в магазине (4 реплики):",
            "instruction_tj": "Муколамаи пурсидани нарх дар мағозаро нависед (4 ҷумла):",
            "example": "A: 你好！___多少钱？\nB: ___块。\nA: ___多少钱？\nB: ___块钱。",
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
