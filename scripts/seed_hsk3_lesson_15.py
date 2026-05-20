import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 15,
    "lesson_code": "HSK3-L15",
    "title": json.dumps({"zh": "其他都没什么问题", "uz": "Boshqa hamma narsa muammosiz", "ru": "Всё остальное без проблем", "tj": "Ҳама чизи дигар мушкиле нест"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "'Bundan tashqari ham/yana' iboralari, so'roq olmoshlarining umumlashtiruvchi qo'llanishi va 'juda' ifodalovchi '极了' o'rganish", "ru": "Выражения 'помимо/кроме', обобщающее использование вопросительных местоимений и '极了' (очень)", "tj": "Ибораҳои 'ғайр аз/ба ҷуз', истифодаи умумикунандаи зомирҳои саволӣ ва '极了' (хеле)"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda '除了…以外，都/还/也' tuzilmasini, so'roq olmoshlarining umumlashtiruvchi ikkinchi qo'llanishini va '极了' so'zini o'rganamiz.", "ru": "В этом уроке мы изучим конструкцию '除了…以外，都/还/也', второе обобщающее использование вопросительных местоимений и '极了'.", "tj": "Дар ин дарс мо сохтори '除了…以外，都/还/也', истифодаи дуввуми умумикунандаи зомирҳои саволӣ ва '极了'-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "其他", "pinyin": "qítā", "pos": "pron/adj", "uz": "boshqa, qolgan", "ru": "другой, остальной", "tj": "дигар, боқӣ"},
        {"no": 2, "zh": "除了", "pinyin": "chúle", "pos": "prep", "uz": "bundan tashqari, ...dan boshqa", "ru": "кроме, помимо", "tj": "ғайр аз, ба ҷуз"},
        {"no": 3, "zh": "以外", "pinyin": "yǐwài", "pos": "n", "uz": "...dan tashqarida", "ru": "за исключением, кроме", "tj": "берун аз, ба ғайр аз"},
        {"no": 4, "zh": "极", "pinyin": "jí", "pos": "adv", "uz": "eng, juda (eng darajada)", "ru": "крайне, чрезвычайно", "tj": "ниҳоят, ниҳоятдараҷа"},
        {"no": 5, "zh": "满意", "pinyin": "mǎnyì", "pos": "adj", "uz": "mamnun, qoniqarli", "ru": "доволен, удовлетворён", "tj": "қаноатманд, хурсанд"},
        {"no": 6, "zh": "解决", "pinyin": "jiějué", "pos": "v", "uz": "hal qilmoq", "ru": "решать, разрешать", "tj": "ҳал кардан"},
        {"no": 7, "zh": "问题", "pinyin": "wèntí", "pos": "n", "uz": "muammo, savol", "ru": "проблема, вопрос", "tj": "мушкил, савол"},
        {"no": 8, "zh": "检查", "pinyin": "jiǎnchá", "pos": "v", "uz": "tekshirmoq", "ru": "проверять, осматривать", "tj": "санҷидан, тафтиш кардан"},
        {"no": 9, "zh": "健康", "pinyin": "jiànkāng", "pos": "adj/n", "uz": "sog'lom; sog'liq", "ru": "здоровый; здоровье", "tj": "солим; саломатӣ"},
        {"no": 10, "zh": "完全", "pinyin": "wánquán", "pos": "adv/adj", "uz": "butunlay, to'liq", "ru": "полностью, совершенно", "tj": "пурра, комилан"},
        {"no": 11, "zh": "报告", "pinyin": "bàogào", "pos": "n/v", "uz": "hisobot; hisobot bermoq", "ru": "доклад; докладывать", "tj": "гузориш; гузориш додан"},
        {"no": 12, "zh": "结果", "pinyin": "jiéguǒ", "pos": "n", "uz": "natija", "ru": "результат, итог", "tj": "натиҷа"},
        {"no": 13, "zh": "正常", "pinyin": "zhèngcháng", "pos": "adj", "uz": "normal, odatiy", "ru": "нормальный, обычный", "tj": "муқаррарӣ, одатӣ"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Tibbiy tekshiruv natijalari", "ru": "Результаты медицинского осмотра", "tj": "Натиҷаҳои муоинаи тиббӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "医生，检查结果怎么样？", "pinyin": "Yīshēng, jiǎnchá jiéguǒ zěnme yàng?", "uz": "Doktor, tekshiruv natijalari qanday?", "ru": "Доктор, каковы результаты осмотра?", "tj": "Духтур, натиҷаҳои муоина чӣ тавр аст?"},
                {"speaker": "B", "zh": "除了血压以外，其他都没什么问题！", "pinyin": "Chúle xuèyā yǐwài, qítā dōu méi shénme wèntí!", "uz": "Qon bosimdan tashqari, boshqa hamma narsa muammosiz!", "ru": "Кроме давления крови, всё остальное без проблем!", "tj": "Ба ғайр аз фишори хун, ҳама чизи дигар мушкиле нест!"},
                {"speaker": "A", "zh": "太好了！血压有什么问题？", "pinyin": "Tài hǎo le! Xuèyā yǒu shénme wèntí?", "uz": "Juda yaxshi! Qon bosimida qanday muammo bor?", "ru": "Отлично! Что с давлением?", "tj": "Олӣ! Фишори хун чӣ мушкилӣ дорад?"},
                {"speaker": "B", "zh": "血压高了一点儿，但不严重，注意饮食就好了。", "pinyin": "Xuèyā gāo le yīdiǎnr, dàn bù yánzhòng, zhùyì yǐnshí jiù hǎo le.", "uz": "Qon bosimi biroz baland, lekin jiddiy emas, ovqatlanishga e'tibor bersangiz bo'ladi.", "ru": "Давление чуть повышено, но не серьёзно, следите за питанием и всё наладится.", "tj": "Фишори хун каме баланд аст, аммо ҷиддӣ нест, ба хӯрок диққат диҳед, хуб мешавад."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Sog'liq haqida muloqot", "ru": "Разговор о здоровье", "tj": "Муколама дар бораи саломатӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "你最近身体怎么样？", "pinyin": "Nǐ zuìjìn shēntǐ zěnme yàng?", "uz": "Yaqinda sog'ligingiz qanday?", "ru": "Как у тебя здоровье последнее время?", "tj": "Охирон саломатиатон чӣ тавр?"},
                {"speaker": "B", "zh": "除了有点儿累以外，其他都正常，极满意了！", "pinyin": "Chúle yǒudiǎnr lèi yǐwài, qítā dōu zhèngcháng, jí mǎnyì le!", "uz": "Biroz charchashdan tashqari, boshqa hammasi normal, juda mamnunam!", "ru": "Кроме небольшой усталости, всё нормально, очень доволен!", "tj": "Ба ғайр аз каме хасташавӣ, ҳама муқаррарӣ, ниҳоят қаноатмандам!"},
                {"speaker": "A", "zh": "真好！健康是最重要的！", "pinyin": "Zhēn hǎo! Jiànkāng shì zuì zhòngyào de!", "uz": "Juda yaxshi! Sog'liq eng muhim narsa!", "ru": "Отлично! Здоровье — это самое важное!", "tj": "Хуб! Саломатӣ муҳимтарин чиз аст!"},
                {"speaker": "B", "zh": "是的，什么都不如健康重要！", "pinyin": "Shì de, shénme dōu bùrú jiànkāng zhòngyào!", "uz": "Ha, hech narsa sog'liqdan muhim emas!", "ru": "Да, ничто не важнее здоровья!", "tj": "Ҳа, ҳеҷ чиз аз саломатӣ муҳимтар нест!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Muammoni hal qilish", "ru": "Решение проблемы", "tj": "Ҳал кардани мушкилот"},
            "dialogue": [
                {"speaker": "A", "zh": "项目报告除了结论以外，其他都写完了。", "pinyin": "Xiàngmù bàogào chúle jiélùn yǐwài, qítā dōu xiě wán le.", "uz": "Loyiha hisobotida xulosa qismidan tashqari, boshqa hammasi yozildi.", "ru": "В отчёте по проекту, кроме заключения, всё написано.", "tj": "Дар гузориши лоиҳа, ба ғайр аз хулоса, ҳама навишта шуд."},
                {"speaker": "B", "zh": "好极了！结论什么时候能写完？", "pinyin": "Hǎo jí le! Jiélùn shénme shíhou néng xiě wán?", "uz": "Zo'r! Xulosa qachon yozib bo'linadi?", "ru": "Отлично! Когда будет готово заключение?", "tj": "Олӣ! Хулоса кай тамом мешавад?"},
                {"speaker": "A", "zh": "今天晚上就能写完，别担心！", "pinyin": "Jīntiān wǎnshàng jiù néng xiě wán, bié dānxīn!", "uz": "Bu kechqurun yozib bo'linadi, xavotir olmang!", "ru": "Сегодня вечером закончу, не беспокойтесь!", "tj": "Имшаб тамом мешавад, нигарон набошед!"},
                {"speaker": "B", "zh": "太好了，你写得极认真，我很满意！", "pinyin": "Tài hǎo le, nǐ xiě de jí rènzhēn, wǒ hěn mǎnyì!", "uz": "Juda yaxshi, siz juda puxta yozasiz, juda mamnunam!", "ru": "Отлично, ты пишешь очень добросовестно, я очень доволен!", "tj": "Олӣ, шумо ниҳоят масъулиятшиносона менависед, ман хеле қаноатмандам!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Kurs natijalarini muhokama qilish", "ru": "Обсуждение итогов курса", "tj": "Муҳокимаи натиҷаҳои курс"},
            "dialogue": [
                {"speaker": "A", "zh": "这次课除了语法以外，其他都完全没问题。", "pinyin": "Zhè cì kè chúle yǔfǎ yǐwài, qítā dōu wánquán méi wèntí.", "uz": "Bu kurs grammatikadan tashqari, boshqa hamma narsa mutlaqo muammosiz.", "ru": "На этом курсе, кроме грамматики, всё остальное совершенно без проблем.", "tj": "Дар ин курс, ба ғайр аз грамматика, ҳама чизи дигар пурра мушкиле нест."},
                {"speaker": "B", "zh": "哪里哪里，你的语法也好极了！", "pinyin": "Nǎlǐ nǎlǐ, nǐ de yǔfǎ yě hǎo jí le!", "uz": "Yo'q yo'q, sizning grammatikangiz ham juda zo'r!", "ru": "Что вы, ваша грамматика тоже очень хороша!", "tj": "Не не, грамматикаи шумо ҳам ниҳоят олӣ аст!"},
                {"speaker": "A", "zh": "谢谢老师，我觉得哪儿都还需要努力！", "pinyin": "Xièxie lǎoshī, wǒ juéde nǎr dōu hái xūyào nǔlì!", "uz": "Rahmat, o'qituvchi, menimcha hamma joyda hali harakat kerak!", "ru": "Спасибо, учитель, я думаю, везде ещё нужно стараться!", "tj": "Раҳмат, муаллим, ба фикрам ҳама ҷо ҳанӯз кӯшиш лозим аст!"},
                {"speaker": "B", "zh": "好，继续加油！", "pinyin": "Hǎo, jìxù jiāyóu!", "uz": "Yaxshi, davom eting!", "ru": "Отлично, продолжай в том же духе!", "tj": "Хуб, идома диҳед!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "除了……以外，都/还/也……",
            "title_uz": "……dan tashqari, hammasi/ham/yana……",
            "title_ru": "Кроме……, всё/тоже/ещё……",
            "title_tj": "Ба ғайр аз……, ҳама/ҳам/боз……",
            "rule_uz": "'除了A以外，都/还/也+B' tuzilmasi ikki ma'noda ishlatiladi: (1) A dan tashqari hamma narsa B (都) — istisno; (2) A dan tashqari B ham (还/也) — qo'shimcha. Farqni '都' va '还/也' orqali tushunish kerak.",
            "rule_ru": "Конструкция '除了A以外，都/还/也+B' имеет два значения: (1) Кроме A всё является B (都) — исключение; (2) Кроме A, B тоже (还/也) — добавление. Разницу нужно понять через '都' и '还/也'.",
            "rule_tj": "Сохтори '除了A以外，都/还/也+B' ду маъно дорад: (1) Ба ғайр аз A ҳама B аст (都) — истисно; (2) Ба ғайр аз A, B ҳам (还/也) — илова. Фарқро тавассути '都' ва '还/也' фаҳмидан лозим аст.",
            "examples": [
                {"zh": "除了血压以外，其他都没问题。", "pinyin": "Chúle xuèyā yǐwài, qítā dōu méi wèntí.", "uz": "Qon bosimdan tashqari, boshqa hamma narsa muammosiz.", "ru": "Кроме давления, всё остальное без проблем.", "tj": "Ба ғайр аз фишори хун, ҳама чизи дигар мушкиле нест."},
                {"zh": "除了汉语，她还会说日语。", "pinyin": "Chúle Hànyǔ, tā hái huì shuō Rìyǔ.", "uz": "Xitoy tilidan tashqari, u yapon tilini ham biladi.", "ru": "Кроме китайского, она ещё умеет говорить по-японски.", "tj": "Ба ғайр аз чинӣ, вай ҳам ба ҷопонӣ ҳарф мезанад."}
            ]
        },
        {
            "no": 2,
            "title_zh": "疑问代词活用②：哪儿都/什么都（否定）",
            "title_uz": "So'roq olmoshlarining maxsus qo'llanishi②: hech qayerda/hech narsa (inkor)",
            "title_ru": "Особое употребление вопросительных местоимений②: нигде/ничего (отрицание)",
            "title_tj": "Истифодаи хоси зомирҳои саволӣ②: ҳеҷ куҷо/ҳеҷ чиз (манфӣ)",
            "rule_uz": "So'roq olmoshlari + 都 + inkor fe'l = mutlaq inkor. Masalan: 什么都不 = hech narsani emas; 哪儿都不 = hech qayerda emas; 谁都不 = hech kim emas. Bular kuchli umumlashtiruvchi inkorlar.",
            "rule_ru": "Вопросительное местоимение + 都 + отрицательный глагол = абсолютное отрицание. Например: 什么都不 = ничего не; 哪儿都不 = нигде не; 谁都不 = никто не. Это сильные обобщающие отрицания.",
            "rule_tj": "Зомири саволӣ + 都 + феъли манфӣ = инкори мутлақ. Масалан: 什么都不 = ҳеҷ чизро не; 哪儿都不 = ҳеҷ куҷо не; 谁都不 = ҳеҷ кас не. Инҳо инкорҳои умумикунандаи қавӣ ҳастанд.",
            "examples": [
                {"zh": "什么都不如健康重要！", "pinyin": "Shénme dōu bùrú jiànkāng zhòngyào!", "uz": "Hech narsa sog'liqdan muhim emas!", "ru": "Ничто не важнее здоровья!", "tj": "Ҳеҷ чиз аз саломатӣ муҳимтар нест!"},
                {"zh": "他哪儿都不想去。", "pinyin": "Tā nǎr dōu bù xiǎng qù.", "uz": "U hech qayerga bormoqchi emas.", "ru": "Он никуда не хочет идти.", "tj": "Вай ҳеҷ куҷо рафтан намехоҳад."}
            ]
        },
        {
            "no": 3,
            "title_zh": "形容词/动词 + 极了",
            "title_uz": "Sifat/Fe'l + 极了 (juda, nihoyatda)",
            "title_ru": "Прилагательное/Глагол + 极了 (очень, крайне)",
            "title_tj": "Сифат/Феъл + 极了 (хеле, ниҳоят)",
            "rule_uz": "'极了' sifat yoki fe'ldan keyin kelib, eng yuqori darajani bildiradi. '非常' dan kuchliroq. Masalan: 好极了 = zo'r (juda ajoyib), 满意极了 = nihoyatda mamnun.",
            "rule_ru": "'极了' следует за прилагательным или глаголом и выражает высшую степень. Сильнее, чем '非常'. Например: 好极了 = отлично (очень здорово), 满意极了 = чрезвычайно доволен.",
            "rule_tj": "'极了' баъди сифат ё феъл омада, дараҷаи олиро ифода мекунад. Аз '非常' қавитар. Масалан: 好极了 = олӣ (хеле аҷоиб), 满意极了 = ниҳоят қаноатманд.",
            "examples": [
                {"zh": "好极了！就这样做！", "pinyin": "Hǎo jí le! Jiù zhèyàng zuò!", "uz": "Zo'r! Xuddi shunday qiling!", "ru": "Отлично! Именно так и делайте!", "tj": "Олӣ! Маҳз ҳамин тавр кунед!"},
                {"zh": "你写得认真极了！", "pinyin": "Nǐ xiě de rènzhēn jí le!", "uz": "Siz juda puxta yozdingiz!", "ru": "Вы написали крайне добросовестно!", "tj": "Шумо ниҳоят масъулиятшиносона навиштед!"}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Qon bosimdan tashqari, boshqa hamma narsa muammosiz!", "ru": "Кроме давления, всё остальное без проблем!", "tj": "Ба ғайр аз фишори хун, ҳама чизи дигар мушкиле нест!"},
                {"no": 2, "uz": "Xitoy tilidan tashqari, u yapon tilini ham biladi.", "ru": "Кроме китайского, она ещё умеет говорить по-японски.", "tj": "Ба ғайр аз чинӣ, вай ҳам ба ҷопонӣ ҳарф мезанад."},
                {"no": 3, "uz": "Hech narsa sog'liqdan muhim emas!", "ru": "Ничто не важнее здоровья!", "tj": "Ҳеҷ чиз аз саломатӣ муҳимтар нест!"},
                {"no": 4, "uz": "Zo'r! Xuddi shunday qiling!", "ru": "Отлично! Именно так и делайте!", "tj": "Олӣ! Маҳз ҳамин тавр кунед!"},
                {"no": 5, "uz": "U hech qayerga bormoqchi emas.", "ru": "Он никуда не хочет идти.", "tj": "Вай ҳеҷ куҷо рафтан намехоҳад."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "除了血压___外，其他都没问题！", "sentence_uz": "Qon bosim___ tashqari, boshqa hammasi muammosiz!", "sentence_ru": "Кроме давления ___, всё без проблем!", "sentence_tj": "Ба ғайр аз фишори хун ___, ҳама мушкиле нест!", "hint": "以"},
                {"no": 2, "sentence_zh": "什么___不如健康重要！", "sentence_uz": "Hech narsa sog'liqdan muhim ___!", "sentence_ru": "Ничто ___ важнее здоровья!", "sentence_tj": "Ҳеҷ чиз аз саломатӣ муҳимтар ___!", "hint": "都"},
                {"no": 3, "sentence_zh": "好___了！就这样做！", "sentence_uz": "Zo'r ___! Xuddi shunday qiling!", "sentence_ru": "___ хорошо! Именно так делайте!", "sentence_tj": "Олӣ ___! Маҳз ҳамин тавр кунед!", "hint": "极"},
                {"no": 4, "sentence_zh": "除了汉语，她___会说日语。", "sentence_uz": "Xitoy tilidan tashqari, u yapon tilini ___ biladi.", "sentence_ru": "Кроме китайского, она ___ умеет по-японски.", "sentence_tj": "Ба ғайр аз чинӣ, вай ба ҷопонӣ ___.", "hint": "还"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "这次课除了语法以外，其他都完全没问题。", "pinyin": "Zhè cì kè chúle yǔfǎ yǐwài, qítā dōu wánquán méi wèntí."},
                {"no": 2, "zh": "你写得认真极了，我很满意！", "pinyin": "Nǐ xiě de rènzhēn jí le, wǒ hěn mǎnyì!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "除了血压以外，其他都没什么问题！"},
                {"no": 2, "zh": "除了汉语，她还会说日语。"},
                {"no": 3, "zh": "什么都不如健康重要！"},
                {"no": 4, "zh": "好极了！就这样做！"},
                {"no": 5, "zh": "他哪儿都不想去。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "以"},
                {"no": 2, "answer": "都"},
                {"no": 3, "answer": "极"},
                {"no": 4, "answer": "还"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Bu kurs grammatikadan tashqari, boshqa hamma narsa mutlaqo muammosiz.", "ru": "На этом курсе, кроме грамматики, всё остальное совершенно без проблем.", "tj": "Дар ин курс, ба ғайр аз грамматика, ҳама чизи дигар пурра мушкиле нест."},
                {"no": 2, "uz": "Siz juda puxta yozdingiz, juda mamnunam!", "ru": "Вы написали крайне добросовестно, я очень доволен!", "tj": "Шумо ниҳоят масъулиятшиносона навиштед, ман хеле қаноатмандам!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'除了…以外，都…' va '除了…以外，还/也…' tuzilmalarini ishlatib, o'z hayotingizdan 4 ta jumla yozing (2 tasida 都, 2 tasida 还 ishlating).", "ru": "Напишите 4 предложения из своей жизни с '除了…以外，都…' и '除了…以外，还/也…' (2 с 都, 2 с 还).", "tj": "4 ҷумла аз ҳаёти худ бо '除了…以外，都…' ва '除了…以外，还/也…' нависед (2 бо 都, 2 бо 还)."},
        {"task_no": 2, "uz": "'极了' va '什么/哪儿/谁+都+inkor' iboralarini ishlatib, sog'liq yoki ish haqida 3 ta jumla tuzing.", "ru": "Составьте 3 предложения о здоровье или работе с '极了' и '什么/哪儿/谁+都+отрицание'.", "tj": "3 ҷумла дар бораи саломатӣ ё кор бо '极了' ва '什么/哪儿/谁+都+инкор' тартиб диҳед."}
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
