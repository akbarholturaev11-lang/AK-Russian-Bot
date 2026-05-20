import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk3",
    "lesson_order": 6,
    "lesson_code": "HSK3-L06",
    "title": "怎么突然找不到了",
    "goal": json.dumps({"uz": "Mumkinlik to'ldiruvchisi V得/不+natija, '呢' so'roqchi so'zi va 'just now' ma'nosidagi 刚/刚才 farqini o'zlashtirish.", "ru": "Освоить потенциальное дополнение V得/不+результат, вопросительную частицу 呢 и разницу 刚/刚才.", "tj": "Азхудкунии иловаи потенсиалии V得/不+натиҷа, зарраи саволии 呢 ва фарқи 刚/刚才."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda narsalarni topa olish/ololmaslik, joylashuvni so'rash va hozirgina bo'lgan voqealarni tasvirlash o'rganiladi. Uy, idora, park va xiyobondagi suhbatlar orqali ko'nikmalar shakllanadi.", "ru": "В этом уроке изучается возможность/невозможность найти что-то, вопросы о местонахождении и описание недавно произошедшего. Навыки формируются через диалоги дома, в офисе, в парке и на бульваре.", "tj": "Дар ин дарс имконияти ёфтан/наёфтани чизе, пурсидани ҷой ва тасвири рӯйдодҳои наздик омӯхта мешавад. Малакаҳо тавассути муколамаҳо дар хона, идора, боғ ва хиёбон ташаккул меёбанд."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "眼镜",  "pinyin": "yǎnjìng",  "pos": "n.",   "uz": "ko'zoynak",                          "ru": "очки",                           "tj": "айнак"},
        {"no": 2,  "zh": "突然",  "pinyin": "tūrán",    "pos": "adv.", "uz": "to'satdan, birdaniga",               "ru": "вдруг, внезапно",                "tj": "якбора, ногаҳон"},
        {"no": 3,  "zh": "离开",  "pinyin": "líkāi",    "pos": "v.",   "uz": "ketmoq, tark etmoq",                 "ru": "уходить, покидать",              "tj": "рафтан, тарк кардан"},
        {"no": 4,  "zh": "清楚",  "pinyin": "qīngchǔ",  "pos": "adj.", "uz": "aniq, ravshan, tushinarli",          "ru": "ясный, чёткий, понятный",        "tj": "равшан, аниқ, фаҳмо"},
        {"no": 5,  "zh": "刚才",  "pinyin": "gāngcái",  "pos": "adv.", "uz": "hozirgina, bir oz avval",             "ru": "только что, только сейчас",      "tj": "ҳозир, як лаҳза пеш"},
        {"no": 6,  "zh": "帮忙",  "pinyin": "bāngmáng", "pos": "v.",   "uz": "yordam bermoq",                      "ru": "помогать, оказывать помощь",     "tj": "кӯмак кардан"},
        {"no": 7,  "zh": "特别",  "pinyin": "tèbié",    "pos": "adv./adj.", "uz": "ayniqsa; alohida, maxsus",       "ru": "особенно; особый",               "tj": "бахусус; хос, махсус"},
        {"no": 8,  "zh": "明白",  "pinyin": "míngbái",  "pos": "v./adj.", "uz": "tushunmoq; tushungan, aniq",      "ru": "понимать; понятный, ясный",      "tj": "фаҳмидан; фаҳмо, равшан"},
        {"no": 9,  "zh": "锻炼",  "pinyin": "duànliàn", "pos": "v.",   "uz": "sport mashq qilmoq",                 "ru": "тренироваться",                  "tj": "машқ кардан, варзиш кардан"},
        {"no": 10, "zh": "音乐",  "pinyin": "yīnyuè",   "pos": "n.",   "uz": "musiqa",                             "ru": "музыка",                         "tj": "мусиқа"},
        {"no": 11, "zh": "公园",  "pinyin": "gōngyuán", "pos": "n.",   "uz": "park, bog'",                         "ru": "парк",                           "tj": "боғ, парк"},
        {"no": 12, "zh": "聊天",  "pinyin": "liáotiān", "pos": "v.",   "uz": "suhbatlashmoq, gaplashmoq",          "ru": "болтать, разговаривать",         "tj": "гуфтугӯ кардан, суҳбат кардан"},
        {"no": 13, "zh": "更",    "pinyin": "gèng",     "pos": "adv.", "uz": "yanada, bundan ham ko'proq",          "ru": "ещё более, ещё больше",          "tj": "боз ҳам, бештар аз пеш"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Uyda ko'zoynak qidirayotganda", "scene_ru": "Поиск очков дома", "scene_tj": "Ҷустуҷӯи айнак дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "我的眼镜呢？刚才还在桌子上，怎么突然找不到了？", "pinyin": "Wǒ de yǎnjìng ne? Gāngcái hái zài zhuōzi shàng, zěnme tūrán zhǎo bu dào le?", "uz": "Ko'zoynagim qani? Hozirgina stol ustida edi, qanday qilib to'satdan topib bo'lmay qoldi?", "ru": "Где мои очки? Только что были на столе — как вдруг не могу найти?", "tj": "Айнакам куҷост? Як лаҳза пеш рӯйи миз буд, чӣ тавр ногаҳон ёфта намешавад?"},
                {"speaker": "B", "zh": "我帮你找。你刚才在哪儿坐的？", "pinyin": "Wǒ bāng nǐ zhǎo. Nǐ gāngcái zài nǎr zuò de?", "uz": "Senga yordam beraman. Sen hozirgina qayerda o'tirganding?", "ru": "Я помогу тебе найти. Где ты только что сидел?", "tj": "Ман ёрӣ мерасонам. Як лаҳза пеш дар куҷо нишаста будед?"},
                {"speaker": "A", "zh": "我刚才在沙发上坐着看书。", "pinyin": "Wǒ gāngcái zài shāfā shàng zuò zhe kànshū.", "uz": "Men hozirgina divanда o'tirib kitob o'qiyotgan edim.", "ru": "Только что сидел на диване и читал книгу.", "tj": "Ман як лаҳза пеш рӯйи диван нишаста китоб мехондам."},
                {"speaker": "B", "zh": "找到了！眼镜在沙发底下呢，你看得清楚吗？", "pinyin": "Zhǎo dào le! Yǎnjìng zài shāfā dǐxia ne, nǐ kàn de qīngchǔ ma?", "uz": "Topdim! Ko'zoynak divan ostida ekan, aniq ko'ra olayapsizmi?", "ru": "Нашёл! Очки под диваном — ты видишь нормально?", "tj": "Ёфтам! Айнак зери диван аст, оё равшан мебинед?"},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Idorada hujjat qidirayotganda", "scene_ru": "Поиск документа в офисе", "scene_tj": "Ҷустуҷӯи ҳуҷҷат дар идора",
            "dialogue": [
                {"speaker": "A", "zh": "你看见我的报告了吗？我刚才放在这里的。", "pinyin": "Nǐ kànjian wǒ de bàogào le ma? Wǒ gāngcái fàng zài zhèlǐ de.", "uz": "Mening hisobotimni ko'rdingizmi? Men hozirgina shu yerga qo'ygan edim.", "ru": "Ты видел мой доклад? Только что положил его здесь.", "tj": "Ҳисоботи маро дидед? Ман он лаҳза ин ҷо гузошта будам."},
                {"speaker": "B", "zh": "经理刚拿走了一个文件，会不会是你的？", "pinyin": "Jīnglǐ gāng ná zǒu le yī ge wénjiàn, huì bu huì shì nǐ de?", "uz": "Menejer hozirgina bir hujjat olib ketdi, siznikimas?", "ru": "Менеджер только что унёс один документ — не твой ли это?", "tj": "Мудир ҳозир як ҳуҷҷат бурд, оё ин ҳуҷҷати шумо нест?"},
                {"speaker": "A", "zh": "不清楚，我去问一下，能帮我找一下吗？", "pinyin": "Bù qīngchǔ, wǒ qù wèn yīxià, néng bāng wǒ zhǎo yīxià ma?", "uz": "Aniq emas, men borib so'rayman, bir qidirib berolaysizmi?", "ru": "Непонятно, я пойду спрошу — можете помочь поискать?", "tj": "Аниқ нест, ман рафта мепурсам, оё метавонед ёрӣ расонед?"},
                {"speaker": "B", "zh": "当然，我帮你找。别着急，肯定找得到！", "pinyin": "Dāngrán, wǒ bāng nǐ zhǎo. Bié zháojí, kěndìng zhǎo de dào!", "uz": "Albatta, yordam beraman. Tashvishlanmang, albatta topiladi!", "ru": "Конечно, помогу найти. Не переживай — обязательно найдётся!", "tj": "Албатта ёрӣ мерасонам. Ташвиш накашед, ҳатман ёфта мешавад!"},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Parkda uchrashuv", "scene_ru": "Встреча в парке", "scene_tj": "Вохӯрӣ дар боғ",
            "dialogue": [
                {"speaker": "A", "zh": "你在公园里找什么？", "pinyin": "Nǐ zài gōngyuán lǐ zhǎo shénme?", "uz": "Parkda nima qidirayapsiz?", "ru": "Что ты ищешь в парке?", "tj": "Дар боғ чӣ меҷӯед?"},
                {"speaker": "B", "zh": "我的钥匙突然找不到了！刚才还在口袋里的。", "pinyin": "Wǒ de yàoshi tūrán zhǎo bu dào le! Gāngcái hái zài kǒudài lǐ de.", "uz": "Kalitim to'satdan yo'qolib qoldi! Hozirgina cho'ntakda edi.", "ru": "Мои ключи вдруг исчезли! Только что были в кармане.", "tj": "Калидам ногаҳон гум шуд! Як лаҳза пеш дар ҷайб буд."},
                {"speaker": "A", "zh": "你刚才在这里聊天了吗？也许在长椅上。", "pinyin": "Nǐ gāngcái zài zhèlǐ liáotiān le ma? Yěxǔ zài cháng yǐ shàng.", "uz": "Hozirgina bu yerda gaplashayotgan edingizmi? Ehtimol uzun o'rindiqda.", "ru": "Только что разговаривал здесь? Может быть, на скамейке.", "tj": "Як лаҳза пеш инҷо суҳбат мекардед? Шояд рӯйи нимкат."},
                {"speaker": "B", "zh": "找到了！在长椅底下。太感谢你了，更感谢你帮忙！", "pinyin": "Zhǎo dào le! Zài cháng yǐ dǐxia. Tài gǎnxiè nǐ le, gèng gǎnxiè nǐ bāngmáng!", "uz": "Topdim! Uzun o'rindiq ostida ekan. Juda rahmat, yordam berganing uchun bundan ham ko'proq rahmat!", "ru": "Нашёл! Под скамейкой. Большое спасибо — и ещё больше за помощь!", "tj": "Ёфтам! Зери нимкат аст. Хеле раҳмат, боз ҳам зиёдтар раҳмат барои кӯмак!"},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Xiyobonda musiqa eshitayotganda", "scene_ru": "На бульваре во время прослушивания музыки", "scene_tj": "Дар хиёбон ҳангоми гӯш кардани мусиқа",
            "dialogue": [
                {"speaker": "A", "zh": "你一边听音乐一边锻炼，特别厉害！", "pinyin": "Nǐ yībiān tīng yīnyuè yībiān duànliàn, tèbié lìhai!", "uz": "Musiqa tinglab ham mashq qilayapsiz, juda zo'rsiz!", "ru": "Ты и музыку слушаешь, и тренируешься — молодец!", "tj": "Шумо ҳам мусиқа мегӯшед ҳам машқ мекунед, хеле зӯр!"},
                {"speaker": "B", "zh": "我觉得听音乐能让人更放松，锻炼效果更好！", "pinyin": "Wǒ juéde tīng yīnyuè néng ràng rén gèng fàngsōng, duànliàn xiàoguǒ gèng hǎo!", "uz": "Musiqa eshitish odamni yanada tinchitadi deb o'ylayman, mashqning samarasi bundan ham yaxshi bo'ladi!", "ru": "Я считаю, что музыка помогает расслабиться, и эффект от тренировки ещё лучше!", "tj": "Ман фикр мекунам, ки мусиқа ба одам боз ҳам осоишро медиҳад, натиҷаи машқ боз ҳам беҳтар мешавад!"},
                {"speaker": "A", "zh": "你离开公园后，去哪儿呢？", "pinyin": "Nǐ líkāi gōngyuán hòu, qù nǎr ne?", "uz": "Parkdan ketganingizdan keyin qayerga bormoqchisiz?", "ru": "Куда ты пойдёшь после того, как уйдёшь из парка?", "tj": "Пас аз тарки боғ ба куҷо мераввед?"},
                {"speaker": "B", "zh": "我刚才看到咖啡馆，想去那里聊聊天，你明白我的意思吗？", "pinyin": "Wǒ gāngcái kàndào kāfēiguǎn, xiǎng qù nàlǐ liáoliao tiān, nǐ míngbái wǒ de yìsi ma?", "uz": "Men hozirgina qahvaxona ko'rdim, u yerga borib bir oz gaplashmoqchiman, mening niyatimni tushunyapsizmi?", "ru": "Только что заметил кафе — хочу зайти поболтать, понимаешь, что я имею в виду?", "tj": "Ман як лаҳза пеш қаҳвахона дидам, мехоҳам он ҷо рафта каме суҳбат кунам, оё мақсадамро мефаҳмед?"},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "可能补语：V得/不+结果补语",
            "title_uz": "Mumkinlik to'ldiruvchisi: V得/不+natija",
            "title_ru": "Потенциальное дополнение: V得/不+результат",
            "title_tj": "Иловаи потенсиалӣ: V得/不+натиҷа",
            "rule_uz": (
                "Bu qolip biror harakatni bajarish mumkin yoki mumkin emasligini bildiradi.\n"
                "Ijobiy: V + 得 + Natija (qila olaman)\n"
                "Inkor: V + 不 + Natija (qila olmayman)\n"
                "Masalan:\n"
                "  找得到 (topib olsa bo'ladi) / 找不到 (topib bo'lmaydi)\n"
                "  听得懂 (tushunib olsa bo'ladi) / 听不懂 (tushunib bo'lmaydi)\n"
                "  看得清楚 (aniq ko'ra oladi) / 看不清楚 (aniq ko'ra olmaydi)"
            ),
            "rule_ru": (
                "Эта конструкция выражает возможность или невозможность совершить действие.\n"
                "Утверждение: V + 得 + Результат (можно сделать)\n"
                "Отрицание: V + 不 + Результат (нельзя сделать)\n"
                "Например:\n"
                "  找得到 (можно найти) / 找不到 (нельзя найти)\n"
                "  听得懂 (можно понять) / 听不懂 (нельзя понять)\n"
                "  看得清楚 (можно разглядеть) / 看不清楚 (нельзя разглядеть)"
            ),
            "rule_tj": (
                "Ин сохтор имкониятро ё набудани имконияти иҷрои амалро ифода мекунад.\n"
                "Тасдиқ: V + 得 + Натиҷа (метавон кард)\n"
                "Инкор: V + 不 + Натиҷа (наметавон кард)\n"
                "Масалан:\n"
                "  找得到 (ёфта мешавад) / 找不到 (ёфта намешавад)\n"
                "  听得懂 (фаҳмида мешавад) / 听不懂 (фаҳмида намешавад)\n"
                "  看得清楚 (равшан дида мешавад) / 看不清楚 (равшан дида намешавад)"
            ),
            "examples": [
                {"zh": "眼镜找不到了，你帮我找得到吗？", "pinyin": "Yǎnjìng zhǎo bu dào le, nǐ bāng wǒ zhǎo de dào ma?", "uz": "Ko'zoynak topilmayapti, siz topib bera olasizmi?", "ru": "Очки не нахожу — ты можешь помочь найти?", "tj": "Айнак ёфта намешавад, оё шумо ёрӣ расонда ёфта метавонед?"},
                {"zh": "他说话太快，我听不懂。", "pinyin": "Tā shuōhuà tài kuài, wǒ tīng bu dǒng.", "uz": "U juda tez gapiradi, men tushunolmayman.", "ru": "Он говорит слишком быстро — я не понимаю.", "tj": "Вай хеле тез гап мезанад, ман фаҳмида наметавонам."},
            ]
        },
        {
            "no": 2,
            "title_zh": "\"N+呢？\"询问处所",
            "title_uz": "'N+呢？' — joylashuvni so'rash",
            "title_ru": "«N+呢？» — вопрос о местонахождении",
            "title_tj": "«N+呢？» — пурсидани ҷой",
            "rule_uz": (
                "'N+呢？' — juda qisqa so'roq qolipи. Biror narsa yoki odamning qayerda ekanligini so'raydi.\n"
                "Ma'nosi: '...qani? ...qayerda?'\n"
                "Masalan:\n"
                "  你的眼镜呢？(Ko'zoynaging qani?)\n"
                "  他呢？(U qani?)\n"
                "  书呢？(Kitob qani?)\n"
                "Suhbat kontekstida yaxshi ma'lum narsaning joylashuvini so'raganda ishlatiladi."
            ),
            "rule_ru": (
                "'N+呢？' — очень краткая вопросительная конструкция, спрашивает о местонахождении.\n"
                "Значение: 'а...? где...?'\n"
                "Например:\n"
                "  你的眼镜呢？(А твои очки?)\n"
                "  他呢？(А где он?)\n"
                "  书呢？(А книга где?)\n"
                "Используется, когда местонахождение уже известного предмета неизвестно."
            ),
            "rule_tj": (
                "'N+呢？' — сохтори саволии хеле кӯтоҳ, дар бораи ҷой мепурсад.\n"
                "Маъно: '...куҷост? ...чист?'\n"
                "Масалан:\n"
                "  你的眼镜呢？(Айнакат куҷост?)\n"
                "  他呢？(Вай куҷост?)\n"
                "  书呢？(Китоб куҷост?)\n"
                "Вақте истифода мешавад, ки ҷои чизи аллакай маълум номаълум аст."
            ),
            "examples": [
                {"zh": "我的眼镜呢？刚才还在桌子上。", "pinyin": "Wǒ de yǎnjìng ne? Gāngcái hái zài zhuōzi shàng.", "uz": "Ko'zoynagim qani? Hozirgina stol ustida edi.", "ru": "Где мои очки? Только что были на столе.", "tj": "Айнакам куҷост? Як лаҳза пеш рӯйи миз буд."},
                {"zh": "经理呢？我有事找他。", "pinyin": "Jīnglǐ ne? Wǒ yǒu shì zhǎo tā.", "uz": "Menejer qani? Unga ishim bor edi.", "ru": "А где менеджер? Мне нужно с ним поговорить.", "tj": "Мудир куҷост? Ман бо вай кор дорам."},
            ]
        },
        {
            "no": 3,
            "title_zh": "\"刚\"和\"刚才\"的比较",
            "title_uz": "'刚' va '刚才' farqi",
            "title_ru": "Сравнение 刚 и 刚才",
            "title_tj": "Муқоисаи 刚 ва 刚才",
            "rule_uz": (
                "Ikkalasi ham 'hozirgina, bir oz avval' ma'nosida, lekin farqli:\n"
                "刚才 — payt so'zi (time word): gap boshida yoki mavzu sifatida turadi\n"
                "       Masalan: 刚才他在这里。(U hozirgina bu yerda edi.)\n"
                "刚 — ravish: fe'l oldidan keladi va to'g'ridan-to'g'ri harakatni ta'riflaydi\n"
                "     Masalan: 他刚到。(U hozirgina keldi.)\n"
                "              经理刚拿走了文件。(Menejer hozirgina hujjatni olib ketdi.)"
            ),
            "rule_ru": (
                "Оба означают 'только что', но различаются по употреблению:\n"
                "刚才 — слово времени: стоит в начале предложения или как подлежащее темы\n"
                "       Например: 刚才他在这里。(Только что он был здесь.)\n"
                "刚 — наречие: стоит перед глаголом, описывает действие напрямую\n"
                "     Например: 他刚到。(Он только что пришёл.)\n"
                "              经理刚拿走了文件。(Менеджер только что унёс документ.)"
            ),
            "rule_tj": (
                "Ҳарду маънои 'як лаҳза пеш, ҳозир' доранд, аммо фарқ мекунанд:\n"
                "刚才 — калимаи вақт: дар аввали ҷумла ё ҳамчун мавзӯ меояд\n"
                "       Масалан: 刚才他在这里。(Як лаҳза пеш вай инҷо буд.)\n"
                "刚 — қайд: пеш аз феъл меояд ва амалро бевосита тасвир мекунад\n"
                "     Масалан: 他刚到。(Вай ҳозир расид.)\n"
                "              经理刚拿走了文件。(Мудир ҳозир ҳуҷҷатро бурд.)"
            ),
            "examples": [
                {"zh": "经理刚拿走了一个文件，会不会是你的？", "pinyin": "Jīnglǐ gāng ná zǒu le yī ge wénjiàn, huì bu huì shì nǐ de?", "uz": "Menejer hozirgina bir hujjat olib ketdi, siznikimas?", "ru": "Менеджер только что унёс документ — не твой ли?", "tj": "Мудир ҳозир як ҳуҷҷат бурд, оё ин ҳуҷҷати шумо нест?"},
                {"zh": "刚才他还在这里，怎么突然不见了？", "pinyin": "Gāngcái tā hái zài zhèlǐ, zěnme tūrán bú jiàn le?", "uz": "U hozirgina shu yerda edi, qanday qilib to'satdan ko'rinmay qoldi?", "ru": "Только что он был здесь — как вдруг исчез?", "tj": "Як лаҳза пеш вай инҷо буд, чӣ тавр ногаҳон нопадид шуд?"},
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
                {"prompt_uz": "ko'zoynak", "prompt_ru": "очки", "prompt_tj": "айнак", "answer": "眼镜", "pinyin": "yǎnjìng"},
                {"prompt_uz": "to'satdan, birdaniga", "prompt_ru": "вдруг, внезапно", "prompt_tj": "якбора, ногаҳон", "answer": "突然", "pinyin": "tūrán"},
                {"prompt_uz": "aniq, ravshan, tushinarli", "prompt_ru": "ясный, понятный", "prompt_tj": "равшан, аниқ", "answer": "清楚", "pinyin": "qīngchǔ"},
                {"prompt_uz": "hozirgina, bir oz avval", "prompt_ru": "только что", "prompt_tj": "ҳозир, як лаҳза пеш", "answer": "刚才", "pinyin": "gāngcái"},
                {"prompt_uz": "tushunmoq; tushungan", "prompt_ru": "понимать; понятный", "prompt_tj": "фаҳмидан; фаҳмо", "answer": "明白", "pinyin": "míngbái"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (找不到、刚才、呢、刚):",
            "instruction_ru": "Вставьте подходящее слово (找不到、刚才、呢、刚):",
            "instruction_tj": "Калимаи мувофиқро дар ҷойи холӣ нависед (找不到、刚才、呢、刚):",
            "items": [
                {"prompt_uz": "我的眼镜突然______了。", "prompt_ru": "Мои очки вдруг ______.", "prompt_tj": "Айнакам ногаҳон ______шуд.", "answer": "找不到", "pinyin": "zhǎo bu dào"},
                {"prompt_uz": "你的书______？在桌子上吗？", "prompt_ru": "А твоя книга ______? На столе?", "prompt_tj": "Китобат ______? Рӯйи миз аст?", "answer": "呢", "pinyin": "ne"},
                {"prompt_uz": "经理______拿走了文件，马上回来。", "prompt_ru": "Менеджер ______унёс документ, скоро вернётся.", "prompt_tj": "Мудир ______ҳуҷҷатро бурд, зуд бармегардад.", "answer": "刚", "pinyin": "gāng"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "我的眼镜呢？刚才还在桌子上，怎么突然找不到了？", "prompt_ru": "我的眼镜呢？刚才还在桌子上，怎么突然找不到了？", "prompt_tj": "我的眼镜呢？刚才还在桌子上，怎么突然找不到了？", "answer": "Ko'zoynagim qani? Hozirgina stol ustida edi, qanday qilib to'satdan topib bo'lmay qoldi?", "pinyin": "Wǒ de yǎnjìng ne? Gāngcái hái zài zhuōzi shàng, zěnme tūrán zhǎo bu dào le?"},
                {"prompt_uz": "找到了！眼镜在沙发底下呢。", "prompt_ru": "找到了！眼镜在沙发底下呢。", "prompt_tj": "找到了！眼镜在沙发底下呢。", "answer": "Topdim! Ko'zoynak divan ostida ekan.", "pinyin": "Zhǎo dào le! Yǎnjìng zài shāfā dǐxia ne."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["眼镜", "突然", "清楚", "刚才", "明白"]},
        {"no": 2, "answers": ["找不到", "呢", "刚"]},
        {"no": 3, "answers": [
            "Ko'zoynagim qani? Hozirgina stol ustida edi, qanday qilib to'satdan topib bo'lmay qoldi?",
            "Topdim! Ko'zoynak divan ostida ekan.",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Mumkinlik to'ldiruvchisi V得/不 ishlatib 4 ta gap tuzing. Kundalik hayotdan misollar keltiring.",
            "instruction_ru": "Составьте 4 предложения с потенциальным дополнением V得/不. Приведите примеры из повседневной жизни.",
            "instruction_tj": "Бо иловаи потенсиалии V得/不 4 ҷумла тартиб диҳед. Аз ҳаёти рӯзмарра мисол овардед.",
            "words": ["找得到/找不到", "听得懂/听不懂", "看得清楚/看不清楚", "做得完/做不完"],
            "topic_uz": "Nima qila olaman, nima qila olmayman",
            "topic_ru": "Что я могу и не могу сделать",
            "topic_tj": "Чӣ карда метавонам ва чӣ карда наметавонам",
        },
        {
            "no": 2,
            "instruction_uz": "Uyingizda biror narsani yo'qotib qo'yganingiz haqida 5-6 gapdan iborat matn yozing. 刚才, 找不到, 突然 so'zlarini ishlating.",
            "instruction_ru": "Напишите 5–6 предложений о том, как вы потеряли что-то дома. Используйте слова 刚才, 找不到, 突然.",
            "instruction_tj": "Дар бораи он ки дар хона чизеро гум кардед 5-6 ҷумла нависед. Калимаҳои 刚才, 找不到, 突然-ро истифода баред.",
            "topic_uz": "Men biror narsani yo'qotdim",
            "topic_ru": "Я потерял что-то",
            "topic_tj": "Ман чизеро гум кардам",
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
