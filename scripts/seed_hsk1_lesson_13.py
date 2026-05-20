import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 13,
    "lesson_code": "HSK1-L13",
    "title": "他在学做中国菜呢",
    "goal": json.dumps({
        "uz": "Davom etayotgan harakatlarni ifodalash (在...呢), telefon raqamlari va 吧 yuklamasi",
        "ru": "Выражение текущих действий (在...呢), телефонные номера и частица 吧",
        "tj": "Баёни амалҳои ҷорӣ (在...呢), рақамҳои телефон ва зарраи 吧",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "O'n uchinchi darsda siz hozir sodir bo'layotgan harakatlarni qanday ifodalashni, 在...呢 tuzilmasini va 吧 yuklamasini o'rganasiz. 10 ta yangi so'z, 3 ta dialog.",
        "ru": "В тринадцатом уроке вы научитесь выражать действия, происходящие прямо сейчас, использовать конструкцию 在...呢 и частицу 吧. 10 новых слов, 3 диалога.",
        "tj": "Дар дарси сездаҳум шумо ёд мегиред, ки амалҳои ҳоло ҷоришударо чӣ тавр баён кунед, сохтори 在...呢 ва зарраи 吧 -ро истифода баред. 10 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "喂",    "pinyin": "wèi",       "pos": "int.",
         "uz": "allo (telefonda)",
         "ru": "алло (по телефону)",
         "tj": "алло (аз телефон)"},
        {"no": 2,  "zh": "也",    "pinyin": "yě",        "pos": "adv.",
         "uz": "ham, shuningdek",
         "ru": "тоже, также",
         "tj": "ҳам, инчунин"},
        {"no": 3,  "zh": "学习",  "pinyin": "xuéxí",     "pos": "v.",
         "uz": "o'qimoq, o'rganmoq",
         "ru": "учиться, изучать",
         "tj": "хондан, омӯхтан"},
        {"no": 4,  "zh": "上午",  "pinyin": "shàngwǔ",   "pos": "n.",
         "uz": "ertalab (tushgacha)",
         "ru": "утро (до полудня)",
         "tj": "субҳ (то нисфирӯзӣ)"},
        {"no": 5,  "zh": "睡觉",  "pinyin": "shuì jiào", "pos": "v.",
         "uz": "uxlamoq",
         "ru": "спать",
         "tj": "хобидан, хоб кардан"},
        {"no": 6,  "zh": "电视",  "pinyin": "diànshì",   "pos": "n.",
         "uz": "televizor",
         "ru": "телевизор",
         "tj": "телевизор"},
        {"no": 7,  "zh": "喜欢",  "pinyin": "xǐhuan",    "pos": "v.",
         "uz": "yoqtirmoq, yaxshi ko'rmoq",
         "ru": "нравиться, любить",
         "tj": "дӯст доштан, хуш доштан"},
        {"no": 8,  "zh": "给",    "pinyin": "gěi",       "pos": "prep.",
         "uz": "uchun, ga (birovga)",
         "ru": "для, кому-то (кому)",
         "tj": "барои, ба (касе)"},
        {"no": 9,  "zh": "打电话", "pinyin": "dǎ diànhuà","pos": "v.",
         "uz": "qo'ng'iroq qilmoq, telefon qilmoq",
         "ru": "звонить по телефону",
         "tj": "занг задан, телефон кардан"},
        {"no": 10, "zh": "吧",    "pinyin": "ba",        "pos": "part.",
         "uz": "yumshatuvchi yukla (taklif yoki maslahat uchun)",
         "ru": "смягчающая частица (для предложений или советов)",
         "tj": "зарраи мулоим (барои пешниҳод ё маслиҳат)"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Telefonda — hozir nima qilyapsan",
            "scene_ru": "По телефону — что делаешь сейчас",
            "scene_tj": "Аз телефон — ҳоло чӣ мекунӣ",
            "dialogue": [
                {"speaker": "A", "zh": "喂，你在做什么呢？",              "pinyin": "Wèi, nǐ zài zuò shénme ne?",
                 "uz": "Allo, hozir nima qilyapsiz?",
                 "ru": "Алло, что вы сейчас делаете?",
                 "tj": "Алло, ҳоло чӣ мекунед?"},
                {"speaker": "B", "zh": "我在看书呢。",                    "pinyin": "Wǒ zài kàn shū ne.",
                 "uz": "Men hozir kitob o'qiyapman.",
                 "ru": "Я сейчас читаю книгу.",
                 "tj": "Ман ҳоло китоб мехонам."},
                {"speaker": "A", "zh": "大卫也在看书吗？",                "pinyin": "Dàwèi yě zài kàn shū ma?",
                 "uz": "Devid ham kitob o'qiyaptimi?",
                 "ru": "Дэвид тоже читает?",
                 "tj": "Дэвид ҳам китоб мехонад?"},
                {"speaker": "B", "zh": "他没看书，他在学做中国菜呢。",    "pinyin": "Tā méi kàn shū, tā zài xué zuò Zhōngguó cài ne.",
                 "uz": "U kitob o'qiyotgani yo'q, u hozir xitoy taomi pishirishni o'rganayapti.",
                 "ru": "Он не читает — он сейчас учится готовить китайскую еду.",
                 "tj": "Ӯ китоб намехонад, ӯ ҳоло тарзи пухтани хӯроки чинӣро меомӯзад."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Qahvaxonada — kecha nima qilding",
            "scene_ru": "В кафе — что делал вчера",
            "scene_tj": "Дар қаҳвахона — дирӯз чӣ кардӣ",
            "dialogue": [
                {"speaker": "A", "zh": "昨天上午你在做什么呢？",          "pinyin": "Zuótiān shàngwǔ nǐ zài zuò shénme ne?",
                 "uz": "Kecha ertalab nima qilyotgan edingiz?",
                 "ru": "Что вы делали вчера утром?",
                 "tj": "Дирӯз субҳ чӣ мекардед?"},
                {"speaker": "B", "zh": "我在睡觉呢。你呢？",              "pinyin": "Wǒ zài shuì jiào ne. Nǐ ne?",
                 "uz": "Men uxlayotgan edim. Siz-chi?",
                 "ru": "Я спал. А вы?",
                 "tj": "Ман мехобидам. Шумо чӣ?"},
                {"speaker": "A", "zh": "我在家看电视呢。你喜欢看电视吗？","pinyin": "Wǒ zài jiā kàn diànshì ne. Nǐ xǐhuan kàn diànshì ma?",
                 "uz": "Men uyda televizor ko'rayotgan edim. Televizor ko'rishni yaxshi ko'rasizmi?",
                 "ru": "Я смотрел телевизор дома. Вам нравится смотреть телевизор?",
                 "tj": "Ман дар хона телевизор тамошо мекардам. Шумо телевизор тамошо карданро дӯст медоред?"},
                {"speaker": "B", "zh": "我不喜欢看电视，我喜欢看电影。",  "pinyin": "Wǒ bù xǐhuan kàn diànshì, wǒ xǐhuan kàn diànyǐng.",
                 "uz": "Men televizor ko'rishni yaxshi ko'rmayman, men kino ko'rishni yaxshi ko'raman.",
                 "ru": "Я не люблю смотреть телевизор — мне нравится кино.",
                 "tj": "Ман телевизор тамошо карданро дӯст надорам, ман кино тамошо карданро дӯст дорам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Maktab ofisida — telefon raqami",
            "scene_ru": "В школьном офисе — телефонный номер",
            "scene_tj": "Дар офиси мактаб — рақами телефон",
            "dialogue": [
                {"speaker": "A", "zh": "82304155，这是李老师的电话吗？",     "pinyin": "Bā èr sān líng sì yāo wǔ wǔ, zhè shì Lǐ lǎoshī de diànhuà ma?",
                 "uz": "82304155, bu O'qituvchi Li ning telefon raqamimi?",
                 "ru": "82304155 — это телефон учителя Ли?",
                 "tj": "82304155, ин рақами телефони устод Лӣ аст?"},
                {"speaker": "B", "zh": "不是。她的电话是82304156。",         "pinyin": "Bú shì. Tā de diànhuà shì bā èr sān líng sì yāo wǔ liù.",
                 "uz": "Yo'q. Uning telefon raqami 82304156.",
                 "ru": "Нет. Её номер 82304156.",
                 "tj": "Не. Рақами телефони ӯ 82304156 аст."},
                {"speaker": "A", "zh": "好，我现在给她打电话。",             "pinyin": "Hǎo, wǒ xiànzài gěi tā dǎ diànhuà.",
                 "uz": "Yaxshi, men hozir unga qo'ng'iroq qilaman.",
                 "ru": "Хорошо, я сейчас ей позвоню.",
                 "tj": "Хуб, ман ҳоло ба ӯ занг мезанам."},
                {"speaker": "B", "zh": "她在工作呢，你下午打吧。",           "pinyin": "Tā zài gōngzuò ne, nǐ xiàwǔ dǎ ba.",
                 "uz": "U hozir ishda, tushdan keyin qo'ng'iroq qiling.",
                 "ru": "Она сейчас на работе — позвоните после обеда.",
                 "tj": "Ӯ ҳоло дар кор аст, баъдазнисфирӯзӣ занг бизанед."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "在……呢",
            "title_uz": "Hozirgi davom harakat 在……呢",
            "title_ru": "Продолжающееся действие 在……呢",
            "title_tj": "Амали идомаёбандаи ҳозира 在……呢",
            "rule_uz": (
                "Hozir davom etayotgan harakat uchun:\n"
                "1-tuzilish: 在 + Fe'l (+ To'ldiruvchi)\n"
                "2-tuzilish: Fe'l + To'ldiruvchi + 呢\n"
                "3-tuzilish: 在 + Fe'l + 呢 (ta'kidlash uchun)\n\n"
                "Misol:\n"
                "我在看书呢。— Men hozir kitob o'qiyapman.\n"
                "他在学做中国菜呢。— U hozir xitoy taomi pishirishni o'rganayapti.\n\n"
                "Inkor: 没(在) + Fe'l, 呢 ishlatilmaydi\n"
                "他没看书。— U kitob o'qiyotgani yo'q.\n"
                "他们没在工作。— Ular ishlamayapti."
            ),
            "rule_ru": (
                "Для действия, происходящего прямо сейчас:\n"
                "Структура 1: 在 + Глагол (+ Дополнение)\n"
                "Структура 2: Глагол + Дополнение + 呢\n"
                "Структура 3: 在 + Глагол + 呢 (усиленная)\n\n"
                "Пример:\n"
                "我在看书呢。— Я сейчас читаю книгу.\n"
                "他在学做中国菜呢。— Он сейчас учится готовить китайскую еду.\n\n"
                "Отрицание: 没(在) + Глагол, без 呢\n"
                "他没看书。— Он не читает.\n"
                "他们没在工作。— Они не работают."
            ),
            "rule_tj": (
                "Барои амали ҳоло ҷоришуда:\n"
                "Сохтори 1: 在 + Феъл (+ Пуркунанда)\n"
                "Сохтори 2: Феъл + Пуркунанда + 呢\n"
                "Сохтори 3: 在 + Феъл + 呢 (таъкидӣ)\n\n"
                "Намуна:\n"
                "我在看书呢。— Ман ҳоло китоб мехонам.\n"
                "他在学做中国菜呢。— Ӯ ҳоло тарзи пухтани хӯроки чинӣро меомӯзад.\n\n"
                "Инкор: 没(在) + Феъл, бе 呢\n"
                "他没看书。— Ӯ китоб намехонад.\n"
                "他们没在工作。— Онҳо кор намекунанд."
            ),
            "examples": [
                {"zh": "我在看书呢。",         "pinyin": "Wǒ zài kàn shū ne.",
                 "uz": "Men hozir kitob o'qiyapman.", "ru": "Я сейчас читаю книгу.", "tj": "Ман ҳоло китоб мехонам."},
                {"zh": "他在学做中国菜呢。",   "pinyin": "Tā zài xué zuò Zhōngguó cài ne.",
                 "uz": "U hozir xitoy taomi pishirishni o'rganayapti.", "ru": "Он учится готовить китайскую еду.", "tj": "Ӯ тарзи пухтани хӯроки чинӣро меомӯзад."},
                {"zh": "她没在工作。",         "pinyin": "Tā méi zài gōngzuò.",
                 "uz": "U ishlamayapti.", "ru": "Она не работает.", "tj": "Ӯ кор намекунад."},
            ]
        },
        {
            "no": 2,
            "title_zh": "也",
            "title_uz": "也 ravishi — ham",
            "title_ru": "Наречие 也 — тоже",
            "title_tj": "Зарфи 也 — ҳам",
            "rule_uz": (
                "也(yě) — 'ham, shuningdek' ma'nosini bildiradi.\n"
                "Har doim fe'l yoki modal fe'ldan oldin keladi.\n\n"
                "Misol:\n"
                "大卫也在看书吗？— Devid ham kitob o'qiyaptimi?\n"
                "我也喜欢看电影。— Men ham kino ko'rishni yaxshi ko'raman.\n"
                "她也是老师。— U ham o'qituvchi."
            ),
            "rule_ru": (
                "也(yě) — означает 'тоже, также'.\n"
                "Всегда стоит перед глаголом или модальным глаголом.\n\n"
                "Пример:\n"
                "大卫也在看书吗？— Дэвид тоже читает?\n"
                "我也喜欢看电影。— Мне тоже нравится кино.\n"
                "她也是老师。— Она тоже учитель."
            ),
            "rule_tj": (
                "也(yě) — маънои 'ҳам, инчунин' дорад.\n"
                "Ҳамеша пеш аз феъл ё феъли модалӣ меояд.\n\n"
                "Намуна:\n"
                "大卫也在看书吗？— Дэвид ҳам китоб мехонад?\n"
                "我也喜欢看电影。— Ман ҳам кино тамошо карданро дӯст дорам.\n"
                "她也是老师。— Ӯ ҳам омӯзгор аст."
            ),
            "examples": [
                {"zh": "大卫也在看书吗？",   "pinyin": "Dàwèi yě zài kàn shū ma?",
                 "uz": "Devid ham kitob o'qiyaptimi?", "ru": "Дэвид тоже читает?", "tj": "Дэвид ҳам китоб мехонад?"},
                {"zh": "我也喜欢中国菜。",   "pinyin": "Wǒ yě xǐhuan Zhōngguó cài.",
                 "uz": "Men ham xitoy taomini yaxshi ko'raman.", "ru": "Мне тоже нравится китайская кухня.", "tj": "Ман ҳам хӯроки чинӣро дӯст дорам."},
                {"zh": "她也是学生。",       "pinyin": "Tā yě shì xuésheng.",
                 "uz": "U ham talaba.", "ru": "Она тоже студентка.", "tj": "Ӯ ҳам донишҷӯ аст."},
            ]
        },
        {
            "no": 3,
            "title_zh": "吧",
            "title_uz": "吧 — yumshatuvchi yukla",
            "title_ru": "Частица 吧 — смягчение",
            "title_tj": "Зарраи 吧 — мулоимкунӣ",
            "rule_uz": (
                "吧(ba) — taklif, maslahat yoki yumshatilgan buyruqni bildiradi.\n"
                "Gapning oxirida keladi.\n\n"
                "Misol:\n"
                "你下午打吧。— Tushdan keyin qo'ng'iroq qiling.\n"
                "今天我们在家吃饭吧。— Bugun uyda ovqatlanaylik.\n"
                "请坐吧。— Marhamat, o'tiring."
            ),
            "rule_ru": (
                "吧(ba) — выражает предложение, совет или мягкую команду.\n"
                "Стоит в конце предложения.\n\n"
                "Пример:\n"
                "你下午打吧。— Позвоните после обеда.\n"
                "今天我们在家吃饭吧。— Давайте сегодня поедим дома.\n"
                "请坐吧。— Пожалуйста, садитесь."
            ),
            "rule_tj": (
                "吧(ba) — пешниҳод, маслиҳат ё амри мулоимро баён мекунад.\n"
                "Дар охири ҷумла меояд.\n\n"
                "Намуна:\n"
                "你下午打吧。— Баъдазнисфирӯзӣ занг бизанед.\n"
                "今天我们在家吃饭吧。— Имрӯз дар хона хӯрок хӯрем.\n"
                "请坐吧。— Хоҳиш мекунам, биниш."
            ),
            "examples": [
                {"zh": "你下午打吧。",           "pinyin": "Nǐ xiàwǔ dǎ ba.",
                 "uz": "Tushdan keyin qo'ng'iroq qiling.", "ru": "Позвоните после обеда.", "tj": "Баъдазнисфирӯзӣ занг бизанед."},
                {"zh": "我们一起去吧。",         "pinyin": "Wǒmen yīqǐ qù ba.",
                 "uz": "Keling birga boraylik.", "ru": "Давайте пойдём вместе.", "tj": "Биёед якҷоя равем."},
                {"zh": "请坐吧。",               "pinyin": "Qǐng zuò ba.",
                 "uz": "Marhamat, o'tiring.", "ru": "Пожалуйста, садитесь.", "tj": "Хоҳиш мекунам, биниш."},
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
                {"prompt_uz": "Hozir nima qilyapsiz?",              "prompt_ru": "Что вы сейчас делаете?",          "prompt_tj": "Ҳоло чӣ мекунед?",              "answer": "你在做什么呢？",          "pinyin": "Nǐ zài zuò shénme ne?"},
                {"prompt_uz": "Men hozir kitob o'qiyapman.",         "prompt_ru": "Я сейчас читаю книгу.",           "prompt_tj": "Ман ҳоло китоб мехонам.",        "answer": "我在看书呢。",             "pinyin": "Wǒ zài kàn shū ne."},
                {"prompt_uz": "U ishlamayapti.",                     "prompt_ru": "Он не работает.",                 "prompt_tj": "Ӯ кор намекунад.",              "answer": "他没在工作。",             "pinyin": "Tā méi zài gōngzuò."},
                {"prompt_uz": "Men ham kino ko'rishni yaxshi ko'raman.","prompt_ru": "Мне тоже нравится кино.",     "prompt_tj": "Ман ҳам кино тамошо карданро дӯст дорам.", "answer": "我也喜欢看电影。", "pinyin": "Wǒ yě xǐhuan kàn diànyǐng."},
                {"prompt_uz": "Men hozir unga qo'ng'iroq qilaman.",  "prompt_ru": "Я сейчас ей позвоню.",            "prompt_tj": "Ман ҳоло ба ӯ занг мезанам.",   "answer": "我现在给她打电话。",       "pinyin": "Wǒ xiànzài gěi tā dǎ diànhuà."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холигиро пур кунед:",
            "items": [
                {"prompt": "我___看书呢。",               "answer": "在",   "pinyin": "zài"},
                {"prompt": "大卫___在看书吗？",           "answer": "也",   "pinyin": "yě"},
                {"prompt": "他没___书，他在学做菜呢。",   "answer": "看",   "pinyin": "kàn"},
                {"prompt": "你下午打___。",               "answer": "吧",   "pinyin": "ba"},
            ]
        },
        {
            "no": 3,
            "type": "phone_numbers",
            "instruction_uz": "Telefon raqamlarini xitoycha o'qing:",
            "instruction_ru": "Прочитайте телефонные номера по-китайски:",
            "instruction_tj": "Рақамҳои телефонро ба хитоӣ хонед:",
            "items": [
                {"prompt": "8069478",     "answer": "bā líng liù jiǔ sì qī bā"},
                {"prompt": "13851897623", "answer": "yāo sān bā wǔ yāo bā jiǔ liù èr sān"},
                {"prompt": "82304156",    "answer": "bā èr sān líng sì yāo wǔ liù"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["你在做什么呢？", "我在看书呢。", "他没在工作。", "我也喜欢看电影。", "我现在给她打电话。"]},
        {"no": 2, "answers": ["在", "也", "看", "吧"]},
        {"no": 3, "answers": ["bā líng liù jiǔ sì qī bā", "yāo sān bā wǔ yāo bā jiǔ liù èr sān", "bā èr sān líng sì yāo wǔ liù"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Kecha ertalab nima qilayotgan edingiz? 3-4 ta gap yozing:",
            "instruction_ru": "Что вы делали вчера утром? Напишите 3–4 предложения:",
            "instruction_tj": "Дирӯз субҳ чӣ мекардед? 3-4 ҷумла нависед:",
            "words": ["在", "呢", "也", "喜欢", "看书", "看电视", "睡觉", "学习"],
            "example": "昨天上午我在___呢。我___喜欢___。",
        },
        {
            "no": 2,
            "instruction_uz": "Do'st bilan telefon dialogini yozing (4 satr, 喂 bilan boshlang):",
            "instruction_ru": "Напишите телефонный диалог с другом (4 реплики, начиная с 喂):",
            "instruction_tj": "Муколамаи телефонии бо дӯст нависед (4 саф, аз 喂 оғоз кунед):",
            "example": "A: 喂，你在做什么呢？\nB: 我在___呢。\nA: ___也在___吗？\nB: 她___，她在___呢。",
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
