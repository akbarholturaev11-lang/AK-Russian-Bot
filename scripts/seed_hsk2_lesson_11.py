import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 11,
    "lesson_code": "HSK2-L11",
    "title": "他比我大三岁",
    "goal": json.dumps({"uz": "'Bǐ' qiyoslash konstruktsiyasini, fe'l sifatdoshini aniqlovchi sifatida ishlatishni va 'kěnéng' yordamchi fe'lini o'rganish.", "ru": "Изучение конструкции сравнения 'bǐ', использования глагольных конструкций в роли определения и модального глагола 'kěnéng'.", "tj": "Омӯзиши конструксияи муқоисавии 'bǐ', истифодаи сохторҳои феълӣ ҳамчун муайянкунанда ва феъли ёрирасони 'kěnéng'."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda biz odamlarni va narsalarni qiyoslashni o'rganamiz. Raqs, bozor va maktab muhitidagi suhbatlar orqali 'bǐ' (dan ko'proq/katta/yaxshi) konstruktsiyasini mashq qilamiz. Shuningdek, fe'l birikmalarini aniqlovchi sifatida ishlatishni va ehtimolni bildiruvchi 'kěnéng' so'zini o'zlashtiramiz.", "ru": "На этом уроке мы учимся сравнивать людей и предметы. Отрабатываем конструкцию 'bǐ' (больше/старше/лучше, чем) через диалоги в кафе, магазине и школе. Также усваиваем использование глагольных конструкций в роли определения и слово 'kěnéng', выражающее вероятность.", "tj": "Дар ин дарс мо ёд мегирем одамон ва чизҳоро муқоиса кунем. Конструксияи 'bǐ' (аз… бештар/калонтар/беҳтар)-ро тавассути муколамаҳо дар кафе, бозор ва мактаб машқ мекунем. Инчунин истифодаи сохторҳои феълиро ҳамчун муайянкунанда ва калимаи 'kěnéng'-и ифодакунандаи эҳтимолро аз бар мекунем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "唱歌", "pinyin": "chànggē", "pos": "v.", "uz": "qo'shiq aytmoq", "ru": "петь песню", "tj": "суруд хондан"},
        {"no": 2, "zh": "男", "pinyin": "nán", "pos": "adj.", "uz": "erkak, o'g'il", "ru": "мужской, мальчик", "tj": "мард, писар"},
        {"no": 3, "zh": "女", "pinyin": "nǚ", "pos": "adj.", "uz": "ayol, qiz", "ru": "женский, девочка", "tj": "зан, духтар"},
        {"no": 4, "zh": "孩子", "pinyin": "háizi", "pos": "n.", "uz": "bola", "ru": "ребёнок", "tj": "кӯдак"},
        {"no": 5, "zh": "右边", "pinyin": "yòubian", "pos": "n.", "uz": "o'ng tomon", "ru": "правая сторона", "tj": "тарафи рост"},
        {"no": 6, "zh": "比", "pinyin": "bǐ", "pos": "prep.", "uz": "… dan (qiyoslash uchun)", "ru": "чем… (для сравнения)", "tj": "аз… (барои муқоиса)"},
        {"no": 7, "zh": "便宜", "pinyin": "piányi", "pos": "adj.", "uz": "arzon", "ru": "дешёвый", "tj": "арзон"},
        {"no": 8, "zh": "说话", "pinyin": "shuōhuà", "pos": "v.", "uz": "gapirmoq, so'zlamoq", "ru": "говорить, разговаривать", "tj": "гап задан, сухан гуфтан"},
        {"no": 9, "zh": "可能", "pinyin": "kěnéng", "pos": "aux.", "uz": "ehtimol, mumkin", "ru": "возможно, может быть", "tj": "эҳтимол, мумкин аст"},
        {"no": 10, "zh": "去年", "pinyin": "qùnián", "pos": "n.", "uz": "o'tgan yil", "ru": "в прошлом году", "tj": "соли гузашта"},
        {"no": 11, "zh": "姓", "pinyin": "xìng", "pos": "v.", "uz": "familiyasi … bo'lmoq", "ru": "иметь фамилию…", "tj": "насабаш … буданаш"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Qo'shiq aytish zalida",
            "scene_ru": "В зале для пения",
            "scene_tj": "Дар толори сурудхонӣ",
            "dialogue": [
                {"speaker": "A", "zh": "王方，昨天和你一起唱歌的人是谁？", "pinyin": "Wáng Fāng, zuótiān hé nǐ yìqǐ chànggē de rén shì shéi?", "uz": "Van Fan, kecha siz bilan birga qo'shiq aytgan odam kim edi?", "ru": "Ван Фан, кто это был вчера, когда ты пел(а) вместе с тобой?", "tj": "Ван Фан, дирӯз он касе ки бо ту якҷоя суруд мехонд кӣ буд?"},
                {"speaker": "B", "zh": "一个朋友。", "pinyin": "Yí ge péngyou.", "uz": "Bir do'stim.", "ru": "Один друг.", "tj": "Як дӯстам."},
                {"speaker": "A", "zh": "什么朋友？是不是男朋友？", "pinyin": "Shénme péngyou? Shì bú shì nán péngyou?", "uz": "Qanday do'st? Yigit do'stingizmi?", "ru": "Что за друг? Это случайно не парень?", "tj": "Чӣ гуна дӯст? Магар дӯсти писарат аст?"},
                {"speaker": "B", "zh": "不是不是，我同学介绍的，昨天第一次见。", "pinyin": "Bú shì bú shì, wǒ tóngxué jièshào de, zuótiān dì yī cì jiàn.", "uz": "Yo'q yo'q, sinfdoshim tanishtirgan, kecha birinchi marta uchrashdik.", "ru": "Нет-нет, познакомил однокурсник, вчера виделись первый раз.", "tj": "Не не, ҳамсинфам шинос кард, дирӯз бори аввал дидем."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Yotoqxonada",
            "scene_ru": "В общежитии",
            "scene_tj": "Дар хобгоҳ",
            "dialogue": [
                {"speaker": "A", "zh": "左边这个看报纸的女孩子是你姐姐吗？", "pinyin": "Zuǒbian zhège kàn bàozhǐ de nǚ háizi shì nǐ jiějie ma?", "uz": "Chap tomondagi gazeta o'qiyotgan qiz sizning opangizmi?", "ru": "Та девушка слева, которая читает газету, это твоя старшая сестра?", "tj": "Он духтаре ки тарафи чап рӯзнома мехонад хоҳари калонии туст?"},
                {"speaker": "B", "zh": "是，右边写字的那个人是我哥哥。", "pinyin": "Shì, yòubian xiě zì de nà ge rén shì wǒ gēge.", "uz": "Ha, o'ng tomonda yozayotgan odam mening akam.", "ru": "Да, а тот, кто справа пишет, это мой старший брат.", "tj": "Бале, он касе ки тарафи рост менависад бародари калонии ман аст."},
                {"speaker": "A", "zh": "你哥哥多大？", "pinyin": "Nǐ gēge duō dà?", "uz": "Akangiz necha yoshda?", "ru": "Сколько лет твоему брату?", "tj": "Бародари калониат чанд сол дорад?"},
                {"speaker": "B", "zh": "25岁，他比我大三岁。", "pinyin": "Èrshíwǔ suì, tā bǐ wǒ dà sān suì.", "uz": "25 yoshda, u mendan uch yosh katta.", "ru": "25 лет, он старше меня на три года.", "tj": "25 сол, ӯ аз ман се сол калонтар аст."}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Do'konda",
            "scene_ru": "В магазине",
            "scene_tj": "Дар мағоза",
            "dialogue": [
                {"speaker": "A", "zh": "今天的西瓜怎么卖？", "pinyin": "Jīntiān de xīguā zěnme mài?", "uz": "Bugungi tarvuz qancha?", "ru": "Сколько стоит сегодня арбуз?", "tj": "Тарбузи имрӯза чанд пул аст?"},
                {"speaker": "B", "zh": "三块五一斤。", "pinyin": "Sān kuài wǔ yì jīn.", "uz": "Bir jin uchun uch yuan besh fen.", "ru": "Три юаня пятьдесят за полкило.", "tj": "Барои як ҷин се юан панҷ феник."},
                {"speaker": "A", "zh": "比昨天便宜。", "pinyin": "Bǐ zuótiān piányi.", "uz": "Kechaga qaraganda arzon.", "ru": "Дешевле, чем вчера.", "tj": "Аз дирӯз арзонтар аст."},
                {"speaker": "B", "zh": "是，苹果也比昨天便宜一些。您来点儿吧。", "pinyin": "Shì, píngguǒ yě bǐ zuótiān piányi yìxiē. Nín lái diǎnr ba.", "uz": "Ha, olma ham kechaga qaraganda biroz arzon. Biroz oling.", "ru": "Да, яблоки тоже немного дешевле, чем вчера. Берите немного.", "tj": "Бале, себ ҳам аз дирӯз каме арзонтар аст. Каме гиред."}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Maktabda",
            "scene_ru": "В школе",
            "scene_tj": "Дар мактаб",
            "dialogue": [
                {"speaker": "A", "zh": "前边说话的那个人是不是我的汉语老师？你可能不认识她。", "pinyin": "Qiánbian shuōhuà de nà ge rén shì bú shì wǒ de Hànyǔ lǎoshī? Nǐ kěnéng bù rènshi tā.", "uz": "Oldinda gapirgan odam mening xitoy tili o'qituvchim emasmi? Siz uni tanimas ehtimol.", "ru": "Тот человек впереди, который говорит, не мой ли преподаватель китайского? Ты, наверное, её не знаешь.", "tj": "Оё он касе ки пеш гап мезанад муаллими забони чинии ман нест? Эҳтимол шумо ӯро намешиносед."},
                {"speaker": "B", "zh": "是新来的汉语老师吗？", "pinyin": "Shì xīn lái de Hànyǔ lǎoshī ma?", "uz": "Yangi kelgan xitoy tili o'qituvchisimi?", "ru": "Это новый преподаватель китайского?", "tj": "Оё ин муаллими нави забони чинӣ аст?"},
                {"speaker": "A", "zh": "是去年来的，她姓王，28岁。", "pinyin": "Shì qùnián lái de, tā xìng Wáng, èrshíbā suì.", "uz": "O'tgan yil kelgan, familiyasi Van, 28 yoshda.", "ru": "Пришла в прошлом году, её фамилия Ван, 28 лет.", "tj": "Соли гузашта омад, насабаш Ван аст, 28 сол дорад."},
                {"speaker": "B", "zh": "她比我们老师小两岁。", "pinyin": "Tā bǐ wǒmen lǎoshī xiǎo liǎng suì.", "uz": "U bizning o'qituvchimizdan ikki yosh kichik.", "ru": "Она на два года моложе нашего учителя.", "tj": "Ӯ аз муаллими мо ду сол хурдтар аст."}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "动词结构做定语",
            "title_uz": "Fe'l birikmasi aniqlovchi sifatida",
            "title_ru": "Глагольная конструкция в роли определения",
            "title_tj": "Сохтори феълӣ ҳамчун муайянкунанда",
            "rule_uz": "Xitoy tilida fe'l birikmasi yoki gap bo'lagi ot oldidan aniqlovchi bo'lib kelishi mumkin. Bu holda aniqlovchi bilan ot orasiga '的' yuklamasi qo'yiladi. Masalan: '看报纸的女孩子' (gazeta o'qiyotgan qiz).",
            "rule_ru": "В китайском языке глагольная конструкция или часть предложения может выступать определением перед существительным. В этом случае между определением и существительным ставится частица '的'. Например: '看报纸的女孩子' (девушка, читающая газету).",
            "rule_tj": "Дар забони чинӣ сохтори феълӣ ё бахши ҷумла метавонад пеш аз исм ҳамчун муайянкунанда бояд. Дар ин ҳол байни муайянкунанда ва исм зарраи '的' гузошта мешавад. Масалан: '看报纸的女孩子' (духтаре ки рӯзнома мехонад).",
            "examples": [
                {"zh": "左边看报纸的女孩子是我姐姐。", "pinyin": "Zuǒbian kàn bàozhǐ de nǚ háizi shì wǒ jiějie.", "uz": "Chap tomondagi gazeta o'qiyotgan qiz mening opam.", "ru": "Девушка слева, читающая газету, — моя старшая сестра.", "tj": "Духтаре ки тарафи чап рӯзнома мехонад хоҳари калонии ман аст."},
                {"zh": "前边说话的那个人是老师。", "pinyin": "Qiánbian shuōhuà de nà ge rén shì lǎoshī.", "uz": "Oldinda gapirgan odam o'qituvchi.", "ru": "Тот человек впереди, который говорит, — учитель.", "tj": "Он касе ки пеш гап мезанад муаллим аст."}
            ]
        },
        {
            "no": 2,
            "title_zh": "“比”字句（1）",
            "title_uz": "'Bǐ' qiyoslash gapi (1)",
            "title_ru": "Предложения сравнения с 'bǐ' (1)",
            "title_tj": "Ҷумлаи муқоисавӣ бо 'bǐ' (1)",
            "rule_uz": "'Bǐ' qiyoslash gapi quyidagi tuzilishga ega: A + 比 + B + sifat (+ miqdor farqi). Bu 'A, B dan ko'proq/katta/yaxshi' ma'nosini beradi. Inkor shaklida '没有' ishlatiladi: A + 没有 + B + sifat.",
            "rule_ru": "Конструкция сравнения с 'bǐ' имеет структуру: A + 比 + B + прилагательное (+ разница в количестве). Означает 'A больше/старше/лучше, чем B'. В отрицательной форме используется '没有': A + 没有 + B + прилагательное.",
            "rule_tj": "Ҷумлаи муқоисавӣ бо 'bǐ' сохтори зеринро дорад: A + 比 + B + сифат (+ фарқи миқдорӣ). Маъниаш 'A аз B бештар/калонтар/беҳтар аст'. Дар шакли инкорӣ '没有' истифода мешавад: A + 没有 + B + сифат.",
            "examples": [
                {"zh": "他比我大三岁。", "pinyin": "Tā bǐ wǒ dà sān suì.", "uz": "U mendan uch yosh katta.", "ru": "Он старше меня на три года.", "tj": "Ӯ аз ман се сол калонтар аст."},
                {"zh": "苹果没有西瓜大。", "pinyin": "Píngguǒ méiyǒu xīguā dà.", "uz": "Olma tarvuz kadar katta emas.", "ru": "Яблоко не такое большое, как арбуз.", "tj": "Себ ба андозаи тарбуз калон нест."}
            ]
        },
        {
            "no": 3,
            "title_zh": "助动词“可能”",
            "title_uz": "'Kěnéng' yordamchi fe'li",
            "title_ru": "Модальный глагол 'kěnéng'",
            "title_tj": "Феъли ёрирасони 'kěnéng'",
            "rule_uz": "'Kěnéng' yordamchi fe'li 'ehtimol, mumkin' ma'nosini beradi va fe'l oldidan qo'yiladi. U ma'lum bo'lmagan holatlar haqida taxmin bildiradi. Inkor shakli: '不可能' (mumkin emas, aslo).",
            "rule_ru": "Модальный глагол 'kěnéng' означает 'возможно, может быть' и ставится перед глаголом. Выражает предположение о неизвестных ситуациях. Отрицательная форма: '不可能' (невозможно).",
            "rule_tj": "Феъли ёрирасони 'kěnéng' маъниаш 'эҳтимол, мумкин аст' буда пеш аз феъл меояд. Вай тахминро дар бораи вазъиятҳои номаълум ифода мекунад. Шакли инкорӣ: '不可能' (ғайриимкон аст).",
            "examples": [
                {"zh": "你可能不认识她。", "pinyin": "Nǐ kěnéng bù rènshi tā.", "uz": "Siz uni tanimas ehtimol.", "ru": "Возможно, ты её не знаешь.", "tj": "Эҳтимол шумо ӯро намешиносед."},
                {"zh": "他可能今天来。", "pinyin": "Tā kěnéng jīntiān lái.", "uz": "U ehtimol bugun keladi.", "ru": "Возможно, он придёт сегодня.", "tj": "Эҳтимол ӯ имрӯз меояд."}
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
                {"prompt_uz": "qo'shiq aytmoq", "prompt_ru": "петь песню", "prompt_tj": "суруд хондан", "answer": "唱歌", "pinyin": "chànggē"},
                {"prompt_uz": "arzon", "prompt_ru": "дешёвый", "prompt_tj": "арзон", "answer": "便宜", "pinyin": "piányi"},
                {"prompt_uz": "ehtimol", "prompt_ru": "возможно", "prompt_tj": "эҳтимол", "answer": "可能", "pinyin": "kěnéng"},
                {"prompt_uz": "o'tgan yil", "prompt_ru": "в прошлом году", "prompt_tj": "соли гузашта", "answer": "去年", "pinyin": "qùnián"},
                {"prompt_uz": "o'ng tomon", "prompt_ru": "правая сторона", "prompt_tj": "тарафи рост", "answer": "右边", "pinyin": "yòubian"}
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "Yashil olma ___qizil olmadan arzon. (比)", "prompt_ru": "Зелёное яблоко ___ дешевле красного. (比)", "prompt_tj": "Себи сабз ___ аз себи сурх арзонтар аст. (比)", "answer": "比", "pinyin": "bǐ"},
                {"prompt_uz": "Opa mendan ___ yosh katta. (三)", "prompt_ru": "Сестра старше меня на ___ года. (三)", "prompt_tj": "Хоҳар аз ман ___ сол калонтар аст. (三)", "answer": "三", "pinyin": "sān"},
                {"prompt_uz": "U ___ bugun kelmaydi. (可能)", "prompt_ru": "Он ___ сегодня не придёт. (可能)", "prompt_tj": "Ӯ ___ имрӯз намеояд. (可能)", "answer": "可能", "pinyin": "kěnéng"},
                {"prompt_uz": "Oldinda gap___yotgan odam o'qituvchi. (话)", "prompt_ru": "Тот человек впереди, который раз___, — учитель. (话)", "prompt_tj": "Он касе ки пеш гап ___ мезанад муаллим аст. (话)", "answer": "话", "pinyin": "huà"}
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "他比我大三岁。", "prompt_ru": "他比我大三岁。", "prompt_tj": "他比我大三岁。", "answer": "U mendan uch yosh katta.", "pinyin": "Tā bǐ wǒ dà sān suì."},
                {"prompt_uz": "前边说话的那个人是不是我的汉语老师？你可能不认识她。", "prompt_ru": "前边说话的那个人是不是我的汉语老师？你可能不认识她。", "prompt_tj": "前边说话的那个人是不是我的汉语老师？你可能不认识她。", "answer": "Oldinda gapirgan odam mening xitoy tili o'qituvchim emasmi? Siz uni tanimas ehtimol.", "pinyin": "Qiánbian shuōhuà de nà ge rén shì bú shì wǒ de Hànyǔ lǎoshī? Nǐ kěnéng bù rènshi tā."},
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["唱歌", "便宜", "可能", "去年", "右边"]},
        {"no": 2, "answers": ["比", "三", "可能", "话"]},
        {"no": 3, "answers": [
            "U mendan uch yosh katta.",
            "Oldinda gapirgan odam mening xitoy tili o'qituvchim emasmi? Siz uni tanimas ehtimol.",
        ]}
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'Bǐ' dan foydalanib o'zingizni oila a'zolaringiz bilan qiyoslang (yosh, bo'y, ovqat ishtahasi va h.k.). Kamida 4 jumla yozing.",
            "instruction_ru": "Используя 'bǐ', сравните себя с членами своей семьи (возраст, рост, аппетит и т.д.). Напишите не менее 4 предложений.",
            "instruction_tj": "Бо истифодаи 'bǐ' худро бо аъзоёни оилаатон муқоиса кунед (синну сол, қад, иштиҳо ва ғ.). Камаш 4 ҷумла нависед.",
            "words": ["比", "没有"],
            "example": "我比哥哥小两岁。",
            "topic_uz": "Oila a'zolari bilan qiyoslash",
            "topic_ru": "Сравнение с членами семьи",
            "topic_tj": "Муқоиса бо аъзоёни оила"
        },
        {
            "no": 2,
            "instruction_uz": "Kecha ko'rgan yoki eshitgan biror voqeani yozing va '可能' so'zidan kamida bir marta foydalaning.",
            "instruction_ru": "Напишите о каком-нибудь событии, которое вы видели или слышали вчера, и используйте '可能' хотя бы один раз.",
            "instruction_tj": "Дар бораи ягон воқеае ки дирӯз дидед ё шунидед нависед ва '可能'-ро камаш як маротиба истифода баред.",
            "words": ["可能"],
            "example": "昨天我可能看见了我的同学。",
            "topic_uz": "Kecha bo'lgan voqea",
            "topic_ru": "Вчерашнее событие",
            "topic_tj": "Воқеаи дирӯза"
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
