import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 5,
    "lesson_code": "HSK2-L05",
    "title": "就买这件吧",
    "goal": json.dumps({
        "uz": "Xarid qilish, ovqatlanish va dam olish haqidagi suhbatlarda o'z fikrini bildira olish; 就 ravishi, 还 ravishi va 有点儿 miqdor birikmasini o'zlashtirish.",
        "ru": "Научиться выражать своё мнение в разговорах о покупках, еде и отдыхе; освоить наречие 就, наречие 还 и конструкцию 有点儿.",
        "tj": "Баён кардани фикр дар сӯҳбатҳо дар бораи харидорӣ, хӯрок ва истироҳат; азхудкунии зарфи 就, зарфи 还 ва ибораи 有点儿.",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Bu darsda kundalik hayotdagi tanlov va qarorlar mavzusi o'rganiladi: qayerda ovqatlanish, qanday kiyim sotib olish, imtihon haqida fikr bildirish va qahva isteʼmoli. Asosiy grammatik mavzular: 就 ravishi (aynan, shu), 还 ravishi (hali ham, qabul qilinarli) va 有点儿 (biroz, sal) miqdor biritmasi.",
        "ru": "На этом уроке изучается тема выбора и принятия решений в повседневной жизни: где поесть, какую одежду купить, мнение об экзамене и потребление кофе. Основные грамматические темы: наречие 就 (именно, вот), наречие 还 (ещё, приемлемо) и конструкция 有点儿 (немного, чуть-чуть).",
        "tj": "Дар ин дарс мавзӯи интихоб ва қабули қарорҳо дар ҳаёти рӯзмарра омӯхта мешавад: дар куҷо хӯрок хӯрдан, кадом либос харидан, фикр дар бораи имтиҳон ва истеъмоли қаҳва. Мавзӯҳои асосии грамматикӣ: зарфи 就, зарфи 还 ва ибораи 有点儿.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "外面",  "pinyin": "wàimiàn", "pos": "n.",    "uz": "tashqarida, tashqi tomon",            "ru": "снаружи, на улице",                  "tj": "берун, берунӣ"},
        {"no": 2,  "zh": "准备",  "pinyin": "zhǔnbèi", "pos": "v.",    "uz": "tayyorlamoq, tayyorgarlik ko'rmoq",   "ru": "готовить, готовиться",               "tj": "омода кардан, тайёр шудан"},
        {"no": 3,  "zh": "就",    "pinyin": "jiù",      "pos": "adv.", "uz": "aynan, shu, xuddi shunday; darhol",   "ru": "именно, вот; сразу, тут же",         "tj": "маҳз, ҳамин; фавран"},
        {"no": 4,  "zh": "鱼",    "pinyin": "yú",       "pos": "n.",    "uz": "baliq",                               "ru": "рыба",                               "tj": "моҳӣ"},
        {"no": 5,  "zh": "吧",    "pinyin": "ba",       "pos": "part.", "uz": "so'roq yoki taklif yuklamasi (shunday emasmi, keling)", "ru": "частица вопроса или предложения (ведь, давай)", "tj": "зарраи савол ё пешниҳод"},
        {"no": 6,  "zh": "件",    "pinyin": "jiàn",     "pos": "m.",   "uz": "dona (kiyim uchun ko'makchi)",        "ru": "штука (счётное слово для одежды)",   "tj": "дона (воҳиди шумориши либос)"},
        {"no": 7,  "zh": "还",    "pinyin": "hái",      "pos": "adv.", "uz": "hali, yana; qabul qilarli, yaxshi",   "ru": "ещё, пока; приемлемо, неплохо",     "tj": "ҳанӯз, боз; қобили қабул"},
        {"no": 8,  "zh": "可以",  "pinyin": "kěyǐ",    "pos": "adj.", "uz": "mumkin, yaxshi, qabul qilarli",       "ru": "можно, хорошо, приемлемо",           "tj": "мумкин, қабул аст"},
        {"no": 9,  "zh": "不错",  "pinyin": "búcuò",   "pos": "adj.", "uz": "yomon emas, yaxshi",                  "ru": "неплохой, хороший",                  "tj": "бад нест, хуб аст"},
        {"no": 10, "zh": "考试",  "pinyin": "kǎoshì",  "pos": "n.",    "uz": "imtihon",                             "ru": "экзамен",                            "tj": "имтиҳон"},
        {"no": 11, "zh": "意思",  "pinyin": "yìsi",    "pos": "n.",    "uz": "ma'no, mazmun",                       "ru": "смысл, значение",                    "tj": "маъно, мазмун"},
        {"no": 12, "zh": "咖啡",  "pinyin": "kāfēi",   "pos": "n.",    "uz": "qahva",                               "ru": "кофе",                               "tj": "қаҳва"},
        {"no": 13, "zh": "对",    "pinyin": "duì",      "pos": "prep.", "uz": "uchun, ga nisbatan (ta'sir ko'rsatish)", "ru": "для, в отношении (воздействие)",  "tj": "барои, нисбат ба (таъсир)"},
        {"no": 14, "zh": "以后",  "pinyin": "yǐhòu",   "pos": "n.",    "uz": "keyingi, keyin, bundan buyon",        "ru": "после, впоследствии, с этих пор",   "tj": "баъд, минбаъд"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "晚上我们去饭馆吃饭，怎么样？", "pinyin": "Wǎnshang wǒmen qù fànguǎn chīfàn, zěnmeyàng?", "uz": "Kechqurun restoranga borib ovqatlansak qanday?", "ru": "Как насчёт того, чтобы вечером пойти поесть в ресторан?", "tj": "Шом мо ба тарабхона рафта хӯрок хӯрем, чӣ тавр?"},
                {"speaker": "B", "zh": "我不想去外面吃，我想在家吃。", "pinyin": "Wǒ bù xiǎng qù wàimiàn chī, wǒ xiǎng zài jiā chī.", "uz": "Men tashqariga chiqib ovqatlanmoqchi emasman, uyda ovqatlanmoqchiman.", "ru": "Я не хочу идти есть на улицу, хочу дома.", "tj": "Ман намехоҳам берун рафта хӯрок хӯрам, мехоҳам дар хона хӯрам."},
                {"speaker": "A", "zh": "那你准备做什么呢？", "pinyin": "Nà nǐ zhǔnbèi zuò shénme ne?", "uz": "Unda nima pishirmoqchisan?", "ru": "Тогда что ты собираешься готовить?", "tj": "Пас ту чӣ пухтан мехоҳӣ?"},
                {"speaker": "B", "zh": "就做你爱吃的鱼吧。", "pinyin": "Jiù zuò nǐ ài chī de yú ba.", "uz": "Sen sevadigan baliqni pishiraylik, shu bo'ladi.", "ru": "Вот приготовлю рыбу, которую ты любишь.", "tj": "Маҳз моҳии дӯстдоштатро мепазам."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Do'konda",
            "scene_ru": "В магазине",
            "scene_tj": "Дар мағоза",
            "dialogue": [
                {"speaker": "A", "zh": "帮我看一下这件衣服怎么样。", "pinyin": "Bāng wǒ kàn yíxià zhè jiàn yīfu zěnmeyàng.", "uz": "Bu kiyimga bir qarab ber, qandayligini ayt.", "ru": "Посмотри, как тебе эта одежда.", "tj": "Ба ин либос як нигоҳ кун, чӣ тавр аст."},
                {"speaker": "B", "zh": "颜色还可以，就是有点儿大。", "pinyin": "Yánsè hái kěyǐ, jiùshì yǒudiǎnr dà.", "uz": "Rangi qabul qilarli, faqat biroz katta.", "ru": "Цвет ничего, только немного велик.", "tj": "Ранг қабул аст, фақат каме калон аст."},
                {"speaker": "A", "zh": "这件小的怎么样？", "pinyin": "Zhè jiàn xiǎo de zěnmeyàng?", "uz": "Bu kichkina kiyim qanday?", "ru": "Как тебе вот этот поменьше?", "tj": "Ин хурдтараш чӣ тавр?"},
                {"speaker": "B", "zh": "这件不错，就买这件吧。", "pinyin": "Zhè jiàn búcuò, jiù mǎi zhè jiàn ba.", "uz": "Bu yamon emas, mana shuni olavering.", "ru": "Этот неплохой, вот его и покупай.", "tj": "Ин бад нест, маҳз ҳамин харед."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Darsxonada",
            "scene_ru": "В классе",
            "scene_tj": "Дар синфхона",
            "dialogue": [
                {"speaker": "A", "zh": "今天去不去打球？", "pinyin": "Jīntiān qù bú qù dǎ qiú?", "uz": "Bugun to'p o'ynagani borami?", "ru": "Сегодня идёшь играть в мяч?", "tj": "Имрӯз ба бозии тӯб меравӣ?"},
                {"speaker": "B", "zh": "这两天有点儿累，不去打球了。", "pinyin": "Zhè liǎng tiān yǒudiǎnr lèi, bù qù dǎ qiú le.", "uz": "Bu ikki kunda biroz charchadim, to'p o'ynagani bormayman.", "ru": "Эти пару дней немного устал, не пойду играть.", "tj": "Ин ду рӯз каме хаста шудам, ба бозии тӯб намеравам."},
                {"speaker": "A", "zh": "你在做什么呢？是在想昨天的考试吗？", "pinyin": "Nǐ zài zuò shénme ne? Shì zài xiǎng zuótiān de kǎoshì ma?", "uz": "Nima qilyapsan? Kechagi imtihon haqida o'ylayapsanmi?", "ru": "Что ты делаешь? Думаешь о вчерашнем экзамене?", "tj": "Ту чӣ мекунӣ? Дар бораи имтиҳони дирӯз фикр мекунӣ?"},
                {"speaker": "B", "zh": "是啊，我觉得听和说还可以，读和写不好，很多字我都不知道是什么意思。", "pinyin": "Shì a, wǒ juéde tīng hé shuō hái kěyǐ, dú hé xiě bù hǎo, hěn duō zì wǒ dōu bù zhīdào shì shénme yìsi.", "uz": "Ha, eshitish va gapirish qabul qilarli, o'qish va yozish yomon, juda ko'p ierogliflarning ma'nosini bilmadim.", "ru": "Да, слушание и говорение ничего, а чтение и письмо плохо, многие иероглифы я не знал.", "tj": "Бале, гӯш додан ва гапидан қабул аст, хондан ва навиштан бад, маъноии хеле зиёд иероглифҳоро надонистам."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Kompaniyada",
            "scene_ru": "В офисе",
            "scene_tj": "Дар идора",
            "dialogue": [
                {"speaker": "A", "zh": "休息一下吧，喝咖啡吗？", "pinyin": "Xiūxi yíxià ba, hē kāfēi ma?", "uz": "Bir oz dam oling, qahva ichasizmi?", "ru": "Отдохни немного, будешь кофе?", "tj": "Каме истироҳат кун, қаҳва менӯшӣ?"},
                {"speaker": "B", "zh": "不喝了，我已经喝两杯了。", "pinyin": "Bù hē le, wǒ yǐjīng hē liǎng bēi le.", "uz": "Ichmayman, allaqachon ikki stakan ichdim.", "ru": "Нет, уже выпил две чашки.", "tj": "Не, аллакай ду косача нӯшидам."},
                {"speaker": "A", "zh": "是啊，咖啡喝多了对身体不好。", "pinyin": "Shì a, kāfēi hē duō le duì shēntǐ bù hǎo.", "uz": "Ha, qahvani ko'p ichish sog'liq uchun yaxshi emas.", "ru": "Да, много кофе пить вредно для здоровья.", "tj": "Бале, зиёд нӯшидани қаҳва барои саломатӣ зарар аст."},
                {"speaker": "B", "zh": "以后我少喝一点儿，每天喝一杯。", "pinyin": "Yǐhòu wǒ shǎo hē yìdiǎnr, měitiān hē yì bēi.", "uz": "Keyingi vaqtda kamroq ichaman, har kuni bir stakan.", "ru": "Впредь буду пить меньше — одну чашку в день.", "tj": "Минбаъд камтар менӯшам, ҳар рӯз як косача."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "副词“就”",
            "title_uz": "Ravish '就'",
            "title_ru": "Наречие 就",
            "title_tj": "Зарфи 就",
            "rule_uz": "'就' ravishi bir nechta ma'noda ishlatiladi: 1) Biror narsa haqida yakun qilib aytilganda ('aynan shu, xuddi shunday'); 2) Tez yoki darhol biror narsa bo'lishini bildiradi; 3) Tasdiq uchun ishlatiladi. Ko'pincha fe'ldan oldin keladi.",
            "rule_ru": "Наречие 就 имеет несколько значений: 1) Подведение итога ('именно вот это'); 2) Скорость или немедленность действия; 3) Подтверждение. Обычно ставится перед глаголом.",
            "rule_tj": "Зарфи 就 якчанд маъно дорад: 1) Хулосабандӣ ('маҳз ин'); 2) Зудии амал ё фавриятро ифода мекунад; 3) Барои тасдиқ. Одатан пеш аз феъл меояд.",
            "examples": [
                {"zh": "就买这件吧。", "pinyin": "Jiù mǎi zhè jiàn ba.", "uz": "Mana shuni olavering.", "ru": "Вот это и покупай.", "tj": "Маҳз ҳамин харед."},
                {"zh": "我二十分钟就到。", "pinyin": "Wǒ èrshí fēnzhōng jiù dào.", "uz": "Men yigirma daqiqada kelaman.", "ru": "Я приеду через двадцать минут.", "tj": "Ман дар бисту дақиқа мерасам."},
            ]
        },
        {
            "no": 2,
            "title_zh": "语气副词“还”（1）",
            "title_uz": "Modal ravish '还' (1)",
            "title_ru": "Модальное наречие 还 (1)",
            "title_tj": "Зарфи модалии 还 (1)",
            "rule_uz": "'还' ravishi bu darsda 'qabul qilarli, yaxshi' ma'nosida ishlatiladi. Biror narsa kutilgandan yaxshiroq yoki o'rtacha yaxshi ekanligini bildiradi. '还可以', '还好' kabi birikmalar odatda 'yomon emas' ma'nosini beradi.",
            "rule_ru": "В этом уроке наречие 还 используется в значении «приемлемо, неплохо». Обозначает, что что-то лучше ожидаемого или на среднем уровне. Сочетания 还可以, 还好 обычно означают «неплохо».",
            "rule_tj": "Дар ин дарс зарфи 还 бо маънои 'қабул аст, бад нест' истифода мешавад. Нишон медиҳад, ки чизе беҳтар аз он чи интизор буданд ё дар сатҳи миёна аст. Ибораҳои 还可以, 还好 одатан маънои 'бад нест' доранд.",
            "examples": [
                {"zh": "颜色还可以，就是有点儿大。", "pinyin": "Yánsè hái kěyǐ, jiùshì yǒudiǎnr dà.", "uz": "Rangi qabul qilarli, faqat biroz katta.", "ru": "Цвет ничего, только немного велик.", "tj": "Ранг қабул аст, фақат каме калон аст."},
                {"zh": "听和说还可以。", "pinyin": "Tīng hé shuō hái kěyǐ.", "uz": "Eshitish va gapirish qabul qilarli.", "ru": "Слушание и говорение приемлемы.", "tj": "Гӯш додан ва гапидан қабул аст."},
            ]
        },
        {
            "no": 3,
            "title_zh": "程度副词“有点儿”",
            "title_uz": "Daraja ravishi '有点儿'",
            "title_ru": "Наречие степени 有点儿",
            "title_tj": "Зарфи дараҷа 有点儿",
            "rule_uz": "'有点儿' sifat yoki fe'l oldidan kelib 'biroz, sal, ozgina' ma'nosini beradi. Ko'pincha salbiy yoki noqulay holatlarda ishlatiladi. O'zbek tilidagi 'biroz, sal ko'p, ozgina' ifodasiga to'g'ri keladi.",
            "rule_ru": "有点儿 ставится перед прилагательным или глаголом и означает «немного, чуть-чуть». Чаще используется в отрицательных или некомфортных ситуациях. Аналог русского «немного, слегка».",
            "rule_tj": "有点儿 пеш аз сифат ё феъл меояд ва маънои 'каме, андак' дорад. Аксар дар вазъиятҳои манфӣ ё номатлуб истифода мешавад.",
            "examples": [
                {"zh": "这件衣服有点儿大。", "pinyin": "Zhè jiàn yīfu yǒudiǎnr dà.", "uz": "Bu kiyim biroz katta.", "ru": "Эта одежда немного велика.", "tj": "Ин либос каме калон аст."},
                {"zh": "这两天有点儿累。", "pinyin": "Zhè liǎng tiān yǒudiǎnr lèi.", "uz": "Bu ikki kunda biroz charchadim.", "ru": "Эти пару дней немного устал.", "tj": "Ин ду рӯз каме хаста шудам."},
            ]
        },
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
            "instruction_ru": "Напишите китайский эквивалент следующих слов:",
            "instruction_tj": "Калимаҳои зеринро ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "tashqarida", "prompt_ru": "снаружи, на улице", "prompt_tj": "берун", "answer": "外面", "pinyin": "wàimiàn"},
                {"prompt_uz": "tayyorlamoq", "prompt_ru": "готовить", "prompt_tj": "омода кардан", "answer": "准备", "pinyin": "zhǔnbèi"},
                {"prompt_uz": "imtihon", "prompt_ru": "экзамен", "prompt_tj": "имтиҳон", "answer": "考试", "pinyin": "kǎoshì"},
                {"prompt_uz": "qahva", "prompt_ru": "кофе", "prompt_tj": "қаҳва", "answer": "咖啡", "pinyin": "kāfēi"},
                {"prompt_uz": "ma'no", "prompt_ru": "смысл, значение", "prompt_tj": "маъно", "answer": "意思", "pinyin": "yìsi"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (就、还、有点儿、不错、以后):",
            "instruction_ru": "Вставьте подходящее слово (就、还、有点儿、不错、以后):",
            "instruction_tj": "Калимаи мувофиқро нависед (就、还、有点儿、不错、以后):",
            "items": [
                {"prompt_uz": "这件衣服______大，我不买了。", "answer": "有点儿", "pinyin": "yǒudiǎnr"},
                {"prompt_uz": "颜色______可以，______是有点儿大。", "answer": "还 / 就", "pinyin": "hái / jiù"},
                {"prompt_uz": "______我少喝一点儿咖啡。", "answer": "以后", "pinyin": "yǐhòu"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_uzbek",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на узбекский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони ӯзбекӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "这件不错，就买这件吧。", "answer": "Bu yamon emas, mana shuni olavering.", "pinyin": "Zhè jiàn búcuò, jiù mǎi zhè jiàn ba."},
                {"prompt_uz": "咖啡喝多了对身体不好。", "answer": "Qahvani ko'p ichish sog'liq uchun yaxshi emas.", "pinyin": "Kāfēi hē duō le duì shēntǐ bù hǎo."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["外面", "准备", "考试", "咖啡", "意思"]},
        {"no": 2, "answers": ["有点儿", "还 / 就", "以后"]},
        {"no": 3, "answers": ["Bu yamon emas, mana shuni olavering.", "Qahvani ko'p ichish sog'liq uchun yaxshi emas."]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib 4 ta gap tuzing. Har bir gapda 就, 还可以 yoki 有点儿 so'zlarini ishlating.",
            "instruction_ru": "Составьте 4 предложения, используя следующие слова. В каждом предложении используйте 就, 还可以 или 有点儿.",
            "instruction_tj": "Бо истифода аз калимаҳои зерин 4 ҷумла тартиб диҳед. Дар ҳар ҷумла 就, 还可以 ё 有点儿 -ро истифода баред.",
            "words": ["就", "还可以", "有点儿", "不错", "以后"],
            "example": "这件衣服颜色还可以，就是有点儿大。",
        },
        {
            "no": 2,
            "instruction_uz": "Do'stingiz bilan xarid qilish haqida kichik suhbat yozing (6-8 gap). Kiyimni tavsiflab, narxini so'rang va qaror qiling.",
            "instruction_ru": "Напишите небольшой диалог с другом о покупках (6–8 реплик). Опишите одежду, спросите цену и примите решение.",
            "instruction_tj": "Мукотибаи хурде бо дӯст дар бораи харидорӣ нависед (6-8 ҷумла). Либосро тавсиф кунед, нархро бипурсед ва қарор қабул кунед.",
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
