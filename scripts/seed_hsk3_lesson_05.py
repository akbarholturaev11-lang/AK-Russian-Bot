import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk3",
    "lesson_order": 5,
    "lesson_code": "HSK3-L05",
    "title": "我最近越来越胖了",
    "goal": json.dumps({"uz": "'了' o'zgarishni bildirishi, '越来越+Adj' va 'для (了)' maqsad qolipini o'zlashtirish.", "ru": "Освоить 了 как изменение состояния, 越来越+Adj и конструкцию 为(了) для цели.", "tj": "Азхудкунии 了 ҳамчун ифодаи тағйирот, 越来越+Adj ва сохтори мақсади 为(了)."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda holat o'zgarishi, tobora kuchayish va maqsad ifodalash o'rganiladi. Sog'liq, mavsumlar, sport va kundalik hayot haqidagi suhbatlar orqali ko'nikmalar shakllanadi.", "ru": "В этом уроке изучается изменение состояния, нарастание качества и выражение цели. Навыки формируются через диалоги о здоровье, временах года, спорте и повседневной жизни.", "tj": "Дар ин дарс тағйироти ҳол, афзоиши сифат ва ифодаи мақсад омӯхта мешавад. Малакаҳо тавассути муколамаҳо дар бораи саломатӣ, фаслҳо, варзиш ва ҳаёти рӯзмарра ташаккул меёбанд."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "发烧",  "pinyin": "fāshāo",   "pos": "v.",   "uz": "isitma chiqmoq, harorat ko'tarilmoq", "ru": "температурить, иметь жар",       "tj": "таб кардан, иситма доштан"},
        {"no": 2,  "zh": "为",    "pinyin": "wèi",      "pos": "prep.","uz": "uchun (kimsa uchun), sababli",        "ru": "ради, для (кого-то)",            "tj": "барои (касе), ба хотири"},
        {"no": 3,  "zh": "照顾",  "pinyin": "zhàogù",   "pos": "v.",   "uz": "g'amxo'rlik qilmoq, parvarish qilmoq","ru": "заботиться, ухаживать",         "tj": "ғамхорӣ кардан, нигоҳубин кардан"},
        {"no": 4,  "zh": "感冒",  "pinyin": "gǎnmào",   "pos": "v./n.","uz": "shamollamoq; shamollash",             "ru": "простужаться; простуда",        "tj": "шамол хӯрдан; шамолхӯрдагӣ"},
        {"no": 5,  "zh": "季节",  "pinyin": "jìjié",    "pos": "n.",   "uz": "fasl (yil fasllari)",                 "ru": "сезон, время года",             "tj": "фасл (фаслҳои сол)"},
        {"no": 6,  "zh": "当然",  "pinyin": "dāngrán",  "pos": "adv.", "uz": "albatta, shubhasiz",                  "ru": "конечно, разумеется",           "tj": "албатта, бешубҳа"},
        {"no": 7,  "zh": "春天",  "pinyin": "chūntiān", "pos": "n.",   "uz": "bahor",                               "ru": "весна",                         "tj": "баҳор"},
        {"no": 8,  "zh": "夏天",  "pinyin": "xiàtiān",  "pos": "n.",   "uz": "yoz",                                 "ru": "лето",                          "tj": "тобистон"},
        {"no": 9,  "zh": "最近",  "pinyin": "zuìjìn",   "pos": "adv.", "uz": "so'nggi paytlarda, yaqinda",         "ru": "в последнее время, недавно",    "tj": "охирон, наздикӣ"},
        {"no": 10, "zh": "越",    "pinyin": "yuè",      "pos": "adv.", "uz": "tobora (ko'proq, kuchliroq)",         "ru": "всё более, чем дальше, тем...", "tj": "рӯ ба рӯ (бештар, қавитар)"},
        {"no": 11, "zh": "锻炼",  "pinyin": "duànliàn", "pos": "v.",   "uz": "sport mashq qilmoq, chiniqmoq",      "ru": "тренироваться, закаляться",     "tj": "машқ кардан, варзиш кардан"},
        {"no": 12, "zh": "体重",  "pinyin": "tǐzhòng",  "pos": "n.",   "uz": "tana og'irligi, vazn",               "ru": "вес тела",                      "tj": "вазни бадан"},
        {"no": 13, "zh": "草地",  "pinyin": "cǎodì",    "pos": "n.",   "uz": "maysa, o'tloq",                      "ru": "лужайка, трава",                "tj": "майдони чаман, алафзор"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Do'stlar ko'rishganda", "scene_ru": "Встреча друзей", "scene_tj": "Вохӯрии дӯстон",
            "dialogue": [
                {"speaker": "A", "zh": "哎，你最近是不是越来越胖了？", "pinyin": "Āi, nǐ zuìjìn shì bu shì yuèláiyuè pàng le?", "uz": "Hay, so'nggi paytlarda tobora semirmaydapsanmi?", "ru": "Эй, ты в последнее время всё толстеешь, да?", "tj": "Ҳай, оё шумо охирон рӯ ба рӯ фарбеҳ мешавед?"},
                {"speaker": "B", "zh": "唉，是啊！我最近体重越来越重了，不知道怎么办。", "pinyin": "Āi, shì a! Wǒ zuìjìn tǐzhòng yuèláiyuè zhòng le, bù zhīdào zěnme bàn.", "uz": "Ah, ha! So'nggi paytlarda vaznm tobora og'irlashyapti, nima qilishni bilmayapman.", "ru": "Да, увы! В последнее время мой вес всё растёт — не знаю, что делать.", "tj": "Ҳа, мутаассифона! Охирон вазнам рӯ ба рӯ вазнинтар мешавад, намедонам чӣ кунам."},
                {"speaker": "A", "zh": "你最近锻炼了吗？为了健康，应该多运动！", "pinyin": "Nǐ zuìjìn duànliàn le ma? Wèile jiànkāng, yīnggāi duō yùndòng!", "uz": "So'nggi paytlarda mashq qildingmi? Sog'liq uchun ko'proq sport qilish kerak!", "ru": "Ты в последнее время тренировался? Ради здоровья нужно больше двигаться!", "tj": "Охирон машқ кардед? Барои саломатӣ бояд бештар варзиш кард!"},
                {"speaker": "B", "zh": "没有，我越来越懒了。从明天开始，我一定要锻炼！", "pinyin": "Méiyǒu, wǒ yuèláiyuè lǎn le. Cóng míngtiān kāishǐ, wǒ yīdìng yào duànliàn!", "uz": "Yo'q, men tobora dangasalashib borayapman. Ertadan boshlab, albatta mashq qilaman!", "ru": "Нет, я всё больше ленюсь. С завтрашнего дня обязательно буду тренироваться!", "tj": "Не, ман рӯ ба рӯ танбалтар мешавам. Аз фардо сар карда, ҳатман машқ мекунам!"},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Bahor mavsumida kasallik", "scene_ru": "Болезнь весной", "scene_tj": "Беморӣ дар фасли баҳор",
            "dialogue": [
                {"speaker": "A", "zh": "春天天气变化多，你最近有没有感冒？", "pinyin": "Chūntiān tiānqì biànhuà duō, nǐ zuìjìn yǒu méiyǒu gǎnmào?", "uz": "Bahorda havo ko'p o'zgaradi, so'nggi paytlarda shamolladingizmi?", "ru": "Весной погода часто меняется — ты в последнее время не простужался?", "tj": "Баҳор ҳаво зиёд тағйир меёбад, оё охирон шамол нахӯрдед?"},
                {"speaker": "B", "zh": "发烧了，身体越来越不舒服，都怪这个季节！", "pinyin": "Fāshāo le, shēntǐ yuèláiyuè bù shūfu, dōu guài zhège jìjié!", "uz": "Isitma chiqdi, tanasim tobora yomonlashmoqda, barchasi shu faslning aybida!", "ru": "Поднялась температура, самочувствие всё хуже — всё из-за этого сезона!", "tj": "Таб баромад, ҳолатам рӯ ба рӯ бадтар мешавад, ҳама айби ин фасл аст!"},
                {"speaker": "A", "zh": "我来照顾你吧！需要什么药吗？", "pinyin": "Wǒ lái zhàogù nǐ ba! Xūyào shénme yào ma?", "uz": "Men sizga g'amxo'rlik qilay! Qandaydir dori kerakmi?", "ru": "Давай я за тобой поухаживаю! Тебе нужны лекарства?", "tj": "Биёед ман аз шумо ғамхорӣ кунам! Ягон дору лозим аст?"},
                {"speaker": "B", "zh": "谢谢你，当然需要！为了快点儿好，我要多喝水。", "pinyin": "Xièxie nǐ, dāngrán xūyào! Wèile kuài diǎnr hǎo, wǒ yào duō hē shuǐ.", "uz": "Rahmat, albatta kerak! Tezroq tuzalish uchun ko'proq suv ichishim kerak.", "ru": "Спасибо, конечно нужны! Чтобы быстрее выздороветь, буду пить больше воды.", "tj": "Раҳмат, албатта лозим аст! Барои зудтар хуб шудан бояд бештар об нӯшам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Parkdagi o'tloqda", "scene_ru": "На лужайке в парке", "scene_tj": "Дар чамани боғ",
            "dialogue": [
                {"speaker": "A", "zh": "草地上的人越来越多了，大家都来锻炼了！", "pinyin": "Cǎodì shàng de rén yuèláiyuè duō le, dàjiā dōu lái duànliàn le!", "uz": "O'tloqdagi odamlar tobora ko'paymoqda, hamma mashq qilgani keldi!", "ru": "На лужайке людей всё больше — все пришли тренироваться!", "tj": "Одамони дар чаман рӯ ба рӯ зиёд мешаванд, ҳама барои машқ омадаанд!"},
                {"speaker": "B", "zh": "是啊，天气越来越暖和了，夏天快来了！", "pinyin": "Shì a, tiānqì yuèláiyuè nuǎnhuo le, xiàtiān kuài lái le!", "uz": "Ha, havo tobora iliymoqda, yoz tez kelib qoladi!", "ru": "Точно, погода всё теплее — лето не за горами!", "tj": "Бале, ҳаво рӯ ба рӯ гармтар мешавад, тобистон зуд меояд!"},
                {"speaker": "A", "zh": "为了减肥，我每天早晨来这里跑步。", "pinyin": "Wèile jiǎnféi, wǒ měitiān zǎochén lái zhèlǐ pǎobù.", "uz": "Ozish uchun men har kuni ertalab bu yerga yugurgani kelaman.", "ru": "Чтобы похудеть, я каждое утро прихожу сюда бегать.", "tj": "Барои лоғар шудан ман ҳар рӯз субҳидам инҷо барои давидан меоям."},
                {"speaker": "B", "zh": "太好了！坚持下去，体重一定会越来越轻的！", "pinyin": "Tài hǎo le! Jiānchí xiàqù, tǐzhòng yīdìng huì yuèláiyuè qīng de!", "uz": "Juda yaxshi! Davom eting, vazningiz albatta tobora kamayib boradi!", "ru": "Отлично! Продолжайте — ваш вес обязательно будет всё меньше!", "tj": "Бисёр хуб! Давом диҳед, вазнатон ҳатман рӯ ба рӯ камтар мешавад!"},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Yil fasllarini taqqoslash", "scene_ru": "Сравнение времён года", "scene_tj": "Муқоисаи фаслҳои сол",
            "dialogue": [
                {"speaker": "A", "zh": "你喜欢哪个季节？春天还是夏天？", "pinyin": "Nǐ xǐhuan nǎge jìjié? Chūntiān háishi xiàtiān?", "uz": "Qaysi faslni yaxshi ko'rasiz? Bahor yoki yoz?", "ru": "Какое время года вам нравится — весна или лето?", "tj": "Шумо кадом фаслро дӯст медоред? Баҳор ё тобистон?"},
                {"speaker": "B", "zh": "我最喜欢春天，天气越来越暖，花越来越漂亮！", "pinyin": "Wǒ zuì xǐhuan chūntiān, tiānqì yuèláiyuè nuǎn, huā yuèláiyuè piàoliang!", "uz": "Men bahorna ko'proq yoqtiraman, havo tobora iliydi, gullar tobora chiroylashadi!", "ru": "Мне больше всего нравится весна — погода всё теплее, цветы всё красивее!", "tj": "Ман баҳорро бештар дӯст медорам, ҳаво рӯ ба рӯ гарм мешавад, гулҳо рӯ ба рӯ зеботар мешаванд!"},
                {"speaker": "A", "zh": "当然！春天是锻炼的好季节，对健康很好。", "pinyin": "Dāngrán! Chūntiān shì duànliàn de hǎo jìjié, duì jiànkāng hěn hǎo.", "uz": "Albatta! Bahor mashq qilish uchun yaxshi fasl, sog'liq uchun juda foydali.", "ru": "Конечно! Весна — хорошее время для тренировок, очень полезно для здоровья.", "tj": "Албатта! Баҳор фасли хуби машқ кардан аст, барои саломатӣ бисёр муфид аст."},
                {"speaker": "B", "zh": "对！为了健康，我打算从春天开始天天锻炼！", "pinyin": "Duì! Wèile jiànkāng, wǒ dǎsuàn cóng chūntiān kāishǐ tiāntiān duànliàn!", "uz": "To'g'ri! Sog'liq uchun men bahordan boshlab har kuni mashq qilishni rejalashtirdim!", "ru": "Точно! Ради здоровья планирую с весны тренироваться каждый день!", "tj": "Дуруст! Барои саломатӣ нақша дорам аз баҳор ҳар рӯз машқ кунам!"},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "\"了\"表示变化",
            "title_uz": "'了' holat o'zgarishini bildiradi",
            "title_ru": "«了» указывает на изменение состояния",
            "title_tj": "«了» тағйироти ҳолро нишон медиҳад",
            "rule_uz": (
                "Gap oxiridagi '了' holat yoki vaziyat o'zganiga ishora qiladi.\n"
                "Masalan: 天热了。(Havo isidi — avval sovuq edi.)\n"
                "         他来了。(U keldi — avval yo'q edi.)\n"
                "         我胖了。(Men semir bo'ldim — avval shunday emas edim.)\n"
                "Bu '了' va harakatning yakunlanishini bildiruvchi '了' dan farq qiladi.\n"
                "O'zgarish 了 ko'pincha holat fe'llari (形容词) bilan keladi."
            ),
            "rule_ru": (
                "Частица '了' в конце предложения указывает на изменение состояния или ситуации.\n"
                "Например: 天热了。(Стало жарко — раньше было не так.)\n"
                "          他来了。(Он пришёл — раньше его не было.)\n"
                "          我胖了。(Я поправился — раньше было иначе.)\n"
                "Это 了 отличается от 了, обозначающего завершение действия.\n"
                "Обычно сочетается с прилагательными-состояниями."
            ),
            "rule_tj": (
                "Зарраи '了' дар охири ҷумла тағйироти ҳол ё вазъиятро нишон медиҳад.\n"
                "Масалан: 天热了。(Гарм шуд — пеш чунин набуд.)\n"
                "         他来了。(Вай омад — пеш набуд.)\n"
                "         我胖了。(Ман фарбеҳ шудам — пеш чунин набудам.)\n"
                "Ин 了 аз 了-е, ки анҷоми амалро нишон медиҳад, фарқ дорад.\n"
                "Одатан бо феълҳои ҳолатӣ (сифатҳо) якҷоя меояд."
            ),
            "examples": [
                {"zh": "我最近体重越来越重了，不知道怎么办。", "pinyin": "Wǒ zuìjìn tǐzhòng yuèláiyuè zhòng le, bù zhīdào zěnme bàn.", "uz": "So'nggi paytlarda vaznm tobora og'irlashyapti, nima qilishni bilmayapman.", "ru": "В последнее время мой вес всё растёт — не знаю, что делать.", "tj": "Охирон вазнам рӯ ба рӯ вазнинтар мешавад, намедонам чӣ кунам."},
                {"zh": "发烧了，身体越来越不舒服。", "pinyin": "Fāshāo le, shēntǐ yuèláiyuè bù shūfu.", "uz": "Isitma chiqdi, tanasim tobora yomonlashmoqda.", "ru": "Поднялась температура, самочувствие всё хуже.", "tj": "Таб баромад, ҳолатам рӯ ба рӯ бадтар мешавад."},
            ]
        },
        {
            "no": 2,
            "title_zh": "\"越来越\"+Adj/V",
            "title_uz": "'越来越'+Sifat/fe'l — tobora..., borgan sari...",
            "title_ru": "«越来越»+Прил./Гл. — всё больше, чем дальше тем...",
            "title_tj": "«越来越»+Сифат/Феъл — рӯ ба рӯ..., ҳар бор бештар...",
            "rule_uz": (
                "'越来越' + sifat yoki fe'l: vaqt o'tishi bilan bir narsa tobora ortib yoki kamayib borishini bildiradi.\n"
                "Qolip: 越来越 + Sifat/fe'l\n"
                "Masalan:\n"
                "  越来越胖 (tobora semirmoq)\n"
                "  越来越热 (tobora issiq bo'lmoq)\n"
                "  越来越喜欢 (tobora yaxshi ko'rmoq)\n"
                "Inkor: 越来越不+Sifat (越来越不舒服 — tobora yomonlashmoq)"
            ),
            "rule_ru": (
                "'越来越' + прилагательное или глагол: с течением времени что-то всё больше нарастает.\n"
                "Структура: 越来越 + Прил./Гл.\n"
                "Например:\n"
                "  越来越胖 (всё толстеть)\n"
                "  越来越热 (всё жарче)\n"
                "  越来越喜欢 (нравиться всё больше)\n"
                "Отрицание: 越来越不+Прил. (越来越不舒服 — всё хуже самочувствие)"
            ),
            "rule_tj": (
                "'越来越' + сифат ё феъл: бо гузашти вақт чизе рӯ ба рӯ зиёд ё кам мешавад.\n"
                "Сохтор: 越来越 + Сифат/Феъл\n"
                "Масалан:\n"
                "  越来越胖 (рӯ ба рӯ фарбеҳ шудан)\n"
                "  越来越热 (рӯ ба рӯ гармтар шудан)\n"
                "  越来越喜欢 (рӯ ба рӯ дӯст доштан)\n"
                "Инкор: 越来越不+Сифат (越来越不舒服 — рӯ ба рӯ бадтар шудан)"
            ),
            "examples": [
                {"zh": "我最近越来越胖了，不知道怎么办。", "pinyin": "Wǒ zuìjìn yuèláiyuè pàng le, bù zhīdào zěnme bàn.", "uz": "So'nggi paytlarda tobora semirmoqdaman, nima qilishni bilmayapman.", "ru": "В последнее время я всё толстею — не знаю, что делать.", "tj": "Охирон ман рӯ ба рӯ фарбеҳ мешавам, намедонам чӣ кунам."},
                {"zh": "天气越来越暖和了，夏天快来了！", "pinyin": "Tiānqì yuèláiyuè nuǎnhuo le, xiàtiān kuài lái le!", "uz": "Havo tobora iliymoqda, yoz tez kelib qoladi!", "ru": "Погода всё теплее — лето не за горами!", "tj": "Ҳаво рӯ ба рӯ гармтар мешавад, тобистон зуд меояд!"},
            ]
        },
        {
            "no": 3,
            "title_zh": "\"为(了)\"+目的",
            "title_uz": "'为(了)' + maqsad — ...uchun, ...maqsadida",
            "title_ru": "«为(了)» + цель — ради..., для того чтобы...",
            "title_tj": "«为(了)» + мақсад — барои..., бо мақсади...",
            "rule_uz": (
                "'为' yoki '为了' + maqsad jumlasi: biror ishning nima uchun bajarilishini bildiradi.\n"
                "Qolip: 为(了) + Maqsad + Asosiy gap\n"
                "Masalan:\n"
                "  为了健康，我每天锻炼。(Sog'liq uchun har kuni mashq qilaman.)\n"
                "  为了减肥，我来这里跑步。(Ozish uchun bu yerga yugurgani kelaman.)\n"
                "  为了快点儿好，我要多喝水。(Tezroq tuzalish uchun ko'proq suv ichaman.)"
            ),
            "rule_ru": (
                "'为' или '为了' + целевое предложение: объясняет, ради чего совершается действие.\n"
                "Структура: 为(了) + Цель + Основное предложение\n"
                "Например:\n"
                "  为了健康，我每天锻炼。(Ради здоровья тренируюсь каждый день.)\n"
                "  为了减肥，我来这里跑步。(Чтобы похудеть, прихожу сюда бегать.)\n"
                "  为了快点儿好，我要多喝水。(Чтобы быстрее выздороветь, буду пить воду.)"
            ),
            "rule_tj": (
                "'为' ё '为了' + ҷумлаи мақсад: шарҳ медиҳад, ки амал барои чӣ иҷро мешавад.\n"
                "Сохтор: 为(了) + Мақсад + Ҷумлаи асосӣ\n"
                "Масалан:\n"
                "  为了健康，我每天锻炼。(Барои саломатӣ ҳар рӯз машқ мекунам.)\n"
                "  为了减肥，我来这里跑步。(Барои лоғар шудан инҷо меоям медавам.)\n"
                "  为了快点儿好，我要多喝水。(Барои зудтар хуб шудан бештар об менӯшам.)"
            ),
            "examples": [
                {"zh": "为了健康，你应该多锻炼！", "pinyin": "Wèile jiànkāng, nǐ yīnggāi duō duànliàn!", "uz": "Sog'liq uchun ko'proq mashq qilish kerak!", "ru": "Ради здоровья нужно больше тренироваться!", "tj": "Барои саломатӣ бояд бештар машқ кард!"},
                {"zh": "为了快点儿好，我要多喝水。", "pinyin": "Wèile kuài diǎnr hǎo, wǒ yào duō hē shuǐ.", "uz": "Tezroq tuzalish uchun ko'proq suv ichishim kerak.", "ru": "Чтобы быстрее выздороветь, буду пить больше воды.", "tj": "Барои зудтар хуб шудан бояд бештар об нӯшам."},
            ]
        },
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
            "instruction_ru": "Напишите по-китайски следующие слова:",
            "instruction_tj": "Калимаҳои зеринро бо хитоӣ нависед:",
            "items": [
                {"prompt_uz": "isitma chiqmoq", "prompt_ru": "температурить, иметь жар", "prompt_tj": "таб кардан", "answer": "发烧", "pinyin": "fāshāo"},
                {"prompt_uz": "g'amxo'rlik qilmoq", "prompt_ru": "заботиться, ухаживать", "prompt_tj": "ғамхорӣ кардан", "answer": "照顾", "pinyin": "zhàogù"},
                {"prompt_uz": "fasl (yil fasllari)", "prompt_ru": "сезон, время года", "prompt_tj": "фасл", "answer": "季节", "pinyin": "jìjié"},
                {"prompt_uz": "sport mashq qilmoq", "prompt_ru": "тренироваться", "prompt_tj": "машқ кардан, варзиш кардан", "answer": "锻炼", "pinyin": "duànliàn"},
                {"prompt_uz": "tana og'irligi, vazn", "prompt_ru": "вес тела", "prompt_tj": "вазни бадан", "answer": "体重", "pinyin": "tǐzhòng"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (越来越、为了、当然、了):",
            "instruction_ru": "Вставьте подходящее слово (越来越、为了、当然、了):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (越来越、为了、当然、了):",
            "items": [
                {"prompt_uz": "我最近______胖了，要多锻炼。", "prompt_ru": "В последнее время я всё толстею, нужно больше тренироваться.", "prompt_tj": "Охирон ман ______фарбеҳ мешавам, бояд бештар машқ кунам.", "answer": "越来越", "pinyin": "yuèláiyuè"},
                {"prompt_uz": "______健康，我每天早晨跑步。", "prompt_ru": "______здоровья я каждое утро бегаю.", "prompt_tj": "______саломатӣ ман ҳар рӯз субҳ медавам.", "answer": "为了", "pinyin": "wèile"},
                {"prompt_uz": "发烧______，身体很不舒服。", "prompt_ru": "Температура______— самочувствие очень плохое.", "prompt_tj": "Таб баромад______, ҳолатам хеле бад аст.", "answer": "了", "pinyin": "le"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "为了健康，我每天早晨来这里跑步。", "prompt_ru": "为了健康，我每天早晨来这里跑步。", "prompt_tj": "为了健康，我每天早晨来这里跑步。", "answer": "Sog'liq uchun men har kuni ertalab bu yerga yugurgani kelaman.", "pinyin": "Wèile jiànkāng, wǒ měitiān zǎochén lái zhèlǐ pǎobù."},
                {"prompt_uz": "我最近体重越来越重了，不知道怎么办。", "prompt_ru": "我最近体重越来越重了，不知道怎么办。", "prompt_tj": "我最近体重越来越重了，不知道怎么办。", "answer": "So'nggi paytlarda vaznm tobora og'irlashyapti, nima qilishni bilmayapman.", "pinyin": "Wǒ zuìjìn tǐzhòng yuèláiyuè zhòng le, bù zhīdào zěnme bàn."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["发烧", "照顾", "季节", "锻炼", "体重"]},
        {"no": 2, "answers": ["越来越", "为了", "了"]},
        {"no": 3, "answers": [
            "Sog'liq uchun men har kuni ertalab bu yerga yugurgani kelaman.",
            "So'nggi paytlarda vaznm tobora og'irlashyapti, nima qilishni bilmayapman.",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'越来越' qolipidan foydalanib hayotingizda o'zgargan 4 ta narsa haqida yozing.",
            "instruction_ru": "Используя '越来越', напишите о 4 вещах, которые изменились в вашей жизни.",
            "instruction_tj": "Бо истифода аз '越来越' 4 чизеро, ки дар ҳаёти шумо тағйир ёфтааст, нависед.",
            "words": ["越来越忙", "越来越好", "越来越难", "越来越有意思"],
            "topic_uz": "Hayotimdagi o'zgarishlar",
            "topic_ru": "Изменения в моей жизни",
            "topic_tj": "Тағйиротҳо дар ҳаёти ман",
        },
        {
            "no": 2,
            "instruction_uz": "'为了……' qolipini ishlatib, sog'liq va sport haqida 5-6 gapdan iborat matn yozing.",
            "instruction_ru": "Используя конструкцию '为了……', напишите 5–6 предложений о здоровье и спорте.",
            "instruction_tj": "Бо истифода аз сохтори '为了……' 5-6 ҷумла дар бораи саломатӣ ва варзиш нависед.",
            "topic_uz": "Sog'lik uchun men nima qilaman",
            "topic_ru": "Что я делаю ради здоровья",
            "topic_tj": "Барои саломатӣ ман чӣ мекунам",
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
