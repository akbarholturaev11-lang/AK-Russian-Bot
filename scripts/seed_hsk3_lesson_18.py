import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 18,
    "lesson_code": "HSK3-L18",
    "title": json.dumps({"zh": "我相信他们会同意的", "uz": "Ularning rozi bo'lishiga ishonaman", "ru": "Я верю, что они согласятся", "tj": "Ман боварам дорам, ки онҳо розӣ мешаванд"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "'Faqat…bo'lsa ham…' shartli gap, '关于' predlogi va 'nafaqat…balki…' biriktiruv bog'lovchisi", "ru": "Условное 'только если…то…', предлог '关于' и союз 'не только…но и…'", "tj": "Шартии 'танҳо агар…пас…', пешоянди '关于' ва пайвандаки 'на танҳо…балки ҳам…'"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda '只要…就…' shartli iborasini, '关于' (haqida, to'g'risida) predlogini va '不但…而且…' (nafaqat…balki ham…) bog'lovchisini o'rganamiz.", "ru": "В этом уроке мы изучим условное выражение '只要…就…', предлог '关于' (о, насчёт) и союз '不但…而且…' (не только…но и…).", "tj": "Дар ин дарс мо ибораи шартии '只要…就…', пешоянди '关于' (дар бораи, оид ба) ва пайвандаки '不但…而且…' (на танҳо…балки ҳам…)-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "相信", "pinyin": "xiāngxìn", "pos": "v", "uz": "ishonmoq", "ru": "верить, доверять", "tj": "бовар кардан"},
        {"no": 2, "zh": "同意", "pinyin": "tóngyì", "pos": "v", "uz": "rozi bo'lmoq, kelishmoq", "ru": "соглашаться", "tj": "розӣ шудан, қабул кардан"},
        {"no": 3, "zh": "只要", "pinyin": "zhǐyào", "pos": "conj", "uz": "faqat...bo'lsa/qilsa", "ru": "только если, лишь бы", "tj": "танҳо агар"},
        {"no": 4, "zh": "关于", "pinyin": "guānyú", "pos": "prep", "uz": "haqida, to'g'risida", "ru": "о, насчёт, относительно", "tj": "дар бораи, оид ба"},
        {"no": 5, "zh": "不但", "pinyin": "búdàn", "pos": "conj", "uz": "nafaqat", "ru": "не только", "tj": "на танҳо"},
        {"no": 6, "zh": "而且", "pinyin": "érqiě", "pos": "conj", "uz": "balki ham, bundan tashqari", "ru": "но и, кроме того", "tj": "балки ҳам, илова бар ин"},
        {"no": 7, "zh": "计划", "pinyin": "jìhuà", "pos": "n/v", "uz": "reja; reja tuzmoq", "ru": "план; планировать", "tj": "нақша; нақша кашидан"},
        {"no": 8, "zh": "提议", "pinyin": "tíyì", "pos": "n/v", "uz": "taklif; taklif qilmoq", "ru": "предложение; предлагать", "tj": "пешниҳод; пешниҳод кардан"},
        {"no": 9, "zh": "活动", "pinyin": "huódòng", "pos": "n/v", "uz": "tadbir, faoliyat; harakat qilmoq", "ru": "мероприятие; двигаться", "tj": "тадбир; ҳаракат кардан"},
        {"no": 10, "zh": "参加", "pinyin": "cānjiā", "pos": "v", "uz": "qatnashmoq, ishtirok qilmoq", "ru": "участвовать, принимать участие", "tj": "иштирок кардан"},
        {"no": 11, "zh": "成功", "pinyin": "chénggōng", "pos": "v/n", "uz": "muvaffaqiyat qozonmoq; muvaffaqiyat", "ru": "добиваться успеха; успех", "tj": "муваффақ шудан; муваффақият"},
        {"no": 12, "zh": "努力", "pinyin": "nǔlì", "pos": "v/adj", "uz": "harakat qilmoq; tirishqoq", "ru": "стараться; усердный", "tj": "кӯшиш кардан; кӯшишкор"},
        {"no": 13, "zh": "会议", "pinyin": "huìyì", "pos": "n", "uz": "majlis, yig'ilish", "ru": "собрание, заседание", "tj": "мажлис, ҷаласа"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Majlis haqida suhbat", "ru": "Разговор о собрании", "tj": "Суҳбат дар бораи мажлис"},
            "dialogue": [
                {"speaker": "A", "zh": "关于明天的会议，你觉得大家会同意吗？", "pinyin": "Guānyú míngtiān de huìyì, nǐ juéde dàjiā huì tóngyì ma?", "uz": "Ertangi majlis haqida, sizningcha hamma rozi bo'ladimi?", "ru": "Насчёт завтрашнего собрания, как думаешь, все согласятся?", "tj": "Дар бораи ҷалсаи фардо, ба фикри шумо ҳама розӣ мешаванд?"},
                {"speaker": "B", "zh": "我相信他们会同意的！只要你好好解释，就没问题！", "pinyin": "Wǒ xiāngxìn tāmen huì tóngyì de! Zhǐyào nǐ hǎohǎo jiěshì, jiù méi wèntí!", "uz": "Ularning rozi bo'lishiga ishonaman! Faqat yaxshilab tushuntirsangiz, muammo yo'q!", "ru": "Я верю, что они согласятся! Только хорошо объясни, и проблем не будет!", "tj": "Ман боварам дорам, ки онҳо розӣ мешаванд! Танҳо хуб шарҳ диҳед, мушкиле нест!"},
                {"speaker": "A", "zh": "好，我会好好准备关于计划的说明。", "pinyin": "Hǎo, wǒ huì hǎohǎo zhǔnbèi guānyú jìhuà de shuōmíng.", "uz": "Yaxshi, men reja haqidagi tushuntirishni yaxshilab tayyorlayman.", "ru": "Хорошо, я хорошо подготовлю объяснение о плане.", "tj": "Хуб, ман шарҳи нақшаро хуб тайёр мекунам."},
                {"speaker": "B", "zh": "只要你努力，一定会成功的！", "pinyin": "Zhǐyào nǐ nǔlì, yīdìng huì chénggōng de!", "uz": "Faqat harakat qilsangiz, albatta muvaffaqiyat qozonasiz!", "ru": "Только старайся, обязательно добьёшься успеха!", "tj": "Танҳо кӯшиш кунед, албатта муваффақ мешавед!"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Tadbir haqida gaplashish", "ru": "Разговор о мероприятии", "tj": "Суҳбат дар бораи тадбир"},
            "dialogue": [
                {"speaker": "A", "zh": "关于这次活动，你有什么想法？", "pinyin": "Guānyú zhè cì huódòng, nǐ yǒu shénme xiǎngfǎ?", "uz": "Bu tadbir haqida qanday fikrlaringiz bor?", "ru": "Насчёт этого мероприятия, какие у тебя мысли?", "tj": "Дар бораи ин тадбир, чӣ фикр доред?"},
                {"speaker": "B", "zh": "我觉得不但要邀请同学，而且还要邀请老师！", "pinyin": "Wǒ juéde búdàn yào yāoqǐng tóngxué, érqiě hái yào yāoqǐng lǎoshī!", "uz": "Menimcha, nafaqat sinfdoshlarni, balki o'qituvchilarni ham taklif qilish kerak!", "ru": "Я думаю, нужно пригласить не только одноклассников, но и учителей!", "tj": "Ба фикрам, на танҳо ҳамсинфонро, балки муаллимонро ҳам даъват кардан лозим аст!"},
                {"speaker": "A", "zh": "好主意！只要大家参加，活动就会成功！", "pinyin": "Hǎo zhǔyì! Zhǐyào dàjiā cānjiā, huódòng jiù huì chénggōng!", "uz": "Zo'r fikr! Faqat hamma qatnashsa, tadbir muvaffaqiyatli bo'ladi!", "ru": "Отличная идея! Только бы все участвовали, мероприятие будет успешным!", "tj": "Ғояи олӣ! Танҳо ҳама иштирок кунанд, тадбир муваффақ мешавад!"},
                {"speaker": "B", "zh": "不但要成功，而且要让大家都开心！", "pinyin": "Búdàn yào chénggōng, érqiě yào ràng dàjiā dōu kāixīn!", "uz": "Nafaqat muvaffaqiyatli, balki hammani xursand qilish kerak!", "ru": "Нужно не только добиться успеха, но и сделать всех счастливыми!", "tj": "На танҳо бояд муваффақ шавем, балки ҳамаро хурсанд кунем!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Xitoy tili kurslari haqida", "ru": "О курсах китайского языка", "tj": "Дар бораи курсҳои забони чинӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "关于汉语课，你有什么建议？", "pinyin": "Guānyú Hànyǔ kè, nǐ yǒu shénme jiànyì?", "uz": "Xitoy tili kurslari haqida qanday takliflaringiz bor?", "ru": "Насчёт курсов китайского, какие у тебя предложения?", "tj": "Дар бораи курсҳои забони чинӣ, чӣ пешниҳод доред?"},
                {"speaker": "B", "zh": "只要你每天练习，汉语就会越来越好！", "pinyin": "Zhǐyào nǐ měitiān liànxí, Hànyǔ jiù huì yuè lái yuè hǎo!", "uz": "Faqat har kuni mashq qilsangiz, xitoy tilingiz tobora yaxshilanadi!", "ru": "Только занимайся каждый день, китайский будет становиться всё лучше!", "tj": "Танҳо ҳар рӯз машқ кунед, забони чиниатон рӯз ба рӯз беҳтар мешавад!"},
                {"speaker": "A", "zh": "这门课不但有用，而且很有意思！", "pinyin": "Zhè mén kè búdàn yǒuyòng, érqiě hěn yǒu yìsi!", "uz": "Bu kurs nafaqat foydali, balki juda qiziqarli ham!", "ru": "Этот курс не только полезный, но и очень интересный!", "tj": "Ин курс на танҳо муфид, балки хеле ҷолиб ҳам аст!"},
                {"speaker": "B", "zh": "我也相信你会不但学好汉语，而且爱上中国文化！", "pinyin": "Wǒ yě xiāngxìn nǐ huì búdàn xué hǎo Hànyǔ, érqiě ài shàng Zhōngguó wénhuà!", "uz": "Men ham ishonaman, siz nafaqat xitoy tilini yaxshi o'rgandingiz, balki xitoy madaniyatiga ham oshiq bo'lasiz!", "ru": "Я тоже верю, что ты не только выучишь хорошо китайский, но и полюбишь китайскую культуру!", "tj": "Ман ҳам боварам дорам, ки шумо на танҳо забони чиниро хуб меомӯзед, балки ба фарҳанги чинӣ ҳам ошиқ мешавед!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Muvaffaqiyat haqida", "ru": "Об успехе", "tj": "Дар бораи муваффақият"},
            "dialogue": [
                {"speaker": "A", "zh": "关于你的成功，你有什么秘诀？", "pinyin": "Guānyú nǐ de chénggōng, nǐ yǒu shénme mìjué?", "uz": "Muvaffaqiyatingiz haqida, sirrningiz nima?", "ru": "Насчёт вашего успеха, в чём ваш секрет?", "tj": "Дар бораи муваффақияти шумо, рози шумо чист?"},
                {"speaker": "B", "zh": "只要你相信自己，就能成功！", "pinyin": "Zhǐyào nǐ xiāngxìn zìjǐ, jiù néng chénggōng!", "uz": "Faqat o'zingizga ishonsangiz, muvaffaqiyat qozonasiz!", "ru": "Только верь в себя, и добьёшься успеха!", "tj": "Танҳо ба худатон боварӣ дошта бошед, муваффақ мешавед!"},
                {"speaker": "A", "zh": "不但要相信自己，而且还要努力工作！", "pinyin": "Búdàn yào xiāngxìn zìjǐ, érqiě hái yào nǔlì gōngzuò!", "uz": "Nafaqat o'ziga ishonish, balki ham qattiq ishlash kerak!", "ru": "Нужно не только верить в себя, но и усердно работать!", "tj": "На танҳо ба худ боварӣ доштан, балки ҳам сахт кор кардан лозим аст!"},
                {"speaker": "B", "zh": "对！我相信只要努力，一定会成功！", "pinyin": "Duì! Wǒ xiāngxìn zhǐyào nǔlì, yīdìng huì chénggōng!", "uz": "To'g'ri! Faqat harakat qilsa, albatta muvaffaqiyat qozonadi deb ishonaman!", "ru": "Верно! Я верю, что только стараясь, обязательно добьёшься успеха!", "tj": "Дуруст! Ман боварам дорам, ки танҳо кӯшиш карда, албатта муваффақ мешавед!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "只要……就……",
            "title_uz": "Faqat……bo'lsa/qilsa……",
            "title_ru": "Только если……то……",
            "title_tj": "Танҳо агар……пас……",
            "rule_uz": "'只要…就…' tuzilmasi shartni ifodalaydi, lekin '如果' dan farqli ravishda '只要' = 'faqat shu shart bajarilsa bo'ladi, boshqa narsa kerak emas' ma'nosini bildiradi. Yengilroq va optimistik shart.",
            "rule_ru": "Конструкция '只要…就…' выражает условие, но в отличие от '如果', '只要' = 'достаточно выполнить только это условие, ничего другого не нужно'. Более лёгкое и оптимистичное условие.",
            "rule_tj": "Сохтори '只要…就…' шартро ифода мекунад, аммо баръакси '如果', '只要' = 'танҳо ин шарт иҷро шавад, дигар ҳеҷ чиз лозим нест' маъно медиҳад. Шарти осонтар ва хушбинонатар.",
            "examples": [
                {"zh": "只要你努力，就能成功！", "pinyin": "Zhǐyào nǐ nǔlì, jiù néng chénggōng!", "uz": "Faqat harakat qilsangiz, muvaffaqiyat qozonasiz!", "ru": "Только старайся, и добьёшься успеха!", "tj": "Танҳо кӯшиш кунед, муваффақ мешавед!"},
                {"zh": "只要大家参加，活动就会成功！", "pinyin": "Zhǐyào dàjiā cānjiā, huódòng jiù huì chénggōng!", "uz": "Faqat hamma qatnashsa, tadbir muvaffaqiyatli bo'ladi!", "ru": "Только бы все участвовали, мероприятие будет успешным!", "tj": "Танҳо ҳама иштирок кунанд, тадбир муваффақ мешавад!"}
            ]
        },
        {
            "no": 2,
            "title_zh": "介词\"关于\"（关于 + N + ……）",
            "title_uz": "'关于' predlogi (关于 + ot + ...)",
            "title_ru": "Предлог '关于' (关于 + сущ. + ...)",
            "title_tj": "Пешоянди '关于' (关于 + исм + ...)",
            "rule_uz": "'关于' = haqida, to'g'risida. Tuzilma: 关于 + mavzu + gapning qolgan qismi. Gap boshida yoki sub'ektdan keyin kelishi mumkin. Ingilizcha 'about / regarding' ga o'xshaydi.",
            "rule_ru": "'关于' = о, насчёт, относительно. Структура: 关于 + тема + остаток предложения. Может стоять в начале предложения или после подлежащего. Похоже на английское 'about / regarding'.",
            "rule_tj": "'关于' = дар бораи, оид ба. Сохтор: 关于 + мавзӯ + қисми боқии ҷумла. Дар аввали ҷумла ё баъди мубтадо омада метавонад. Ба 'about / regarding'-и инглисӣ монанд аст.",
            "examples": [
                {"zh": "关于这次活动，你有什么想法？", "pinyin": "Guānyú zhè cì huódòng, nǐ yǒu shénme xiǎngfǎ?", "uz": "Bu tadbir haqida qanday fikrlaringiz bor?", "ru": "Насчёт этого мероприятия, какие у тебя мысли?", "tj": "Дар бораи ин тадбир, чӣ фикр доред?"},
                {"zh": "我写了一篇关于健康的文章。", "pinyin": "Wǒ xiě le yī piān guānyú jiànkāng de wénzhāng.", "uz": "Men sog'liq haqida bir maqola yozdim.", "ru": "Я написал статью о здоровье.", "tj": "Ман мақолае дар бораи саломатӣ навиштам."}
            ]
        },
        {
            "no": 3,
            "title_zh": "不但……而且……",
            "title_uz": "Nafaqat……balki ham……",
            "title_ru": "Не только……но и……",
            "title_tj": "На танҳо……балки ҳам……",
            "rule_uz": "'不但…而且…' tuzilmasi ikkita ijobiy holatni kuchaytirib bog'laydi. '不但' = nafaqat, '而且' = balki ham. Birinchi jumladan ikkinchisi yanada kuchli yoki qo'shimcha ma'no qo'shadi.",
            "rule_ru": "Конструкция '不但…而且…' усиленно соединяет два положительных факта. '不但' = не только, '而且' = но и. Второе предложение добавляет ещё более сильный или дополнительный смысл.",
            "rule_tj": "Сохтори '不但…而且…' ду ҳолати мусбатро бо таъкид мепайвандад. '不但' = на танҳо, '而且' = балки ҳам. Ҷумлаи дуввум маъноеро ҳам қавитар ё иловагӣ илова мекунад.",
            "examples": [
                {"zh": "这门课不但有用，而且很有意思！", "pinyin": "Zhè mén kè búdàn yǒuyòng, érqiě hěn yǒu yìsi!", "uz": "Bu kurs nafaqat foydali, balki juda qiziqarli ham!", "ru": "Этот курс не только полезный, но и очень интересный!", "tj": "Ин курс на танҳо муфид, балки хеле ҷолиб ҳам аст!"},
                {"zh": "他不但会说汉语，而且还会说日语！", "pinyin": "Tā búdàn huì shuō Hànyǔ, érqiě hái huì shuō Rìyǔ!", "uz": "U nafaqat xitoy tilini, balki yapon tilini ham biladi!", "ru": "Он умеет говорить не только по-китайски, но и по-японски!", "tj": "Вай на танҳо чинӣ, балки ба ҷопонӣ ҳам гап мезанад!"}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Faqat harakat qilsangiz, muvaffaqiyat qozonasiz!", "ru": "Только старайся, и добьёшься успеха!", "tj": "Танҳо кӯшиш кунед, муваффақ мешавед!"},
                {"no": 2, "uz": "Bu tadbir haqida qanday fikrlaringiz bor?", "ru": "Насчёт этого мероприятия, какие у тебя мысли?", "tj": "Дар бораи ин тадбир, чӣ фикр доред?"},
                {"no": 3, "uz": "Bu kurs nafaqat foydali, balki juda qiziqarli ham!", "ru": "Этот курс не только полезный, но и очень интересный!", "tj": "Ин курс на танҳо муфид, балки хеле ҷолиб ҳам аст!"},
                {"no": 4, "uz": "Men sog'liq haqida bir maqola yozdim.", "ru": "Я написал статью о здоровье.", "tj": "Ман мақолае дар бораи саломатӣ навиштам."},
                {"no": 5, "uz": "U nafaqat xitoy tilini, balki yapon tilini ham biladi!", "ru": "Он умеет говорить не только по-китайски, но и по-японски!", "tj": "Вай на танҳо чинӣ, балки ба ҷопонӣ ҳам гап мезанад!"}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "只要你努力，___能成功！", "sentence_uz": "Faqat harakat qilsangiz, ___ muvaffaqiyat qozonasiz!", "sentence_ru": "Только старайся, ___ добьёшься успеха!", "sentence_tj": "Танҳо кӯшиш кунед, ___ муваффақ мешавед!", "hint": "就"},
                {"no": 2, "sentence_zh": "___这次活动，你有什么想法？", "sentence_uz": "Bu tadbir ___, qanday fikrlaringiz bor?", "sentence_ru": "___ этого мероприятия, какие у тебя мысли?", "sentence_tj": "___ ин тадбир, чӣ фикр доред?", "hint": "关于"},
                {"no": 3, "sentence_zh": "这门课___有用，___很有意思！", "sentence_uz": "Bu kurs ___ foydali, ___ juda qiziqarli!", "sentence_ru": "Этот курс ___ полезный, ___ очень интересный!", "sentence_tj": "Ин курс ___ муфид, ___ хеле ҷолиб!", "hint": "不但…而且"},
                {"no": 4, "sentence_zh": "我___他们会同意___！", "sentence_uz": "Ularning rozi bo'lishiga ___!", "sentence_ru": "Я верю, что они ___!", "sentence_tj": "Ман ___ онҳо розӣ ___ боварам дорам!", "hint": "相信……的"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "不但要相信自己，而且还要努力工作！", "pinyin": "Búdàn yào xiāngxìn zìjǐ, érqiě hái yào nǔlì gōngzuò!"},
                {"no": 2, "zh": "只要你相信自己，就一定能成功！", "pinyin": "Zhǐyào nǐ xiāngxìn zìjǐ, jiù yīdìng néng chénggōng!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "只要你努力，就能成功！"},
                {"no": 2, "zh": "关于这次活动，你有什么想法？"},
                {"no": 3, "zh": "这门课不但有用，而且很有意思！"},
                {"no": 4, "zh": "我写了一篇关于健康的文章。"},
                {"no": 5, "zh": "他不但会说汉语，而且还会说日语！"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "就"},
                {"no": 2, "answer": "关于"},
                {"no": 3, "answer": "不但…而且"},
                {"no": 4, "answer": "相信……的"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Nafaqat o'ziga ishonish, balki ham qattiq ishlash kerak!", "ru": "Нужно не только верить в себя, но и усердно работать!", "tj": "На танҳо ба худ боварӣ доштан, балки ҳам сахт кор кардан лозим аст!"},
                {"no": 2, "uz": "Faqat o'zingizga ishonsangiz, albatta muvaffaqiyat qozonasiz!", "ru": "Только верь в себя, и обязательно добьёшься успеха!", "tj": "Танҳо ба худатон боварӣ дошта бошед, албатта муваффақ мешавед!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'只要…就…' va '不但…而且…' iboralarini ishlatib, o'zingiz va do'stlaringiz haqida 4 ta jumla yozing.", "ru": "Напишите 4 предложения о себе и своих друзьях, используя '只要…就…' и '不但…而且…'.", "tj": "4 ҷумла дар бораи худ ва дӯстонатон бо '只要…就…' ва '不但…而且…' нависед."},
        {"task_no": 2, "uz": "'关于' predlogini ishlatib, o'z qiziqishlaringiz yoki ish haqida 3 ta jumla tuzing.", "ru": "Составьте 3 предложения о своих интересах или работе, используя предлог '关于'.", "tj": "3 ҷумла дар бораи шавқҳои худ ё кор бо пешоянди '关于' тартиб диҳед."}
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
