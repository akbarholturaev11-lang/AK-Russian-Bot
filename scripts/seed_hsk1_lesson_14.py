import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 14,
    "lesson_code": "HSK1-L14",
    "title": "她买了不少衣服",
    "goal": json.dumps({
        "uz": "Tugallangan harakatlar uchun 了 yuklamasi, vaqt ko'rsatkichi sifatida 后 va ravish 都",
        "ru": "Частица 了 для завершённых действий, 后 как временной маркер и наречие 都",
        "tj": "Зарраи 了 барои амалҳои анҷомшуда, 后 ҳамчун нишонаи вақт ва зарфи 都",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "O'n to'rtinchi darsda siz 了 bilan tugallangan harakatlarni, 后 bilan kelajak vaqtni ifodalashni va 都 ravishini o'rganasiz. 16 ta yangi so'z, 3 ta dialog.",
        "ru": "В четырнадцатом уроке вы научитесь выражать завершённые действия с 了, будущее время с 后 и использовать наречие 都. 16 новых слов, 3 диалога.",
        "tj": "Дар дарси чордаҳум шумо ёд мегиред, ки амалҳои анҷомшударо бо 了 баён кунед, оянда бо 后 ва зарфи 都 -ро истифода баред. 16 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "东西",  "pinyin": "dōngxi",    "pos": "n.",
         "uz": "narsa, buyum",
         "ru": "вещь, предмет",
         "tj": "чиз, асбоб"},
        {"no": 2,  "zh": "一点儿","pinyin": "yīdiǎnr",   "pos": "num.",
         "uz": "bir oz, biroz",
         "ru": "немного, чуть-чуть",
         "tj": "каме, андаке"},
        {"no": 3,  "zh": "苹果",  "pinyin": "píngguǒ",   "pos": "n.",
         "uz": "olma",
         "ru": "яблоко",
         "tj": "себ"},
        {"no": 4,  "zh": "看见",  "pinyin": "kànjiàn",   "pos": "v.",
         "uz": "ko'rmoq, ko'rib qolmoq",
         "ru": "увидеть, заметить",
         "tj": "дидан, мушоҳида кардан"},
        {"no": 5,  "zh": "先生",  "pinyin": "xiānsheng", "pos": "n.",
         "uz": "janob, ser",
         "ru": "господин, мистер",
         "tj": "ҷаноб, оғо"},
        {"no": 6,  "zh": "开",    "pinyin": "kāi",       "pos": "v.",
         "uz": "ochmoq, haydamoq (mashina)",
         "ru": "открывать, водить (машину)",
         "tj": "кушодан, рондан (мошин)"},
        {"no": 7,  "zh": "车",    "pinyin": "chē",       "pos": "n.",
         "uz": "mashina, transport",
         "ru": "машина, транспорт",
         "tj": "мошин, нақлиёт"},
        {"no": 8,  "zh": "回来",  "pinyin": "huílai",    "pos": "v.",
         "uz": "qaytib kelmoq",
         "ru": "вернуться, прийти обратно",
         "tj": "баргаштан, бозгашт кардан"},
        {"no": 9,  "zh": "分钟",  "pinyin": "fēnzhōng",  "pos": "n.",
         "uz": "daqiqa (vaqt birligi)",
         "ru": "минута (единица времени)",
         "tj": "дақиқа (воҳиди вақт)"},
        {"no": 10, "zh": "后",    "pinyin": "hòu",       "pos": "n.",
         "uz": "keyin, so'ng",
         "ru": "после, позже",
         "tj": "баъд аз, пас аз"},
        {"no": 11, "zh": "衣服",  "pinyin": "yīfu",      "pos": "n.",
         "uz": "kiyim",
         "ru": "одежда",
         "tj": "либос, кӯйлак"},
        {"no": 12, "zh": "漂亮",  "pinyin": "piàoliang", "pos": "adj.",
         "uz": "chiroyli, go'zal",
         "ru": "красивый, симпатичный",
         "tj": "зебо, хушрӯй"},
        {"no": 13, "zh": "啊",    "pinyin": "a",         "pos": "part.",
         "uz": "ha, voy (undov yuklamasi)",
         "ru": "ах, да (восклицательная частица)",
         "tj": "оҳ, ҳа (зарраи ҳайҷонӣ)"},
        {"no": 14, "zh": "少",    "pinyin": "shǎo",      "pos": "adj.",
         "uz": "kam, oz",
         "ru": "мало, немного",
         "tj": "кам, андак"},
        {"no": 15, "zh": "这些",  "pinyin": "zhèxiē",    "pos": "pron.",
         "uz": "bular, shu narsalar",
         "ru": "эти, эти вещи",
         "tj": "инҳо, ин чизҳо"},
        {"no": 16, "zh": "都",    "pinyin": "dōu",       "pos": "adv.",
         "uz": "hammasi, barchasi",
         "ru": "все, всё, оба",
         "tj": "ҳама, тамом"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Yotoqxonada — kecha nima qilding",
            "scene_ru": "В комнате — что делал вчера",
            "scene_tj": "Дар хоб — дирӯз чӣ кардӣ",
            "dialogue": [
                {"speaker": "A", "zh": "昨天上午你去哪儿了？",   "pinyin": "Zuótiān shàngwǔ nǐ qù nǎr le?",
                 "uz": "Kecha ertalab qayerga bordingiz?",
                 "ru": "Куда вы ходили вчера утром?",
                 "tj": "Дирӯз субҳ шумо куҷо рафтед?"},
                {"speaker": "B", "zh": "我去商店买东西了。",     "pinyin": "Wǒ qù shāngdiàn mǎi dōngxi le.",
                 "uz": "Men do'konga narsa sotib olishga bordim.",
                 "ru": "Я ходил в магазин за покупками.",
                 "tj": "Ман ба дӯкон рафтам, чизҳо харидам."},
                {"speaker": "A", "zh": "你买什么了？",           "pinyin": "Nǐ mǎi shénme le?",
                 "uz": "Nima sotib oldingiz?",
                 "ru": "Что вы купили?",
                 "tj": "Шумо чӣ харидед?"},
                {"speaker": "B", "zh": "我买了一点儿苹果。",     "pinyin": "Wǒ mǎile yīdiǎnr píngguǒ.",
                 "uz": "Men bir oz olma sotib oldim.",
                 "ru": "Я купил немного яблок.",
                 "tj": "Ман каме себ харидам."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Kompaniyada — Zhang janobni ko'rdingizmi",
            "scene_ru": "В компании — видели ли вы господина Чжана",
            "scene_tj": "Дар ширкат — ҷаноби Чжанро дидед",
            "dialogue": [
                {"speaker": "A", "zh": "你看见张先生了吗？",        "pinyin": "Nǐ kànjiàn Zhāng xiānsheng le ma?",
                 "uz": "Janob Jangni ko'rdingizmi?",
                 "ru": "Вы видели господина Чжана?",
                 "tj": "Шумо ҷаноби Чжанро дидед?"},
                {"speaker": "B", "zh": "看见了，他去学开车了。",    "pinyin": "Kànjiàn le, tā qù xué kāi chē le.",
                 "uz": "Ko'rdim, u mashina haydashni o'rganishga ketdi.",
                 "ru": "Да, видел — он пошёл учиться водить машину.",
                 "tj": "Ҳа, дидам — ӯ рафт рондани мошинро биомӯзад."},
                {"speaker": "A", "zh": "他什么时候能回来？",        "pinyin": "Tā shénme shíhou néng huílai?",
                 "uz": "Qachon qaytib kela oladi?",
                 "ru": "Когда он сможет вернуться?",
                 "tj": "Ӯ кай баргашта метавонад?"},
                {"speaker": "B", "zh": "40分钟后回来。",           "pinyin": "Sìshí fēnzhōng hòu huílai.",
                 "uz": "40 daqiqadan keyin qaytadi.",
                 "ru": "Вернётся через 40 минут.",
                 "tj": "Баъд аз 40 дақиқа бармегардад."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Do'kon oldida — kiyimlar",
            "scene_ru": "У магазина — одежда",
            "scene_tj": "Дар назди дӯкон — либосҳо",
            "dialogue": [
                {"speaker": "A", "zh": "王方的衣服太漂亮了！",     "pinyin": "Wáng Fāng de yīfu tài piàoliang le!",
                 "uz": "Van Fanning kiyimlari juda chiroyli!",
                 "ru": "Одежда Ван Фан такая красивая!",
                 "tj": "Либоси Ван Фан хеле зебо аст!"},
                {"speaker": "B", "zh": "是啊，她买了不少衣服。",   "pinyin": "Shì a, tā mǎile bùshǎo yīfu.",
                 "uz": "Ha, u juda ko'p kiyim sotib oldi.",
                 "ru": "Да уж — она купила немало одежды.",
                 "tj": "Ҳа, ӯ хеле зиёд либос харид."},
                {"speaker": "A", "zh": "你买什么了？",             "pinyin": "Nǐ mǎi shénme le?",
                 "uz": "Siz nima sotib oldingiz?",
                 "ru": "А вы что купили?",
                 "tj": "Шумо чӣ харидед?"},
                {"speaker": "B", "zh": "我没买，这些都是王方的东西。","pinyin": "Wǒ méi mǎi, zhèxiē dōu shì Wáng Fāng de dōngxi.",
                 "uz": "Men hech narsa sotib olmadim, bular hammasi Van Fanning narsalari.",
                 "ru": "Я ничего не купила — всё это вещи Ван Фан.",
                 "tj": "Ман ҳеҷ чиз нахаридам, инҳо ҳама чизҳои Ван Фан аст."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "了 — harakat tugallangani",
            "title_uz": "了 — tugallangan harakat",
            "title_ru": "了 — завершённое действие",
            "title_tj": "了 — амали анҷомшуда",
            "rule_uz": (
                "了(le) gapning oxirida — harakatning sodir bo'lganligi yoki tugallanganligini bildiradi.\n\n"
                "Tuzilish:\n"
                "Ega + Fe'l + 了 (gapning oxiri)\n"
                "Ega + Fe'l + 了 + Son/Sifat + Ot\n\n"
                "Misol:\n"
                "我去商店了。— Men do'konga bordim.\n"
                "她买了不少衣服。— U juda ko'p kiyim sotib oldi.\n\n"
                "Inkor: 没 + Fe'l (了 tushirib qoldiriladi)\n"
                "我没买。— Men hech narsa sotib olmadim.\n"
                "她没去商店。— U do'konga bormadi."
            ),
            "rule_ru": (
                "了(le) в конце предложения — указывает, что действие произошло или завершилось.\n\n"
                "Структура:\n"
                "Подлежащее + Глагол + 了 (конец предложения)\n"
                "Подлежащее + Глагол + 了 + Число/Прилагательное + Существительное\n\n"
                "Пример:\n"
                "我去商店了。— Я ходил в магазин.\n"
                "她买了不少衣服。— Она купила немало одежды.\n\n"
                "Отрицание: 没 + Глагол (了 опускается)\n"
                "我没买。— Я ничего не купил.\n"
                "她没去商店。— Она не ходила в магазин."
            ),
            "rule_tj": (
                "了(le) дар охири ҷумла — нишон медиҳад, ки амал рӯй додааст ё анҷом ёфтааст.\n\n"
                "Сохтор:\n"
                "Муб. + Феъл + 了 (охири ҷумла)\n"
                "Муб. + Феъл + 了 + Адад/Сифат + Исм\n\n"
                "Намуна:\n"
                "我去商店了。— Ман ба дӯкон рафтам.\n"
                "她买了不少衣服。— Ӯ хеле зиёд либос харид.\n\n"
                "Инкор: 没 + Феъл (了 меафтад)\n"
                "我没买。— Ман ҳеҷ чиз нахаридам.\n"
                "她没去商店。— Ӯ ба дӯкон нарафт."
            ),
            "examples": [
                {"zh": "我去商店了。",       "pinyin": "Wǒ qù shāngdiàn le.",
                 "uz": "Men do'konga bordim.", "ru": "Я ходил в магазин.", "tj": "Ман ба дӯкон рафтам."},
                {"zh": "她买了不少衣服。",   "pinyin": "Tā mǎile bùshǎo yīfu.",
                 "uz": "U juda ko'p kiyim sotib oldi.", "ru": "Она купила немало одежды.", "tj": "Ӯ хеле зиёд либос харид."},
                {"zh": "我没买。",           "pinyin": "Wǒ méi mǎi.",
                 "uz": "Men hech narsa sotib olmadim.", "ru": "Я ничего не купил.", "tj": "Ман ҳеҷ чиз нахаридам."},
            ]
        },
        {
            "no": 2,
            "title_zh": "名词 后",
            "title_uz": "后 vaqt belgisi",
            "title_ru": "后 — временной маркер",
            "title_tj": "后 — нишонаи вақт",
            "rule_uz": (
                "后(hòu) — muayyan voqeadan keyingi vaqtni bildiradi.\n\n"
                "40分钟后 — 40 daqiqadan keyin\n"
                "三天后 — uch kundan keyin\n"
                "一个星期后 — bir haftadan keyin\n"
                "五点后 — soat beshdan keyin\n\n"
                "Misol:\n"
                "40分钟后回来。— 40 daqiqadan keyin qaytadi.\n"
                "三天后我去北京。— Uch kundan keyin Pekinga boraman."
            ),
            "rule_ru": (
                "后(hòu) — указывает на момент времени после определённого события.\n\n"
                "40分钟后 — через 40 минут\n"
                "三天后 — через три дня\n"
                "一个星期后 — через одну неделю\n"
                "五点后 — после пяти часов\n\n"
                "Пример:\n"
                "40分钟后回来。— Вернётся через 40 минут.\n"
                "三天后我去北京。— Я поеду в Пекин через три дня."
            ),
            "rule_tj": (
                "后(hòu) — лаҳзаи вақтро баъд аз рӯйдоди муайян нишон медиҳад.\n\n"
                "40分钟后 — баъд аз 40 дақиқа\n"
                "三天后 — баъд аз се рӯз\n"
                "一个星期后 — баъд аз як ҳафта\n"
                "五点后 — баъд аз соати панҷ\n\n"
                "Намуна:\n"
                "40分钟后回来。— Баъд аз 40 дақиқа бармегардад.\n"
                "三天后我去北京。— Баъд аз се рӯз ман ба Пекин меравам."
            ),
            "examples": [
                {"zh": "40分钟后回来。",   "pinyin": "Sìshí fēnzhōng hòu huílai.",
                 "uz": "40 daqiqadan keyin qaytadi.", "ru": "Вернётся через 40 минут.", "tj": "Баъд аз 40 дақиқа бармегардад."},
                {"zh": "三天后见。",       "pinyin": "Sān tiān hòu jiàn.",
                 "uz": "Uch kundan keyin ko'rishamiz.", "ru": "Увидимся через три дня.", "tj": "Баъд аз се рӯз мебинамон."},
                {"zh": "八点后能来吗？",   "pinyin": "Bā diǎn hòu néng lái ma?",
                 "uz": "Soat sakkizdan keyin kela olasizmi?", "ru": "Вы можете прийти после восьми?", "tj": "Баъд аз соати ҳашт омада метавонед?"},
            ]
        },
        {
            "no": 3,
            "title_zh": "副词 都",
            "title_uz": "Ravish 都 — hammasi",
            "title_ru": "Наречие 都 — все, всё",
            "title_tj": "Зарфи 都 — ҳама",
            "rule_uz": (
                "都(dōu) — 'hammasi, barchasi, ikkalasi' ma'nosini bildiradi.\n"
                "Muhim: sanab o'tilayotgan narsalar 都 DAN OLDIN keladi.\n\n"
                "Misol:\n"
                "这些都是王方的东西。— Bular hammasi Van Fanning narsalari.\n"
                "我们都是中国人。— Biz hammamiz xitoylarmiz.\n"
                "他们都喜欢喝茶。— Ularning hammasi choy ichishni yaxshi ko'radi."
            ),
            "rule_ru": (
                "都(dōu) — означает 'все, всё, оба'.\n"
                "Важно: перечисляемые объекты стоят ПЕРЕД 都.\n\n"
                "Пример:\n"
                "这些都是王方的东西。— Всё это вещи Ван Фан.\n"
                "我们都是中国人。— Мы все китайцы.\n"
                "他们都喜欢喝茶。— Они все любят пить чай."
            ),
            "rule_tj": (
                "都(dōu) — маънои 'ҳама, тамом, ҳарду' дорад.\n"
                "Муҳим: чизҳои шуморидашуда ПЕШ АЗ 都 меоянд.\n\n"
                "Намуна:\n"
                "这些都是王方的东西。— Инҳо ҳама чизҳои Ван Фан аст.\n"
                "我们都是中国人。— Мо ҳама чинӣ ҳастем.\n"
                "他们都喜欢喝茶。— Онҳо ҳама чой нӯшиданро дӯст доранд."
            ),
            "examples": [
                {"zh": "这些都是王方的东西。", "pinyin": "Zhèxiē dōu shì Wáng Fāng de dōngxi.",
                 "uz": "Bular hammasi Van Fanning narsalari.", "ru": "Всё это вещи Ван Фан.", "tj": "Инҳо ҳама чизҳои Ван Фан аст."},
                {"zh": "我们都是中国人。",     "pinyin": "Wǒmen dōu shì Zhōngguó rén.",
                 "uz": "Biz hammamiz xitoylarmiz.", "ru": "Мы все китайцы.", "tj": "Мо ҳама чинӣ ҳастем."},
                {"zh": "他们都喜欢喝茶。",     "pinyin": "Tāmen dōu xǐhuan hē chá.",
                 "uz": "Ularning hammasi choy ichishni yaxshi ko'radi.", "ru": "Они все любят пить чай.", "tj": "Онҳо ҳама чой нӯшиданро дӯст доранд."},
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
                {"prompt_uz": "Kecha ertalab qayerga bordingiz?",          "prompt_ru": "Куда вы ходили вчера утром?",       "prompt_tj": "Дирӯз субҳ шумо куҷо рафтед?",          "answer": "昨天上午你去哪儿了？",  "pinyin": "Zuótiān shàngwǔ nǐ qù nǎr le?"},
                {"prompt_uz": "Men do'konga narsa sotib olishga bordim.",   "prompt_ru": "Я ходил в магазин за покупками.",   "prompt_tj": "Ман ба дӯкон рафтам, чизҳо харидам.",   "answer": "我去商店买东西了。",    "pinyin": "Wǒ qù shāngdiàn mǎi dōngxi le."},
                {"prompt_uz": "U juda ko'p kiyim sotib oldi.",             "prompt_ru": "Она купила немало одежды.",          "prompt_tj": "Ӯ хеле зиёд либос харид.",              "answer": "她买了不少衣服。",      "pinyin": "Tā mǎile bùshǎo yīfu."},
                {"prompt_uz": "40 daqiqadan keyin qaytadi.",               "prompt_ru": "Вернётся через 40 минут.",           "prompt_tj": "Баъд аз 40 дақиқа бармегардад.",        "answer": "40分钟后回来。",        "pinyin": "Sìshí fēnzhōng hòu huílai."},
                {"prompt_uz": "Bular hammasi uning narsalari.",             "prompt_ru": "Всё это его вещи.",                  "prompt_tj": "Инҳо ҳама чизҳои ӯ аст.",               "answer": "这些都是他的东西。",    "pinyin": "Zhèxiē dōu shì tā de dōngxi."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холигиро пур кунед:",
            "items": [
                {"prompt": "我去商店买东西___。",       "answer": "了",  "pinyin": "le"},
                {"prompt": "40分钟___回来。",           "answer": "后",  "pinyin": "hòu"},
                {"prompt": "这些___是王方的东西。",     "answer": "都",  "pinyin": "dōu"},
                {"prompt": "我___买，这些不是我的。",   "answer": "没",  "pinyin": "méi"},
            ]
        },
        {
            "no": 3,
            "type": "negative",
            "instruction_uz": "Gapni inkorga aylantiring (没 dan foydalanib):",
            "instruction_ru": "Сделайте предложение отрицательным (используя 没):",
            "instruction_tj": "Ҷумларо инкорӣ кунед (бо 没):",
            "items": [
                {"prompt": "她买了不少衣服。",
                 "answer": "她没买衣服。",     "pinyin": "Tā méi mǎi yīfu."},
                {"prompt": "我去商店了。",
                 "answer": "我没去商店。",     "pinyin": "Wǒ méi qù shāngdiàn."},
                {"prompt": "他看见张先生了。",
                 "answer": "他没看见张先生。", "pinyin": "Tā méi kànjiàn Zhāng xiānsheng."},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["昨天上午你去哪儿了？", "我去商店买东西了。", "她买了不少衣服。", "40分钟后回来。", "这些都是他的东西。"]},
        {"no": 2, "answers": ["了", "后", "都", "没"]},
        {"no": 3, "answers": ["她没买衣服。", "我没去商店。", "他没看见张先生。"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "了 dan foydalanib kecha haqida 4 ta gap yozing:",
            "instruction_ru": "Напишите 4 предложения о вчерашнем дне, используя 了:",
            "instruction_tj": "Бо 了 дар бораи дирӯз 4 ҷумла нависед:",
            "words": ["了", "没", "去", "买", "后", "分钟"],
            "example": "昨天我___了。我买了___。我没___。___后我回家了。",
        },
        {
            "no": 2,
            "instruction_uz": "都 dan foydalanib javob bering:",
            "instruction_ru": "Ответьте, используя 都:",
            "instruction_tj": "Бо 都 ҷавоб диҳед:",
            "items": [
                {"prompt": "你的朋友都是中国人吗？",
                 "hint_uz": "Ha yoki yo'q, 都 dan foydalanib",
                 "hint_ru": "Да/нет, используйте 都",
                 "hint_tj": "Ҳа/не, бо 都"},
                {"prompt": "桌子上的东西都是谁的？",
                 "hint_uz": "Kimin narsalari ekanligini ayting",
                 "hint_ru": "Скажите, чьи это вещи",
                 "hint_tj": "Гӯед, ин чизҳои кӣ аст"},
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
            print(f"Updated Lesson {LESSON['lesson_code']} — {LESSON['title']}.")
        else:
            lesson = CourseLesson(**LESSON)
            session.add(lesson)
            await session.commit()
            print(f"Created Lesson {LESSON['lesson_code']} — {LESSON['title']}.")


if __name__ == "__main__":
    asyncio.run(seed())
