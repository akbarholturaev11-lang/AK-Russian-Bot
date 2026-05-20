import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 6,
    "lesson_code": "HSK4-L06",
    "title": "一分钱一分货",
    "goal": json.dumps({"uz": "narx va sifat munosabati, bozorda savdo haqida gapirish; 竟然, 倍, 值得, 其中, (在)...下 grammatik qoliplarini o'zlashtirish", "ru": "говорить о соотношении цены и качества, торговле; освоить конструкции 竟然, 倍, 值得, 其中, (在)...下", "tj": "гуфтугӯ дар бораи нисбати нарх ва сифат, тиҷорат; аз худ кардани қолипҳои 竟然, 倍, 值得, 其中, (在)...下"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Narx sifatga mos' mavzusiga bag'ishlangan. Unda do'konda narx savdolashish, mahsulot sifatini baholash va iste'molchi huquqlari haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 竟然, 倍, 值得, 其中, （在）...下.", "ru": "Этот урок посвящён теме 'Цена соответствует качеству'. В нём вы научитесь говорить о торге в магазине, оценке качества товара и правах потребителя. Основные грамматические конструкции: 竟然, 倍, 值得, 其中, （在）...下.", "tj": "Ин дарс ба мавзӯи 'Нарх ба сифат мувофиқ аст' бахшида шудааст. Дар он чонезанӣ дар дӯкон, арзёбии сифати мол ва ҳуқуқи истеъмолкунанда омӯхта мешавад. Қолипҳои асосии грамматикӣ: 竟然, 倍, 值得, 其中, （在）...下."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "果汁", "pinyin": "guǒzhī", "pos": "n.", "uz": "meva sharbati", "ru": "фруктовый сок", "tj": "шарбати мева"},
            {"no": 2, "zh": "售货员", "pinyin": "shòuhuòyuán", "pos": "n.", "uz": "sotuvchi, do'kon xodimi", "ru": "продавец, работник магазина", "tj": "фурӯшанда, корманди дӯкон"},
            {"no": 3, "zh": "袜子", "pinyin": "wàzi", "pos": "n.", "uz": "paypoq", "ru": "носки", "tj": "ҷӯроб"},
            {"no": 4, "zh": "打扰", "pinyin": "dǎrǎo", "pos": "v.", "uz": "bezovta qilmoq, halaqit bermoq", "ru": "беспокоить, мешать", "tj": "безовтор кардан, халал додан"},
            {"no": 5, "zh": "竟然", "pinyin": "jìngrán", "pos": "adv.", "uz": "kutilmaganda, ajablanish bilan", "ru": "неожиданно, к удивлению", "tj": "ногаҳон, бо ҳайрат"},
            {"no": 6, "zh": "西红柿", "pinyin": "xīhóngshì", "pos": "n.", "uz": "pomidor", "ru": "помидор, томат", "tj": "помидор"},
            {"no": 7, "zh": "百分之", "pinyin": "bǎi fēn zhī", "pos": "phrase", "uz": "foiz", "ru": "процент", "tj": "фоиз"},
            {"no": 8, "zh": "倍", "pinyin": "bèi", "pos": "m.", "uz": "marta, barobar (ko'paytma)", "ru": "раз, кратно (умножение)", "tj": "баробар, маротиба (зиёдшавӣ)"},
            {"no": 9, "zh": "皮肤", "pinyin": "pífū", "pos": "n.", "uz": "teri, tana terisi", "ru": "кожа, кожный покров", "tj": "пӯст"},
            {"no": 10, "zh": "好处", "pinyin": "hǎochu", "pos": "n.", "uz": "foyda, manfaat", "ru": "польза, выгода", "tj": "фоида, манфиат"},
            {"no": 11, "zh": "尝", "pinyin": "cháng", "pos": "v.", "uz": "tatib ko'rmoq, sinab ko'rmoq", "ru": "пробовать на вкус", "tj": "чашидан, санҷидан"},
            {"no": 12, "zh": "值得", "pinyin": "zhíde", "pos": "v.", "uz": "arziydi, qimmatga arziydi", "ru": "стоит того, заслуживает", "tj": "меарзад, сазовор аст"},
            {"no": 13, "zh": "其中", "pinyin": "qízhōng", "pos": "pron.", "uz": "ularning ichida, shular orasida", "ru": "среди них, в том числе", "tj": "дар байни онҳо, аз ҷумлаи онҳо"},
            {"no": 14, "zh": "活动", "pinyin": "huódòng", "pos": "n./v.", "uz": "tadbir, aksiya; harakatlanmoq", "ru": "мероприятие, акция; двигаться", "tj": "тадбир, акция; ҳаракат кардан"},
            {"no": 15, "zh": "免费", "pinyin": "miǎnfèi", "pos": "v./adj.", "uz": "bepul bermoq; bepul", "ru": "давать бесплатно; бесплатный", "tj": "бепул додан; бепул"},
            {"no": 16, "zh": "修理", "pinyin": "xiūlǐ", "pos": "v.", "uz": "ta'mirlash, tuzatish", "ru": "ремонтировать, чинить", "tj": "таъмир кардан, ислоҳ кардан"},
            {"no": 17, "zh": "退换", "pinyin": "tuìhuàn", "pos": "v.", "uz": "qaytarib almashmoq", "ru": "возвращать и обменивать", "tj": "баргардондан ва иваз кардан"},
            {"no": 18, "zh": "便宜", "pinyin": "piányí", "pos": "adj.", "uz": "arzon", "ru": "дешёвый", "tj": "арзон"},
            {"no": 19, "zh": "贵", "pinyin": "guì", "pos": "adj.", "uz": "qimmat, baholi", "ru": "дорогой, дорогостоящий", "tj": "гарон, қиматбаҳо"},
            {"no": 20, "zh": "比较", "pinyin": "bǐjiào", "pos": "adv.", "uz": "nisbatan, ancha", "ru": "относительно, довольно", "tj": "нисбатан, кам-кам"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "张远 va 李谦 supermarketga borish haqida gaplashadi",
                "scene_ru": "张远 и 李谦 обсуждают поход в супермаркет",
                "scene_tj": "张远 ва 李谦 дар бораи рафтан ба супермаркет гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "张远", "zh": "昨天晚上我找给你打电话一直没人接，你在做什么呢？", "pinyin": "",
                     "uz": "Kecha kechqurun senga qo'ng'iroq qildim, hech kim ko'tarmadi, nima qilyapding?",
                     "ru": "Вчера вечером я несколько раз звонил тебе, никто не брал трубку — что ты делал?",
                     "tj": "Дирӯз шаб ба ту занг задам, ҳеч кас гӯширо бар намедошт — ту чӣ кор мекардӣ?"},
                    {"speaker": "李谦", "zh": "我妻子让我陪她去超市买果汁，我把手机忘在家里了。", "pinyin": "",
                     "uz": "Xotinim meni supermarketda meva sharbati sotib olishga olib borgandi, telefonimy uyda qolgan edi.",
                     "ru": "Жена попросила меня сходить с ней в супермаркет за фруктовым соком, я забыл телефон дома.",
                     "tj": "Ҳамсарам аз ман хост, ки бо вай ба супермаркет барои харидани шарбати мева равам, телефонамро дар хона фаромӯш кардам."},
                    {"speaker": "张远", "zh": "那里从来不让我们进去，售货员说那地方我们偌大，拿了一条领带、两双袜子，然后我们就高高兴兴地回来了。", "pinyin": "",
                     "uz": "Avval u yerga kirishimizga ruxsat bermadilar, sotuvchi aytdiki... Keyin bir bo'yin bog'ich va ikki juft paypoq oldik, so'ng xursandchilik bilan qaytdik.",
                     "ru": "Сначала нас туда не пускали, продавец сказал... Потом мы взяли один галстук и две пары носков и радостно вернулись.",
                     "tj": "Аввал ба мо иҷозат надоданд, ки дохил шавем, фурӯшанда гуфт... Сипас як галстук ва ду ҷуфт ҷӯроб гирифтем ва шодмона баргаштем."},
                    {"speaker": "李谦", "zh": "买东西时我自己选、自己买，自己决定，从来不希望别人帮我选。", "pinyin": "",
                     "uz": "Men o'zim tanlayman, o'zim sotib olaman, o'zim qaror qilaman, hech qachon boshqaning yordam berishini xohlamayman.",
                     "ru": "При покупках я сам выбираю, сам покупаю, сам решаю — никогда не хочу, чтобы кто-то помогал мне выбирать.",
                     "tj": "Ҳангоми харид худам интихоб мекунам, худам мехарам, худам қарор мегирам — ҳеч вақт намехоҳам, ки кас ба ман дар интихоб кӯмак кунад."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "王静 do'konda pomidor sotib oladi",
                "scene_ru": "王静 покупает помидоры в магазине",
                "scene_tj": "王静 дар дӯкон помидор мехарад",
                "dialogue": [
                    {"speaker": "王静", "zh": "西红柿新鲜吗？怎么卖？", "pinyin": "",
                     "uz": "Pomidor yangi chiqibdimi? Qancha turadi?",
                     "ru": "Помидоры свежие? Почём продаёте?",
                     "tj": "Помидор тозаст? Чанд пул аст?"},
                    {"speaker": "售货员", "zh": "七块钱一斤，您放心，保证百分之百新鲜。", "pinyin": "",
                     "uz": "Bir jin etti yuan, xotirjam bo'ling, yuz foiz yangi.",
                     "ru": "Семь юаней за цзинь, не беспокойтесь — гарантированно сто процентов свежие.",
                     "tj": "Ҳафт юань барои як ҷин, хотирҷамъ бошед — сад дар сади тоза."},
                    {"speaker": "王静", "zh": "怎么这么贵呀！我昨天天在另一个超市，才五块五，今天的价格是昨天的两倍！", "pinyin": "",
                     "uz": "Bu qadar qimmatmi! Men kecha boshqa supermarketda besh yuan besh fen topgan edim, bugungi narx kechagidan ikki barobar qimmat!",
                     "ru": "Как так дорого! Вчера в другом супермаркете было всего пять с половиной юаней — сегодняшняя цена вдвое больше вчерашней!",
                     "tj": "Ин қадар гарон! Дирӯз дар супермаркети дигар панҷ юаню ним буд — нархи имрӯз аз нархи дирӯз ду баробар зиёд аст!"},
                    {"speaker": "售货员", "zh": "您看我们的西红柿是'绿色'的，一分钱一分货，每天吃两个这种特别的西红柿，对皮肤好处很多。", "pinyin": "",
                     "uz": "Ko'ring, bizning pomidorimiz 'ekologik' toza, narx sifatga mos, har kuni bunday maxsus pomidordan ikkita yesangiz, teringizga juda foydali.",
                     "ru": "Посмотрите — наши помидоры 'экологически чистые', цена соответствует качеству. Если есть каждый день по два таких особых помидора, для кожи очень полезно.",
                     "tj": "Нигаред — помидори мо 'экологӣ' тоза аст, нарх ба сифат мувофиқ аст. Агар ҳар рӯз аз ин помидорҳои махсус ду адад хӯред, барои пӯст хеле муфид аст."},
                    {"speaker": "王静", "zh": "好，那我先买先尝尝。", "pinyin": "",
                     "uz": "Yaxshi, unda avval sotib olib tatib ko'raman.",
                     "ru": "Хорошо, тогда сначала куплю и попробую.",
                     "tj": "Хуб, пас аввал харида мечашам."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "竟然",
                "title_uz": "kutilmaganda, ajablanib",
                "title_ru": "неожиданно, к удивлению",
                "title_tj": "ногаҳон, бо ҳайрат",
                "rule_uz": "'Kutilmaganda, ajablanib' ma'nosini beradi. Kutilmagan yoki hayratlanarli hodisani ifodalaydi.",
                "rule_ru": "Означает 'неожиданно, к удивлению'. Выражает неожиданное или удивительное событие.",
                "rule_tj": "Маънои 'ногаҳон, бо ҳайрат' дорад. Рӯйдоди ногаҳонӣ ё шигифтовареро ифода мекунад.",
                "examples": [
                    {"zh": "他竟然一个人吃了两个西瓜！", "pinyin": "",
                     "uz": "U kutilmaganda bir o'zi ikkita tarvuz yedi!",
                     "ru": "Он неожиданно съел два арбуза в одиночку!",
                     "tj": "Ӯ ногаҳон танҳо ду тарбуз хӯрд!"},
                    {"zh": "这道题竟然这么简单。", "pinyin": "",
                     "uz": "Bu masala hayratlanarli darajada oddiy ekan.",
                     "ru": "Эта задача оказалась неожиданно простой.",
                     "tj": "Ин масъала ногаҳон ин қадар осон буд."},
                ],
            },
            {
                "no": 2,
                "title_zh": "倍",
                "title_uz": "marta, barobar",
                "title_ru": "раз, кратно",
                "title_tj": "маротиба, баробар",
                "rule_uz": "'Marta, barobar' ma'nosini beradi. Miqdorning necha marta ko'payganini bildiradi.",
                "rule_ru": "Означает 'раз, кратно'. Указывает, во сколько раз увеличилось количество.",
                "rule_tj": "Маънои 'маротиба, баробар' дорад. Нишон медиҳад, ки миқдор чанд маротиба зиёд шуд.",
                "examples": [
                    {"zh": "今天的价格是昨天的两倍。", "pinyin": "",
                     "uz": "Bugungi narx kechagidan ikki barobar.",
                     "ru": "Сегодняшняя цена вдвое больше вчерашней.",
                     "tj": "Нархи имрӯз аз нархи дирӯз ду баробар зиёд аст."},
                    {"zh": "我的速度是他的三倍。", "pinyin": "",
                     "uz": "Mening tezligim undan uch barobar ko'p.",
                     "ru": "Моя скорость втрое больше его.",
                     "tj": "Суръати ман аз суръати ӯ се баробар зиёд аст."},
                ],
            },
            {
                "no": 3,
                "title_zh": "值得",
                "title_uz": "arziydi, qimmatga arziydi",
                "title_ru": "стоит того, заслуживает",
                "title_tj": "меарзад, сазовор аст",
                "rule_uz": "'Arziydi, qimmatga arziydi' ma'nosini beradi. Biror narsa qilinishga arzirligini bildiradi.",
                "rule_ru": "Означает 'стоит того, заслуживает'. Указывает, что что-то достойно того, чтобы это сделать.",
                "rule_tj": "Маънои 'меарзад, сазовор аст' дорад. Нишон медиҳад, ки чизе сазовори анҷом додан аст.",
                "examples": [
                    {"zh": "这本书值得一读。", "pinyin": "",
                     "uz": "Bu kitob o'qishga arziydi.",
                     "ru": "Эта книга стоит того, чтобы её прочитать.",
                     "tj": "Ин китоб хондан меарзад."},
                    {"zh": "健康是最值得投资的事情。", "pinyin": "",
                     "uz": "Sog'liq — investitsiyaga eng ko'p arzigulik narsa.",
                     "ru": "Здоровье — это то, во что больше всего стоит вкладываться.",
                     "tj": "Саломатӣ — чизест, ки сармоягузорӣ дар он аз ҳама зиёдтар меарзад."},
                ],
            },
            {
                "no": 4,
                "title_zh": "其中",
                "title_uz": "ularning ichida, shular orasida",
                "title_ru": "среди них, в том числе",
                "title_tj": "дар байни онҳо, аз ҷумлаи онҳо",
                "rule_uz": "'Ularning ichida, shular orasida' ma'nosini beradi. Bir guruh ichidan ma'lum bir qismni ajratadi.",
                "rule_ru": "Означает 'среди них, в том числе'. Выделяет определённую часть из группы.",
                "rule_tj": "Маънои 'дар байни онҳо, аз ҷумлаи онҳо' дорад. Қисми муайяни гурӯҳро ҷудо мекунад.",
                "examples": [
                    {"zh": "他买了很多水果，其中有苹果和西红柿。", "pinyin": "",
                     "uz": "U ko'p meva-sabzavot sotib oldi, ular orasida olma va pomidor bor.",
                     "ru": "Он купил много фруктов и овощей, в том числе яблоки и помидоры.",
                     "tj": "Ӯ бисёр мева-сабзавот харид, дар байни онҳо себ ва помидор ҳам буд."},
                    {"zh": "班里有三十个同学，其中五个是外国人。", "pinyin": "",
                     "uz": "Sinfda o'ttiz talaba bor, ulardan beshta chet ellik.",
                     "ru": "В классе тридцать учеников, из них пятеро иностранцы.",
                     "tj": "Дар синф си донишҷӯ аст, аз байни онҳо панҷ нафар хориҷӣ."},
                ],
            },
            {
                "no": 5,
                "title_zh": "（在）……下",
                "title_uz": "...sharoitida, ...ostida",
                "title_ru": "в условиях..., под...",
                "title_tj": "дар шароити..., зери...",
                "rule_uz": "'...sharoitida, ...ostida' ma'nosini beradi. Biror shart yoki holat ostida narsa sodir bo'lishini bildiradi.",
                "rule_ru": "Означает 'в условиях..., под...'. Указывает, что что-то происходит при определённом условии или обстоятельстве.",
                "rule_tj": "Маънои 'дар шароити..., зери...' дорад. Нишон медиҳад, ки чизе дар шарт ё ҳолати муайян рӯй медиҳад.",
                "examples": [
                    {"zh": "在父母的支持下，他完成了学业。", "pinyin": "",
                     "uz": "Ota-onasining qo'llab-quvvatlashi ostida u o'qishini tugatdi.",
                     "ru": "При поддержке родителей он завершил учёбу.",
                     "tj": "Зери дастгирии падару модар ӯ таҳсилашро хатм кард."},
                    {"zh": "在这种情况下，我们应该怎么做？", "pinyin": "",
                     "uz": "Bunday sharoitda biz nima qilishimiz kerak?",
                     "ru": "В таких условиях что нам следует делать?",
                     "tj": "Дар ин гуна шароит мо бояд чӣ кор кунем?"},
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
                    {"prompt_uz": "meva sharbati", "prompt_ru": "фруктовый сок", "prompt_tj": "шарбати мева", "answer": "果汁", "pinyin": "guǒzhī"},
                    {"prompt_uz": "foiz", "prompt_ru": "процент", "prompt_tj": "фоиз", "answer": "百分之", "pinyin": "bǎi fēn zhī"},
                    {"prompt_uz": "foyda, manfaat", "prompt_ru": "польза, выгода", "prompt_tj": "фоида, манфиат", "answer": "好处", "pinyin": "hǎochu"},
                    {"prompt_uz": "arziydi", "prompt_ru": "стоит того", "prompt_tj": "меарзад", "answer": "值得", "pinyin": "zhíde"},
                    {"prompt_uz": "bepul", "prompt_ru": "бесплатный", "prompt_tj": "бепул", "answer": "免费", "pinyin": "miǎnfèi"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский эквивалент следующих слов:",
                "instruction_tj": "Муодили ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "竟然", "prompt_ru": "竟然", "prompt_tj": "竟然", "answer": "kutilmaganda, ajablanib", "pinyin": "jìngrán"},
                    {"prompt_uz": "倍", "prompt_ru": "倍", "prompt_tj": "倍", "answer": "marta, barobar", "pinyin": "bèi"},
                    {"prompt_uz": "其中", "prompt_ru": "其中", "prompt_tj": "其中", "answer": "ularning ichida, shular orasida", "pinyin": "qízhōng"},
                    {"prompt_uz": "打扰", "prompt_ru": "打扰", "prompt_tj": "打扰", "answer": "bezovta qilmoq", "pinyin": "dǎrǎo"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (竟然、倍、值得、其中、在...下):",
                "instruction_ru": "Выберите подходящее слово (竟然、倍、值得、其中、在...下):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (竟然、倍、值得、其中、在...下):",
                "items": [
                    {"prompt_uz": "他______一个人喝了三瓶果汁！", "prompt_ru": "他______一个人喝了三瓶果汁！", "prompt_tj": "他______一个人喝了三瓶果汁！", "answer": "竟然", "pinyin": "jìngrán"},
                    {"prompt_uz": "这里的苹果是那里的两______。", "prompt_ru": "这里的苹果是那里的两______。", "prompt_tj": "这里的苹果是那里的两______。", "answer": "倍", "pinyin": "bèi"},
                    {"prompt_uz": "______老师的帮助______，他进步很快。", "prompt_ru": "______老师的帮助______，他进步很快。", "prompt_tj": "______老师的帮助______，他进步很快。", "answer": "在 / 下", "pinyin": "zài / xià"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["果汁", "百分之", "好处", "值得", "免费"]},
            {"no": 2, "answers": ["kutilmaganda, ajablanib", "marta, barobar", "ularning ichida, shular orasida", "bezovta qilmoq"]},
            {"no": 3, "answers": ["竟然", "倍", "在 / 下"]},
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
                "words": ["竟然", "值得", "其中", "好处"],
                "example": "这种水果对皮肤好处很多，其中维生素C尤其丰富，值得每天吃。",
            },
            {
                "no": 2,
                "instruction_uz": "'倍' va '（在）...下' qoliplaridan foydalanib har biridan 2 ta gap tuzing.",
                "instruction_ru": "Составьте по 2 предложения с конструкциями '倍' и '（在）...下'.",
                "instruction_tj": "Бо истифода аз қолипҳои '倍' ва '（在）...下' аз ҳар кадоме 2 ҷумла созед.",
                "topic_uz": "narx, xarid, iqtisodiyot mavzusida",
                "topic_ru": "на тему цены, покупок, экономики",
                "topic_tj": "дар мавзӯи нарх, харид, иқтисод",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Siz narx bilan sifatning qaysi biriga ko'proq e'tibor berasiz? 你认为一分钱一分货有道理吗？",
                "topic_ru": "На что вы обращаете больше внимания — на цену или на качество? 你认为一分钱一分货有道理吗？",
                "topic_tj": "Ба чӣ бештар диққат медиҳед — нарх ё сифат? 你认为一分钱一分货有道理吗？",
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
