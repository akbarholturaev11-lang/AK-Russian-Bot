import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 12,
    "lesson_code": "HSK3-L12",
    "title": json.dumps({"zh": "把重要的东西放在我这儿吧", "uz": "Muhim narsalarni men oldimda qoldir", "ru": "Оставь важные вещи у меня", "tj": "Чизҳои муҳимро пеши ман монд"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "'才' va '就' farqi, '把'-konstruktsiyasi 2-qism va '让+odam+F' iborasi", "ru": "Разница '才' и '就', конструкция '把' часть 2, выражение '让+человек+Гл'", "tj": "Фарқи '才' ва '就', сохтори '把' қисми 2, ибораи '让+одам+Ф'"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda '才' (nisbatan kech) va '就' (nisbatan erta) farqini, '把'-konstruktsiyasining V+在/到/给 shaklini va '让' causative iborasini o'rganamiz.", "ru": "В этом уроке мы изучим разницу '才' (относительно поздно) и '就' (относительно рано), форму '把+V+在/到/给' и каузативное выражение '让'.", "tj": "Дар ин дарс мо фарқи '才' (нисбатан дер) ва '就' (нисбатан зуд), шакли '把+V+в/ба/ба' ва ибораи каузативии '让'-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "重要", "pinyin": "zhòngyào", "pos": "adj", "uz": "muhim, ahamiyatli", "ru": "важный", "tj": "муҳим"},
        {"no": 2, "zh": "才", "pinyin": "cái", "pos": "adv", "uz": "shundagina; (kutilganidan) kech", "ru": "только тогда; (позже ожидаемого)", "tj": "танҳо он вақт; (дертар аз интизорӣ)"},
        {"no": 3, "zh": "就", "pinyin": "jiù", "pos": "adv", "uz": "(kutilganidan) erta; darhol", "ru": "(раньше ожидаемого); сразу", "tj": "(зудтар аз интизорӣ); фавран"},
        {"no": 4, "zh": "让", "pinyin": "ràng", "pos": "v", "uz": "ruxsat bermoq; majbur qilmoq", "ru": "позволять; заставлять", "tj": "иҷозат додан; маҷбур кардан"},
        {"no": 5, "zh": "保管", "pinyin": "bǎoguǎn", "pos": "v", "uz": "asrab saqlash, saqlamoq", "ru": "хранить, сберегать", "tj": "нигоҳ доштан, ҳифз кардан"},
        {"no": 6, "zh": "钥匙", "pinyin": "yàoshi", "pos": "n", "uz": "kalit", "ru": "ключ", "tj": "калид"},
        {"no": 7, "zh": "证件", "pinyin": "zhèngjiàn", "pos": "n", "uz": "hujjat, guvohnoma", "ru": "документ, удостоверение", "tj": "ҳуҷҷат, гувоҳнома"},
        {"no": 8, "zh": "交", "pinyin": "jiāo", "pos": "v", "uz": "topshirmoq, bermoq", "ru": "сдавать, передавать", "tj": "супурдан, додан"},
        {"no": 9, "zh": "放心", "pinyin": "fàngxīn", "pos": "v", "uz": "xotirjam bo'lmoq", "ru": "не беспокоиться", "tj": "хотирҷамъ будан"},
        {"no": 10, "zh": "担心", "pinyin": "dānxīn", "pos": "v", "uz": "xavotir olmoq", "ru": "беспокоиться, волноваться", "tj": "нигарон будан"},
        {"no": 11, "zh": "安全", "pinyin": "ānquán", "pos": "adj/n", "uz": "xavfsiz; xavfsizlik", "ru": "безопасный; безопасность", "tj": "бехатар; бехатарӣ"},
        {"no": 12, "zh": "丢", "pinyin": "diū", "pos": "v", "uz": "yo'qotmoq, tashlamoq", "ru": "терять, потерять", "tj": "гум кардан"},
        {"no": 13, "zh": "小心", "pinyin": "xiǎoxīn", "pos": "v/adj", "uz": "ehtiyot bo'lmoq; ehtiyotkor", "ru": "быть осторожным; осторожный", "tj": "эҳтиёт будан; эҳтиёткор"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Muhim narsalarni topshirish", "ru": "Передача важных вещей", "tj": "Супурдани чизҳои муҳим"},
            "dialogue": [
                {"speaker": "A", "zh": "把重要的东西放在我这儿吧，安全。", "pinyin": "Bǎ zhòngyào de dōngxi fàng zài wǒ zhèr ba, ānquán.", "uz": "Muhim narsalarni men oldimda qoldir, xavfsiz bo'ladi.", "ru": "Оставь важные вещи у меня, будет безопасно.", "tj": "Чизҳои муҳимро пеши ман монд, бехатар мешавад."},
                {"speaker": "B", "zh": "好，我把钥匙交给你。你帮我保管吧。", "pinyin": "Hǎo, wǒ bǎ yàoshi jiāo gěi nǐ. Nǐ bāng wǒ bǎoguǎn ba.", "uz": "Yaxshi, kalitni sizga topshiraman. Saqlab qo'yib bering.", "ru": "Ладно, отдам тебе ключ. Сохрани, пожалуйста.", "tj": "Хуб, калидро ба шумо медиҳам. Нигоҳ доред."},
                {"speaker": "A", "zh": "放心，我会好好保管的。", "pinyin": "Fàngxīn, wǒ huì hǎohǎo bǎoguǎn de.", "uz": "Xotirjam bo'ling, yaxshi saqlayman.", "ru": "Не беспокойся, я хорошо сохраню.", "tj": "Хотирҷамъ бошед, хуб нигоҳ медорам."},
                {"speaker": "B", "zh": "谢谢你！你让我放心多了。", "pinyin": "Xièxie nǐ! Nǐ ràng wǒ fàngxīn duō le.", "uz": "Rahmat! Siz meni ancha xotirjam qildingiz.", "ru": "Спасибо! Ты меня очень успокоил.", "tj": "Раҳмат! Шумо маро хеле хотирҷамъ кардед."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Hujjatlarni saqlash", "ru": "Хранение документов", "tj": "Нигоҳ доштани ҳуҷҷатҳо"},
            "dialogue": [
                {"speaker": "A", "zh": "你的证件放到哪儿了？", "pinyin": "Nǐ de zhèngjiàn fàng dào nǎr le?", "uz": "Hujjatlaringizni qayerga qo'ydingiz?", "ru": "Куда ты положил документы?", "tj": "Ҳуҷҷатҳоятонро куҷо гузоштед?"},
                {"speaker": "B", "zh": "我把证件放在包里了，别担心。", "pinyin": "Wǒ bǎ zhèngjiàn fàng zài bāo lǐ le, bié dānxīn.", "uz": "Hujjatlarni sumkaga solib qo'ydim, xavotir olmang.", "ru": "Я положил документы в сумку, не беспокойся.", "tj": "Ман ҳуҷҷатҳоро дар сумка гузоштам, нигарон набошед."},
                {"speaker": "A", "zh": "他才七点就回来了，真早！", "pinyin": "Tā cái qī diǎn jiù huílái le, zhēn zǎo!", "uz": "U soat yettiday uyga keldi, juda erta!", "ru": "Он уже в семь вернулся домой, так рано!", "tj": "Вай соати ҳафт баргашт ба хона, хеле барвақт!"},
                {"speaker": "B", "zh": "是啊，他平时八点才回来。", "pinyin": "Shì a, tā píngshí bā diǎn cái huílái.", "uz": "Ha, u odatda soat sakkizda keladi.", "ru": "Да, обычно он возвращается только в восемь.", "tj": "Ҳа, вай одатан соати ҳашт меояд."}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "'才' va '就' farqi", "ru": "Разница '才' и '就'", "tj": "Фарқи '才' ва '就'"},
            "dialogue": [
                {"speaker": "A", "zh": "你几点到的？我等了很久！", "pinyin": "Nǐ jǐ diǎn dào de? Wǒ děng le hěn jiǔ!", "uz": "Soat nechada keldingiz? Men ancha kutdim!", "ru": "Во сколько ты пришёл? Я долго ждал!", "tj": "Соати чанд омадед? Ман хеле интизор шудам!"},
                {"speaker": "B", "zh": "我九点就到了，你怎么九点半才来？", "pinyin": "Wǒ jiǔ diǎn jiù dào le, nǐ zěnme jiǔ diǎn bàn cái lái?", "uz": "Men soat to'qqizda keldim, nima uchun siz soat to'qqiz yarimda keldingiz?", "ru": "Я пришёл в девять, почему ты пришёл только в половине десятого?", "tj": "Ман соати нӯҳ омадам, чаро шумо соати нӯҳ ва ним омадед?"},
                {"speaker": "A", "zh": "对不起，我让你久等了！", "pinyin": "Duìbuqǐ, wǒ ràng nǐ jiǔ děng le!", "uz": "Kechirasiz, sizni uzoq kutdirdim!", "ru": "Извини, я заставил тебя долго ждать!", "tj": "Бубахшед, ман шуморо дер интизор гузоштам!"},
                {"speaker": "B", "zh": "没关系，以后别让我等就行了！", "pinyin": "Méi guānxi, yǐhòu bié ràng wǒ děng jiù xíng le!", "uz": "Hech gap emas, keyingi safar meni kutdirmang, bas!", "ru": "Ничего, только в следующий раз не заставляй меня ждать!", "tj": "Майлаш, дафъаи дигар маро интизор нагузоред, бас!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Yo'qotmaslik uchun ehtiyotkorlik", "ru": "Осторожность, чтобы не потерять", "tj": "Эҳтиёт барои гум накардан"},
            "dialogue": [
                {"speaker": "A", "zh": "你把护照放到安全的地方了吗？", "pinyin": "Nǐ bǎ hùzhào fàng dào ānquán de dìfāng le ma?", "uz": "Pasportni xavfsiz joyga qo'ydingizmi?", "ru": "Ты положил паспорт в безопасное место?", "tj": "Оё шиносномаро дар ҷои бехатар гузоштед?"},
                {"speaker": "B", "zh": "放了，让你担心了，不好意思。", "pinyin": "Fàng le, ràng nǐ dānxīn le, bù hǎo yìsi.", "uz": "Qo'ydim, sizni xavotir qildim, kechirasiz.", "ru": "Положил, извини, что заставил тебя беспокоиться.", "tj": "Гузоштам, ман шуморо нигарон кардам, бубахшед."},
                {"speaker": "A", "zh": "小心点儿，别把它丢了！", "pinyin": "Xiǎoxīn diǎnr, bié bǎ tā diū le!", "uz": "Ehtiyot bo'ling, yo'qotmang!", "ru": "Будь осторожен, не потеряй его!", "tj": "Эҳтиёт бошед, гум накунед!"},
                {"speaker": "B", "zh": "知道了，我才不会让它丢的！", "pinyin": "Zhīdào le, wǒ cái bú huì ràng tā diū de!", "uz": "Bildim, men uni yo'qotmasam kerak!", "ru": "Понял, я вовсе не дам ему потеряться!", "tj": "Фаҳмидам, ман ҳаргиз онро гум намекунам!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "\"才\"和\"就\"的区别",
            "title_uz": "\"才\" va \"就\" farqi",
            "title_ru": "Разница между \"才\" и \"就\"",
            "title_tj": "Фарқи \"才\" ва \"就\"",
            "rule_uz": "'就' kutilganidan erta yoki tez bo'lganini bildiradi (erta keldi = soat to'qqizda keldi). '才' kutilganidan kech yoki qiyin bo'lganini bildiradi (soat o'n birda keldi). Ikkalasi ham taqqoslash asosida baholanadi.",
            "rule_ru": "'就' выражает, что что-то произошло раньше или быстрее ожидаемого (рано пришёл = в девять). '才' выражает, что что-то произошло позже или сложнее ожидаемого (пришёл только в одиннадцать). Оба оцениваются на основе сравнения.",
            "rule_tj": "'就' ифода мекунад, ки чизе зудтар ё барвақттар аз интизорӣ рух дод (барвақт омад = соати нӯҳ). '才' ифода мекунад, ки чизе дертар ё мушкилтар аз интизорӣ рух дод (фақат соати ёздаҳ омад). Ҳарду дар асоси муқоиса арзёбӣ мешаванд.",
            "examples": [
                {"zh": "他八点就来了，真早！", "pinyin": "Tā bā diǎn jiù lái le, zhēn zǎo!", "uz": "U soat sakkizda keldi, juda erta!", "ru": "Он пришёл уже в восемь, так рано!", "tj": "Вай соати ҳашт омад, хеле барвақт!"},
                {"zh": "他十一点才来，太晚了！", "pinyin": "Tā shíyī diǎn cái lái, tài wǎn le!", "uz": "U soat o'n birda keldi, juda kech!", "ru": "Он пришёл только в одиннадцать, так поздно!", "tj": "Вай соати ёздаҳ омад, хеле дер!"}
            ]
        },
        {
            "no": 2,
            "title_zh": "把字句②：把 + O + V + 在/到/给",
            "title_uz": "把-konstruktsiyasi②: 把 + OB + F + 在/到/给",
            "title_ru": "Конструкция 把②: 把 + объект + Гл + 在/到/给",
            "title_tj": "Сохтори 把②: 把 + объект + Ф + 在/到/给",
            "rule_uz": "'把'-konstruktsiyasida fe'ldan keyin '在' (joyda), '到' (joyga) yoki '给' (kimgadir) qo'shilishi mumkin. Bu ob'ektning qayerda, qayerga yoki kimga taalluqli ekanini bildiradi.",
            "rule_ru": "В конструкции '把' после глагола может следовать '在' (на/в месте), '到' (к месту) или '给' (кому-то). Это указывает на место, пункт назначения или получателя объекта.",
            "rule_tj": "Дар сохтори '把' баъди феъл '在' (дар ҷое), '到' (ба ҷое) ё '给' (ба касе) омада метавонад. Ин ҷойгоҳ, мақсади ҳаракат ё гирандаи объектро нишон медиҳад.",
            "examples": [
                {"zh": "把钥匙交给你。", "pinyin": "Bǎ yàoshi jiāo gěi nǐ.", "uz": "Kalitni sizga topshiraman.", "ru": "Отдаю ключ тебе.", "tj": "Калидро ба шумо медиҳам."},
                {"zh": "把书放在桌子上。", "pinyin": "Bǎ shū fàng zài zhuōzi shàng.", "uz": "Kitobni stolda qoldiring.", "ru": "Положи книгу на стол.", "tj": "Китобро ба болои миз монд."}
            ]
        },
        {
            "no": 3,
            "title_zh": "让 + 人 + 动词（使役句）",
            "title_uz": "让 + odam + fe'l (majbur qilmoq)",
            "title_ru": "让 + человек + глагол (каузатив)",
            "title_tj": "让 + одам + феъл (маҷбур кардан)",
            "rule_uz": "'让' = biror kishini biror narsa qilishiga ruxsat bermoq yoki uni shunday qilishga majbur qilmoq. Tuzilma: subekt + 让 + odam + fe'l. Salbiy: 让……别……",
            "rule_ru": "'让' = позволять кому-то сделать что-то или заставлять кого-то это делать. Структура: подлежащее + 让 + человек + глагол. Отрицание: 让……别……",
            "rule_tj": "'让' = иҷозат додан ба касе барои кардани чизе ё маҷбур кардани вай ба ин амал. Сохтор: мубтадо + 让 + одам + феъл. Манфӣ: 让……别……",
            "examples": [
                {"zh": "你让我放心多了。", "pinyin": "Nǐ ràng wǒ fàngxīn duō le.", "uz": "Siz meni ancha xotirjam qildingiz.", "ru": "Ты меня очень успокоил.", "tj": "Шумо маро хеле хотирҷамъ кардед."},
                {"zh": "别让我等太久！", "pinyin": "Bié ràng wǒ děng tài jiǔ!", "uz": "Meni uzoq kutdirmang!", "ru": "Не заставляй меня долго ждать!", "tj": "Маро дер интизор нагузор!"}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Muhim narsalarni men oldimda qoldir, xavfsiz bo'ladi.", "ru": "Оставь важные вещи у меня, будет безопасно.", "tj": "Чизҳои муҳимро пеши ман монд, бехатар мешавад."},
                {"no": 2, "uz": "U soat sakkizda keldi, juda erta!", "ru": "Он пришёл уже в восемь, так рано!", "tj": "Вай соати ҳашт омад, хеле барвақт!"},
                {"no": 3, "uz": "U soat o'n birda keldi, juda kech!", "ru": "Он пришёл только в одиннадцать, так поздно!", "tj": "Вай соати ёздаҳ омад, хеле дер!"},
                {"no": 4, "uz": "Kalitni sizga topshiraman.", "ru": "Отдаю ключ тебе.", "tj": "Калидро ба шумо медиҳам."},
                {"no": 5, "uz": "Meni uzoq kutdirmang!", "ru": "Не заставляй меня долго ждать!", "tj": "Маро дер интизор нагузор!"}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "他八点___来了，真早！", "sentence_uz": "U soat sakkizda ___ keldi, juda erta!", "sentence_ru": "Он ___ пришёл в восемь, так рано!", "sentence_tj": "Вай соати ҳашт ___ омад, хеле барвақт!", "hint": "就"},
                {"no": 2, "sentence_zh": "他十一点___来，太晚了！", "sentence_uz": "U soat o'n birda ___ keldi, juda kech!", "sentence_ru": "Он ___ пришёл в одиннадцать, так поздно!", "sentence_tj": "Вай соати ёздаҳ ___ омад, хеле дер!", "hint": "才"},
                {"no": 3, "sentence_zh": "把钥匙交___你。", "sentence_uz": "Kalitni sizga ___.", "sentence_ru": "Отдаю ключ ___.", "sentence_tj": "Калидро ___ шумо медиҳам.", "hint": "给"},
                {"no": 4, "sentence_zh": "你___我放心多了！", "sentence_uz": "Siz meni ancha xotirjam ___!", "sentence_ru": "Ты ___ меня успокоил!", "sentence_tj": "Шумо маро хеле хотирҷамъ ___!", "hint": "让"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "我把证件放在包里了，别担心。", "pinyin": "Wǒ bǎ zhèngjiàn fàng zài bāo lǐ le, bié dānxīn."},
                {"no": 2, "zh": "小心点儿，别让它丢了！", "pinyin": "Xiǎoxīn diǎnr, bié ràng tā diū le!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "把重要的东西放在我这儿吧，安全。"},
                {"no": 2, "zh": "他八点就来了，真早！"},
                {"no": 3, "zh": "他十一点才来，太晚了！"},
                {"no": 4, "zh": "把钥匙交给你。"},
                {"no": 5, "zh": "别让我等太久！"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "就"},
                {"no": 2, "answer": "才"},
                {"no": 3, "answer": "给"},
                {"no": 4, "answer": "让"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Hujjatlarni sumkaga solib qo'ydim, xavotir olmang.", "ru": "Я положил документы в сумку, не беспокойся.", "tj": "Ман ҳуҷҷатҳоро дар сумка гузоштам, нигарон набошед."},
                {"no": 2, "uz": "Ehtiyot bo'ling, yo'qotmang!", "ru": "Будь осторожен, не дай ему потеряться!", "tj": "Эҳтиёт бошед, гум накунед!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'才' va '就' so'zlaridan foydalanib, kutilganidan erta va kech bo'lgan voqealar haqida 4 ta jumla yozing.", "ru": "Напишите 4 предложения о событиях, которые произошли раньше или позже ожидаемого, используя '才' и '就'.", "tj": "4 ҷумла дар бораи рӯйдодҳое нависед, ки барвақттар ё дертар аз интизорӣ рух додаанд, бо '才' ва '就'."},
        {"task_no": 2, "uz": "'让' va '把+V+给/在/到' tuzilmalarini ishlatib, kundalik hayotdan 4 ta jumla tuzing.", "ru": "Составьте 4 предложения из повседневной жизни, используя '让' и '把+V+给/在/到'.", "tj": "4 ҷумла аз ҳаёти ҳаррӯза бо '让' ва '把+V+给/在/到' тартиб диҳед."}
    ], ensure_ascii=False),
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
