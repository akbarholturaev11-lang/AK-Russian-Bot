import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 11,
    "lesson_code": "HSK4-L11",
    "title": "读书好，读好书，好读书",
    "goal": json.dumps({"uz": "kitob o'qish odatlari va usullari haqida gapirish; 连……也/都……, 否则, 无论……都/也……, 然而, 同时 grammatik qoliplarini o'zlashtirish", "ru": "говорить о привычках и методах чтения; освоить грамматические конструкции 连……也/都……, 否则, 无论……都/也……, 然而, 同时", "tj": "дар бораи одатҳо ва усулҳои мутолиа гуфтугӯ кардан; азхуд кардани қолабҳои грамматикии 连……也/都……, 否则, 无论……都/也……, 然而, 同时"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars kitob o'qishning afzalliklari va yaxshi o'qish odatlarini shakllantirish haqida. Unda xitoy tilini o'rganish, imtihonlar topshirish va ko'p o'qishning ahamiyati haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 连……也/都……, 否则, 无论……都/也……, 然而, 同时.", "ru": "Этот урок посвящён пользе чтения и формированию хороших читательских привычек. В нём изучается, как говорить об изучении китайского языка, сдаче экзаменов и важности широкого чтения. Основные грамматические конструкции: 连……也/都……, 否则, 无论……都/也……, 然而, 同时.", "tj": "Ин дарс дар бораи фоидаҳои мутолиа ва ташаккули одатҳои хуби хондан мебошад. Дар он гуфтугӯ дар бораи омӯхтани забони чинӣ, супоридани имтиҳонҳо ва аҳамияти мутолиаи васеъ омӯхта мешавад. Қолабҳои асосии грамматикӣ: 连……也/都……, 否则, 无论……都/也……, 然而, 同时."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "流利", "pinyin": "liúlì", "pos": "adj.", "uz": "ravon, bemalol", "ru": "беглый, свободный", "tj": "равон, бемалол"},
            {"no": 2, "zh": "厉害", "pinyin": "lìhai", "pos": "adj.", "uz": "zo'r, kuchli, ajoyib", "ru": "крутой, сильный, впечатляющий", "tj": "зӯр, қавӣ, аҷоиб"},
            {"no": 3, "zh": "语法", "pinyin": "yǔfǎ", "pos": "n.", "uz": "grammatika", "ru": "грамматика", "tj": "грамматика"},
            {"no": 4, "zh": "准确", "pinyin": "zhǔnquè", "pos": "adj.", "uz": "aniq, to'g'ri", "ru": "точный, правильный", "tj": "дақиқ, дуруст"},
            {"no": 5, "zh": "词语", "pinyin": "cíyǔ", "pos": "n.", "uz": "so'z, ibora", "ru": "слово, выражение", "tj": "калима, ибора"},
            {"no": 6, "zh": "连", "pinyin": "lián", "pos": "prep./conj.", "uz": "hatto (ekstremal holatni ta'kidlaydi)", "ru": "даже (подчёркивает крайний случай)", "tj": "ҳатто (ҳолати ифротиро таъкид мекунад)"},
            {"no": 7, "zh": "阅读", "pinyin": "yuèdú", "pos": "v.", "uz": "o'qimoq (matn)", "ru": "читать (текст)", "tj": "хондан (матн)"},
            {"no": 8, "zh": "来得及", "pinyin": "láidejí", "pos": "v.", "uz": "vaqt bor, ulgurmoq", "ru": "успеть, ещё есть время", "tj": "вақт ҳаст, расидан"},
            {"no": 9, "zh": "复杂", "pinyin": "fùzá", "pos": "adj.", "uz": "murakkab, qiyin", "ru": "сложный, запутанный", "tj": "мураккаб, душвор"},
            {"no": 10, "zh": "只好", "pinyin": "zhǐhǎo", "pos": "adv.", "uz": "majbur bo'lmoq, boshqa iloji yo'q", "ru": "вынужден, не остаётся ничего иного", "tj": "маҷбур шудан, чораи дигаре нест"},
            {"no": 11, "zh": "填空", "pinyin": "tián kòng", "pos": "v.", "uz": "bo'sh joyni to'ldirmoq", "ru": "заполнять пропуски", "tj": "ҷойи холиро пур кардан"},
            {"no": 12, "zh": "猜", "pinyin": "cāi", "pos": "v.", "uz": "taxmin qilmoq, mo'ljal olmoq", "ru": "угадывать, предполагать", "tj": "тахмин кардан, ҳадс задан"},
            {"no": 13, "zh": "否则", "pinyin": "fǒuzé", "pos": "conj.", "uz": "aks holda, bo'lmasa", "ru": "иначе, в противном случае", "tj": "акс ҳол, дар ғайри ин сурат"},
            {"no": 14, "zh": "客厅", "pinyin": "kètīng", "pos": "n.", "uz": "mehmonxona, zal", "ru": "гостиная", "tj": "меҳмонхона, толор"},
            {"no": 15, "zh": "无论", "pinyin": "wúlùn", "pos": "conj.", "uz": "qanday bo'lmasin, farqi yo'q", "ru": "независимо от, невзирая на", "tj": "ҳар чӣ бошад, новобаста аз"},
            {"no": 16, "zh": "杂志", "pinyin": "zázhì", "pos": "n.", "uz": "jurnal", "ru": "журнал", "tj": "маҷалла"},
            {"no": 17, "zh": "著名", "pinyin": "zhùmíng", "pos": "adj.", "uz": "mashhur, taniqli", "ru": "известный, знаменитый", "tj": "машҳур, маъруф"},
            {"no": 18, "zh": "页", "pinyin": "yè", "pos": "m.", "uz": "sahifa (o'lchov so'z)", "ru": "страница (счётное слово)", "tj": "саҳифа (ҳисобшавандаи)"},
            {"no": 19, "zh": "增加", "pinyin": "zēngjiā", "pos": "v.", "uz": "oshirmoq, ko'paytirmoq", "ru": "увеличивать, добавлять", "tj": "зиёд кардан, афзудан"},
            {"no": 20, "zh": "文章", "pinyin": "wénzhāng", "pos": "n.", "uz": "maqola, matn", "ru": "статья, текст, эссе", "tj": "мақола, матн"},
            {"no": 21, "zh": "之", "pinyin": "zhī", "pos": "part.", "uz": "klassik bog'lovchi zarracha (otlar o'rtasida)", "ru": "классическая соединительная частица (между существительными)", "tj": "зарраи классикии пайвасткунанда (байни исмҳо)"},
            {"no": 22, "zh": "内容", "pinyin": "nèiróng", "pos": "n.", "uz": "mazmun, kontent", "ru": "содержание, контент", "tj": "мазмун, контент"},
            {"no": 23, "zh": "然而", "pinyin": "rán'ér", "pos": "conj.", "uz": "biroq, ammo (rasmiy yozma uslub)", "ru": "однако, но (книжный стиль)", "tj": "аммо, лекин (услуби расмии хаттӣ)"},
            {"no": 24, "zh": "看法", "pinyin": "kànfǎ", "pos": "n.", "uz": "nuqtai nazar, fikr", "ru": "точка зрения, мнение", "tj": "нуқтаи назар, фикр"},
            {"no": 25, "zh": "相同", "pinyin": "xiāngtóng", "pos": "adj.", "uz": "bir xil, o'xshash", "ru": "одинаковый, идентичный", "tj": "якхела, монанд"},
            {"no": 26, "zh": "顺序", "pinyin": "shùnxù", "pos": "n.", "uz": "tartib, ketma-ketlik", "ru": "порядок, последовательность", "tj": "тартиб, пайдарпайӣ"},
            {"no": 27, "zh": "表示", "pinyin": "biǎoshì", "pos": "v.", "uz": "bildirmoq, ifodalash", "ru": "выражать, указывать", "tj": "ифода кардан, нишон додан"},
            {"no": 28, "zh": "养成", "pinyin": "yǎngchéng", "pos": "v.", "uz": "odat shakllantirmoq, rivojlantirmoq", "ru": "вырабатывать (привычку), формировать", "tj": "одат ташаккул додан, парвариш кардан"},
            {"no": 29, "zh": "同时", "pinyin": "tóngshí", "pos": "conj./adv.", "uz": "bir vaqtda, shu bilan birga", "ru": "в то же время, одновременно", "tj": "дар як вақт, ҳамзамон"},
            {"no": 30, "zh": "精彩", "pinyin": "jīngcǎi", "pos": "adj.", "uz": "ajoyib, zo'r, yaxshi", "ru": "замечательный, великолепный", "tj": "аҷоиб, зӯр, олӣ"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "Mark xitoy tilini o'rganish usuli haqida tushuntirmoqda",
                "scene_ru": "Марк рассказывает о своём методе изучения китайского языка",
                "scene_tj": "Марк усули омӯхтани забони хитоии худро шарҳ медиҳад",
                "dialogue": [
                    {"speaker": "老师", "zh": "马克，你的汉语说得这么流利，有什么好方法吗？", "pinyin": "", "uz": "Mark, sizning xitoy tilingiz juda ravon, qandaydir yaxshi usullaringiz bormi?", "ru": "Марк, ваш китайский такой беглый — есть какие-то хорошие методы?", "tj": "Марк, забони хитоии шумо чунин равон аст — оё усулҳои хубе доред?"},
                    {"speaker": "马克", "zh": "我每天都阅读中文文章，无论多忙，都坚持读至少十页。", "pinyin": "", "uz": "Men har kuni xitoycha maqolalar o'qiyman, qanchalik band bo'lmasin, kamida o'n sahifa o'qishni davom ettiraman.", "ru": "Я каждый день читаю китайские статьи, и независимо от того, насколько я занят, всегда читаю минимум десять страниц.", "tj": "Ман ҳар рӯз мақолаҳои хитоӣ мехонам, ҳар чӣ қадар банд бошам, ҳатман на кам аз даҳ саҳифа мехонам."},
                    {"speaker": "老师", "zh": "那语法呢？语法对你来说复杂吗？", "pinyin": "", "uz": "Xo'sh, grammatika-chi? Grammatika siz uchun murakkabmi?", "ru": "А как насчёт грамматики? Грамматика для вас сложная?", "tj": "Хӯш, грамматика чӣ? Оё грамматика барои шумо мураккаб аст?"},
                    {"speaker": "马克", "zh": "一开始连基本词语都不准确，然而通过大量阅读，我的语法慢慢提高了。", "pinyin": "", "uz": "Boshida hatto asosiy so'zlarni ham aniq ayta olmas edim, biroq ko'p o'qish orqali grammatikam asta-sekin yaxshilandi.", "ru": "Поначалу я не мог даже точно произносить базовые слова, однако благодаря большому количеству чтения моя грамматика постепенно улучшилась.", "tj": "Аввал ҳатто калимаҳои асосиро ҳам дақиқ гуфта наметавонистам, аммо тавассути мутолиаи зиёд грамматикаам оҳиста-оҳиста беҳтар шуд."},
                    {"speaker": "老师", "zh": "你的方法很好！坚持阅读，同时注意语法，效果一定很好。", "pinyin": "", "uz": "Sizning usullaringiz juda yaxshi! Doimiy o'qish va bir vaqtda grammatikaga e'tibor berish — natija albatta yaxshi bo'ladi.", "ru": "Ваш метод отличный! Продолжать читать, одновременно обращая внимание на грамматику, — результат обязательно будет хорошим.", "tj": "Усули шумо хеле хуб аст! Мутолиаро давом додан ва дар як вақт ба грамматика диққат додан — натиҷа ҳатман хуб хоҳад буд."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "Xiao Xia va Xiao Yu imtihon haqida suhbatlashmoqda",
                "scene_ru": "Сяо Ся и Сяо Юй разговаривают об экзамене",
                "scene_tj": "Сяо Ся ва Сяо Юй дар бораи имтиҳон сӯҳбат мекунанд",
                "dialogue": [
                    {"speaker": "小夏", "zh": "昨天的考试怎么样？", "pinyin": "", "uz": "Kechagi imtihon qanday o'tdi?", "ru": "Как прошёл вчерашний экзамен?", "tj": "Имтиҳони дирӯза чӣ гуна гузашт?"},
                    {"speaker": "小雨", "zh": "不太好。填空题太难了，连一半都没做对。", "pinyin": "", "uz": "Uncha yaxshi emas. Bo'sh joy to'ldirish savollari juda qiyin edi, hatto yarmini ham to'g'ri qilmadim.", "ru": "Не очень хорошо. Задания с пропусками были слишком сложными — я даже половины не сделал правильно.", "tj": "Он қадар хуб нест. Саволҳои пури холӣ хеле душвор буданд, ҳатто нисфашро дуруст накардам."},
                    {"speaker": "小夏", "zh": "你平时有没有好好复习？否则考试的时候只好猜了。", "pinyin": "", "uz": "Odatda yaxshilab takrorlayapsizmi? Aks holda imtihon paytida majbur bo'lib taxmin qilasiz.", "ru": "Вы обычно хорошо повторяете? Иначе на экзамене остаётся только угадывать.", "tj": "Шумо одатан хуб такрор мекунед? Акс ҳол дар вақти имтиҳон маҷбур мешавед ҳадс занед."},
                    {"speaker": "小雨", "zh": "我知道，下次我一定要养成好的学习习惯，无论多累都要复习。", "pinyin": "", "uz": "Bilaman, keyingi gal albatta yaxshi o'qish odatini shakllantiraman, qanchalik charchagan bo'lmasin takrorlayman.", "ru": "Знаю, в следующий раз обязательно выработаю хорошие учебные привычки — буду повторять материал, независимо от того, насколько устал.", "tj": "Медонам, дафъаи оянда ҳатман одати хуби омӯзишро ташаккул медиҳам, ҳар чӣ қадар хаста бошам ҳам такрор мекунам."},
                    {"speaker": "小夏", "zh": "对，来得及的话，我们一起学吧！", "pinyin": "", "uz": "To'g'ri, vaqt bo'lsa, birga o'rganaylik!", "ru": "Верно, если ещё есть время — давайте учиться вместе!", "tj": "Дуруст, агар вақт бошад, биёед якҷо ёд гирем!"},
                ],
            },
            {
                "block_no": 3,
                "section_label": "课文 3",
                "scene_uz": "Xiao Li Xiao Linga kitob o'qishning foydalari haqida tushuntirmoqda",
                "scene_ru": "Сяо Ли рассказывает Сяо Линю о пользе чтения",
                "scene_tj": "Сяо Ли ба Сяо Лин фоидаҳои мутолиаро шарҳ медиҳад",
                "dialogue": [
                    {"speaker": "小林", "zh": "你为什么每天都要看那么多杂志和书？", "pinyin": "", "uz": "Nega har kuni shuncha ko'p jurnal va kitob o'qiysiz?", "ru": "Почему вы каждый день читаете так много журналов и книг?", "tj": "Чаро ҳар рӯз ин қадар маҷаллаю китоб мехонед?"},
                    {"speaker": "小李", "zh": "阅读能增加知识，同时让我的语言表达更加准确。", "pinyin": "", "uz": "O'qish bilimni oshiradi va bir vaqtda tilim ifodasini yanada aniq qiladi.", "ru": "Чтение увеличивает знания и одновременно делает мою речь более точной.", "tj": "Мутолиа дониширо меафзояд ва дар як вақт ифодаи забонамро дақиқтар мекунад."},
                    {"speaker": "小林", "zh": "那些著名文章的内容你都看懂了吗？", "pinyin": "", "uz": "O'sha mashhur maqolalarning mazmunini tushundingizmi?", "ru": "Вы поняли содержание тех известных статей?", "tj": "Оё мазмуни он мақолаҳои машҳурро фаҳмидед?"},
                    {"speaker": "小李", "zh": "大部分看懂了，然而有些词语还是不明白，只好查字典。", "pinyin": "", "uz": "Ko'p qismini tushundim, biroq ba'zi so'zlarni hali ham bilmay, majbur bo'lib lug'at qaradim.", "ru": "Большую часть понял, однако некоторые слова по-прежнему непонятны — пришлось смотреть в словарь.", "tj": "Аксари онро фаҳмидам, аммо баъзе калимаҳо ҳанӯз ҳам маълум нестанд — маҷбур шудам луғатро нигоҳ кунам."},
                    {"speaker": "小林", "zh": "精彩的书真的值得多读！我也要养成每天读书的习惯。", "pinyin": "", "uz": "Ajoyib kitoblar ko'proq o'qishga arziydi! Men ham har kuni kitob o'qish odatini shakllantirmoqchiman.", "ru": "Замечательные книги действительно стоит читать побольше! Я тоже хочу выработать привычку читать каждый день.", "tj": "Китобҳои аҷоиб воқеан арзанда аст, ки бештар хонда шаванд! Ман ҳам мехоҳам одати ҳар рӯз китоб хонданро ташаккул диҳам."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "连……也/都……",
                "title_uz": "连……也/都…… (hatto...ham...)",
                "title_ru": "连……也/都…… (даже...тоже/всё равно...)",
                "title_tj": "连……也/都…… (ҳатто...ҳам...)",
                "rule_uz": "'Hatto' ma'nosini beradi. Ekstremal yoki kutilmagan holatni ta'kidlaydi. 连 dan keyingi element ajablantiradigan narsa. Qolip: 连 + [ot/fe'l] + 也/都 + [kesim].",
                "rule_ru": "Означает «даже»; используется для акцента на крайнем или неожиданном случае. Элемент после 连 — это то, что удивительно. Конструкция: 连 + [сущ./гл.] + 也/都 + [сказуемое].",
                "rule_tj": "Маънои «ҳатто»-ро медиҳад; барои таъкиди ҳолати ифротӣ ё ғайричашмдошт истифода мешавад. Унсури пас аз 连 чизи ғайричашмдошт аст. Қолаб: 连 + [исм/феъл] + 也/都 + [хабар].",
                "examples": [
                    {"zh": "他连基本词语都不准确。", "pinyin": "", "uz": "U hatto asosiy so'zlarni ham aniq ayta olmaydi.", "ru": "Он даже базовые слова не может произнести правильно.", "tj": "Ӯ ҳатто калимаҳои асосиро ҳам дақиқ гуфта наметавонад."},
                    {"zh": "她忙得连饭都没时间吃。", "pinyin": "", "uz": "U shunchalik bandki, hatto ovqatlanishga vaqti yo'q.", "ru": "Она настолько занята, что даже не успевает поесть.", "tj": "Ӯ он қадар банд аст, ки ҳатто вақт барои хӯрок хӯрдан надорад."},
                ],
            },
            {
                "no": 2,
                "title_zh": "否则",
                "title_uz": "否则 (aks holda, bo'lmasa)",
                "title_ru": "否则 (иначе, в противном случае)",
                "title_tj": "否则 (акс ҳол, дар ғайри ин сурат)",
                "rule_uz": "'Aks holda, bo'lmasa' ma'nosini beradi. Avvalgi shart bajarilmasa yuz beradigan salbiy natijani bildiradi. Ikki gap o'rtasida ishlatiladi.",
                "rule_ru": "Означает «иначе, в противном случае»; вводит негативное последствие, которое произойдёт, если предыдущее условие не выполнено. Употребляется между двумя предложениями.",
                "rule_tj": "Маънои «акс ҳол, дар ғайри ин сурат»-ро медиҳад. Натиҷаи манфиеро нишон медиҳад, ки агар шарти қаблӣ иҷро нашавад, рӯй медиҳад. Байни ду ҷумла истифода мешавад.",
                "examples": [
                    {"zh": "你要好好复习，否则考试只好猜了。", "pinyin": "", "uz": "Yaxshilab takrorlash kerak, aks holda imtihonda majbur bo'lib taxmin qilasiz.", "ru": "Нужно хорошо повторить, иначе на экзамене придётся только угадывать.", "tj": "Бояд хуб такрор кард, акс ҳол дар имтиҳон маҷбур мешавед ҳадс занед."},
                    {"zh": "快点走吧，否则要迟到了。", "pinyin": "", "uz": "Tezroq boraylik, aks holda kechikamiz.", "ru": "Поспешим, иначе опоздаем.", "tj": "Зудтар биравем, акс ҳол дер мемонем."},
                ],
            },
            {
                "no": 3,
                "title_zh": "无论……都/也……",
                "title_uz": "无论……都/也…… (qanday bo'lmasin...baribir...)",
                "title_ru": "无论……都/也…… (независимо от...всё равно...)",
                "title_tj": "无论……都/也…… (ҳар чӣ бошад...боз ҳам...)",
                "rule_uz": "'Qanday bo'lmasin; farqi yo'q' ma'nosini beradi. Shart qanday bo'lishidan qat'i nazar natija o'zgarmaydi. Qolip: 无论 + [shart] + 都/也 + [natija].",
                "rule_ru": "Означает «независимо от того, что/как/кто»; результат одинаков при любом условии. Конструкция: 无论 + [условие] + 都/也 + [результат].",
                "rule_tj": "Маънои «ҳар чӣ бошад; новобаста аз»-ро медиҳад. Натиҷа новобаста аз шарт яксон аст. Қолаб: 无论 + [шарт] + 都/也 + [натиҷа].",
                "examples": [
                    {"zh": "无论多忙，我都坚持阅读。", "pinyin": "", "uz": "Qanchalik band bo'lmasin, men doim o'qishni davom ettiraman.", "ru": "Независимо от того, насколько я занят, я всегда продолжаю читать.", "tj": "Ҳар чӣ қадар банд бошам, ман ҳамеша мутолиаро давом медиҳам."},
                    {"zh": "无论你去哪里，我都支持你。", "pinyin": "", "uz": "Qayerga bormaylik, men seni qo'llab-quvvatlayman.", "ru": "Независимо от того, куда ты пойдёшь, я тебя поддержу.", "tj": "Ба куҷо бравӣ ҳам, ман туро дастгирӣ мекунам."},
                ],
            },
            {
                "no": 4,
                "title_zh": "然而",
                "title_uz": "然而 (biroq, ammo — rasmiy yozma)",
                "title_ru": "然而 (однако, но — книжный стиль)",
                "title_tj": "然而 (аммо, лекин — услуби расмии хаттӣ)",
                "rule_uz": "'Biroq, ammo' ma'nosini beradi. Rasmiy yozma uslubdagi bog'lovchi. Ziddiyat yoki kutilmagan o'zgarishni bildiradi. 但是 ga o'xshash, lekin badiiyroq.",
                "rule_ru": "Означает «однако, но»; книжный союз, вводящий контраст или неожиданный поворот. Похоже на 但是, но более литературное.",
                "rule_tj": "Маънои «аммо, лекин»-ро медиҳад; пайвандаки расмии хаттӣ, ки муқобилат ё тағйири ногаҳонӣ меорад. Монанди 但是 аст, аммо адабиётиртар.",
                "examples": [
                    {"zh": "我努力学习，然而成绩还是不理想。", "pinyin": "", "uz": "Men qattiq o'qidim, biroq natijam hali ham qoniqarli emas.", "ru": "Я усердно учился, однако результаты по-прежнему неудовлетворительные.", "tj": "Ман сахт таҳсил кардам, аммо натиҷаҳо ҳанӯз ҳам қонеъкунанда нестанд."},
                    {"zh": "他看起来很轻松，然而内心很紧张。", "pinyin": "", "uz": "U xotirjam ko'rinadi, biroq ichida juda hayajonlangan.", "ru": "Он выглядит спокойным, однако внутри очень нервничает.", "tj": "Ӯ ором менамояд, аммо дар ботин хеле ҳаяҷонзада аст."},
                ],
            },
            {
                "no": 5,
                "title_zh": "同时",
                "title_uz": "同时 (bir vaqtda, shu bilan birga)",
                "title_ru": "同时 (в то же время, одновременно)",
                "title_tj": "同时 (дар як вақт, ҳамзамон)",
                "rule_uz": "'Bir vaqtda, shu bilan birga' ma'nosini beradi. Ikki harakat yoki holat bir vaqtda sodir bo'lishini bildiradi. Ikkita parallel fikrni ham bog'laydi.",
                "rule_ru": "Означает «в то же время, одновременно»; указывает на два действия или состояния, происходящих одновременно. Также соединяет два параллельных суждения.",
                "rule_tj": "Маънои «дар як вақт, ҳамзамон»-ро медиҳад. Ду амал ё ҳолатро, ки дар як вақт рӯй медиҳанд, нишон медиҳад. Инчунин ду фикри параллелиро мепайвандад.",
                "examples": [
                    {"zh": "阅读能增加知识，同时提高语言能力。", "pinyin": "", "uz": "O'qish bilimni oshiradi va bir vaqtda til qobiliyatini yaxshilaydi.", "ru": "Чтение увеличивает знания и одновременно повышает языковые способности.", "tj": "Мутолиа дониширо меафзояд ва дар як вақт қобилияти забониро баланд мебардорад."},
                    {"zh": "他是一位老师，同时也是一位作家。", "pinyin": "", "uz": "U o'qituvchi, shu bilan birga yozuvchi ham.", "ru": "Он учитель и в то же время писатель.", "tj": "Ӯ муаллим аст ва дар як вақт нависанда ҳам мебошад."},
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
                    {"prompt_uz": "ravon, bemalol", "prompt_ru": "беглый, свободный", "prompt_tj": "равон, бемалол", "answer": "流利", "pinyin": "liúlì"},
                    {"prompt_uz": "grammatika", "prompt_ru": "грамматика", "prompt_tj": "грамматика", "answer": "语法", "pinyin": "yǔfǎ"},
                    {"prompt_uz": "aniq, to'g'ri", "prompt_ru": "точный, правильный", "prompt_tj": "дақиқ, дуруст", "answer": "准确", "pinyin": "zhǔnquè"},
                    {"prompt_uz": "maqola, matn", "prompt_ru": "статья, текст, эссе", "prompt_tj": "мақола, матн", "answer": "文章", "pinyin": "wénzhāng"},
                    {"prompt_uz": "odat shakllantirmoq", "prompt_ru": "вырабатывать привычку", "prompt_tj": "одат ташаккул додан", "answer": "养成", "pinyin": "yǎngchéng"},
                    {"prompt_uz": "ajoyib, zo'r", "prompt_ru": "замечательный, великолепный", "prompt_tj": "аҷоиб, зӯр", "answer": "精彩", "pinyin": "jīngcǎi"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский перевод следующих слов:",
                "instruction_tj": "Тарҷумаи ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "词语", "prompt_ru": "词语", "prompt_tj": "词语", "answer": "so'z, ibora", "pinyin": "cíyǔ"},
                    {"prompt_uz": "增加", "prompt_ru": "增加", "prompt_tj": "增加", "answer": "oshirmoq, ko'paytirmoq", "pinyin": "zēngjiā"},
                    {"prompt_uz": "内容", "prompt_ru": "内容", "prompt_tj": "内容", "answer": "mazmun, kontent", "pinyin": "nèiróng"},
                    {"prompt_uz": "看法", "prompt_ru": "看法", "prompt_tj": "看法", "answer": "nuqtai nazar, fikr", "pinyin": "kànfǎ"},
                    {"prompt_uz": "顺序", "prompt_ru": "顺序", "prompt_tj": "顺序", "answer": "tartib, ketma-ketlik", "pinyin": "shùnxù"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (连、否则、无论、然而、同时):",
                "instruction_ru": "Выберите подходящее слово (连、否则、无论、然而、同时):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (连、否则、无论、然而、同时):",
                "items": [
                    {"prompt_uz": "______多忙，我都坚持学习。", "prompt_ru": "______多忙，我都坚持学习。", "prompt_tj": "______多忙，我都坚持学习。", "answer": "无论", "pinyin": "wúlùn"},
                    {"prompt_uz": "你要认真学习，______考试会不及格。", "prompt_ru": "你要认真学习，______考试会不及格。", "prompt_tj": "你要认真学习，______考试会不及格。", "answer": "否则", "pinyin": "fǒuzé"},
                    {"prompt_uz": "他______基本的词语都不认识。", "prompt_ru": "他______基本的词语都不认识。", "prompt_tj": "他______基本的词语都不认识。", "answer": "连", "pinyin": "lián"},
                    {"prompt_uz": "她努力工作，______照顾家庭。", "prompt_ru": "她努力工作，______照顾家庭。", "prompt_tj": "她努力工作，______照顾家庭。", "answer": "同时", "pinyin": "tóngshí"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["流利", "语法", "准确", "文章", "养成", "精彩"]},
            {"no": 2, "answers": ["so'z, ibora", "oshirmoq, ko'paytirmoq", "mazmun, kontent", "nuqtai nazar, fikr", "tartib, ketma-ketlik"]},
            {"no": 3, "answers": ["无论", "否则", "连", "同时"]},
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
                "words": ["流利", "养成", "阅读", "精彩"],
                "example": "我养成了每天阅读的好习惯，所以我的汉语越来越流利。",
            },
            {
                "no": 2,
                "instruction_uz": "'无论……都……' qolipidan foydalanib 2 ta gap tuzing.",
                "instruction_ru": "Напишите 2 предложения с конструкцией '无论……都……'.",
                "instruction_tj": "Бо қолаби '无论……都……' 2 ҷумла нависед.",
                "topic_uz": "o'qish yoki kundalik hayot odatlari haqida",
                "topic_ru": "о привычках в учёбе или повседневной жизни",
                "topic_tj": "дар бораи одатҳои таҳсилӣ ё зиндагии ҳаррӯза",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Kitob o'qishning afzalliklari nimada? 读书有哪些好处？",
                "topic_ru": "В чём польза чтения? 读书有哪些好处？",
                "topic_tj": "Фоидаҳои мутолиа дар чист? 读书有哪些好处？",
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
