import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 7,
    "lesson_code": "HSK4-L07",
    "title": "最好的医生是自己",
    "goal": json.dumps({"uz": "sog'liq, kasallik va sport haqida gapirish; 估计, 再也不, 合适, 出现, 来不及 grammatik qoliplarini o'zlashtirish", "ru": "говорить о здоровье, болезнях и спорте; освоить конструкции 估计, 再也不, 合适, 出现, 来不及", "tj": "гуфтугӯ дар бораи саломатӣ, беморӣ ва варзиш; аз худ кардани қолипҳои 估计, 再也不, 合适, 出现, 来不及"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Eng yaxshi shifokor o'zingiz' mavzusiga bag'ishlangan. Unda sog'lom hayot kechirish, kasallikdan saqlanish va sport haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 估计, 再也不, 合适, 出现, 来不及.", "ru": "Этот урок посвящён теме 'Лучший врач — это вы сами'. В нём вы научитесь говорить о здоровом образе жизни, профилактике заболеваний и спорте. Основные грамматические конструкции: 估计, 再也不, 合适, 出现, 来不及.", "tj": "Ин дарс ба мавзӯи 'Беҳтарин духтур худи шумо аст' бахшида шудааст. Дар он зиндагии солим, пешгирии беморӣ ва варзиш омӯхта мешавад. Қолипҳои асосии грамматикӣ: 估计, 再也不, 合适, 出现, 来不及."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "流血", "pinyin": "liú xiě", "pos": "v.", "uz": "qon ketmoq, qon oqmoq", "ru": "кровоточить, идти крови", "tj": "хун рафтан, хун ҷорӣ шудан"},
            {"no": 2, "zh": "擦", "pinyin": "cā", "pos": "v.", "uz": "artmoq, tozalamoq", "ru": "вытирать, протирать", "tj": "артидан, тоза кардан"},
            {"no": 3, "zh": "气候", "pinyin": "qìhòu", "pos": "n.", "uz": "iqlim, ob-havo", "ru": "климат, погода", "tj": "иқлим, ҳаво"},
            {"no": 4, "zh": "估计", "pinyin": "gūjì", "pos": "v.", "uz": "taxmin qilmoq, hisoblash", "ru": "оценивать, предполагать", "tj": "тахмин кардан, ҳисоб кардан"},
            {"no": 5, "zh": "咳嗽", "pinyin": "késou", "pos": "v.", "uz": "yo'talmoq", "ru": "кашлять", "tj": "сулфа задан"},
            {"no": 6, "zh": "严重", "pinyin": "yánzhòng", "pos": "adj.", "uz": "jiddiy, og'ir (holat)", "ru": "серьёзный, тяжёлый", "tj": "ҷиддӣ, вазнин"},
            {"no": 7, "zh": "窗户", "pinyin": "chuānghù", "pos": "n.", "uz": "deraza", "ru": "окно", "tj": "тиреза"},
            {"no": 8, "zh": "空气", "pinyin": "kōngqì", "pos": "n.", "uz": "havo", "ru": "воздух", "tj": "ҳаво"},
            {"no": 9, "zh": "抽烟", "pinyin": "chōu yān", "pos": "v.", "uz": "chekmoq (sigaret)", "ru": "курить (сигарету)", "tj": "тамоку кашидан"},
            {"no": 10, "zh": "动作", "pinyin": "dòngzuò", "pos": "n.", "uz": "harakat, imo-ishora", "ru": "движение, действие, жест", "tj": "ҳаракат, имо-ишора"},
            {"no": 11, "zh": "帅", "pinyin": "shuài", "pos": "adj.", "uz": "kelishgan, chiroyli (erkak)", "ru": "красивый, привлекательный (о мужчине)", "tj": "зебо, хушрӯй (дар бораи мард)"},
            {"no": 12, "zh": "出现", "pinyin": "chūxiàn", "pos": "v.", "uz": "paydo bo'lmoq, namoyon bo'lmoq", "ru": "появляться, возникать", "tj": "пайдо шудан, зоҳир шудан"},
            {"no": 13, "zh": "后悔", "pinyin": "hòuhuǐ", "pos": "v.", "uz": "pushaymon bo'lmoq, afsuslanmoq", "ru": "сожалеть, раскаиваться", "tj": "пушаймон шудан, афсӯс хӯрдан"},
            {"no": 14, "zh": "来不及", "pinyin": "láibují", "pos": "v.", "uz": "vaqt yetmaydi, kech qolmoq", "ru": "не успевать, опаздывать", "tj": "вақт намерасад, кеч мондан"},
            {"no": 15, "zh": "反对", "pinyin": "fǎnduì", "pos": "v.", "uz": "qarshi bo'lmoq, e'tiroz bildirmoq", "ru": "возражать, быть против", "tj": "муқобил будан, эътироз баён кардан"},
            {"no": 16, "zh": "健康", "pinyin": "jiànkāng", "pos": "adj./n.", "uz": "sog'lom; sog'liq", "ru": "здоровый; здоровье", "tj": "солим; саломатӣ"},
            {"no": 17, "zh": "锻炼", "pinyin": "duànliàn", "pos": "v.", "uz": "mashq qilmoq, sport bilan shug'ullanmoq", "ru": "тренироваться, заниматься спортом", "tj": "машқ кардан, варзиш кардан"},
            {"no": 18, "zh": "休息", "pinyin": "xiūxi", "pos": "v.", "uz": "dam olmoq", "ru": "отдыхать", "tj": "истироҳат кардан"},
            {"no": 19, "zh": "医生", "pinyin": "yīshēng", "pos": "n.", "uz": "shifokor, doktor", "ru": "врач, доктор", "tj": "духтур, табиб"},
            {"no": 20, "zh": "合适", "pinyin": "héshì", "pos": "adj.", "uz": "mos, to'g'ri keladigan", "ru": "подходящий, уместный", "tj": "мувофиқ, дуруст"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "小李 va 小林 ob-havo va sog'liq haqida gaplashadi",
                "scene_ru": "小李 и 小林 обсуждают погоду и самочувствие",
                "scene_tj": "小李 ва 小林 дар бораи ҳаво ва саломатӣ гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "小李", "zh": "你的鼻子怎么流血了？使用纸巾擦擦。", "pinyin": "",
                     "uz": "Burnig'iz nima uchun qon ketmoqda? Doka bilan arting.",
                     "ru": "Почему у тебя носовое кровотечение? Вытри салфеткой.",
                     "tj": "Чаро бинии ту хун мерезад? Бо дастмол арт."},
                    {"speaker": "小林", "zh": "我还不习惯北方的气候，估计是天气不是很干，你怎么这么多？", "pinyin": "",
                     "uz": "Men hali shimoliy iqlimga ko'nikmaganman, taxminan havo quruq bo'lgani uchun, siz nega bu qadar ko'p?",
                     "ru": "Я ещё не привык к северному климату, наверное, из-за сухого воздуха — а у тебя так часто бывает?",
                     "tj": "Ман ҳанӯз ба иқлими шимолӣ одат накардам, тахминан аз хушкии ҳаво — шумо чаро ин қадар зиёд аст?"},
                    {"speaker": "小李", "zh": "那说明你要多喝水，这种天气容易咳嗽，要注意身体啊。", "pinyin": "",
                     "uz": "Demak ko'p suv ichishingiz kerak, bunday havoda yo'tal osonlikcha bo'ladi, sog'lig'ingizga e'tibor bering.",
                     "ru": "Значит, нужно больше пить воды — в такую погоду легко закашляться, береги здоровье.",
                     "tj": "Яъне бояд бештар об нӯшӣ — дар ин гуна ҳаво сулфа задан осон аст, ба саломатиат диққат кун."},
                    {"speaker": "小林", "zh": "没有，我只是有点儿咳嗽，不严重，多喝点儿水就好了，另外要经常开窗户，让空气流通。", "pinyin": "",
                     "uz": "Yo'q, biroz yo'talim bor, jiddiy emas, ko'p suv ichsam bo'ladi, bundan tashqari tez-tez deraza ochib, havo almashtirib turish kerak.",
                     "ru": "Нет, я просто немного кашляю, не серьёзно — если побольше пить воды, пройдёт. Ещё нужно почаще открывать окна, чтобы воздух циркулировал.",
                     "tj": "Не, ман танҳо каме сулфа мезанам, ҷиддӣ нест — агар бештар об нӯшам, мегузарад. Ғайр аз ин бояд зудтар-зудтар тиреза кушод, то ҳаво давр занад."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "小夏 va 小雨 chekishni tashlash haqida gaplashadi",
                "scene_ru": "小夏 и 小雨 обсуждают отказ от курения",
                "scene_tj": "小夏 ва 小雨 дар бораи тарки тамоку гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "小夏", "zh": "你不是说不抽烟了吗？", "pinyin": "",
                     "uz": "Sigaret chekmaydi demaganmidingiz?",
                     "ru": "Разве ты не говорил, что больше не будешь курить?",
                     "tj": "Магар нагуфтӣ, ки дигар тамоку намекашӣ?"},
                    {"speaker": "小雨", "zh": "是老毛病了，就让我抽完这一根以后不再抽了。", "pinyin": "",
                     "uz": "Bu eski odat, mana shuni tugatib, keyin boshqa chekmayman.",
                     "ru": "Это старая привычка, позволь докурить эту последнюю — потом больше не буду.",
                     "tj": "Ин одати кӯҳна аст, биёй ин якиро тамом кунам — баъд дигар намекашам."},
                    {"speaker": "小夏", "zh": "你的身体出现了一些问题，如果再不改变的话，后来就来不及了。", "pinyin": "",
                     "uz": "Sizning sog'lig'ingizda ba'zi muammolar paydo bo'ldi, agar o'zgartirmasangiz, keyinroq kech bo'lib qoladi.",
                     "ru": "У тебя появились некоторые проблемы со здоровьем — если не изменишь образ жизни, потом будет уже поздно.",
                     "tj": "Дар саломатии ту баъзе мушкилот пайдо шуд — агар тағйир надиҳӣ, баъдтар кеч мешавад."},
                    {"speaker": "小雨", "zh": "我自己也知道，再不见的话对身体不好，我家人也一直反对我抽烟，拉我去健身房，时时刻刻提醒我。", "pinyin": "",
                     "uz": "Men o'zim ham bilaman, davom etsam sog'lig'm yomonlashadi, oilam ham chekishimga doim qarshi, meni sport zaliga olib boradi, har doim eslatib turadi.",
                     "ru": "Я и сам знаю — если продолжать, здоровью будет плохо. Семья тоже всегда против того, чтобы я курил, тянет меня в спортзал, постоянно напоминает.",
                     "tj": "Ман худам ҳам медонам — агар давом кунам, саломатӣ бад мешавад. Оилаам ҳам ҳамеша муқобили тамоку кашиданам аст, маро ба толори варзишӣ мебарад, ҳамеша ёдоварӣ мекунад."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "估计",
                "title_uz": "taxmin qilmoq",
                "title_ru": "предполагать, оценивать",
                "title_tj": "тахмин кардан",
                "rule_uz": "'Taxmin qilmoq, hisoblash' ma'nosini beradi. Aniq ma'lumot bo'lmagan holda taxminan qanday ekanligi haqida fikr bildiradi.",
                "rule_ru": "Означает 'предполагать, оценивать'. Используется для выражения предположения при отсутствии точных данных.",
                "rule_tj": "Маънои 'тахмин кардан, ҳисоб кардан' дорад. Бе маълумоти дақиқ ақида баён кардан.",
                "examples": [
                    {"zh": "估计是天气太干了。", "pinyin": "",
                     "uz": "Taxminan havo juda quruq bo'lgani uchun.",
                     "ru": "Наверное, это из-за слишком сухого воздуха.",
                     "tj": "Тахминан аз хеле хушкии ҳаво."},
                    {"zh": "我估计他今天不会来了。", "pinyin": "",
                     "uz": "Men taxmin qilaman, u bugun kelmaydi.",
                     "ru": "Я полагаю, что сегодня он не придёт.",
                     "tj": "Ман тахмин мекунам, ки ӯ имрӯз намеояд."},
                ],
            },
            {
                "no": 2,
                "title_zh": "再也不……了",
                "title_uz": "boshqa hech qachon...emas",
                "title_ru": "больше никогда не...",
                "title_tj": "дигар ҳеч вақт не...",
                "rule_uz": "'Boshqa hech qachon...emas' ma'nosini beradi. Biror narsa endi qilinmaydi yoki sodir bo'lmaydi degan qat'iy qarorni bildiradi.",
                "rule_ru": "Означает 'больше никогда не...'. Выражает твёрдое решение о том, что что-то больше никогда не произойдёт.",
                "rule_tj": "Маънои 'дигар ҳеч вақт не...' дорад. Қарори қатъии он, ки чизе дигар ҳеч вақт рӯй намедиҳад.",
                "examples": [
                    {"zh": "我再也不抽烟了！", "pinyin": "",
                     "uz": "Men boshqa hech qachon chekmayman!",
                     "ru": "Я больше никогда не буду курить!",
                     "tj": "Ман дигар ҳеч вақт тамоку намекашам!"},
                    {"zh": "他说再也不迟到了。", "pinyin": "",
                     "uz": "U boshqa hech qachon kech qolmasligini aytdi.",
                     "ru": "Он сказал, что больше никогда не будет опаздывать.",
                     "tj": "Ӯ гуфт, ки дигар ҳеч вақт дер намеояд."},
                ],
            },
            {
                "no": 3,
                "title_zh": "合适",
                "title_uz": "mos, to'g'ri keladigan",
                "title_ru": "подходящий, уместный",
                "title_tj": "мувофиқ, дуруст",
                "rule_uz": "'Mos, to'g'ri keladigan' ma'nosini beradi. Biror narsa biror holat yoki kishiga mos ekanligini bildiradi.",
                "rule_ru": "Означает 'подходящий, уместный'. Указывает, что что-то подходит для определённой ситуации или человека.",
                "rule_tj": "Маънои 'мувофиқ, дуруст' дорад. Нишон медиҳад, ки чизе ба ҳолат ё шахси муайян мувофиқ аст.",
                "examples": [
                    {"zh": "每天跑步对健康很合适。", "pinyin": "",
                     "uz": "Har kuni yugurish sog'liq uchun juda mos.",
                     "ru": "Ежедневный бег очень подходит для здоровья.",
                     "tj": "Давидан ҳар рӯз барои саломатӣ хеле мувофиқ аст."},
                    {"zh": "这种药对你的情况合适吗？", "pinyin": "",
                     "uz": "Bu dori sizning holatingizga mos keladimi?",
                     "ru": "Это лекарство подходит для вашего состояния?",
                     "tj": "Ин дору ба ҳолати шумо мувофиқ аст?"},
                ],
            },
            {
                "no": 4,
                "title_zh": "出现",
                "title_uz": "paydo bo'lmoq, namoyon bo'lmoq",
                "title_ru": "появляться, возникать",
                "title_tj": "пайдо шудан, зоҳир шудан",
                "rule_uz": "'Paydo bo'lmoq, namoyon bo'lmoq' ma'nosini beradi. Oldin bo'lmagan narsa endi bo'ladigan bo'lishini bildiradi.",
                "rule_ru": "Означает 'появляться, возникать'. Указывает, что то, чего раньше не было, теперь появилось.",
                "rule_tj": "Маънои 'пайдо шудан, зоҳир шудан' дорад. Нишон медиҳад, ки чизе, ки пеш набуд, ҳоло пайдо шуд.",
                "examples": [
                    {"zh": "身体出现了一些问题。", "pinyin": "",
                     "uz": "Tanada ba'zi muammolar paydo bo'ldi.",
                     "ru": "Появились некоторые проблемы со здоровьем.",
                     "tj": "Дар бадан баъзе мушкилот пайдо шуд."},
                    {"zh": "他突然出现在我面前。", "pinyin": "",
                     "uz": "U to'satdan ro'paramda paydo bo'ldi.",
                     "ru": "Он неожиданно появился передо мной.",
                     "tj": "Ӯ ногаҳон дар рӯ ба рӯи ман пайдо шуд."},
                ],
            },
            {
                "no": 5,
                "title_zh": "来不及",
                "title_uz": "vaqt yetmaydi, kech qolmoq",
                "title_ru": "не успевать, слишком поздно",
                "title_tj": "вақт намерасад, кеч мондан",
                "rule_uz": "'Vaqt yetmaydi, kech qolmoq' ma'nosini beradi. Biror narsa uchun vaqt qolmaganligini bildiradi.",
                "rule_ru": "Означает 'не успевать, слишком поздно'. Указывает, что времени на что-то уже не осталось.",
                "rule_tj": "Маънои 'вақт намерасад, кеч мондан' дорад. Нишон медиҳад, ки барои чизе вақт намондааст.",
                "examples": [
                    {"zh": "如果再不改变，后来就来不及了。", "pinyin": "",
                     "uz": "Agar o'zgartirmasang, keyinroq kech bo'lib qoladi.",
                     "ru": "Если не изменишь образ жизни, потом будет слишком поздно.",
                     "tj": "Агар тағйир надиҳӣ, баъдтар кеч мешавад."},
                    {"zh": "我来不及吃早饭就出发了。", "pinyin": "",
                     "uz": "Nonushta qilishga vaqtim bo'lmay yo'lga chiqdim.",
                     "ru": "Я вышел, не успев позавтракать.",
                     "tj": "Ман бе хӯрдани субҳона ба роҳ баромадам."},
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
                    {"prompt_uz": "iqlim, ob-havo", "prompt_ru": "климат, погода", "prompt_tj": "иқлим, ҳаво", "answer": "气候", "pinyin": "qìhòu"},
                    {"prompt_uz": "yo'talmoq", "prompt_ru": "кашлять", "prompt_tj": "сулфа задан", "answer": "咳嗽", "pinyin": "késou"},
                    {"prompt_uz": "deraza", "prompt_ru": "окно", "prompt_tj": "тиреза", "answer": "窗户", "pinyin": "chuānghù"},
                    {"prompt_uz": "pushaymon bo'lmoq", "prompt_ru": "сожалеть", "prompt_tj": "пушаймон шудан", "answer": "后悔", "pinyin": "hòuhuǐ"},
                    {"prompt_uz": "mashq qilmoq", "prompt_ru": "тренироваться", "prompt_tj": "машқ кардан", "answer": "锻炼", "pinyin": "duànliàn"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский эквивалент следующих слов:",
                "instruction_tj": "Муодили ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "估计", "prompt_ru": "估计", "prompt_tj": "估计", "answer": "taxmin qilmoq", "pinyin": "gūjì"},
                    {"prompt_uz": "严重", "prompt_ru": "严重", "prompt_tj": "严重", "answer": "jiddiy, og'ir", "pinyin": "yánzhòng"},
                    {"prompt_uz": "反对", "prompt_ru": "反对", "prompt_tj": "反对", "answer": "qarshi bo'lmoq", "pinyin": "fǎnduì"},
                    {"prompt_uz": "来不及", "prompt_ru": "来不及", "prompt_tj": "来不及", "answer": "vaqt yetmaydi, kech qolmoq", "pinyin": "láibují"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (估计、再也不、出现、合适、来不及):",
                "instruction_ru": "Выберите подходящее слово (估计、再也不、出现、合适、来不及):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (估计、再也不、出现、合适、来不及):",
                "items": [
                    {"prompt_uz": "他说这次以后______喝酒了。", "prompt_ru": "他说这次以后______喝酒了。", "prompt_tj": "他说这次以后______喝酒了。", "answer": "再也不", "pinyin": "zài yě bù"},
                    {"prompt_uz": "最近他身体______了一些问题。", "prompt_ru": "最近他身体______了一些问题。", "prompt_tj": "最近他身体______了一些问题。", "answer": "出现", "pinyin": "chūxiàn"},
                    {"prompt_uz": "______他现在在图书馆。", "prompt_ru": "______他现在在图书馆。", "prompt_tj": "______他现在在图书馆。", "answer": "估计", "pinyin": "gūjì"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["气候", "咳嗽", "窗户", "后悔", "锻炼"]},
            {"no": 2, "answers": ["taxmin qilmoq", "jiddiy, og'ir", "qarshi bo'lmoq", "vaqt yetmaydi, kech qolmoq"]},
            {"no": 3, "answers": ["再也不", "出现", "估计"]},
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
                "words": ["健康", "锻炼", "估计", "严重"],
                "example": "估计每天锻炼对健康很有好处，不要等问题严重才去医院。",
            },
            {
                "no": 2,
                "instruction_uz": "'再也不...了' va '来不及' qoliplaridan foydalanib har biridan 2 ta gap tuzing.",
                "instruction_ru": "Составьте по 2 предложения с конструкциями '再也不...了' и '来不及'.",
                "instruction_tj": "Бо истифода аз қолипҳои '再也不...了' ва '来不及' аз ҳар кадоме 2 ҷумла созед.",
                "topic_uz": "sog'liq va yomon odatlardan xalos bo'lish mavzusida",
                "topic_ru": "на тему здоровья и избавления от вредных привычек",
                "topic_tj": "дар мавзӯи саломатӣ ва халосӣ аз одатҳои бад",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Sog'lom yashash uchun nima qilish kerak? 怎么样才能保持健康的生活？",
                "topic_ru": "Что нужно делать для здорового образа жизни? 怎么样才能保持健康的生活？",
                "topic_tj": "Барои зиндагии солим чӣ бояд кард? 怎么样才能保持健康的生活？",
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
