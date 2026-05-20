import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 8,
    "lesson_code": "HSK4-L08",
    "title": "生活中不缺少美",
    "goal": json.dumps({"uz": "go'zallik, his-tuyg'u va tabiat haqida gapirish; 使, 因此, 往往, 可不是 grammatik qoliplarini o'zlashtirish", "ru": "говорить о красоте, чувствах и природе; освоить грамматические конструкции 使, 因此, 往往, 可不是", "tj": "дар бораи зебоӣ, эҳсосот ва табиат гуфтугӯ кардан; азхуд кардани қолабҳои грамматикии 使, 因此, 往往, 可不是"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Hayotda go'zallik ko'p' mavzusiga bag'ishlangan. Unda tabiat go'zalligi, his-tuyg'ular, sport va psixologik holat haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 使, 因此, 往往, 可不是, 只要...就...", "ru": "Этот урок посвящён теме «В жизни много красоты». В нём изучается, как говорить о красоте природы, чувствах, спорте и психологическом состоянии. Основные грамматические конструкции: 使, 因此, 往往, 可不是, 只要...就...", "tj": "Ин дарс ба мавзӯи «Дар ҳаёт зебоӣ бисёр аст» бахшида шудааст. Дар он гуфтугӯ дар бораи зебоии табиат, эҳсосот, варзиш ва ҳолати равонӣ омӯхта мешавад. Қолабҳои асосии грамматикӣ: 使, 因此, 往往, 可不是, 只要...就..."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "巧克力", "pinyin": "qiǎokèlì", "pos": "n.", "uz": "shokolad", "ru": "шоколад", "tj": "шоколад"},
            {"no": 2, "zh": "亲戚", "pinyin": "qīnqì", "pos": "n.", "uz": "qarindosh, yaqin", "ru": "родственник", "tj": "хешу ақраб"},
            {"no": 3, "zh": "伤心", "pinyin": "shāng xīn", "pos": "adj.", "uz": "qayg'uli, xafa", "ru": "расстроенный, огорчённый", "tj": "ғамгин, дилтанг"},
            {"no": 4, "zh": "使", "pinyin": "shǐ", "pos": "v.", "uz": "qilmoq, bo'lishiga sabab bo'lmoq", "ru": "заставлять, делать (так, что)", "tj": "кардан, боиси шудан"},
            {"no": 5, "zh": "心情", "pinyin": "xīnqíng", "pos": "n.", "uz": "kayfiyat, ruhiy holat", "ru": "настроение, душевное состояние", "tj": "кайфият, ҳолати рӯҳӣ"},
            {"no": 6, "zh": "愉快", "pinyin": "yúkuài", "pos": "adj.", "uz": "xursand, shod", "ru": "радостный, весёлый", "tj": "хурсанд, шод"},
            {"no": 7, "zh": "景色", "pinyin": "jǐngsè", "pos": "n.", "uz": "manzara, ko'rinish", "ru": "пейзаж, вид", "tj": "манзара, чашманддоз"},
            {"no": 8, "zh": "放松", "pinyin": "fàngsōng", "pos": "v.", "uz": "bo'shashmoq, dam olmoq (ruhiy)", "ru": "расслабляться, отдыхать (психологически)", "tj": "ором гирифтан, истироҳат кардан"},
            {"no": 9, "zh": "压力", "pinyin": "yālì", "pos": "n.", "uz": "bosim, stres", "ru": "давление, стресс", "tj": "фишор, стресс"},
            {"no": 10, "zh": "回忆", "pinyin": "huíyì", "pos": "v./n.", "uz": "eslamoq; xotira, esdalik", "ru": "вспоминать; воспоминание", "tj": "ёд кардан; хотира, ёдгорӣ"},
            {"no": 11, "zh": "发生", "pinyin": "fāshēng", "pos": "v.", "uz": "sodir bo'lmoq, yuz bermoq", "ru": "происходить, случаться", "tj": "рӯй додан, воқеъ шудан"},
            {"no": 12, "zh": "成为", "pinyin": "chéngwéi", "pos": "v.", "uz": "bo'lmoq, aylanmoq", "ru": "становиться, превращаться", "tj": "шудан, табдил ёфтан"},
            {"no": 13, "zh": "只要", "pinyin": "zhǐyào", "pos": "conj.", "uz": "faqat...bo'lsa, agar...bo'lsa kifoya", "ru": "лишь бы, при условии что", "tj": "агар танҳо...бошад, кофист ки"},
            {"no": 14, "zh": "师傅", "pinyin": "shīfu", "pos": "n.", "uz": "usta, malakali mutaxassis", "ru": "мастер, умелец", "tj": "устод, мутахассис"},
            {"no": 15, "zh": "大使馆", "pinyin": "dàshǐguǎn", "pos": "n.", "uz": "elchixona", "ru": "посольство", "tj": "сафорат"},
            {"no": 16, "zh": "堵车", "pinyin": "dǔ chē", "pos": "v.", "uz": "tiqilinch, transport qotib qolmoq", "ru": "пробка, застрять в пробке", "tj": "гузаргоҳ банд шудан, тарофик"},
            {"no": 17, "zh": "距离", "pinyin": "jùlí", "pos": "n.", "uz": "masofa, uzoqlik", "ru": "расстояние, дистанция", "tj": "масофа, дурӣ"},
            {"no": 18, "zh": "耐心", "pinyin": "nàixīn", "pos": "n./adj.", "uz": "sabr, toqat; sabr-toqatli", "ru": "терпение; терпеливый", "tj": "сабр, тоқат; сабрдор"},
            {"no": 19, "zh": "因此", "pinyin": "yīncǐ", "pos": "conj.", "uz": "shu sababli, shuning uchun", "ru": "поэтому, по этой причине", "tj": "аз ин сабаб, аз ин рӯ"},
            {"no": 20, "zh": "往往", "pinyin": "wǎngwǎng", "pos": "adv.", "uz": "ko'pincha, odatda", "ru": "зачастую, нередко", "tj": "аксар вақт, одатан"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "Li o'qituvchi va Gao o'qituvchi shokolad haqida suhbatlashmoqda",
                "scene_ru": "Учитель Ли и учитель Гао разговаривают о шоколаде",
                "scene_tj": "Муаллим Ли ва муаллим Гао дар бораи шоколад сӯҳбат мекунанд",
                "dialogue": [
                    {"speaker": "李老师", "zh": "这种巧克力不好找，你在哪儿买的？", "pinyin": "", "uz": "Bunday shokolad topish qiyin, siz uni qayerdan topdingiz?", "ru": "Такой шоколад нелегко найти, где вы его купили?", "tj": "Чунин шоколадро ёфтан душвор аст, шумо онро аз куҷо харидед?"},
                    {"speaker": "高老师", "zh": "不是我买的，是我女儿从国外常常买回来送给我的礼物。", "pinyin": "", "uz": "Men sotib olmadim, bu qizim chet eldan tez-tez olib keladigan sovg'a.", "ru": "Это не я купил, это подарок, который моя дочь часто привозит мне из-за рубежа.", "tj": "Ман нахаридам, ин туҳфаест, ки духтарам аз хориҷ зуд-зуд меорад."},
                    {"speaker": "李老师", "zh": "不是说吃巧克力以后常常会有很多亲戚来？", "pinyin": "", "uz": "Shokolad yegandan keyin ko'p qarindosh keladi deyishmaydimi?", "ru": "Разве не говорят, что после того как съешь шоколад, появится много родственников?", "tj": "Магар намегӯянд, ки пас аз хӯрдани шоколад хешу ақраби зиёд меоянд?"},
                    {"speaker": "高老师", "zh": "是呀！而且很多人伤心的时候都会吃巧克力，因为它能使人的心情变得愉快。", "pinyin": "", "uz": "Ha! Ko'p odamlar xafa bo'lganida shokolad yeydi, chunki u kishining kayfiyatini yaxshilaydi.", "ru": "Да! И многие люди едят шоколад, когда расстроены, потому что он способен улучшить настроение.", "tj": "Бале! Ва бисёр одамон вақти ғамгинӣ шоколад мехӯранд, зеро он метавонад кайфиятро хуб кунад."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "Xia va Mark o'tgan futbol musobaqasi haqida suhbatlashmoqda",
                "scene_ru": "Сяо Ся и Марк разговаривают о прошедшем футбольном матче",
                "scene_tj": "Сяо Ся ва Марк дар бораи мусобиқаи гузаштаи футбол сӯҳбат мекунанд",
                "dialogue": [
                    {"speaker": "小夏", "zh": "这里的景色真美，空气也好，心情放松多了。", "pinyin": "", "uz": "Bu yerdagi manzara juda chiroyli, havosi ham yaxshi, kayfiyat ancha yaxshilandi.", "ru": "Здешний пейзаж очень красивый, воздух тоже хороший, настроение намного лучше.", "tj": "Манзараи ин ҷо воқеан зебо аст, ҳаво ҳам хуб аст, кайфият анча беҳтар шуд."},
                    {"speaker": "马克", "zh": "你不要有压力，好好儿把这次比赛当做一次学习机会。", "pinyin": "", "uz": "Xavotir olmang, bu musobaqani yaxshilab o'rganish imkoniyati deb biling.", "ru": "Не нервничай, хорошенько восприми этот матч как возможность для обучения.", "tj": "Нигарон мабош, ин мусобиқаро ҳамчун як фурсати омӯзиш қабул кун."},
                    {"speaker": "小夏", "zh": "这段时间我总是回忆以前发生的事，一个人空着的时间里往往会这样。", "pinyin": "", "uz": "Bu vaqt ichida men doim oldin bo'lgan voqealarni eslab yuraman, bo'sh vaqt bo'lganda ko'pincha shunday bo'ladi.", "ru": "В последнее время я всё время вспоминаю прошлые события — в свободное время зачастую так и бывает.", "tj": "Дар ин муддат ман ҳамеша воқеаҳои гузаштаро ёд мекунам, вақти холӣ аксар вақт чунин мешавад."},
                    {"speaker": "马克", "zh": "只要你保持好的心情，一切都会成为美好的回忆。生活中不缺少美，因此要用心去发现。", "pinyin": "", "uz": "Faqat yaxshi kayfiyatni saqlasang, hammasi yaxshi xotiraga aylanadi. Hayotda go'zallik ko'p, shuning uchun uni yurak bilan topish kerak.", "ru": "Если только сохранишь хорошее настроение, всё превратится в прекрасные воспоминания. В жизни красоты немало, поэтому нужно искать её всем сердцем.", "tj": "Агар танҳо кайфияти хубро нигоҳ дорӣ, ҳама чиз ба хотираҳои зебо табдил меёбад. Дар ҳаёт зебоӣ бисёр аст, аз ин рӯ бояд онро бо дил ёфт."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "使",
                "title_uz": "使 (qilmoq, sabab bo'lmoq)",
                "title_ru": "使 (заставлять, делать так, что)",
                "title_tj": "使 (кардан, боиси шудан)",
                "rule_uz": "'Qilmoq, bo'lishiga sabab bo'lmoq' ma'nosini beradi. Birov yoki biror narsa boshqa bir holatga olib kelishini bildiradi.",
                "rule_ru": "Означает «заставлять, приводить к чему-либо». Указывает на то, что кто-то или что-то приводит к определённому состоянию.",
                "rule_tj": "Маънои «кардан, боиси шудан»-ро медиҳад. Нишон медиҳад, ки касе ё чизе ба ҳолати дигаре оварда мешавад.",
                "examples": [
                    {"zh": "巧克力能使人的心情变得愉快。", "pinyin": "", "uz": "Shokolad kishining kayfiyatini yaxshilaydi.", "ru": "Шоколад способен улучшить настроение человека.", "tj": "Шоколад метавонад кайфияти одамро хуб кунад."},
                    {"zh": "这件事使我很感动。", "pinyin": "", "uz": "Bu narsa meni juda ta'sirlantirdi.", "ru": "Это дело меня очень растрогало.", "tj": "Ин кор маро хеле таъсир кард."},
                ],
            },
            {
                "no": 2,
                "title_zh": "因此",
                "title_uz": "因此 (shu sababli, shuning uchun)",
                "title_ru": "因此 (поэтому, по этой причине)",
                "title_tj": "因此 (аз ин сабаб, аз ин рӯ)",
                "rule_uz": "'Shu sababli, shuning uchun' ma'nosini beradi. Sabab-natija munosabatini bildiradi.",
                "rule_ru": "Означает «поэтому, по этой причине». Выражает причинно-следственную связь.",
                "rule_tj": "Маънои «аз ин сабаб, аз ин рӯ»-ро медиҳад. Робитаи сабаб ва натиҷаро нишон медиҳад.",
                "examples": [
                    {"zh": "生活中不缺少美，因此要用心去发现。", "pinyin": "", "uz": "Hayotda go'zallik ko'p, shuning uchun uni topishga harakat qilish kerak.", "ru": "В жизни красоты немало, поэтому нужно стараться её найти.", "tj": "Дар ҳаёт зебоӣ бисёр аст, аз ин рӯ бояд кӯшиш кард, ки онро ёбем."},
                    {"zh": "他努力工作，因此取得了好成绩。", "pinyin": "", "uz": "U qattiq ishladi, shuning uchun yaxshi natijaga erishdi.", "ru": "Он усердно работал, поэтому добился хороших результатов.", "tj": "Ӯ сахт кор кард, аз ин рӯ ба натиҷаи хуб расид."},
                ],
            },
            {
                "no": 3,
                "title_zh": "往往",
                "title_uz": "往往 (ko'pincha, odatda)",
                "title_ru": "往往 (зачастую, нередко)",
                "title_tj": "往往 (аксар вақт, одатан)",
                "rule_uz": "'Ko'pincha, odatda' ma'nosini beradi. Biror holat ko'p marta yoki odatda shunday bo'lishini bildiradi.",
                "rule_ru": "Означает «зачастую, нередко». Указывает на то, что некоторое состояние происходит часто или обычно именно так.",
                "rule_tj": "Маънои «аксар вақт, одатан»-ро медиҳад. Нишон медиҳад, ки ҳолате борҳо ё одатан чунин мешавад.",
                "examples": [
                    {"zh": "一个人的时候往往会想很多。", "pinyin": "", "uz": "Yolg'iz qolganda ko'pincha ko'p narsalar o'ylanadi.", "ru": "Когда остаёшься один, зачастую думаешь о многом.", "tj": "Вақти танҳоӣ аксар вақт бисёр чизҳо ба хаёл меояд."},
                    {"zh": "下雨天往往让人心情不好。", "pinyin": "", "uz": "Yomg'irli kunda ko'pincha kayfiyat yaxshi bo'lmaydi.", "ru": "В дождливые дни настроение зачастую бывает плохим.", "tj": "Рӯзҳои борон аксар вақт кайфият хуб намешавад."},
                ],
            },
            {
                "no": 4,
                "title_zh": "可不是",
                "title_uz": "可不是 (albatta, to'g'ri, ha-da)",
                "title_ru": "可不是 (конечно, именно так, ну и правда)",
                "title_tj": "可不是 (албатта, дуруст аст, ҳа-да)",
                "rule_uz": "'Albatta, to'g'ri, ha-da' ma'nosini beradi. Boshqa kishining gapiga qo'shilish yoki tasdiqlash uchun ishlatiladi (og'zaki nutqda).",
                "rule_ru": "Означает «конечно, именно так». Используется для согласия или подтверждения слов другого человека (в разговорной речи).",
                "rule_tj": "Маънои «албатта, дуруст аст»-ро медиҳад. Барои розӣ шудан ё тасдиқ кардани гуфтаҳои дигарон истифода мешавад (дар нутқи гуфтугӯӣ).",
                "examples": [
                    {"zh": "A: 今天天气真好！B: 可不是！", "pinyin": "", "uz": "A: Bugun havo juda yaxshi! B: Ha, albatta!", "ru": "A: Сегодня погода отличная! B: Конечно!", "tj": "A: Имрӯз ҳаво воқеан хуб аст! B: Албатта!"},
                    {"zh": "A: 这里的景色太美了。B: 可不是，我也这么觉得。", "pinyin": "", "uz": "A: Bu yerdagi manzara juda chiroyli. B: Ha, ha, men ham shunday deb o'ylayman.", "ru": "A: Здешний пейзаж очень красивый. B: Конечно, я тоже так думаю.", "tj": "A: Манзараи ин ҷо хеле зебо аст. B: Албатта, ман ҳам чунин фикр мекунам."},
                ],
            },
            {
                "no": 5,
                "title_zh": "只要……就……",
                "title_uz": "只要……就…… (faqat...bo'lsa,...bo'ladi)",
                "title_ru": "只要……就…… (лишь бы...то...)",
                "title_tj": "只要……就…… (агар танҳо...бошад,...мешавад)",
                "rule_uz": "'Faqat...bo'lsa, ...bo'ladi' ma'nosini beradi. Minimal shart bajarilsa natija yuz berishini bildiradi.",
                "rule_ru": "Означает «лишь бы..., то...». Указывает на то, что при выполнении минимального условия наступает результат.",
                "rule_tj": "Маънои «агар танҳо...бошад,...мешавад»-ро медиҳад. Нишон медиҳад, ки агар шарти ҳадди ақал иҷро шавад, натиҷа ба даст меояд.",
                "examples": [
                    {"zh": "只要你保持好心情，一切都会好的。", "pinyin": "", "uz": "Faqat yaxshi kayfiyatni saqlasang, hammasi yaxshi bo'ladi.", "ru": "Лишь бы ты сохранял хорошее настроение — всё будет хорошо.", "tj": "Агар танҳо кайфияти хубро нигоҳ дорӣ, ҳама чиз хуб мешавад."},
                    {"zh": "只要努力，就能成功。", "pinyin": "", "uz": "Faqat harakat qilsang, muvaffaqiyat qozonasan.", "ru": "Лишь бы стараться — и можно добиться успеха.", "tj": "Агар танҳо кӯшиш кунӣ, муваффақ мешавӣ."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "exercise_json": json.dumps(
        [
            {
                "no": 1,
                "type": "translate_to_chinese",
                "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
                "instruction_ru": "Напишите китайский вариант следующих слов:",
                "instruction_tj": "Тарҷумаи хитоии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "kayfiyat", "prompt_ru": "настроение", "prompt_tj": "кайфият", "answer": "心情", "pinyin": "xīnqíng"},
                    {"prompt_uz": "manzara, ko'rinish", "prompt_ru": "пейзаж, вид", "prompt_tj": "манзара", "answer": "景色", "pinyin": "jǐngsè"},
                    {"prompt_uz": "bosim, stres", "prompt_ru": "давление, стресс", "prompt_tj": "фишор, стресс", "answer": "压力", "pinyin": "yālì"},
                    {"prompt_uz": "eslamoq; xotira", "prompt_ru": "вспоминать; воспоминание", "prompt_tj": "ёд кардан; хотира", "answer": "回忆", "pinyin": "huíyì"},
                    {"prompt_uz": "sabr, toqat", "prompt_ru": "терпение", "prompt_tj": "сабр, тоқат", "answer": "耐心", "pinyin": "nàixīn"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский перевод следующих слов:",
                "instruction_tj": "Тарҷумаи ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "使", "prompt_ru": "使", "prompt_tj": "使", "answer": "qilmoq, sabab bo'lmoq", "pinyin": "shǐ"},
                    {"prompt_uz": "因此", "prompt_ru": "因此", "prompt_tj": "因此", "answer": "shu sababli, shuning uchun", "pinyin": "yīncǐ"},
                    {"prompt_uz": "往往", "prompt_ru": "往往", "prompt_tj": "往往", "answer": "ko'pincha, odatda", "pinyin": "wǎngwǎng"},
                    {"prompt_uz": "成为", "prompt_ru": "成为", "prompt_tj": "成为", "answer": "bo'lmoq, aylanmoq", "pinyin": "chéngwéi"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (使、因此、往往、只要、成为):",
                "instruction_ru": "Выберите подходящее слово (使、因此、往往、只要、成为):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (使、因此、往往、只要、成为):",
                "items": [
                    {"prompt_uz": "这首歌______我想起了很多过去的事。", "prompt_ru": "这首歌______我想起了很多过去的事。", "prompt_tj": "这首歌______我想起了很多过去的事。", "answer": "使", "pinyin": "shǐ"},
                    {"prompt_uz": "他很努力，______取得了很好的成绩。", "prompt_ru": "他很努力，______取得了很好的成绩。", "prompt_tj": "他很努力，______取得了很好的成绩。", "answer": "因此", "pinyin": "yīncǐ"},
                    {"prompt_uz": "______你坚持，就一定能______优秀的人。", "prompt_ru": "______你坚持，就一定能______优秀的人。", "prompt_tj": "______你坚持，就一定能______优秀的人。", "answer": "只要 / 成为", "pinyin": "zhǐyào / chéngwéi"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["心情", "景色", "压力", "回忆", "耐心"]},
            {"no": 2, "answers": ["qilmoq, sabab bo'lmoq", "shu sababli, shuning uchun", "ko'pincha, odatda", "bo'lmoq, aylanmoq"]},
            {"no": 3, "answers": ["使", "因此", "只要 / 成为"]},
        ],
        ensure_ascii=False,
    ),
    "homework_json": json.dumps(
        [
            {
                "no": 1,
                "instruction_uz": "Quyidagi so'zlardan foydalanib 3 ta gap tuzing:",
                "instruction_ru": "Составьте 3 предложения, используя следующие слова:",
                "instruction_tj": "Бо истифодаи калимаҳои зерин 3 ҷумла тартиб диҳед:",
                "words": ["心情", "景色", "使", "往往"],
                "example": "美丽的景色使我心情愉快，压力往往在大自然中消失了。",
            },
            {
                "no": 2,
                "instruction_uz": "'使' va '只要...就...' qoliplaridan foydalanib har biridan 2 ta gap tuzing.",
                "instruction_ru": "Напишите по 2 предложения с конструкциями '使' и '只要...就...'.",
                "instruction_tj": "Бо қолабҳои '使' ва '只要...就...' аз ҳар кадом 2 ҷумла нависед.",
                "topic_uz": "his-tuyg'u, tabiat va go'zallik mavzusida",
                "topic_ru": "на тему чувств, природы и красоты",
                "topic_tj": "дар мавзӯи эҳсосот, табиат ва зебоӣ",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Siz hayotda go'zallikni qayerdan topasiz? 生活中你在哪里发现美？",
                "topic_ru": "Где вы находите красоту в жизни? 生活中你在哪里发现美？",
                "topic_tj": "Шумо дар ҳаёт зебоиро аз куҷо меёбед? 生活中你在哪里发现美？",
            },
        ],
        ensure_ascii=False,
    ),
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
