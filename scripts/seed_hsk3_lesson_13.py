import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 13,
    "lesson_code": "HSK3-L13",
    "title": json.dumps({"zh": "我是走回来的", "uz": "Men piyoda qaytib keldim", "ru": "Я вернулся пешком", "tj": "Ман пиёда баргаштам"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "Murakkab yo'nalish to'ldiruvchisi, 'bir vaqtda ikki ish' va '是……的' ta'kidlovchi gaplar", "ru": "Сложные направленные дополнения, 'два действия одновременно' и выделительная конструкция '是……的'", "tj": "Пуркунандаи самти мураккаб, 'ду амал ҳамзамон' ва ҷумлаи таъкидии '是……的'"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda murakkab yo'nalish to'ldiruvchilarini (回来、过去、进来 kabilar), '一边…一边…' tuzilmasini va o'tmishdagi harakatni ta'kidlovchi '是……的' gaplarini o'rganamiz.", "ru": "В этом уроке мы изучим сложные направленные дополнения (回来、过去、进来 и другие), конструкцию '一边…一边…' и выделительную конструкцию '是……的' для акцентирования в прошлом.", "tj": "Дар ин дарс мо пуркунандаҳои мураккаби самтӣ (回来、过去、进来 ва ғайра), сохтори '一边…一边…' ва ҷумлаи таъкидии '是……的' барои таъкид дар гузаштаро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "走", "pinyin": "zǒu", "pos": "v", "uz": "yurmoq, piyoda bormoq", "ru": "ходить, идти пешком", "tj": "рафтан, пиёда рафтан"},
        {"no": 2, "zh": "回来", "pinyin": "huí lái", "pos": "v", "uz": "qaytib kelmoq", "ru": "вернуться", "tj": "баргаштан"},
        {"no": 3, "zh": "过去", "pinyin": "guò qù", "pos": "v", "uz": "o'tib ketmoq, bormoq (u yerga)", "ru": "пройти туда, пройти мимо", "tj": "гузаштан, рафтан (он тараф)"},
        {"no": 4, "zh": "进来", "pinyin": "jìn lái", "pos": "v", "uz": "kirib kelmoq", "ru": "входить (сюда)", "tj": "даромадан (ин ҷо)"},
        {"no": 5, "zh": "出去", "pinyin": "chū qù", "pos": "v", "uz": "chiqib ketmoq", "ru": "выходить (туда)", "tj": "баромадан (он ҷо)"},
        {"no": 6, "zh": "一边", "pinyin": "yībiān", "pos": "adv", "uz": "bir vaqtda, ayni paytda", "ru": "одновременно, в то же время", "tj": "ҳамзамон, дар ҳамон вақт"},
        {"no": 7, "zh": "唱歌", "pinyin": "chànggē", "pos": "v", "uz": "qo'shiq aytmoq", "ru": "петь (песню)", "tj": "суруд хондан"},
        {"no": 8, "zh": "跳舞", "pinyin": "tiàowǔ", "pos": "v", "uz": "raqsga tushmoq", "ru": "танцевать", "tj": "рақс кардан"},
        {"no": 9, "zh": "骑", "pinyin": "qí", "pos": "v", "uz": "minmoq (velosiped, ot)", "ru": "ехать верхом (на велосипеде, лошади)", "tj": "савор шудан (ба велосипед, асп)"},
        {"no": 10, "zh": "自行车", "pinyin": "zìxíngchē", "pos": "n", "uz": "velosiped", "ru": "велосипед", "tj": "велосипед"},
        {"no": 11, "zh": "坐", "pinyin": "zuò", "pos": "v", "uz": "o'tirmoq; (transport bilan) bormoq", "ru": "сидеть; ехать (на транспорте)", "tj": "нишастан; рафтан (бо нақлиёт)"},
        {"no": 12, "zh": "地铁", "pinyin": "dìtiě", "pos": "n", "uz": "metro", "ru": "метро", "tj": "метро"},
        {"no": 13, "zh": "方式", "pinyin": "fāngshì", "pos": "n", "uz": "usul, yo'l", "ru": "способ, метод", "tj": "усул, роҳ"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Qanday qaytib keldingiz?", "ru": "Как ты вернулся?", "tj": "Чӣ тавр баргаштед?"},
            "dialogue": [
                {"speaker": "A", "zh": "你是怎么回来的？", "pinyin": "Nǐ shì zěnme huílái de?", "uz": "Siz qanday qaytib keldingiz?", "ru": "Как ты вернулся?", "tj": "Шумо чӣ тавр баргаштед?"},
                {"speaker": "B", "zh": "我是走回来的，天气太好了！", "pinyin": "Wǒ shì zǒu huílái de, tiānqì tài hǎo le!", "uz": "Men piyoda qaytib keldim, havo juda yaxshi edi!", "ru": "Я вернулся пешком, погода была такая хорошая!", "tj": "Ман пиёда баргаштам, ҳаво хеле хуб буд!"},
                {"speaker": "A", "zh": "真的吗？多远啊？", "pinyin": "Zhēn de ma? Duō yuǎn a?", "uz": "Chinmi? Qanchalik uzoq?", "ru": "Правда? Как далеко?", "tj": "Ростан? Чӣ қадар дур?"},
                {"speaker": "B", "zh": "不太远，大概三十分钟的路。你是坐地铁来的吗？", "pinyin": "Bú tài yuǎn, dàgài sānshí fēnzhōng de lù. Nǐ shì zuò dìtiě lái de ma?", "uz": "Juda uzoq emas, taxminan o'ttiz daqiqalik yo'l. Siz metroda keldingizmi?", "ru": "Не очень далеко, примерно тридцать минут ходьбы. Ты приехал на метро?", "tj": "На хеле дур, тахминан сӣ дақиқа роҳ. Шумо бо метро омадед?"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Transport vositalari haqida", "ru": "О транспорте", "tj": "Дар бораи нақлиёт"},
            "dialogue": [
                {"speaker": "A", "zh": "我是坐公共汽车来的，你呢？", "pinyin": "Wǒ shì zuò gōnggòng qìchē lái de, nǐ ne?", "uz": "Men avtobus bilan keldim, siz-chi?", "ru": "Я приехал на автобусе, а ты?", "tj": "Ман бо автобус омадам, шумо чӣ?"},
                {"speaker": "B", "zh": "我是骑自行车来的，锻炼身体！", "pinyin": "Wǒ shì qí zìxíngchē lái de, duànliàn shēntǐ!", "uz": "Men velosipedda keldim, jismoniy mashqq!", "ru": "Я приехал на велосипеде, упражнение для тела!", "tj": "Ман бо велосипед омадам, варзиш!"},
                {"speaker": "A", "zh": "太好了！我也想骑自行车来上班。", "pinyin": "Tài hǎo le! Wǒ yě xiǎng qí zìxíngchē lái shàngbān.", "uz": "Zo'r! Men ham velosipedda ishga kelishni xohlardim.", "ru": "Отлично! Я тоже хочу приезжать на работу на велосипеде.", "tj": "Олӣ! Ман ҳам мехоҳам бо велосипед ба кор оям."},
                {"speaker": "B", "zh": "来吧！一边骑车一边看风景，很舒服！", "pinyin": "Lái ba! Yībiān qí chē yībiān kàn fēngjǐng, hěn shūfu!", "uz": "Keling! Bir vaqtda velosiped minib manzarani tomosha qilish, juda yoqimli!", "ru": "Давай! Одновременно едешь на велосипеде и смотришь на пейзаж, очень приятно!", "tj": "Биё! Ҳамзамон велосипед мекашед ва манзараро тамошо мекунед, хеле дилнишин!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Bir vaqtda ikki ish qilish", "ru": "Делать два дела одновременно", "tj": "Анҷом додани ду кор ҳамзамон"},
            "dialogue": [
                {"speaker": "A", "zh": "你喜欢一边做什么一边学习？", "pinyin": "Nǐ xǐhuān yībiān zuò shénme yībiān xuéxí?", "uz": "Siz nima qila turib o'qishni yaxshi ko'rasiz?", "ru": "Что ты любишь делать одновременно с учёбой?", "tj": "Шумо чиро ҳамзамон бо таҳсил карданро дӯст доред?"},
                {"speaker": "B", "zh": "我喜欢一边听音乐一边做作业。", "pinyin": "Wǒ xǐhuān yībiān tīng yīnyuè yībiān zuò zuòyè.", "uz": "Men musiqa tinglab uy vazifasini yaxshi ko'raman.", "ru": "Мне нравится слушать музыку и одновременно делать домашнюю работу.", "tj": "Ман дӯст медорам ҳамзамон мусиқӣ гӯш кунам ва вазифаи хонагиро анҷом диҳам."},
                {"speaker": "A", "zh": "我也是！我一边唱歌一边做家务。", "pinyin": "Wǒ yě shì! Wǒ yībiān chànggē yībiān zuò jiāwù.", "uz": "Men ham! Men qo'shiq aytib uy ishlarini qilaman.", "ru": "Я тоже! Я пою и одновременно делаю домашние дела.", "tj": "Ман ҳам! Ман суруд мехонам ва ҳамзамон кори хонаро мекунам."},
                {"speaker": "B", "zh": "哈哈，我们一边跳舞一边收拾房间吧！", "pinyin": "Hāhā, wǒmen yībiān tiàowǔ yībiān shōushi fángjiān ba!", "uz": "Xaxa, biz raqsga tushib xonani tartibga solaylik!", "ru": "Хахаха, давай одновременно танцевать и убирать комнату!", "tj": "Ҳаҳаҳа, биё ҳамзамон рақс кунем ва хонаро тартиб диҳем!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Sinfga kirish usuli", "ru": "Способ прихода на урок", "tj": "Усули омадан ба дарс"},
            "dialogue": [
                {"speaker": "A", "zh": "你是什么时候进来的？没看见你！", "pinyin": "Nǐ shì shénme shíhou jìnlái de? Méi kànjian nǐ!", "uz": "Siz qachon kirdingiz? Seni ko'rmadim!", "ru": "Когда ты вошёл? Я тебя не видел!", "tj": "Шумо кай даромадед? Ман шуморо надидам!"},
                {"speaker": "B", "zh": "我是悄悄进来的，不想打扰你们。", "pinyin": "Wǒ shì qiāoqiāo jìnlái de, bù xiǎng dǎrǎo nǐmen.", "uz": "Men jimgina kirdim, sizlarni bezovta qilmoqchi emas edim.", "ru": "Я вошёл тихо, не хотел вас беспокоить.", "tj": "Ман оромона даромадам, намехостам шуморо халал расонам."},
                {"speaker": "A", "zh": "没关系，下次直接进来就行了！", "pinyin": "Méi guānxi, xià cì zhíjiē jìnlái jiù xíng le!", "uz": "Hech gap emas, keyingi safar to'g'ri kiravering!", "ru": "Ничего, в следующий раз просто заходи!", "tj": "Майлаш, дафъаи дигар мустақиман биё даром!"},
                {"speaker": "B", "zh": "好的，谢谢！", "pinyin": "Hǎo de, xièxie!", "uz": "Yaxshi, rahmat!", "ru": "Хорошо, спасибо!", "tj": "Хуб, раҳмат!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "复合趋向补语",
            "title_uz": "Murakkab yo'nalish to'ldiruvchisi",
            "title_ru": "Сложное направленное дополнение",
            "title_tj": "Пуркунандаи мураккаби самтӣ",
            "rule_uz": "Murakkab yo'nalish to'ldiruvchisi ikki qismdan iborat: yo'nalish fe'li (上、下、进、出、回、过、起) + 来 yoki 去. Masalan: 回来 = qaytib kelmoq, 进去 = kirib ketmoq, 出来 = chiqib kelmoq.",
            "rule_ru": "Сложное направленное дополнение состоит из двух частей: глагол направления (上、下、进、出、回、过、起) + 来 или 去. Например: 回来 = вернуться (сюда), 进去 = войти (туда), 出来 = выйти (сюда).",
            "rule_tj": "Пуркунандаи мураккаби самтӣ аз ду қисм иборат аст: феъли самт (上、下、进、出、回、过、起) + 来 ё 去. Масалан: 回来 = баргаштан (ин ҷо), 进去 = даромадан (он ҷо), 出来 = баромадан (ин ҷо).",
            "examples": [
                {"zh": "他走进来了。", "pinyin": "Tā zǒu jìn lái le.", "uz": "U yurib kirib keldi.", "ru": "Он вошёл пешком.", "tj": "Вай пиёда даромад."},
                {"zh": "她跑出去了。", "pinyin": "Tā pǎo chū qù le.", "uz": "U yugurib chiqib ketdi.", "ru": "Она выбежала (туда).", "tj": "Вай давон баромад (он ҷо)."}
            ]
        },
        {
            "no": 2,
            "title_zh": "一边……一边……",
            "title_uz": "Bir vaqtda A qila turib B qilmoq",
            "title_ru": "Одновременно делать A и B",
            "title_tj": "Ҳамзамон A ва B кардан",
            "rule_uz": "'一边…一边…' tuzilmasi ikki harakatning bir vaqtda bajarilishini bildiradi. Ikki fe'l ham bir xil sub'ektga tegishli bo'lishi kerak. Masalan: 一边听音乐一边看书 = musiqa tinglab kitob o'qimoq.",
            "rule_ru": "Конструкция '一边…一边…' выражает два действия, выполняемых одновременно. Оба глагола относятся к одному подлежащему. Например: 一边听音乐一边看书 = слушать музыку и читать книгу одновременно.",
            "rule_tj": "Сохтори '一边…一边…' ду амали ҳамзаманро ифода мекунад. Ҳарду феъл ба як мубтадо тааллуқ доранд. Масалан: 一边听音乐一边看书 = ҳамзамон мусиқӣ гӯш кардан ва китоб хондан.",
            "examples": [
                {"zh": "我喜欢一边听音乐一边做作业。", "pinyin": "Wǒ xǐhuān yībiān tīng yīnyuè yībiān zuò zuòyè.", "uz": "Men musiqa tinglab uy vazifasini yaxshi ko'raman.", "ru": "Мне нравится слушать музыку и одновременно делать домашнее задание.", "tj": "Ман дӯст медорам ҳамзамон мусиқӣ гӯш кунам ва вазифаи хонагиро анҷом диҳам."},
                {"zh": "他一边唱歌一边跳舞。", "pinyin": "Tā yībiān chànggē yībiān tiàowǔ.", "uz": "U qo'shiq ayta turib raqsga tushmoqda.", "ru": "Он поёт и одновременно танцует.", "tj": "Вай ҳамзамон суруд мехонад ва рақс мекунад."}
            ]
        },
        {
            "no": 3,
            "title_zh": "是……的（强调过去动作的方式/时间/地点）",
            "title_uz": "是……的 (o'tgan harakat usuli/vaqti/joyini ta'kidlash)",
            "title_ru": "是……的 (акцент на способ/время/место прошлого действия)",
            "title_tj": "是……的 (таъкид бар усул/вақт/ҷойи амали гузашта)",
            "rule_uz": "'是……的' tuzilmasi o'tgan vaqtda yuz bergan harakatning QANday (usul), QACHON (vaqt) yoki QAERDA (joy) bo'lganini ta'kidlash uchun ishlatiladi. Ob'ekt ko'pincha 的 bilan 是 o'rtasida keladi.",
            "rule_ru": "Конструкция '是……的' используется для акцентирования КАК (способ), КОГДА (время) или ГДЕ (место) произошло прошлое действие. Объект часто стоит между 的 и 是.",
            "rule_tj": "Сохтори '是……的' барои таъкид бар ЧӢ ТАВРа (усул), КАЙ (вақт) ё ДАР КУҶо (ҷой) рух додани амали гузашта истифода мешавад. Объект аксаран байни 的 ва 是 меояд.",
            "examples": [
                {"zh": "我是走回来的。", "pinyin": "Wǒ shì zǒu huílái de.", "uz": "Men piyoda qaytib keldim. (usul ta'kidlangan)", "ru": "Я вернулся пешком. (акцент на способ)", "tj": "Ман пиёда баргаштам. (таъкид бар усул)"},
                {"zh": "你是什么时候到的？", "pinyin": "Nǐ shì shénme shíhou dào de?", "uz": "Siz qachon keldingiz? (vaqt ta'kidlangan)", "ru": "Когда ты прибыл? (акцент на время)", "tj": "Шумо кай расидед? (таъкид бар вақт)"}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Men piyoda qaytib keldim.", "ru": "Я вернулся пешком.", "tj": "Ман пиёда баргаштам."},
                {"no": 2, "uz": "Men musiqa tinglab uy vazifasini yaxshi ko'raman.", "ru": "Мне нравится слушать музыку и одновременно делать домашнее задание.", "tj": "Ман дӯст медорам ҳамзамон мусиқӣ гӯш кунам ва вазифаи хонагиро анҷом диҳам."},
                {"no": 3, "uz": "U yurib kirib keldi.", "ru": "Он вошёл пешком.", "tj": "Вай пиёда даромад."},
                {"no": 4, "uz": "Siz qachon keldingiz?", "ru": "Когда ты прибыл?", "tj": "Шумо кай расидед?"},
                {"no": 5, "uz": "U qo'shiq ayta turib raqsga tushmoqda.", "ru": "Он поёт и одновременно танцует.", "tj": "Вай ҳамзамон суруд мехонад ва рақс мекунад."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "我___走回来___。", "sentence_uz": "Men piyoda qaytib ___.", "sentence_ru": "Я ___ пешком ___ вернулся.", "sentence_tj": "Ман ___ пиёда ___.", "hint": "是……的"},
                {"no": 2, "sentence_zh": "她___唱歌___跳舞。", "sentence_uz": "U qo'shiq ayta turib ___ raqsga tushmoqda.", "sentence_ru": "Она ___ поёт ___ танцует.", "sentence_tj": "Вай ___ суруд мехонад ___ рақс мекунад.", "hint": "一边……一边"},
                {"no": 3, "sentence_zh": "他走进___了。", "sentence_uz": "U yurib kirib ___.", "sentence_ru": "Он вошёл ___.", "sentence_tj": "Вай пиёда ___ даромад.", "hint": "来"},
                {"no": 4, "sentence_zh": "你是什么时候到___？", "sentence_uz": "Siz qachon keld___?", "sentence_ru": "Когда ты приб___?", "sentence_tj": "Шумо кай расид___?", "hint": "的"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "你是骑自行车来的还是坐地铁来的？", "pinyin": "Nǐ shì qí zìxíngchē lái de háishì zuò dìtiě lái de?"},
                {"no": 2, "zh": "我们一边跳舞一边唱歌，很开心！", "pinyin": "Wǒmen yībiān tiàowǔ yībiān chànggē, hěn kāixīn!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "我是走回来的。"},
                {"no": 2, "zh": "我喜欢一边听音乐一边做作业。"},
                {"no": 3, "zh": "他走进来了。"},
                {"no": 4, "zh": "你是什么时候到的？"},
                {"no": 5, "zh": "他一边唱歌一边跳舞。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "是……的"},
                {"no": 2, "answer": "一边……一边"},
                {"no": 3, "answer": "来"},
                {"no": 4, "answer": "的"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Siz velosipedda keldingizmi yoki metroda?", "ru": "Ты приехал на велосипеде или на метро?", "tj": "Шумо бо велосипед омадед ё бо метро?"},
                {"no": 2, "uz": "Biz raqsga tushib qo'shiq aytdik, juda quvondik!", "ru": "Мы танцевали и пели одновременно, было очень весело!", "tj": "Мо ҳамзамон рақс кардем ва суруд хондем, хеле хурсанд шудем!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'是……的' tuzilmasini ishlatib, bugun yoki kecha nima qilganingizni (qanday, qayerda, qachon) ta'kidlab 3 ta jumla yozing.", "ru": "Напишите 3 предложения с '是……的', акцентируя, как/где/когда вы что-то делали сегодня или вчера.", "tj": "3 ҷумла бо '是……的' нависед, таъкид бар усул/ҷой/вақти кардани чизе имрӯз ё дирӯз."},
        {"task_no": 2, "uz": "'一边…一边…' ishlatib, kundalik odatlaringizni ifodalab 4 ta jumla tuzing.", "ru": "Составьте 4 предложения с '一边…一边…', описывая свои повседневные привычки.", "tj": "4 ҷумла бо '一边…一边…' тартиб диҳед, тасвир кардани одатҳои ҳаррӯзаатон."}
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
