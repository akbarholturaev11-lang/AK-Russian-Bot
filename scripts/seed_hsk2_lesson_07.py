import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 7,
    "lesson_code": "HSK2-L07",
    "title": "你家离公司远吗",
    "goal": json.dumps({"uz": "Masofa, yo'l vaqti va joylashuv haqida gapira olish; 还 ravishining ikkinchi ma'nosini, 就 vaqt ravishinini, 离 old ko'makchisini va 呢 yuklamasini o'zlashtirish.", "ru": "Научиться говорить о расстоянии, времени в пути и местонахождении; освоить второе значение 还, наречие времени 就, предлог 离 и частицу 呢.", "tj": "Омӯзиши гуфтан дар бораи масофа, вақти роҳ ва ҷойгиршавӣ; аз бар кардани маъноии дуввуми 还, зарфи вақтии 就, пешояндии 离 ва ҷузъаи 呢."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda uy, maktab, aeroport va yo'l masofasi haqida suhbat o'rganiladi. Transport vositasi, yo'l davomiyligi va joy topish mavzularida gapira olasiz. Asosiy grammatik mavzular: 还 (hali), 就 (yaqinda, tez), 离 (masofani ifodalash) va 呢 yuklama.", "ru": "В этом уроке изучаются разговоры о доме, школе, аэропорте и расстоянии в дороге. Вы сможете говорить о транспортных средствах, продолжительности пути и нахождении мест. Основные грамматические темы: 还 (ещё), 就 (скоро, быстро), 离 (выражение расстояния) и частица 呢.", "tj": "Дар ин дарс муколамаҳо дар бораи хона, мактаб, фурудгоҳ ва масофаи роҳ омӯхта мешаванд. Шумо метавонед дар бораи воситаи нақлиёт, давомнокии роҳ ва ёфтани ҷой гап занед. Мавзӯҳои асосии грамматикӣ: 还 (ҳанӯз), 就 (зуд, ба зудӣ), 离 (ифодаи масофа) ва ҷузъаи 呢."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "教室",     "pinyin": "jiàoshì",       "pos": "n.",    "uz": "darsxona, sinf xonasi",                   "ru": "классная комната, аудитория",         "tj": "синфхона, толори дарс"},
        {"no": 2,  "zh": "机场",     "pinyin": "jīchǎng",       "pos": "n.",    "uz": "aeroport",                                "ru": "аэропорт",                            "tj": "фурудгоҳ"},
        {"no": 3,  "zh": "路",       "pinyin": "lù",             "pos": "n.",    "uz": "yo'l, ko'cha",                            "ru": "дорога, улица",                       "tj": "роҳ, кӯча"},
        {"no": 4,  "zh": "离",       "pinyin": "lí",             "pos": "prep.", "uz": "dan (masofa ifodalash uchun)",            "ru": "от, до (для выражения расстояния)",   "tj": "аз (барои ифодаи масофа)"},
        {"no": 5,  "zh": "公司",     "pinyin": "gōngsī",        "pos": "n.",    "uz": "kompaniya, firma",                        "ru": "компания, фирма",                     "tj": "ширкат, корхона"},
        {"no": 6,  "zh": "远",       "pinyin": "yuǎn",           "pos": "adj.",  "uz": "uzoq (masofa haqida)",                   "ru": "далёкий, дальний",                    "tj": "дур (дар бораи масофа)"},
        {"no": 7,  "zh": "公共汽车", "pinyin": "gōnggòng qìchē", "pos": "n.",    "uz": "avtobus (jamoat transporti)",             "ru": "автобус (общественный транспорт)",    "tj": "автобус (нақлиёти ҷамъиятӣ)"},
        {"no": 8,  "zh": "小时",     "pinyin": "xiǎoshí",       "pos": "n.",    "uz": "soat (vaqt o'lchovi)",                   "ru": "час (единица времени)",               "tj": "соат (воҳиди вақт)"},
        {"no": 9,  "zh": "慢",       "pinyin": "màn",            "pos": "adj.",  "uz": "sekin, asta",                             "ru": "медленный",                           "tj": "суст, оҳиста"},
        {"no": 10, "zh": "快",       "pinyin": "kuài",           "pos": "adj.",  "uz": "tez, shoshilinch",                        "ru": "быстрый",                             "tj": "тез, чолок"},
        {"no": 11, "zh": "过",       "pinyin": "guò",            "pos": "v.",    "uz": "o'tmoq; o'tkazmoq (bayramni)",           "ru": "проходить; отмечать (праздник)",      "tj": "гузаштан; ҷашн гирифтан"},
        {"no": 12, "zh": "走",       "pinyin": "zǒu",            "pos": "v.",    "uz": "yurib bormoq, ketmoq",                   "ru": "идти пешком, уходить",                "tj": "пиёда рафтан, рафтан"},
        {"no": 13, "zh": "到",       "pinyin": "dào",            "pos": "v.",    "uz": "yetib bormoq, kelmoq",                   "ru": "добираться, прибывать",               "tj": "расидан, омадан"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "大卫回来了吗？", "pinyin": "Dàwèi huílái le ma?", "uz": "Devid qaytib keldimi?", "ru": "Дэвид вернулся?", "tj": "Дэвид баргашт?"},
                {"speaker": "B", "zh": "没有，他还在教室学习呢。", "pinyin": "Méiyǒu, tā hái zài jiàoshì xuéxí ne.", "uz": "Yo'q, u hali darsxonada o'qiyapti.", "ru": "Нет, он ещё занимается в классе.", "tj": "Не, вай ҳанӯз дар синфхона дарс мехонад."},
                {"speaker": "A", "zh": "已经9点多了，他怎么还在学习？", "pinyin": "Yǐjīng jiǔ diǎn duō le, tā zěnme hái zài xuéxí?", "uz": "Soat to'qqizdan oshdi, u nega hali ham o'qiyapti?", "ru": "Уже больше девяти, почему он ещё занимается?", "tj": "Аллакай аз соати нӯҳ гузашт, чаро вай ҳанӯз дарс мехонад?"},
                {"speaker": "B", "zh": "明天有考试，他说今天要好好准备。", "pinyin": "Míngtiān yǒu kǎoshì, tā shuō jīntiān yào hǎohǎo zhǔnbèi.", "uz": "Ertaga imtihon bor, u bugun yaxshilab tayyorlanaman, dedi.", "ru": "Завтра экзамен, он сказал, что сегодня хочет хорошо подготовиться.", "tj": "Фардо имтиҳон аст, вай гуфт, ки имрӯз мехоҳад хуб омода шавад."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Aeroportga yo'lda",
            "scene_ru": "По дороге в аэропорт",
            "scene_tj": "Дар роҳ ба фурудгоҳ",
            "dialogue": [
                {"speaker": "A", "zh": "你现在在哪儿呢？", "pinyin": "Nǐ xiànzài zài nǎr ne?", "uz": "Hozir qayerdasen?", "ru": "Где ты сейчас?", "tj": "Ту ҳоло куҷоӣ?"},
                {"speaker": "B", "zh": "在去机场的路上。你已经到了吗？", "pinyin": "Zài qù jīchǎng de lùshang. Nǐ yǐjīng dào le ma?", "uz": "Aeroportga ketayotgan yo'ldaman. Sen allaqachon yetib kelding mi?", "ru": "На пути в аэропорт. Ты уже добрался?", "tj": "Дар роҳ ба фурудгоҳам. Оё ту аллакай расидӣ?"},
                {"speaker": "A", "zh": "我下飞机了。你还有多长时间能到这儿？", "pinyin": "Wǒ xià fēijī le. Nǐ hái yǒu duō cháng shíjiān néng dào zhèr?", "uz": "Men samolyotdan tushdim. Sening yetib kelishingga qancha vaqt qoldi?", "ru": "Я уже вышел из самолёта. Сколько тебе ещё ехать?", "tj": "Ман аз ҳавопаймо фаромадам. То ба ин ҷо расидани ту чанд вақт мемонад?"},
                {"speaker": "B", "zh": "二十分钟就到。", "pinyin": "Èrshí fēnzhōng jiù dào.", "uz": "Yigirma daqiqada yetib boraman.", "ru": "Через двадцать минут буду.", "tj": "Дар бист дақиқа мерасам."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Sport zalida",
            "scene_ru": "В спортзале",
            "scene_tj": "Дар толори варзиш",
            "dialogue": [
                {"speaker": "A", "zh": "你家离公司远吗？", "pinyin": "Nǐ jiā lí gōngsī yuǎn ma?", "uz": "Uying kompaniyadan uzoqmi?", "ru": "Ваш дом далеко от компании?", "tj": "Хонаи ту аз ширкат дур аст?"},
                {"speaker": "B", "zh": "很远，坐公共汽车要一个多小时呢！", "pinyin": "Hěn yuǎn, zuò gōnggòng qìchē yào yí ge duō xiǎoshí ne!", "uz": "Juda uzoq, avtobus bilan bir soatdan ko'proq vaqt ketadi!", "ru": "Очень далеко, на автобусе больше часа!", "tj": "Бисёр дур, бо автобус аз як соат зиёд лозим!"},
                {"speaker": "A", "zh": "坐公共汽车太慢了，你怎么不开车？", "pinyin": "Zuò gōnggòng qìchē tài màn le, nǐ zěnme bù kāi chē?", "uz": "Avtobus juda sekin, nega mashina haydamaysan?", "ru": "На автобусе слишком медленно, почему ты не едешь на машине?", "tj": "Бо автобус хеле суст, чаро ту мошин намерони?"},
                {"speaker": "B", "zh": "开车也不快，路上车太多了！", "pinyin": "Kāi chē yě bù kuài, lùshang chē tài duō le!", "uz": "Mashina ham tez emas, yo'lda mashina juda ko'p!", "ru": "На машине тоже не быстро, на дороге слишком много машин!", "tj": "Мошин ҳам тез нест, дар роҳ мошин бисёр зиёд!"},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Yo'lda",
            "scene_ru": "В дороге",
            "scene_tj": "Дар роҳ",
            "dialogue": [
                {"speaker": "A", "zh": "今天晚上我们一起吃饭吧，给你过生日。", "pinyin": "Jīntiān wǎnshang wǒmen yìqǐ chīfàn ba, gěi nǐ guò shēngrì.", "uz": "Bugun kechqurun birga ovqatlanaylik, senga tug'ilgan kunni nishonlaymiz.", "ru": "Давай сегодня вечером вместе поужинаем, отметим твой день рождения.", "tj": "Биёед имшаб якҷоя шом бихӯрем, таваллуди туро ҷашн мегирем."},
                {"speaker": "B", "zh": "今天？离我的生日还有一个多星期呢！", "pinyin": "Jīntiān? Lí wǒ de shēngrì hái yǒu yí ge duō xīngqī ne!", "uz": "Bugunmi? Mening tug'ilgan kunim hali bir haftadan ko'proq bor!", "ru": "Сегодня? До моего дня рождения ещё больше недели!", "tj": "Имрӯз? То таваллуди ман ҳанӯз аз як ҳафта зиёд мемонад!"},
                {"speaker": "A", "zh": "下个星期我要去北京，今天过吧。", "pinyin": "Xià ge xīngqī wǒ yào qù Běijīng, jīntiān guò ba.", "uz": "Kelgusi hafta men Pekinga ketaman, shuning uchun bugun nishonlaymiz.", "ru": "На следующей неделе я еду в Пекин, давай отметим сегодня.", "tj": "Ҳафтаи оянда ман ба Пекин меравам, биёед имрӯз ҷашн гирем."},
                {"speaker": "B", "zh": "好吧，离这儿不远有一个中国饭馆，走几分钟就到了。", "pinyin": "Hǎo ba, lí zhèr bù yuǎn yǒu yí ge Zhōngguó fànguǎn, zǒu jǐ fēnzhōng jiù dào le.", "uz": "Mayli, bu yerdan uzoq bo'lmagan yerda xitoy restoran bor, bir necha daqiqa yursak yetib boramiz.", "ru": "Хорошо, недалеко отсюда есть китайский ресторан, пешком несколько минут.", "tj": "Хуб, аз ин ҷо дур нест як тарабхонаи чинӣ ҳаст, чанд дақиқа пиёда рафтем мерасем."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "语气副词“还”（2）",
            "title_uz": "Ravish 还 — ikkinchi ma'nosi (hali, hanuz)",
            "title_ru": "Наречие 还 — второе значение (ещё, по-прежнему)",
            "title_tj": "Зарф 还 — маъноии дуввум (ҳанӯз, то ҳол)",
            "rule_uz": (
                "'还' ravishining ikkinchi ma'nosi — 'hali, hanuz'.\n"
                "Biror holat davom etayotganini yoki biror narsa hali sodir bo'lmaganini bildiradi.\n"
                "Ko'pincha 呢 yuklama bilan birga keladi."
            ),
            "rule_ru": (
                "Второе значение наречия '还' — 'ещё, по-прежнему'.\n"
                "Обозначает продолжение какого-либо состояния или то, что что-то ещё не произошло.\n"
                "Часто используется вместе с частицей 呢."
            ),
            "rule_tj": (
                "Маъноии дуввуми зарфи '还' — 'ҳанӯз, то ҳол'.\n"
                "Нишон медиҳад, ки ягон ҳолат идома дорад ё ягон чиз ҳанӯз рӯй надодааст.\n"
                "Аксар вақт бо ҷузъаи 呢 якҷоя истифода мешавад."
            ),
            "examples": [
                {"zh": "他还在教室学习呢。", "pinyin": "Tā hái zài jiàoshì xuéxí ne.", "uz": "U hali darsxonada o'qiyapti.", "ru": "Он ещё занимается в классе.", "tj": "Вай ҳанӯз дар синфхона дарс мехонад."},
                {"zh": "离我的生日还有一个多星期。", "pinyin": "Lí wǒ de shēngrì hái yǒu yí ge duō xīngqī.", "uz": "Tug'ilgan kunim hali bir haftadan ko'proq bor.", "ru": "До моего дня рождения ещё больше недели.", "tj": "То таваллуди ман ҳанӯз аз як ҳафта зиёд мемонад."},
            ]
        },
        {
            "no": 2,
            "title_zh": "时间副词“就”",
            "title_uz": "Vaqt ravishi 就 (tez, yaqinda, darhol)",
            "title_ru": "Наречие времени 就 (скоро, быстро, сразу)",
            "title_tj": "Зарфи вақт 就 (зуд, ба зудӣ, дарҳол)",
            "rule_uz": (
                "'就' ravishi vaqt ifodasida 'tez, yaqinda, darhol' ma'nosini beradi.\n"
                "Biror hodisa kutilgandan tezroq yoki yaqinroq bo'lishini ta'kidlaydi."
            ),
            "rule_ru": (
                "Наречие '就' в выражении времени означает 'скоро, быстро, сразу'.\n"
                "Подчёркивает, что событие произойдёт быстрее или ближе, чем ожидалось."
            ),
            "rule_tj": (
                "Зарфи '就' дар ифодаи вақт маъноии 'зуд, ба зудӣ, дарҳол'-ро медиҳад.\n"
                "Таъкид мекунад, ки ягон ҳодиса тезтар ё наздиктар аз он ки интизор буданд рӯй медиҳад."
            ),
            "examples": [
                {"zh": "二十分钟就到。", "pinyin": "Èrshí fēnzhōng jiù dào.", "uz": "Yigirma daqiqada yetib boraman.", "ru": "Через двадцать минут буду.", "tj": "Дар бист дақиқа мерасам."},
                {"zh": "走几分钟就到了。", "pinyin": "Zǒu jǐ fēnzhōng jiù dào le.", "uz": "Bir necha daqiqa yursak yetib boramiz.", "ru": "Несколько минут пешком — и на месте.", "tj": "Чанд дақиқа пиёда равем — мерасем."},
            ]
        },
        {
            "no": 3,
            "title_zh": "离",
            "title_uz": "Old ko'makchi 离 (masofani ifodalash)",
            "title_ru": "Предлог 离 (выражение расстояния)",
            "title_tj": "Пешоянди 离 (ифодаи масофа)",
            "rule_uz": (
                "'离' old ko'makchisi ikki joy yoki ikki vaqt o'rtasidagi masofani bildiradi.\n"
                "Gap tuzilishi: A + 离 + B + masofa/vaqt.\n"
                "O'zbek tilidagi '...dan (qancha uzoqlikda)' iborasiga to'g'ri keladi."
            ),
            "rule_ru": (
                "Предлог '离' выражает расстояние между двумя местами или промежуток времени.\n"
                "Структура предложения: A + 离 + B + расстояние/время.\n"
                "Соответствует русскому 'от ... (на каком расстоянии)'."
            ),
            "rule_tj": (
                "Пешоянди '离' масофаро байни ду ҷой ё фосилаи вақтиро нишон медиҳад.\n"
                "Сохтори ҷумла: A + 离 + B + масофа/вақт.\n"
                "Ба тоҷикӣ 'аз ... (дар чанд масофа)' мувофиқат мекунад."
            ),
            "examples": [
                {"zh": "你家离公司远吗？", "pinyin": "Nǐ jiā lí gōngsī yuǎn ma?", "uz": "Uying kompaniyadan uzoqmi?", "ru": "Ваш дом далеко от компании?", "tj": "Хонаи ту аз ширкат дур аст?"},
                {"zh": "离这儿不远有一个中国饭馆。", "pinyin": "Lí zhèr bù yuǎn yǒu yí ge Zhōngguó fànguǎn.", "uz": "Bu yerdan uzoq bo'lmagan yerda xitoy restoran bor.", "ru": "Недалеко отсюда есть китайский ресторан.", "tj": "Аз ин ҷо дур нест як тарабхонаи чинӣ ҳаст."},
            ]
        },
        {
            "no": 4,
            "title_zh": "语气助词“呢”",
            "title_uz": "Modal yuklamasi 呢 (davomiylik, ta'kid, -chi?)",
            "title_ru": "Модальная частица 呢 (продолжение, усиление, -а?)",
            "title_tj": "Ҷузъаи оҳангии 呢 (давомнокӣ, таъкид, -чӣ?)",
            "rule_uz": (
                "'呢' yuklama gap oxirida kelib davomiylik yoki ta'kidlash bildiradigan ohang hosil qiladi.\n"
                "Ko'pincha hayrat yoki ta'kid ifodalaydi.\n"
                "Savol gapida esa qisqa 'a, -chi?' ma'nosini beradi."
            ),
            "rule_ru": (
                "Частица '呢' в конце предложения создаёт интонацию продолжения или усиления.\n"
                "Часто выражает удивление или подчёркивание.\n"
                "В вопросительном предложении имеет значение 'а?, ну?'."
            ),
            "rule_tj": (
                "Ҷузъаи '呢' дар охири ҷумла оҳанги давомнокӣ ё таъкидро ба вуҷуд меорад.\n"
                "Аксар вақт шигифт ё таъкидро ифода мекунад.\n"
                "Дар ҷумлаи саволӣ маъноии '-чӣ? -а?' дорад."
            ),
            "examples": [
                {"zh": "坐公共汽车要一个多小时呢！", "pinyin": "Zuò gōnggòng qìchē yào yí ge duō xiǎoshí ne!", "uz": "Avtobus bilan bir soatdan ko'proq vaqt ketadi!", "ru": "На автобусе больше часа!", "tj": "Бо автобус аз як соат зиёд лозим!"},
                {"zh": "你现在在哪儿呢？", "pinyin": "Nǐ xiànzài zài nǎr ne?", "uz": "Hozir qayerdasen?", "ru": "Где ты сейчас?", "tj": "Ту ҳоло куҷоӣ?"},
            ]
        },
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
            "instruction_ru": "Напишите по-китайски следующие слова:",
            "instruction_tj": "Калимаҳои зеринро бо хатти чинӣ нависед:",
            "items": [
                {"prompt_uz": "aeroport",                    "prompt_ru": "аэропорт",                        "prompt_tj": "фурудгоҳ",                    "answer": "机场",     "pinyin": "jīchǎng"},
                {"prompt_uz": "avtobus (jamoat transporti)", "prompt_ru": "автобус (общественный транспорт)", "prompt_tj": "автобус (нақлиёти ҷамъиятӣ)","answer": "公共汽车", "pinyin": "gōnggòng qìchē"},
                {"prompt_uz": "uzoq",                        "prompt_ru": "далёкий",                         "prompt_tj": "дур",                         "answer": "远",       "pinyin": "yuǎn"},
                {"prompt_uz": "sekin",                       "prompt_ru": "медленный",                       "prompt_tj": "суст",                        "answer": "慢",       "pinyin": "màn"},
                {"prompt_uz": "yetib bormoq",                "prompt_ru": "добираться",                      "prompt_tj": "расидан",                     "answer": "到",       "pinyin": "dào"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (离、还、就、呢、慢):",
            "instruction_ru": "Вставьте подходящее слово (离、还、就、呢、慢):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (离、还、就、呢、慢):",
            "items": [
                {"prompt_uz": "你家______公司远吗？", "prompt_ru": "你家______公司远吗？", "prompt_tj": "你家______公司远吗？", "answer": "离", "pinyin": "lí"},
                {"prompt_uz": "他______在教室学习______！", "prompt_ru": "他______在教室学习______！", "prompt_tj": "他______在教室学习______！", "answer": "还 / 呢", "pinyin": "hái / ne"},
                {"prompt_uz": "二十分钟______到了。", "prompt_ru": "二十分钟______到了。", "prompt_tj": "二十分钟______到了。", "answer": "就", "pinyin": "jiù"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "你家离公司远吗？", "prompt_ru": "你家离公司远吗？", "prompt_tj": "你家离公司远吗？", "answer": "Uying kompaniyadan uzoqmi?", "pinyin": "Nǐ jiā lí gōngsī yuǎn ma?"},
                {"prompt_uz": "走几分钟就到了。", "prompt_ru": "走几分钟就到了。", "prompt_tj": "走几分钟就到了。", "answer": "Bir necha daqiqa yursak yetib boramiz.", "pinyin": "Zǒu jǐ fēnzhōng jiù dào le."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["机场", "公共汽车", "远", "慢", "到"]},
        {"no": 2, "answers": ["离", "还 / 呢", "就"]},
        {"no": 3, "answers": ["Uying kompaniyadan uzoqmi?", "Bir necha daqiqa yursak yetib boramiz."]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "'离' old ko'makchisidan foydalanib 4 ta gap tuzing. Uyingiz, maktabingiz, do'koningiz va aeroportga masofani tasvirlang.",
            "instruction_ru": "Составьте 4 предложения, используя предлог '离'. Опишите расстояние до вашего дома, школы, магазина и аэропорта.",
            "instruction_tj": "Бо истифода аз пешоянди '离' 4 ҷумла тартиб диҳед. Масофаро то хона, мактаб, мағоза ва фурудгоҳи худ тасвир кунед.",
            "words": ["离", "远", "近", "分钟", "小时"],
            "example": "我家离学校很近，走五分钟就到了。",
        },
        {
            "no": 2,
            "instruction_uz": "O'z kundalik yo'lingiz haqida 5-6 gapdan iborat matn yozing. Qayerdan qayerga borasiz? Necha daqiqa? Qanday transport vositasida?",
            "instruction_ru": "Напишите текст из 5–6 предложений о вашем ежедневном маршруте. Откуда куда вы едете? Сколько минут? На каком транспорте?",
            "instruction_tj": "Дар бораи роҳи рӯзонаи худ матне аз 5-6 ҷумла нависед. Аз куҷо ба куҷо меравед? Чанд дақиқа? Бо кадом нақлиёт?",
            "topic_uz": "Mening kundalik yo'lim",
            "topic_ru": "Мой ежедневный маршрут",
            "topic_tj": "Роҳи рӯзонаи ман",
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
