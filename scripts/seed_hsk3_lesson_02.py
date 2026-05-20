import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk3",
    "lesson_order": 2,
    "lesson_code": "HSK3-L02",
    "title": "他什么时候回来",
    "goal": json.dumps({"uz": "Yo'nalish to'ldiruvchilari, ketma-ket harakatlar va ritorik so'roqlarni o'zlashtirish.", "ru": "Освоить направленные дополнения, последовательные действия и риторические вопросы.", "tj": "Азхудкунии иловаҳои самтнок, амалҳои пайдарпай ва саволҳои риторикӣ."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda kimningdir qaytib kelishini so'rash, ketma-ket harakatlarni ifodalash va qobiliyatga shubha bildirish o'rganiladi. Idora, ko'cha, bozor va uy muhitidagi suhbatlar orqali ko'nikmalar shakllanadi.", "ru": "В этом уроке изучается вопрос о возвращении кого-либо, выражение последовательных действий и сомнение в способности. Навыки формируются через диалоги в офисе, на улице, на рынке и дома.", "tj": "Дар ин дарс пурсидан дар бораи баргаштани касе, ифодаи амалҳои пайдарпай ва шубҳа дар қобилият омӯхта мешавад. Малакаҳо тавассути муколамаҳо дар идора, кӯча, бозор ва хона ташаккул меёбанд."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "腿",    "pinyin": "tuǐ",        "pos": "n.",   "uz": "oyoq (son va boldirdan iborat)",  "ru": "нога (бедро и голень)",          "tj": "по (аз ронак то пои по)"},
        {"no": 2,  "zh": "疼",    "pinyin": "téng",       "pos": "v.",   "uz": "og'riqli bo'lmoq, og'rimoq",     "ru": "болеть, быть болезненным",       "tj": "дард кардан, дарднок будан"},
        {"no": 3,  "zh": "脚",    "pinyin": "jiǎo",       "pos": "n.",   "uz": "oyoq (panja qismi)",              "ru": "нога (ступня, стопа)",           "tj": "по (пои по)"},
        {"no": 4,  "zh": "容易",  "pinyin": "róngyì",     "pos": "adj.", "uz": "oson, qo'lay",                   "ru": "лёгкий, несложный",              "tj": "осон, дастрас"},
        {"no": 5,  "zh": "难",    "pinyin": "nán",        "pos": "adj.", "uz": "qiyin, mushkul",                  "ru": "трудный, сложный",               "tj": "душвор, мушкил"},
        {"no": 6,  "zh": "太太",  "pinyin": "tàitai",     "pos": "n.",   "uz": "xotin, xonim (turmushga chiqqan)","ru": "жена, замужняя женщина",        "tj": "зан, хонум (шавҳардор)"},
        {"no": 7,  "zh": "经理",  "pinyin": "jīnglǐ",     "pos": "n.",   "uz": "menejer, direktor",               "ru": "менеджер, директор",             "tj": "мудир, директор"},
        {"no": 8,  "zh": "办公室","pinyin": "bàngōngshì", "pos": "n.",   "uz": "idora, ofis",                     "ru": "офис, кабинет",                  "tj": "идора, кабинет"},
        {"no": 9,  "zh": "楼",    "pinyin": "lóu",        "pos": "n./m.","uz": "bino, qavat",                     "ru": "здание, этаж",                   "tj": "бино, ошёна"},
        {"no": 10, "zh": "拿",    "pinyin": "ná",         "pos": "v.",   "uz": "olmoq, ko'tarmoq, ushlamoq",     "ru": "взять, держать, нести",          "tj": "гирифтан, бардоштан"},
        {"no": 11, "zh": "伞",    "pinyin": "sǎn",        "pos": "n.",   "uz": "soyabon",                         "ru": "зонт",                           "tj": "чатр"},
        {"no": 12, "zh": "胖",    "pinyin": "pàng",       "pos": "adj.", "uz": "semiz, to'la",                    "ru": "толстый, полный",                "tj": "фарбеҳ, чоқ"},
        {"no": 13, "zh": "瘦",    "pinyin": "shòu",       "pos": "adj.", "uz": "ozg'in, ingichka",                "ru": "худой, тонкий",                  "tj": "лоғар, борик"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Idorada hamkasb kutmoqda",
            "scene_ru": "В офисе, коллега ждёт",
            "scene_tj": "Дар идора, ҳамкор интизор мешавад",
            "dialogue": [
                {"speaker": "A", "zh": "请问，王经理什么时候回来？", "pinyin": "Qǐngwèn, Wáng jīnglǐ shénme shíhou huílai?", "uz": "Kechirasiz, Vang menejer qachon qaytib keladi?", "ru": "Извините, когда вернётся менеджер Ван?", "tj": "Бубахшед, мудир Ван кай бармегардад?"},
                {"speaker": "B", "zh": "他先去三楼办公室拿文件，马上就回来。", "pinyin": "Tā xiān qù sān lóu bàngōngshì ná wénjiàn, mǎshàng jiù huílai.", "uz": "U avval uchinchi qavatdagi idoraga hujjat olishga ketdi, hoziroq qaytadi.", "ru": "Он сначала пошёл в кабинет на третьем этаже за документами, сейчас вернётся.", "tj": "Вай аввал ба кабинети ошёнаи сеюм барои ҳуҷҷат рафт, ҳозир бармегардад."},
                {"speaker": "A", "zh": "好的，那我在这里等他。", "pinyin": "Hǎo de, nà wǒ zài zhèlǐ děng tā.", "uz": "Xo'p, unda men bu yerda uni kutaman.", "ru": "Хорошо, тогда я подожду его здесь.", "tj": "Хуб, пас ман инҷо интизораш мешавам."},
                {"speaker": "B", "zh": "请坐，他很快就回来了。", "pinyin": "Qǐng zuò, tā hěn kuài jiù huílai le.", "uz": "Marhamat o'tiring, u juda tez qaytadi.", "ru": "Присаживайтесь, он вернётся очень скоро.", "tj": "Биншинед, вай хеле зуд бармегардад."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Ko'chada yomg'irli kunda",
            "scene_ru": "На улице в дождливый день",
            "scene_tj": "Дар кӯча дар рӯзи борондор",
            "dialogue": [
                {"speaker": "A", "zh": "外边下雨了！你有没有带伞？", "pinyin": "Wàibiān xiàyǔ le! Nǐ yǒu méiyǒu dài sǎn?", "uz": "Tashqarida yomg'ir yog'yapti! Soyabon olib chiqdingmi?", "ru": "На улице дождь! Ты взял зонт?", "tj": "Берун борон мебарад! Оё чатр гирифтӣ?"},
                {"speaker": "B", "zh": "没带，我跑进去拿，你等我一下！", "pinyin": "Méi dài, wǒ pǎo jìnqu ná, nǐ děng wǒ yīxià!", "uz": "Olmadim, men yugurib kirib olib chiqaman, bir oz kutib turing!", "ru": "Не взял, я забегу и возьму, подождите меня!", "tj": "Нагирифтам, ман давида дохил мешавам ва мегирам, каме интизор шав!"},
                {"speaker": "A", "zh": "好，快点儿！这么多水，我的脚都湿了。", "pinyin": "Hǎo, kuài diǎnr! Zhème duō shuǐ, wǒ de jiǎo dōu shī le.", "uz": "Xo'p, tez bo'l! Shu qadar ko'p suv bor, oyog'im ho'l bo'lib ketdi.", "ru": "Хорошо, побыстрее! Столько воды, у меня уже ноги промокли.", "tj": "Хуб, зудтар! Ин қадар об ҳаст, пои ман ҳама тар шуд."},
                {"speaker": "B", "zh": "拿回来了！快上车吧，别站在雨里。", "pinyin": "Ná huílai le! Kuài shàng chē ba, bié zhàn zài yǔ lǐ.", "uz": "Olib keldim! Tezroq mashinaga chiqing, yomg'irda turmang.", "ru": "Принёс! Быстрее садитесь в машину, не стойте под дождём.", "tj": "Оvardам! Зудтар ба мошин нишин, дар борон наист."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Bozorda xarid qilayotganda",
            "scene_ru": "На рынке при покупках",
            "scene_tj": "Дар бозор ҳангоми харид",
            "dialogue": [
                {"speaker": "A", "zh": "这些东西这么多，你一个人能拿得了吗？", "pinyin": "Zhèxiē dōngxi zhème duō, nǐ yī ge rén néng ná de liǎo ma?", "uz": "Bu narsa-buyumlar juda ko'p, sen yolg'iz olib keta olasanmi?", "ru": "Столько вещей, ты один сможешь всё унести?", "tj": "Ин қадар чизҳо, оё ту танҳо ҳама гирифта метавонӣ?"},
                {"speaker": "B", "zh": "当然能！这有什么难的？你太太呢？", "pinyin": "Dāngrán néng! Zhè yǒu shénme nán de? Nǐ tàitai ne?", "uz": "Albatta, olaman! Buning nesi qiyin? Xotiningiz qani?", "ru": "Конечно, смогу! Что тут сложного? А ваша жена где?", "tj": "Албатта метавонам! Ин чӣ душворист? Ҳамсари шумо куҷост?"},
                {"speaker": "A", "zh": "她腿有点儿疼，先坐在那边了。", "pinyin": "Tā tuǐ yǒudiǎnr téng, xiān zuò zài nàbiān le.", "uz": "Uning oyog'i biroz og'riyapti, u tomonda o'tirib turdi.", "ru": "У неё немного болит нога, она пока сидит вон там.", "tj": "Пои ӯ каме дард мекунад, вай аввал он тараф нишаст."},
                {"speaker": "B", "zh": "容易胖、难减肥，我太太也一样！哈哈！", "pinyin": "Róngyì pàng, nán jiǎnféi, wǒ tàitai yě yīyàng! Hāhā!", "uz": "Semirish oson, ozish qiyin — mening xotinim ham shunday! Ha-ha!", "ru": "Полнеть легко, худеть трудно — у моей жены то же самое! Ха-ха!", "tj": "Фарбеҳ шудан осон, лоғар шудан душвор — ҳамсари ман ҳам ҳамин тавр! Ха-ха!"},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Uyda oilaviy suhbat",
            "scene_ru": "Дома, семейный разговор",
            "scene_tj": "Дар хона, суҳбати оилавӣ",
            "dialogue": [
                {"speaker": "A", "zh": "你看，我最近是不是瘦了一点儿？", "pinyin": "Nǐ kàn, wǒ zuìjìn shì bu shì shòu le yīdiǎnr?", "uz": "Qara, men so'nggi paytlarda biroz ozibmanmi?", "ru": "Смотри, я в последнее время немного похудел?", "tj": "Бубин, оё ман охирон каме лоғар шудам?"},
                {"speaker": "B", "zh": "嗯……好像是，但你以前太胖了！", "pinyin": "Ń……hǎoxiàng shì, dàn nǐ yǐqián tài pàng le!", "uz": "Hmm… shunday ko'rinadi, lekin oldin juda semiz bo'lgansiz!", "ru": "Хм… кажется, да, но раньше ты был слишком толстым!", "tj": "Хм... шояд, аммо пеш шумо хеле фарбеҳ будед!"},
                {"speaker": "A", "zh": "我每天都跑步，从楼上跑到楼下，一共跑十层！", "pinyin": "Wǒ měitiān dōu pǎobù, cóng lóu shàng pǎo dào lóu xià, yīgòng pǎo shí céng!", "uz": "Men har kuni yuguraman, yuqoridan pastga, jami o'n qavat!", "ru": "Я каждый день бегаю — с верхнего этажа до нижнего, всего десять этажей!", "tj": "Ман ҳар рӯз медавам, аз ошёнаи боло то поён, ҷамъ даҳ ошёна!"},
                {"speaker": "B", "zh": "这么多！难怪你瘦了！坚持下去！", "pinyin": "Zhème duō! Nánguài nǐ shòu le! Jiānchí xiàqù!", "uz": "Bu qadar ko'p! Shunday qilib ozibsiz! Davom eting!", "ru": "Так много! Неудивительно, что ты похудел! Продолжай!", "tj": "Ин қадар зиёд! Не ажаб ки лоғар шудӣ! Давом деҳ!"},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "简单趋向补语",
            "title_uz": "Oddiy yo'nalish to'ldiruvchisi",
            "title_ru": "Простые направленные дополнения",
            "title_tj": "Иловаҳои самтноки содда",
            "rule_uz": (
                "Yo'nalish to'ldiruvchilari fe'lga qo'shilgan 来 yoki 去 dan iborat.\n"
                "来 — harakat so'zlovchi tomonga yoki ma'lum nuqtaga qarab;\n"
                "去 — harakat so'zlovchidan yoki ma'lum nuqtadan uzoqlashipti.\n"
                "Qolip: V + 来/去\n"
                "Masalan: 回来 (qaytib kelmoq), 进去 (kirib ketmoq), 上来 (yuqoriga chiqib kelmoq),\n"
                "         拿回来 (olib qaytmoq), 跑进去 (yugurib kirib ketmoq)."
            ),
            "rule_ru": (
                "Направленные дополнения состоят из 来 или 去, присоединённых к глаголу.\n"
                "来 — движение к говорящему или к определённой точке;\n"
                "去 — движение от говорящего или от точки.\n"
                "Структура: Глагол + 来/去\n"
                "Например: 回来 (вернуться), 进去 (войти), 上来 (подняться),\n"
                "          拿回来 (принести обратно), 跑进去 (забежать)."
            ),
            "rule_tj": (
                "Иловаҳои самтнок аз 来 ё 去, ки ба феъл ҳамроҳ мешаванд, иборатанд.\n"
                "来 — ҳаракат ба сӯи гӯянда ё нуқтаи муайян;\n"
                "去 — ҳаракат аз гӯянда ё аз нуқта.\n"
                "Сохтор: Феъл + 来/去\n"
                "Масалан: 回来 (баргаштан), 进去 (дохил шудан), 上来 (боло омадан),\n"
                "         拿回来 (бо худ оварадан), 跑进去 (давида дохил шудан)."
            ),
            "examples": [
                {"zh": "他先去三楼拿文件，马上就回来。", "pinyin": "Tā xiān qù sān lóu ná wénjiàn, mǎshàng jiù huílai.", "uz": "U avval uchinchi qavatga hujjat olishga ketdi, hoziroq qaytadi.", "ru": "Он сначала пошёл на третий этаж за документами, сейчас вернётся.", "tj": "Вай аввал ба ошёнаи сеюм барои ҳуҷҷат рафт, ҳозир бармегардад."},
                {"zh": "我跑进去拿伞，你等我一下！", "pinyin": "Wǒ pǎo jìnqu ná sǎn, nǐ děng wǒ yīxià!", "uz": "Men yugurib kirib soyabon olib chiqaman, bir oz kutib turing!", "ru": "Я забегу за зонтом, подождите меня!", "tj": "Ман давида дохил мешавам чатр мегирам, каме интизор шав!"},
            ]
        },
        {
            "no": 2,
            "title_zh": "两个动作连续发生",
            "title_uz": "Ikki ketma-ket harakat",
            "title_ru": "Два последовательных действия",
            "title_tj": "Ду амали пайдарпай",
            "rule_uz": (
                "Ikki harakat ketma-ket sodir bo'lganda, quyidagi so'zlar ishlatiladi:\n"
                "先……然后……  — avval...keyin...\n"
                "先……再……  — avval...so'ngra...\n"
                "……完……就…… — ...tamomlagandan keyin...\n"
                "Masalan: 他先去办公室拿文件，然后回来。\n"
                "         我先复习，再出去玩儿。"
            ),
            "rule_ru": (
                "Для выражения двух последовательных действий используются:\n"
                "先……然后…… — сначала...потом...\n"
                "先……再…… — сначала...затем...\n"
                "……完……就…… — после того как закончил...\n"
                "Например: 他先去办公室拿文件，然后回来。\n"
                "          我先复习，再出去玩儿。"
            ),
            "rule_tj": (
                "Барои ифодаи ду амали пайдарпай истифода мешавад:\n"
                "先……然后…… — аввал...баъд...\n"
                "先……再…… — аввал...сипас...\n"
                "……完……就…… — пас аз тамом кардан...\n"
                "Масалан: 他先去办公室拿文件，然后回来。\n"
                "         我先复习，再出去玩儿。"
            ),
            "examples": [
                {"zh": "他先去三楼办公室拿文件，然后马上回来。", "pinyin": "Tā xiān qù sān lóu bàngōngshì ná wénjiàn, ránhòu mǎshàng huílai.", "uz": "U avval uchinchi qavatdagi idoraga hujjat olishga ketdi, keyin hoziroq qaytadi.", "ru": "Он сначала пошёл в кабинет на третьем этаже за документами, потом сразу вернётся.", "tj": "Вай аввал ба кабинети ошёнаи сеюм барои ҳуҷҷат рафт, баъд ҳозир бармегардад."},
                {"zh": "我先复习功课，再跟朋友出去。", "pinyin": "Wǒ xiān fùxí gōngkè, zài gēn péngyou chūqù.", "uz": "Avval darslarni takrorlayman, so'ngra do'stlar bilan chiqaman.", "ru": "Сначала повторю уроки, потом пойду с друзьями.", "tj": "Аввал дарсҳоро такрор мекунам, сипас бо дӯстон берун мешавам."},
            ]
        },
        {
            "no": 3,
            "title_zh": "反问句\"能……吗？\"",
            "title_uz": "Ritorik so'roq '能……吗？'",
            "title_ru": "Риторический вопрос «能……吗？»",
            "title_tj": "Саволи риторикӣ «能……吗？»",
            "rule_uz": (
                "'能……吗？' — ko'pincha hayrat yoki shubha bildiruvchi ritorik so'roq.\n"
                "Ma'nosi: 'bunga qodirsanmi? (qodir emas)', 'bu mumkinmi? (mumkin emas)'\n"
                "Javob ko'pincha inkor bo'ladi yoki so'roq o'zi inkor ma'nosi beradi.\n"
                "Masalan: 这么多东西，你一个人能拿得了吗？\n"
                "         (Bu qadar narsani yolg'iz olib keta olasanmi? — yaqqol olib keta olmaysan)"
            ),
            "rule_ru": (
                "'能……吗？' — риторический вопрос, выражающий удивление или сомнение.\n"
                "Значение: 'разве ты сможешь?', 'разве это возможно?'\n"
                "Ответ обычно отрицательный, или вопрос сам несёт отрицательный смысл.\n"
                "Например: 这么多东西，你一个人能拿得了吗？\n"
                "          (Столько вещей, ты один сможешь всё унести? — явно не сможешь)"
            ),
            "rule_tj": (
                "'能……吗？' — саволи риторикӣ, ки шигифт ё шубҳаро ифода мекунад.\n"
                "Маъно: 'оё метавонӣ?', 'оё ин имконпазир аст?'\n"
                "Ҷавоб одатан инкорӣ аст ё худи савол маънои инкориро дорад.\n"
                "Масалан: 这么多东西，你一个人能拿得了吗？\n"
                "         (Ин қадар чизҳо, оё ту танҳо ҳама гирифта метавонӣ? — аён аст ки не)"
            ),
            "examples": [
                {"zh": "这些东西这么多，你一个人能拿得了吗？", "pinyin": "Zhèxiē dōngxi zhème duō, nǐ yī ge rén néng ná de liǎo ma?", "uz": "Bu narsalar shu qadar ko'p, sen yolg'iz olib keta olasanmi?", "ru": "Столько вещей, ты один сможешь всё унести?", "tj": "Ин қадар чизҳо, оё ту танҳо ҳама гирифта метавонӣ?"},
                {"zh": "这条路这么远，你一个人能走回来吗？", "pinyin": "Zhè tiáo lù zhème yuǎn, nǐ yī ge rén néng zǒu huílai ma?", "uz": "Bu yo'l shu qadar uzoq, sen yolg'iz piyoda qaytib kela olasanmi?", "ru": "Дорога такая длинная, ты один сможешь вернуться пешком?", "tj": "Ин роҳ ин қадар дур аст, оё ту танҳо пиёда бармегардӣ?"},
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
                {"prompt_uz": "qaytib kelmoq", "prompt_ru": "вернуться", "prompt_tj": "баргаштан", "answer": "回来", "pinyin": "huílai"},
                {"prompt_uz": "idora, ofis", "prompt_ru": "офис, кабинет", "prompt_tj": "идора, кабинет", "answer": "办公室", "pinyin": "bàngōngshì"},
                {"prompt_uz": "olmoq, ko'tarmoq", "prompt_ru": "взять, держать", "prompt_tj": "гирифтан, бардоштан", "answer": "拿", "pinyin": "ná"},
                {"prompt_uz": "soyabon", "prompt_ru": "зонт", "prompt_tj": "чатр", "answer": "伞", "pinyin": "sǎn"},
                {"prompt_uz": "og'riqli bo'lmoq", "prompt_ru": "болеть", "prompt_tj": "дард кардан", "answer": "疼", "pinyin": "téng"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (先……然后、回来、拿进去、能……吗):",
            "instruction_ru": "Вставьте подходящее слово (先……然后、回来、拿进去、能……吗):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (先……然后、回来、拿进去、能……吗):",
            "items": [
                {"prompt_uz": "他______去三楼______回来。", "prompt_ru": "他______去三楼______回来。", "prompt_tj": "他______去三楼______回来。", "answer": "先 / 然后", "pinyin": "xiān / ránhòu"},
                {"prompt_uz": "这么多东西，你一个人______？", "prompt_ru": "这么多东西，你一个人______？", "prompt_tj": "这么多东西，你一个人______？", "answer": "能拿得了吗", "pinyin": "néng ná de liǎo ma"},
                {"prompt_uz": "外边下雨了，你把伞______。", "prompt_ru": "На улице дождь, занеси зонт ______.", "prompt_tj": "Берун борон мебарад, чатрро ______.", "answer": "拿进去", "pinyin": "ná jìnqu"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "他先去三楼办公室拿文件，马上就回来。", "prompt_ru": "他先去三楼办公室拿文件，马上就回来。", "prompt_tj": "他先去三楼办公室拿文件，马上就回来。", "answer": "U avval uchinchi qavatdagi idoraga hujjat olishga ketdi, hoziroq qaytadi.", "pinyin": "Tā xiān qù sān lóu bàngōngshì ná wénjiàn, mǎshàng jiù huílai."},
                {"prompt_uz": "这些东西这么多，你一个人能拿得了吗？", "prompt_ru": "这些东西这么多，你一个人能拿得了吗？", "prompt_tj": "这些东西这么多，你一个人能拿得了吗？", "answer": "Bu narsalar shu qadar ko'p, sen yolg'iz olib keta olasanmi?", "pinyin": "Zhèxiē dōngxi zhème duō, nǐ yī ge rén néng ná de liǎo ma?"},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["回来", "办公室", "拿", "伞", "疼"]},
        {"no": 2, "answers": ["先 / 然后", "能拿得了吗", "拿进去"]},
        {"no": 3, "answers": [
            "U avval uchinchi qavatdagi idoraga hujjat olishga ketdi, hoziroq qaytadi.",
            "Bu narsalar shu qadar ko'p, sen yolg'iz olib keta olasanmi?",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "简单趋向补语 ishlatib 4 ta gap tuzing. 回来, 进去, 出来, 上去 kabi so'zlarni qo'llang.",
            "instruction_ru": "Составьте 4 предложения с простыми направленными дополнениями. Используйте слова 回来, 进去, 出来, 上去.",
            "instruction_tj": "Бо иловаҳои самтноки содда 4 ҷумла тартиб диҳед. Калимаҳои 回来, 进去, 出来, 上去-ро истифода баред.",
            "words": ["回来", "进去", "出来", "上去", "拿回来", "跑进去"],
            "topic_uz": "Harakatlar yo'nalishi",
            "topic_ru": "Направление действий",
            "topic_tj": "Самти амалҳо",
        },
        {
            "no": 2,
            "instruction_uz": "Kundalik hayotingizda ketma-ket bajariladigan ishlar haqida 5-6 gapdan iborat matn yozing. 先……然后…… qolipini ishlating.",
            "instruction_ru": "Напишите текст из 5–6 предложений о последовательных делах в вашей повседневной жизни. Используйте конструкцию 先……然后……",
            "instruction_tj": "Дар бораи корҳои пайдарпае, ки дар ҳаёти рӯзмарраи худ анҷом медиҳед, матни 5-6 ҷумлагӣ нависед. Сохтори 先……然后……-ро истифода баред.",
            "topic_uz": "Mening kundalik tartibim",
            "topic_ru": "Мой распорядок дня",
            "topic_tj": "Тартиби рӯзонаи ман",
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
