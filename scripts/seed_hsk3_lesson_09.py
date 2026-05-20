import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 9,
    "lesson_code": "HSK3-L09",
    "title": json.dumps({"zh": "她的汉语说得跟中国人一样好", "uz": "Uning xitoycha gapirishi xitoyliklarnikidek yaxshi", "ru": "Она говорит по-китайски так же хорошо, как китайцы", "tj": "Вай ба монанди чиниҳо хуб чинӣ ҳарф мезанад"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "Taqqoslash iboralarini o'rganish: A xuddi B kabi, A B kadar emas", "ru": "Изучить сравнительные конструкции: A так же, как B; A не так, как B", "tj": "Омӯхтани ибораҳои муқоиса: A монанди B, A ба монанди B нест"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda '越A越B', 'A跟B一样+Adj' va 'A没有B那么+Adj' taqqoslash tuzilmalarini o'rganamiz.", "ru": "В этом уроке мы изучим сравнительные конструкции '越A越B', 'A跟B一样+Adj' и 'A没有B那么+Adj'.", "tj": "Дар ин дарс мо сохтори муқоисаи '越A越B', 'A跟B一样+Adj' ва 'A没有B那么+Adj'-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "普通话", "pinyin": "pǔtōnghuà", "pos": "n", "uz": "standart xitoy tili (mandarin)", "ru": "мандаринский (путунхуа)", "tj": "забони стандартии чинӣ"},
        {"no": 2, "zh": "口音", "pinyin": "kǒuyīn", "pos": "n", "uz": "talaffuz, lahja", "ru": "произношение, акцент", "tj": "талаффуз, лаҳҷа"},
        {"no": 3, "zh": "流利", "pinyin": "liúlì", "pos": "adj", "uz": "ravon, behalovat", "ru": "свободно, бегло", "tj": "равон, озодона"},
        {"no": 4, "zh": "标准", "pinyin": "biāozhǔn", "pos": "adj/n", "uz": "standart, me'yor", "ru": "стандарт, норма", "tj": "стандарт, меъёр"},
        {"no": 5, "zh": "地道", "pinyin": "dìdao", "pos": "adj", "uz": "haqiqiy, native", "ru": "настоящий, аутентичный", "tj": "воқеӣ, аслӣ"},
        {"no": 6, "zh": "词汇", "pinyin": "cíhuì", "pos": "n", "uz": "lug'at boyligi, so'z boyligi", "ru": "словарный запас", "tj": "луғатдон"},
        {"no": 7, "zh": "语法", "pinyin": "yǔfǎ", "pos": "n", "uz": "grammatika", "ru": "грамматика", "tj": "грамматика"},
        {"no": 8, "zh": "进步", "pinyin": "jìnbù", "pos": "n/v", "uz": "taraqqiyot; rivojlanmoq", "ru": "прогресс; прогрессировать", "tj": "пешрафт; пешрафт кардан"},
        {"no": 9, "zh": "努力", "pinyin": "nǔlì", "pos": "adj/v", "uz": "tirishqoq; harakat qilmoq", "ru": "усердный; стараться", "tj": "кӯшишкор; кӯшиш кардан"},
        {"no": 10, "zh": "坚持", "pinyin": "jiānchí", "pos": "v", "uz": "davom ettirmoq, qat'iy turib olmoq", "ru": "настаивать; продолжать", "tj": "идома додан, устувор мондан"},
        {"no": 11, "zh": "复杂", "pinyin": "fùzá", "pos": "adj", "uz": "murakkab", "ru": "сложный, запутанный", "tj": "мураккаб"},
        {"no": 12, "zh": "简单", "pinyin": "jiǎndān", "pos": "adj", "uz": "oddiy, sodda", "ru": "простой, лёгкий", "tj": "оддӣ, содда"},
        {"no": 13, "zh": "认真", "pinyin": "rènzhēn", "pos": "adj", "uz": "vijdonli, puxta", "ru": "серьёзный, добросовестный", "tj": "масъулиятшинос, ҷиддӣ"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Xitoy tili haqida suhbat", "ru": "Разговор о китайском языке", "tj": "Суҳбат дар бораи забони чинӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "你的普通话说得真流利！", "pinyin": "Nǐ de pǔtōnghuà shuō de zhēn liúlì!", "uz": "Sizning mandarin tiligizdagi gapirish juda ravon!", "ru": "Ты говоришь на путунхуа очень свободно!", "tj": "Шумо ба забони путунхуа хеле равон ҳарф мезанед!"},
                {"speaker": "B", "zh": "哪里，她的汉语说得跟中国人一样好。", "pinyin": "Nǎlǐ, tā de Hànyǔ shuō de gēn Zhōngguórén yīyàng hǎo.", "uz": "Nima deyaysiz, uning xitoycha gapirishi xitoyliklarnikidek yaxshi.", "ru": "Что вы, она говорит по-китайски так же хорошо, как китайцы.", "tj": "Чӣ мегӯед, вай ба монанди чиниҳо хуб чинӣ ҳарф мезанад."},
                {"speaker": "A", "zh": "真的吗？你学了多长时间汉语了？", "pinyin": "Zhēn de ma? Nǐ xué le duō cháng shíjiān Hànyǔ le?", "uz": "Chinmi? Siz qancha vaqt xitoy tili o'rgandingiz?", "ru": "Правда? Как долго ты учила китайский?", "tj": "Ростан? Шумо чанд вақт забони чинӣ омӯхтед?"},
                {"speaker": "B", "zh": "她学了三年，越学越觉得有意思。", "pinyin": "Tā xué le sān nián, yuè xué yuè juéde yǒu yìsi.", "uz": "U uch yil o'rgandi, o'rganган sari qiziqarliroq bo'lmoqda.", "ru": "Она учила три года, чем больше учишь, тем интереснее.", "tj": "Вай се сол омӯхт, ҳар чӣ бештар омӯзӣ, ҳамон қадар ҷолибтар мешавад."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Grammatika va lug'at", "ru": "Грамматика и словарный запас", "tj": "Грамматика ва луғатдон"},
            "dialogue": [
                {"speaker": "A", "zh": "汉语语法难不难？", "pinyin": "Hànyǔ yǔfǎ nán bu nán?", "uz": "Xitoy tili grammatikasi qiyinmi?", "ru": "Китайская грамматика сложная?", "tj": "Грамматикаи забони чинӣ душвор аст?"},
                {"speaker": "B", "zh": "汉语语法没有英语语法那么复杂。", "pinyin": "Hànyǔ yǔfǎ méiyǒu Yīngyǔ yǔfǎ nàme fùzá.", "uz": "Xitoy tili grammatikasi ingliz tili grammatikasi kadar murakkab emas.", "ru": "Китайская грамматика не такая сложная, как английская.", "tj": "Грамматикаи забони чинӣ ба монанди грамматикаи забони англисӣ мураккаб нест."},
                {"speaker": "A", "zh": "那词汇呢？", "pinyin": "Nà cíhuì ne?", "uz": "Xo'sh, lug'at boyligichi?", "ru": "А словарный запас?", "tj": "Луғатдон чӣ?"},
                {"speaker": "B", "zh": "词汇很多，但越学越简单，只要坚持！", "pinyin": "Cíhuì hěn duō, dàn yuè xué yuè jiǎndān, zhǐyào jiānchí!", "uz": "So'z boyligi ko'p, lekin o'rganган sari soddalashadi, faqat davom eting!", "ru": "Слов много, но чем больше учишь, тем проще, главное — не сдаваться!", "tj": "Луғат зиёд аст, аммо ҳар чӣ бештар омӯзӣ, содда мешавад, фақат давом диҳ!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Taqqoslash: ikki o'quvchi", "ru": "Сравнение двух студентов", "tj": "Муқоисаи ду донишҷӯ"},
            "dialogue": [
                {"speaker": "A", "zh": "你觉得他的汉语怎么样？", "pinyin": "Nǐ juéde tā de Hànyǔ zěnme yàng?", "uz": "Sizningcha, uning xitoy tili qanday?", "ru": "Как ты думаешь, как его китайский?", "tj": "Ба фикри шумо, забони чинии вай чӣ тавр аст?"},
                {"speaker": "B", "zh": "他的口音跟标准普通话一样标准。", "pinyin": "Tā de kǒuyīn gēn biāozhǔn pǔtōnghuà yīyàng biāozhǔn.", "uz": "Uning talaffuzi standart mandarin tili kabi standart.", "ru": "Его произношение такое же стандартное, как путунхуа.", "tj": "Талаффузи вай ба монанди путунхуаи стандартӣ аст."},
                {"speaker": "A", "zh": "但是他的进步没有她那么快。", "pinyin": "Dànshì tā de jìnbù méiyǒu tā nàme kuài.", "uz": "Lekin uning rivojlanishi u qiznikidek tez emas.", "ru": "Но его прогресс не такой быстрый, как у неё.", "tj": "Аммо пешрафти вай ба монанди ӯ тез нест."},
                {"speaker": "B", "zh": "是，她比他更认真，越努力越进步！", "pinyin": "Shì, tā bǐ tā gèng rènzhēn, yuè nǔlì yuè jìnbù!", "uz": "Ha, u undan ko'ra ko'proq mehnatkash, qanchalik harakat qilsang, shunchalik rivojlanasan!", "ru": "Да, она усерднее его, чем больше стараешься, тем быстрее прогресс!", "tj": "Ҳа, вай аз вай масъулиятшинос аст, ҳар чӣ бештар кӯшиш кунӣ, ҳамон қадар пешрафт мекунӣ!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "O'rganish maslahatlari", "ru": "Советы по обучению", "tj": "Тавсияҳо оид ба омӯзиш"},
            "dialogue": [
                {"speaker": "A", "zh": "你有什么学习汉语的好方法？", "pinyin": "Nǐ yǒu shénme xuéxí Hànyǔ de hǎo fāngfǎ?", "uz": "Xitoy tilini o'rganishning qanday yaxshi usullarini bilasiz?", "ru": "Есть ли у тебя хорошие методы изучения китайского?", "tj": "Оё усулҳои хуби омӯзиши забони чинӣ доред?"},
                {"speaker": "B", "zh": "每天都跟中国人练习，越练越地道！", "pinyin": "Měitiān dōu gēn Zhōngguórén liànxí, yuè liàn yuè dìdao!", "uz": "Har kuni xitoyliklar bilan mashq qiling, qanchalik mashq qilsangiz, shunchalik natural bo'ladi!", "ru": "Каждый день практикуйся с китайцами, чем больше практики, тем естественнее!", "tj": "Ҳар рӯз бо чиниҳо машқ кунед, ҳар чӣ бештар машқ кунӣ, ҳамон қадар табиӣтар мешавад!"},
                {"speaker": "A", "zh": "我的汉语没有你那么流利，怎么办？", "pinyin": "Wǒ de Hànyǔ méiyǒu nǐ nàme liúlì, zěnme bàn?", "uz": "Mening xitoyim siznikidek ravon emas, nima qilishim kerak?", "ru": "Мой китайский не такой свободный, как твой, что делать?", "tj": "Забони чинии ман ба монанди шумо равон нест, чӣ кор кунам?"},
                {"speaker": "B", "zh": "别担心，坚持学，越学越好！", "pinyin": "Bié dānxīn, jiānchí xué, yuè xué yuè hǎo!", "uz": "Xavotir olmang, davom eting, o'rganган sari yaxshilashadi!", "ru": "Не беспокойся, продолжай учить, чем больше учишь, тем лучше!", "tj": "Нигарон набошед, давом диҳед, ҳар чӣ бештар омӯзед, беҳтар мешавад!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "越A越B",
            "title_uz": "Qanchalik A bo'lsa, shunchalik B bo'ladi",
            "title_ru": "Чем больше A, тем больше B",
            "title_tj": "Ҳар чӣ бештар A, ҳамон қадар B",
            "rule_uz": "'越A越B' tuzilmasi ikki hodisaning bir vaqtda o'sishini bildiradi. A - shart, B - natija. Masalan: 越学越好 = o'rganган sari yaxshilashadi.",
            "rule_ru": "Конструкция '越A越B' выражает параллельное усиление двух явлений. A — условие, B — результат. Например: 越学越好 = чем больше учишь, тем лучше.",
            "rule_tj": "Сохтори '越A越B' афзоиши якҷояи ду ҳодисаро ифода мекунад. A — шарт, B — натиҷа. Масалан: 越学越好 = ҳар чӣ бештар омӯзӣ, беҳтар мешавад.",
            "examples": [
                {"zh": "她越学越觉得有意思。", "pinyin": "Tā yuè xué yuè juéde yǒu yìsi.", "uz": "U o'rganган sari qiziqarliroq deb hisoblaydi.", "ru": "Чем больше она учит, тем интереснее ей кажется.", "tj": "Ҳар чӣ бештар омӯзад, ҳамон қадар ҷолибтар ба назараш мерасад."},
                {"zh": "天气越来越冷了。", "pinyin": "Tiānqì yuè lái yuè lěng le.", "uz": "Havo tobora sovuqlashmoqda.", "ru": "Погода становится всё холоднее.", "tj": "Ҳаво рӯз ба рӯз сардтар мешавад."}
            ]
        },
        {
            "no": 2,
            "title_zh": "A跟B一样 + 形容词",
            "title_uz": "A xuddi B kabi + sifat",
            "title_ru": "A такой же, как B + прилагательное",
            "title_tj": "A монанди B + сифат",
            "rule_uz": "'A跟B一样+Adj' tuzilmasi A va B ning bir xil xususiyatga ega ekanini bildiradi. Inkor shaklida: 'A跟B不一样'. Sifat oldida 'ba'zan' 那么 qo'yiladi.",
            "rule_ru": "Конструкция 'A跟B一样+Adj' означает, что A и B имеют одинаковое свойство. Отрицательная форма: 'A跟B不一样'. Перед прилагательным иногда ставится 那么.",
            "rule_tj": "Сохтори 'A跟B一样+Adj' маъно медиҳад, ки A ва B хусусияти якхела доранд. Шакли манфӣ: 'A跟B不一样'. Пеш аз сифат гоҳо 那么 мегузорад.",
            "examples": [
                {"zh": "她的汉语说得跟中国人一样好。", "pinyin": "Tā de Hànyǔ shuō de gēn Zhōngguórén yīyàng hǎo.", "uz": "Uning xitoycha gapirishi xitoyliklarnikidek yaxshi.", "ru": "Она говорит по-китайски так же хорошо, как китайцы.", "tj": "Вай ба монанди чиниҳо хуб чинӣ ҳарф мезанад."},
                {"zh": "这个跟那个一样贵。", "pinyin": "Zhège gēn nàge yīyàng guì.", "uz": "Bu xuddi u kabi qimmat.", "ru": "Это такое же дорогое, как то.", "tj": "Ин монанди он қимат аст."}
            ]
        },
        {
            "no": 3,
            "title_zh": "A没有B那么 + 形容词",
            "title_uz": "A, B kadar + sifat emas",
            "title_ru": "A не такой, как B + прилагательное",
            "title_tj": "A ба монанди B + сифат нест",
            "rule_uz": "'A没有B那么+Adj' tuzilmasi A ning B darajasida emasligi yoki pastroq ekanini bildiradi. 'A不如B' bilan sinonim bo'lishi mumkin.",
            "rule_ru": "Конструкция 'A没有B那么+Adj' означает, что A не достигает степени B. Может быть синонимом 'A不如B'.",
            "rule_tj": "Сохтори 'A没有B那么+Adj' маъно медиҳад, ки A ба дараҷаи B нарасидааст. Бо 'A不如B' ҳаммаъно буда метавонад.",
            "examples": [
                {"zh": "他的进步没有她那么快。", "pinyin": "Tā de jìnbù méiyǒu tā nàme kuài.", "uz": "Uning rivojlanishi u qiznikidek tez emas.", "ru": "Его прогресс не такой быстрый, как у неё.", "tj": "Пешрафти вай ба монанди ӯ тез нест."},
                {"zh": "今天没有昨天那么冷。", "pinyin": "Jīntiān méiyǒu zuótiān nàme lěng.", "uz": "Bugun kecha kabi sovuq emas.", "ru": "Сегодня не так холодно, как вчера.", "tj": "Имрӯз ба монанди дирӯз сард нест."}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Uning xitoycha gapirishi xitoyliklarnikidek yaxshi.", "ru": "Она говорит по-китайски так же хорошо, как китайцы.", "tj": "Вай ба монанди чиниҳо хуб чинӣ ҳарф мезанад."},
                {"no": 2, "uz": "Uning rivojlanishi u qiznikidek tez emas.", "ru": "Его прогресс не такой быстрый, как у неё.", "tj": "Пешрафти вай ба монанди ӯ тез нест."},
                {"no": 3, "uz": "Havo tobora sovuqlashmoqda.", "ru": "Погода становится всё холоднее.", "tj": "Ҳаво рӯз ба рӯз сардтар мешавад."},
                {"no": 4, "uz": "Bu xuddi u kabi qimmat.", "ru": "Это такое же дорогое, как то.", "tj": "Ин монанди он қимат аст."},
                {"no": 5, "uz": "U o'rganган sari qiziqarliroq deb hisoblaydi.", "ru": "Чем больше она учит, тем интереснее ей.", "tj": "Ҳар чӣ бештар омӯзад, ҳамон қадар ҷолибтар ба назараш мерасад."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "她的汉语说得___中国人一样好。", "sentence_uz": "Uning xitoycha gapirishi xitoyliklarniki___ yaxshi.", "sentence_ru": "Она говорит ___ хорошо, как китайцы.", "sentence_tj": "Вай ба монанди чиниҳо ___ хуб чинӣ ҳарф мезанад.", "hint": "跟"},
                {"no": 2, "sentence_zh": "他的进步___有她那么快。", "sentence_uz": "Uning rivojlanishi u qiznikidek tez ___.", "sentence_ru": "Его прогресс ___ такой быстрый, как у неё.", "sentence_tj": "Пешрафти вай ба монанди ӯ тез ___.", "hint": "没"},
                {"no": 3, "sentence_zh": "越学___觉得有意思。", "sentence_uz": "O'rganган sari ___ qiziqarliroq bo'ladi.", "sentence_ru": "Чем больше учишь, ___ интереснее.", "sentence_tj": "Ҳар чӣ бештар омӯзед, ___ ҷолибтар мешавад.", "hint": "越"},
                {"no": 4, "sentence_zh": "今天没有昨天___冷。", "sentence_uz": "Bugun kecha kabi ___ sovuq emas.", "sentence_ru": "Сегодня не ___ холодно, как вчера.", "sentence_tj": "Имрӯз ба монанди дирӯз ___ сард нест.", "hint": "那么"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "他的口音跟标准普通话一样标准。", "pinyin": "Tā de kǒuyīn gēn biāozhǔn pǔtōnghuà yīyàng biāozhǔn."},
                {"no": 2, "zh": "越努力越进步，别放弃！", "pinyin": "Yuè nǔlì yuè jìnbù, bié fàngqì!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "她的汉语说得跟中国人一样好。"},
                {"no": 2, "zh": "他的进步没有她那么快。"},
                {"no": 3, "zh": "天气越来越冷了。"},
                {"no": 4, "zh": "这个跟那个一样贵。"},
                {"no": 5, "zh": "她越学越觉得有意思。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "跟"},
                {"no": 2, "answer": "没"},
                {"no": 3, "answer": "越"},
                {"no": 4, "answer": "那么"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Uning talaffuzi standart mandarin tili kabi standart.", "ru": "Его произношение такое же стандартное, как путунхуа.", "tj": "Талаффузи вай ба монанди путунхуаи стандартӣ аст."},
                {"no": 2, "uz": "Qanchalik harakat qilsang, shunchalik rivojlanasan, taslim bo'lma!", "ru": "Чем больше стараешься, тем больше прогресс, не сдавайся!", "tj": "Ҳар чӣ бештар кӯшиш кунӣ, ҳамон қадар пешрафт мекунӣ, таслим нашав!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'A跟B一样+Adj' va 'A没有B那么+Adj' tuzilmalaridan foydalanib, o'zingiz va do'stingizni taqqoslab 4 ta jumla yozing.", "ru": "Сравните себя и друга, написав 4 предложения с 'A跟B一样+Adj' и 'A没有B那么+Adj'.", "tj": "Бо истифода аз 'A跟B一样+Adj' ва 'A没有B那么+Adj' 4 ҷумла дар бораи муқоисаи худ ва дӯстатон нависед."},
        {"task_no": 2, "uz": "'越……越……' tuzilmasini ishlatib, o'rganish, ish yoki kundalik hayot haqida 3 ta jumla tuzing.", "ru": "Составьте 3 предложения с '越……越……' об учёбе, работе или повседневной жизни.", "tj": "3 ҷумла бо '越……越……' дар бораи таҳсил, кор ё ҳаёти ҳаррӯза тартиб диҳед."}
    ], ensure_ascii=False),
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
