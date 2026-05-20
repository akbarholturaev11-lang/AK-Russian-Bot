import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 1,
    "lesson_code": "HSK4-L01",
    "title": "简单的爱情",
    "goal": json.dumps({"uz": "romantik munosabatlar va sevgi haqida gapirish; 不仅…也…, 从来, 刚, 即使…也… grammatik qoliplarini o'zlashtirish", "ru": "говорить о романтических отношениях и любви; освоить грамматические конструкции 不仅…也…, 从来, 刚, 即使…也…", "tj": "гуфтугӯ дар бораи муносибатҳои романтикӣ ва муҳаббат; аз худ кардани қолипҳои грамматикии 不仅…也…, 从来, 刚, 即使…也…"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Oddiy sevgi' mavzusiga bag'ishlangan. Unda turmush o'rtoq tanlash, sevgi va munosabatlar haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 不仅...也/还/而且..., 从来, 刚, 即使...也..., (在)...上.", "ru": "Этот урок посвящён теме 'Простая любовь'. В нём вы научитесь говорить о выборе партнёра, любви и отношениях. Основные грамматические конструкции: 不仅...也/还/而且..., 从来, 刚, 即使...也..., (在)...上.", "tj": "Ин дарс ба мавзӯи 'Муҳаббати содда' бахшида шудааст. Дар он интихоби ҳамсар, муҳаббат ва муносибатҳо омӯхта мешавад. Қолипҳои асосии грамматикӣ: 不仅...也/还/而且..., 从来, 刚, 即使...也..., (在)...上."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "法律", "pinyin": "fǎlǜ", "pos": "n.", "uz": "huquq, qonun", "ru": "право, закон", "tj": "ҳуқуқ, қонун"},
            {"no": 2, "zh": "俩", "pinyin": "liǎ", "pos": "num.-m.", "uz": "ikkalasi, ikki (kishi)", "ru": "оба, двое", "tj": "ҳарду, ду нафар"},
            {"no": 3, "zh": "印象", "pinyin": "yìnxiàng", "pos": "n.", "uz": "taassurot", "ru": "впечатление", "tj": "таассурот"},
            {"no": 4, "zh": "深", "pinyin": "shēn", "pos": "adj.", "uz": "chuqur", "ru": "глубокий", "tj": "чуқур"},
            {"no": 5, "zh": "熟悉", "pinyin": "shúxī", "pos": "v.", "uz": "yaxshi bilmoq, tanish bo'lmoq", "ru": "хорошо знать, быть знакомым", "tj": "хуб донистан, шинос будан"},
            {"no": 6, "zh": "不仅", "pinyin": "bùjǐn", "pos": "conj.", "uz": "nafaqat, faqat emas", "ru": "не только", "tj": "на танҳо"},
            {"no": 7, "zh": "性格", "pinyin": "xìnggé", "pos": "n.", "uz": "xarakter, tabiat", "ru": "характер, натура", "tj": "хусусият, табиат"},
            {"no": 8, "zh": "开玩笑", "pinyin": "kāi wánxiào", "pos": "v.", "uz": "hazil qilmoq, kulgi qilmoq", "ru": "шутить, разыгрывать", "tj": "шӯхӣ кардан"},
            {"no": 9, "zh": "从来", "pinyin": "cónglái", "pos": "adv.", "uz": "hech qachon (inkor bilan), doim", "ru": "никогда (с отрицанием), всегда", "tj": "ҳеч вақт (бо инкор), ҳамеша"},
            {"no": 10, "zh": "最好", "pinyin": "zuìhǎo", "pos": "adv.", "uz": "eng yaxshisi, ma'quli", "ru": "лучше всего, лучше бы", "tj": "беҳтар аст"},
            {"no": 11, "zh": "共同", "pinyin": "gòngtóng", "pos": "adj.", "uz": "umumiy, birgalikdagi", "ru": "общий, совместный", "tj": "умумӣ, муштарак"},
            {"no": 12, "zh": "适合", "pinyin": "shìhé", "pos": "v.", "uz": "mos kelmoq, to'g'ri kelmoq", "ru": "подходить, соответствовать", "tj": "мувофиқ будан"},
            {"no": 13, "zh": "幸福", "pinyin": "xìngfú", "pos": "adj./n.", "uz": "baxtli; baxt", "ru": "счастливый; счастье", "tj": "хушбахт; бахт"},
            {"no": 14, "zh": "生活", "pinyin": "shēnghuó", "pos": "v./n.", "uz": "yashash; hayot, turmush", "ru": "жить; жизнь, быт", "tj": "зиндагӣ кардан; зиндагӣ, ҳаёт"},
            {"no": 15, "zh": "刚", "pinyin": "gāng", "pos": "adv.", "uz": "hozir, yaqinda (nisbatan)", "ru": "только что, недавно", "tj": "ҳозир, тоза"},
            {"no": 16, "zh": "浪漫", "pinyin": "làngmàn", "pos": "adj.", "uz": "romantik", "ru": "романтичный", "tj": "романтикӣ"},
            {"no": 17, "zh": "够", "pinyin": "gòu", "pos": "v./adj.", "uz": "yetarli bo'lmoq; yetarli", "ru": "быть достаточным; достаточный", "tj": "кофӣ будан; кофӣ"},
            {"no": 18, "zh": "缺点", "pinyin": "quēdiǎn", "pos": "n.", "uz": "kamchilik, nuqson", "ru": "недостаток, изъян", "tj": "камбудӣ, нуқсон"},
            {"no": 19, "zh": "接受", "pinyin": "jiēshòu", "pos": "v.", "uz": "qabul qilmoq", "ru": "принимать, воспринимать", "tj": "қабул кардан"},
            {"no": 20, "zh": "羡慕", "pinyin": "xiànmù", "pos": "v.", "uz": "hasad qilmoq, qiziqish bilan qarash", "ru": "завидовать, восхищаться", "tj": "ҳасад бурдан, ҳавас кардан"},
            {"no": 21, "zh": "爱情", "pinyin": "àiqíng", "pos": "n.", "uz": "sevgi (romantik)", "ru": "любовь (романтическая)", "tj": "муҳаббат (романтикӣ)"},
            {"no": 22, "zh": "星星", "pinyin": "xīngxīng", "pos": "n.", "uz": "yulduz", "ru": "звезда", "tj": "ситора"},
            {"no": 23, "zh": "即使", "pinyin": "jíshǐ", "pos": "conj.", "uz": "hatto agar...ham", "ru": "даже если", "tj": "ҳатто агар...ҳам"},
            {"no": 24, "zh": "加班", "pinyin": "jiābān", "pos": "v.", "uz": "qo'shimcha ish soatlarida ishlash", "ru": "работать сверхурочно", "tj": "аз вақти кор зиёд кор кардан"},
            {"no": 25, "zh": "照", "pinyin": "zhào", "pos": "v.", "uz": "yoritmoq, nur sochmoq", "ru": "светить, освещать", "tj": "равшан кардан, нур пошидан"},
            {"no": 26, "zh": "感动", "pinyin": "gǎndòng", "pos": "v.", "uz": "ta'sir qilmoq, his qilmoq", "ru": "трогать, волновать", "tj": "таъсир кардан, дил ба даст овардан"},
            {"no": 27, "zh": "自然", "pinyin": "zìrán", "pos": "adv.", "uz": "tabiiyki, o'z-o'zidan", "ru": "естественно, само собой", "tj": "табиатан, худ аз худ"},
            {"no": 28, "zh": "原因", "pinyin": "yuányīn", "pos": "n.", "uz": "sabab", "ru": "причина", "tj": "сабаб"},
            {"no": 29, "zh": "互相", "pinyin": "hùxiāng", "pos": "adv.", "uz": "bir-biriga, o'zaro", "ru": "друг другу, взаимно", "tj": "якдигарро, мутақобилан"},
            {"no": 30, "zh": "吸引", "pinyin": "xīyǐn", "pos": "v.", "uz": "jalb qilmoq, tortmoq", "ru": "привлекать, притягивать", "tj": "ҷалб кардан, кашидан"},
            {"no": 31, "zh": "脾气", "pinyin": "píqì", "pos": "n.", "uz": "fe'l-atvor, kayfiyat", "ru": "характер, темперамент", "tj": "феъл-атвор, хулқ"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "孙月 va 王静 ning erkak do'sti haqida suhbat",
                "scene_ru": "孙月 и 王静 разговаривают о парне 王静",
                "scene_tj": "孙月 ва 王静 дар бораи писари 王静 гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "孙月", "zh": "听说你哥哥最近要结婚了，他是你同学吗？", "pinyin": "",
                     "uz": "Eshitdim, akang yaqinda uylanadi, u sening sinfdoshing ekanmi?",
                     "ru": "Слышала, твой брат скоро женится — он твой однокурсник?",
                     "tj": "Шунидам, бародарат ба наздикӣ хонадор мешавад — ӯ ҳамсинфи туст?"},
                    {"speaker": "王静", "zh": "不是，他学的是新闻，我学的是法律，我们不是一个班。", "pinyin": "",
                     "uz": "Yo'q, u jurnalistika o'qiydi, men esa huquq, biz bir guruhda emasmiz.",
                     "ru": "Нет, он учится на журналистике, я — на юридическом, мы в разных группах.",
                     "tj": "Не, ӯ журналистика мехонад, ман ҳуқуқ, мо дар як гурӯҳ нестем."},
                    {"speaker": "孙月", "zh": "那你们俩是怎么认识的？", "pinyin": "",
                     "uz": "Xo'sh, siz ikkalangiz qanday tanishib qoldingiz?",
                     "ru": "Тогда как вы двое познакомились?",
                     "tj": "Пас шумо ду нафар чӣ тавр шинос шудед?"},
                    {"speaker": "王静", "zh": "我们是在足球比赛中认识的，我对他的印象很深，他不仅踢球踢得好，性格也不错。", "pinyin": "",
                     "uz": "Biz futbol musobaqasida tanishdik, u menga katta taassurot qoldirdi — nafaqat yaxshi futbol o'ynaydi, xarakteri ham yaxshi.",
                     "ru": "Мы познакомились на футбольном матче, он произвёл на меня сильное впечатление — не только хорошо играет в футбол, но и характер хороший.",
                     "tj": "Мо дар мусобақаи футбол шинос шудем, ӯ таассуроти амиқ гузошт — на танҳо хуб футбол мебозад, балки хулқаш ҳам хуб аст."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "王静 o'qituvchi Li bilan ulanayotgani haqida gaplashadi",
                "scene_ru": "王静 рассказывает учителю Ли о предстоящей свадьбе",
                "scene_tj": "王静 бо муаллим Ли дар бораи никоҳи наздик сӯҳбат мекунад",
                "dialogue": [
                    {"speaker": "王静", "zh": "李老师，我下周五就要结婚了。", "pinyin": "",
                     "uz": "O'qituvchi Li, men kelasi juma kuni turmushga chiqaman.",
                     "ru": "Учитель Ли, я выхожу замуж в следующую пятницу.",
                     "tj": "Муаллим Ли, ман ҷумъаи оянда арӯсӣ мекунам."},
                    {"speaker": "李老师", "zh": "你是在开玩笑吧？你们不是才认识一个月？", "pinyin": "",
                     "uz": "Hazil qilayapsanmi? Siz bir oy oldin tanishmagandingizmi?",
                     "ru": "Ты шутишь? Вы же познакомились всего месяц назад?",
                     "tj": "Шӯхӣ мекунӣ? Шумо як моҳ пеш шинос нашудед?"},
                    {"speaker": "王静", "zh": "虽然我们认识的时间不长，但我从来没有这么快乐过。我们有共同的爱好，彼此很适合。", "pinyin": "",
                     "uz": "Garchi biz uzoq vaqt tanish bo'lmasak-da, men hech qachon bunday baxtli bo'lmagan edim. Bizda umumiy qiziqishlar bor, bir-birimizga mos kelamiz.",
                     "ru": "Хотя мы знакомы недолго, я никогда не была так счастлива. У нас общие увлечения, мы очень подходим друг другу.",
                     "tj": "Гарчанде мо муддати кӯтоҳ шинос шудем, ман ҳеч вақт ин қадар хушбахт набудам. Мо шавқу завқи умумӣ дорем, ба ҳам мувофиқем."},
                    {"speaker": "李老师", "zh": "那太好了！祝你们幸福！", "pinyin": "",
                     "uz": "Bu juda yaxshi! Sizlarga baxt tilayman!",
                     "ru": "Это замечательно! Желаю вам счастья!",
                     "tj": "Ин хеле хуб аст! Ба шумо хушбахтӣ мехоҳам!"},
                ],
            },
            {
                "block_no": 3,
                "section_label": "课文 3",
                "scene_uz": "O'qituvchi Gao va o'qituvchi Li turmush hayoti haqida suhbatlashadi",
                "scene_ru": "Учитель Гао и учитель Ли беседуют о семейной жизни",
                "scene_tj": "Муаллим Гао ва муаллим Ли дар бораи ҳаёти оилавӣ гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "高老师", "zh": "听说您和丈夫结婚快二十年了？", "pinyin": "",
                     "uz": "Eshitdim, siz eringiz bilan yigirma yilga yaqin turmush qurgan ekansiz?",
                     "ru": "Говорят, вы с мужем замужем почти двадцать лет?",
                     "tj": "Шунидам, шумо бо шавҳаратон наздик ба бист сол аст никоҳ кардед?"},
                    {"speaker": "李老师", "zh": "是的。刚结婚那时候，每天都很浪漫，现在生活虽然不够浪漫，但是我们很幸福。", "pinyin": "",
                     "uz": "Ha. Yangi turmush qurgan paytimizda hamma narsa romantik edi, hozir hayot unchalik romantik emas, lekin biz baxtlimiz.",
                     "ru": "Да. Когда мы только поженились, каждый день был очень романтичным, сейчас жизнь не такая романтичная, но мы очень счастливы.",
                     "tj": "Бале. Вақте ки тоза хонадор шудем, ҳар рӯз хеле романтикӣ буд, ҳоло зиндагӣ он қадар романтикӣ нест, аммо мо хушбахтем."},
                    {"speaker": "高老师", "zh": "幸福的原因是什么？", "pinyin": "",
                     "uz": "Baxtning sababi nima?",
                     "ru": "В чём причина вашего счастья?",
                     "tj": "Сабаби хушбахтӣ чист?"},
                    {"speaker": "李老师", "zh": "即使有缺点，也要互相接受、互相吸引。简单的生活就是最大的幸福。", "pinyin": "",
                     "uz": "Hatto kamchiliklari bo'lsa ham, bir-birini qabul qilish, bir-biriga jalb bo'lish kerak. Oddiy hayot — eng katta baxt.",
                     "ru": "Даже если есть недостатки, нужно принимать друг друга и притягиваться друг к другу. Простая жизнь — это и есть наибольшее счастье.",
                     "tj": "Ҳатто агар камбудиҳо ҳам бошанд, бояд якдигарро қабул кард ва ба ҳам ҷалб шуд. Зиндагии содда — бузургтарин бахт аст."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "不仅……也/还/而且……",
                "title_uz": "nafaqat...balki/ham...",
                "title_ru": "не только...но и/также...",
                "title_tj": "на танҳо...балки/ҳам...",
                "rule_uz": "'Nafaqat...balki...ham' ma'nosini beradi. Birinchi gapda 不仅, ikkinchi gapda 也, 还 yoki 而且 ishlatiladi.",
                "rule_ru": "Означает 'не только...но и...'. В первом предложении используется 不仅, во втором — 也, 还 или 而且.",
                "rule_tj": "Маънои 'на танҳо...балки...ҳам' дорад. Дар ҷумлаи аввал 不仅, дар дуввум 也, 还 ё 而且 истифода мешавад.",
                "examples": [
                    {"zh": "他不仅足球踢得好，性格也不错。", "pinyin": "",
                     "uz": "U nafaqat futbolni yaxshi o'ynaydi, xarakteri ham yaxshi.",
                     "ru": "Он не только хорошо играет в футбол, но и характер у него хороший.",
                     "tj": "Ӯ на танҳо хуб футбол мебозад, балки хулқаш ҳам хуб аст."},
                    {"zh": "这里不仅风景美，而且空气也很好。", "pinyin": "",
                     "uz": "Bu yerda nafaqat manzara chiroyli, balki havo ham yaxshi.",
                     "ru": "Здесь не только красивые виды, но и воздух очень чистый.",
                     "tj": "Дар ин ҷо на танҳо манзара зебост, балки ҳаво ҳам хуб аст."},
                ],
            },
            {
                "no": 2,
                "title_zh": "从来",
                "title_uz": "hech qachon / doim",
                "title_ru": "никогда / всегда",
                "title_tj": "ҳеч вақт / ҳамеша",
                "rule_uz": "'Hech qachon' yoki 'doim' ma'nosini beradi. Ko'pincha inkor fe'llari (不/没) bilan birga ishlatiladi.",
                "rule_ru": "Означает 'никогда' или 'всегда'. Часто используется вместе с отрицательными глаголами (不/没).",
                "rule_tj": "Маънои 'ҳеч вақт' ё 'ҳамеша' дорад. Аксар вақт бо феълҳои инкорӣ (不/没) якҷоя истифода мешавад.",
                "examples": [
                    {"zh": "我从来没有这么快乐过。", "pinyin": "",
                     "uz": "Men hech qachon bunday baxtli bo'lmagan edim.",
                     "ru": "Я никогда не была так счастлива.",
                     "tj": "Ман ҳеч вақт ин қадар хушбахт набудам."},
                    {"zh": "他从来不迟到。", "pinyin": "",
                     "uz": "U hech qachon kech qolmaydi.",
                     "ru": "Он никогда не опаздывает.",
                     "tj": "Ӯ ҳеч вақт дер намеояд."},
                ],
            },
            {
                "no": 3,
                "title_zh": "刚",
                "title_uz": "hozirgina, yaqinda",
                "title_ru": "только что, недавно",
                "title_tj": "ҳозир, тоза",
                "rule_uz": "'Hozirgina, yaqinda' ma'nosini beradi. Biror narsa yaqin o'tmishda bo'lganini bildiradi.",
                "rule_ru": "Означает 'только что, недавно'. Указывает на то, что что-то произошло в ближайшем прошлом.",
                "rule_tj": "Маънои 'ҳозир, тоза' дорад. Нишон медиҳад, ки чизе дар гузаштаи наздик рӯй додааст.",
                "examples": [
                    {"zh": "刚结婚那时候，每天都很浪漫。", "pinyin": "",
                     "uz": "Yangi turmush qurgan paytimizda hamma kun romantik edi.",
                     "ru": "Когда мы только поженились, каждый день был романтичным.",
                     "tj": "Вақте ки тоза хонадор шудем, ҳар рӯз романтикӣ буд."},
                    {"zh": "我刚到家，你就来了。", "pinyin": "",
                     "uz": "Men uyga hozirgina kelgan edim, sen ham kelding.",
                     "ru": "Я только что пришёл домой, и ты пришёл.",
                     "tj": "Ман ҳозир ба хона расидам, ту ҳам омадӣ."},
                ],
            },
            {
                "no": 4,
                "title_zh": "即使……也……",
                "title_uz": "hatto agar...bo'lsa ham",
                "title_ru": "даже если...всё равно",
                "title_tj": "ҳатто агар...ҳам бошад",
                "rule_uz": "'Hatto agar...bo'lsa ham' ma'nosini beradi. Shart qanchalik og'ir bo'lmasin, natija o'zgarmaydi.",
                "rule_ru": "Означает 'даже если...всё равно'. Результат не меняется, каким бы трудным ни было условие.",
                "rule_tj": "Маънои 'ҳатто агар...ҳам бошад' дорад. Натиҷа тағйир намеёбад, ҳарчанд шарт душвор бошад.",
                "examples": [
                    {"zh": "即使有缺点，也要互相接受。", "pinyin": "",
                     "uz": "Hatto kamchiliklari bo'lsa ham, bir-birini qabul qilish kerak.",
                     "ru": "Даже если есть недостатки, нужно принимать друг друга.",
                     "tj": "Ҳатто агар камбудиҳо ҳам бошанд, бояд якдигарро қабул кард."},
                    {"zh": "即使很忙，他也会打电话。", "pinyin": "",
                     "uz": "Hatto band bo'lsa ham, u qo'ng'iroq qiladi.",
                     "ru": "Даже если он очень занят, он всё равно позвонит.",
                     "tj": "Ҳатто агар машғул ҳам бошад, ӯ боз ҳам занг мезанад."},
                ],
            },
            {
                "no": 5,
                "title_zh": "（在）……上",
                "title_uz": "...jihatidan, ...sohasida",
                "title_ru": "в сфере..., с точки зрения...",
                "title_tj": "аз ҷиҳати..., дар соҳаи...",
                "rule_uz": "'...jihatidan, ...sohasida' ma'nosini beradi. Biror sohani yoki aspektni bildiradi.",
                "rule_ru": "Означает 'в сфере..., с точки зрения...'. Указывает на определённую область или аспект.",
                "rule_tj": "Маънои 'аз ҷиҳати..., дар соҳаи...' дорад. Соҳа ё ҷанбаи муайянро нишон медиҳад.",
                "examples": [
                    {"zh": "在性格上，他们两个很合适。", "pinyin": "",
                     "uz": "Xarakter jihatidan, ular ikkalasi juda mos keladi.",
                     "ru": "С точки зрения характера, они двое очень подходят друг другу.",
                     "tj": "Аз ҷиҳати хулқ, онҳо ду нафар хеле мувофиқанд."},
                    {"zh": "在学习上，他很认真。", "pinyin": "",
                     "uz": "O'qish sohasida u juda tirishqoq.",
                     "ru": "В учёбе он очень серьёзен.",
                     "tj": "Дар соҳаи таҳсил ӯ хеле ҷиддист."},
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
                    {"prompt_uz": "taassurot", "prompt_ru": "впечатление", "prompt_tj": "таассурот", "answer": "印象", "pinyin": "yìnxiàng"},
                    {"prompt_uz": "xarakter, tabiat", "prompt_ru": "характер, натура", "prompt_tj": "хусусият, табиат", "answer": "性格", "pinyin": "xìnggé"},
                    {"prompt_uz": "umumiy, birgalikdagi", "prompt_ru": "общий, совместный", "prompt_tj": "умумӣ, муштарак", "answer": "共同", "pinyin": "gòngtóng"},
                    {"prompt_uz": "mos kelmoq", "prompt_ru": "подходить", "prompt_tj": "мувофиқ будан", "answer": "适合", "pinyin": "shìhé"},
                    {"prompt_uz": "kamchilik", "prompt_ru": "недостаток", "prompt_tj": "камбудӣ", "answer": "缺点", "pinyin": "quēdiǎn"},
                    {"prompt_uz": "sevgi (romantik)", "prompt_ru": "любовь (романтическая)", "prompt_tj": "муҳаббат (романтикӣ)", "answer": "爱情", "pinyin": "àiqíng"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский эквивалент следующих слов:",
                "instruction_tj": "Муодили ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "幸福", "prompt_ru": "幸福", "prompt_tj": "幸福", "answer": "baxtli; baxt", "pinyin": "xìngfú"},
                    {"prompt_uz": "浪漫", "prompt_ru": "浪漫", "prompt_tj": "浪漫", "answer": "romantik", "pinyin": "làngmàn"},
                    {"prompt_uz": "吸引", "prompt_ru": "吸引", "prompt_tj": "吸引", "answer": "jalb qilmoq", "pinyin": "xīyǐn"},
                    {"prompt_uz": "接受", "prompt_ru": "接受", "prompt_tj": "接受", "answer": "qabul qilmoq", "pinyin": "jiēshòu"},
                    {"prompt_uz": "脾气", "prompt_ru": "脾气", "prompt_tj": "脾气", "answer": "fe'l-atvor, kayfiyat", "pinyin": "píqì"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (不仅、从来、即使、适合、共同):",
                "instruction_ru": "Выберите подходящее слово (不仅、从来、即使、适合、共同):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (不仅、从来、即使、适合、共同):",
                "items": [
                    {"prompt_uz": "他______没有迟到过。", "prompt_ru": "他______没有迟到过。", "prompt_tj": "他______没有迟到过。", "answer": "从来", "pinyin": "cónglái"},
                    {"prompt_uz": "______很忙，他也会陪家人。", "prompt_ru": "______很忙，他也会陪家人。", "prompt_tj": "______很忙，他也会陪家人。", "answer": "即使", "pinyin": "jíshǐ"},
                    {"prompt_uz": "他们有______的爱好，很______在一起。", "prompt_ru": "他们有______的爱好，很______在一起。", "prompt_tj": "他们有______的爱好，很______在一起。", "answer": "共同 / 适合", "pinyin": "gòngtóng / shìhé"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["印象", "性格", "共同", "适合", "缺点", "爱情"]},
            {"no": 2, "answers": ["baxtli; baxt", "romantik", "jalb qilmoq", "qabul qilmoq", "fe'l-atvor, kayfiyat"]},
            {"no": 3, "answers": ["从来", "即使", "共同 / 适合"]},
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
                "words": ["印象", "性格", "适合", "幸福"],
                "example": "他给我留下了很深的印象，因为他的性格很好。",
            },
            {
                "no": 2,
                "instruction_uz": "'不仅...也...' qolipidan foydalanib 2 ta gap tuzing.",
                "instruction_ru": "Составьте 2 предложения с конструкцией '不仅...也...'.",
                "instruction_tj": "Бо истифода аз қолипи '不仅...也...' 2 ҷумла созед.",
                "topic_uz": "sevgi va do'stlik mavzusida",
                "topic_ru": "на тему любви и дружбы",
                "topic_tj": "дар мавзӯи муҳаббат ва дӯстӣ",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Siz uchun ideal turmush o'rtoq qanday bo'lishi kerak? 幸福的爱情是什么样的？",
                "topic_ru": "Каким должен быть ваш идеальный партнёр? 幸福的爱情是什么样的？",
                "topic_tj": "Барои шумо ҳамсари идеалӣ чӣ гуна бояд бошад? 幸福的爱情是什么样的？",
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
