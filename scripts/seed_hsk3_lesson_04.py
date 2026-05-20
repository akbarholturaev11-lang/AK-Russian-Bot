import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk3",
    "lesson_order": 4,
    "lesson_code": "HSK3-L04",
    "title": "她总是笑着跟客人说话",
    "goal": json.dumps({"uz": "'又……又……', V₁着+V₂ hamroh harakat qolipini va '总是' ravishi bilan doim takrorlanadigan harakatlarni o'zlashtirish.", "ru": "Освоить конструкцию 又……又……, сопутствующее действие V₁着+V₂ и привычные действия с наречием 总是.", "tj": "Азхудкунии сохтори 又……又……, амали ҳамроҳ V₁着+V₂ ва амалҳои одатии бо қайди 总是."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda bir vaqtning o'zida ikki sifatga ega bo'lish, bir harakat davomida ikkinchi harakat qilish va odatiy takrorlanuvchi harakatlar haqida gaplashish o'rganiladi. Sinfxona, supermarket, musobaqa va mehmonxona muhitidagi suhbatlar orqali ko'nikmalar shakllanadi.", "ru": "В этом уроке изучается выражение двух качеств одновременно, совершение одного действия во время другого и привычные повторяющиеся действия. Навыки формируются через диалоги в классе, супермаркете, на соревновании и в гостинице.", "tj": "Дар ин дарс ифодаи ду сифат дар як вақт, иҷрои як амал ҳангоми амали дигар ва амалҳои одатии такроршаванда омӯхта мешавад. Малакаҳо тавассути муколамаҳо дар синф, супермаркет, мусобақа ва меҳмонхона ташаккул меёбанд."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "比赛",  "pinyin": "bǐsài",    "pos": "n./v.", "uz": "musobaqa; musobaqalashmoq",        "ru": "соревнование; соревноваться",      "tj": "мусобақа; мусобақа кардан"},
        {"no": 2,  "zh": "照片",  "pinyin": "zhàopiàn", "pos": "n.",   "uz": "rasm, foto",                       "ru": "фотография, снимок",               "tj": "акс, сурат"},
        {"no": 3,  "zh": "年级",  "pinyin": "niánjí",   "pos": "n.",   "uz": "sinf (maktabda), kurs",            "ru": "класс (в школе), курс",            "tj": "синф (дар мактаб), курс"},
        {"no": 4,  "zh": "聪明",  "pinyin": "cōngmíng", "pos": "adj.", "uz": "aqlli, zehnli",                    "ru": "умный, сообразительный",           "tj": "зирак, ақлманд"},
        {"no": 5,  "zh": "热情",  "pinyin": "rèqíng",   "pos": "adj.", "uz": "iliq, mehribon, ishtiyoqli",       "ru": "горячий, тёплый, энтузиастичный",  "tj": "гармсер, меҳрубон, пурҳавас"},
        {"no": 6,  "zh": "努力",  "pinyin": "nǔlì",     "pos": "adj./adv.", "uz": "g'ayratli; g'ayrat bilan",    "ru": "старательный; старательно",        "tj": "кӯшишкор; бо кӯшиш"},
        {"no": 7,  "zh": "总是",  "pinyin": "zǒngshì",  "pos": "adv.", "uz": "doim, hamisha",                    "ru": "всегда, постоянно",                "tj": "ҳамеша, доимо"},
        {"no": 8,  "zh": "回答",  "pinyin": "huídá",    "pos": "v.",   "uz": "javob bermoq",                     "ru": "отвечать, давать ответ",           "tj": "ҷавоб додан"},
        {"no": 9,  "zh": "饿",    "pinyin": "è",        "pos": "adj.", "uz": "och (qorni och)",                   "ru": "голодный",                         "tj": "гурусна, оч"},
        {"no": 10, "zh": "超市",  "pinyin": "chāoshì",  "pos": "n.",   "uz": "supermarket, do'kon",               "ru": "супермаркет",                      "tj": "супермаркет, дӯкон"},
        {"no": 11, "zh": "蛋糕",  "pinyin": "dàngāo",   "pos": "n.",   "uz": "tort, pirog",                       "ru": "торт, пирог",                      "tj": "торт, кулча"},
        {"no": 12, "zh": "认真",  "pinyin": "rènzhēn",  "pos": "adj.", "uz": "vijdonli, jiddiy, mas'uliyatli",   "ru": "серьёзный, ответственный",         "tj": "масъулиятшинос, ҷиддӣ"},
        {"no": 13, "zh": "客人",  "pinyin": "kèrén",    "pos": "n.",   "uz": "mehmon, xaridor",                   "ru": "гость, посетитель",                "tj": "меҳмон, харидор"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Sinfxonada talabalar haqida suhbat", "scene_ru": "Разговор о студентах в классе", "scene_tj": "Суҳбат дар бораи донишҷӯён дар синф",
            "dialogue": [
                {"speaker": "A", "zh": "你们班有没有又聪明又努力的学生？", "pinyin": "Nǐmen bān yǒu méiyǒu yòu cōngmíng yòu nǔlì de xuésheng?", "uz": "Sizlarda ham aqlli ham g'ayratli talaba bormi?", "ru": "Есть ли у вас в классе студент, который и умный, и старательный?", "tj": "Дар синфи шумо оё донишҷӯе ҳаст, ки ҳам зирак ҳам кӯшишкор бошад?"},
                {"speaker": "B", "zh": "有！小丽又聪明又认真，总是第一个回答问题。", "pinyin": "Yǒu! Xiǎo Lì yòu cōngmíng yòu rènzhēn, zǒngshì dì yī ge huídá wèntí.", "uz": "Bor! Kichik Li ham aqlli ham mas'uliyatli, doim birinchi bo'lib savollarga javob beradi.", "ru": "Есть! Маленькая Ли и умная, и ответственная — всегда первой отвечает на вопросы.", "tj": "Ҳаст! Сяо Ли ҳам зирак ҳам масъулиятшинос аст, ҳамеша аввалин ҷавоб медиҳад."},
                {"speaker": "A", "zh": "她是几年级的？", "pinyin": "Tā shì jǐ niánjí de?", "uz": "U nechanchi sinfda?", "ru": "Она в каком классе?", "tj": "Вай дар синфи чанд аст?"},
                {"speaker": "B", "zh": "她是二年级的，但是学习比三年级的学生还好！", "pinyin": "Tā shì èr niánjí de, dànshì xuéxí bǐ sān niánjí de xuésheng hái hǎo!", "uz": "U ikkinchi sinfda, lekin o'qishi uchinchi sinfliklar bilan ham yaxshiroq!", "ru": "Она во втором классе, но учится лучше, чем третьеклассники!", "tj": "Вай дар синфи дуюм аст, аммо аз донишҷӯёни синфи сеюм беҳтар мехонад!"},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Supermarketda savdo xodimi haqida", "scene_ru": "О продавце в супермаркете", "scene_tj": "Дар бораи фурӯшанда дар супермаркет",
            "dialogue": [
                {"speaker": "A", "zh": "你看那个售货员，她总是笑着跟客人说话。", "pinyin": "Nǐ kàn nàge shòuhuòyuán, tā zǒngshì xiào zhe gēn kèrén shuōhuà.", "uz": "O'sha sotuvchiga qara, u doim kulib mehmonlar bilan gaplashadi.", "ru": "Посмотри на ту продавщицу — она всегда разговаривает с покупателями с улыбкой.", "tj": "Ба он фурӯшанда нигоҳ кун, вай ҳамеша бо табассум бо харидорон сӯҳбат мекунад."},
                {"speaker": "B", "zh": "是啊，她又热情又认真，客人都很喜欢她。", "pinyin": "Shì a, tā yòu rèqíng yòu rènzhēn, kèrén dōu hěn xǐhuan tā.", "uz": "Ha, u ham iliq ham mas'uliyatli, barcha mehmonlar uni yaxshi ko'rishadi.", "ru": "Точно — она и приветливая, и ответственная, все покупатели её любят.", "tj": "Бале, вай ҳам гармсер ҳам масъулиятшинос аст, ҳама харидорон ӯро дӯст медоранд."},
                {"speaker": "A", "zh": "她站着工作了这么多小时，不累吗？", "pinyin": "Tā zhàn zhe gōngzuò le zhème duō xiǎoshí, bù lèi ma?", "uz": "U shu qadar ko'p soat tik turib ishladi, charchamadimi?", "ru": "Она столько часов работала стоя — разве не устала?", "tj": "Вай ин қадар соатҳо истода кор кард, оё хаста нашуд?"},
                {"speaker": "B", "zh": "她说喜欢这个工作，所以不觉得累！", "pinyin": "Tā shuō xǐhuan zhège gōngzuò, suǒyǐ bù juéde lèi!", "uz": "U bu ishni yaxshi ko'rishini aytdi, shuning uchun charchoqni sezmaydi!", "ru": "Она говорит, что любит эту работу, поэтому не чувствует усталости!", "tj": "Вай гуфт, ки ин корро дӯст дорад, аз ин сабаб хастагӣ ҳис намекунад!"},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Musobaqa fotosuratlari haqida", "scene_ru": "О фотографиях соревнований", "scene_tj": "Дар бораи аксҳои мусобақа",
            "dialogue": [
                {"speaker": "A", "zh": "这张照片是在哪儿拍的？你们在参加比赛吗？", "pinyin": "Zhè zhāng zhàopiàn shì zài nǎr pāi de? Nǐmen zài cānjiā bǐsài ma?", "uz": "Bu rasm qayerda tushirilgan? Siz musobaqada qatnashyapsizmi?", "ru": "Где сделано это фото? Вы участвуете в соревновании?", "tj": "Ин акс дар куҷо гирифта шудааст? Шумо дар мусобақа иштирок мекардед?"},
                {"speaker": "B", "zh": "对，这是去年的篮球比赛。我们班又努力又团结，赢了！", "pinyin": "Duì, zhè shì qùnián de lánqiú bǐsài. Wǒmen bān yòu nǔlì yòu tuánjié, yíng le!", "uz": "Ha, bu o'tgan yilgi basketbol musobaqasi. Bizning sinfimiz ham g'ayratli ham birjamul edi, yutdik!", "ru": "Да, это прошлогоднее баскетбольное соревнование. Наш класс и старательный, и дружный — победили!", "tj": "Бале, ин мусобақаи баскетболи соли гузашта аст. Синфи мо ҳам кӯшишкор ҳам якдил буд, ғалаба кардем!"},
                {"speaker": "A", "zh": "太棒了！你是几年级的时候开始打篮球的？", "pinyin": "Tài bàng le! Nǐ shì jǐ niánjí de shíhou kāishǐ dǎ lánqiú de?", "uz": "Ajoyib! Nechanchi sinfda basketbol o'ynashni boshlagansiz?", "ru": "Отлично! В каком классе ты начал играть в баскетбол?", "tj": "Аъло! Дар синфи чанд баскетбол бозӣ карданро оғоз кардед?"},
                {"speaker": "B", "zh": "三年级开始的，我的老师总是鼓励我，非常感谢他。", "pinyin": "Sān niánjí kāishǐ de, wǒ de lǎoshī zǒngshì gǔlì wǒ, fēicháng gǎnxiè tā.", "uz": "Uchinchi sinfdan boshladim, o'qituvchim doim meni rag'batlantirar edi, unga juda minnatdorman.", "ru": "Начал в третьем классе, мой учитель всегда поддерживал меня — очень ему благодарен.", "tj": "Аз синфи сеюм оғоз кардам, омӯзгорам ҳамеша маро ҳавасманд мекард, хеле миннатдорам."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Supermarketda tort sotib olish", "scene_ru": "Покупка торта в супермаркете", "scene_tj": "Харидани торт дар супермаркет",
            "dialogue": [
                {"speaker": "A", "zh": "我今天饿极了，我们去超市买点儿吃的吧。", "pinyin": "Wǒ jīntiān è jí le, wǒmen qù chāoshì mǎi diǎnr chī de ba.", "uz": "Men bugun juda ochinchman, supermarketga borib biroz yegulik sotib olaylik.", "ru": "Я сегодня страшно голоден — пойдём в супермаркет купим что-нибудь поесть.", "tj": "Ман имрӯз хеле гурусна ҳастам, биёед ба супермаркет равем каме хӯрокӣ харем."},
                {"speaker": "B", "zh": "好啊！你想吃什么？超市里有很多又好吃又新鲜的东西。", "pinyin": "Hǎo a! Nǐ xiǎng chī shénme? Chāoshì lǐ yǒu hěn duō yòu hǎochī yòu xīnxiān de dōngxi.", "uz": "Yaxshi! Nima yemoqchisiz? Supermarketda juda ko'p ham mazali ham yangi narsalar bor.", "ru": "Хорошо! Что хочешь есть? В супермаркете много вкусного и свежего.", "tj": "Хуб! Чӣ хӯрдан мехоҳед? Дар супермаркет чизҳои ҳам хӯрданӣ ҳам тозаи зиёде ҳаст."},
                {"speaker": "A", "zh": "我看到那边有蛋糕，又甜又好看！", "pinyin": "Wǒ kàndào nàbiān yǒu dàngāo, yòu tián yòu hǎokàn!", "uz": "U tomonda tort borini ko'rdim, ham shirin ham chiroyli!", "ru": "Я вижу там торт — и сладкий, и красивый!", "tj": "Он тараф торт мебинам, ҳам ширин ҳам зебо!"},
                {"speaker": "B", "zh": "那就买蛋糕吧！售货员总是笑着给客人推荐最好的。", "pinyin": "Nà jiù mǎi dàngāo ba! Shòuhuòyuán zǒngshì xiào zhe gěi kèrén tuījiàn zuì hǎo de.", "uz": "Unday bo'lsa tort sotib olaylik! Sotuvchi doim kulib mehmonlarga eng yaxshisini tavsiya qiladi.", "ru": "Тогда возьмём торт! Продавец всегда улыбается и рекомендует лучшее покупателям.", "tj": "Пас торт харем! Фурӯшанда ҳамеша бо табассум ба харидорон беҳтаринашро тавсия медиҳад."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "\"又……又……\"",
            "title_uz": "'又……又……' — ham...ham... (ikki xususiyat)",
            "title_ru": "Конструкция «又……又……» — и...и... (два качества)",
            "title_tj": "Сохтори «又……又……» — ҳам...ҳам... (ду сифат)",
            "rule_uz": (
                "'又……又……' qolipi biror narsa yoki odamda bir vaqtda ikki sifat yoki holat borligini bildiradi.\n"
                "Qolip: 又 + Sifat/fe'l + 又 + Sifat/fe'l\n"
                "Masalan:\n"
                "  又聪明又努力 (ham aqlli ham g'ayratli)\n"
                "  又新鲜又甜 (ham yangi ham shirin)\n"
                "  又便宜又好看 (ham arzon ham chiroyli)"
            ),
            "rule_ru": (
                "Конструкция '又……又……' выражает наличие двух качеств или состояний одновременно.\n"
                "Структура: 又 + Прил./Гл. + 又 + Прил./Гл.\n"
                "Например:\n"
                "  又聪明又努力 (и умный, и старательный)\n"
                "  又新鲜又甜 (и свежий, и сладкий)\n"
                "  又便宜又好看 (и дешёвый, и красивый)"
            ),
            "rule_tj": (
                "Сохтори '又……又……' мавҷудияти ду сифат ё ҳолатро дар як вақт ифода мекунад.\n"
                "Сохтор: 又 + Сифат/Феъл + 又 + Сифат/Феъл\n"
                "Масалан:\n"
                "  又聪明又努力 (ҳам зирак ҳам кӯшишкор)\n"
                "  又新鲜又甜 (ҳам тоза ҳам ширин)\n"
                "  又便宜又好看 (ҳам арзон ҳам зебо)"
            ),
            "examples": [
                {"zh": "小丽又聪明又认真，总是第一个回答问题。", "pinyin": "Xiǎo Lì yòu cōngmíng yòu rènzhēn, zǒngshì dì yī ge huídá wèntí.", "uz": "Kichik Li ham aqlli ham mas'uliyatli, doim birinchi bo'lib savollarga javob beradi.", "ru": "Маленькая Ли и умная, и ответственная — всегда первой отвечает на вопросы.", "tj": "Сяо Ли ҳам зирак ҳам масъулиятшинос аст, ҳамеша аввалин ҷавоб медиҳад."},
                {"zh": "超市里有很多又好吃又新鲜的东西。", "pinyin": "Chāoshì lǐ yǒu hěn duō yòu hǎochī yòu xīnxiān de dōngxi.", "uz": "Supermarketda juda ko'p ham mazali ham yangi narsalar bor.", "ru": "В супермаркете много вкусного и свежего.", "tj": "Дар супермаркет чизҳои ҳам хӯрданӣ ҳам тозаи зиёде ҳаст."},
            ]
        },
        {
            "no": 2,
            "title_zh": "动作的伴随：V₁着(O₁) + V₂(O₂)",
            "title_uz": "Hamroh harakat: V₁着 + V₂",
            "title_ru": "Сопутствующее действие: V₁着 + V₂",
            "title_tj": "Амали ҳамроҳ: V₁着 + V₂",
            "rule_uz": (
                "Bu qolip V₂ ni V₁ bilan bir vaqtda bajarishni ifodalaydi — V₁ asosiy harakatning shaklini beradi.\n"
                "Qolip: V₁ + 着 + (O₁) + V₂ + (O₂)\n"
                "着 — birinchi harakatning davomiy holatini bildiradi.\n"
                "Masalan:\n"
                "  笑着说话 (kulib gaplashmoq)\n"
                "  站着工作 (tik turib ishlash)\n"
                "  听着音乐学习 (musiqa tinglab o'rganish)"
            ),
            "rule_ru": (
                "Конструкция выражает выполнение V₂ одновременно с V₁ — V₁ задаёт способ действия.\n"
                "Структура: V₁ + 着 + (O₁) + V₂ + (O₂)\n"
                "着 — обозначает длящееся состояние первого действия.\n"
                "Например:\n"
                "  笑着说话 (разговаривать с улыбкой)\n"
                "  站着工作 (работать стоя)\n"
                "  听着音乐学习 (учиться под музыку)"
            ),
            "rule_tj": (
                "Ин сохтор иҷрои V₂-ро дар як вақт бо V₁ ифода мекунад — V₁ тарзи амалро медиҳад.\n"
                "Сохтор: V₁ + 着 + (O₁) + V₂ + (O₂)\n"
                "着 — ҳолати давомандаи амали аввалро нишон медиҳад.\n"
                "Масалан:\n"
                "  笑着说话 (бо табассум сӯҳбат кардан)\n"
                "  站着工作 (истода кор кардан)\n"
                "  听着音乐学习 (бо мусиқа омӯхтан)"
            ),
            "examples": [
                {"zh": "她总是笑着跟客人说话。", "pinyin": "Tā zǒngshì xiào zhe gēn kèrén shuōhuà.", "uz": "U doim kulib mehmonlar bilan gaplashadi.", "ru": "Она всегда разговаривает с покупателями с улыбкой.", "tj": "Вай ҳамеша бо табассум бо харидорон сӯҳбат мекунад."},
                {"zh": "他站着工作了这么多小时，真不容易！", "pinyin": "Tā zhàn zhe gōngzuò le zhème duō xiǎoshí, zhēn bù róngyì!", "uz": "U shu qadar ko'p soat tik turib ishladi, bu rostdan ham oson emas!", "ru": "Он столько часов проработал стоя — это действительно нелегко!", "tj": "Вай ин қадар соатҳо истода кор кард, ин воқеан осон нест!"},
            ]
        },
        {
            "no": 3,
            "title_zh": "\"总是\"+V 表示习惯性动作",
            "title_uz": "'总是'+V — doim takrorlanadigan harakat",
            "title_ru": "«总是»+V — привычное, повторяющееся действие",
            "title_tj": "«总是»+V — амали одатии такроршаванда",
            "rule_uz": (
                "'总是' ravishi fe'l oldidan keladi va harakatning doim yoki ko'p marta takrorlanishini bildiradi.\n"
                "Ma'nosi: doim, hamisha, ko'pincha\n"
                "Qolip: 主语 + 总是 + V + (O)\n"
                "Masalan:\n"
                "  她总是第一个回答问题。(U doim birinchi bo'lib javob beradi.)\n"
                "  他总是迟到。(U doim kechikadi.)\n"
                "  我总是喝热茶。(Men doim issiq choy ichaman.)"
            ),
            "rule_ru": (
                "Наречие '总是' стоит перед глаголом и означает постоянное или повторяющееся действие.\n"
                "Значение: всегда, постоянно\n"
                "Структура: Подлеж. + 总是 + Гл. + (Доп.)\n"
                "Например:\n"
                "  她总是第一个回答问题。(Она всегда первой отвечает.)\n"
                "  他总是迟到。(Он всегда опаздывает.)\n"
                "  我总是喝热茶。(Я всегда пью горячий чай.)"
            ),
            "rule_tj": (
                "Қайди '总是' пеш аз феъл меояд ва амали доимӣ ё такроршавандаро ифода мекунад.\n"
                "Маъно: ҳамеша, доимо\n"
                "Сохтор: Мубтадо + 总是 + Феъл + (Иловаи феълӣ)\n"
                "Масалан:\n"
                "  她总是第一个回答问题。(Вай ҳамеша аввалин ҷавоб медиҳад.)\n"
                "  他总是迟到。(Вай ҳамеша дер меояд.)\n"
                "  我总是喝热茶。(Ман ҳамеша чои гарм менӯшам.)"
            ),
            "examples": [
                {"zh": "她总是笑着跟客人说话，客人都很喜欢她。", "pinyin": "Tā zǒngshì xiào zhe gēn kèrén shuōhuà, kèrén dōu hěn xǐhuan tā.", "uz": "U doim kulib mehmonlar bilan gaplashadi, barcha mehmonlar uni yaxshi ko'rishadi.", "ru": "Она всегда разговаривает с покупателями с улыбкой — все её любят.", "tj": "Вай ҳамеша бо табассум бо харидорон сӯҳбат мекунад, ҳама харидорон ӯро дӯст медоранд."},
                {"zh": "我的老师总是鼓励我，非常感谢他。", "pinyin": "Wǒ de lǎoshī zǒngshì gǔlì wǒ, fēicháng gǎnxiè tā.", "uz": "Mening o'qituvchim doim meni rag'batlantiradi, unga juda minnatdorman.", "ru": "Мой учитель всегда меня поддерживает — очень ему благодарен.", "tj": "Омӯзгорам ҳамеша маро ҳавасманд мекунад, хеле миннатдорам."},
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
                {"prompt_uz": "doim, hamisha", "prompt_ru": "всегда, постоянно", "prompt_tj": "ҳамеша, доимо", "answer": "总是", "pinyin": "zǒngshì"},
                {"prompt_uz": "aqlli, zehnli", "prompt_ru": "умный, сообразительный", "prompt_tj": "зирак, ақлманд", "answer": "聪明", "pinyin": "cōngmíng"},
                {"prompt_uz": "javob bermoq", "prompt_ru": "отвечать", "prompt_tj": "ҷавоб додан", "answer": "回答", "pinyin": "huídá"},
                {"prompt_uz": "och (qorni och)", "prompt_ru": "голодный", "prompt_tj": "гурусна, оч", "answer": "饿", "pinyin": "è"},
                {"prompt_uz": "tort, pirog", "prompt_ru": "торт, пирог", "prompt_tj": "торт, кулча", "answer": "蛋糕", "pinyin": "dàngāo"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (又……又、总是、笑着、认真):",
            "instruction_ru": "Вставьте подходящее слово (又……又、总是、笑着、认真):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (又……又、总是、笑着、认真):",
            "items": [
                {"prompt_uz": "她______聪明______努力，学习很好。", "prompt_ru": "Она ______умная ______старательная, учится хорошо.", "prompt_tj": "Вай ______зирак ______кӯшишкор аст, хуб мехонад.", "answer": "又 / 又", "pinyin": "yòu / yòu"},
                {"prompt_uz": "售货员______跟客人说话，很受欢迎。", "prompt_ru": "Продавец ______разговаривает с покупателями — очень популярен.", "prompt_tj": "Фурӯшанда ______бо харидорон сӯҳбат мекунад, хеле маъруф аст.", "answer": "笑着", "pinyin": "xiào zhe"},
                {"prompt_uz": "他______迟到，老师很不高兴。", "prompt_ru": "Он ______опаздывает, учитель очень недоволен.", "prompt_tj": "Вай ______дер меояд, омӯзгор хеле норозӣ аст.", "answer": "总是", "pinyin": "zǒngshì"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "她总是笑着跟客人说话，客人都很喜欢她。", "prompt_ru": "她总是笑着跟客人说话，客人都很喜欢她。", "prompt_tj": "她总是笑着跟客人说话，客人都很喜欢她。", "answer": "U doim kulib mehmonlar bilan gaplashadi, barcha mehmonlar uni yaxshi ko'rishadi.", "pinyin": "Tā zǒngshì xiào zhe gēn kèrén shuōhuà, kèrén dōu hěn xǐhuan tā."},
                {"prompt_uz": "小丽又聪明又认真，总是第一个回答问题。", "prompt_ru": "小丽又聪明又认真，总是第一个回答问题。", "prompt_tj": "小丽又聪明又认真，总是第一个回答问题。", "answer": "Kichik Li ham aqlli ham mas'uliyatli, doim birinchi bo'lib savollarga javob beradi.", "pinyin": "Xiǎo Lì yòu cōngmíng yòu rènzhēn, zǒngshì dì yī ge huídá wèntí."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["总是", "聪明", "回答", "饿", "蛋糕"]},
        {"no": 2, "answers": ["又 / 又", "笑着", "总是"]},
        {"no": 3, "answers": [
            "U doim kulib mehmonlar bilan gaplashadi, barcha mehmonlar uni yaxshi ko'rishadi.",
            "Kichik Li ham aqlli ham mas'uliyatli, doim birinchi bo'lib savollarga javob beradi.",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'又……又……' qolipidan foydalanib 4 ta gap tuzing. Odamlar va narsalar haqida ikki xususiyatni bildiring.",
            "instruction_ru": "Составьте 4 предложения с конструкцией '又……又……'. Опишите двойные качества людей и предметов.",
            "instruction_tj": "Бо сохтори '又……又……' 4 ҷумла тартиб диҳед. Ду сифати одамон ва чизҳоро нишон диҳед.",
            "words": ["又聪明又", "又热情又", "又新鲜又", "又便宜又", "又甜又"],
            "topic_uz": "Odamlar va narsalarning ikki xususiyati",
            "topic_ru": "Двойные качества людей и предметов",
            "topic_tj": "Ду сифати одамон ва чизҳо",
        },
        {
            "no": 2,
            "instruction_uz": "Tanigan yaxshi do'st yoki o'qituvchi haqida 5-6 gapdan iborat matn yozing. 总是、又……又……、着 qoliplarini ishlating.",
            "instruction_ru": "Напишите 5–6 предложений о хорошем друге или учителе. Используйте конструкции 总是, 又……又……, 着.",
            "instruction_tj": "Дар бораи дӯсти хуб ё омӯзгор 5-6 ҷумла нависед. Сохторҳои 总是, 又……又……, 着-ро истифода баред.",
            "topic_uz": "Mening sevimli o'qituvchim yoki do'stim",
            "topic_ru": "Мой любимый учитель или друг",
            "topic_tj": "Омӯзгор ё дӯсти дӯстдоштаи ман",
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
