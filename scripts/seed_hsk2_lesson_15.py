import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 15,
    "lesson_code": "HSK2-L15",
    "title": "新年就要到了",
    "goal": json.dumps({"uz": "Yaqin kelajakda bo'ladigan voqeani bildiruvchi '要……了' / '快要……了' va '都……了' konstruktsiyalarini o'rganish.", "ru": "Изучение конструкций '要……了' / '快要……了' для выражения ближайшего будущего и конструкции '都……了'.", "tj": "Омӯзиши конструксияҳои '要……了' / '快要……了' барои ифодаи оянда ва '都……了'."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda yangi yil va tadbirga tayyorlanish mavzusida gaplashamiz. '就要……了' (yaqinda bo'ladi) va '快要……了' (tez orada bo'ladi) konstruktsiyalari orqali yaqin kelajakdagi hodisalarni ifodalashni o'rganamiz. Shuningdek, '都……了' iborasi yordamida vaqt yoki miqdorning ortiqligini ta'kidlashni mashq qilamiz.", "ru": "На этом уроке мы говорим о подготовке к новому году и мероприятиям. Учимся выражать предстоящие события с помощью конструкций '就要……了' (скоро будет) и '快要……了' (вот-вот будет). Также отрабатываем конструкцию '都……了' для выражения того, что времени или количества уже много.", "tj": "Дар ин дарс дар бораи тайёрӣ ба соли нав ва тадбирҳо сухан мезанем. Тавассути конструксияҳои '就要……了' (наздик мешавад) ва '快要……了' (зуд мешавад) рӯйдодҳои оянда ро ифода мекунем. Инчунин конструксияи '都……了' барои таъкиди зиёд будани вақт ё миқдорро машқ мекунем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "日", "pinyin": "rì", "pos": "n.", "uz": "kun, sana", "ru": "день, дата", "tj": "рӯз, сана"},
        {"no": 2, "zh": "新年", "pinyin": "xīnnián", "pos": "n.", "uz": "yangi yil", "ru": "новый год", "tj": "соли нав"},
        {"no": 3, "zh": "票", "pinyin": "piào", "pos": "n.", "uz": "chipta, bilet", "ru": "билет", "tj": "чиптаи сафар"},
        {"no": 4, "zh": "火车站", "pinyin": "huǒchēzhàn", "pos": "n.", "uz": "temir yo'l stantsiyasi, vokzal", "ru": "железнодорожная станция, вокзал", "tj": "истгоҳи роҳи оҳан, вокзал"},
        {"no": 5, "zh": "大家", "pinyin": "dàjiā", "pos": "pron.", "uz": "hamma, barchalar", "ru": "все, каждый", "tj": "ҳама, тамоми"},
        {"no": 6, "zh": "更", "pinyin": "gèng", "pos": "adv.", "uz": "yanada, bundan ham ko'proq", "ru": "ещё более, ещё больше", "tj": "ҳатто бештар, боз ҳам зиёдтар"},
        {"no": 7, "zh": "妹妹", "pinyin": "mèimei", "pos": "n.", "uz": "singil", "ru": "младшая сестра", "tj": "хоҳари хурдӣ"},
        {"no": 8,  "zh": "阴",   "pinyin": "yīn",    "pos": "adj.", "uz": "bulutli, quyosh ko'rinmaydi",              "ru": "пасмурный, облачный",                  "tj": "абрнок, офтоб намоён нест"},
        {"no": 9,  "zh": "旅游", "pinyin": "lǚyóu",  "pos": "v.",   "uz": "sayohat qilmoq",                           "ru": "путешествовать",                       "tj": "сафар кардан, гашт кардан"},
        {"no": 10, "zh": "伞",   "pinyin": "sǎn",    "pos": "n.",   "uz": "soyabon, qoʻldagi yomg'irdan saqlash",    "ru": "зонт",                                 "tj": "чатр"},
        {"no": 11, "zh": "月",   "pinyin": "yuè",    "pos": "n.",   "uz": "oy (vaqt o'lchovi)",                      "ru": "месяц",                                "tj": "моҳ (вақти ченкунӣ)"},
        {"no": 12, "zh": "节日", "pinyin": "jiérì",  "pos": "n.",   "uz": "bayram, tantana",                         "ru": "праздник",                             "tj": "ид, ҷашн"},
        {"no": 13, "zh": "祝",   "pinyin": "zhù",    "pos": "v.",   "uz": "tilak bildirmoq, tabriklamoq",            "ru": "желать, поздравлять",                  "tj": "орзу кардан, табрик гуфтан"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Do'st uyida",
            "scene_ru": "В доме друга",
            "scene_tj": "Дар хонаи дӯст",
            "dialogue": [
                {"speaker": "A", "zh": "今天是12月20日，新年就要到了。", "pinyin": "Jīntiān shì shí'èr yuè èrshí rì, xīnnián jiù yào dào le.", "uz": "Bugun 20-dekabr, yangi yil yaqinlashib qoldi.", "ru": "Сегодня 20 декабря, новый год уже совсем скоро.", "tj": "Имрӯз 20 декабр аст, соли нав наздик шуд."},
                {"speaker": "B", "zh": "新年你准备做什么？", "pinyin": "Xīnnián nǐ zhǔnbèi zuò shénme?", "uz": "Yangi yilda nima qilishni rejalashtirganmisiz?", "ru": "Что ты планируешь делать на новый год?", "tj": "Дар соли нав чӣ кор карданӣ ҳастед?"},
                {"speaker": "A", "zh": "我想去北京旅游，北京很不错，我去过一次。", "pinyin": "Wǒ xiǎng qù Běijīng lǚyóu, Běijīng hěn búcuò, wǒ qùguo yí cì.", "uz": "Pekinga sayohat qilmoqchiman, Pekin juda yaxshi joy, bir marta borgan edim.", "ru": "Хочу съездить в Пекин, там очень хорошо, я уже был(а) там один раз.", "tj": "Мехоҳам ба Пекин сафар кунам, Пекин хеле хуб аст, як маротиба рафтаам."},
                {"speaker": "B", "zh": "你买票了吗？", "pinyin": "Nǐ mǎi piào le ma?", "uz": "Chipta oldingizmi?", "ru": "Ты уже купил(а) билет?", "tj": "Оё шумо чиптаи сафар харидаед?"},
                {"speaker": "A", "zh": "还没有呢，明天就去火车站买票。", "pinyin": "Hái méiyǒu ne, míngtiān jiù qù huǒchēzhàn mǎi piào.", "uz": "Hali olmadim, ertaga vokzalga borib chipta olaman.", "ru": "Ещё нет, завтра пойду на вокзал за билетом.", "tj": "Ҳанӯз не, фардо ба вокзал мераваму чипта мехарам."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Kompaniyada",
            "scene_ru": "В компании",
            "scene_tj": "Дар ширкат",
            "dialogue": [
                {"speaker": "A", "zh": "时间过得真快，新的一年快要到了！", "pinyin": "Shíjiān guò de zhēn kuài, xīn de yì nián kuài yào dào le!", "uz": "Vaqt juda tez o'tar ekan, yangi yil ham tez orada keladi!", "ru": "Время летит так быстро, новый год уже вот-вот!", "tj": "Вақт хеле зуд мегузарад, соли нав ҳам наздик шуд!"},
                {"speaker": "B", "zh": "是啊，谢谢大家这一年对我的帮助！", "pinyin": "Shì a, xièxie dàjiā zhè yì nián duì wǒ de bāngzhù!", "uz": "Ha, hammaga bu yil menga bergan yordamlari uchun katta rahmat!", "ru": "Да, спасибо всем за помощь в этом году!", "tj": "Бале, ташаккур ба ҳама барои ёрии ин сол!"},
                {"speaker": "C", "zh": "希望我们的公司明年更好！", "pinyin": "Xīwàng wǒmen de gōngsī míngnián gèng hǎo!", "uz": "Umid qilamanki kompaniyamiz kelasi yil yanada yaxshilansin!", "ru": "Надеюсь, в следующем году наша компания будет ещё лучше!", "tj": "Умедворам ширкати мо соли оянда боз ҳам беҳтар шавад!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Stantsiyada",
            "scene_ru": "На станции",
            "scene_tj": "Дар истгоҳ",
            "dialogue": [
                {"speaker": "A", "zh": "你妹妹怎么还没来？都八点四十了！", "pinyin": "Nǐ mèimei zěnme hái méi lái? Dōu bā diǎn sìshí le!", "uz": "Singling nima uchun hali kelmadi? Soat sakkiz qirq bo'lib qoldi!", "ru": "Почему твоя сестра ещё не пришла? Уже восемь сорок!", "tj": "Чаро хоҳари хурдиат ҳанӯз наомад? Дигар соати ҳашту чил шуд!"},
                {"speaker": "B", "zh": "我们再等她几分钟吧。", "pinyin": "Wǒmen zài děng tā jǐ fēnzhōng ba.", "uz": "Uni yana bir necha daqiqa kutaylik.", "ru": "Давай подождём её ещё несколько минут.", "tj": "Биёед чанд дақиқаи дигар интизораш шавем."},
                {"speaker": "A", "zh": "都等她半个小时了！", "pinyin": "Dōu děng tā bàn ge xiǎoshí le!", "uz": "Uni yarim soatdan beri kutib turibmiz!", "ru": "Мы уже полчаса её ждём!", "tj": "Мо нимсоат интизораш шудем!"},
                {"speaker": "B", "zh": "她来了，我听见她说话了。", "pinyin": "Tā lái le, wǒ tīngjiàn tā shuōhuà le.", "uz": "U keldi, uning gapirayotganini eshitdim.", "ru": "Она пришла, я слышу, как она говорит.", "tj": "Вай омад, ман садои ӯро шунидам."}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Qahvaxona oldida",
            "scene_ru": "У входа в кафе",
            "scene_tj": "Дар пеши қаҳвахона",
            "dialogue": [
                {"speaker": "A", "zh": "天阴了，我要回去了。", "pinyin": "Tiān yīn le, wǒ yào huíqù le.", "uz": "Osmon bulutlandi, ketishim kerak.", "ru": "Небо затянулось тучами, мне нужно идти.", "tj": "Осмон абрнок шуд, бояд бираваm."},
                {"speaker": "B", "zh": "好的，快要下雨了，你路上慢点儿。", "pinyin": "Hǎo de, kuài yào xiàyǔ le, nǐ lùshang màn diǎnr.", "uz": "Yaxshi, tez orada yomg'ir yog'adi, yo'lda ehtiyot bo'ling.", "ru": "Хорошо, скоро пойдёт дождь, будьте осторожны в дороге.", "tj": "Хуб, зуд борон мешавад, дар роҳ эҳтиёт шавед."},
                {"speaker": "A", "zh": "没关系，我坐公共汽车。", "pinyin": "Méi guānxi, wǒ zuò gōnggòng qìchē.", "uz": "Muammo yo'q, men avtobus bilan boraman.", "ru": "Ничего, я поеду на автобусе.", "tj": "Мушкил нест, ман бо автобус мераваm."},
                {"speaker": "B", "zh": "好的，再见。", "pinyin": "Hǎo de, zàijiàn.", "uz": "Yaxshi, xayr.", "ru": "Хорошо, до свидания.", "tj": "Хуб, хайр."}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "动作的状态\"要……了\"",
            "title_uz": "'Yào……le' yaqin kelajak konstruktsiyasi",
            "title_ru": "Конструкция '要……了' ближайшего будущего",
            "title_tj": "Конструксияи '要……了' ояндаи наздик",
            "rule_uz": "'Yào……le' yoki 'jiù yào……le' yoki 'kuài yào……le' konstruktsiyasi yaqin kelajakda bo'ladigan voqeani bildiradi: 'tez orada …bo'ladi / …qilmoqchi'. 'Jiù yào' aniqroq vaqt bilan, 'kuài yào' esa umumiy 'tez orada' ma'nosida ishlatiladi. Gap oxiridagi 'le' o'zgarish yoki yangi holat yaqinligini ko'rsatadi.",
            "rule_ru": "Конструкции '要……了', '就要……了' или '快要……了' обозначают события ближайшего будущего: 'вот-вот произойдёт'. '就要' используется с более конкретным временем, '快要' — в общем смысле 'скоро'. Частица 'le' в конце указывает на близость изменения или нового состояния.",
            "rule_tj": "Конструксияҳои '要……了', '就要……了' ё '快要……了' рӯйдодҳои оянда наздикро нишон медиҳанд: 'зуд мешавад / қариб'. '就要' бо вақти мушаххастар, '快要' дар маъноии умумии 'зуд' истифода мешавад. Зарраи 'le' дар охири ҷумла наздикии тағйирот ё ҳолати навро нишон медиҳад.",
            "examples": [
                {"zh": "新年就要到了。", "pinyin": "Xīnnián jiù yào dào le.", "uz": "Yangi yil yaqinlashib qoldi.", "ru": "Новый год уже совсем близко.", "tj": "Соли нав наздик шуд."},
                {"zh": "快要下雨了，带上伞吧。", "pinyin": "Kuài yào xiàyǔ le, dài shàng sǎn ba.", "uz": "Tez orada yomg'ir yog'adi, soyabon oling.", "ru": "Скоро пойдёт дождь, возьмите зонт.", "tj": "Зуд борон мешавад, чатр гиред."}
            ]
        },
        {
            "no": 2,
            "title_zh": "\"都……了\"",
            "title_uz": "'Dōu……le' ta'kid konstruktsiyasi",
            "title_ru": "Конструкция '都……了' для выражения удивления",
            "title_tj": "Конструксияи '都……了' барои таъкид",
            "rule_uz": "'Dōu……le' konstruktsiyasi ta'kid bildiradi: vaqt yoki miqdor allaqachon ancha ko'p yoki kutilgandan ortiq bo'lib qoldi. O'zbek tilidagi '…bo'lib ketdi!' yoki '…bo'lib qoldi-ku!' iborasiga o'xshaydi. Ko'pincha hayrat yoki norozilik ifodalamoqda qo'llanadi.",
            "rule_ru": "Конструкция '都……了' выражает акцент: время или количество уже достигло неожиданного или чрезмерного уровня. Аналог русского 'уже … же!' или 'ну и…!'. Часто выражает удивление или недовольство.",
            "rule_tj": "Конструксияи '都……了' таъкид мекунад: вақт ё миқдор аллакай ба сатҳи ғайричашмдошт ё аз ҳад зиёд расидааст. Ба ибораҳои '…шуду рафт!' ё '…шуд-ку!' дар тоҷикӣ монанд аст. Аксар вақт ҳайрат ё норозигиро ифода мекунад.",
            "examples": [
                {"zh": "都八点四十了！", "pinyin": "Dōu bā diǎn sìshí le!", "uz": "Soat sakkiz qirq bo'lib qoldi!", "ru": "Уже восемь сорок!", "tj": "Дигар соати ҳашту чил шуд!"},
                {"zh": "都等她半个小时了！", "pinyin": "Dōu děng tā bàn ge xiǎoshí le!", "uz": "Uni yarim soatdan beri kutib turibmiz!", "ru": "Мы уже полчаса её ждём!", "tj": "Мо нимсоат интизораш шудем!"}
            ]
        },
        {
            "no": 3,
            "title_zh": "副词\"更\"的用法",
            "title_uz": "'Gèng' (yanada, bundan ham ko'proq) ravishining ishlatilishi",
            "title_ru": "Использование наречия '更' (ещё более, ещё больше)",
            "title_tj": "Истифодаи зарфи '更' (ҳатто бештар, боз ҳам зиёдтар)",
            "rule_uz": (
                "'更' ravishi sifat yoki ravish oldidan kelib, qiyoslashni kuchaytiradi: 'yanada, bundan ham ko'proq'.\n"
                "Tuzilish: A 比 B 更 + sifat (A dan B dan yanada …).\n"
                "'更' mustaqil ham qo'llanadi: '我希望明年更好' (Umid qilamanki keyingi yil yanada yaxshi bo'lsin).\n"
                "'还' (hái) bilan almashtirib ham ishlatilishi mumkin."
            ),
            "rule_ru": (
                "Наречие '更' стоит перед прилагательным или наречием и усиливает сравнение: 'ещё более, ещё больше'.\n"
                "Структура: A 比 B 更 + прилагательное (A ещё более … чем B).\n"
                "'更' употребляется и самостоятельно: '我希望明年更好' (Надеюсь, в следующем году будет ещё лучше).\n"
                "Может взаимозаменяться с '还' (hái) в некоторых контекстах."
            ),
            "rule_tj": (
                "Зарфи '更' пеш аз сифат ё зарф меояд ва муқоисаро тақвият медиҳад: 'ҳатто бештар, боз ҳам зиёдтар'.\n"
                "Сохтор: A 比 B 更 + сифат (A аз B ҳатто … бештар).\n"
                "'更' мустақилона ҳам истифода мешавад: '我希望明年更好' (Умедворам соли оянда боз ҳам беҳтар шавад).\n"
                "Дар баъзе контекстҳо бо '还' (hái) иваз шуда метавонад."
            ),
            "examples": [
                {"zh": "希望我们的公司明年更好！", "pinyin": "Xīwàng wǒmen de gōngsī míngnián gèng hǎo!", "uz": "Umid qilamanki kompaniyamiz kelasi yil yanada yaxshilansin!", "ru": "Надеюсь, в следующем году наша компания будет ещё лучше!", "tj": "Умедворам ширкати мо соли оянда боз ҳам беҳтар шавад!"},
                {"zh": "北京比这儿更好玩儿。", "pinyin": "Běijīng bǐ zhèr gèng hǎo wánr.", "uz": "Pekin bu yerdan yanada qiziqarliroq.", "ru": "В Пекине ещё интереснее, чем здесь.", "tj": "Пекин аз ин ҷо боз ҳам ҷолибтар аст."},
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
                {"prompt_uz": "yangi yil", "prompt_ru": "новый год", "prompt_tj": "соли нав", "answer": "新年", "pinyin": "xīnnián"},
                {"prompt_uz": "chipta", "prompt_ru": "билет", "prompt_tj": "чипта", "answer": "票", "pinyin": "piào"},
                {"prompt_uz": "vokzal", "prompt_ru": "вокзал", "prompt_tj": "вокзал", "answer": "火车站", "pinyin": "huǒchēzhàn"},
                {"prompt_uz": "singil", "prompt_ru": "младшая сестра", "prompt_tj": "хоҳари хурдӣ", "answer": "妹妹", "pinyin": "mèimei"},
                {"prompt_uz": "yanada", "prompt_ru": "ещё более", "prompt_tj": "боз ҳам бештар", "answer": "更", "pinyin": "gèng"}
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "Opa ertaga ___ ketadi. (就)", "prompt_ru": "Сестра завтра ___ уедет. (就)", "prompt_tj": "Хоҳар фардо ___ мераваd. (就)", "answer": "就", "pinyin": "jiù"},
                {"prompt_uz": "Soat o'n ikki ___, do'kon yopiq. (了)", "prompt_ru": "Уже полночь ___, магазин закрыт. (了)", "prompt_tj": "Дигар нимашаб ___, дӯкон баста аст. (了)", "answer": "了", "pinyin": "le"},
                {"prompt_uz": "Uka ___ besh yoshda bo'lib qoldi. (都)", "prompt_ru": "Братишка ___ исполнилось пять лет. (都)", "prompt_tj": "Бародари хурдӣ ___ панҷ сола шуд. (都)", "answer": "都", "pinyin": "dōu"},
                {"prompt_uz": "Tez orada yomg'ir yog'___, kirgin! (要)", "prompt_ru": "Скоро ___ дождь, заходи! (要)", "prompt_tj": "Зуд борон меша___д, дар! (要)", "answer": "要", "pinyin": "yào"}
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "新年就要到了。", "prompt_ru": "新年就要到了。", "prompt_tj": "新年就要到了。", "answer": "Yangi yil yaqinlashib qoldi.", "pinyin": "Xīnnián jiù yào dào le."},
                {"prompt_uz": "好的，快要下雨了，你路上慢点儿。", "prompt_ru": "好的，快要下雨了，你路上慢点儿。", "prompt_tj": "好的，快要下雨了，你路上慢点儿。", "answer": "Yaxshi, tez orada yomg'ir yog'adi, yo'lda ehtiyot bo'ling.", "pinyin": "Hǎo de, kuài yào xiàyǔ le, nǐ lùshang màn diǎnr."},
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["新年", "票", "火车站", "妹妹", "更"]},
        {"no": 2, "answers": ["就", "了", "都", "要"]},
        {"no": 3, "answers": [
            "Yangi yil yaqinlashib qoldi.",
            "Yaxshi, tez orada yomg'ir yog'adi, yo'lda ehtiyot bo'ling.",
        ]}
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'Jiù yào……le' yoki 'kuài yào……le' ishlatib, tez orada bo'ladigan 3-4 ta voqea haqida yozing (masalan: imtihon, bayram, sayohat va h.k.).",
            "instruction_ru": "Используя '就要……了' или '快要……了', напишите о 3-4 предстоящих событиях (например: экзамен, праздник, поездка и т.д.).",
            "instruction_tj": "Бо истифодаи '就要……了' ё '快要……了' дар бораи 3-4 рӯйдоди наздик нависед (масалан: имтиҳон, иди, сафар ва ғ.).",
            "words": ["就要……了", "快要……了"],
            "example": "考试就要到了，我要好好学习。",
            "topic_uz": "Yaqinda bo'ladigan voqealar",
            "topic_ru": "Предстоящие события",
            "topic_tj": "Рӯйдодҳои наздик"
        },
        {
            "no": 2,
            "instruction_uz": "Yangi yilga rejalaringiz haqida yozing: qayerga borasiz, kim bilan o'tkazasiz, nima sotib olasiz.",
            "instruction_ru": "Напишите о своих планах на новый год: куда поедете, с кем проведёте, что купите.",
            "instruction_tj": "Дар бораи нақшаҳои соли наватон нависед: ба куҷо мераваед, бо кӣ мегузаронед, чӣ мехаред.",
            "words": ["新年", "就要", "快要"],
            "example": "新年快要到了，我想去北京旅游。",
            "topic_uz": "Yangi yil rejalarim",
            "topic_ru": "Мои планы на новый год",
            "topic_tj": "Нақшаҳои соли нави ман"
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
