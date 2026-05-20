import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 6,
    "lesson_code": "HSK2-L06",
    "title": "你怎么不吃了",
    "goal": json.dumps({"uz": "Sabab va oqibat haqida gapira olish, 怎么 so'roq olmoshi, miqdor ko'makchilarining takrorlanishi va 因为……所以…… bog'lovchi qolipini o'zlashtirish.", "ru": "Научиться говорить о причине и следствии, вопросительное местоимение 怎么, удвоение счётных слов и союзная конструкция 因为……所以……", "tj": "Омӯзиши гуфтан дар бораи сабаб ва натиҷа, исми саволии 怎么, такрори калимаҳои шуморавӣ ва сохтори пайвандакии 因为……所以……"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda kundalik suhbatlarda sabab va oqibatni tushuntirish o'rganiladi. Maktab, restoran, sport zali va idoradagi suhbatlar orqali so'roq qilish va izoh berish ko'nikmasi shakllanadi. Asosiy grammatik mavzular: 怎么 so'roq olmoshi, miqdor ko'makchilarining takrorlanishi va 因为……所以…… bog'lovchi qolipи.", "ru": "В этом уроке изучается объяснение причины и следствия в повседневных разговорах. Навыки спрашивания и объяснения формируются через диалоги в школе, ресторане, спортзале и офисе. Основные грамматические темы: вопросительное местоимение 怎么, удвоение счётных слов и союзная конструкция 因为……所以……", "tj": "Дар ин дарс шарҳ додани сабаб ва натиҷа дар муколамаҳои рӯзмарра омӯхта мешавад. Малакаҳои пурсидан ва шарҳ додан тавассути муколамаҳо дар мактаб, тарабхона, толори варзиш ва идора ташаккул меёбанд. Мавзӯҳои асосии грамматикӣ: исми саволии 怎么, такрори калимаҳои шуморавӣ ва сохтори пайвандакии 因为……所以……"}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "门",     "pinyin": "mén",       "pos": "n.",    "uz": "eshik, darvoza",                  "ru": "дверь, ворота",                    "tj": "дар, дарвоза"},
        {"no": 2,  "zh": "外",     "pinyin": "wài",       "pos": "n.",    "uz": "tashqarisi, tashqi tomon",        "ru": "снаружи, внешняя сторона",         "tj": "берун, тарафи берун"},
        {"no": 3,  "zh": "自行车", "pinyin": "zìxíngchē", "pos": "n.",    "uz": "velosiped",                       "ru": "велосипед",                        "tj": "велосипед"},
        {"no": 4,  "zh": "羊肉",   "pinyin": "yángròu",   "pos": "n.",    "uz": "qo'y go'shti",                   "ru": "баранина",                         "tj": "гӯшти гӯсфанд"},
        {"no": 5,  "zh": "好吃",   "pinyin": "hǎochī",    "pos": "adj.",  "uz": "mazali (ovqat haqida)",           "ru": "вкусный (о еде)",                  "tj": "хӯрданӣ, болаззат (дар бораи хӯрок)"},
        {"no": 6,  "zh": "面条",   "pinyin": "miàntiáo",  "pos": "n.",    "uz": "makaron, lag'mon",                "ru": "лапша",                            "tj": "лоғмон, макарон"},
        {"no": 7,  "zh": "打篮球", "pinyin": "dǎ lánqiú", "pos": "v.",    "uz": "basketbol o'ynamoq",              "ru": "играть в баскетбол",               "tj": "баскетбол бозӣ кардан"},
        {"no": 8,  "zh": "因为",   "pinyin": "yīnwèi",    "pos": "conj.", "uz": "chunki, sababi",                  "ru": "потому что, так как",              "tj": "зеро, чунки"},
        {"no": 9,  "zh": "所以",   "pinyin": "suǒyǐ",     "pos": "conj.", "uz": "shuning uchun, shunday qilib",   "ru": "поэтому, вот почему",              "tj": "аз ин сабаб, бинобар ин"},
        {"no": 10, "zh": "游泳",   "pinyin": "yóuyǒng",   "pos": "v.",    "uz": "suzmoq",                         "ru": "плавать",                          "tj": "шино кардан"},
        {"no": 11, "zh": "经常",   "pinyin": "jīngcháng", "pos": "adv.",  "uz": "tez-tez, ko'pincha",             "ru": "часто, постоянно",                 "tj": "зуд-зуд, аксар вақт"},
        {"no": 12, "zh": "公斤",   "pinyin": "gōngjīn",   "pos": "m.",    "uz": "kilogram",                       "ru": "килограмм",                        "tj": "килограмм"},
        {"no": 13, "zh": "姐姐",   "pinyin": "jiějie",    "pos": "n.",    "uz": "katta singl (aka-ukaniki), opa", "ru": "старшая сестра",                   "tj": "хоҳари калонӣ"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Maktabda",
            "scene_ru": "В школе",
            "scene_tj": "Дар мактаб",
            "dialogue": [
                {"speaker": "A", "zh": "你知道小王今天什么时候来学校吗？", "pinyin": "Nǐ zhīdào Xiǎo Wáng jīntiān shénme shíhou lái xuéxiào ma?", "uz": "Kichik Vang bugun qachon maktabga kelishini bilasanmi?", "ru": "Ты знаешь, когда Маленький Ван придёт в школу сегодня?", "tj": "Оё медонӣ, ки Сяо Ван имрӯз кай ба мактаб меояд?"},
                {"speaker": "B", "zh": "他已经来了。", "pinyin": "Tā yǐjīng lái le.", "uz": "U allaqachon keldi.", "ru": "Он уже пришёл.", "tj": "Вай аллакай омадааст."},
                {"speaker": "A", "zh": "你怎么知道他来了？", "pinyin": "Nǐ zěnme zhīdào tā lái le?", "uz": "U kelganini qanday bilding?", "ru": "Как ты узнал, что он пришёл?", "tj": "Ту чӣ тавр донистӣ, ки вай омад?"},
                {"speaker": "B", "zh": "我在门外看见他的自行车了。", "pinyin": "Wǒ zài mén wài kànjian tā de zìxíngchē le.", "uz": "Eshik tashqarisida uning velosipedini ko'rdim.", "ru": "Я увидел его велосипед за дверью.", "tj": "Ман берун аз дар велосипеди ӯро дидам."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Restoranda",
            "scene_ru": "В ресторане",
            "scene_tj": "Дар тарабхона",
            "dialogue": [
                {"speaker": "A", "zh": "今天的羊肉很好吃，你怎么不吃了？", "pinyin": "Jīntiān de yángròu hěn hǎochī, nǐ zěnme bù chī le?", "uz": "Bugungi qo'y go'shti juda mazali, nega yemayapsan?", "ru": "Сегодняшняя баранина очень вкусная, почему ты не ешь?", "tj": "Гӯшти гӯсфанди имрӯз бисёр болаззат аст, ту чаро намехӯрӣ?"},
                {"speaker": "B", "zh": "这个星期我天天都吃羊肉，不想吃了。", "pinyin": "Zhège xīngqī wǒ tiāntiān dōu chī yángròu, bù xiǎng chī le.", "uz": "Bu hafta har kuni qo'y go'shti edim, endi yeygim kelmayapti.", "ru": "На этой неделе я ел баранину каждый день, больше не хочу.", "tj": "Ин ҳафта ман ҳар рӯз гӯшти гӯсфанд хӯрдам, дигар намехоҳам."},
                {"speaker": "A", "zh": "那你想吃什么？", "pinyin": "Nà nǐ xiǎng chī shénme?", "uz": "Unda nima yemoqchisan?", "ru": "Тогда что ты хочешь поесть?", "tj": "Пас ту чӣ хӯрдан мехоҳӣ?"},
                {"speaker": "B", "zh": "来一点儿面条吧。", "pinyin": "Lái yìdiǎnr miàntiáo ba.", "uz": "Bir oz lag'mon gapirtiraylik.", "ru": "Давай закажем немного лапши.", "tj": "Каме лоғмон оварем."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Sport zalida",
            "scene_ru": "В спортзале",
            "scene_tj": "Дар толори варзиш",
            "dialogue": [
                {"speaker": "A", "zh": "昨天你们怎么都没去打篮球？", "pinyin": "Zuótiān nǐmen zěnme dōu méi qù dǎ lánqiú?", "uz": "Kecha nega barchang basketbol o'ynamaganga bormadinglar?", "ru": "Почему вы все вчера не пошли играть в баскетбол?", "tj": "Дирӯз шумо чаро ҳама наравон бозии баскетбол накардед?"},
                {"speaker": "B", "zh": "因为昨天下雨，所以我们都没去。我去游泳了。", "pinyin": "Yīnwèi zuótiān xiàyǔ, suǒyǐ wǒmen dōu méi qù. Wǒ qù yóuyǒng le.", "uz": "Chunki kecha yomg'ir yog'di, shuning uchun barchimiz bormadik. Men suzgani bordim.", "ru": "Потому что вчера шёл дождь, поэтому мы все не пошли. Я пошёл плавать.", "tj": "Зеро дирӯз борон меборид, аз ин сабаб мо ҳама наравон. Ман рафтам шино кардам."},
                {"speaker": "A", "zh": "你经常游泳吗？", "pinyin": "Nǐ jīngcháng yóuyǒng ma?", "uz": "Sen tez-tez suzasanmi?", "ru": "Ты часто плаваешь?", "tj": "Оё ту зуд-зуд шино мекунӣ?"},
                {"speaker": "B", "zh": "这个月我天天都游泳，我现在七十公斤了。", "pinyin": "Zhège yuè wǒ tiāntiān dōu yóuyǒng, wǒ xiànzài qīshí gōngjīn le.", "uz": "Bu oy har kuni suzaman, hozir yetmish kilogram bo'ldim.", "ru": "В этом месяце я плаваю каждый день, сейчас вешу семьдесят килограмм.", "tj": "Ин моҳ ман ҳар рӯз шино мекунам, ҳоло ҳафтод килограмм шудам."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Idorada",
            "scene_ru": "В офисе",
            "scene_tj": "Дар идора",
            "dialogue": [
                {"speaker": "A", "zh": "这两天怎么没看见小张？", "pinyin": "Zhè liǎng tiān zěnme méi kànjian Xiǎo Zhāng?", "uz": "Bu ikki kunda nega Kichik Jangni ko'rmadim?", "ru": "Почему я не видел Маленького Чжана эти два дня?", "tj": "Ин ду рӯз чаро Сяо Чжанро надидам?"},
                {"speaker": "B", "zh": "他去北京了。", "pinyin": "Tā qù Běijīng le.", "uz": "U Pekinga ketdi.", "ru": "Он уехал в Пекин.", "tj": "Вай ба Пекин рафтааст."},
                {"speaker": "A", "zh": "去北京了？是去旅游吗？", "pinyin": "Qù Běijīng le? Shì qù lǚyóu ma?", "uz": "Pekinga ketdimi? Sayohatgami?", "ru": "Уехал в Пекин? На экскурсию?", "tj": "Ба Пекин рафт? Сайёҳӣ?"},
                {"speaker": "B", "zh": "不是，听说是去看他姐姐。", "pinyin": "Bú shì, tīngshuō shì qù kàn tā jiějie.", "uz": "Yo'q, eshitdim, opasini ko'rgani ketgan.", "ru": "Нет, говорят, поехал навестить старшую сестру.", "tj": "Не, шунидам, рафтааст хоҳари калониашро бинад."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "疑问代词“怎么”",
            "title_uz": "So'roq olmoshi 怎么",
            "title_ru": "Вопросительное местоимение 怎么",
            "title_tj": "Исми саволии 怎么",
            "rule_uz": (
                "'怎么' so'roq olmoshi ikki xil ma'noda ishlatiladi:\n"
                "1) 'Qanday qilib? Qanday yo'l bilan?' — usul yoki harakat tarzini so'rashda;\n"
                "2) 'Nega? Nima uchun?' — hayrat yoki tushunmovchilik bildiruvchi savolda.\n"
                "Ikkinchi ma'noda ko'pincha salbiy gaplarda uchraydi."
            ),
            "rule_ru": (
                "Вопросительное местоимение '怎么' используется в двух значениях:\n"
                "1) 'Как? Каким образом?' — для вопроса о способе или методе действия;\n"
                "2) 'Почему? Как так?' — для выражения удивления или непонимания.\n"
                "Во втором значении часто встречается в отрицательных предложениях."
            ),
            "rule_tj": (
                "Исми саволии '怎么' дар ду маъно истифода мешавад:\n"
                "1) 'Чӣ тавр? Бо кадом роҳ?' — барои пурсидани усул ё тарзи амал;\n"
                "2) 'Чаро? Чи хел?' — барои ифодаи шигифт ё нофаҳмӣ.\n"
                "Дар маъноии дуввум аксар вақт дар ҷумлаҳои инкорӣ истифода мешавад."
            ),
            "examples": [
                {"zh": "你怎么知道他来了？", "pinyin": "Nǐ zěnme zhīdào tā lái le?", "uz": "U kelganini qanday bilding?", "ru": "Как ты узнал, что он пришёл?", "tj": "Ту чӣ тавр донистӣ, ки вай омад?"},
                {"zh": "你怎么不吃了？", "pinyin": "Nǐ zěnme bù chī le?", "uz": "Nega yemayapsan?", "ru": "Почему ты не ешь?", "tj": "Ту чаро намехӯрӣ?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "量词的重叠",
            "title_uz": "Miqdor ko'makchilarining takrorlanishi",
            "title_ru": "Удвоение счётных слов",
            "title_tj": "Такрори калимаҳои шуморавӣ",
            "rule_uz": (
                "Miqdor ko'makchilarini takrorlash orqali 'har bir, har qaysi' ma'nosi hosil qilinadi.\n"
                "Masalan, 天天 = har kuni, 年年 = har yili.\n"
                "Bu qolip davomiylik va takrorlanuvchilikni ta'kidlaydi."
            ),
            "rule_ru": (
                "Удвоение счётных слов образует значение 'каждый, любой'.\n"
                "Например, 天天 = каждый день, 年年 = каждый год.\n"
                "Эта конструкция подчёркивает постоянство и повторяемость."
            ),
            "rule_tj": (
                "Такрори калимаҳои шуморавӣ маъноии 'ҳар, ҳар як'-ро месозад.\n"
                "Масалан, 天天 = ҳар рӯз, 年年 = ҳар сол.\n"
                "Ин сохтор давомнокӣ ва такрорпазириро таъкид мекунад."
            ),
            "examples": [
                {"zh": "这个星期我天天都吃羊肉。", "pinyin": "Zhège xīngqī wǒ tiāntiān dōu chī yángròu.", "uz": "Bu hafta har kuni qo'y go'shti edim.", "ru": "На этой неделе я ел баранину каждый день.", "tj": "Ин ҳафта ман ҳар рӯз гӯшти гӯсфанд хӯрдам."},
                {"zh": "这个月我天天都游泳。", "pinyin": "Zhège yuè wǒ tiāntiān dōu yóuyǒng.", "uz": "Bu oy har kuni suzaman.", "ru": "В этом месяце я плаваю каждый день.", "tj": "Ин моҳ ман ҳар рӯз шино мекунам."},
            ]
        },
        {
            "no": 3,
            "title_zh": "关联词“因为……，所以……”",
            "title_uz": "Bog'lovchi 因为……所以…… (chunki...shuning uchun...)",
            "title_ru": "Союзная конструкция 因为……所以…… (потому что...поэтому...)",
            "title_tj": "Пайвандаки 因为……所以…… (зеро...аз ин сабаб...)",
            "rule_uz": (
                "'因为……所以……' qolipida sabab va oqibat ko'rsatiladi.\n"
                "因为 sabab gapini, 所以 esa oqibat gapini boshlab keladi.\n"
                "O'zbek tilidagi 'chunki…, shuning uchun…' iborasiga to'g'ri keladi.\n"
                "Ikkala qism ham birgalikda yoki alohida ishlatilishi mumkin."
            ),
            "rule_ru": (
                "Конструкция '因为……所以……' выражает причину и следствие.\n"
                "因为 вводит предложение с причиной, 所以 — со следствием.\n"
                "Соответствует русскому 'потому что…, поэтому…'.\n"
                "Обе части могут использоваться вместе или по отдельности."
            ),
            "rule_tj": (
                "Дар сохтори '因为……所以……' сабаб ва натиҷа нишон дода мешавад.\n"
                "因为 ҷумлаи сабабро, 所以 ҷумлаи натиҷаро мебарад.\n"
                "Ба форсии тоҷикӣ 'зеро…, аз ин сабаб…' мувофиқат мекунад.\n"
                "Ҳар ду қисм метавонанд якҷоя ё алоҳида истифода шаванд."
            ),
            "examples": [
                {"zh": "因为昨天下雨，所以我们都没去。", "pinyin": "Yīnwèi zuótiān xiàyǔ, suǒyǐ wǒmen dōu méi qù.", "uz": "Chunki kecha yomg'ir yog'di, shuning uchun barchimiz bormadik.", "ru": "Потому что вчера шёл дождь, поэтому мы все не пошли.", "tj": "Зеро дирӯз борон меборид, аз ин сабаб мо ҳама наравон."},
                {"zh": "因为他很忙，所以没来。", "pinyin": "Yīnwèi tā hěn máng, suǒyǐ méi lái.", "uz": "Chunki u juda band edi, shuning uchun kelmadi.", "ru": "Потому что он был очень занят, поэтому не пришёл.", "tj": "Зеро вай бисёр машғул буд, аз ин сабаб наомад."},
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
                {"prompt_uz": "velosiped", "prompt_ru": "велосипед", "prompt_tj": "велосипед", "answer": "自行车", "pinyin": "zìxíngchē"},
                {"prompt_uz": "qo'y go'shti", "prompt_ru": "баранина", "prompt_tj": "гӯшти гӯсфанд", "answer": "羊肉", "pinyin": "yángròu"},
                {"prompt_uz": "suzmoq", "prompt_ru": "плавать", "prompt_tj": "шино кардан", "answer": "游泳", "pinyin": "yóuyǒng"},
                {"prompt_uz": "tez-tez", "prompt_ru": "часто", "prompt_tj": "зуд-зуд", "answer": "经常", "pinyin": "jīngcháng"},
                {"prompt_uz": "opa", "prompt_ru": "старшая сестра", "prompt_tj": "хоҳари калонӣ", "answer": "姐姐", "pinyin": "jiějie"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (因为、所以、怎么、天天、经常):",
            "instruction_ru": "Вставьте подходящее слово (因为、所以、怎么、天天、经常):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (因为、所以、怎么、天天、经常):",
            "items": [
                {"prompt_uz": "______昨天下雨，______我们都没去。", "prompt_ru": "______昨天下雨，______我们都没去。", "prompt_tj": "______昨天下雨，______我们都没去。", "answer": "因为 / 所以", "pinyin": "yīnwèi / suǒyǐ"},
                {"prompt_uz": "你______不吃了？", "prompt_ru": "你______不吃了？", "prompt_tj": "你______不吃了？", "answer": "怎么", "pinyin": "zěnme"},
                {"prompt_uz": "这个月我______都游泳。", "prompt_ru": "这个月我______都游泳。", "prompt_tj": "这个月我______都游泳。", "answer": "天天", "pinyin": "tiāntiān"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "因为昨天下雨，所以我们都没去打篮球。", "prompt_ru": "因为昨天下雨，所以我们都没去打篮球。", "prompt_tj": "因为昨天下雨，所以我们都没去打篮球。", "answer": "Chunki kecha yomg'ir yog'di, shuning uchun barchimiz basketbol o'ynamaganga bormadik.", "pinyin": "Yīnwèi zuótiān xiàyǔ, suǒyǐ wǒmen dōu méi qù dǎ lánqiú."},
                {"prompt_uz": "这个星期我天天都吃羊肉，不想吃了。", "prompt_ru": "这个星期我天天都吃羊肉，不想吃了。", "prompt_tj": "这个星期我天天都吃羊肉，不想吃了。", "answer": "Bu hafta har kuni qo'y go'shti edim, endi yeygim kelmayapti.", "pinyin": "Zhège xīngqī wǒ tiāntiān dōu chī yángròu, bù xiǎng chī le."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["自行车", "羊肉", "游泳", "经常", "姐姐"]},
        {"no": 2, "answers": ["因为 / 所以", "怎么", "天天"]},
        {"no": 3, "answers": [
            "Chunki kecha yomg'ir yog'di, shuning uchun barchimiz basketbol o'ynamaganga bormadik.",
            "Bu hafta har kuni qo'y go'shti edim, endi yeygim kelmayapti.",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'因为……所以……' qolipidan foydalanib 4 ta gap tuzing. Kundalik hayotingizdan sabab va oqibat keltiring.",
            "instruction_ru": "Составьте 4 предложения, используя конструкцию '因为……所以……'. Приведите причины и следствия из повседневной жизни.",
            "instruction_tj": "Бо истифода аз сохтори '因为……所以……' 4 ҷумла тартиб диҳед. Аз ҳаёти рӯзмарраи худ сабаб ва натиҷа овардед.",
            "words": ["因为", "所以", "下雨", "忙", "累", "没去"],
            "example": "因为今天很忙，所以我没有时间休息。",
        },
        {
            "no": 2,
            "instruction_uz": "Sevimli ovqatingiz haqida 5-6 gapdan iborat kichik matn yozing. 天天, 经常, 怎么 so'zlarini ishlating.",
            "instruction_ru": "Напишите небольшой текст из 5–6 предложений о вашей любимой еде. Используйте слова 天天, 经常, 怎么.",
            "instruction_tj": "Дар бораи хӯроки дӯстдоштаи худ матни хурде аз 5-6 ҷумла нависед. Калимаҳои 天天, 经常, 怎么-ро истифода баред.",
            "topic_uz": "Мening sevimli ovqatim",
            "topic_ru": "Моя любимая еда",
            "topic_tj": "Хӯроки дӯстдоштаи ман",
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
