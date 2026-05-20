import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 4,
    "lesson_code": "HSK4-L04",
    "title": "不要太着急赚钱",
    "goal": json.dumps({"uz": "pul ishlash, ish va hayot balansi haqida gapirish; 以为, 原来, 并, 起初, 甚至 grammatik qoliplarini o'zlashtirish", "ru": "говорить о зарабатывании денег, балансе работы и жизни; освоить конструкции 以为, 原来, 并, 起初, 甚至", "tj": "гуфтугӯ дар бораи пул даровардан ва тавозуни кор ва зиндагӣ; аз худ кардани қолипҳои 以为, 原来, 并, 起初, 甚至"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Pul topishga shoshilmang' mavzusiga bag'ishlangan. Unda yangi ish boshlash, moddiy va ma'naviy qadriyatlar haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 以为, 原来, 并, 起初, 甚至.", "ru": "Этот урок посвящён теме 'Не спешите зарабатывать деньги'. В нём вы научитесь говорить о начале новой работы, материальных и духовных ценностях. Основные грамматические конструкции: 以为, 原来, 并, 起初, 甚至.", "tj": "Ин дарс ба мавзӯи 'Барои пул даровардан шитоб накунед' бахшида шудааст. Дар он оғози кори нав, арзишҳои моддӣ ва маънавӣ омӯхта мешавад. Қолипҳои асосии грамматикӣ: 以为, 原来, 并, 起初, 甚至."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "提", "pinyin": "tí", "pos": "v.", "uz": "eslatmoq, aytmoq, ko'tarmoq", "ru": "упоминать, поднимать", "tj": "зикр кардан, гуфтан, бардоштан"},
            {"no": 2, "zh": "以为", "pinyin": "yǐwéi", "pos": "v.", "uz": "o'ylash (noto'g'ri bo'lib chiqadigan), xayol qilmoq", "ru": "считать (ошибочно), полагать", "tj": "фикр кардан (нодуруст), хаёл кардан"},
            {"no": 3, "zh": "份", "pinyin": "fèn", "pos": "m.", "uz": "dona (ish, gazeta, hujjat uchun)", "ru": "единица (для работы, газеты, документа)", "tj": "дона (барои кор, рӯзнома, ҳуҷҷат)"},
            {"no": 4, "zh": "完全", "pinyin": "wánquán", "pos": "adv.", "uz": "butunlay, to'liq", "ru": "полностью, совершенно", "tj": "пурра, комилан"},
            {"no": 5, "zh": "赚", "pinyin": "zhuàn", "pos": "v.", "uz": "pul ishlash, daromad qilish", "ru": "зарабатывать деньги", "tj": "пул даровардан, даромад кардан"},
            {"no": 6, "zh": "调查", "pinyin": "diàochá", "pos": "v./n.", "uz": "o'rganmoq, tekshirmoq; tadqiqot", "ru": "исследовать, изучать; исследование", "tj": "омӯхтан, санҷидан; тадқиқот"},
            {"no": 7, "zh": "原来", "pinyin": "yuánlái", "pos": "adv./adj.", "uz": "aslida, demak; dastlabki", "ru": "оказывается; первоначальный", "tj": "маълум мешавад; аслӣ, ибтидоӣ"},
            {"no": 8, "zh": "计划", "pinyin": "jìhuà", "pos": "n./v.", "uz": "reja; reja qilmoq", "ru": "план; планировать", "tj": "нақша; нақша кашидан"},
            {"no": 9, "zh": "提前", "pinyin": "tíqián", "pos": "v.", "uz": "oldindan qilmoq, muddatidan oldin", "ru": "делать заранее, досрочно", "tj": "пешакӣ кардан, пеш аз мӯҳлат"},
            {"no": 10, "zh": "保证", "pinyin": "bǎozhèng", "pos": "v./n.", "uz": "kafolat bermoq; kafolat", "ru": "гарантировать; гарантия", "tj": "кафолат додан; кафолат"},
            {"no": 11, "zh": "提醒", "pinyin": "tíxǐng", "pos": "v.", "uz": "eslatmoq, ogohlantirilmoq", "ru": "напоминать, предупреждать", "tj": "ёдоварӣ кардан, огоҳ кардан"},
            {"no": 12, "zh": "乱", "pinyin": "luàn", "pos": "adj.", "uz": "tartibsiz, chalkash; shoshqaloq", "ru": "беспорядочный, хаотичный; суетливый", "tj": "беназм, ошуфта; шошқалоқ"},
            {"no": 13, "zh": "起初", "pinyin": "qǐchū", "pos": "adv.", "uz": "dastlab, boshida", "ru": "вначале, поначалу", "tj": "аввалан, дар ибтидо"},
            {"no": 14, "zh": "甚至", "pinyin": "shènzhì", "pos": "adv.", "uz": "hatto, shu qadar", "ru": "даже, настолько", "tj": "ҳатто, то ҳадде"},
            {"no": 15, "zh": "并", "pinyin": "bìng", "pos": "adv.", "uz": "umuman (inkor bilan), aslida emas", "ru": "вовсе не, на самом деле (с отрицанием)", "tj": "умуман (бо инкор), дар асл не"},
            {"no": 16, "zh": "收入", "pinyin": "shōurù", "pos": "n.", "uz": "daromad, maosh", "ru": "доход, зарплата", "tj": "даромад, музд"},
            {"no": 17, "zh": "稳定", "pinyin": "wěndìng", "pos": "adj.", "uz": "barqaror, beqiyos", "ru": "стабильный, устойчивый", "tj": "устувор, барқарор"},
            {"no": 18, "zh": "努力", "pinyin": "nǔlì", "pos": "v./adj.", "uz": "harakat qilmoq; g'ayratli", "ru": "стараться; усердный", "tj": "кӯшиш кардан; ғайраткор"},
            {"no": 19, "zh": "成功", "pinyin": "chénggōng", "pos": "v./n.", "uz": "muvaffaqiyat qozonmoq; muvaffaqiyat", "ru": "добиться успеха; успех", "tj": "муваффақ шудан; муваффақият"},
            {"no": 20, "zh": "经历", "pinyin": "jīnglì", "pos": "n./v.", "uz": "tajriba; boshdan kechirmoq", "ru": "опыт; переживать", "tj": "таҷриба; аз сар гузарондан"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "小林 va 小李 ishlar haqida gaplashadi",
                "scene_ru": "小林 и 小李 обсуждают работу",
                "scene_tj": "小林 ва 小李 дар бораи кор гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "小林", "zh": "听说你找到新工作了？今年已经换了三次工作了。", "pinyin": "",
                     "uz": "Eshitdim, yangi ish topdingmi? Bu yil allaqachon uch marta ish almashtirding.",
                     "ru": "Слышал, ты нашёл новую работу? В этом году уже трижды менял работу.",
                     "tj": "Шунидам, кори нав ёфтӣ? Имсол аллакай се маротиба кор иваз кардӣ."},
                    {"speaker": "小李", "zh": "对了！我以前以为薪水高的工作才是好工作，现在完全改变了想法。", "pinyin": "",
                     "uz": "Ha! Ilgari men maoshi yuqori ish — yaxshi ish deb o'ylardim, endi fikrim butunlay o'zgardi.",
                     "ru": "Да! Раньше я считал, что хорошая работа — это высокооплачиваемая, теперь моё мнение полностью изменилось.",
                     "tj": "Бале! Пештар фикр мекардам, ки кори бо музди баланд — кори хуб аст, ҳоло фикрам пурра тағйир ёфт."},
                    {"speaker": "小林", "zh": "以前那份工作不是挺好的吗？收入高，工作稳定。", "pinyin": "",
                     "uz": "Oldingi ishing yaxshi emasmi? Maoshi yuqori, ishi barqaror.",
                     "ru": "Разве прежняя работа не была хороша? Высокий доход, стабильная работа.",
                     "tj": "Магар кори пешина хуб набуд? Даромади баланд, кори устувор."},
                    {"speaker": "小李", "zh": "起初以为不错，但实际上每天加班，甚至周末也要上班，这样下去并不好，所以我决定换一份工作。", "pinyin": "",
                     "uz": "Boshida yaxshi deb o'ylardim, lekin aslida har kuni qo'shimcha ishlayman, hatto dushanba kunlari ham ishga boraman, bu holat umuman yaxshi emas, shu sababli ish almashtirishga qaror qildim.",
                     "ru": "Поначалу казалось неплохо, но на самом деле каждый день сверхурочно, даже в выходные нужно работать — так продолжать вовсе нехорошо, поэтому я решил сменить работу.",
                     "tj": "Дар ибтидо фикр мекардам хуб аст, аммо воқеан ҳар рӯз аз вақти кор зиёд кор мекардам, ҳатто охири ҳафта ҳам, ин тавр давом кардан умуман хуб нест, бинобар ин қарор кардам кор иваз кунам."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "Menejer Van va 小李 ish rejasi haqida gaplashadi",
                "scene_ru": "Менеджер Ван и 小李 обсуждают рабочий план",
                "scene_tj": "Мудир Ван ва 小李 дар бораи нақшаи кор гуфтугӯ мекунанд",
                "dialogue": [
                    {"speaker": "王经理", "zh": "那份调查报告应该需要多长时间才能做完？", "pinyin": "",
                     "uz": "U tadqiqot hisoboti qancha vaqt oladi?",
                     "ru": "Сколько времени займёт подготовка того исследовательского отчёта?",
                     "tj": "Он гузориши тадқиқотӣ чанд вақт мебарад?"},
                    {"speaker": "小李", "zh": "原来的计划是周末，但是我们可以提前完成，周末前能保证完成。", "pinyin": "",
                     "uz": "Dastlabki reja shanba kuni edi, lekin biz ertaroq tugatishimiz mumkin, shanba kunidan oldin kafolat bera olaman.",
                     "ru": "Первоначальный план был к выходным, но мы можем закончить раньше — гарантирую выполнение до выходных.",
                     "tj": "Нақшаи аввалӣ охири ҳафта буд, аммо мо метавонем зудтар тамом кунем — то охири ҳафта кафолат медиҳам."},
                    {"speaker": "王经理", "zh": "虽然我们公司在做这类工作上经验还没那么多，但认真努力的态度非常重要，提醒你不要太着急。", "pinyin": "",
                     "uz": "Garchi bizning kompaniyamizda bunday ishda tajriba unchalik ko'p bo'lmasa ham, jiddiy va g'ayratli munosabat juda muhim, sizni shoshmaslik haqida ogohlantiraman.",
                     "ru": "Хотя у нашей компании не так много опыта в таких делах, серьёзное и усердное отношение очень важно — напоминаю, не нужно слишком торопиться.",
                     "tj": "Гарчанде ширкати мо дар ин гуна кор таҷрибаи зиёд надорад, муносибати ҷиддӣ ва ғайраткорона хеле муҳим аст — ёдоварӣ мекунам, ки хеле шошқалоқ нашавед."},
                    {"speaker": "小李", "zh": "谢谢您的提醒！我明白了，成功需要时间，不要太乱，要按计划来。", "pinyin": "",
                     "uz": "Eslatganiz uchun rahmat! Tushundim, muvaffaqiyat vaqt talab qiladi, shoshqaloq bo'lmay, rejaga ko'ra ish qilish kerak.",
                     "ru": "Спасибо за напоминание! Понял — успех требует времени, не нужно суетиться, нужно действовать по плану.",
                     "tj": "Ташаккур барои ёдоварӣ! Фаҳмидам — муваффақият вақт талаб мекунад, шошқалоқ набошем, бояд мувофиқи нақша амал кунем."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "以为",
                "title_uz": "...deb o'ylash (lekin noto'g'ri)",
                "title_ru": "считать (ошибочно)",
                "title_tj": "фикр кардан (нодуруст)",
                "rule_uz": "'...deb o'ylash (lekin noto'g'ri bo'lib chiqqan)' ma'nosini beradi. Ko'pincha keyinroq noto'g'ri bo'lib chiqqan fikrni bildiradi.",
                "rule_ru": "Означает 'считать что-то (но оказалось неверным)'. Обычно выражает ошибочное мнение, которое впоследствии оказалось неправильным.",
                "rule_tj": "Маънои 'фикр кардан (аммо нодуруст баромад)' дорад. Одатан ақидаи нодурустеро ифода мекунад, ки баъдтар ғалат буд.",
                "examples": [
                    {"zh": "我以为他不来了，原来他在等我们。", "pinyin": "",
                     "uz": "Men u kelmaydi deb o'ylardim, aslida u bizni kutayotgan ekan.",
                     "ru": "Я считал, что он не придёт, а оказывается, он ждал нас.",
                     "tj": "Фикр мекардам, ки ӯ намеояд, маълум шуд, ки ӯ мо дошт мунтазир буд."},
                    {"zh": "起初以为这份工作很好。", "pinyin": "",
                     "uz": "Boshida bu ish yaxshi deb o'ylardim.",
                     "ru": "Поначалу я считал, что эта работа хорошая.",
                     "tj": "Дар ибтидо фикр мекардам, ки ин кор хуб аст."},
                ],
            },
            {
                "no": 2,
                "title_zh": "原来",
                "title_uz": "aslida, demak (ajablanish)",
                "title_ru": "оказывается, первоначальный",
                "title_tj": "маълум мешавад, аслӣ",
                "rule_uz": "'Aslida, demak (ajablanishni bildiradi)' yoki 'dastlabki holat' ma'nosini beradi.",
                "rule_ru": "Означает 'оказывается (выражает удивление)' или 'первоначальное состояние'.",
                "rule_tj": "Маънои 'маълум мешавад (ҳайрат)' ё 'ҳолати аввалӣ' дорад.",
                "examples": [
                    {"zh": "原来他在这儿！我找了半天。", "pinyin": "",
                     "uz": "Demak u bu yerda ekan! Men uni anchadan beri qidiryapman.",
                     "ru": "Оказывается, он здесь! Я его долго искал.",
                     "tj": "Маълум шуд, ки ӯ ин ҷост! Ман ӯро муддатест меҷустам."},
                    {"zh": "原来的计划是周末完成。", "pinyin": "",
                     "uz": "Dastlabki reja shanba kuni tugatish edi.",
                     "ru": "Первоначальный план — завершить к выходным.",
                     "tj": "Нақшаи аввалӣ охири ҳафта тамом кардан буд."},
                ],
            },
            {
                "no": 3,
                "title_zh": "并（不/没）",
                "title_uz": "umuman emas, aslida emas",
                "title_ru": "вовсе не, на самом деле нет",
                "title_tj": "умуман не, дар асл не",
                "rule_uz": "'Umuman emas, aslida emas' ma'nosini beradi. Inkor gaplarda kutilganidek emas ekanligini ta'kidlaydi.",
                "rule_ru": "Означает 'вовсе не, на самом деле нет'. В отрицательных предложениях подчёркивает несоответствие ожиданиям.",
                "rule_tj": "Маънои 'умуман не, дар асл не' дорад. Дар ҷумлаҳои инкорӣ таъкид мекунад, ки воқеъият аз интизор фарқ мекунад.",
                "examples": [
                    {"zh": "这样下去并不好。", "pinyin": "",
                     "uz": "Bunday davom etish umuman yaxshi emas.",
                     "ru": "Так продолжать вовсе нехорошо.",
                     "tj": "Ин тавр идома додан умуман хуб нест."},
                    {"zh": "他并没有不高兴，只是有点儿累。", "pinyin": "",
                     "uz": "U umuman xafa emas edi, shunchaki biroz charchagan edi.",
                     "ru": "Он вовсе не был недоволен, просто немного устал.",
                     "tj": "Ӯ умуман норозӣ набуд, танҳо каме хаста буд."},
                ],
            },
            {
                "no": 4,
                "title_zh": "起初",
                "title_uz": "boshida, dastlab",
                "title_ru": "вначале, поначалу",
                "title_tj": "дар ибтидо, аввалан",
                "rule_uz": "'Boshida, dastlab' ma'nosini beradi. Biror hodisaning boshlanish vaqtini bildiradi.",
                "rule_ru": "Означает 'вначале, поначалу'. Указывает на начальный момент какого-либо события.",
                "rule_tj": "Маънои 'дар ибтидо, аввалан' дорад. Ибтидои рӯйдодеро нишон медиҳад.",
                "examples": [
                    {"zh": "起初我觉得这个工作很难，后来慢慢就好了。", "pinyin": "",
                     "uz": "Boshida bu ish juda qiyin deb o'ylardim, keyin asta-sekin yaxshi bo'ldi.",
                     "ru": "Поначалу я думал, что эта работа очень сложная, потом постепенно стало лучше.",
                     "tj": "Дар ибтидо фикр мекардам, ки ин кор хеле душвор аст, баъд оҳиста-оҳиста беҳтар шуд."},
                    {"zh": "起初他并不同意，后来改变了主意。", "pinyin": "",
                     "uz": "Boshida u rozi bo'lmadi, keyin fikrini o'zgartirdi.",
                     "ru": "Поначалу он не согласился, потом изменил мнение.",
                     "tj": "Дар ибтидо ӯ розӣ набуд, баъд фикрашро тағйир дод."},
                ],
            },
            {
                "no": 5,
                "title_zh": "甚至",
                "title_uz": "hatto, shu qadar",
                "title_ru": "даже, настолько",
                "title_tj": "ҳатто, то ҳадде ки",
                "rule_uz": "'Hatto, shu qadar' ma'nosini beradi. Kutilmagan yoki juda yuqori darajani bildiradi.",
                "rule_ru": "Означает 'даже, настолько'. Выражает неожиданно высокую степень или неожиданный факт.",
                "rule_tj": "Маънои 'ҳатто, то ҳадде ки' дорад. Дараҷаи ногаҳонии баланд ё факти ногаҳониро ифода мекунад.",
                "examples": [
                    {"zh": "他每天加班，甚至周末也要上班。", "pinyin": "",
                     "uz": "U har kuni qo'shimcha ishlaydi, hatto shanba-yakshanba kunlari ham.",
                     "ru": "Он каждый день работает сверхурочно, даже в выходные.",
                     "tj": "Ӯ ҳар рӯз аз вақти кор зиёд кор мекунад, ҳатто охири ҳафта ҳам."},
                    {"zh": "她汉语说得很好，甚至比中国人还好。", "pinyin": "",
                     "uz": "U xitoycha juda yaxshi gapiradi, hatto xitoyliklardan ham yaxshiroq.",
                     "ru": "Она говорит по-китайски очень хорошо, даже лучше, чем китайцы.",
                     "tj": "Ӯ хитоӣ хеле хуб гап мезанад, ҳатто беҳтар аз хитоиҳо."},
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
                    {"prompt_uz": "pul ishlash", "prompt_ru": "зарабатывать деньги", "prompt_tj": "пул даровардан", "answer": "赚钱", "pinyin": "zhuàn qián"},
                    {"prompt_uz": "kafolat bermoq", "prompt_ru": "гарантировать", "prompt_tj": "кафолат додан", "answer": "保证", "pinyin": "bǎozhèng"},
                    {"prompt_uz": "eslatmoq", "prompt_ru": "напоминать", "prompt_tj": "ёдоварӣ кардан", "answer": "提醒", "pinyin": "tíxǐng"},
                    {"prompt_uz": "daromad", "prompt_ru": "доход", "prompt_tj": "даромад", "answer": "收入", "pinyin": "shōurù"},
                    {"prompt_uz": "muvaffaqiyat", "prompt_ru": "успех", "prompt_tj": "муваффақият", "answer": "成功", "pinyin": "chénggōng"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский эквивалент следующих слов:",
                "instruction_tj": "Муодили ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "以为", "prompt_ru": "以为", "prompt_tj": "以为", "answer": "o'ylash (noto'g'ri bo'lib chiqadigan)", "pinyin": "yǐwéi"},
                    {"prompt_uz": "原来", "prompt_ru": "原来", "prompt_tj": "原来", "answer": "aslida, demak", "pinyin": "yuánlái"},
                    {"prompt_uz": "甚至", "prompt_ru": "甚至", "prompt_tj": "甚至", "answer": "hatto, shu qadar", "pinyin": "shènzhì"},
                    {"prompt_uz": "起初", "prompt_ru": "起初", "prompt_tj": "起初", "answer": "boshida, dastlab", "pinyin": "qǐchū"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (以为、原来、并、起初、甚至):",
                "instruction_ru": "Выберите подходящее слово (以为、原来、并、起初、甚至):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (以为、原来、并、起初、甚至):",
                "items": [
                    {"prompt_uz": "我______他已经回国了，______他还在这儿。", "prompt_ru": "我______他已经回国了，______他还在这儿。", "prompt_tj": "我______他已经回国了，______他还在这儿。", "answer": "以为 / 原来", "pinyin": "yǐwéi / yuánlái"},
                    {"prompt_uz": "他______没有生气，只是有点累。", "prompt_ru": "他______没有生气，只是有点累。", "prompt_tj": "他______没有生气，只是有点累。", "answer": "并", "pinyin": "bìng"},
                    {"prompt_uz": "______，我不喜欢吃辣的，现在______爱上了四川菜。", "prompt_ru": "______，我不喜欢吃辣的，现在______爱上了四川菜。", "prompt_tj": "______，我不喜欢吃辣的，现在______爱上了四川菜。", "answer": "起初 / 甚至", "pinyin": "qǐchū / shènzhì"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["赚钱", "保证", "提醒", "收入", "成功"]},
            {"no": 2, "answers": ["o'ylash (noto'g'ri bo'lib chiqadigan)", "aslida, demak", "hatto, shu qadar", "boshida, dastlab"]},
            {"no": 3, "answers": ["以为 / 原来", "并", "起初 / 甚至"]},
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
                "words": ["以为", "原来", "甚至", "努力"],
                "example": "起初我以为这份工作很好，原来需要甚至周末也工作。",
            },
            {
                "no": 2,
                "instruction_uz": "'并不/并没...' va '甚至...' qoliplaridan foydalanib har biridan 2 ta gap tuzing.",
                "instruction_ru": "Составьте по 2 предложения с конструкциями '并不/并没...' и '甚至...'.",
                "instruction_tj": "Бо истифода аз қолипҳои '并不/并没...' ва '甚至...' аз ҳар кадоме 2 ҷумла созед.",
                "topic_uz": "ish va pul topish mavzusida",
                "topic_ru": "на тему работы и заработка",
                "topic_tj": "дар мавзӯи кор ва пул даровардан",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Sizning karyera va hayot maqsadlaringiz qanday? 你的职业理想是什么？",
                "topic_ru": "Каковы ваши карьерные и жизненные цели? 你的职业理想是什么？",
                "topic_tj": "Ҳадафҳои касбӣ ва зиндагии шумо чӣ гунаанд? 你的职业理想是什么？",
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
