import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 2,
    "lesson_code": "HSK4-L02",
    "title": "真正的朋友",
    "goal": json.dumps({"uz": "do'stlik va munosabatlar haqida gapirish; 正好, 差不多, 尽管 grammatik qoliplarini o'zlashtirish", "ru": "говорить о дружбе и отношениях; освоить грамматические конструкции 正好, 差不多, 尽管", "tj": "гуфтугӯ дар бораи дӯстӣ ва муносибатҳо; аз худ кардани қолипҳои грамматикии 正好, 差不多, 尽管"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Haqiqiy do'st' mavzusiga bag'ishlangan. Unda do'stlik qilish, aloqada bo'lish va yangi muhitga moslashish haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 正好, 差不多, 弄, 帮, 尽管.", "ru": "Этот урок посвящён теме 'Настоящий друг'. В нём вы научитесь говорить о дружбе, поддержании связи и адаптации к новой среде. Основные грамматические конструкции: 正好, 差不多, 弄, 帮, 尽管.", "tj": "Ин дарс ба мавзӯи 'Дӯсти воқеӣ' бахшида шудааст. Дар он дӯстӣ кардан, дар тамос будан ва мутобиқ шудан ба муҳити нав омӯхта мешавад. Қолипҳои асосии грамматикӣ: 正好, 差不多, 弄, 帮, 尽管."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "适应", "pinyin": "shìyìng", "pos": "v.", "uz": "moslashmoq, ko'nikmoq", "ru": "адаптироваться, привыкать", "tj": "мутобиқ шудан, одат кардан"},
            {"no": 2, "zh": "交", "pinyin": "jiāo", "pos": "v.", "uz": "do'st orttirmoq, tanishmoq", "ru": "заводить друзей, знакомиться", "tj": "дӯст пайдо кардан, шинос шудан"},
            {"no": 3, "zh": "平时", "pinyin": "píngshí", "pos": "n.", "uz": "odatda, kundalik hayotda", "ru": "обычно, в повседневной жизни", "tj": "одатан, дар ҳаёти ҳаррӯза"},
            {"no": 4, "zh": "逛", "pinyin": "guàng", "pos": "v.", "uz": "sayr qilmoq, ko'rinib chiqmoq", "ru": "гулять, прогуливаться", "tj": "гаштан, сайр кардан"},
            {"no": 5, "zh": "短信", "pinyin": "duǎnxìn", "pos": "n.", "uz": "qisqa xabar (SMS)", "ru": "короткое сообщение (SMS)", "tj": "паёми кӯтоҳ (SMS)"},
            {"no": 6, "zh": "正好", "pinyin": "zhènghǎo", "pos": "adv.", "uz": "aynan, o'z vaqtida, to'g'ri keldi", "ru": "как раз, вовремя, очень кстати", "tj": "маҳз, дар вақти муносиб омад"},
            {"no": 7, "zh": "聚会", "pinyin": "jùhuì", "pos": "v./n.", "uz": "yig'ilish o'tkazmoq; yig'ilish, ziyofat", "ru": "собираться; вечеринка, встреча", "tj": "ҷамъ шудан; ҷамъомад, зиёфат"},
            {"no": 8, "zh": "联系", "pinyin": "liánxì", "pos": "v.", "uz": "aloqa qilmoq, bog'lanmoq", "ru": "поддерживать связь, связываться", "tj": "тамос гирифтан, иртибот доштан"},
            {"no": 9, "zh": "差不多", "pinyin": "chàbuduō", "pos": "adv.", "uz": "deyarli, taxminan, xuddi shunday", "ru": "почти, приблизительно, примерно одинаково", "tj": "тақрибан, қариб ки, тахминан"},
            {"no": 10, "zh": "专门", "pinyin": "zhuānmén", "pos": "adv.", "uz": "maxsus, ataylab", "ru": "специально, нарочно", "tj": "махсус, атайлаб"},
            {"no": 11, "zh": "毕业", "pinyin": "bì yè", "pos": "v.", "uz": "bitirmoq (maktab, universitet)", "ru": "окончить (школу, университет)", "tj": "хатм кардан (мактаб, донишгоҳ)"},
            {"no": 12, "zh": "麻烦", "pinyin": "máfan", "pos": "v./adj.", "uz": "bezovta qilmoq; qiyin, muammoli", "ru": "беспокоить; сложный, проблематичный", "tj": "безовтор кардан; мушкил, мушкилсоз"},
            {"no": 13, "zh": "好像", "pinyin": "hǎoxiàng", "pos": "adv.", "uz": "xuddi, go'yo, shekilli", "ru": "как будто, похоже, кажется", "tj": "гӯё, ба назар мерасад"},
            {"no": 14, "zh": "重新", "pinyin": "chóngxīn", "pos": "adv.", "uz": "qaytadan, yana", "ru": "заново, снова", "tj": "аз нав, боз"},
            {"no": 15, "zh": "尽管", "pinyin": "jǐnguǎn", "pos": "conj.", "uz": "garchi...bo'lsa ham, qaramay", "ru": "хотя, несмотря на то что", "tj": "гарчанде...ҳам бошад, новобаста аз"},
            {"no": 16, "zh": "真正", "pinyin": "zhēnzhèng", "pos": "adj.", "uz": "haqiqiy, chin", "ru": "настоящий, истинный", "tj": "воқеӣ, ҳақиқӣ"},
            {"no": 17, "zh": "友谊", "pinyin": "yǒuyì", "pos": "n.", "uz": "do'stlik", "ru": "дружба", "tj": "дӯстӣ"},
            {"no": 18, "zh": "了解", "pinyin": "liǎojiě", "pos": "v.", "uz": "bilmoq, tanib olmoq", "ru": "знать, понимать", "tj": "донистан, шинохтан"},
            {"no": 19, "zh": "帮助", "pinyin": "bāngzhù", "pos": "v./n.", "uz": "yordam bermoq; yordam", "ru": "помогать; помощь", "tj": "кӯмак кардан; кӯмак"},
            {"no": 20, "zh": "关心", "pinyin": "guānxīn", "pos": "v.", "uz": "g'amxo'rlik qilmoq, qayg'urmoq", "ru": "заботиться, беспокоиться", "tj": "ғамхорӣ кардан, аҳамият додан"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "小夏 va 马克 Xitoyda do'stlar haqida suhbatlashadi",
                "scene_ru": "小夏 и 马克 разговаривают о друзьях в Китае",
                "scene_tj": "小夏 ва 马克 дар бораи дӯстон дар Чин гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "小夏", "zh": "来中国快一年了，你适应这儿的生活了吗？", "pinyin": "",
                     "uz": "Xitoyga kelganing bir yilga yaqin bo'ldi, bu yerdagi hayotga moslashdingmi?",
                     "ru": "Уже почти год как ты в Китае — ты привык к здешней жизни?",
                     "tj": "Тақрибан як сол аст ба Чин омадӣ — ба ҳаёти ин ҷо мутобиқ шудӣ?"},
                    {"speaker": "马克", "zh": "开始有点儿不习惯，后来慢慢就好了，我还交了一个中国朋友。", "pinyin": "",
                     "uz": "Boshida biroz qiyin bo'ldi, keyin asta-sekin odatlandim, bir xitoylik do'stim ham bor.",
                     "ru": "Сначала было немного непривычно, потом постепенно всё наладилось, и я завёл китайского друга.",
                     "tj": "Аввал каме душвор буд, баъд оҳиста-оҳиста одат кардам, як дӯсти хитоӣ ҳам пайдо кардам."},
                    {"speaker": "小夏", "zh": "那挺好的！你们平时一起做什么？", "pinyin": "",
                     "uz": "Bu juda yaxshi! Siz odatda birga nima qilasiz?",
                     "ru": "Это здорово! Чем вы обычно занимаетесь вместе?",
                     "tj": "Ин хеле хуб аст! Шумо одатан якҷоя чӣ кор мекунед?"},
                    {"speaker": "马克", "zh": "我们在图书馆认识的，平时一起逛街、踢球，他还给我发短信教我汉语。", "pinyin": "",
                     "uz": "Biz kutubxonada tanishdik, odatda birga ko'chada sayr qilamiz, futbol o'ynaymiz, u menga SMS bilan xitoy tilini o'rgatadi.",
                     "ru": "Мы познакомились в библиотеке, обычно вместе гуляем по улицам, играем в футбол, и он присылает мне SMS, учит меня китайскому.",
                     "tj": "Мо дар китобхона шинос шудем, одатан якҷоя дар кӯча мегардем, футбол мебозем, ӯ ба ман паёмҳои кӯтоҳ мефиристад ва хитоӣ меомӯзонад."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "小李 va 小林 sinfdoshlar yig'ilishi haqida gaplashadi",
                "scene_ru": "小李 и 小林 обсуждают встречу однокурсников",
                "scene_tj": "小李 ва 小林 дар бораи ҷамъомади ҳамсинфон гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "小李", "zh": "星期天同学聚会，你能来吗？", "pinyin": "",
                     "uz": "Yakshanba kuni sinfdoshlar yig'ilishadi, kela olasanmi?",
                     "ru": "В воскресенье собираются однокурсники, ты сможешь прийти?",
                     "tj": "Якшанбе ҳамсинфон ҷамъ мешаванд, метавонӣ биёӣ?"},
                    {"speaker": "小林", "zh": "是不是上次联系过我的那几位同学？大概多少人？", "pinyin": "",
                     "uz": "O'sha safar men bilan aloqa qilgan sinfdoshlar emasmi? Taxminan necha kishi?",
                     "ru": "Это те однокурсники, которые в прошлый раз со мной связывались? Примерно сколько человек?",
                     "tj": "Ин ҳамон ҳамсинфоне нест, ки дафъаи гузашта бо ман тамос гирифтанд? Тақрибан чанд нафар?"},
                    {"speaker": "小李", "zh": "差不多十五个人，好多都是专门从外地飞回来的。", "pinyin": "",
                     "uz": "Taxminan o'n besh kishi, ko'plari maxsus boshqa shaharlardan uchib kelishdi.",
                     "ru": "Примерно пятнадцать человек, многие специально прилетели из других городов.",
                     "tj": "Тақрибан понздаҳ нафар, бисёриҳо махсус аз шаҳрҳои дигар парвоз карда омаданд."},
                    {"speaker": "小林", "zh": "太好了！毕业后大家联系少了，正好借这个机会重新聚一聚。", "pinyin": "",
                     "uz": "Juda yaxshi! Bitiruvdan keyin hammaning aloqasi kamaydi, bu aynan qayta yig'ilish uchun yaxshi imkoniyat.",
                     "ru": "Отлично! После выпуска все реже общались, как раз хорошая возможность собраться снова.",
                     "tj": "Хеле хуб! Пас аз хатм ҳамаи иртибот камтар шуд, ин маҳз фурсати хуб барои боз ҷамъ шудан аст."},
                ],
            },
            {
                "block_no": 3,
                "section_label": "课文 3",
                "scene_uz": "Haqiqiy do'stlik haqida qisqa matn",
                "scene_ru": "Короткий текст о настоящей дружбе",
                "scene_tj": "Матни кӯтоҳ дар бораи дӯстии воқеӣ",
                "dialogue": [
                    {"speaker": "旁白", "zh": "真正的朋友，不是见面次数多的人，而是了解你、关心你、在你需要帮助时出现的人。", "pinyin": "",
                     "uz": "Haqiqiy do'st — ko'p uchrashuvchi kishi emas, balki seni tushunib, g'amxo'rlik qilib, muhtoj paytingda yonida bo'ladigan kishidir.",
                     "ru": "Настоящий друг — это не тот, кто часто встречается с тобой, а тот, кто тебя понимает, заботится о тебе и появляется, когда ты нуждаешься в помощи.",
                     "tj": "Дӯсти воқеӣ — касе нест, ки бисёр мулоқот кунад, балки касест, ки туро мефаҳмад, ғамхорӣ мекунад ва вақте ки ба кӯмак ниёз дорӣ, пеш меояд."},
                    {"speaker": "旁白", "zh": "尽管大家都很忙，但真正的友谊经得起时间和距离的考验。", "pinyin": "",
                     "uz": "Garchi hammaning vaqti yo'q bo'lsa ham, haqiqiy do'stlik vaqt va masofaga bardosh beradi.",
                     "ru": "Хотя все очень заняты, настоящая дружба выдерживает испытание временем и расстоянием.",
                     "tj": "Гарчанде ҳамаи вақт надоранд, дӯстии воқеӣ имтиҳони вақт ва масофаро тоб меорад."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "正好",
                "title_uz": "aynan, to'g'ri keldi",
                "title_ru": "как раз, очень кстати",
                "title_tj": "маҳз, дар вақти муносиб",
                "rule_uz": "'Aynan, to'g'ri keldi, o'z vaqtida' ma'nosini beradi. Biror narsa kutilmaganda yoki mos holda sodir bo'lganini bildiradi.",
                "rule_ru": "Означает 'как раз, очень кстати, вовремя'. Используется когда что-то произошло неожиданно или очень к месту.",
                "rule_tj": "Маънои 'маҳз, дар вақти муносиб' дорад. Нишон медиҳад, ки чизе ногаҳон ё дар ҷои мувофиқ рӯй додааст.",
                "examples": [
                    {"zh": "我刚想找你，你正好来了。", "pinyin": "",
                     "uz": "Men seni izlamoqchi edim, sen aynan kelib qolding.",
                     "ru": "Я только подумал о тебе, а ты как раз пришёл.",
                     "tj": "Ман маҳз мехостам туро ёбам, ту маҳз омадӣ."},
                    {"zh": "这件衣服正好合适。", "pinyin": "",
                     "uz": "Bu kiyim aynan mos keldi.",
                     "ru": "Эта одежда как раз подошла.",
                     "tj": "Ин либос маҳз мувофиқ омад."},
                ],
            },
            {
                "no": 2,
                "title_zh": "差不多",
                "title_uz": "deyarli, taxminan",
                "title_ru": "почти, приблизительно",
                "title_tj": "тақрибан, қариб ки",
                "rule_uz": "'Deyarli, taxminan, xuddi shunday' ma'nosini beradi. Miqdor yoki sifat jihatidan o'xshashlikni bildiradi.",
                "rule_ru": "Означает 'почти, приблизительно, примерно одинаково'. Выражает сходство по количеству или качеству.",
                "rule_tj": "Маънои 'тақрибан, қариб ки' дорад. Шабоҳатро аз ҷиҳати миқдор ё сифат ифода мекунад.",
                "examples": [
                    {"zh": "差不多十五个人来了。", "pinyin": "",
                     "uz": "Taxminan o'n besh kishi keldi.",
                     "ru": "Пришло примерно пятнадцать человек.",
                     "tj": "Тақрибан понздаҳ нафар омад."},
                    {"zh": "我们俩的想法差不多。", "pinyin": "",
                     "uz": "Bizning ikkalamizning fikrimiz deyarli bir xil.",
                     "ru": "Наши с тобой мысли почти одинаковые.",
                     "tj": "Фикри мо ду нафар тақрибан якхела аст."},
                ],
            },
            {
                "no": 3,
                "title_zh": "弄 + 结果补语",
                "title_uz": "弄 + natija to'ldiruvchisi",
                "title_ru": "弄 + результативное дополнение",
                "title_tj": "弄 + иловаи натиҷа",
                "rule_uz": "'弄' fe'li + natija to'ldiruvchisi qo'shilib, biror natijaga erishishni bildiradi. Masalan: 弄坏 (buzdim), 弄脏 (kirdim), 弄好 (yakladim).",
                "rule_ru": "Глагол '弄' + результативное дополнение обозначает достижение какого-либо результата. Например: 弄坏 (сломал), 弄脏 (испачкал), 弄好 (доделал).",
                "rule_tj": "Феъли '弄' + иловаи натиҷа маънои расидан ба натиҷаеро дорад. Масалан: 弄坏 (шикастам), 弄脏 (олудам), 弄好 (тайёр кардам).",
                "examples": [
                    {"zh": "对不起，我把你的书弄坏了。", "pinyin": "",
                     "uz": "Kechirasiz, men sizning kitobingizni buzdim.",
                     "ru": "Извините, я сломал вашу книгу.",
                     "tj": "Бубахшед, ман китоби шуморо шикастам."},
                    {"zh": "这个问题我弄清楚了。", "pinyin": "",
                     "uz": "Bu masalani men aniqladim.",
                     "ru": "Этот вопрос я прояснил.",
                     "tj": "Ин масаларо ман равшан кардам."},
                ],
            },
            {
                "no": 4,
                "title_zh": "帮",
                "title_uz": "yordam bermoq",
                "title_ru": "помогать",
                "title_tj": "кӯмак кардан",
                "rule_uz": "'帮' — 'yordam bermoq' ma'nosida ishlatiladi. 帮 + kishi + fe'l yoki 帮助 + kishi + fe'l shaklida qo'llanadi.",
                "rule_ru": "'帮' используется в значении 'помогать'. Употребляется в форме 帮 + человек + глагол или 帮助 + человек + глагол.",
                "rule_tj": "'帮' бо маънои 'кӯмак кардан' истифода мешавад. Дар шакли 帮 + одам + феъл ё 帮助 + одам + феъл ба кор меравад.",
                "examples": [
                    {"zh": "他帮我学汉语。", "pinyin": "",
                     "uz": "U menga xitoy tilini o'rgatadi (yordam beradi).",
                     "ru": "Он помогает мне учить китайский.",
                     "tj": "Ӯ ба ман хитоӣ омӯхтанро кӯмак мекунад."},
                    {"zh": "朋友帮助我解决了问题。", "pinyin": "",
                     "uz": "Do'st menga muammoni hal qilishda yordam berdi.",
                     "ru": "Друг помог мне решить проблему.",
                     "tj": "Дӯст ба ман дар ҳал кардани мушкил кӯмак кард."},
                ],
            },
            {
                "no": 5,
                "title_zh": "尽管……但是/还是……",
                "title_uz": "garchi...bo'lsa ham...baribir",
                "title_ru": "хотя...но всё равно",
                "title_tj": "гарчанде...аммо боз ҳам",
                "rule_uz": "'Garchi...bo'lsa ham' ma'nosini beradi. Birinchi gapda 尽管, ikkinchi gapda 但是 yoki 还是 ishlatiladi.",
                "rule_ru": "Означает 'хотя...всё равно'. В первом предложении используется 尽管, во втором — 但是 или 还是.",
                "rule_tj": "Маънои 'гарчанде...аммо боз ҳам' дорад. Дар ҷумлаи аввал 尽管, дар дуввум 但是 ё 还是 истифода мешавад.",
                "examples": [
                    {"zh": "尽管大家都很忙，但真正的友谊经得起考验。", "pinyin": "",
                     "uz": "Garchi hammaning vaqti yo'q bo'lsa ham, haqiqiy do'stlik bardosh beradi.",
                     "ru": "Хотя все очень заняты, настоящая дружба выдерживает испытания.",
                     "tj": "Гарчанде ҳамаи вақт надоранд, дӯстии воқеӣ имтиҳонро тоб меорад."},
                    {"zh": "尽管很远，他还是来了。", "pinyin": "",
                     "uz": "Garchi uzoq bo'lsa ham, u baribir keldi.",
                     "ru": "Хотя это далеко, он всё равно пришёл.",
                     "tj": "Гарчанде дур буд, ӯ боз ҳам омад."},
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
                "instruction_ru": "Напишите китайский эквивалент следующих слов:",
                "instruction_tj": "Муодили хитоии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "moslashmoq", "prompt_ru": "адаптироваться", "prompt_tj": "мутобиқ шудан", "answer": "适应", "pinyin": "shìyìng"},
                    {"prompt_uz": "do'st orttirmoq", "prompt_ru": "заводить друзей", "prompt_tj": "дӯст пайдо кардан", "answer": "交朋友", "pinyin": "jiāo péngyou"},
                    {"prompt_uz": "haqiqiy", "prompt_ru": "настоящий", "prompt_tj": "воқеӣ", "answer": "真正", "pinyin": "zhēnzhèng"},
                    {"prompt_uz": "do'stlik", "prompt_ru": "дружба", "prompt_tj": "дӯстӣ", "answer": "友谊", "pinyin": "yǒuyì"},
                    {"prompt_uz": "qaytadan", "prompt_ru": "заново", "prompt_tj": "аз нав", "answer": "重新", "pinyin": "chóngxīn"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский эквивалент следующих слов:",
                "instruction_tj": "Муодили ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "正好", "prompt_ru": "正好", "prompt_tj": "正好", "answer": "aynan, to'g'ri keldi", "pinyin": "zhènghǎo"},
                    {"prompt_uz": "差不多", "prompt_ru": "差不多", "prompt_tj": "差不多", "answer": "deyarli, taxminan", "pinyin": "chàbuduō"},
                    {"prompt_uz": "联系", "prompt_ru": "联系", "prompt_tj": "联系", "answer": "aloqa qilmoq", "pinyin": "liánxì"},
                    {"prompt_uz": "尽管", "prompt_ru": "尽管", "prompt_tj": "尽管", "answer": "garchi...bo'lsa ham", "pinyin": "jǐnguǎn"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (正好、差不多、尽管、专门、重新):",
                "instruction_ru": "Выберите подходящее слово (正好、差不多、尽管、专门、重新):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (正好、差不多、尽管、专门、重新):",
                "items": [
                    {"prompt_uz": "他______从上海飞回来参加聚会。", "prompt_ru": "他______从上海飞回来参加聚会。", "prompt_tj": "他______从上海飞回来参加聚会。", "answer": "专门", "pinyin": "zhuānmén"},
                    {"prompt_uz": "______很忙，他还是来帮我了。", "prompt_ru": "______很忙，他还是来帮我了。", "prompt_tj": "______很忙，他还是来帮我了。", "answer": "尽管", "pinyin": "jǐnguǎn"},
                    {"prompt_uz": "我找你，你______来了。", "prompt_ru": "我找你，你______来了。", "prompt_tj": "我找你，你______来了。", "answer": "正好", "pinyin": "zhènghǎo"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["适应", "交朋友", "真正", "友谊", "重新"]},
            {"no": 2, "answers": ["aynan, to'g'ri keldi", "deyarli, taxminan", "aloqa qilmoq", "garchi...bo'lsa ham"]},
            {"no": 3, "answers": ["专门", "尽管", "正好"]},
        ],
        ensure_ascii=False,
    ),
    "homework_json": json.dumps(
        [
            {
                "no": 1,
                "instruction_uz": "Quyidagi so'zlardan foydalanib 3 ta gap tuzing:",
                "instruction_ru": "Составьте 3 предложения, используя следующие слова:",
                "instruction_tj": "Бо истифода аз калимаҳои зерин 3 ҷумла созед:",
                "words": ["适应", "联系", "友谊", "了解"],
                "example": "来到新城市后，我慢慢地适应了这里的生活。",
            },
            {
                "no": 2,
                "instruction_uz": "'尽管...但是...' qolipidan foydalanib 2 ta gap tuzing.",
                "instruction_ru": "Составьте 2 предложения с конструкцией '尽管...但是...'.",
                "instruction_tj": "Бо истифода аз қолипи '尽管...但是...' 2 ҷумла созед.",
                "topic_uz": "do'stlik va munosabatlar mavzusida",
                "topic_ru": "на тему дружбы и отношений",
                "topic_tj": "дар мавзӯи дӯстӣ ва муносибатҳо",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Sizning eng yaqin do'stingiz haqida yozing. 你最好的朋友是什么样的人？",
                "topic_ru": "Напишите о вашем лучшем друге. 你最好的朋友是什么样的人？",
                "topic_tj": "Дар бораи наздиктарин дӯсти худ нависед. 你最好的朋友是什么样的人？",
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
