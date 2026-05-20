import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 20,
    "lesson_code": "HSK3-L20",
    "title": json.dumps({"zh": "我被他影响了", "uz": "U meni ta'sirlantirdi", "ru": "Он повлиял на меня", "tj": "Вай ба ман таъсир кард"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "'被' passiv konstruktsiya, '只有…才…' shartli gap va '多么…啊' hayrat undalmasi", "ru": "Пассивная конструкция '被', условное '只有…才…' и восклицание '多么…啊'", "tj": "Сохтори пассивии '被', шартии '只有…才…' ва ندای тааҷубии '多么…啊'"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu oxirgi darsda '被'-konstruktsiyasi (passiv gap), '只有…才…' (faqatgina…bo'lganda) va '多么…啊' (qanchalik…!) hayrat iboralarini o'rganamiz.", "ru": "В этом последнем уроке мы изучим конструкцию '被' (пассивный залог), '只有…才…' (только когда…) и восклицательное выражение '多么…啊' (как …!).", "tj": "Дар ин дарси охирин мо сохтори '被' (замони маҷҳул), '只有…才…' (танҳо вақте ки…) ва ибораи тааҷубии '多么…啊' (чӣ қадар…!)-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "影响", "pinyin": "yǐngxiǎng", "pos": "v/n", "uz": "ta'sir qilmoq; ta'sir", "ru": "влиять; влияние", "tj": "таъсир расондан; таъсир"},
        {"no": 2, "zh": "被", "pinyin": "bèi", "pos": "prep", "uz": "tomonidan (passiv belgisi)", "ru": "частица пассивного залога", "tj": "нишондиҳандаи замони маҷҳул"},
        {"no": 3, "zh": "只有", "pinyin": "zhǐyǒu", "pos": "conj", "uz": "faqatgina; faqat shunday bo'lganda", "ru": "только; лишь в этом случае", "tj": "танҳо; фақат ин тавр"},
        {"no": 4, "zh": "多么", "pinyin": "duōme", "pos": "adv", "uz": "qanchalik, naqadar (hayrat)", "ru": "как, насколько (восклицание)", "tj": "чӣ қадар (тааҷуб)"},
        {"no": 7, "zh": "感动", "pinyin": "gǎndòng", "pos": "v/adj", "uz": "ta'sirlantirmoq; ta'sirlangan", "ru": "трогать, растрогать; тронутый", "tj": "мутаассир кардан; мутаассир"},
        {"no": 5, "zh": "批评", "pinyin": "pīpíng", "pos": "v/n", "uz": "tanqid qilmoq; tanqid", "ru": "критиковать; критика", "tj": "танқид кардан; танқид"},
        {"no": 6, "zh": "表扬", "pinyin": "biǎoyáng", "pos": "v/n", "uz": "maqtamoq; maqtov", "ru": "хвалить; похвала", "tj": "мақтамоқ; мақтов"},
        {"no": 8, "zh": "打败", "pinyin": "dǎ bài", "pos": "v", "uz": "yengmoq, mag'lubiyatga uchratmoq", "ru": "побеждать, разбивать", "tj": "шикаст додан, мағлуб кардан"},
        {"no": 9, "zh": "吸引", "pinyin": "xīyǐn", "pos": "v", "uz": "jalb qilmoq, o'ziga tortmoq", "ru": "привлекать, притягивать", "tj": "ҷалб кардан, ба худ кашидан"},
        {"no": 10, "zh": "激励", "pinyin": "jīlì", "pos": "v", "uz": "ilhomlantirmoq, rag'batlantirmoq", "ru": "вдохновлять, поощрять", "tj": "илҳом бахшидан, ташвиқ кардан"},
        {"no": 11, "zh": "感谢", "pinyin": "gǎnxiè", "pos": "v/n", "uz": "minnatdorlik bildirmoq; minnatdorlik", "ru": "благодарить; благодарность", "tj": "миннатдорӣ изҳор кардан; миннатдорӣ"},
        {"no": 12, "zh": "宝贵", "pinyin": "bǎoguì", "pos": "adj", "uz": "qimmatli, bebaho", "ru": "ценный, драгоценный", "tj": "қиматбаҳо, гаронбаҳо"},
        {"no": 13, "zh": "经历", "pinyin": "jīnglì", "pos": "n/v", "uz": "tajriba; boshdan kechirmoq", "ru": "опыт; пережить, испытать", "tj": "таҷриба; аз сар гузаронидан"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Ta'sir va ilhom haqida", "ru": "О влиянии и вдохновении", "tj": "Дар бораи таъсир ва илҳом"},
            "dialogue": [
                {"speaker": "A", "zh": "你为什么开始学音乐的？", "pinyin": "Nǐ wèishénme kāishǐ xué yīnyuè de?", "uz": "Nima uchun musiqa o'rganishni boshladingiz?", "ru": "Почему ты начал учить музыку?", "tj": "Чаро шумо мусиқӣ омӯхтанро оғоз кардед?"},
                {"speaker": "B", "zh": "我被他影响了！他演奏得多么精彩啊！", "pinyin": "Wǒ bèi tā yǐngxiǎng le! Tā yǎnzòu de duōme jīngcǎi a!", "uz": "U meni ta'sirlantirdi! Uning ijrosi qanchalik ajoyib edi!", "ru": "Он повлиял на меня! Как замечательно он играл!", "tj": "Вай ба ман таъсир кард! Иҷрои вай чӣ қадар зебо буд!"},
                {"speaker": "A", "zh": "只有像他那样练习，才能弹得那么好！", "pinyin": "Zhǐyǒu xiàng tā nàyàng liànxí, cái néng tán de nàme hǎo!", "uz": "Faqat u kabi mashq qilsangizgina, shunchalik yaxshi chala olasiz!", "ru": "Только тренируясь так, как он, можно играть так хорошо!", "tj": "Танҳо ба монанди вай машқ карданатон, ин қадар хуб навохта метавонед!"},
                {"speaker": "B", "zh": "是的！我被他激励了，每天都努力练习！", "pinyin": "Shì de! Wǒ bèi tā jīlì le, měitiān dōu nǔlì liànxí!", "uz": "Ha! U meni ilhomlantirdi, men har kuni qattiq mashq qilaman!", "ru": "Да! Он меня вдохновил, я каждый день усердно тренируюсь!", "tj": "Ҳа! Вай маро илҳом бахшид, ман ҳар рӯз сахт машқ мекунам!"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Tanqid va maqtov", "ru": "Критика и похвала", "tj": "Танқид ва мақтов"},
            "dialogue": [
                {"speaker": "A", "zh": "你今天被老师表扬了吗？", "pinyin": "Nǐ jīntiān bèi lǎoshī biǎoyáng le ma?", "uz": "Bugun o'qituvchi sizni maqtadimi?", "ru": "Сегодня учитель тебя похвалил?", "tj": "Имрӯз муаллим шуморо мақтод?"},
                {"speaker": "B", "zh": "没有，反而被批评了！多么难受啊！", "pinyin": "Méiyǒu, fǎn'ér bèi pīpíng le! Duōme nánshòu a!", "uz": "Yo'q, aksincha tanqid qilindi! Qanchalik yomon his etildi!", "ru": "Нет, наоборот, его критиковали! Как неприятно!", "tj": "Не, баракс танқид шуд! Чӣ қадар нохуш!"},
                {"speaker": "A", "zh": "只有被批评了，才能知道哪里需要改进！", "pinyin": "Zhǐyǒu bèi pīpíng le, cái néng zhīdào nǎlǐ xūyào gǎijìn!", "uz": "Faqat tanqid qilingandagina, qayerda yaxshilash kerakligini bilish mumkin!", "ru": "Только получив критику, можно узнать, где нужно улучшиться!", "tj": "Танҳо вақте танқид шавед, медонед куҷо бояд беҳтар кунед!"},
                {"speaker": "B", "zh": "你说得对，多么宝贵的经历啊！", "pinyin": "Nǐ shuō de duì, duōme bǎoguì de jīnglì a!", "uz": "Siz to'g'ri aytdingiz, qanchalik qimmatli tajriba!", "ru": "Ты прав, как ценный опыт!", "tj": "Шумо дуруст гуфтед, чӣ қадар таҷрибаи гаронбаҳо!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Musobaqa", "ru": "Соревнование", "tj": "Мусобақа"},
            "dialogue": [
                {"speaker": "A", "zh": "比赛结果怎么样？", "pinyin": "Bǐsài jiéguǒ zěnme yàng?", "uz": "Musobaqa natijasi qanday?", "ru": "Каков результат соревнования?", "tj": "Натиҷаи мусобақа чӣ тавр аст?"},
                {"speaker": "B", "zh": "我们被对方打败了！多么可惜啊！", "pinyin": "Wǒmen bèi duìfāng dǎ bài le! Duōme kěxī a!", "uz": "Biz raqiblar tomonidan yengilib qoldik! Qanchalik achinarlisi!", "ru": "Нас победила другая команда! Как жаль!", "tj": "Мо аз тарафи рақибон шикаст хӯрдем! Чӣ қадар ҳайф!"},
                {"speaker": "A", "zh": "只有经历失败，才能变得更强！", "pinyin": "Zhǐyǒu jīnglì shībài, cái néng biàn de gèng qiáng!", "uz": "Faqat mag'lubiyatni boshdan kechirganingizda, kuchliroq bo'la olasiz!", "ru": "Только пережив поражение, можно стать сильнее!", "tj": "Танҳо вақте шикастро аз сар гузаронед, метавонед қавитар шавед!"},
                {"speaker": "B", "zh": "对！被打败了也没关系，我们被激励了！", "pinyin": "Duì! Bèi dǎ bài le yě méi guānxi, wǒmen bèi jīlì le!", "uz": "Ha! Yengilganimiz ham mayli, biz ilhomlankandik!", "ru": "Верно! Пусть проиграли, мы были вдохновлены!", "tj": "Ҳа! Шикаст хӯрдем ҳам майлаш, мо илҳом гирифтем!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "O'qituvchiga minnatdorlik", "ru": "Благодарность учителю", "tj": "Миннатдорӣ ба муаллим"},
            "dialogue": [
                {"speaker": "A", "zh": "老师，我被您影响了，多么感谢啊！", "pinyin": "Lǎoshī, wǒ bèi nín yǐngxiǎng le, duōme gǎnxiè a!", "uz": "O'qituvchi, siz meni ta'sirlantirdingiz, qanchalik minnatdorman!", "ru": "Учитель, вы повлияли на меня, как я благодарен!", "tj": "Муаллим, шумо ба ман таъсир кардед, чӣ қадар миннатдорам!"},
                {"speaker": "B", "zh": "只有你自己努力，才能有今天的成绩！", "pinyin": "Zhǐyǒu nǐ zìjǐ nǔlì, cái néng yǒu jīntiān de chéngjì!", "uz": "Faqat o'zingizning harakat qilishingiz tufaylida bugungi natijangiz bor!", "ru": "Только благодаря твоим собственным усилиям — сегодняшние результаты!", "tj": "Танҳо бо кӯшиши худатон — натиҷаҳои имрӯза мавҷуданд!"},
                {"speaker": "A", "zh": "我被您的话感动了，多么宝贵的教导啊！", "pinyin": "Wǒ bèi nín de huà gǎndòng le, duōme bǎoguì de jiàodǎo a!", "uz": "Sizning so'zlaringiz meni ta'sirlantirdi, qanchalik qimmatli nasihat!", "ru": "Ваши слова меня тронули, как ценное наставление!", "tj": "Суханони шумо маро мутаассир кард, чӣ қадар дарси гаронбаҳо!"},
                {"speaker": "B", "zh": "加油！多么美好的未来在等着你啊！", "pinyin": "Jiāyóu! Duōme měihǎo de wèilái zài děngzhe nǐ a!", "uz": "Davom eting! Qanchalik ajoyib kelajak sizi kutmoqda!", "ru": "Не сдавайся! Как прекрасное будущее тебя ждёт!", "tj": "Идома диҳед! Чӣ қадар ояндаи зебо шуморо интизор аст!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "被字句：被 + 施事者 + 动词（被动句）",
            "title_uz": "被-konstruktsiya: 被 + harakat bajaruvchi + fe'l (passiv gap)",
            "title_ru": "Конструкция 被: 被 + деятель + глагол (пассивный залог)",
            "title_tj": "Сохтори 被: 被 + иҷрогар + феъл (замони маҷҳул)",
            "rule_uz": "'被'-konstruktsiya passiv gaplarni ifodalaydi. Tuzilma: sub'ekt (ob'ekt) + 被 + harakat bajaruvchi + fe'l. Ko'pincha noxush hodisalarda ishlatiladi, lekin ijobiy hodisalar uchun ham mumkin. Harakat bajaruvchi tushirilishi mumkin.",
            "rule_ru": "Конструкция '被' выражает пассивный залог. Структура: субъект (объект) + 被 + деятель + глагол. Часто используется при неприятных событиях, но возможна и для позитивных. Деятель может быть опущен.",
            "rule_tj": "Сохтори '被' замони маҷҳулро ифода мекунад. Сохтор: мубтадо (объект) + 被 + иҷрогар + феъл. Зиёдтар дар ҳодисаҳои нохуш истифода мешавад, аммо барои мусбат ҳам мумкин. Иҷрогар партофта шавад мешавад.",
            "examples": [
                {"zh": "我被他影响了！", "pinyin": "Wǒ bèi tā yǐngxiǎng le!", "uz": "U meni ta'sirlantirdi!", "ru": "Он повлиял на меня!", "tj": "Вай ба ман таъсир кард!"},
                {"zh": "他被老师批评了。", "pinyin": "Tā bèi lǎoshī pīpíng le.", "uz": "Uni o'qituvchi tanqid qildi.", "ru": "Его покритиковал учитель.", "tj": "Вайро муаллим танқид кард."}
            ]
        },
        {
            "no": 2,
            "title_zh": "只有……才……",
            "title_uz": "Faqat……bo'lgandagina……mumkin",
            "title_ru": "Только……тогда только……",
            "title_tj": "Танҳо……вақте ки……мумкин аст",
            "rule_uz": "'只有…才…' = biror shart faqat shu tarzda bajarilsa, natijaga erishish mumkin. '只要…就…' dan farqi: '只有' kuchliroq shart, bitta to'g'ri yo'l bor; '只要' = yetarli shart, boshqa yo'llar ham mumkin.",
            "rule_ru": "'只有…才…' = результат возможен только при выполнении именно этого условия. Отличие от '只要…就…': '只有' — более строгое условие, только один правильный путь; '只要' — достаточное условие, другие пути тоже возможны.",
            "rule_tj": "'只有…才…' = натиҷа танҳо ҳангоми иҷрои маҳз ин шарт имконпазир аст. Фарқ аз '只要…就…': '只有' — шарти қатъитар, танҳо як роҳи дуруст; '只要' — шарти кофӣ, роҳҳои дигар ҳам мумкин.",
            "examples": [
                {"zh": "只有经历失败，才能变得更强！", "pinyin": "Zhǐyǒu jīnglì shībài, cái néng biàn de gèng qiáng!", "uz": "Faqat mag'lubiyatni boshdan kechirganingizda, kuchliroq bo'la olasiz!", "ru": "Только пережив поражение, можно стать сильнее!", "tj": "Танҳо вақте шикастро аз сар гузаронед, метавонед қавитар шавед!"},
                {"zh": "只有努力学习，才能考上大学。", "pinyin": "Zhǐyǒu nǔlì xuéxí, cái néng kǎo shàng dàxué.", "uz": "Faqat qattiq o'qisangizgina, universitetga kira olasiz.", "ru": "Только усердно учась, можно поступить в университет.", "tj": "Танҳо сахт омӯхтан имкон медиҳад ба донишгоҳ дохил шавед."}
            ]
        },
        {
            "no": 3,
            "title_zh": "多么……啊！（感叹句）",
            "title_uz": "Qanchalik……! (hayrat undalmasi)",
            "title_ru": "Как……! (восклицательное предложение)",
            "title_tj": "Чӣ қадар……! (ҷумлаи тааҷубӣ)",
            "rule_uz": "'多么…啊！' tuzilmasi kuchli his-tuyg'u, hayrat yoki quvonchni ifodalaydi. Tuzilma: 多么 + sifat/holat + 啊！ Ingilizcha 'How …!' ga o'xshaydi. Og'zaki nutqda '啊' o'rniga '呀' ishlatilishi mumkin.",
            "rule_ru": "Конструкция '多么…啊！' выражает сильные эмоции, восхищение или радость. Структура: 多么 + прилагательное/состояние + 啊！ Похоже на английское 'How …!'. В разговорной речи '啊' может заменяться на '呀'.",
            "rule_tj": "Сохтори '多么…啊！' эҳсосоти қавӣ, тааҷуб ё шодиро ифода мекунад. Сохтор: 多么 + сифат/ҳол + 啊！ Ба 'How …!'-и инглисӣ монанд. Дар забони гуфторӣ '啊' ба '呀' иваз шуда метавонад.",
            "examples": [
                {"zh": "多么美好的未来在等着你啊！", "pinyin": "Duōme měihǎo de wèilái zài děngzhe nǐ a!", "uz": "Qanchalik ajoyib kelajak sizi kutmoqda!", "ru": "Как прекрасное будущее тебя ждёт!", "tj": "Чӣ қадар ояндаи зебо шуморо интизор аст!"},
                {"zh": "多么宝贵的经历啊！", "pinyin": "Duōme bǎoguì de jīnglì a!", "uz": "Qanchalik qimmatli tajriba!", "ru": "Как ценный опыт!", "tj": "Чӣ қадар таҷрибаи гаронбаҳо!"}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "U meni ta'sirlantirdi!", "ru": "Он повлиял на меня!", "tj": "Вай ба ман таъсир кард!"},
                {"no": 2, "uz": "Faqat qattiq o'qisangizgina, universitetga kira olasiz.", "ru": "Только усердно учась, можно поступить в университет.", "tj": "Танҳо сахт омӯхтан имкон медиҳад ба донишгоҳ дохил шавед."},
                {"no": 3, "uz": "Qanchalik qimmatli tajriba!", "ru": "Как ценный опыт!", "tj": "Чӣ қадар таҷрибаи гаронбаҳо!"},
                {"no": 4, "uz": "Uni o'qituvchi tanqid qildi.", "ru": "Его покритиковал учитель.", "tj": "Вайро муаллим танқид кард."},
                {"no": 5, "uz": "Faqat mag'lubiyatni boshdan kechirganingizda, kuchliroq bo'la olasiz!", "ru": "Только пережив поражение, можно стать сильнее!", "tj": "Танҳо вақте шикастро аз сар гузаронед, метавонед қавитар шавед!"}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "我___他影响了！", "sentence_uz": "U meni ___lantirdi!", "sentence_ru": "Он ___ меня повлиял!", "sentence_tj": "Вай ба ман ___ кард!", "hint": "被"},
                {"no": 2, "sentence_zh": "只有努力学习，___能考上大学。", "sentence_uz": "Faqat qattiq o'qisangizgina, ___ universitetga kira olasiz.", "sentence_ru": "Только усердно учась, ___ поступить в университет.", "sentence_tj": "Танҳо сахт омӯхтан ___ ба донишгоҳ дохил шавед.", "hint": "才"},
                {"no": 3, "sentence_zh": "___美好的未来在等着你啊！", "sentence_uz": "___ ajoyib kelajak sizi kutmoqda!", "sentence_ru": "___ прекрасное будущее тебя ждёт!", "sentence_tj": "___ ояндаи зебо шуморо интизор аст!", "hint": "多么"},
                {"no": 4, "sentence_zh": "他___老师表扬了！", "sentence_uz": "Uni o'qituvchi ___!", "sentence_ru": "Его ___ учитель похвалил!", "sentence_tj": "Вайро муаллим ___!", "hint": "被"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "只有经历失败，才能变得更强！", "pinyin": "Zhǐyǒu jīnglì shībài, cái néng biàn de gèng qiáng!"},
                {"no": 2, "zh": "我被您的话感动了，多么宝贵的教导啊！", "pinyin": "Wǒ bèi nín de huà gǎndòng le, duōme bǎoguì de jiàodǎo a!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "我被他影响了！"},
                {"no": 2, "zh": "只有努力学习，才能考上大学。"},
                {"no": 3, "zh": "多么宝贵的经历啊！"},
                {"no": 4, "zh": "他被老师批评了。"},
                {"no": 5, "zh": "只有经历失败，才能变得更强！"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "被"},
                {"no": 2, "answer": "才"},
                {"no": 3, "answer": "多么"},
                {"no": 4, "answer": "被"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Faqat mag'lubiyatni boshdan kechirganingizda, kuchliroq bo'la olasiz!", "ru": "Только пережив поражение, можно стать сильнее!", "tj": "Танҳо вақте шикастро аз сар гузаронед, метавонед қавитар шавед!"},
                {"no": 2, "uz": "Sizning so'zlaringiz meni ta'sirlantirdi, qanchalik qimmatli nasihat!", "ru": "Ваши слова меня тронули, как ценное наставление!", "tj": "Суханони шумо маро мутаассир кард, чӣ қадар дарси гаронбаҳо!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'被'-konstruktsiyasidan foydalanib, hayotingizda bo'lgan 3 ta hodisani passiv shaklda yozing (ijobiy va salbiy ikkalasini ham qo'shing).", "ru": "Используя конструкцию '被', напишите 3 события из вашей жизни в пассивном залоге (включите и положительные, и отрицательные).", "tj": "Бо сохтори '被' 3 ҳодисаи ҳаётиатонро ба шакли маҷҳул нависед (ҳам мусбат ва ҳам манфӣ илова кунед)."},
        {"task_no": 2, "uz": "'只有…才…' va '多么…啊！' iboralarini ishlatib, o'z hayotiy tajribangiz haqida 3 ta jumla yozing va kurs davomida o'rgangan eng muhim narsani yozing.", "ru": "Напишите 3 предложения о вашем жизненном опыте с '只有…才…' и '多么…啊！', а также напишите самое важное, что узнали за этот курс.", "tj": "3 ҷумла дар бораи таҷрибаи ҳаётиатон бо '只有…才…' ва '多么…啊！' нависед ва муҳимтарин чизеро ки дар ин курс омӯхтед нависед."}
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
