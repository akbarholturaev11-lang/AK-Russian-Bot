import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk3",
    "lesson_order": 1,
    "lesson_code": "HSK3-L01",
    "title": "周末你有什么打算",
    "goal": json.dumps({"uz": "Dam olish kunlari rejalari haqida gaplashish; 结果补语'好', '一……也/都+不/没……' va 那 bog'lovchisini o'zlashtirish.", "ru": "Говорить о планах на выходные; освоить результативное дополнение '好', конструкцию '一……也/都+不/没……' и союз 那.", "tj": "Сӯҳбат дар бораи нақшаҳои охири ҳафта; азхудкунии иловаи натиҷавии '好', сохтори '一……也/都+不/没……' ва пайвандаки 那."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda dam olish kunlari rejalari muhokama qilinadi. Maktab, uy, park va kafedagi suhbatlar orqali reja qilish, takliflar berish va inkor ifodalash ko'nikmasi shakllanadi. Asosiy grammatik mavzular: natija to'ldiruvchisi '好', '一……也/都+不/没……' inkor qolipi va 那 bog'lovchisi.", "ru": "В этом уроке обсуждаются планы на выходные дни. Навыки планирования, предложений и выражения отрицания формируются через диалоги в школе, дома, в парке и кафе. Основные грамматические темы: результативное дополнение '好', конструкция '一……也/都+不/没……' и союз 那.", "tj": "Дар ин дарс нақшаҳои охири ҳафта муҳокима карда мешавад. Малакаҳои нақша кашидан, пешниҳод кардан ва ифодаи инкор тавассути муколамаҳо дар мактаб, хона, боғ ва қаҳвахона ташаккул меёбанд. Мавзӯҳои асосии грамматикӣ: иловаи натиҷавии '好', сохтори '一……也/都+不/没……' ва пайвандаки 那."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "周末",  "pinyin": "zhōumò",   "pos": "n.",    "uz": "dam olish kuni, hafta oxiri",     "ru": "выходные дни, конец недели",       "tj": "охири ҳафта, рӯзҳои истироҳат"},
        {"no": 2,  "zh": "打算",  "pinyin": "dǎsuàn",   "pos": "v./n.", "uz": "reja qilmoq; reja, niyat",        "ru": "планировать; план, намерение",     "tj": "нақша кашидан; нақша, қасд"},
        {"no": 3,  "zh": "跟",    "pinyin": "gēn",      "pos": "prep.", "uz": "bilan (kimsa bilan)",              "ru": "с (кем-либо)",                     "tj": "бо (касе)"},
        {"no": 4,  "zh": "一直",  "pinyin": "yīzhí",    "pos": "adv.", "uz": "doimo, hamisha; to'g'ri",          "ru": "всё время, постоянно; прямо",      "tj": "ҳамеша, доимо; рост"},
        {"no": 5,  "zh": "游戏",  "pinyin": "yóuxì",    "pos": "n.",    "uz": "o'yin",                           "ru": "игра",                             "tj": "бозӣ"},
        {"no": 6,  "zh": "作业",  "pinyin": "zuòyè",    "pos": "n.",    "uz": "uy vazifasi",                     "ru": "домашнее задание",                 "tj": "вазифаи хонагӣ"},
        {"no": 7,  "zh": "着急",  "pinyin": "zháojí",   "pos": "adj.",  "uz": "tashvishlanmoq, xavotir olmoq",  "ru": "беспокоиться, нервничать",         "tj": "ташвиш кашидан, нигарон будан"},
        {"no": 8,  "zh": "复习",  "pinyin": "fùxí",     "pos": "v.",    "uz": "takrorlash (darsni), qayta o'qish","ru": "повторять (урок), повторение",    "tj": "такрор кардан (дарс)"},
        {"no": 9,  "zh": "南方",  "pinyin": "nánfāng",  "pos": "n.",    "uz": "janub, janubiy tomon",            "ru": "юг, южная сторона",                "tj": "ҷануб, тарафи ҷанубӣ"},
        {"no": 10, "zh": "面包",  "pinyin": "miànbāo",  "pos": "n.",    "uz": "non, bulka",                      "ru": "хлеб, булка",                      "tj": "нон, булка"},
        {"no": 11, "zh": "带",    "pinyin": "dài",      "pos": "v.",    "uz": "olib bormoq/kelmoq, olib yurmoq", "ru": "взять с собой, нести",             "tj": "бурдан, бо худ гирифтан"},
        {"no": 12, "zh": "地图",  "pinyin": "dìtú",     "pos": "n.",    "uz": "xarita",                          "ru": "карта",                            "tj": "харита"},
        {"no": 13, "zh": "准备",  "pinyin": "zhǔnbèi",  "pos": "v.",    "uz": "tayyorlamoq, tayyorgarlik ko'rmoq","ru": "готовить, готовиться",            "tj": "тайёр кардан, омода шудан"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Sinfxonada dars oxirida",
            "scene_ru": "В классе в конце урока",
            "scene_tj": "Дар синфхона дар охири дарс",
            "dialogue": [
                {"speaker": "A", "zh": "周末你有什么打算？", "pinyin": "Zhōumò nǐ yǒu shénme dǎsuàn?", "uz": "Dam olish kunlari nima qilmoqchisiz?", "ru": "Какие у тебя планы на выходные?", "tj": "Охири ҳафта чӣ нақша дорӣ?"},
                {"speaker": "B", "zh": "我打算先复习功课，然后跟朋友出去玩儿。", "pinyin": "Wǒ dǎsuàn xiān fùxí gōngkè, ránhòu gēn péngyou chūqù wánr.", "uz": "Avval darslarni takrorlash, keyin do'stlar bilan chiqib o'ynashni rejalashtirdim.", "ru": "Планирую сначала повторить уроки, потом выйти погулять с друзьями.", "tj": "Нақша дорам аввал дарсҳоро такрор кунам, сипас бо дӯстон берун равам бозӣ кунем."},
                {"speaker": "A", "zh": "那你星期六有没有时间？我们一起去公园吧。", "pinyin": "Nà nǐ xīngqīliù yǒu méiyǒu shíjiān? Wǒmen yīqǐ qù gōngyuán ba.", "uz": "Unday bo'lsa shanba kuni vaqting bormi? Birgalikda parka boraylik.", "ru": "Тогда у тебя есть время в субботу? Пойдём вместе в парк.", "tj": "Пас шанбе вақт дорӣ? Биёед якҷоя ба боғ равем."},
                {"speaker": "B", "zh": "好啊！几点出发？要带地图吗？", "pinyin": "Hǎo a! Jǐ diǎn chūfā? Yào dài dìtú ma?", "uz": "Yaxshi! Necha soatda jo'naymiz? Xarita olib borishimiz kerakmi?", "ru": "Хорошо! В котором часу выезжаем? Нужно брать карту?", "tj": "Хуб! Соати чанд ҳаракат мекунем? Харита гирифтан лозим аст?"},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Uyda oilaviy suhbat",
            "scene_ru": "Дома, семейный разговор",
            "scene_tj": "Дар хона, суҳбати оилавӣ",
            "dialogue": [
                {"speaker": "A", "zh": "妈妈，周末我能去朋友家玩儿吗？", "pinyin": "Māma, zhōumò wǒ néng qù péngyou jiā wánr ma?", "uz": "Oyi, dam olish kunlari do'stimnikiga borsammi?", "ru": "Мама, можно я в выходные пойду к другу домой?", "tj": "Модар, охири ҳафта метавонам ба хонаи дӯстам равам?"},
                {"speaker": "B", "zh": "作业做好了吗？一点儿都没做完，不能去。", "pinyin": "Zuòyè zuò hǎo le ma? Yīdiǎnr dōu méi zuòwán, bù néng qù.", "uz": "Uy vazifasi bajardingmi? Bir oz ham tugatmagan bo'lsang, borolmaysan.", "ru": "Домашнее задание сделано? Если не сделал ни капли, нельзя идти.", "tj": "Оё вазифаи хонагиро тайёр кардӣ? Агар каме ҳам тамом накарда бошӣ, рафта наметавонӣ."},
                {"speaker": "A", "zh": "都做好了！我一直在做，没玩儿游戏。", "pinyin": "Dōu zuò hǎo le! Wǒ yīzhí zài zuò, méi wánr yóuxì.", "uz": "Hammasini bajardim! Doimo ishlayotgan edim, o'yin o'ynamadim.", "ru": "Всё сделал! Я постоянно делал, не играл в игры.", "tj": "Ҳама тайёр! Ман доимо кор мекардам, бозӣ накардам."},
                {"speaker": "B", "zh": "好，那你去吧。记得早点儿回来。", "pinyin": "Hǎo, nà nǐ qù ba. Jìde zǎo diǎnr huílai.", "uz": "Xo'p, unda bor. Erta qaytishni yodda tut.", "ru": "Хорошо, тогда иди. Помни — вернись пораньше.", "tj": "Хуб, пас рав. Фаромӯш накун ки барвақт баргардӣ."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Kafeda ikkita do'st",
            "scene_ru": "В кафе, двое друзей",
            "scene_tj": "Дар қаҳвахона, ду дӯст",
            "dialogue": [
                {"speaker": "A", "zh": "你为什么着急？发生什么事了吗？", "pinyin": "Nǐ wèishénme zháojí? Fāshēng shénme shì le ma?", "uz": "Nima uchun tashvishlanayapsan? Nimadur bo'ldimi?", "ru": "Почему ты нервничаешь? Что-то случилось?", "tj": "Чаро ташвиш мекашӣ? Оё чизе шуд?"},
                {"speaker": "B", "zh": "我约了朋友在这儿见面，他一个电话也没打。", "pinyin": "Wǒ yuē le péngyou zài zhèr jiànmiàn, tā yī ge diànhuà yě méi dǎ.", "uz": "Do'stimni bu yerda uchrashishga chaqirgan edim, u bitta ham qo'ng'iroq qilmadi.", "ru": "Я договорился встретиться с другом здесь, он не позвонил ни разу.", "tj": "Ман бо дӯстам қарор гузоштам, ки инҷо вохӯрем, вай як занг ҳам назад."},
                {"speaker": "A", "zh": "别着急，他也许在路上。要不要我帮你准备面包？", "pinyin": "Bié zháojí, tā yěxǔ zài lùshang. Yào bú yào wǒ bāng nǐ zhǔnbèi miànbāo?", "uz": "Xavotir olma, u yo'lda bo'lsa kerak. Non tayyorlashga yordam beraymi?", "ru": "Не нервничай, он, наверное, в дороге. Хочешь, я помогу приготовить хлеб?", "tj": "Ташвиш накаш, вай шояд дар роҳ бошад. Оё мехоҳӣ ман ба тайёр кардани нон кӯмак кунам?"},
                {"speaker": "B", "zh": "谢谢，不用了。他来了！你看，他从南方来的。", "pinyin": "Xièxie, bú yòng le. Tā lái le! Nǐ kàn, tā cóng nánfāng lái de.", "uz": "Rahmat, kerak emas. U keldi! Qara, u janubdan kelgan.", "ru": "Спасибо, не нужно. Он пришёл! Смотри, он приехал с юга.", "tj": "Раҳмат, лозим нест. Вай омад! Бубин, вай аз ҷануб омадааст."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Parkda yurish paytida",
            "scene_ru": "На прогулке в парке",
            "scene_tj": "Ҳангоми гаштан дар боғ",
            "dialogue": [
                {"speaker": "A", "zh": "这个公园真大！你以前来过吗？", "pinyin": "Zhège gōngyuán zhēn dà! Nǐ yǐqián lái guo ma?", "uz": "Bu park juda katta! Avval kelgan bo'lganmisiz?", "ru": "Этот парк очень большой! Ты раньше приходил сюда?", "tj": "Ин боғ бисёр калон! Оё пеш омада будӣ?"},
                {"speaker": "B", "zh": "来过一次，但那时候一点儿都不了解这里。", "pinyin": "Lái guo yī cì, dàn nà shíhou yīdiǎnr dōu bù liǎojiě zhèlǐ.", "uz": "Bir marta kelgan edim, lekin o'shanda bu haqda hech nima bilmas edim.", "ru": "Приходил один раз, но тогда совсем ничего не знал об этом месте.", "tj": "Як бор омада будам, аммо он вақт ин ҷоро каме ҳам намешинохтам."},
                {"speaker": "A", "zh": "那我们带了地图，今天可以好好参观！", "pinyin": "Nà wǒmen dài le dìtú, jīntiān kěyǐ hǎohāo cānguān!", "uz": "Unday bo'lsa xarita oldik, bugun yaxshilab tomosha qilishimiz mumkin!", "ru": "Тогда мы взяли карту, сегодня можем хорошо осмотреться!", "tj": "Пас мо харита гирифтем, имрӯз метавонем хуб тамошо кунем!"},
                {"speaker": "B", "zh": "对！周末能跟好朋友一起出来，真开心！", "pinyin": "Duì! Zhōumò néng gēn hǎo péngyou yīqǐ chūlai, zhēn kāixīn!", "uz": "Ha to'g'ri! Dam olish kunida yaxshi do'st bilan birgalikda chiqish, rostdan ham quvonchli!", "ru": "Точно! Выйти в выходные вместе с хорошим другом — это так здорово!", "tj": "Дуруст! Охири ҳафта бо дӯсти хуб якҷоя баромадан, воқеан хурсандӣ аст!"},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "结果补语\"好\"",
            "title_uz": "Natija to'ldiruvchisi '好'",
            "title_ru": "Результативное дополнение «好»",
            "title_tj": "Иловаи натиҷавии «好»",
            "rule_uz": (
                "Fe'ldan keyin '好' keltirib, harakat muvaffaqiyatli yoki to'liq bajarilganligini bildiradi.\n"
                "Qolip: Fe'l + 好 + 了\n"
                "Masalan: 做好了 (bajardi/tamom qildi), 准备好了 (tayyorladi), 写好了 (yozib bo'ldi).\n"
                "Inkor shakli: 没+做好 (bajarmadi/tugallamadi)."
            ),
            "rule_ru": (
                "Частица '好' после глагола означает, что действие выполнено успешно или полностью.\n"
                "Структура: Глагол + 好 + 了\n"
                "Например: 做好了 (сделал/закончил), 准备好了 (приготовил), 写好了 (написал).\n"
                "Отрицание: 没+做好 (не сделал/не завершил)."
            ),
            "rule_tj": (
                "Зарраи '好' пас аз феъл нишон медиҳад, ки амал бомуваффақият ё пурра иҷро шудааст.\n"
                "Сохтор: Феъл + 好 + 了\n"
                "Масалан: 做好了 (иҷро кард), 准备好了 (тайёр кард), 写好了 (навишт).\n"
                "Инкор: 没+做好 (иҷро накард/тамом накард)."
            ),
            "examples": [
                {"zh": "作业都做好了！", "pinyin": "Zuòyè dōu zuò hǎo le!", "uz": "Barcha uy vazifalari bajarildi!", "ru": "Все домашние задания сделаны!", "tj": "Ҳамаи вазифаҳои хонагӣ иҷро шуд!"},
                {"zh": "我已经准备好了，可以出发了。", "pinyin": "Wǒ yǐjīng zhǔnbèi hǎo le, kěyǐ chūfā le.", "uz": "Men allaqachon tayyorlandim, jo'nashim mumkin.", "ru": "Я уже готов, можно выезжать.", "tj": "Ман аллакай омода шудам, метавонем ҳаракат кунем."},
            ]
        },
        {
            "no": 2,
            "title_zh": "\"一……也/都+不/没……\"表示否定",
            "title_uz": "'一……也/都+不/没……' — kuchli inkor",
            "title_ru": "Конструкция '一……也/都+不/没……' — усиленное отрицание",
            "title_tj": "Сохтори '一……也/都+不/没……' — инкори қавӣ",
            "rule_uz": (
                "Bu qolip 'hech bir...ham yo'q/emas' ma'nosini beradi — mutlaq inkorni ifodalaydi.\n"
                "Qolip: 一 + miqdor+ot + 也/都 + 不/没 + fe'l\n"
                "Masalan: 一个人也没来 (bitta kishi ham kelmadi)\n"
                "         一点儿都不想去 (zarra ham bormoqchi emasman)\n"
                "         一个电话也没打 (bitta qo'ng'iroq ham qilmadi)"
            ),
            "rule_ru": (
                "Конструкция выражает абсолютное отрицание: 'ни одного...даже нет'.\n"
                "Структура: 一 + числит.+сущ. + 也/都 + 不/没 + глагол\n"
                "Например: 一个人也没来 (никто не пришёл)\n"
                "          一点儿都不想去 (совсем не хочу идти)\n"
                "          一个电话也没打 (не позвонил ни разу)"
            ),
            "rule_tj": (
                "Ин сохтор инкори мутлақро ифода мекунад: 'ҳатто як...ҳам нест'.\n"
                "Сохтор: 一 + шумор+исм + 也/都 + 不/没 + феъл\n"
                "Масалан: 一个人也没来 (ҳатто як нафар ҳам наомад)\n"
                "         一点儿都不想去 (каме ҳам рафтан намехоҳам)\n"
                "         一个电话也没打 (ҳатто як занг ҳам назад)"
            ),
            "examples": [
                {"zh": "他一个电话也没打，我很着急。", "pinyin": "Tā yī ge diànhuà yě méi dǎ, wǒ hěn zháojí.", "uz": "U bitta ham qo'ng'iroq qilmadi, men juda tashvishlandim.", "ru": "Он ни разу не позвонил, я очень переживал.", "tj": "Вай ҳатто як занг ҳам назад, ман хеле нигарон шудам."},
                {"zh": "那天我一点儿都不想出去。", "pinyin": "Nà tiān wǒ yīdiǎnr dōu bù xiǎng chūqù.", "uz": "O'sha kuni zarra ham tashqariga chiqmoqchi emas edim.", "ru": "В тот день я совсем не хотел выходить.", "tj": "Он рӯз ман каме ҳам берун рафтан намехостам."},
            ]
        },
        {
            "no": 3,
            "title_zh": "连词\"那\"",
            "title_uz": "Bog'lovchi '那' (unday bo'lsa, unda)",
            "title_ru": "Союз «那» (тогда, в таком случае)",
            "title_tj": "Пайвандаки «那» (пас, дар он сурат)",
            "rule_uz": (
                "'那' bog'lovchisi oldingi gapdan kelib chiquvchi xulosani yoki qarorni kiritadi.\n"
                "Ma'nosi: 'unday bo'lsa, unda, bo'lmasa'\n"
                "Ko'pincha 那 + gap shaklida keladi, gapning boshida turadi.\n"
                "Masalan: 那我们明天去吧。(Unday bo'lsa ertaga boraylik.)\n"
                "         那你去吧。(Unda sen bor.)"
            ),
            "rule_ru": (
                "Союз '那' вводит вывод или решение, вытекающее из предыдущей реплики.\n"
                "Значение: 'тогда, в таком случае'\n"
                "Обычно стоит в начале предложения: 那 + предложение.\n"
                "Например: 那我们明天去吧。(Тогда пойдём завтра.)\n"
                "          那你去吧。(Тогда ты иди.)"
            ),
            "rule_tj": (
                "Пайвандаки '那' хулоса ё қарореро, ки аз гапи қаблӣ бармеояд, ворид мекунад.\n"
                "Маъно: 'пас, дар он сурат'\n"
                "Одатан дар аввали ҷумла меояд: 那 + ҷумла.\n"
                "Масалан: 那我们明天去吧。(Пас фардо равем.)\n"
                "         那你去吧。(Пас ту рав.)"
            ),
            "examples": [
                {"zh": "那你星期六有没有时间？我们一起去公园吧。", "pinyin": "Nà nǐ xīngqīliù yǒu méiyǒu shíjiān? Wǒmen yīqǐ qù gōngyuán ba.", "uz": "Unday bo'lsa shanba kuni vaqting bormi? Birgalikda parka boraylik.", "ru": "Тогда есть ли у тебя время в субботу? Пойдём вместе в парк.", "tj": "Пас шанбе вақт дорӣ? Биёед якҷоя ба боғ равем."},
                {"zh": "好，那你去吧。记得早点儿回来。", "pinyin": "Hǎo, nà nǐ qù ba. Jìde zǎo diǎnr huílai.", "uz": "Xo'p, unda bor. Erta qaytishni yodda tut.", "ru": "Хорошо, тогда иди. Помни — вернись пораньше.", "tj": "Хуб, пас рав. Фаромӯш накун ки барвақт баргардӣ."},
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
                {"prompt_uz": "dam olish kuni, hafta oxiri", "prompt_ru": "выходные дни", "prompt_tj": "охири ҳафта", "answer": "周末", "pinyin": "zhōumò"},
                {"prompt_uz": "reja qilmoq; reja", "prompt_ru": "планировать; план", "prompt_tj": "нақша кашидан; нақша", "answer": "打算", "pinyin": "dǎsuàn"},
                {"prompt_uz": "uy vazifasi", "prompt_ru": "домашнее задание", "prompt_tj": "вазифаи хонагӣ", "answer": "作业", "pinyin": "zuòyè"},
                {"prompt_uz": "tashvishlanmoq, xavotir olmoq", "prompt_ru": "беспокоиться, нервничать", "prompt_tj": "ташвиш кашидан, нигарон будан", "answer": "着急", "pinyin": "zháojí"},
                {"prompt_uz": "tayyorlamoq", "prompt_ru": "готовить, готовиться", "prompt_tj": "тайёр кардан", "answer": "准备", "pinyin": "zhǔnbèi"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (那、一直、一点儿都、做好):",
            "instruction_ru": "Вставьте подходящее слово (那、一直、一点儿都、做好):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (那、一直、一点儿都、做好):",
            "items": [
                {"prompt_uz": "作业______了！我可以出去玩儿了。", "prompt_ru": "作业______了！我可以出去玩儿了。", "prompt_tj": "作业______了！我可以出去玩儿了。", "answer": "做好", "pinyin": "zuò hǎo"},
                {"prompt_uz": "______你星期六有时间，我们一起去吧。", "prompt_ru": "______你星期六有时间，我们一起去吧。", "prompt_tj": "______你星期六有时间，我们一起去吧。", "answer": "那", "pinyin": "nà"},
                {"prompt_uz": "那天他______不想出来玩儿。", "prompt_ru": "那天他______不想出来玩儿。", "prompt_tj": "Он рӯз вай______намехост берун ояд бозӣ кунад.", "answer": "一点儿都", "pinyin": "yīdiǎnr dōu"},
                {"prompt_uz": "他______在等你，都等了一个小时了。", "prompt_ru": "Он______ждёт тебя, уже ждёт целый час.", "prompt_tj": "Вай______интизори ту аст, як соат шуд интизор мешавад.", "answer": "一直", "pinyin": "yīzhí"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "作业都做好了！我一直在做，没玩儿游戏。", "prompt_ru": "作业都做好了！我一直在做，没玩儿游戏。", "prompt_tj": "作业都做好了！我一直在做，没玩儿游戏。", "answer": "Barcha uy vazifalari bajarildi! Doimo ishlayotgan edim, o'yin o'ynamadim.", "pinyin": "Zuòyè dōu zuò hǎo le! Wǒ yīzhí zài zuò, méi wánr yóuxì."},
                {"prompt_uz": "他一个电话也没打，我很着急。", "prompt_ru": "他一个电话也没打，我很着急。", "prompt_tj": "他一个电话也没打，我很着急。", "answer": "U bitta ham qo'ng'iroq qilmadi, men juda tashvishlandim.", "pinyin": "Tā yī ge diànhuà yě méi dǎ, wǒ hěn zháojí."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["周末", "打算", "作业", "着急", "准备"]},
        {"no": 2, "answers": ["做好", "那", "一点儿都", "一直"]},
        {"no": 3, "answers": [
            "Barcha uy vazifalari bajarildi! Doimo ishlayotgan edim, o'yin o'ynamadim.",
            "U bitta ham qo'ng'iroq qilmadi, men juda tashvishlandim.",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'一……也/都+不/没……' qolipidan foydalanib 3 ta gap tuzing. Kundalik hayotdan misollar keltiring.",
            "instruction_ru": "Составьте 3 предложения с конструкцией '一……也/都+不/没……'. Приведите примеры из повседневной жизни.",
            "instruction_tj": "Бо истифода аз сохтори '一……也/都+不/没……' 3 ҷумла тартиб диҳед. Аз ҳаёти рӯзмарра мисол овардед.",
            "words": ["一点儿都", "一个人也", "一次也", "不想", "没来", "没打"],
            "topic_uz": "Dam olish kunlari nima qildingiz?",
            "topic_ru": "Что вы делали в выходные?",
            "topic_tj": "Охири ҳафта чӣ кардед?",
        },
        {
            "no": 2,
            "instruction_uz": "Dam olish kunlari rejangiz haqida 5-6 gapdan iborat qisqa matn yozing. 打算, 准备好, 那 so'zlarini ishlating.",
            "instruction_ru": "Напишите небольшой текст из 5–6 предложений о своих планах на выходные. Используйте слова 打算, 准备好, 那.",
            "instruction_tj": "Дар бораи нақшаҳои охири ҳафтаи худ матни хурде аз 5-6 ҷумла нависед. Калимаҳои 打算, 准备好, 那-ро истифода баред.",
            "topic_uz": "Mening dam olish kuni rejasi",
            "topic_ru": "Мои планы на выходные",
            "topic_tj": "Нақшаи охири ҳафтаи ман",
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
