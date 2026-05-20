import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 8,
    "lesson_code": "HSK2-L08",
    "title": "让我想想再告诉你",
    "goal": json.dumps({"uz": "Taklif so'rash, ruxsat berish va harakatni keyinga qoldirish haqida gapira olish; '……好吗' savol qolipini, 再 ravishin, 让 pivotal fe'lni va fe'llarning takrorlanishini o'zlashtirish.", "ru": "Научиться просить разрешения, откладывать действие; освоить вопросную конструкцию '……好吗', наречие 再, глагол-пивот 让 и удвоение глаголов.", "tj": "Омӯзиши хостани иҷозат, ба баъд гузоштани амал; аз бар кардани сохтори саволии '……好吗', зарфи 再, феъли пивотии 让 ва такрори феълҳо."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda biror narsani so'rash, kutish va qaror qilishni kechiktirish kabi kundalik vaziyatlar o'rganiladi. Kinoga borish, do'stni ko'rish va mehmonxona muammolari mavzularida gapira olasiz. Asosiy grammatik mavzular: '……好吗' savol qolipi, 再 (yana, keyin) ravishi, 让 pivotal fe'li va fe'llarning takrorlanishi.", "ru": "В этом уроке изучаются повседневные ситуации: просьба, ожидание, откладывание решения. Вы сможете говорить о походе в кино, посещении друга и проблемах в гостинице. Основные грамматические темы: вопросная конструкция '……好吗', наречие 再 (снова, потом), глагол-пивот 让 и удвоение глаголов.", "tj": "Дар ин дарс вазъиятҳои рӯзмарра омӯхта мешаванд: дархост кардан, интизор мондан ва ба баъд гузоштани қарор. Шумо метавонед дар бораи рафтан ба кино, дидани дӯст ва мушкилоти меҳмонхона гап занед. Мавзӯҳои асосии грамматикӣ: сохтори саволии '……好吗', зарфи 再 (боз, баъд), феъли пивотии 让 ва такрори феълҳо."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "再",    "pinyin": "zài",      "pos": "adv.", "uz": "yana, keyin, qayta (kelajak uchun)",        "ru": "снова, потом, опять (о будущем)",         "tj": "боз, баъд, дубора (барои оянда)"},
        {"no": 2,  "zh": "让",    "pinyin": "ràng",     "pos": "v.",   "uz": "ruxsat bermoq, qo'ymoq; buyurmoq",         "ru": "позволять, разрешать; приказывать",        "tj": "иҷозат додан; дастур додан"},
        {"no": 3,  "zh": "告诉",  "pinyin": "gàosu",    "pos": "v.",   "uz": "aytib bermoq, xabar bermoq",               "ru": "сказать, сообщить",                        "tj": "гуфтан, хабар додан"},
        {"no": 4,  "zh": "等",    "pinyin": "děng",     "pos": "v.",   "uz": "kutmoq",                                   "ru": "ждать",                                    "tj": "интизор мондан"},
        {"no": 5,  "zh": "找",    "pinyin": "zhǎo",     "pos": "v.",   "uz": "qidirmoq, izlamoq; topmoq",                "ru": "искать; найти",                            "tj": "ҷустан, пайдо кардан"},
        {"no": 6,  "zh": "事情",  "pinyin": "shìqing",  "pos": "n.",   "uz": "ish, vazifa; voqea",                        "ru": "дело, задача; событие",                    "tj": "кор, вазифа; ҳодиса"},
        {"no": 7,  "zh": "服务员","pinyin": "fúwùyuán", "pos": "n.",   "uz": "xizmatchi, ofitsiant",                      "ru": "служащий, официант",                       "tj": "хизматрасон, официант"},
        {"no": 8,  "zh": "白",    "pinyin": "bái",      "pos": "adj.", "uz": "oq (rang)",                                 "ru": "белый (цвет)",                             "tj": "сафед (ранг)"},
        {"no": 9,  "zh": "黑",    "pinyin": "hēi",      "pos": "adj.", "uz": "qora (rang)",                               "ru": "чёрный (цвет)",                            "tj": "сиёҳ (ранг)"},
        {"no": 10, "zh": "贵",    "pinyin": "guì",      "pos": "adj.", "uz": "qimmat, narxi yuqori",                      "ru": "дорогой, высокая цена",                    "tj": "гарон, нарх баланд"},
        {"no": 11, "zh": "病",    "pinyin": "bìng",     "pos": "v./n.", "uz": "kasal bo'lmoq; kasallik",                   "ru": "болеть; болезнь",                          "tj": "бемор шудан; беморӣ"},
        {"no": 12, "zh": "运动",  "pinyin": "yùndòng",  "pos": "v./n.", "uz": "sport qilmoq; sport, mashq",                "ru": "заниматься спортом; спорт, движение",      "tj": "варзиш кардан; варзиш"},
        {"no": 13, "zh": "颜色",  "pinyin": "yánsè",    "pos": "n.",   "uz": "rang",                                       "ru": "цвет",                                     "tj": "ранг"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Darsxonada",
            "scene_ru": "В классе",
            "scene_tj": "Дар синфхона",
            "dialogue": [
                {"speaker": "A", "zh": "我们下午去看电影，好吗？", "pinyin": "Wǒmen xiàwǔ qù kàn diànyǐng, hǎo ma?", "uz": "Tushdan keyin kino ko'rgani boramizmi?", "ru": "Давай во второй половине дня сходим в кино, хорошо?", "tj": "Биёед баъд аз нисфирӯзӣ ба кино равем, хуб аст?"},
                {"speaker": "B", "zh": "今天下午我没有时间，明天下午再去吧。", "pinyin": "Jīntiān xiàwǔ wǒ méiyǒu shíjiān, míngtiān xiàwǔ zài qù ba.", "uz": "Bugun tushdan keyin vaqtim yo'q, ertaga tushdan keyin boramiz.", "ru": "Сегодня после полудня у меня нет времени, пойдём завтра.", "tj": "Имрӯз баъд аз нисфирӯзӣ вақт надорам, фардо равем."},
                {"speaker": "A", "zh": "你想看什么电影？", "pinyin": "Nǐ xiǎng kàn shénme diànyǐng?", "uz": "Qanday film ko'rmoqchisan?", "ru": "Какой фильм ты хочешь посмотреть?", "tj": "Ту чӣ филм дидан мехоҳӣ?"},
                {"speaker": "B", "zh": "让我想想再告诉你。", "pinyin": "Ràng wǒ xiǎngxiang zài gàosu nǐ.", "uz": "Bir o'ylab, keyin aytaman.", "ru": "Дай подумаю и потом скажу.", "tj": "Бигзор андеша кунам, баъд мегӯям."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Yotoqxonada",
            "scene_ru": "В общежитии",
            "scene_tj": "Дар хобгоҳ",
            "dialogue": [
                {"speaker": "A", "zh": "外边天气很好，我们出去运动运动吧！", "pinyin": "Wàibian tiānqì hěn hǎo, wǒmen chūqù yùndòng yùndòng ba!", "uz": "Tashqarida havo juda yaxshi, chiqib sport qilaylik!", "ru": "На улице хорошая погода, выйдем позанимаемся спортом!", "tj": "Берун хаво хуб аст, биёем чоре варзиш кунем!"},
                {"speaker": "B", "zh": "你等等我，好吗？王老师让我给大卫打个电话。", "pinyin": "Nǐ děngdeng wǒ, hǎo ma? Wáng lǎoshī ràng wǒ gěi Dàwèi dǎ ge diànhuà.", "uz": "Menga bir kuting, bo'ladimi? Vang o'qituvchi Devidga qo'ng'iroq qilishimni so'radi.", "ru": "Подожди меня, хорошо? Учитель Ван попросил меня позвонить Дэвиду.", "tj": "Маро каме интизор шав, хуб аст? Устод Ван аз ман хост, ки ба Дэвид занг занам."},
                {"speaker": "A", "zh": "回来再打吧。找大卫有什么事情吗？", "pinyin": "Huílái zài dǎ ba. Zhǎo Dàwèi yǒu shénme shìqing ma?", "uz": "Qaytib kelgach qo'ng'iroq qilarsiz. Devidga nima ish bor?", "ru": "Позвони потом, когда вернёшься. Какое дело к Дэвиду?", "tj": "Баъди баргашт занг зан. Бо Дэвид чӣ кор дорӣ?"},
                {"speaker": "B", "zh": "听说大卫病了，我想找时间去看看他。", "pinyin": "Tīngshuō Dàwèi bìng le, wǒ xiǎng zhǎo shíjiān qù kànkan tā.", "uz": "Eshitdim, Devid kasal, uни ko'rgani borishga vaqt topmoqchiman.", "ru": "Говорят, Дэвид заболел, хочу найти время навестить его.", "tj": "Шунидам, Дэвид бемор шуд, мехоҳам вақт ёбам ва ӯро бинам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Mehmonxonaning qabulida",
            "scene_ru": "На стойке регистрации гостиницы",
            "scene_tj": "Дар қабулгоҳи меҳмонхона",
            "dialogue": [
                {"speaker": "A", "zh": "服务员，我房间的门打不开了。", "pinyin": "Fúwùyuán, wǒ fángjiān de mén dǎ bù kāi le.", "uz": "Ofitsiant, xonamning eshigi ochmayapti.", "ru": "Сотрудник, дверь моего номера не открывается.", "tj": "Хизматрасон, дари хонаи ман намекушояд."},
                {"speaker": "B", "zh": "您住哪个房间？", "pinyin": "Nín zhù nǎ ge fángjiān?", "uz": "Siz qaysi xonada turasiz?", "ru": "В каком номере вы проживаете?", "tj": "Шумо дар кадом хона ҳастед?"},
                {"speaker": "A", "zh": "317。", "pinyin": "Sān yāo qī.", "uz": "317-xona.", "ru": "317.", "tj": "317."},
                {"speaker": "B", "zh": "好的，我叫人去看看。", "pinyin": "Hǎo de, wǒ jiào rén qù kànkan.", "uz": "Xop, birovni yuborib qarayman.", "ru": "Хорошо, пошлю кого-нибудь посмотреть.", "tj": "Хуб, касеро мефиристам бинад."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Do'konda",
            "scene_ru": "В магазине",
            "scene_tj": "Дар мағоза",
            "dialogue": [
                {"speaker": "A", "zh": "你看看这几件衣服怎么样。", "pinyin": "Nǐ kànkan zhè jǐ jiàn yīfu zěnmeyàng.", "uz": "Bu bir nechta kiyimga bir qarab ber, qandayligini ayt.", "ru": "Посмотри на эти несколько вещей, как они?", "tj": "Ин чанд либосро каме бин, чӣ гуна?"},
                {"speaker": "B", "zh": "这件白的有点儿长，那件黑的有点儿贵。", "pinyin": "Zhè jiàn bái de yǒudiǎnr cháng, nà jiàn hēi de yǒudiǎnr guì.", "uz": "Bu oqi biroz uzun, u qorasi biroz qimmat.", "ru": "Эта белая немного длинная, та чёрная немного дорогая.", "tj": "Ин сафеда каме дароз, он сиёҳа каме гарон."},
                {"speaker": "A", "zh": "这件红的呢？这是今天新来的。", "pinyin": "Zhè jiàn hóng de ne? Zhè shì jīntiān xīn lái de.", "uz": "Bu qizilchi? Bu bugun yangi kelgan.", "ru": "А эта красная? Это новинка сегодняшнего дня.", "tj": "Ин сурхча чӣ? Ин имрӯз нав омадааст."},
                {"speaker": "B", "zh": "让我再看看。", "pinyin": "Ràng wǒ zài kànkan.", "uz": "Yana bir qarayin.", "ru": "Дай посмотрю ещё раз.", "tj": "Бигзор боз бинам."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "疑问句“……，好吗”",
            "title_uz": "Savol qolipi '……，好吗' (bo'ladimi?, xopmi?)",
            "title_ru": "Вопросная конструкция '……，好吗' (хорошо?, ладно?)",
            "title_tj": "Сохтори саволии '……，好吗' (хуб аст?, розӣ?)",
            "rule_uz": (
                "'……，好吗？' qolipida biror taklif yoki iltimos yumshoq tarzda bildiriladi.\n"
                "Gap oxirida '好吗？' qo'shiladi va 'bo'ladimi?, xopmi?' ma'nosini beradi.\n"
                "O'zbek tilidagi 'qilamizmi?, bo'ladimi?' iborasiga to'g'ri keladi."
            ),
            "rule_ru": (
                "Конструкция '……，好吗？' используется для мягкого предложения или просьбы.\n"
                "В конце предложения добавляется '好吗？' со значением 'хорошо?, ладно?'.\n"
                "Соответствует русскому 'сделаем?, ладно?'."
            ),
            "rule_tj": (
                "Сохтори '……，好吗？' барои ба таври нарм пешниҳод ё илтимос кардан истифода мешавад.\n"
                "Дар охири ҷумла '好吗？' илова мешавад бо маъноии 'хуб аст?, розӣ?'.\n"
                "Ба тоҷикӣ 'мекунем?, розӣ?' мувофиқат мекунад."
            ),
            "examples": [
                {"zh": "我们下午去看电影，好吗？", "pinyin": "Wǒmen xiàwǔ qù kàn diànyǐng, hǎo ma?", "uz": "Tushdan keyin kino ko'rgani boramizmi?", "ru": "Давай сходим в кино после полудня, хорошо?", "tj": "Баъд аз нисфирӯзӣ ба кино равем, хуб аст?"},
                {"zh": "你等等我，好吗？", "pinyin": "Nǐ děngdeng wǒ, hǎo ma?", "uz": "Menga bir kuting, bo'ladimi?", "ru": "Подожди меня, хорошо?", "tj": "Маро каме интизор шав, хуб аст?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "副词“再”",
            "title_uz": "Ravish 再 (yana, keyin, qayta — kelajak uchun)",
            "title_ru": "Наречие 再 (снова, потом, опять — о будущем)",
            "title_tj": "Зарфи 再 (боз, баъд, дубора — барои оянда)",
            "rule_uz": (
                "'再' ravishi 'yana, keyin, qayta' ma'nosini beradi.\n"
                "Kelajakda takrorlanadigan yoki keyinga qoldirilgan harakatni bildiradi.\n"
                "又 dan farqi shundaki, 再 kelajak uchun, 又 esa o'tgan uchun ishlatiladi."
            ),
            "rule_ru": (
                "Наречие '再' означает 'снова, потом, опять'.\n"
                "Обозначает действие, которое будет повторяться или откладывается на потом.\n"
                "Отличие от 又: 再 — для будущего, 又 — для прошедшего."
            ),
            "rule_tj": (
                "Зарфи '再' маъноии 'боз, баъд, дубора'-ро медиҳад.\n"
                "Амалеро нишон медиҳад, ки дар оянда такрор мешавад ё ба баъд гузошта мешавад.\n"
                "Фарқ аз 又: 再 — барои оянда, 又 — барои гузашта."
            ),
            "examples": [
                {"zh": "明天下午再去吧。", "pinyin": "Míngtiān xiàwǔ zài qù ba.", "uz": "Ertaga tushdan keyin boramiz.", "ru": "Пойдём завтра после полудня.", "tj": "Фардо баъд аз нисфирӯзӣ равем."},
                {"zh": "让我再看看。", "pinyin": "Ràng wǒ zài kànkan.", "uz": "Yana bir qarayin.", "ru": "Дай посмотрю ещё раз.", "tj": "Бигзор боз бинам."},
            ]
        },
        {
            "no": 3,
            "title_zh": "兼语句",
            "title_uz": "Pivotal gap (让/叫 + kishi + fe'l)",
            "title_ru": "Пивотальное предложение (让/叫 + человек + глагол)",
            "title_tj": "Ҷумлаи пивотӣ (让/叫 + шахс + феъл)",
            "rule_uz": (
                "Pivotal gapda birinchi fe'lning to'ldiruvchisi ikkinchi fe'lning egaligini bajaradi.\n"
                "Masalan, '让 + kishi + fe'l' qolipida: 让 — ruxsat bermoq/buyurmoq,\n"
                "keyin boshqa kishi va uning harakati keladi.\n"
                "'叫 + kishi + fe'l' ham shu qolipga kiradi."
            ),
            "rule_ru": (
                "В пивотальном предложении дополнение первого глагола является подлежащим второго.\n"
                "В конструкции '让 + человек + глагол': 让 — позволять/приказывать,\n"
                "затем следует другой человек и его действие.\n"
                "'叫 + человек + глагол' тоже относится к этому типу."
            ),
            "rule_tj": (
                "Дар ҷумлаи пивотӣ пуркунандаи феъли аввал мубтадои феъли дуввум мегардад.\n"
                "Дар сохтори '让 + шахс + феъл': 让 — иҷозат додан/дастур додан,\n"
                "баъд шахси дигар ва амали ӯ меояд.\n"
                "'叫 + шахс + феъл' ҳам ба ҳамин намуд дохил мешавад."
            ),
            "examples": [
                {"zh": "王老师让我给大卫打个电话。", "pinyin": "Wáng lǎoshī ràng wǒ gěi Dàwèi dǎ ge diànhuà.", "uz": "Vang o'qituvchi menga Devidga qo'ng'iroq qilishimni so'radi.", "ru": "Учитель Ван попросил меня позвонить Дэвиду.", "tj": "Устод Ван аз ман хост, ки ба Дэвид занг занам."},
                {"zh": "我叫人去看看。", "pinyin": "Wǒ jiào rén qù kànkan.", "uz": "Birovni yuborib qarayman.", "ru": "Пошлю кого-нибудь посмотреть.", "tj": "Касеро мефиристам бинад."},
            ]
        },
        {
            "no": 4,
            "title_zh": "动词的重叠",
            "title_uz": "Fe'lning takrorlanishi (kamaytirish ma'nosi)",
            "title_ru": "Удвоение глагола (смягчение действия)",
            "title_tj": "Такрори феъл (сабуктарини амал)",
            "rule_uz": (
                "Fe'lni takrorlash harakatning qisqa yoki engil bajarilishini bildiradi.\n"
                "Bir bo'g'inli fe'l AB shaklida (看看, 想想),\n"
                "ikki bo'g'inli fe'l ABAB shaklida (运动运动) takrorlanadi.\n"
                "Bu usul muloyim yoki noaniq ifodalar uchun ishlatiladi."
            ),
            "rule_ru": (
                "Удвоение глагола означает краткое или лёгкое выполнение действия.\n"
                "Односложный глагол удваивается по схеме AB (看看, 想想),\n"
                "двусложный — по схеме ABAB (运动运动).\n"
                "Используется для смягчённых или неопределённых выражений."
            ),
            "rule_tj": (
                "Такрори феъл нишон медиҳад, ки амал кӯтоҳ ё сабук иҷро мешавад.\n"
                "Феъли яктаҳарфа бо схемаи AB такрор мешавад (看看, 想想),\n"
                "феъли дутаҳарфа бо схемаи ABAB (运动运动).\n"
                "Барои ифодаҳои нарм ё ноаниқ истифода мешавад."
            ),
            "examples": [
                {"zh": "让我想想再告诉你。", "pinyin": "Ràng wǒ xiǎngxiang zài gàosu nǐ.", "uz": "Bir o'ylab, keyin aytaman.", "ru": "Дай подумаю и потом скажу.", "tj": "Бигзор андеша кунам, баъд мегӯям."},
                {"zh": "我们出去运动运动吧。", "pinyin": "Wǒmen chūqù yùndòng yùndòng ba.", "uz": "Chiqib sport qilaylik.", "ru": "Выйдем позанимаемся спортом.", "tj": "Биёем берун чоре варзиш кунем."},
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
                {"prompt_uz": "aytib bermoq",         "prompt_ru": "сказать, сообщить",       "prompt_tj": "гуфтан, хабар додан",    "answer": "告诉",  "pinyin": "gàosu"},
                {"prompt_uz": "kutmoq",                "prompt_ru": "ждать",                   "prompt_tj": "интизор мондан",         "answer": "等",    "pinyin": "děng"},
                {"prompt_uz": "qidirmoq",              "prompt_ru": "искать",                  "prompt_tj": "ҷустан",                 "answer": "找",    "pinyin": "zhǎo"},
                {"prompt_uz": "xizmatchi, ofitsiant",  "prompt_ru": "служащий, официант",      "prompt_tj": "хизматрасон, официант",  "answer": "服务员","pinyin": "fúwùyuán"},
                {"prompt_uz": "qimmat",                "prompt_ru": "дорогой",                 "prompt_tj": "гарон",                  "answer": "贵",    "pinyin": "guì"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (让、再、好吗、等等、告诉):",
            "instruction_ru": "Вставьте подходящее слово (让、再、好吗、等等、告诉):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (让、再、好吗、等等、告诉):",
            "items": [
                {"prompt_uz": "______我想想______你。", "prompt_ru": "______我想想______你。", "prompt_tj": "______我想想______你。", "answer": "让 / 告诉", "pinyin": "ràng / gàosu"},
                {"prompt_uz": "你______我，______？", "prompt_ru": "你______我，______？", "prompt_tj": "你______我，______？", "answer": "等等 / 好吗", "pinyin": "děngdeng / hǎo ma"},
                {"prompt_uz": "明天______去看电影吧。", "prompt_ru": "明天______去看电影吧。", "prompt_tj": "明天______去看电影吧。", "answer": "再", "pinyin": "zài"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "让我想想再告诉你。", "prompt_ru": "让我想想再告诉你。", "prompt_tj": "让我想想再告诉你。", "answer": "Bir o'ylab, keyin aytaman.", "pinyin": "Ràng wǒ xiǎngxiang zài gàosu nǐ."},
                {"prompt_uz": "王老师让我给大卫打个电话。", "prompt_ru": "王老师让我给大卫打个电话。", "prompt_tj": "王老师让我给大卫打个电话。", "answer": "Vang o'qituvchi menga Devidga qo'ng'iroq qilishimni so'radi.", "pinyin": "Wáng lǎoshī ràng wǒ gěi Dàwèi dǎ ge diànhuà."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["告诉", "等", "找", "服务员", "贵"]},
        {"no": 2, "answers": ["让 / 告诉", "等等 / 好吗", "再"]},
        {"no": 3, "answers": [
            "Bir o'ylab, keyin aytaman.",
            "Vang o'qituvchi menga Devidga qo'ng'iroq qilishimni so'radi.",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Fe'lni takrorlab 4 ta gap tuzing. Har bir gapda boshqa fe'l ishlating.",
            "instruction_ru": "Составьте 4 предложения с удвоением глагола. Используйте разные глаголы в каждом предложении.",
            "instruction_tj": "Бо такрори феъл 4 ҷумла тартиб диҳед. Дар ҳар ҷумла феъли дигар истифода баред.",
            "words": ["看看", "想想", "走走", "说说"],
            "example": "让我想想，再告诉你答案。",
        },
        {
            "no": 2,
            "instruction_uz": "Do'stingizga biror taklif qilib, '……好吗？' va '让……' qoliplaridan foydalanib kichik suhbat yozing (6-8 gap).",
            "instruction_ru": "Напишите небольшой диалог с другом, предлагая что-нибудь, используя '……好吗？' и '让……' (6–8 реплик).",
            "instruction_tj": "Бо дӯстатон муколамаи хурде нависед, чизеро пешниҳод карда, аз '……好吗？' ва '让……' истифода баред (6-8 ҷумла).",
            "topic_uz": "Do'st bilan suhbat",
            "topic_ru": "Разговор с другом",
            "topic_tj": "Суҳбат бо дӯст",
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
