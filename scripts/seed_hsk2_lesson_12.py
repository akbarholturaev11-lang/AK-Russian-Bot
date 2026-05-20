import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 12,
    "lesson_code": "HSK2-L12",
    "title": "你穿得太少了",
    "goal": json.dumps({"uz": "Holat to'ldiruvchisi ('de' yuklamasi bilan) va 'bǐ' qiyoslash gapining kengaytirilgan shaklini o'rganish.", "ru": "Изучение дополнения состояния (с частицей 'de') и расширенной формы конструкции сравнения 'bǐ'.", "tj": "Омӯзиши илова ба ҳолат (бо зарраи 'de') ва шакли васеъшудаи конструксияи муқоисавии 'bǐ'."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda kundalik hayotdagi harakatlarni qanday bajarilganligini tasvirlashni o'rganamiz. 'De' yuklamasi yordamida holat to'ldiruvchisi hosil qilib, uyqu, ovqatlanish, kiyinish kabi harakatlarni baholashni mashq qilamiz. Shuningdek, 'bǐ' qiyoslovini fe'l birikmalariga tatbiq qilishni o'rganamiz.", "ru": "На этом уроке мы учимся описывать, как выполняются действия в повседневной жизни. Отрабатываем образование дополнения состояния с помощью частицы 'de' для оценки таких действий, как сон, еда, одевание. Также учимся применять сравнение 'bǐ' к глагольным конструкциям.", "tj": "Дар ин дарс ёд мегирем тавсиф кунем амалҳои ҳаррӯзаро чӣ тавр иҷро мешаванд. Бо ёрии зарраи 'de' иловаи ҳолат сохта, амалҳои хобидан, хӯрдан ва пӯшидан ро баҳо медиҳем. Инчунин истифодаи 'bǐ'-ро барои сохторҳои феълӣ меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "得", "pinyin": "de", "pos": "part.", "uz": "holat to'ldiruvchisi yuklamasi (fe'ldan keyin)", "ru": "частица дополнения состояния (после глагола)", "tj": "зарраи иловаи ҳолат (баъд аз феъл)"},
        {"no": 2, "zh": "妻子", "pinyin": "qīzi", "pos": "n.", "uz": "xotin, turmush o'rtoq (ayol)", "ru": "жена, супруга", "tj": "зан, ҳамсар (зан)"},
        {"no": 3, "zh": "雪", "pinyin": "xuě", "pos": "n.", "uz": "qor", "ru": "снег", "tj": "барф"},
        {"no": 4, "zh": "零", "pinyin": "líng", "pos": "num.", "uz": "nol", "ru": "ноль", "tj": "сифр"},
        {"no": 5, "zh": "度", "pinyin": "dù", "pos": "n./m.", "uz": "daraja (harorat o'lchovi)", "ru": "градус (единица температуры)", "tj": "дараҷа (воҳиди ҳарорат)"},
        {"no": 6, "zh": "穿", "pinyin": "chuān", "pos": "v.", "uz": "kiymoq (kiyim-bosh)", "ru": "надевать, носить (одежду)", "tj": "пӯшидан (либос)"},
        {"no": 7, "zh": "进", "pinyin": "jìn", "pos": "v.", "uz": "kirmoq", "ru": "войти, заходить", "tj": "даромадан"},
        {"no": 8, "zh": "弟弟", "pinyin": "dìdi", "pos": "n.", "uz": "uka", "ru": "младший брат", "tj": "бародари хурдӣ"},
        {"no": 9,  "zh": "近",  "pinyin": "jìn",    "pos": "adj.", "uz": "yaqin",                                   "ru": "близкий, недалёкий",             "tj": "наздик"},
        {"no": 10, "zh": "身体", "pinyin": "shēntǐ", "pos": "n.",   "uz": "tana, sog'liq",                           "ru": "тело, здоровье",                 "tj": "тан, саломатӣ"},
        {"no": 11, "zh": "少",  "pinyin": "shǎo",   "pos": "adj.", "uz": "oz, kam",                                  "ru": "мало, немного",                  "tj": "кам, андак"},
        {"no": 12, "zh": "早",  "pinyin": "zǎo",    "pos": "adj./adv.", "uz": "erta; ertaroq",                       "ru": "ранний; рано, пораньше",         "tj": "барвақт; зудтар"},
        {"no": 13, "zh": "冷",  "pinyin": "lěng",   "pos": "adj.", "uz": "sovuq",                                   "ru": "холодный",                       "tj": "сард"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Sinfxonada",
            "scene_ru": "В классе",
            "scene_tj": "Дар синфхона",
            "dialogue": [
                {"speaker": "A", "zh": "你每天早上几点起床？", "pinyin": "Nǐ měitiān zǎoshang jǐ diǎn qǐchuáng?", "uz": "Siz har kuni ertalab soat nechada turasiz?", "ru": "В котором часу ты встаёшь каждое утро?", "tj": "Ҳар рӯз субҳ шумо соати чанд бармехезед?"},
                {"speaker": "B", "zh": "六点多。", "pinyin": "Liù diǎn duō.", "uz": "Oltidan o'tganda.", "ru": "Чуть больше шести.", "tj": "Каме аз соати шаш гузашта."},
                {"speaker": "A", "zh": "你比我早起一个小时。", "pinyin": "Nǐ bǐ wǒ zǎo qǐ yí ge xiǎoshí.", "uz": "Siz mendan bir soat oldin turasiz.", "ru": "Ты встаёшь на час раньше меня.", "tj": "Шумо аз ман як соат зудтар бармехезед."},
                {"speaker": "B", "zh": "我睡得也早，我每天晚上十点就睡觉。早睡早起对身体好。", "pinyin": "Wǒ shuì de yě zǎo, wǒ měitiān wǎnshang shí diǎn jiù shuìjiào. Zǎo shuì zǎo qǐ duì shēntǐ hǎo.", "uz": "Men ham erta yotaman, har kuni kechqurun o'n da yotaman. Erta yotib erta turish sog'liq uchun foydali.", "ru": "Я тоже ложусь рано, каждый вечер в десять. Рано ложиться и рано вставать полезно для здоровья.", "tj": "Ман ҳам барвақт мехобам, ҳар шаб соати даҳ мехобам. Барвақт хобидан ва барвақт бархестан барои саломатӣ муфид аст."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Do'st uyida",
            "scene_ru": "В доме друга",
            "scene_tj": "Дар хонаи дӯст",
            "dialogue": [
                {"speaker": "A", "zh": "再来点儿米饭吧，你吃得太少了。", "pinyin": "Zài lái diǎnr mǐfàn ba, nǐ chī de tài shǎo le.", "uz": "Yana biroz guruch oling, siz juda oz yedingiz.", "ru": "Возьми ещё немного риса, ты съел(а) слишком мало.", "tj": "Боз каме биринҷ гиред, шумо хеле кам хӯрдед."},
                {"speaker": "B", "zh": "不心了，今天吃得很好，太谢谢你了。", "pinyin": "Bù xīn le, jīntiān chī de hěn hǎo, tài xièxie nǐ le.", "uz": "Kerak emas, bugun juda yaxshi yedim, katta rahmat sizga.", "ru": "Не надо, сегодня я поел(а) очень хорошо, большое тебе спасибо.", "tj": "Даркор нест, имрӯз хеле хуб хӯрдам, ташаккури зиёд."},
                {"speaker": "A", "zh": "你饭做得怎么样？", "pinyin": "Nǐ fàn zuò de zěnmeyàng?", "uz": "Siz ovqat qanday pishirasiz?", "ru": "Как ты готовишь еду?", "tj": "Шумо хӯрок чӣ хел мепазед?"},
                {"speaker": "B", "zh": "不怎么样，我妻子比我饭做得好。", "pinyin": "Bù zěnmeyàng, wǒ qīzi bǐ wǒ zuò fàn zuò de hǎo.", "uz": "Unchalik emas, xotinim mendan yaxshiroq ovqat pishiradi.", "ru": "Не очень, моя жена готовит лучше меня.", "tj": "Чандон не, занам аз ман беҳтар хӯрок мепазад."}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Uy eshigi oldida",
            "scene_ru": "У двери дома",
            "scene_tj": "Дар пеши дари хона",
            "dialogue": [
                {"speaker": "A", "zh": "下雪了，今天真冷。", "pinyin": "Xià xuě le, jīntiān zhēn lěng.", "uz": "Qor yog'yapti, bugun juda sovuq.", "ru": "Пошёл снег, сегодня очень холодно.", "tj": "Барф борид, имрӯз хеле сард аст."},
                {"speaker": "B", "zh": "有零下10度吧？", "pinyin": "Yǒu líng xià shí dù ba?", "uz": "Minus o'n daraja bo'lsa kerak?", "ru": "Наверное, минус десять градусов?", "tj": "Эҳтимол даҳ дараҷа зер аз сифр бошад?"},
                {"speaker": "A", "zh": "是啊，你穿得太少了，我们进房间吧。", "pinyin": "Shì a, nǐ chuān de tài shǎo le, wǒmen jìn fángjiān ba.", "uz": "Ha, siz juda kam kiyingiz, xonaga kiraylik.", "ru": "Да, ты слишком мало надел(а), давай зайдём в комнату.", "tj": "Бале, шумо хеле кам пӯшидед, биёед ба хона дарем."},
                {"speaker": "B", "zh": "好吧。", "pinyin": "Hǎo ba.", "uz": "Xo'p bo'lmasa.", "ru": "Ладно.", "tj": "Хуб."}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "你在忙什么呢？", "pinyin": "Nǐ zài máng shénme ne?", "uz": "Siz nima bilan bandsiniz?", "ru": "Чем ты сейчас занят(а)?", "tj": "Шумо ба чӣ машғул ҳастед?"},
                {"speaker": "B", "zh": "我弟弟让我帮他找个房子，现在他离公司有点儿远。", "pinyin": "Wǒ dìdi ràng wǒ bāng tā zhǎo ge fángzi, xiànzài tā lí gōngsī yǒudiǎnr yuǎn.", "uz": "Ukam menga unga uy topishda yordam berishimni so'radi, hozir u kompaniyadan biroz uzoqda turadi.", "ru": "Мой младший брат попросил помочь найти ему жильё, сейчас он живёт немного далеко от компании.", "tj": "Бародари хурдиам хоҳиш кард ба ӯ хона ёбам, ҳоло ӯ аз ширкат каме дур зиндагӣ мекунад."},
                {"speaker": "A", "zh": "住得远真的很累！", "pinyin": "Zhù de yuǎn zhēn de hěn lèi!", "uz": "Uzoqda yashash chindan ham charchatadi!", "ru": "Жить далеко действительно очень утомительно!", "tj": "Дур зиндагӣ кардан воқеан хеле монандакор аст!"},
                {"speaker": "B", "zh": "是啊，他也希望能住得近一点儿。", "pinyin": "Shì a, tā yě xīwàng néng zhù de jìn yìdiǎnr.", "uz": "Ha, u ham biroz yaqinroqda yashashni xohlaydi.", "ru": "Да, он тоже хочет жить немного ближе.", "tj": "Бале, ӯ ҳам мехоҳад каме наздиктар зиндагӣ кунад."}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "状态补语",
            "title_uz": "Holat to'ldiruvchisi",
            "title_ru": "Дополнение состояния",
            "title_tj": "Иловаи ҳолат",
            "rule_uz": "Holat to'ldiruvchisi fe'ldan keyin '得(de)' yuklamasi qo'shilib, harakatning qanday bajarilganligini yoki natijani bildiradi. Tuzilish: Fe'l + 得 + sifat/holat. Agar fe'lning to'ldiruvchisi bo'lsa, fe'l takrorlanadi: 做饭做得好. Inkor: 得 dan keyin '不' qo'yiladi: 做得不好.",
            "rule_ru": "Дополнение состояния образуется после глагола с частицей '得(de)' и описывает, как выполняется действие или каков его результат. Структура: Глагол + 得 + прилагательное/состояние. Если у глагола есть дополнение, глагол повторяется: 做饭做得好. Отрицание: после '得' ставится '不': 做得不好.",
            "rule_tj": "Иловаи ҳолат баъд аз феъл бо зарраи '得(de)' омада, тавсиф мекунад амал чӣ тавр иҷро мешавад ё натиҷааш чист. Сохтор: Феъл + 得 + сифат/ҳолат. Агар феъл иловаи хос дошта бошад, феъл такрор мешавад: 做饭做得好. Инкор: баъд аз '得' '不' гузошта мешавад: 做得不好.",
            "examples": [
                {"zh": "你穿得太少了。", "pinyin": "Nǐ chuān de tài shǎo le.", "uz": "Siz juda kam kiyingiz.", "ru": "Ты надел(а) слишком мало.", "tj": "Шумо хеле кам пӯшидед."},
                {"zh": "她睡得很早。", "pinyin": "Tā shuì de hěn zǎo.", "uz": "U juda erta yotadi.", "ru": "Она ложится спать очень рано.", "tj": "Ӯ хеле барвақт мехобад."}
            ]
        },
        {
            "no": 2,
            "title_zh": "“比”字句（2）",
            "title_uz": "'Bǐ' qiyoslash gapi (2)",
            "title_ru": "Предложения сравнения с 'bǐ' (2)",
            "title_tj": "Ҷумлаи муқоисавӣ бо 'bǐ' (2)",
            "rule_uz": "Fe'l birikmalarini qiyoslashda '比' quyidagicha ishlatiladi: A + 比 + B + fe'l + 得 + sifat. Yoki fe'l takrorlanadi: A + 比 + B + fe'l + fe'l + 得 + sifat. Masalan: 我妻子比我做饭做得好. Miqdor farqini qo'shish mumkin: 比我早起一个小时.",
            "rule_ru": "При сравнении глагольных конструкций '比' используется так: A + 比 + B + глагол + 得 + прилагательное. Или глагол повторяется: A + 比 + B + глагол + глагол + 得 + прилагательное. Например: 我妻子比我做饭做得好. Можно добавить разницу: 比我早起一个小时.",
            "rule_tj": "Ҳангоми муқоисаи сохторҳои феълӣ 'bǐ' чунин истифода мешавад: A + 比 + B + феъл + 得 + сифат. Ё феъл такрор мешавад: A + 比 + B + феъл + феъл + 得 + сифат. Масалан: 我妻子比我做饭做得好. Метавон фарқро ҳам зиёд кард: 比我早起一个小时.",
            "examples": [
                {"zh": "我妻子比我做饭做得好。", "pinyin": "Wǒ qīzi bǐ wǒ zuò fàn zuò de hǎo.", "uz": "Xotinim mendan yaxshiroq ovqat pishiradi.", "ru": "Моя жена готовит лучше меня.", "tj": "Занам аз ман беҳтар хӯрок мепазад."},
                {"zh": "你比我早起一个小时。", "pinyin": "Nǐ bǐ wǒ zǎo qǐ yí ge xiǎoshí.", "uz": "Siz mendan bir soat oldin turasiz.", "ru": "Ты встаёшь на час раньше меня.", "tj": "Шумо аз ман як соат зудтар бармехезед."}
            ]
        },
        {
            "no": 3,
            "title_zh": "趋向补语（进、出、上、下）",
            "title_uz": "Yo'nalish to'ldiruvchisi (进, 出, 上, 下)",
            "title_ru": "Направленное дополнение (进, 出, 上, 下)",
            "title_tj": "Иловаи самт (进, 出, 上, 下)",
            "rule_uz": (
                "Yo'nalish to'ldiruvchisi fe'ldan keyin kelib, harakatning yo'nalishini bildiradi.\n"
                "Oddiy shakl: fe'l + 进/出/上/下 (va h.k.)\n"
                "Murakkab shakl: fe'l + 进/出 + 来/去 (yaqin yoki uzoqlashuv uchun).\n"
                "Masalan: 进来 (kiring — yaqin), 进去 (kiring — uzoq), 出来/出去 (chiqing)."
            ),
            "rule_ru": (
                "Направленное дополнение ставится после глагола и указывает направление действия.\n"
                "Простая форма: глагол + 进/出/上/下 и т.д.\n"
                "Составная форма: глагол + 进/出 + 来/去 (для приближения или удаления).\n"
                "Например: 进来 (войдите — приближение), 进去 (войдите — удаление), 出来/出去 (выйдите)."
            ),
            "rule_tj": (
                "Иловаи самт баъд аз феъл меояд ва самти амалро нишон медиҳад.\n"
                "Шакли оддӣ: феъл + 进/出/上/下 ва ғ.\n"
                "Шакли мураккаб: феъл + 进/出 + 来/去 (барои наздик шудан ё дур шудан).\n"
                "Масалан: 进来 (дароед — наздик), 进去 (дароед — дур), 出来/出去 (берун шавед)."
            ),
            "examples": [
                {"zh": "外边冷，我们进房间吧。", "pinyin": "Wàibian lěng, wǒmen jìn fángjiān ba.", "uz": "Tashqari sovuq, xonaga kiraylik.", "ru": "На улице холодно, давай зайдём в комнату.", "tj": "Берун сард аст, биёем ба хона дарем."},
                {"zh": "她弟弟走进来了。", "pinyin": "Tā dìdi zǒu jìn lái le.", "uz": "Uning ukasi kirib keldi.", "ru": "Её младший брат вошёл (сюда).", "tj": "Бародари хурдиаш даромад."},
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
            "instruction_ru": "Напишите китайские эквиваленты следующих слов:",
            "instruction_tj": "Тарҷумаи чинии калимаҳои зеринро нависед:",
            "items": [
                {"prompt_uz": "qor", "prompt_ru": "снег", "prompt_tj": "барф", "answer": "雪", "pinyin": "xuě"},
                {"prompt_uz": "kiymoq", "prompt_ru": "надевать", "prompt_tj": "пӯшидан", "answer": "穿", "pinyin": "chuān"},
                {"prompt_uz": "uka", "prompt_ru": "младший брат", "prompt_tj": "бародари хурдӣ", "answer": "弟弟", "pinyin": "dìdi"},
                {"prompt_uz": "xotin", "prompt_ru": "жена", "prompt_tj": "зан", "answer": "妻子", "pinyin": "qīzi"},
                {"prompt_uz": "yaqin", "prompt_ru": "близкий", "prompt_tj": "наздик", "answer": "近", "pinyin": "jìn"}
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "U qo'shiq ayt___ juda yaxshi. (得)", "prompt_ru": "Она поёт очень хорошо. (得)", "prompt_tj": "Ӯ суруд хон___ хеле хуб аст. (得)", "answer": "得", "pinyin": "de"},
                {"prompt_uz": "Aka mendan ko'p ye___. (得)", "prompt_ru": "Старший брат ест больше меня. (得)", "prompt_tj": "Бародари калон аз ман бештар хӯр___. (得)", "answer": "得", "pinyin": "de"},
                {"prompt_uz": "Bugun ___ o'n daraja. (零)", "prompt_ru": "Сегодня ___ десять градусов. (零)", "prompt_tj": "Имрӯз ___ даҳ дараҷа. (零)", "answer": "零", "pinyin": "líng"},
                {"prompt_uz": "U juda uzoqda yasha___. (得)", "prompt_ru": "Он живёт очень далеко. (得)", "prompt_tj": "Ӯ хеле дур зиндагӣ мекун___. (得)", "answer": "得", "pinyin": "de"}
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "你穿得太少了，我们进房间吧。", "prompt_ru": "你穿得太少了，我们进房间吧。", "prompt_tj": "你穿得太少了，我们进房间吧。", "answer": "Siz juda kam kiyingiz, xonaga kiraylik.", "pinyin": "Nǐ chuān de tài shǎo le, wǒmen jìn fángjiān ba."},
                {"prompt_uz": "我妻子比我做饭做得好。", "prompt_ru": "我妻子比我做饭做得好。", "prompt_tj": "我妻子比我做饭做得好。", "answer": "Xotinim mendan yaxshiroq ovqat pishiradi.", "pinyin": "Wǒ qīzi bǐ wǒ zuò fàn zuò de hǎo."},
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["雪", "穿", "弟弟", "妻子", "近"]},
        {"no": 2, "answers": ["得", "得", "零", "得"]},
        {"no": 3, "answers": [
            "Siz juda kam kiyingiz, xonaga kiraylik.",
            "Xotinim mendan yaxshiroq ovqat pishiradi.",
        ]}
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Holat to'ldiruvchisi ('de') ishlatib oila a'zolaringiz yoki do'stlaringizni tasvirlang: ular qanday gapiradi, yuradi, ovqatlanadi va h.k. Kamida 4 jumla yozing.",
            "instruction_ru": "Используя дополнение состояния ('de'), опишите членов своей семьи или друзей: как они говорят, ходят, едят и т.д. Напишите не менее 4 предложений.",
            "instruction_tj": "Бо истифодаи иловаи ҳолат ('de') аъзоёни оила ё дӯстонатонро тавсиф кунед: онҳо чӣ хел гап мезананд, мераванд, хӯрок мехӯранд ва ғ. Камаш 4 ҷумла нависед.",
            "words": ["得", "比……得"],
            "example": "妈妈做饭做得很好。",
            "topic_uz": "Oila va do'stlar tavsifi",
            "topic_ru": "Описание семьи и друзей",
            "topic_tj": "Тавсифи оила ва дӯстон"
        },
        {
            "no": 2,
            "instruction_uz": "Kiyinish va ob-havo haqida yozing: bugun qanday kiyindingiz, ob-havo qanday, nega bunday kiyindingiz.",
            "instruction_ru": "Напишите об одежде и погоде: как вы оделись сегодня, какая погода, почему вы так оделись.",
            "instruction_tj": "Дар бораи либос ва ҳаво нависед: имрӯз чӣ пӯшидед, ҳаво чӣ хел аст, чаро чунин пӯшидед.",
            "words": ["穿得", "零下", "度"],
            "example": "今天天气很冷，我穿得很多。",
            "topic_uz": "Bugungi kiyim va ob-havo",
            "topic_ru": "Сегодняшняя одежда и погода",
            "topic_tj": "Либоси имрӯза ва ҳаво"
        }
    ], ensure_ascii=False),
    "review_json": "[]",
    "is_active": True
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
