import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 14,
    "lesson_code": "HSK3-L14",
    "title": json.dumps({"zh": "你把水果拿过来", "uz": "Mevalarni olib keling", "ru": "Принеси фрукты сюда", "tj": "Меваҳоро ин ҷо биёр"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "'把'-konstruktsiyasi 3-qism (natija/yo'nalish to'ldiruvchisi bilan), 'avval...keyin...so'ng...' va 'xuddi...kabi' iboralari", "ru": "Конструкция '把' часть 3 (с результатным/направленным дополнением), 'сначала...потом...затем...' и 'как/словно'", "tj": "Сохтори '把' қисми 3 (бо пуркунандаи натиҷа/самт), 'аввал...баъд...пас...' ва 'монанди...' "}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda '把'-konstruktsiyasining natija yoki yo'nalish to'ldiruvchisi bilan qo'llanishini, 'Avval…Keyin/Yana…So'ng' ketma-ketlik ifodasini va 'xuddi…kabi' taqqoslash iborasini o'rganamiz.", "ru": "В этом уроке мы изучим '把' с результатным/направленным дополнением, последовательность 'сначала…потом/снова…затем' и сравнительное выражение 'как/словно…'.", "tj": "Дар ин дарс мо '把' бо пуркунандаи натиҷа/самт, пайдарпаии 'аввал…баъд/боз…пас' ва ибораи муқоисавии 'монанди…'-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "水果", "pinyin": "shuǐguǒ", "pos": "n", "uz": "meva", "ru": "фрукты", "tj": "мева"},
        {"no": 2, "zh": "拿", "pinyin": "ná", "pos": "v", "uz": "olmoq, ko'tarmoq", "ru": "брать, нести", "tj": "гирифтан, бурдан"},
        {"no": 3, "zh": "过来", "pinyin": "guò lái", "pos": "v", "uz": "bu yerga o'tib kelmoq", "ru": "подойти сюда", "tj": "ин ҷо омадан"},
        {"no": 4, "zh": "先", "pinyin": "xiān", "pos": "adv", "uz": "avval, birinchi", "ru": "сначала, прежде всего", "tj": "аввал, пеш аз ҳама"},
        {"no": 5, "zh": "再", "pinyin": "zài", "pos": "adv", "uz": "keyin, undan so'ng", "ru": "потом, затем", "tj": "баъд, пас аз он"},
        {"no": 6, "zh": "然后", "pinyin": "ránhòu", "pos": "conj", "uz": "so'ng, shundan keyin", "ru": "затем, после этого", "tj": "сипас, баъд аз ин"},
        {"no": 7, "zh": "像", "pinyin": "xiàng", "pos": "v/prep", "uz": "o'xshash, xuddi...kabi", "ru": "похожий; как, словно", "tj": "монанд; ба монанди"},
        {"no": 8, "zh": "盘子", "pinyin": "pánzi", "pos": "n", "uz": "lagan, tarelka", "ru": "тарелка, блюдо", "tj": "табақ, лаган"},
        {"no": 9, "zh": "洗", "pinyin": "xǐ", "pos": "v", "uz": "yuvmoq", "ru": "мыть, стирать", "tj": "шустан"},
        {"no": 10, "zh": "切", "pinyin": "qiē", "pos": "v", "uz": "kesmoq", "ru": "резать, нарезать", "tj": "буридан"},
        {"no": 11, "zh": "摆", "pinyin": "bǎi", "pos": "v", "uz": "joylashtirmoq, termoq", "ru": "расставлять, разложить", "tj": "ҷой кардан, паҳн кардан"},
        {"no": 12, "zh": "准备", "pinyin": "zhǔnbèi", "pos": "v", "uz": "tayyorlamoq", "ru": "готовить, подготавливать", "tj": "омода кардан"},
        {"no": 13, "zh": "桌子", "pinyin": "zhuōzi", "pos": "n", "uz": "stol", "ru": "стол", "tj": "миз"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Dasturxon tayyorlash", "ru": "Подготовка стола", "tj": "Омода кардани дастархон"},
            "dialogue": [
                {"speaker": "A", "zh": "你把水果拿过来，我来切。", "pinyin": "Nǐ bǎ shuǐguǒ ná guò lái, wǒ lái qiē.", "uz": "Mevalarni olib keling, men kesaman.", "ru": "Принеси фрукты сюда, я порежу.", "tj": "Меваҳоро ин ҷо биёр, ман мебурам."},
                {"speaker": "B", "zh": "好，先把苹果洗干净了再切吧。", "pinyin": "Hǎo, xiān bǎ píngguǒ xǐ gānjìng le zài qiē ba.", "uz": "Yaxshi, avval olmani yaxshilab yuvib, keyin kesaylik.", "ru": "Хорошо, сначала тщательно помой яблоки, потом режем.", "tj": "Хуб, аввал себро хуб бишӯем, баъд мебурем."},
                {"speaker": "A", "zh": "对，先洗，再切，然后摆在盘子里。", "pinyin": "Duì, xiān xǐ, zài qiē, ránhòu bǎi zài pánzi lǐ.", "uz": "To'g'ri, avval yuvib, keyin kesib, so'ng laganga tizamiz.", "ru": "Верно, сначала мыть, потом резать, затем разложить на тарелку.", "tj": "Дуруст, аввал мешӯем, баъд мебурем, сипас дар табақ мечинем."},
                {"speaker": "B", "zh": "好，我把桌子也准备好了！", "pinyin": "Hǎo, wǒ bǎ zhuōzi yě zhǔnbèi hǎo le!", "uz": "Yaxshi, men stolni ham tayyorladim!", "ru": "Хорошо, я и стол приготовил!", "tj": "Хуб, ман мизро ҳам тайёр кардам!"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Taom pishirish tartibi", "ru": "Порядок приготовления блюда", "tj": "Тартиби пухтани хӯрок"},
            "dialogue": [
                {"speaker": "A", "zh": "做这道菜怎么做？", "pinyin": "Zuò zhè dào cài zěnme zuò?", "uz": "Bu taomni qanday tayyorlash kerak?", "ru": "Как готовить это блюдо?", "tj": "Ин хӯрокро чӣ тавр пухтан?"},
                {"speaker": "B", "zh": "先把肉切成小块，再放油，然后加蔬菜。", "pinyin": "Xiān bǎ ròu qiē chéng xiǎo kuài, zài fàng yóu, ránhòu jiā shūcài.", "uz": "Avval go'shtni kichik bo'laklarga kesing, keyin yog' soling, so'ng sabzavot qo'shing.", "ru": "Сначала нарежьте мясо на кусочки, потом добавьте масло, затем добавьте овощи.", "tj": "Аввал гӯштро ба порчаҳои хурд буред, баъд равған рехта, сипас сабзавот илова кунед."},
                {"speaker": "A", "zh": "像你这样做，肯定很好吃！", "pinyin": "Xiàng nǐ zhèyàng zuò, kěndìng hěn hǎochī!", "uz": "Sizning usulda pishirsam, albatta juda mazali bo'ladi!", "ru": "Если готовить так, как ты, обязательно будет очень вкусно!", "tj": "Агар ба монанди шумо пазем, албатта хеле хушмаза мешавад!"},
                {"speaker": "B", "zh": "哈哈，多练习就好了，先做做看！", "pinyin": "Hāhā, duō liànxí jiù hǎo le, xiān zuòzuò kàn!", "uz": "Xaxa, ko'p mashq qilsangiz bo'ladi, avval sinab ko'ring!", "ru": "Хахаха, больше практикуйся и всё получится, сначала попробуй!", "tj": "Ҳаҳаҳа, бештар машқ кунед, мешавад, аввал санҷед!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Narsalarni joylashtirish", "ru": "Расстановка вещей", "tj": "Ҷой кардани чизҳо"},
            "dialogue": [
                {"speaker": "A", "zh": "请你把这些书搬过去放好。", "pinyin": "Qǐng nǐ bǎ zhèxiē shū bān guò qù fàng hǎo.", "uz": "Iltimos, bu kitoblarni ko'chirib u yerga qo'yib qo'ying.", "ru": "Пожалуйста, перенеси эти книги туда и поставь.", "tj": "Лутфан ин китобҳоро он ҷо бубар ва монд."},
                {"speaker": "B", "zh": "好，先把大书搬过去，再拿小书。", "pinyin": "Hǎo, xiān bǎ dà shū bān guò qù, zài ná xiǎo shū.", "uz": "Yaxshi, avval katta kitoblarni ko'chirib, keyin kichik kitoblarni olaman.", "ru": "Хорошо, сначала перенесу большие книги, потом возьму маленькие.", "tj": "Хуб, аввал китобҳои калонро мебарам, баъд китобҳои хурдро мегирам."},
                {"speaker": "A", "zh": "像这样摆，漂亮多了！", "pinyin": "Xiàng zhèyàng bǎi, piàoliang duō le!", "uz": "Shunday joylashtiring, ancha chiroyliroq bo'ladi!", "ru": "Расставь вот так, будет намного красивее!", "tj": "Ин тавр бичинед, хеле зебтар мешавад!"},
                {"speaker": "B", "zh": "好的，然后把桌子擦干净！", "pinyin": "Hǎo de, ránhòu bǎ zhuōzi cā gānjìng!", "uz": "Yaxshi, so'ng stolni artib tozalaymiz!", "ru": "Хорошо, потом протрём стол до чистоты!", "tj": "Хуб, сипас мизро тоза мекунем!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Mehmonlarni qabul qilishga tayyorlanish", "ru": "Подготовка к приёму гостей", "tj": "Омодагӣ барои пазироии меҳмонон"},
            "dialogue": [
                {"speaker": "A", "zh": "客人快来了，你把椅子搬过来吧。", "pinyin": "Kèrén kuài lái le, nǐ bǎ yǐzi bān guò lái ba.", "uz": "Mehmonlar tez keladi, stullarni bu yerga ko'chirib keling.", "ru": "Гости скоро придут, принеси стулья сюда.", "tj": "Меҳмонон зуд меоянд, курсиҳоро ин ҷо биёр."},
                {"speaker": "B", "zh": "好，像上次那样准备，还是有什么不同？", "pinyin": "Hǎo, xiàng shàng cì nàyàng zhǔnbèi, háishi yǒu shénme bùtóng?", "uz": "Yaxshi, o'tgan safar kabi tayyorlaymizmi, yoki farq bormi?", "ru": "Хорошо, готовить как в прошлый раз или что-то по-другому?", "tj": "Хуб, ба монанди дафъаи гузашта тайёр мекунем, ё фарке ҳаст?"},
                {"speaker": "A", "zh": "先把饮料放到桌上，然后把水果摆好。", "pinyin": "Xiān bǎ yǐnliào fàng dào zhuō shàng, ránhòu bǎ shuǐguǒ bǎi hǎo.", "uz": "Avval ichimliklarni stolga qo'ying, so'ng mevalarni joylashtiring.", "ru": "Сначала поставь напитки на стол, затем расставь фрукты.", "tj": "Аввал нӯшокиҳоро ба болои миз гузоред, сипас меваҳоро мечинем."},
                {"speaker": "B", "zh": "明白了，马上就好！", "pinyin": "Míngbái le, mǎshàng jiù hǎo!", "uz": "Tushundim, hoziroq tayyor bo'ladi!", "ru": "Понял, сейчас всё будет готово!", "tj": "Фаҳмидам, ҳозир тайёр мешавад!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "把字句③：把 + O + V + 结果补语/趋向补语",
            "title_uz": "把-konstruktsiyasi③: 把 + OB + F + natija/yo'nalish to'ldiruvchisi",
            "title_ru": "Конструкция 把③: 把 + объект + Гл + результатное/направленное дополнение",
            "title_tj": "Сохтори 把③: 把 + объект + Ф + пуркунандаи натиҷа/самт",
            "rule_uz": "'把'-konstruktsiyasida fe'ldan keyin natija to'ldiruvchisi (好、完、干净、成 kabi) yoki yo'nalish to'ldiruvchisi (过来、过去、进来 kabi) keladi. Bu harakatning natijasini yoki yo'nalishini ta'kidlaydi.",
            "rule_ru": "В конструкции '把' после глагола следует результатное дополнение (好、完、干净、成 и т.д.) или направленное дополнение (过来、过去、进来 и т.д.). Это акцентирует результат или направление действия.",
            "rule_tj": "Дар сохтори '把' баъди феъл пуркунандаи натиҷа (好、完、干净、成 ва ғайра) ё пуркунандаи самт (过来、过去、进来 ва ғайра) меояд. Ин натиҷа ё самти амалро таъкид мекунад.",
            "examples": [
                {"zh": "把苹果洗干净了！", "pinyin": "Bǎ píngguǒ xǐ gānjìng le!", "uz": "Olmani yaxshilab yuvib!", "ru": "Тщательно помой яблоки!", "tj": "Себро хуб бишӯй!"},
                {"zh": "你把水果拿过来。", "pinyin": "Nǐ bǎ shuǐguǒ ná guò lái.", "uz": "Mevalarni bu yerga olib keling.", "ru": "Принеси фрукты сюда.", "tj": "Меваҳоро ин ҷо биёр."}
            ]
        },
        {
            "no": 2,
            "title_zh": "先……再/又……然后……",
            "title_uz": "Avval……keyin/yana……so'ng……",
            "title_ru": "Сначала……потом/снова……затем……",
            "title_tj": "Аввал……баъд/боз……сипас……",
            "rule_uz": "'先…再…然后…' tuzilmasi bir nechta harakatning ketma-ketligini bildiradi. '先' = avval, '再' = keyin (shu sub'ekt bajaradi), '然后' = so'ng, keyingi qadam. '先…再…' = A dan keyin B.",
            "rule_ru": "Конструкция '先…再…然后…' выражает последовательность нескольких действий. '先' = сначала, '再' = потом (тот же субъект), '然后' = затем, следующий шаг. '先…再…' = A, потом B.",
            "rule_tj": "Сохтори '先…再…然后…' пайдарпаии чанд амалро ифода мекунад. '先' = аввал, '再' = баъд (ҳамон мубтадо), '然后' = сипас, қадами навбатӣ. '先…再…' = A, баъд B.",
            "examples": [
                {"zh": "先把肉切了，再放油，然后加蔬菜。", "pinyin": "Xiān bǎ ròu qiē le, zài fàng yóu, ránhòu jiā shūcài.", "uz": "Avval go'shtni kesing, keyin yog' soling, so'ng sabzavot qo'shing.", "ru": "Сначала нарежьте мясо, потом добавьте масло, затем положите овощи.", "tj": "Аввал гӯштро буред, баъд равған рехта, сипас сабзавот илова кунед."},
                {"zh": "先洗手，再吃饭。", "pinyin": "Xiān xǐ shǒu, zài chī fàn.", "uz": "Avval qo'l yuvib, keyin ovqat ye.", "ru": "Сначала вымой руки, потом ешь.", "tj": "Аввал дастро бишӯй, баъд хӯрок бихӯр."}
            ]
        },
        {
            "no": 3,
            "title_zh": "像……一样（比较/描述）",
            "title_uz": "Xuddi……kabi (taqqoslash/tavsif)",
            "title_ru": "Как/Словно……（сравнение/описание）",
            "title_tj": "Ба монанди……（муқоиса/тавсиф）",
            "rule_uz": "'像…一样' tuzilmasi ikki narsani taqqoslash yoki o'xshatish uchun ishlatiladi. '像+narsA+一样+sifat/fe'l'. 'A跟B一样' bilan o'xshash, lekin ko'proq tasvir uchun ishlatiladi.",
            "rule_ru": "Конструкция '像…一样' используется для сравнения двух вещей или описания. '像+предметA+一样+прилагательное/глагол'. Похоже на 'A跟B一样', но чаще используется для описания.",
            "rule_tj": "Сохтори '像…一样' барои муқоисаи ду чиз ё тавсиф истифода мешавад. '像+чизиА+一样+сифат/феъл'. Ба 'A跟B一样' монанд аст, аммо бештар барои тавсиф истифода мешавад.",
            "examples": [
                {"zh": "像你这样做，肯定很好吃！", "pinyin": "Xiàng nǐ zhèyàng zuò, kěndìng hěn hǎochī!", "uz": "Sizning usulda pishirsam, albatta juda mazali bo'ladi!", "ru": "Если готовить так, как ты, обязательно будет вкусно!", "tj": "Агар ба монанди шумо пазем, албатта хеле хушмаза мешавад!"},
                {"zh": "她唱歌像专业歌手一样好。", "pinyin": "Tā chànggē xiàng zhuānyè gēshǒu yīyàng hǎo.", "uz": "U qo'shiq aytishi professional qo'shiqchi kabi yaxshi.", "ru": "Она поёт так же хорошо, как профессиональный певец.", "tj": "Вай суруд хондани профессионал хонандаро монанд хуб аст."}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Mevalarni bu yerga olib keling.", "ru": "Принеси фрукты сюда.", "tj": "Меваҳоро ин ҷо биёр."},
                {"no": 2, "uz": "Avval qo'l yuvib, keyin ovqat ye.", "ru": "Сначала вымой руки, потом ешь.", "tj": "Аввал дастро бишӯй, баъд хӯрок бихӯр."},
                {"no": 3, "uz": "Olmani yaxshilab yuving!", "ru": "Тщательно помой яблоки!", "tj": "Себро хуб бишӯй!"},
                {"no": 4, "uz": "Sizning usulda pishirsam, albatta juda mazali bo'ladi!", "ru": "Если готовить так, как ты, обязательно будет вкусно!", "tj": "Агар ба монанди шумо пазем, албатта хеле хушмаза мешавад!"},
                {"no": 5, "uz": "Avval go'shtni kesing, keyin yog' soling, so'ng sabzavot qo'shing.", "ru": "Сначала нарежьте мясо, потом масло, затем овощи.", "tj": "Аввал гӯштро буред, баъд равған рехта, сипас сабзавот илова кунед."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "你把水果___过来。", "sentence_uz": "Mevalarni bu yerga ___ keling.", "sentence_ru": "Принеси фрукты ___.", "sentence_tj": "Меваҳоро ин ҷо ___.", "hint": "拿"},
                {"no": 2, "sentence_zh": "___把苹果洗干净，___切，___摆好。", "sentence_uz": "___ olmani yuvib, ___ kesib, ___ terish kerak.", "sentence_ru": "___ помой яблоки, ___ режь, ___ разложи.", "sentence_tj": "___ себро бишӯй, ___ бур, ___ бичин.", "hint": "先…再…然后"},
                {"no": 3, "sentence_zh": "___你这样做，肯定很好吃！", "sentence_uz": "___ sizning usulda, albatta mazali bo'ladi!", "sentence_ru": "___ так, как ты, обязательно вкусно!", "sentence_tj": "___ шумо ин тавр, албатта хушмаза!", "hint": "像"},
                {"no": 4, "sentence_zh": "先洗手，___吃饭。", "sentence_uz": "Avval qo'l yuving, ___ ovqat ye.", "sentence_ru": "Сначала вымой руки, ___ ешь.", "sentence_tj": "Аввал дастро бишӯй, ___ хӯрок бихӯр.", "hint": "再"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "先把饮料放到桌上，然后把水果摆好。", "pinyin": "Xiān bǎ yǐnliào fàng dào zhuō shàng, ránhòu bǎ shuǐguǒ bǎi hǎo."},
                {"no": 2, "zh": "她唱歌像专业歌手一样好。", "pinyin": "Tā chànggē xiàng zhuānyè gēshǒu yīyàng hǎo."}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "你把水果拿过来。"},
                {"no": 2, "zh": "先洗手，再吃饭。"},
                {"no": 3, "zh": "把苹果洗干净！"},
                {"no": 4, "zh": "像你这样做，肯定很好吃！"},
                {"no": 5, "zh": "先把肉切了，再放油，然后加蔬菜。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "拿"},
                {"no": 2, "answer": "先…再…然后"},
                {"no": 3, "answer": "像"},
                {"no": 4, "answer": "再"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Avval ichimliklarni stolga qo'ying, so'ng mevalarni joylashtiring.", "ru": "Сначала поставь напитки на стол, затем расставь фрукты.", "tj": "Аввал нӯшокиҳоро ба болои миз гузоред, сипас меваҳоро мечинем."},
                {"no": 2, "uz": "U qo'shiq aytishi professional qo'shiqchi kabi yaxshi.", "ru": "Она поёт так же хорошо, как профессиональный певец.", "tj": "Вай суруд хондани профессионал хонандаро монанд хуб аст."}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'先…再…然后…' tuzilmasidan foydalanib, taom tayyorlash yoki biror ish bajarish tartibini 1 ta porsiya yozib bering (kamida 3 qadam).", "ru": "Опишите порядок приготовления блюда или выполнения какого-либо дела, используя '先…再…然后…' (минимум 3 шага).", "tj": "Тартиби пухтани хӯрок ё анҷом додани кореро бо '先…再…然后…' тасвир кунед (ақаллан 3 қадам)."},
        {"task_no": 2, "uz": "'把+V+натija' va '像…一样' tuzilmalarini ishlatib, uyni tartibga solish haqida 4 ta jumla yozing.", "ru": "Напишите 4 предложения об уборке дома, используя '把+V+результат' и '像…一样'.", "tj": "4 ҷумла дар бораи тартиб додани хона бо '把+V+натиҷа' ва '像…一样' нависед."}
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
