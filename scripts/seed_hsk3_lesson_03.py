import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk3",
    "lesson_order": 3,
    "lesson_code": "HSK3-L03",
    "title": "桌子上放着很多饮料",
    "goal": json.dumps({"uz": "'还是' va '或者' farqini, mavjudlik gapini va '会' ehtimol ma'nosini o'zlashtirish.", "ru": "Освоить разницу 还是/或者, предложение существования и значение вероятности 会.", "tj": "Азхудкунии фарқи 还是/或者, ҷумлаи мавҷудият ва маънои эҳтимолии 会."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda tanlov ifodalash, narsa mavjudligini tasvirlash va ehtimol bildirish o'rganiladi. Uy ziyofati, do'kon, tog' sayohati va mehmonxona muhitidagi suhbatlar orqali ko'nikmalar shakllanadi.", "ru": "В этом уроке изучается выражение выбора, описание существования предмета и вероятности. Навыки формируются через диалоги на вечеринке, в магазине, в горах и в гостинице.", "tj": "Дар ин дарс ифодаи интихоб, тасвири мавҷудияти чиз ва эҳтимол омӯхта мешавад. Малакаҳо тавассути муколамаҳо дар зиёфат, дӯкон, кӯҳ ва меҳмонхона ташаккул меёбанд."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "还是",  "pinyin": "háishi",   "pos": "conj.", "uz": "yoki (so'roqda)",                  "ru": "или (в вопросе)",                 "tj": "ё (дар савол)"},
        {"no": 2,  "zh": "或者",  "pinyin": "huòzhě",   "pos": "conj.", "uz": "yoki (darak gapda)",               "ru": "или (в утверждении)",             "tj": "ё (дар изҳор)"},
        {"no": 3,  "zh": "爬山",  "pinyin": "páshān",   "pos": "v.",   "uz": "tog'ga chiqmoq",                   "ru": "подниматься в горы",              "tj": "ба кӯҳ баромадан"},
        {"no": 4,  "zh": "小心",  "pinyin": "xiǎoxīn",  "pos": "adj.", "uz": "ehtiyotkor bo'lmoq",               "ru": "быть осторожным",                 "tj": "эҳтиёткор будан"},
        {"no": 5,  "zh": "条",    "pinyin": "tiáo",     "pos": "m.",   "uz": "dona (uzun narsalar uchun)",       "ru": "штука (для длинных предметов)",   "tj": "дона (барои чизҳои дароз)"},
        {"no": 6,  "zh": "裤子",  "pinyin": "kùzi",     "pos": "n.",   "uz": "shim",                             "ru": "брюки, штаны",                    "tj": "шалвор"},
        {"no": 7,  "zh": "记得",  "pinyin": "jìde",     "pos": "v.",   "uz": "esida tutmoq",                     "ru": "помнить",                         "tj": "дар хотир доштан"},
        {"no": 8,  "zh": "新鲜",  "pinyin": "xīnxiān",  "pos": "adj.", "uz": "yangi, toza (oziq-ovqat)",         "ru": "свежий (о продуктах)",            "tj": "тоза, сабза"},
        {"no": 9,  "zh": "甜",    "pinyin": "tián",     "pos": "adj.", "uz": "shirin",                           "ru": "сладкий",                         "tj": "ширин"},
        {"no": 10, "zh": "放",    "pinyin": "fàng",     "pos": "v.",   "uz": "qo'ymoq, joylashtirib qo'ymoq",   "ru": "класть, ставить",                 "tj": "гузоштан, мондан"},
        {"no": 11, "zh": "饮料",  "pinyin": "yǐnliào",  "pos": "n.",   "uz": "ichimlik, sharbat",                "ru": "напиток",                         "tj": "нӯшокӣ, шарбат"},
        {"no": 12, "zh": "舒服",  "pinyin": "shūfu",    "pos": "adj.", "uz": "qulay, yoqimli",                   "ru": "удобный, комфортный",             "tj": "роҳат, мувофиқ"},
        {"no": 13, "zh": "绿",    "pinyin": "lǜ",       "pos": "adj.", "uz": "yashil",                           "ru": "зелёный",                         "tj": "сабз"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Uy ziyofatida", "scene_ru": "На домашней вечеринке", "scene_tj": "Дар зиёфати хонагӣ",
            "dialogue": [
                {"speaker": "A", "zh": "桌子上放着很多饮料，你想喝茶还是果汁？", "pinyin": "Zhuōzi shàng fàng zhe hěn duō yǐnliào, nǐ xiǎng hē chá háishi guǒzhī?", "uz": "Stol ustida ko'p ichimlik bor, choy ichmoqchimisiz yoki mevali sharbat?", "ru": "На столе много напитков, ты хочешь чай или сок?", "tj": "Рӯйи миз нӯшокиҳои зиёд гузошта шудааст, шумо чой ё шарбати мева мехоҳед?"},
                {"speaker": "B", "zh": "来一杯果汁吧！这些水果看起来很新鲜。", "pinyin": "Lái yī bēi guǒzhī ba! Zhèxiē shuǐguǒ kànqǐlai hěn xīnxiān.", "uz": "Bir stakan mevali sharbat bering! Bu mevalar juda yangi ko'rinadi.", "ru": "Дайте сок! Эти фрукты выглядят очень свежими.", "tj": "Як пиёла шарбати мева биёред! Ин меваҳо хеле тоза менамоянд."},
                {"speaker": "A", "zh": "这是从南方带来的，又新鲜又甜！", "pinyin": "Zhè shì cóng nánfāng dài lái de, yòu xīnxiān yòu tián!", "uz": "Bularni janubdan olib kelgan, ham yangi ham shirin!", "ru": "Их привезли с юга — и свежие, и сладкие!", "tj": "Инҳоро аз ҷануб овардаанд, ҳам тоза ҳам ширин!"},
                {"speaker": "B", "zh": "真好！还有其他颜色的吗？我喜欢绿色的。", "pinyin": "Zhēn hǎo! Hái yǒu qítā yánsè de ma? Wǒ xǐhuan lǜ sè de.", "uz": "Juda yaxshi! Boshqa rangdagilari ham bormi? Men yashil ranglilarini yaxshi ko'raman.", "ru": "Отлично! А есть другие цвета? Мне нравятся зелёные.", "tj": "Бисёр хуб! Оё рангҳои дигар ҳам ҳаст? Ман сабзро дӯст медорам."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Kiyim-kechak do'konida", "scene_ru": "В магазине одежды", "scene_tj": "Дар дӯкони либос",
            "dialogue": [
                {"speaker": "A", "zh": "您好，您要买裤子还是裙子？", "pinyin": "Nínhǎo, nín yào mǎi kùzi háishi qúnzi?", "uz": "Salom, shim sotib olmoqchimisiz yoki yubka?", "ru": "Здравствуйте, вы хотите купить брюки или юбку?", "tj": "Салом, шумо шалвор мехоҳед харед ё дӯмон?"},
                {"speaker": "B", "zh": "我要买一条裤子，你们有没有绿色的？", "pinyin": "Wǒ yào mǎi yī tiáo kùzi, nǐmen yǒu méiyǒu lǜ sè de?", "uz": "Menga bir juft shim kerak, sizlarda yashil rangdagisi bormi?", "ru": "Мне нужны одни брюки, у вас есть зелёные?", "tj": "Ман як шалвор мехоҳам харам, оё шумо сабз доред?"},
                {"speaker": "A", "zh": "有，这边放着好几条呢，您喜欢深绿还是浅绿？", "pinyin": "Yǒu, zhèbiān fàng zhe hǎo jǐ tiáo ne, nín xǐhuan shēn lǜ háishi qiǎn lǜ?", "uz": "Bor, bu tomonda bir nechta turibdi, to'q yashilni yoqtirasizmi yoki och yashilni?", "ru": "Есть, здесь несколько штук — тёмно-зелёный или светло-зелёный?", "tj": "Ҳаст, ин тараф якчанд адад гузошта шудааст, сабзи торик ё сабзи равшан?"},
                {"speaker": "B", "zh": "浅绿吧！记得给我便宜一点儿，好吗？", "pinyin": "Qiǎn lǜ ba! Jìde gěi wǒ piányí yīdiǎnr, hǎo ma?", "uz": "Och yashil! Menga biroz arzonroq bering, bo'ladimi?", "ru": "Светло-зелёный! Помните — немного дешевле, хорошо?", "tj": "Сабзи равшан! Ёд доред — каме арзонтар диҳед, хуб аст?"},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Tog' sayohatida", "scene_ru": "В горном походе", "scene_tj": "Ҳангоми сайри кӯҳ",
            "dialogue": [
                {"speaker": "A", "zh": "你会爬山吗？今天我们打算去爬山。", "pinyin": "Nǐ huì páshān ma? Jīntiān wǒmen dǎsuàn qù páshān.", "uz": "Tog' tirmasha olasizmi? Bugun tog'ga chiqmoqchi edik.", "ru": "Ты умеешь лазать в горы? Сегодня планируем сходить.", "tj": "Оё ба кӯҳ баромада метавонӣ? Имрӯз нақша дорем ба кӯҳ равем."},
                {"speaker": "B", "zh": "会，但是我怕累。坐缆车还是走路上去？", "pinyin": "Huì, dànshì wǒ pà lèi. Zuò lǎnchē háishi zǒulù shàngqù?", "uz": "Chiqaman, lekin charchashdan qo'rqaman. Kanatli aravacha bilan yoki piyoda?", "ru": "Умею, но боюсь устать. На фуникулёре или пешком?", "tj": "Метавонам, аммо аз хастагӣ метарсам. Бо канаткаш ё пиёда?"},
                {"speaker": "A", "zh": "可以坐缆车或者走路，看你喜欢哪个。", "pinyin": "Kěyǐ zuò lǎnchē huòzhě zǒulù, kàn nǐ xǐhuan nǎge.", "uz": "Kanatli aravacha bilan yoki piyoda borish mumkin, o'zingiz tanlang.", "ru": "Можно на фуникулёре или пешком — на ваш выбор.", "tj": "Метавонед бо канаткаш ё пиёда, ба хоҳиши худ интихоб кунед."},
                {"speaker": "B", "zh": "那我们走路吧！小心一点儿，路上很滑。", "pinyin": "Nà wǒmen zǒulù ba! Xiǎoxīn yīdiǎnr, lùshang hěn huá.", "uz": "Unday bo'lsa piyoda boraylik! Ehtiyot bo'ling, yo'l juda sirpanchiq.", "ru": "Тогда идём пешком! Осторожнее — дорога скользкая.", "tj": "Пас пиёда равем! Эҳтиёт кунед, роҳ лағжон аст."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Mehmonxonada ro'yxatdan o'tish", "scene_ru": "Регистрация в гостинице", "scene_tj": "Қайдиёт дар меҳмонхона",
            "dialogue": [
                {"speaker": "A", "zh": "您好，您要单人间还是双人间？", "pinyin": "Nínhǎo, nín yào dānrén jiān háishi shuāngrén jiān?", "uz": "Salom, sizga bir kishilik xona kerakmi yoki ikki kishilik?", "ru": "Здравствуйте, вам одноместный или двухместный номер?", "tj": "Салом, ба шумо як нафара хона лозим аст ё ду нафара?"},
                {"speaker": "B", "zh": "两个人，要一间双人间。房间里有放空调吗？", "pinyin": "Liǎng ge rén, yào yī jiān shuāngrén jiān. Fángjiān lǐ yǒu fàng kōngtiáo ma?", "uz": "Ikki kishi uchun, ikki kishilik xona kerak. Xonada konditsioner bormi?", "ru": "Нас двое, нужен двухместный номер. В комнате есть кондиционер?", "tj": "Ду нафарем, як хонаи ду нафара лозим аст. Дар хона кондитсионер ҳаст?"},
                {"speaker": "A", "zh": "有，房间里放着空调、电视和冰箱，非常舒服。", "pinyin": "Yǒu, fángjiān lǐ fàng zhe kōngtiáo, diànshì hé bīngxiāng, fēicháng shūfu.", "uz": "Bor, xonada konditsioner, televizor va muzlatgich o'rnatilgan, juda qulay.", "ru": "Да, в номере есть кондиционер, телевизор и холодильник — очень комфортно.", "tj": "Ҳаст, дар хона кондитсионер, телевизор ва яхдон гузошта шудааст, хеле роҳат аст."},
                {"speaker": "B", "zh": "太好了！这里的环境会让人感觉很舒服！", "pinyin": "Tài hǎo le! Zhèlǐ de huánjìng huì ràng rén gǎnjué hěn shūfu!", "uz": "Juda yaxshi! Bu yerdagi muhit odamga juda qulay his-tuyg'u bag'ishlasa kerak!", "ru": "Замечательно! Обстановка здесь, наверное, делает человека расслабленным!", "tj": "Бисёр хуб! Муҳити ин ҷо ба одам ҳисси роҳатиро мебахшад!"},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "\"还是\"和\"或者\"的比较",
            "title_uz": "'还是' va '或者' farqi",
            "title_ru": "Сравнение 还是 и 或者",
            "title_tj": "Муқоисаи 还是 ва 或者",
            "rule_uz": (
                "Ikkalasi ham 'yoki' ma'nosini beradi, lekin qo'llanishi farqli:\n"
                "还是 — so'roq gaplarda: 你要A还是B？\n"
                "或者 — darak gaplarda: 你可以A或者B。\n"
                "Masalan:\n"
                "  你想喝茶还是果汁？(So'roq — choy yoki sharbat?)\n"
                "  你可以坐地铁或者打车。(Darak — metro yoki taksi.)"
            ),
            "rule_ru": (
                "Оба означают 'или', но употребляются по-разному:\n"
                "还是 — в вопросах: 你要A还是B？\n"
                "或者 — в утверждениях: 你可以A或者B。\n"
                "Например:\n"
                "  你想喝茶还是果汁？(Вопрос — чай или сок?)\n"
                "  你可以坐地铁或者打车。(Утверждение — на метро или такси.)"
            ),
            "rule_tj": (
                "Ҳарду маънои 'ё'-ро доранд, аммо истифодаашон фарқ мекунад:\n"
                "还是 — дар саволҳо: 你要A还是B？\n"
                "或者 — дар изҳор: 你可以A或者B。\n"
                "Масалан:\n"
                "  你想喝茶还是果汁？(Савол — чой ё шарбат?)\n"
                "  你可以坐地铁或者打车。(Изҳор — бо метро ё такси.)"
            ),
            "examples": [
                {"zh": "你想喝茶还是果汁？", "pinyin": "Nǐ xiǎng hē chá háishi guǒzhī?", "uz": "Choy ichmoqchimisiz yoki mevali sharbat?", "ru": "Ты хочешь чай или сок?", "tj": "Шумо чой мехоҳед ё шарбати мева?"},
                {"zh": "可以坐缆车或者走路上去。", "pinyin": "Kěyǐ zuò lǎnchē huòzhě zǒulù shàngqù.", "uz": "Kanatli aravacha bilan yoki piyoda chiqish mumkin.", "ru": "Можно подняться на фуникулёре или пешком.", "tj": "Метавонед бо канаткаш ё пиёда боло равед."},
            ]
        },
        {
            "no": 2,
            "title_zh": "存在句：处所+V着+数量+N",
            "title_uz": "Mavjudlik gapi: joy+V着+son+ot",
            "title_ru": "Предложение существования: место+V着+числ.+сущ.",
            "title_tj": "Ҷумлаи мавҷудият: ҷой+V着+шумор+исм",
            "rule_uz": (
                "Bu qolip biror joyda nima borligini tasvirlaydi.\n"
                "Qolip: Joy + V + 着 + son + ot\n"
                "着 — holatning davomiyligini bildiradi (qo'yilgan, turgan, osilib turgan).\n"
                "Masalan:\n"
                "  桌子上放着很多饮料。(Stol ustida ko'p ichimlik turadi.)\n"
                "  床上躺着一个人。(Ko'rpada bir kishi yotibdi.)\n"
                "  墙上挂着一幅画。(Devorga bir rasm osilgan.)"
            ),
            "rule_ru": (
                "Конструкция описывает наличие чего-либо в каком-то месте.\n"
                "Структура: Место + V + 着 + числит. + сущ.\n"
                "着 — состояние, в котором находится объект (лежит, висит, стоит).\n"
                "Например:\n"
                "  桌子上放着很多饮料。(На столе стоит много напитков.)\n"
                "  床上躺着一个人。(На кровати лежит человек.)\n"
                "  墙上挂着一幅画。(На стене висит картина.)"
            ),
            "rule_tj": (
                "Ин сохтор мавҷудияти чизеро дар ҷое тасвир мекунад.\n"
                "Сохтор: Ҷой + V + 着 + шумор + исм\n"
                "着 — ҳолати давомандаро нишон медиҳад (гузошта, хобида, овехта).\n"
                "Масалан:\n"
                "  桌子上放着很多饮料。(Рӯйи миз нӯшокиҳои зиёд гузошта шудааст.)\n"
                "  床上躺着一个人。(Рӯйи кат як одам хобида аст.)\n"
                "  墙上挂着一幅画。(Ба девор як расм овехта шудааст.)"
            ),
            "examples": [
                {"zh": "桌子上放着很多饮料，还有新鲜水果。", "pinyin": "Zhuōzi shàng fàng zhe hěn duō yǐnliào, hái yǒu xīnxiān shuǐguǒ.", "uz": "Stol ustida ko'p ichimlik va yangi mevalar turibdi.", "ru": "На столе стоит много напитков и свежих фруктов.", "tj": "Рӯйи миз нӯшокиҳои зиёд ва меваҳои тоза гузошта шудааст."},
                {"zh": "房间里放着空调、电视和冰箱。", "pinyin": "Fángjiān lǐ fàng zhe kōngtiáo, diànshì hé bīngxiāng.", "uz": "Xonada konditsioner, televizor va muzlatgich o'rnatilgan.", "ru": "В комнате есть кондиционер, телевизор и холодильник.", "tj": "Дар хона кондитсионер, телевизор ва яхдон гузошта шудааст."},
            ]
        },
        {
            "no": 3,
            "title_zh": "\"会\"表示可能性",
            "title_uz": "'会' ehtimol ma'nosida",
            "title_ru": "«会» в значении вероятности",
            "title_tj": "«会» дар маънои эҳтимол",
            "rule_uz": (
                "'会' so'zi ikki asosiy ma'noda ishlatiladi:\n"
                "1) Mahorat: V qila olaman (o'rganib olingan qobiliyat)\n"
                "   Masalan: 我会游泳。(Men suza olaman.)\n"
                "2) Ehtimol: ...bo'lsa kerak, ...bo'lishi mumkin\n"
                "   Masalan: 明天会下雨吧。(Ertaga yomg'ir yog'sa kerak.)\n"
                "Kontekst orqali qaysi ma'noda ekanligini bilsa bo'ladi."
            ),
            "rule_ru": (
                "Слово '会' имеет два основных значения:\n"
                "1) Умение: умею V (приобретённый навык)\n"
                "   Например: 我会游泳。(Я умею плавать.)\n"
                "2) Вероятность: наверное..., скорее всего...\n"
                "   Например: 明天会下雨吧。(Завтра, наверное, будет дождь.)\n"
                "Значение определяется по контексту."
            ),
            "rule_tj": (
                "Калимаи '会' ду маъноии асосӣ дорад:\n"
                "1) Тавонистан: V карда метавонам (малакаи омӯхтагӣ)\n"
                "   Масалан: 我会游泳。(Ман шино карда метавонам.)\n"
                "2) Эҳтимол: шояд..., эҳтимол...\n"
                "   Масалан: 明天会下雨吧。(Фардо шояд борон борад.)\n"
                "Маъно аз рӯи контекст муайян карда мешавад."
            ),
            "examples": [
                {"zh": "你会爬山吗？今天我们打算去爬山。", "pinyin": "Nǐ huì páshān ma? Jīntiān wǒmen dǎsuàn qù páshān.", "uz": "Tog' tirmasha olasizmi? Bugun tog'ga chiqmoqchi edik.", "ru": "Умеешь лазать в горы? Сегодня планируем сходить.", "tj": "Оё ба кӯҳ баромада метавонӣ? Имрӯз нақша дорем ба кӯҳ равем."},
                {"zh": "明天会下雨，记得带伞！", "pinyin": "Míngtiān huì xiàyǔ, jìde dài sǎn!", "uz": "Ertaga yomg'ir yog'sa kerak, soyabon olishni yodda tuting!", "ru": "Завтра, наверное, будет дождь — возьмите зонт!", "tj": "Фардо шояд борон борад, чатр гиред!"},
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
                {"prompt_uz": "ichimlik, sharbat", "prompt_ru": "напиток", "prompt_tj": "нӯшокӣ", "answer": "饮料", "pinyin": "yǐnliào"},
                {"prompt_uz": "yangi, toza (oziq-ovqat)", "prompt_ru": "свежий", "prompt_tj": "тоза, сабза", "answer": "新鲜", "pinyin": "xīnxiān"},
                {"prompt_uz": "qo'ymoq, joylashtirib qo'ymoq", "prompt_ru": "класть, ставить", "prompt_tj": "гузоштан, мондан", "answer": "放", "pinyin": "fàng"},
                {"prompt_uz": "ehtiyotkor bo'lmoq", "prompt_ru": "быть осторожным", "prompt_tj": "эҳтиёткор будан", "answer": "小心", "pinyin": "xiǎoxīn"},
                {"prompt_uz": "qulay, yoqimli", "prompt_ru": "удобный, комфортный", "prompt_tj": "роҳат, мувофиқ", "answer": "舒服", "pinyin": "shūfu"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (还是、或者、放着、会):",
            "instruction_ru": "Вставьте подходящее слово (还是、或者、放着、会):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (还是、或者、放着、会):",
            "items": [
                {"prompt_uz": "桌子上______很多饮料和水果。", "prompt_ru": "桌子上______很多饮料和水果。", "prompt_tj": "桌子上______很多饮料和水果。", "answer": "放着", "pinyin": "fàng zhe"},
                {"prompt_uz": "你想喝茶______咖啡？", "prompt_ru": "Ты хочешь чай ______кофе?", "prompt_tj": "Шумо чой мехоҳед ______қаҳва?", "answer": "还是", "pinyin": "háishi"},
                {"prompt_uz": "你可以坐地铁______打车去。", "prompt_ru": "Можешь поехать на метро ______такси.", "prompt_tj": "Метавонед бо метро ______такси равед.", "answer": "或者", "pinyin": "huòzhě"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "桌子上放着很多饮料，你想喝茶还是果汁？", "prompt_ru": "桌子上放着很多饮料，你想喝茶还是果汁？", "prompt_tj": "桌子上放着很多饮料，你想喝茶还是果汁？", "answer": "Stol ustida ko'p ichimlik bor, choy ichmoqchimisiz yoki mevali sharbat?", "pinyin": "Zhuōzi shàng fàng zhe hěn duō yǐnliào, nǐ xiǎng hē chá háishi guǒzhī?"},
                {"prompt_uz": "明天会下雨，记得带伞！", "prompt_ru": "明天会下雨，记得带伞！", "prompt_tj": "明天会下雨，记得带伞！", "answer": "Ertaga yomg'ir yog'sa kerak, soyabon olishni yodda tuting!", "pinyin": "Míngtiān huì xiàyǔ, jìde dài sǎn!"},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["饮料", "新鲜", "放", "小心", "舒服"]},
        {"no": 2, "answers": ["放着", "还是", "或者"]},
        {"no": 3, "answers": [
            "Stol ustida ko'p ichimlik bor, choy ichmoqchimisiz yoki mevali sharbat?",
            "Ertaga yomg'ir yog'sa kerak, soyabon olishni yodda tuting!",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "还是 va 或者 dan foydalanib 4 ta gap tuzing (ikkitasi so'roq, ikkitasi darak).",
            "instruction_ru": "Составьте 4 предложения с 还是 и 或者 (два вопросительных и два утвердительных).",
            "instruction_tj": "Бо 还是 ва 或者 4 ҷумла тартиб диҳед (ду саволӣ ва ду изҳорӣ).",
            "words": ["还是", "或者", "喝茶", "吃饭", "走路", "坐车"],
            "topic_uz": "Tanlov va imkoniyatlar",
            "topic_ru": "Выбор и возможности",
            "topic_tj": "Интихоб ва имкониятҳо",
        },
        {
            "no": 2,
            "instruction_uz": "Xonangizni tasvirlab, 放着 qolipini ishlatib 5-6 gap yozing.",
            "instruction_ru": "Опишите свою комнату, используя конструкцию 放着, 挂着 — 5–6 предложений.",
            "instruction_tj": "Утоқи худро тасвир кунед, сохторҳои 放着, 挂着-ро истифода баред — 5-6 ҷумла.",
            "topic_uz": "Mening xonam", "topic_ru": "Моя комната", "topic_tj": "Утоқи ман",
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
