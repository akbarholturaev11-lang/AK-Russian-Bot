import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 14,
    "lesson_code": "HSK2-L14",
    "title": "你看过那个电影吗",
    "goal": json.dumps({"uz": "O'tgan tajribani bildiruvchi '过' yuklamasini, 'suīrán……dànshì' bog'lovchi juftligini va '次' harakat miqdori to'ldiruvchisini o'rganish.", "ru": "Изучение частицы '过', обозначающей прошлый опыт, союзного сочетания 'suīrán……dànshì' и счётного слова '次' для количества действий.", "tj": "Омӯзиши зарраи '过' ифодакунандаи таҷрибаи гузашта, ҷуфти пайвандии 'suīrán……dànshì' ва калимаи шуморавии '次' барои миқдори амал."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda biz o'tmishdagi tajribalar, sayohatlar va ko'rgan filmlar haqida gaplashishni o'rganamiz. '过' yuklamasi yordamida hayotiy tajribani ifodalash, 'suīrán……dànshì' (garchi……lekin) bog'lovchisini ishlatish va '次' (marta) so'zi bilan harakatning necha marta bajarilganligini aytishni mashq qilamiz.", "ru": "На этом уроке мы учимся говорить о прошлом опыте, путешествиях и просмотренных фильмах. Отрабатываем выражение жизненного опыта с помощью частицы '过', использование союза 'suīrán……dànshì' (хотя……но) и слово '次' (раз) для обозначения количества действий.", "tj": "Дар ин дарс ёд мегирем дар бораи таҷрибаи гузашта, сафарҳо ва филмҳои дидашуда сухан ронем. Ифодаи таҷрибаи зиндагиро бо ёрии зарраи '过', истифодаи пайванди 'suīrán……dànshì' (гарчи……аммо) ва калимаи '次' (маротиба) барои миқдори амал машқ мекунем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "有意思", "pinyin": "yǒu yìsi", "pos": "adj.", "uz": "qiziqarli, maroqli", "ru": "интересный, занимательный", "tj": "ҷолиб, хонанданӣ"},
        {"no": 2, "zh": "但是", "pinyin": "dànshì", "pos": "conj.", "uz": "lekin, ammo", "ru": "но, однако", "tj": "аммо, вале"},
        {"no": 3, "zh": "虽然", "pinyin": "suīrán", "pos": "conj.", "uz": "garchi, garchanda", "ru": "хотя, несмотря на то что", "tj": "гарчи, ҳарчанд"},
        {"no": 4, "zh": "次", "pinyin": "cì", "pos": "m.", "uz": "marta, safar (harakat o'lchovi)", "ru": "раз (счётное слово для действий)", "tj": "маротиба, бор (воҳиди шуморавӣ)"},
        {"no": 5, "zh": "玩儿", "pinyin": "wánr", "pos": "v.", "uz": "o'ynamoq, sayr qilmoq, dam olmoq", "ru": "играть, гулять, отдыхать", "tj": "бозӣ кардан, сайр кардан, истироҳат кардан"},
        {"no": 6, "zh": "晴", "pinyin": "qíng", "pos": "adj.", "uz": "ochiq (ob-havo), quyoshli", "ru": "ясный, солнечный (о погоде)", "tj": "ҳаво равшан, офтобӣ"},
        {"no": 7,  "zh": "百",   "pinyin": "bǎi",      "pos": "num.", "uz": "yuz (100)",                                    "ru": "сто (100)",                           "tj": "сад (100)"},
        {"no": 8,  "zh": "自己", "pinyin": "zìjǐ",     "pos": "pron.", "uz": "o'zi, o'zing",                               "ru": "сам, сама, себя",                     "tj": "худ, худаш"},
        {"no": 9,  "zh": "旅游", "pinyin": "lǚyóu",    "pos": "v.",   "uz": "sayohat qilmoq",                              "ru": "путешествовать",                      "tj": "сафар кардан, гашт кардан"},
        {"no": 10, "zh": "跑步", "pinyin": "pǎobù",    "pos": "v.",   "uz": "yugurmoq, estafeta yugurishi",                "ru": "бегать, делать пробежку",             "tj": "давидан, ҷиқ задан"},
        {"no": 11, "zh": "参加", "pinyin": "cānjia",   "pos": "v.",   "uz": "qatnashmoq, ishtiroq etmoq",                  "ru": "участвовать, принимать участие",      "tj": "иштирок кардан, ширкат кардан"},
        {"no": 12, "zh": "表演", "pinyin": "biǎoyǎn",  "pos": "v./n.", "uz": "sahna ko'rsatmoq; tamosha, spektakl",        "ru": "выступать; выступление, спектакль",   "tj": "намоиш додан; намоиш, спектакл"},
        {"no": 13, "zh": "商店", "pinyin": "shāngdiàn","pos": "n.",   "uz": "do'kon, magazin",                             "ru": "магазин",                             "tj": "дӯкон, мағоза"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Sinfxonada",
            "scene_ru": "В классе",
            "scene_tj": "Дар синфхона",
            "dialogue": [
                {"speaker": "A", "zh": "你看过那个电影没有？", "pinyin": "Nǐ kànguo nàge diànyǐng méiyǒu?", "uz": "Siz u filmni ko'rganmisiz?", "ru": "Ты смотрел(а) тот фильм?", "tj": "Оё шумо он филмро дидаед?"},
                {"speaker": "B", "zh": "没看过，听说很有意思。", "pinyin": "Méi kànguo, tīngshuō hěn yǒu yìsi.", "uz": "Ko'rmaganman, eshitishimcha juda qiziqarli emish.", "ru": "Не смотрел(а), говорят, очень интересный.", "tj": "Надидаам, гуфтанд хеле ҷолиб аст."},
                {"speaker": "A", "zh": "那我们下个星期一一起去看吧？", "pinyin": "Nà wǒmen xià ge xīngqīyī yìqǐ qù kàn ba?", "uz": "Unda biz kelasi dushanbada birga ko'rishga borsakchi?", "ru": "Тогда давай в следующий понедельник вместе сходим?", "tj": "Пас биёед душанбаи оянда якҷоя биравем тамошо кунем?"},
                {"speaker": "B", "zh": "可以，但是我女朋友也想去。", "pinyin": "Kěyǐ, dànshì wǒ nǚpéngyou yě xiǎng qù.", "uz": "Bo'ladi, lekin qiz do'stim ham bormoqchi.", "ru": "Можно, но моя девушка тоже хочет пойти.", "tj": "Мешавад, аммо дӯстдухтарам ҳам мехоҳад биравад."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Ofisda",
            "scene_ru": "В офисе",
            "scene_tj": "Дар дафтар",
            "dialogue": [
                {"speaker": "A", "zh": "听说你去过中国，还想去吗？", "pinyin": "Tīngshuō nǐ qùguo Zhōngguó, hái xiǎng qù ma?", "uz": "Eshitdimki siz Xitoyga borgansiz, yana bormoqchimisiz?", "ru": "Говорят, ты бывал(а) в Китае, хочешь съездить снова?", "tj": "Шунидам ки шумо ба Чин рафтаед, боз рафтанӣ ҳастед?"},
                {"speaker": "B", "zh": "我虽然去过好几次，但是还想再去中国玩儿。", "pinyin": "Wǒ suīrán qùguo hǎo jǐ cì, dànshì hái xiǎng zài qù Zhōngguó wánr.", "uz": "Men garchi bir necha marta borgan bo'lsam ham, lekin yana Xitoyga sayohat qilmoqchiman.", "ru": "Хотя я там бывал(а) несколько раз, всё равно хочу снова поехать в Китай.", "tj": "Гарчи ман чанд маротиба рафта бошам ҳам, аммо боз мехоҳам ба Чин барам сайр кунам."},
                {"speaker": "A", "zh": "那我们一起去吧。", "pinyin": "Nà wǒmen yìqǐ qù ba.", "uz": "Unda birga boraylik.", "ru": "Тогда давай поедем вместе.", "tj": "Пас биёед якҷоя биравем."},
                {"speaker": "B", "zh": "好啊，到时候我给你打电话。", "pinyin": "Hǎo a, dào shíhou wǒ gěi nǐ dǎ diànhuà.", "uz": "Yaxshi, o'sha vaqt kelganda telefon qilaman.", "ru": "Хорошо, когда придёт время, позвоню тебе.", "tj": "Хуб, вақташ расид занг мезанам."}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Xonada",
            "scene_ru": "В комнате",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "明天天气怎么样？", "pinyin": "Míngtiān tiānqì zěnmeyàng?", "uz": "Ertaga ob-havo qanday bo'ladi?", "ru": "Какая завтра будет погода?", "tj": "Фардо ҳаво чӣ хел мешавад?"},
                {"speaker": "B", "zh": "虽然是晴天，但是很冷。", "pinyin": "Suīrán shì qíngtiān, dànshì hěn lěng.", "uz": "Garchi quyoshli kun bo'lsa ham, lekin juda sovuq.", "ru": "Хотя будет солнечно, но очень холодно.", "tj": "Гарчи рӯзи офтобӣ бошад ҳам, аммо хеле сард аст."},
                {"speaker": "A", "zh": "那还能够跑步吗？", "pinyin": "Nà hái nénggòu pǎobù ma?", "uz": "Unda yugurish mumkinmi?", "ru": "Тогда ещё можно бегать?", "tj": "Пас ҳанӯз давидан мешавад?"},
                {"speaker": "B", "zh": "可以，但是你自己去吧，我还有很多事情要做。", "pinyin": "Kěyǐ, dànshì nǐ zìjǐ qù ba, wǒ hái yǒu hěn duō shìqing yào zuò.", "uz": "Mumkin, lekin o'zingiz boring, menda hali ko'p ish bor.", "ru": "Можно, но иди сам(а), у меня ещё много дел.", "tj": "Мешавад, аммо худатон равед, ман ҳанӯз кори зиёд дорам."}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Do'konda",
            "scene_ru": "В магазине",
            "scene_tj": "Дар мағоза",
            "dialogue": [
                {"speaker": "A", "zh": "你在这个商店买过东西没有？", "pinyin": "Nǐ zài zhège shāngdiàn mǎiguo dōngxi méiyǒu?", "uz": "Siz bu do'konda narsa sotib olganmisiz?", "ru": "Ты когда-нибудь покупал(а) что-то в этом магазине?", "tj": "Оё шумо дар ин дӯкон чизе харидаед?"},
                {"speaker": "B", "zh": "买过一次，这儿的东西还可以，就是有点儿贵。", "pinyin": "Mǎiguo yí cì, zhèr de dōngxi hái kěyǐ, jiùshì yǒudiǎnr guì.", "uz": "Bir marta olganman, bu yerdagi narsalar yomonmas, faqat biroz qimmat.", "ru": "Покупал(а) один раз, товары здесь неплохие, только немного дорогие.", "tj": "Як маротиба харидаам, молҳои ин ҷо бад нест, фақат каме гарон."},
                {"speaker": "A", "zh": "我喜欢这件衣服，但是觉得有点儿贵。", "pinyin": "Wǒ xǐhuan zhè jiàn yīfu, dànshì juéde yǒudiǎnr guì.", "uz": "Men bu kiyimni yoqtiraman, lekin biroz qimmat deb hisoblayman.", "ru": "Мне нравится эта одежда, но думаю, немного дорого.", "tj": "Ман ин либосро дӯст медорам, аммо фикр мекунам каме гарон аст."},
                {"speaker": "B", "zh": "两百块还可以，喜欢就买吧。", "pinyin": "Liǎng bǎi kuài hái kěyǐ, xǐhuan jiù mǎi ba.", "uz": "Ikki yuz yuan yomonmas, yoqsa olaverıng.", "ru": "Двести юаней — нормально, если нравится, покупай.", "tj": "Дусад юан бад нест, агар дӯст дорӣ бихар."}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "动态助词“过”",
            "title_uz": "'Guo' harakat yuklamasi",
            "title_ru": "Динамическая частица '过'",
            "title_tj": "Зарраи динамикии '过'",
            "rule_uz": "'Guo' yuklamasi fe'ldan keyin kelib, hayotiy tajribani bildiradi: 'bir vaqtlar …qilganman'. Bu faqat shaxsiy o'tmish tajribasini ifodalaydi. Inkor: '没' + fe'l + '过' (hech qachon …qilmaganman). Savol: fe'l + '过' + '没有?'",
            "rule_ru": "Частица '过' ставится после глагола и обозначает жизненный опыт: 'когда-то делал(а)'. Выражает только личный прошлый опыт. Отрицание: '没' + глагол + '过' (никогда не делал(а)). Вопрос: глагол + '过' + '没有?'",
            "rule_tj": "Зарраи '过' баъд аз феъл меояд ва таҷрибаи зиндагиро ифода мекунад: 'вақте кардаам'. Танҳо таҷрибаи шахсии гузаштаро ифода мекунад. Инкор: '没' + феъл + '过' (ҳеҷгоҳ накардаам). Пурсиш: феъл + '过' + '没有?'",
            "examples": [
                {"zh": "你看过那个电影吗？", "pinyin": "Nǐ kànguo nàge diànyǐng ma?", "uz": "Siz o'sha filmni ko'rganmisiz?", "ru": "Ты смотрел(а) тот фильм?", "tj": "Оё шумо он филмро дидаед?"},
                {"zh": "我去过北京两次。", "pinyin": "Wǒ qùguo Běijīng liǎng cì.", "uz": "Men Pekinga ikki marta borgan.", "ru": "Я бывал(а) в Пекине два раза.", "tj": "Ман ба Пекин ду маротиба рафтаам."}
            ]
        },
        {
            "no": 2,
            "title_zh": "关联词“虽然……，但是……”",
            "title_uz": "'Suīrán……dànshì……' bog'lovchi juftligi",
            "title_ru": "Союзная пара 'suīrán……dànshì……'",
            "title_tj": "Ҷуфти пайвандии 'suīrán……dànshì……'",
            "rule_uz": "'Suīrán……dànshì……' bog'lovchi juftligi 'garchi……bo'lsa ham, lekin……' ma'nosini beradi. Birinchi qismda tan olingan holat, ikkinchi qismda unga qarama-qarshi fikr ifodalanadi. 'Suīrán' ko'pincha gap boshida yoki ot/sifatdan oldin keladi.",
            "rule_ru": "Союзная пара 'suīrán……dànshì……' означает 'хотя……но……'. В первой части признаётся некоторый факт, во второй выражается противоположная мысль. 'Suīrán' обычно стоит в начале предложения или перед существительным/прилагательным.",
            "rule_tj": "Ҷуфти пайвандии 'suīrán……dànshì……' маъниаш 'гарчи……бошад ҳам, аммо……' аст. Дар қисми аввал ҳолате эътироф мешавад, дар қисми дуввум фикри муқобил ифода мешавад. 'Suīrán' одатан дар аввали ҷумла ё пеш аз исм/сифат меояд.",
            "examples": [
                {"zh": "虽然是晴天，但是很冷。", "pinyin": "Suīrán shì qíngtiān, dànshì hěn lěng.", "uz": "Garchi quyoshli kun bo'lsa ham, lekin juda sovuq.", "ru": "Хотя солнечно, но очень холодно.", "tj": "Гарчи рӯзи офтобӣ бошад ҳам, аммо хеле сард аст."},
                {"zh": "虽然去过好几次，但是还想再去。", "pinyin": "Suīrán qùguo hǎo jǐ cì, dànshì hái xiǎng zài qù.", "uz": "Garchi bir necha marta borgan bo'lsam ham, lekin yana bormoqchiman.", "ru": "Хотя бывал(а) несколько раз, но всё равно хочу поехать снова.", "tj": "Гарчи чанд маротиба рафта бошам ҳам, аммо боз рафтанӣ ҳастам."}
            ]
        },
        {
            "no": 3,
            "title_zh": "动量补语“次”",
            "title_uz": "'Cì' harakat miqdori to'ldiruvchisi",
            "title_ru": "Счётное дополнение '次'",
            "title_tj": "Иловаи миқдории '次'",
            "rule_uz": "'Cì' (marta, safar) harakat miqdori to'ldiruvchisi bo'lib, fe'ldan keyin keladi va harakatning necha marta bajarilganligini bildiradi. Tuzilish: fe'l + '过' + sanoq + '次'. Masalan: 去过两次 (ikki marta borgan).",
            "rule_ru": "'Cì' (раз) является счётным дополнением, стоит после глагола и указывает, сколько раз выполнено действие. Структура: глагол + '过' + число + '次'. Например: 去过两次 (бывал(а) два раза).",
            "rule_tj": "'Cì' (маротиба, бор) иловаи миқдорӣ аст, баъд аз феъл меояд ва нишон медиҳад амал чанд маротиба иҷро шудааст. Сохтор: феъл + '过' + рақам + '次'. Масалан: 去过两次 (ду маротиба рафтаам).",
            "examples": [
                {"zh": "我去过中国好几次。", "pinyin": "Wǒ qùguo Zhōngguó hǎo jǐ cì.", "uz": "Men Xitoyga bir necha marta borgan.", "ru": "Я бывал(а) в Китае несколько раз.", "tj": "Ман ба Чин чанд маротиба рафтаам."},
                {"zh": "我在这个商店买过一次东西。", "pinyin": "Wǒ zài zhège shāngdiàn mǎiguo yí cì dōngxi.", "uz": "Men bu do'konda bir marta narsa sotib olganman.", "ru": "Я однажды покупал(а) что-то в этом магазине.", "tj": "Ман дар ин дӯкон як маротиба чиз харидаам."}
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
                {"prompt_uz": "qiziqarli", "prompt_ru": "интересный", "prompt_tj": "ҷолиб", "answer": "有意思", "pinyin": "yǒu yìsi"},
                {"prompt_uz": "lekin", "prompt_ru": "но", "prompt_tj": "аммо", "answer": "但是", "pinyin": "dànshì"},
                {"prompt_uz": "garchi", "prompt_ru": "хотя", "prompt_tj": "гарчи", "answer": "虽然", "pinyin": "suīrán"},
                {"prompt_uz": "marta", "prompt_ru": "раз", "prompt_tj": "маротиба", "answer": "次", "pinyin": "cì"},
                {"prompt_uz": "quyoshli", "prompt_ru": "солнечный", "prompt_tj": "офтобӣ", "answer": "晴", "pinyin": "qíng"}
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "Siz ilgari bu ovqatni ye___ misiz? (过)", "prompt_ru": "Ты когда-нибудь пробовал(а) эту еду? (过)", "prompt_tj": "Оё шумо пештар ин хӯрокро хӯрда ___? (过)", "answer": "过", "pinyin": "guo"},
                {"prompt_uz": "Men o'tgan yil opangni bir ___ ko'rdim. (次)", "prompt_ru": "В прошлом году я видел(а) твою сестру один ___. (次)", "prompt_tj": "Соли гузашта ман хоҳаратро як ___ дидам. (次)", "answer": "次", "pinyin": "cì"},
                {"prompt_uz": "___ havo sovuq, u hali ham yugurdi. (虽然)", "prompt_ru": "___ погода была холодной, он всё равно побежал. (虽然)", "prompt_tj": "___ ҳаво сард буд, вай боз ҳам давид. (虽然)", "answer": "虽然", "pinyin": "suīrán"},
                {"prompt_uz": "Garchi ingliz tili qiyin bo'lsa ham, ___ u yaxshi o'rganmoqda. (但是)", "prompt_ru": "Хотя английский сложный, ___ она хорошо его учит. (但是)", "prompt_tj": "Гарчи забони англисӣ душвор бошад ҳам, ___ вай хуб меомӯзад. (但是)", "answer": "但是", "pinyin": "dànshì"}
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "我虽然去过好几次，但是还想再去中国玩儿。", "prompt_ru": "我虽然去过好几次，但是还想再去中国玩儿。", "prompt_tj": "我虽然去过好几次，但是还想再去中国玩儿。", "answer": "Men garchi bir necha marta borgan bo'lsam ham, lekin yana Xitoyga sayohat qilmoqchiman.", "pinyin": "Wǒ suīrán qùguo hǎo jǐ cì, dànshì hái xiǎng zài qù Zhōngguó wánr."},
                {"prompt_uz": "买过一次，这儿的东西还可以，就是有点儿贵。", "prompt_ru": "买过一次，这儿的东西还可以，就是有点儿贵。", "prompt_tj": "买过一次，这儿的东西还可以，就是有点儿贵。", "answer": "Bir marta olganman, bu yerdagi narsalar yomonmas, faqat biroz qimmat.", "pinyin": "Mǎiguo yí cì, zhèr de dōngxi hái kěyǐ, jiùshì yǒudiǎnr guì."},
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["有意思", "但是", "虽然", "次", "晴"]},
        {"no": 2, "answers": ["过", "次", "虽然", "但是"]},
        {"no": 3, "answers": [
            "Men garchi bir necha marta borgan bo'lsam ham, lekin yana Xitoyga sayohat qilmoqchiman.",
            "Bir marta olganman, bu yerdagi narsalar yomonmas, faqat biroz qimmat.",
        ]}
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "O'zingiz borib ko'rgan joy yoki ko'rgan film haqida '过' yuklamasidan foydalanib yozing. Necha marta borgan yoki ko'rganingizni ham qo'shing.",
            "instruction_ru": "Напишите о месте, которое вы посещали, или о фильме, который смотрели, используя частицу '过'. Укажите, сколько раз вы там были или смотрели.",
            "instruction_tj": "Дар бораи ҷойе ки рафтаед ё филме ки дидаед бо истифодаи зарраи '过' нависед. Чанд маротиба рафтан ё дидани худро ҳам зиёд кунед.",
            "words": ["过", "次", "虽然……但是……"],
            "example": "我去过北京一次，那里很好玩儿。",
            "topic_uz": "Borib ko'rgan joy yoki film",
            "topic_ru": "Место, которое посещали, или фильм",
            "topic_tj": "Ҷойе ки рафтаед ё филми дидашуда"
        },
        {
            "no": 2,
            "instruction_uz": "'Suīrán……dànshì……' ishlatib hayotdagi biror narsa haqida fikringizni yozing (masalan: xitoy tili, ob-havo, maktab va h.k.).",
            "instruction_ru": "Используя 'suīrán……dànshì……', напишите своё мнение о чём-либо в жизни (например: китайский язык, погода, учёба и т.д.).",
            "instruction_tj": "Бо истифодаи 'suīrán……dànshì……' фикри худро дар бораи ягон чизи зиндагӣ нависед (масалан: забони чинӣ, ҳаво, мактаб ва ғ.).",
            "words": ["虽然……但是……"],
            "example": "虽然汉语很难，但是很有意思。",
            "topic_uz": "Hayotdagi fikrim",
            "topic_ru": "Моё мнение о жизни",
            "topic_tj": "Фикри ман дар бораи зиндагӣ"
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
