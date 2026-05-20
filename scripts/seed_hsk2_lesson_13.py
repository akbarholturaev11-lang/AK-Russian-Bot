import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 13,
    "lesson_code": "HSK2-L13",
    "title": "门开着呢",
    "goal": json.dumps({"uz": "Davom etayotgan holatni bildiruvchi '着' yuklamasini, 'wǎng' yo'nalish ko'makchisini va '不是……吗' ritorik savol shaklini o'rganish.", "ru": "Изучение частицы '着', обозначающей продолжающееся состояние, предлога направления 'wǎng' и риторической конструкции '不是……吗'.", "tj": "Омӯзиши зарраи '着' ифодакунандаи ҳолати давомдор, пешоянди самт 'wǎng' ва шакли пурсиши риторикии '不是……吗'."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda biz holatlarning davomiyligini ifodalashni o'rganamiz. Ofis, ko'cha va sport maydonchasida bo'lib o'tgan suhbatlar orqali '着' yuklamasining ishlatilishini, yo'nalish bildiruvchi 'wǎng' so'zini va ritorik savol shaklini mashq qilamiz. Shuningdek, tanish kiritish va yo'l ko'rsatish iboralarini o'zlashtiramiz.", "ru": "На этом уроке мы учимся выражать продолжительность состояний. Отрабатываем использование частицы '着', слова 'wǎng' для обозначения направления и риторического вопроса через диалоги в офисе, на улице и на спортивной площадке. Также осваиваем выражения для знакомства и указания пути.", "tj": "Дар ин дарс ёд мегирем давомнокии ҳолатҳоро ифода кунем. Тавассути муколамаҳо дар дафтар, кӯча ва майдони варзишӣ истифодаи зарраи '着', калимаи 'wǎng' барои нишон додани самт ва шакли пурсиши риторикиро машқ мекунем. Инчунин ибораҳои шинос кардан ва роҳ нишон доданро аз бар мекунем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "着", "pinyin": "zhe", "pos": "part.", "uz": "davom etayotgan holatni bildiruvchi yuklama", "ru": "частица продолжающегося состояния", "tj": "зарраи ҳолати давомдор"},
        {"no": 2, "zh": "手", "pinyin": "shǒu", "pos": "n.", "uz": "qo'l", "ru": "рука", "tj": "даст"},
        {"no": 3, "zh": "拿", "pinyin": "ná", "pos": "v.", "uz": "ushlamoq, ko'tarmoq", "ru": "держать, нести", "tj": "нигоҳ доштан, бардоштан"},
        {"no": 4, "zh": "铅笔", "pinyin": "qiānbǐ", "pos": "n.", "uz": "qo'rg'oshin qalam", "ru": "карандаш", "tj": "қалами оддӣ"},
        {"no": 5, "zh": "班", "pinyin": "bān", "pos": "n.", "uz": "sinf, guruh", "ru": "класс, группа", "tj": "синф, гурӯҳ"},
        {"no": 6, "zh": "长", "pinyin": "zhǎng", "pos": "v./adj.", "uz": "o'smoq; uzun", "ru": "расти; длинный", "tj": "калон шудан; дароз"},
        {"no": 7, "zh": "笑", "pinyin": "xiào", "pos": "v.", "uz": "kulmoq", "ru": "смеяться, улыбаться", "tj": "хандидан"},
        {"no": 8, "zh": "宾馆", "pinyin": "bīnguǎn", "pos": "n.", "uz": "mehmonxona", "ru": "гостиница", "tj": "меҳмонхона"},
        {"no": 9, "zh": "一直", "pinyin": "yìzhí", "pos": "adv.", "uz": "to'g'riga, to'xtovsiz", "ru": "прямо, постоянно", "tj": "рост, пайваста"},
        {"no": 10, "zh": "往", "pinyin": "wǎng", "pos": "prep.", "uz": "tomon, yo'nalish bildiradi", "ru": "в сторону, по направлению к", "tj": "ба самти, нишонадиҳандаи самт"},
        {"no": 11, "zh": "路口", "pinyin": "lùkǒu", "pos": "n.", "uz": "yo'l chorrahasi, chorraha", "ru": "перекрёсток", "tj": "чорраҳа, буриши роҳ"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Ofisda",
            "scene_ru": "В офисе",
            "scene_tj": "Дар дафтар",
            "dialogue": [
                {"speaker": "A", "zh": "门开着呢，请进。", "pinyin": "Mén kāi zhe ne, qǐng jìn.", "uz": "Eshik ochiq turibdi, marhamat kiring.", "ru": "Дверь открыта, пожалуйста, входите.", "tj": "Дар кушода истодааст, марҳамат даред."},
                {"speaker": "B", "zh": "请问，张先生在吗？", "pinyin": "Qǐngwèn, Zhāng xiānsheng zài ma?", "uz": "Iltimos, Chjan janob bormi?", "ru": "Скажите, пожалуйста, господин Чжан здесь?", "tj": "Бубахшед, ҷаноби Чжан ҳастанд?"},
                {"speaker": "A", "zh": "他出去了。你下午再来吧。", "pinyin": "Tā chūqù le. Nǐ xiàwǔ zài lái ba.", "uz": "U chiqib ketdi. Siz tushdan keyin yana keling.", "ru": "Он вышел. Приходите ещё раз после полудня.", "tj": "Ӯ берун рафт. Шумо баъд аз нисфирӯзӣ боз биёед."},
                {"speaker": "B", "zh": "好的，谢谢！", "pinyin": "Hǎo de, xièxie!", "uz": "Yaxshi, rahmat!", "ru": "Хорошо, спасибо!", "tj": "Хуб, ташаккур!"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Ofisda",
            "scene_ru": "В офисе",
            "scene_tj": "Дар дафтар",
            "dialogue": [
                {"speaker": "A", "zh": "那个正在说话的女孩子是谁？", "pinyin": "Nàge zhèngzài shuōhuà de nǚ háizi shì shéi?", "uz": "O'sha hozir gapiriyotgan qiz kim?", "ru": "Кто та девушка, которая сейчас разговаривает?", "tj": "Он духтаре ки ҳоло гап мезанад кист?"},
                {"speaker": "B", "zh": "我知道她的名字，她姓杨，叫杨笑笑。她姐姐是我同学。", "pinyin": "Wǒ zhīdào tā de míngzi, tā xìng Yáng, jiào Yáng Xiàoxiào. Tā jiějie shì wǒ tóngxué.", "uz": "Men uning ismini bilaman, familiyasi Yang, ismi Yang Syaosyao. Uning opasi mening sinfdoshim.", "ru": "Я знаю её имя, её фамилия Ян, зовут Ян Сяосяо. Её сестра — моя одноклассница.", "tj": "Ман номашро медонам, насабаш Ян аст, номаш Ян Сяосяо аст. Хоҳараш ҳамсинфи ман аст."},
                {"speaker": "A", "zh": "那个手里拿着铅笔的呢？", "pinyin": "Nàge shǒu lǐ ná zhe qiānbǐ de ne?", "uz": "Qo'lida qalam ushlab turgan odam-chi?", "ru": "А тот, кто держит в руке карандаш?", "tj": "Он касе ки дар дасташ қалам дорад чӣ?"},
                {"speaker": "B", "zh": "我不认识。", "pinyin": "Wǒ bù rènshi.", "uz": "Men uni tanimas.", "ru": "Не знаю его.", "tj": "Ман ӯро намешиносам."}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Sport maydonchasida",
            "scene_ru": "На спортивной площадке",
            "scene_tj": "Дар майдони варзишӣ",
            "dialogue": [
                {"speaker": "A", "zh": "听说你有女朋友了？我认识她吗？", "pinyin": "Tīngshuō nǐ yǒu nǚpéngyou le? Wǒ rènshi tā ma?", "uz": "Eshitdimki, sizda qiz do'st bor? Men uni tanisam?", "ru": "Говорят, у тебя есть девушка? Я её знаю?", "tj": "Шунидам, ту дӯстдухтар дорӣ? Ман ӯро мешиносам?"},
                {"speaker": "B", "zh": "就是我们班那个长着两个大眼睛，非常爱笑的女孩子。", "pinyin": "Jiù shì wǒmen bān nàge zhǎng zhe liǎng ge dà yǎnjing, fēicháng ài xiào de nǚ háizi.", "uz": "Bizning sinfimizdagi o'sha ikki katta ko'zi bor, juda kulishni sevadigan qiz.", "ru": "Та девушка из нашего класса с двумя большими глазами, которая очень любит смеяться.", "tj": "Ҳамон духтаре аз синфи мо ки ду чашми калон дорад ва хеле механдад."},
                {"speaker": "A", "zh": "她不是有男朋友了吗？", "pinyin": "Tā bú shì yǒu nánpéngyou le ma?", "uz": "Uning yigit do'sti bor-ku?", "ru": "У неё же был парень?", "tj": "Магар ӯ дӯстписар надошт?"},
                {"speaker": "B", "zh": "那个已经是她的前男友了。", "pinyin": "Nàge yǐjīng shì tā de qián nányǒu le.", "uz": "U allaqachon uning sobiq yigit do'sti.", "ru": "Это уже её бывший парень.", "tj": "Он аллакай дӯстписари собиқи ӯ шудааст."}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Ko'chada",
            "scene_ru": "На улице",
            "scene_tj": "Дар кӯча",
            "dialogue": [
                {"speaker": "A", "zh": "请问，这儿离新京宾馆远吗？", "pinyin": "Qǐngwèn, zhèr lí Xīnjīng Bīnguǎn yuǎn ma?", "uz": "Iltimos, bu yerdan Syanjin mehmonxonasigacha uzoqmi?", "ru": "Скажите, пожалуйста, отсюда до гостиницы Синьцзин далеко?", "tj": "Бубахшед, аз ин ҷо то меҳмонхонаи Синьцзин дур аст?"},
                {"speaker": "B", "zh": "不远，走二十分钟就到了。", "pinyin": "Bù yuǎn, zǒu èrshí fēnzhōng jiù dào le.", "uz": "Uzoq emas, yigirma daqiqa yursangiz yetib olasiz.", "ru": "Недалеко, двадцать минут пешком — и вы на месте.", "tj": "Дур нест, бист дақиқа рафтед мерасед."},
                {"speaker": "A", "zh": "你能告诉我怎么走吗？", "pinyin": "Nǐ néng gàosu wǒ zěnme zǒu ma?", "uz": "Yo'lni aytib bera olasizmi?", "ru": "Вы можете объяснить, как пройти?", "tj": "Метавонед роҳро нишон диҳед?"},
                {"speaker": "B", "zh": "从这儿一直往前走，到了前面的路口再往右走。", "pinyin": "Cóng zhèr yìzhí wǎng qián zǒu, dào le qiánmian de lùkǒu zài wǎng yòu zǒu.", "uz": "Bu yerdan to'g'ri oldinga boring, oldindagi chorrahaga yetgach o'ngga buriling.", "ru": "Идите прямо отсюда, а на ближайшем перекрёстке поверните направо.", "tj": "Аз ин ҷо рост пеш равед, ба чорраҳаи пеш расидед ба тарафи рост гардед."}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "动态助词“着”",
            "title_uz": "'Zhe' harakat yuklamasi",
            "title_ru": "Динамическая частица '着'",
            "title_tj": "Зарраи динамикии '着'",
            "rule_uz": "'Zhe' yuklamasi fe'ldan keyin kelib, holatning davom etayotganligini bildiradi (statik holat). Bu ingliz tilidagi '-ing' bilan hosil qilingan sifatdoshga o'xshaydi, lekin harakat emas, balki holat davomiyligini ifodalaydi. Masalan: 门开着 (eshik ochiq turibdi), 手里拿着铅笔 (qo'lida qalam ushlab turibdi). Inkor: 没 + fe'l + 着.",
            "rule_ru": "Частица '着' ставится после глагола и обозначает продолжение состояния (статическое состояние). Похоже на причастие с '-ing' в английском, но выражает не действие, а его длительность. Например: 门开着 (дверь открыта), 手里拿着铅笔 (держит в руке карандаш). Отрицание: 没 + глагол + 着.",
            "rule_tj": "Зарраи '着' баъд аз феъл меояд ва давомнокии ҳолатро нишон медиҳад (ҳолати статикӣ). Ба феъли иштиракии '-ing' дар забони англисӣ монанд аст, аммо на амал балки давомнокии ҳолатро ифода мекунад. Масалан: 门开着 (дар кушода истодааст), 手里拿着铅笔 (дар дасташ қалам дорад). Инкор: 没 + феъл + 着.",
            "examples": [
                {"zh": "门开着呢，请进。", "pinyin": "Mén kāi zhe ne, qǐng jìn.", "uz": "Eshik ochiq turibdi, kiring.", "ru": "Дверь открыта, заходите.", "tj": "Дар кушода истодааст, дарояд."},
                {"zh": "他手里拿着一本书。", "pinyin": "Tā shǒu lǐ ná zhe yì běn shū.", "uz": "U qo'lida bir kitob ushlab turibdi.", "ru": "Он держит в руке одну книгу.", "tj": "Ӯ дар дасташ як китоб дорад."}
            ]
        },
        {
            "no": 2,
            "title_zh": "反问句“不是……吗”",
            "title_uz": "Ritorik savol '不是……吗'",
            "title_ru": "Риторический вопрос '不是……吗'",
            "title_tj": "Пурсиши риторикии '不是……吗'",
            "rule_uz": "'Bú shì……ma' konstruktsiyasi ritorik savol hosil qiladi: siz allaqachon bilib turib, tasdiqlash uchun savol qo'yasiz. O'zbek tilidagi '…-ku?' yoki '…emasmi?' ma'nosini beradi. Bu ma'lumotni eslatish yoki hayrat bildirish uchun ishlatiladi.",
            "rule_ru": "Конструкция '不是……吗' образует риторический вопрос: вы уже знаете ответ и задаёте вопрос для подтверждения. Аналог русского '…же?' или '…разве нет?'. Используется для напоминания информации или выражения удивления.",
            "rule_tj": "Конструксияи '不是……吗' пурсиши риторикӣ месозад: шумо аллакай медонед ва барои тасдиқ мепурсед. Ба '…-ку?' ё '…нест?' дар забони тоҷикӣ монанд аст. Барои ёдоварии маълумот ё ифодаи ҳайрат истифода мешавад.",
            "examples": [
                {"zh": "她不是有男朋友了吗？", "pinyin": "Tā bú shì yǒu nánpéngyou le ma?", "uz": "Uning yigit do'sti bor-ku?", "ru": "У неё же был парень?", "tj": "Магар ӯ дӯстписар надошт?"},
                {"zh": "你不是说今天来吗？", "pinyin": "Nǐ bú shì shuō jīntiān lái ma?", "uz": "Siz bugun kelaman demagandingizmi?", "ru": "Ты же говорил(а), что придёшь сегодня?", "tj": "Магар ту нагуфтӣ ки имрӯз меоям?"}
            ]
        },
        {
            "no": 3,
            "title_zh": "介词“往”",
            "title_uz": "'Wǎng' old ko'makchisi",
            "title_ru": "Предлог 'wǎng'",
            "title_tj": "Пешоянди 'wǎng'",
            "rule_uz": "'Wǎng' old ko'makchisi harakat yo'nalishini bildiradi: 'tomon, tomonga'. Fe'l oldidan keladi. Asosiy yo'nalishlar: 往前 (oldinga), 往后 (orqaga), 往左 (chapga), 往右 (o'ngga).",
            "rule_ru": "Предлог 'wǎng' обозначает направление движения: 'в сторону, к'. Ставится перед глаголом. Основные направления: 往前 (вперёд), 往后 (назад), 往左 (налево), 往右 (направо).",
            "rule_tj": "Пешоянди 'wǎng' самти ҳаракатро нишон медиҳад: 'ба тараф, ба самти'. Пеш аз феъл меояд. Самтҳои асосӣ: 往前 (пеш), 往后 (ақиб), 往左 (чап), 往右 (рост).",
            "examples": [
                {"zh": "一直往前走。", "pinyin": "Yìzhí wǎng qián zǒu.", "uz": "To'g'ri oldinga yuring.", "ru": "Идите прямо вперёд.", "tj": "Рост пеш равед."},
                {"zh": "到路口再往右走。", "pinyin": "Dào lùkǒu zài wǎng yòu zǒu.", "uz": "Chorrahaga yetgach o'ngga buriling.", "ru": "На перекрёстке поверните направо.", "tj": "Ба чорраҳа расидед ба тарафи рост гардед."}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
            "instruction_ru": "Напишите китайские эквиваленты следующих слов:",
            "instruction_tj": "Тарҷумаи чинии калимаҳои зеринро нависед:",
            "items": [
                {"prompt_uz": "qo'rg'oshin qalam", "prompt_ru": "карандаш", "prompt_tj": "қалами оддӣ", "answer": "铅笔", "pinyin": "qiānbǐ"},
                {"prompt_uz": "mehmonxona", "prompt_ru": "гостиница", "prompt_tj": "меҳмонхона", "answer": "宾馆", "pinyin": "bīnguǎn"},
                {"prompt_uz": "chorraha", "prompt_ru": "перекрёсток", "prompt_tj": "чорраҳа", "answer": "路口", "pinyin": "lùkǒu"},
                {"prompt_uz": "kulmoq", "prompt_ru": "смеяться", "prompt_tj": "хандидан", "answer": "笑", "pinyin": "xiào"},
                {"prompt_uz": "ushlamoq", "prompt_ru": "держать", "prompt_tj": "нигоҳ доштан", "answer": "拿", "pinyin": "ná"}
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "U qo'lida qalam ushlab ___di. (着)", "prompt_ru": "Он держит в руке карандаш. (着)", "prompt_tj": "Ӯ дар дасташ қалам дор___. (着)", "answer": "着", "pinyin": "zhe"},
                {"prompt_uz": "Televizor yoniq ___bdi. (着)", "prompt_ru": "Телевизор включён. (着)", "prompt_tj": "Телевизор кушода ___. (着)", "answer": "着", "pinyin": "zhe"},
                {"prompt_uz": "To'g'ri ___ oldinga yuring. (往)", "prompt_ru": "Идите прямо ___. (往)", "prompt_tj": "Рост ___ пеш равед. (往)", "answer": "往", "pinyin": "wǎng"},
                {"prompt_uz": "Uning yigit do'sti bor ___? (是)", "prompt_ru": "У неё же есть парень? (是)", "prompt_tj": "Магар ӯ дӯстписар надорад ___ ? (是)", "answer": "是", "pinyin": "shì"}
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "门开着呢，请进。", "prompt_ru": "门开着呢，请进。", "prompt_tj": "门开着呢，请进。", "answer": "Eshik ochiq turibdi, marhamat kiring.", "pinyin": "Mén kāi zhe ne, qǐng jìn."},
                {"prompt_uz": "从这儿一直往前走，到了前面的路口再往右走。", "prompt_ru": "从这儿一直往前走，到了前面的路口再往右走。", "prompt_tj": "从这儿一直往前走，到了前面的路口再往右走。", "answer": "Bu yerdan to'g'ri oldinga boring, oldindagi chorrahaga yetgach o'ngga buriling.", "pinyin": "Cóng zhèr yìzhí wǎng qián zǒu, dào le qiánmian de lùkǒu zài wǎng yòu zǒu."},
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["铅笔", "宾馆", "路口", "笑", "拿"]},
        {"no": 2, "answers": ["着", "着", "往", "是"]},
        {"no": 3, "answers": [
            "Eshik ochiq turibdi, marhamat kiring.",
            "Bu yerdan to'g'ri oldinga boring, oldindagi chorrahaga yetgach o'ngga buriling.",
        ]}
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'Zhe' yuklamasidan foydalanib, hozirgi vaziyatingizni tasvirlang: nima kiyib turibsiz, qo'lingizda nima bor va h.k. Kamida 3 jumla yozing.",
            "instruction_ru": "Используя частицу '着', опишите вашу текущую ситуацию: что вы надели, что держите в руке и т.д. Напишите не менее 3 предложений.",
            "instruction_tj": "Бо истифодаи зарраи '着' вазъияти ҳозираи худро тавсиф кунед: чӣ пӯшидаед, дар дастатон чӣ дорид ва ғ. Камаш 3 ҷумла нависед.",
            "words": ["着"],
            "example": "我穿着白色的衣服。",
            "topic_uz": "Hozirgi vaziyat tavsifi",
            "topic_ru": "Описание текущей ситуации",
            "topic_tj": "Тавсифи вазъияти ҳозира"
        },
        {
            "no": 2,
            "instruction_uz": "Uyingizdan maktabgacha yoki boshqa tanish joyga yo'l ko'rsatib yozing. 'Wǎng', 'yìzhí', 'lùkǒu' so'zlaridan foydalaning.",
            "instruction_ru": "Опишите маршрут от вашего дома до школы или другого знакомого места. Используйте слова 'wǎng', 'yìzhí', 'lùkǒu'.",
            "instruction_tj": "Роҳро аз хонаатон то мактаб ё ягон ҷойи дигари шинос тавсиф кунед. Калимаҳои 'wǎng', 'yìzhí', 'lùkǒu' истифода баред.",
            "words": ["往", "一直", "路口"],
            "example": "从我家一直往前走，到路口再往右走。",
            "topic_uz": "Uydan maktabgacha yo'l",
            "topic_ru": "Путь от дома до школы",
            "topic_tj": "Роҳ аз хона то мактаб"
        }
    ], ensure_ascii=False),
    "review_json": "[]",
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
