import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 3,
    "lesson_code": "HSK4-L03",
    "title": "经理对我印象不错",
    "goal": json.dumps({"uz": "ish topish, suhbat va ish muhiti haqida gapirish; 越...越..., 本来, 另外, 首先...其次..., 不管 grammatik qoliplarini o'zlashtirish", "ru": "говорить о поиске работы, собеседовании и рабочей среде; освоить конструкции 越...越..., 本来, 另外, 首先...其次..., 不管", "tj": "гуфтугӯ дар бораи ёфтани кор, мусоҳиба ва муҳити кор; аз худ кардани қолипҳои 越...越..., 本来, 另外, 首先...其次..., 不管"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Menejer men haqimda yaxshi fikrda' mavzusiga bag'ishlangan. Unda ish intervyusi, ish topish va yangi ish joyiga ko'nikish haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 越...越..., 本来, 另外, 首先...其次..., 不管.", "ru": "Этот урок посвящён теме 'Менеджер хорошо обо мне думает'. В нём вы научитесь говорить о собеседовании, поиске работы и адаптации на новом месте. Основные грамматические конструкции: 越...越..., 本来, 另外, 首先...其次..., 不管.", "tj": "Ин дарс ба мавзӯи 'Мудир дар бораи ман фикри хуб дорад' бахшида шудааст. Дар он мусоҳибаи кор, ёфтани кор ва мутобиқ шудан дар ҷои нав омӯхта мешавад. Қолипҳои асосии грамматикӣ: 越...越..., 本来, 另外, 首先...其次..., 不管."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "挺", "pinyin": "tǐng", "pos": "adv.", "uz": "juda, ancha (og'zaki)", "ru": "очень, довольно (разговорное)", "tj": "хеле, кам-кам (забони гуфторӣ)"},
            {"no": 2, "zh": "紧张", "pinyin": "jǐnzhāng", "pos": "adj.", "uz": "asabiy, ta'sirchan, hayajonlangan", "ru": "нервный, взволнованный", "tj": "асабӣ, ҳаяҷонзада"},
            {"no": 3, "zh": "信心", "pinyin": "xìnxīn", "pos": "n.", "uz": "ishonch, o'ziga ishonch", "ru": "уверенность, вера в себя", "tj": "боварӣ, эътимод ба худ"},
            {"no": 4, "zh": "能力", "pinyin": "nénglì", "pos": "n.", "uz": "qobiliyat, mahorat", "ru": "способность, умение", "tj": "қобилият, маҳорат"},
            {"no": 5, "zh": "招聘", "pinyin": "zhāopìn", "pos": "v.", "uz": "ishchi yollash, xodim qidirish", "ru": "нанимать на работу, вербовать", "tj": "кормандро кор гирифтан, ба кор даъват кардан"},
            {"no": 6, "zh": "提供", "pinyin": "tígōng", "pos": "v.", "uz": "ta'minlamoq, bermoq", "ru": "предоставлять, обеспечивать", "tj": "таъмин кардан, додан"},
            {"no": 7, "zh": "负责", "pinyin": "fùzé", "pos": "v.", "uz": "mas'ul bo'lmoq, javobgarlikni o'z zimmasiga olmoq", "ru": "нести ответственность", "tj": "масъул будан, зиммадор будан"},
            {"no": 8, "zh": "本来", "pinyin": "běnlái", "pos": "adv.", "uz": "aslida, dastlab, oldindan", "ru": "изначально, на самом деле", "tj": "дар асл, аввалан"},
            {"no": 9, "zh": "应聘", "pinyin": "yìngpìn", "pos": "v.", "uz": "ish uchun murojaat qilmoq, intervyuga bormoq", "ru": "откликаться на вакансию, проходить собеседование", "tj": "барои кор мурољиат кардан, ба мусоҳиба рафтан"},
            {"no": 10, "zh": "材料", "pinyin": "cáiliào", "pos": "n.", "uz": "material, hujjat, ma'lumot", "ru": "материал, документ, информация", "tj": "мавод, ҳуҷҷат, маълумот"},
            {"no": 11, "zh": "符合", "pinyin": "fúhé", "pos": "v.", "uz": "mos kelmoq, muvofiq bo'lmoq", "ru": "соответствовать, отвечать требованиям", "tj": "мувофиқ будан, мутобиқ будан"},
            {"no": 12, "zh": "通知", "pinyin": "tōngzhī", "pos": "v./n.", "uz": "xabar bermoq; xabarnoma", "ru": "уведомлять; уведомление", "tj": "хабар додан; хабарнома"},
            {"no": 13, "zh": "越", "pinyin": "yuè", "pos": "adv.", "uz": "tobora, borgan sari", "ru": "всё более, с каждым разом", "tj": "ҳар чи бештар, рӯ ба рӯ"},
            {"no": 14, "zh": "另外", "pinyin": "lìngwài", "pos": "adv./conj.", "uz": "bundan tashqari, boshqacha", "ru": "кроме того, к тому же", "tj": "илова бар ин, ғайр аз ин"},
            {"no": 15, "zh": "首先", "pinyin": "shǒuxiān", "pos": "adv.", "uz": "avvalo, birinchi navbatda", "ru": "прежде всего, во-первых", "tj": "пеш аз ҳама, аввалан"},
            {"no": 16, "zh": "其次", "pinyin": "qícì", "pos": "adv.", "uz": "ikkinchidan, so'ngra", "ru": "во-вторых, затем", "tj": "дуввум, сипас"},
            {"no": 17, "zh": "不管", "pinyin": "bùguǎn", "pos": "conj.", "uz": "qanday bo'lmasin, nima bo'lsa ham", "ru": "независимо от, неважно что", "tj": "новобаста аз, ҳар чӣ ҳам бошад"},
            {"no": 18, "zh": "面试", "pinyin": "miànshì", "pos": "v./n.", "uz": "og'zaki suhbat o'tkazmoq; og'zaki suhbat", "ru": "проводить собеседование; собеседование", "tj": "мусоҳибаи шифоҳӣ гузаронидан; мусоҳибаи шифоҳӣ"},
            {"no": 19, "zh": "经验", "pinyin": "jīngyàn", "pos": "n.", "uz": "tajriba", "ru": "опыт", "tj": "таҷриба"},
            {"no": 20, "zh": "机会", "pinyin": "jīhuì", "pos": "n.", "uz": "imkoniyat, fursat", "ru": "возможность, шанс", "tj": "имконият, фурсат"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "小夏 va 小雨 ish suhbati haqida gaplashadi",
                "scene_ru": "小夏 и 小雨 обсуждают собеседование",
                "scene_tj": "小夏 ва 小雨 дар бораи мусоҳибаи кор гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "小夏", "zh": "你上午的面试怎么样？", "pinyin": "",
                     "uz": "Ertalabki suhbating qanday o'tdi?",
                     "ru": "Как прошло утреннее собеседование?",
                     "tj": "Мусоҳибаи субҳонии ту чӣ тавр гузашт?"},
                    {"speaker": "小雨", "zh": "还可以，他们问的问题都挺容易的，就是我有点儿紧张。", "pinyin": "",
                     "uz": "Yaxshi edi, berishgan savollar ancha oson edi, lekin men biroz asabiy bo'ldim.",
                     "ru": "Ничего, вопросы были довольно лёгкими, только я немного нервничал.",
                     "tj": "Кам-кам, саволҳои доданашон нисбатан осон буданд, фақат ман каме асабӣ шудам."},
                    {"speaker": "小夏", "zh": "面试的时候，一定要表现出自己有能力、有信心。", "pinyin": "",
                     "uz": "Suhbatda o'zingning qobiliyatli va ishonchli ekanligini ko'rsatish kerak.",
                     "ru": "На собеседовании обязательно нужно показать, что ты способный и уверенный.",
                     "tj": "Дар мусоҳиба ҳатман бояд нишон дод, ки қобилиятманд ва боэтимодӣ."},
                    {"speaker": "小雨", "zh": "这次招聘对我来说是个好机会，我们一起去看看吧，越了解越有信心。", "pinyin": "",
                     "uz": "Bu ishga yollash men uchun yaxshi imkoniyat, birga borib ko'ramiz, qancha ko'p bilsak, shuncha ko'p ishonch hosil qilamiz.",
                     "ru": "Эта вакансия для меня хорошая возможность, давай вместе посмотрим — чем больше знаешь, тем увереннее себя чувствуешь.",
                     "tj": "Ин кор гирифтан барои ман фурсати хуб аст, якҷоя бибинем — ҳар чи бештар бидонӣ, ҳамон қадар боэтимодтар мешавӣ."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "Menejer Ma va 小林 ishga yollash haqida gaplashadi",
                "scene_ru": "Менеджер Ма и 小林 обсуждают набор персонала",
                "scene_tj": "Мудир Ма ва 小林 дар бораи кор гирифтан гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "马经理", "zh": "林，这次招聘不是小事，你觉得应该怎么做？", "pinyin": "",
                     "uz": "Lin, bu safar ishga yollash kichik ish emas, qanday qilishimiz kerak deb o'ylaysiz?",
                     "ru": "Линь, на этот раз набор персонала — серьёзное дело, как вы думаете, что нужно сделать?",
                     "tj": "Лин, ин дафъа кор гирифтан кори хурд нест, ба назари шумо чӣ бояд кард?"},
                    {"speaker": "小林", "zh": "本来是小季员责任的，但他突然生病住院了，所以就委给我来做了。", "pinyin": "",
                     "uz": "Bu aslida kichik Ji-ning mas'uliyati edi, lekin u to'satdan kasalxonaga yotdi, shuning uchun menga topshirildi.",
                     "ru": "Изначально это была обязанность маленького Цзи, но он внезапно заболел и лёг в больницу, поэтому поручили мне.",
                     "tj": "Дар аввал ин масъулияти Ҷии хурд буд, аммо ӯ ногаҳон бемор шуд ва ба беморхона рафт, бинобар ин ба ман вогузор шуд."},
                    {"speaker": "马经理", "zh": "哦，这次应聘的人多吗？", "pinyin": "",
                     "uz": "E, bu safar murojaat qilganlar ko'pmi?",
                     "ru": "О, много ли людей подали заявки в этот раз?",
                     "tj": "О, ин дафъа мурољиаткунандагон зиёданд?"},
                    {"speaker": "小林", "zh": "本次共有应聘者15人，经过笔试和面试，有两个人不错。这是他们提供的材料，都符合我们的要求。另外，我已经通知他们下周一来办公室。", "pinyin": "",
                     "uz": "Bu safar jami 15 kishi murojaat qildi, yozma va og'zaki suhbatdan so'ng ikkita kishi yaxshi bo'ldi. Bu ularning hujjatlari, hammasi bizning talablarimizga mos keladi. Bundan tashqari, men ularni dushanba kuni ofisga kelishga chaqirdim.",
                     "ru": "В этот раз всего подали заявки 15 человек, после письменного и устного экзаменов двое оказались хорошими. Вот их документы — все соответствуют нашим требованиям. Кроме того, я уже уведомил их прийти в офис в следующий понедельник.",
                     "tj": "Ин дафъа ҷамъан 15 нафар мурољиат карданд, пас аз санҷиши хаттӣ ва шифоҳӣ ду нафар хуб баромаданд. Инак ҳуҷҷатҳои онҳо — ҳама ба талаботи мо мувофиқ аст. Илова бар ин, ман аллакай ба онҳо хабар додам, ки душанбе ба офис биёянд."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "越……越……",
                "title_uz": "qancha...shuncha...",
                "title_ru": "чем...тем...",
                "title_tj": "ҳар чи...ҳамон қадар...",
                "rule_uz": "'Qancha...shuncha...' ma'nosini beradi. Birinchi 越 dan keyingi holat ortishi bilan, ikkinchi 越 dan keyingi natija ham ortadi.",
                "rule_ru": "Означает 'чем...тем...'. По мере увеличения состояния после первого 越, результат после второго 越 тоже растёт.",
                "rule_tj": "Маънои 'ҳар чи...ҳамон қадар...' дорад. Бо афзоиши ҳолат пас аз 越 аввал, натиҷа пас аз 越 дуввум ҳам меафзояд.",
                "examples": [
                    {"zh": "越了解越有信心。", "pinyin": "",
                     "uz": "Qancha ko'p bilsak, shuncha ko'proq ishonch hosil qilamiz.",
                     "ru": "Чем больше знаешь, тем увереннее себя чувствуешь.",
                     "tj": "Ҳар чи бештар бидонӣ, ҳамон қадар боэтимодтар мешавӣ."},
                    {"zh": "天气越来越冷了。", "pinyin": "",
                     "uz": "Havo tobora sovuq bo'lmoqda.",
                     "ru": "Погода становится всё холоднее.",
                     "tj": "Ҳаво ҳар рӯз сардтар мешавад."},
                ],
            },
            {
                "no": 2,
                "title_zh": "本来",
                "title_uz": "aslida, dastlab",
                "title_ru": "изначально, на самом деле",
                "title_tj": "дар аввал, дар асл",
                "rule_uz": "'Aslida, dastlab' ma'nosini beradi. Hozirgi holat aslida boshqacha bo'lishi kerak edi, degan ma'noni bildiradi.",
                "rule_ru": "Означает 'изначально, на самом деле'. Указывает на то, что нынешняя ситуация должна была быть иной.",
                "rule_tj": "Маънои 'дар аввал, дар асл' дорад. Нишон медиҳад, ки ҳолати кунунӣ бояд дигар мебуд.",
                "examples": [
                    {"zh": "本来是小季的责任，但他生病了。", "pinyin": "",
                     "uz": "Bu aslida kichik Ji-ning mas'uliyati edi, lekin u kasal bo'ldi.",
                     "ru": "Изначально это была обязанность маленького Цзи, но он заболел.",
                     "tj": "Дар аввал ин масъулияти Ҷии хурд буд, аммо ӯ бемор шуд."},
                    {"zh": "我本来想去，但没时间。", "pinyin": "",
                     "uz": "Men aslida bormoqchi edim, lekin vaqtim bo'lmadi.",
                     "ru": "Я изначально хотел пойти, но не было времени.",
                     "tj": "Ман дар аввал мехостам биравам, аммо вақт надоштам."},
                ],
            },
            {
                "no": 3,
                "title_zh": "另外",
                "title_uz": "bundan tashqari, yana",
                "title_ru": "кроме того, к тому же",
                "title_tj": "илова бар ин, ғайр аз ин",
                "rule_uz": "'Bundan tashqari, yana' ma'nosini beradi. Avvalgi gapdagi ma'lumotga qo'shimcha ma'lumot qo'shadi.",
                "rule_ru": "Означает 'кроме того, к тому же'. Добавляет дополнительную информацию к предыдущему высказыванию.",
                "rule_tj": "Маънои 'илова бар ин, ғайр аз ин' дорад. Маълумоти иловагӣ ба гуфтаи қаблӣ мезанад.",
                "examples": [
                    {"zh": "另外，我已经通知他们了。", "pinyin": "",
                     "uz": "Bundan tashqari, men ularni allaqachon xabardor qildim.",
                     "ru": "Кроме того, я уже уведомил их.",
                     "tj": "Илова бар ин, ман аллакай ба онҳо хабар додам."},
                    {"zh": "他会说英语，另外还会说法语。", "pinyin": "",
                     "uz": "U inglizcha gapiradi, bundan tashqari frantsuzcha ham biladi.",
                     "ru": "Он говорит по-английски, а кроме того — ещё и по-французски.",
                     "tj": "Ӯ бо забони англисӣ гап мезанад, илова бар ин бо забони фаронсавӣ ҳам медонад."},
                ],
            },
            {
                "no": 4,
                "title_zh": "首先……其次……",
                "title_uz": "avvalo...ikkinchidan...",
                "title_ru": "во-первых...во-вторых...",
                "title_tj": "аввалан...дуввум...",
                "rule_uz": "'Avvalo...ikkinchidan...' ma'nosini beradi. Bir nechta fikrni tartib bilan sanash uchun ishlatiladi.",
                "rule_ru": "Означает 'во-первых...во-вторых...'. Используется для перечисления нескольких мыслей по порядку.",
                "rule_tj": "Маънои 'аввалан...дуввум...' дорад. Барои шумурдани якчанд фикр ба тартиб истифода мешавад.",
                "examples": [
                    {"zh": "首先要有能力，其次还要有经验。", "pinyin": "",
                     "uz": "Avvalo qobiliyat kerak, ikkinchidan tajriba ham zarur.",
                     "ru": "Во-первых, нужна способность, во-вторых, ещё и опыт.",
                     "tj": "Аввалан қобилият лозим аст, дуввум таҷриба ҳам зарур."},
                    {"zh": "首先感谢大家，其次介绍一下情况。", "pinyin": "",
                     "uz": "Avvalo hammaga rahmat, keyin vaziyatni tushuntiraman.",
                     "ru": "Во-первых, спасибо всем, а во-вторых, расскажу о ситуации.",
                     "tj": "Аввалан аз ҳама ташаккур, сипас вазъиятро шарҳ медиҳам."},
                ],
            },
            {
                "no": 5,
                "title_zh": "不管……都/也……",
                "title_uz": "qanday bo'lmasin, baribir...",
                "title_ru": "независимо от..., всё равно...",
                "title_tj": "новобаста аз..., боз ҳам...",
                "rule_uz": "'Qanday bo'lmasin, baribir...' ma'nosini beradi. Har qanday holatda ham natija o'zgarmasligini bildiradi.",
                "rule_ru": "Означает 'независимо от..., всё равно...'. Указывает, что результат не меняется ни при каких условиях.",
                "rule_tj": "Маънои 'новобаста аз..., боз ҳам...' дорад. Нишон медиҳад, ки натиҷа дар ҳеч ҳолат тағйир намеёбад.",
                "examples": [
                    {"zh": "不管多忙，他都会按时完成工作。", "pinyin": "",
                     "uz": "Qancha band bo'lmasin, u ishni o'z vaqtida tugatadi.",
                     "ru": "Независимо от занятости, он всегда вовремя завершает работу.",
                     "tj": "Новобаста аз банд будан, ӯ корро дар вақти муқарраршуда тамом мекунад."},
                    {"zh": "不管天气怎么样，我们都要去。", "pinyin": "",
                     "uz": "Ob-havo qanday bo'lmasin, biz baribir boramiz.",
                     "ru": "Независимо от погоды, мы всё равно поедем.",
                     "tj": "Новобаста аз ҳаво, мо боз ҳам меравем."},
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
                    {"prompt_uz": "qobiliyat, mahorat", "prompt_ru": "способность, умение", "prompt_tj": "қобилият, маҳорат", "answer": "能力", "pinyin": "nénglì"},
                    {"prompt_uz": "ishonch", "prompt_ru": "уверенность", "prompt_tj": "боварӣ", "answer": "信心", "pinyin": "xìnxīn"},
                    {"prompt_uz": "mos kelmoq", "prompt_ru": "соответствовать", "prompt_tj": "мувофиқ будан", "answer": "符合", "pinyin": "fúhé"},
                    {"prompt_uz": "tajriba", "prompt_ru": "опыт", "prompt_tj": "таҷриба", "answer": "经验", "pinyin": "jīngyàn"},
                    {"prompt_uz": "imkoniyat", "prompt_ru": "возможность", "prompt_tj": "имконият", "answer": "机会", "pinyin": "jīhuì"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский эквивалент следующих слов:",
                "instruction_tj": "Муодили ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "招聘", "prompt_ru": "招聘", "prompt_tj": "招聘", "answer": "ishchi yollash", "pinyin": "zhāopìn"},
                    {"prompt_uz": "负责", "prompt_ru": "负责", "prompt_tj": "负责", "answer": "mas'ul bo'lmoq", "pinyin": "fùzé"},
                    {"prompt_uz": "通知", "prompt_ru": "通知", "prompt_tj": "通知", "answer": "xabar bermoq", "pinyin": "tōngzhī"},
                    {"prompt_uz": "另外", "prompt_ru": "另外", "prompt_tj": "另外", "answer": "bundan tashqari", "pinyin": "lìngwài"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (越、本来、另外、首先、不管):",
                "instruction_ru": "Выберите подходящее слово (越、本来、另外、首先、不管):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (越、本来、另外、首先、不管):",
                "items": [
                    {"prompt_uz": "______，要有能力，______还要有经验。", "prompt_ru": "______，要有能力，______还要有经验。", "prompt_tj": "______，要有能力，______还要有经验。", "answer": "首先 / 其次", "pinyin": "shǒuxiān / qícì"},
                    {"prompt_uz": "天气______来______热了。", "prompt_ru": "天气______来______热了。", "prompt_tj": "天气______来______热了。", "answer": "越 / 越", "pinyin": "yuè / yuè"},
                    {"prompt_uz": "______多忙，她也会按时来。", "prompt_ru": "______多忙，她也会按时来。", "prompt_tj": "______多忙，她也会按时来。", "answer": "不管", "pinyin": "bùguǎn"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["能力", "信心", "符合", "经验", "机会"]},
            {"no": 2, "answers": ["ishchi yollash", "mas'ul bo'lmoq", "xabar bermoq", "bundan tashqari"]},
            {"no": 3, "answers": ["首先 / 其次", "越 / 越", "不管"]},
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
                "words": ["能力", "经验", "机会", "负责"],
                "example": "首先要有能力，其次还要有丰富的经验。",
            },
            {
                "no": 2,
                "instruction_uz": "'越...越...' va '不管...都...' qoliplaridan foydalanib har biridan 2 ta gap tuzing.",
                "instruction_ru": "Составьте по 2 предложения с конструкциями '越...越...' и '不管...都...'.",
                "instruction_tj": "Бо истифода аз қолипҳои '越...越...' ва '不管...都...' аз ҳар кадоме 2 ҷумла созед.",
                "topic_uz": "ish va o'qish mavzusida",
                "topic_ru": "на тему работы и учёбы",
                "topic_tj": "дар мавзӯи кор ва таҳсил",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Ish intervyusida o'zingizni qanday taqdim etasiz? 如果参加面试，你会怎么介绍自己？",
                "topic_ru": "Как вы представите себя на собеседовании? 如果参加面试，你会怎么介绍自己？",
                "topic_tj": "Дар мусоҳибаи кор худро чӣ тавр муаррифӣ мекунед? 如果参加面试，你会怎么介绍自己？",
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
