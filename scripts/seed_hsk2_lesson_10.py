import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 10,
    "lesson_code": "HSK2-L10",
    "title": "别找了，手机在桌子上呢",
    "goal": json.dumps({"uz": "Buyruq gaplarini ('别……了'), 'duì' old ko'makchisini va 'zhèngzài' davom ko'rsatkichini ishlatishni o'rganish.", "ru": "Научиться использовать побудительные предложения ('别……了'), предлог 'duì' и показатель продолжения 'zhèngzài'.", "tj": "Омӯзиши истифодаи ҷумлаҳои фармоишӣ ('别……了'), пешоянди 'duì' ва нишондиҳандаи давомнокии 'zhèngzài'."}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda biz birovga biror narsani to'xtatishni aytish, sog'liq va kundalik hayot mavzularida gaplashishni o'rganamiz. 'Bié……le' (…qilma) va 'búyào……le' (…qilma) konstruktsiyalari orqali buyruq gaplari, shuningdek 'duì' old ko'makchisi bilan foydali iboralar hosil qilamiz.", "ru": "В этом уроке мы учимся говорить кому-то прекратить что-либо, общаться на темы здоровья и повседневной жизни. Формируем побудительные предложения через конструкции 'bié……le' (не делай) и 'búyào……le' (не делай), а также полезные выражения с предлогом 'duì'.", "tj": "Дар ин дарс мо ёд мегирем, ки ба касе гӯем, ки чизеро қатъ кунад, дар бораи саломатӣ ва ҳаёти рӯзмарра гап занем. Тавассути сохторҳои 'bié……le' (накун) ва 'búyào……le' (накун) ҷумлаҳои фармоишӣ, инчунин ибораҳои фоиданок бо пешоянди 'duì' месозем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "课",   "pinyin": "kè",       "pos": "n.",    "uz": "dars, mashg'ulot",                         "ru": "урок, занятие",                            "tj": "дарс, машғулот"},
        {"no": 2, "zh": "帮助", "pinyin": "bāngzhù",  "pos": "v.",    "uz": "yordam bermoq",                            "ru": "помогать",                                 "tj": "кӯмак кардан"},
        {"no": 3, "zh": "别",   "pinyin": "bié",       "pos": "adv.", "uz": "…qilma (taqiq)",                           "ru": "не (запрет)",                              "tj": "накун (манъ)"},
        {"no": 4, "zh": "哥哥", "pinyin": "gēge",      "pos": "n.",    "uz": "aka",                                      "ru": "старший брат",                             "tj": "бародари калонӣ"},
        {"no": 5, "zh": "鸡蛋", "pinyin": "jīdàn",    "pos": "n.",    "uz": "tuxum",                                    "ru": "яйцо",                                     "tj": "тухм"},
        {"no": 6, "zh": "西瓜", "pinyin": "xīguā",    "pos": "n.",    "uz": "tarvuz",                                   "ru": "арбуз",                                    "tj": "тарбуз"},
        {"no": 7, "zh": "正在", "pinyin": "zhèngzài", "pos": "adv.", "uz": "hozir …qilmoqda (davom etayotgan harakat)","ru": "сейчас … (продолжающееся действие)",       "tj": "ҳоло …қилмоқда (амали ҷорӣ)"},
        {"no": 8, "zh": "手机", "pinyin": "shǒujī",   "pos": "n.",    "uz": "mobil telefon",                            "ru": "мобильный телефон",                        "tj": "телефони мобилӣ"},
        {"no": 9,  "zh": "洗",   "pinyin": "xǐ",       "pos": "v.",    "uz": "yuvmoq",                                   "ru": "мыть, стирать",                            "tj": "шустан"},
        {"no": 10, "zh": "药",   "pinyin": "yào",      "pos": "n.",    "uz": "dori-darmon",                              "ru": "лекарство",                                "tj": "дору"},
        {"no": 11, "zh": "身体", "pinyin": "shēntǐ",   "pos": "n.",    "uz": "tana, sog'liq",                            "ru": "тело, здоровье",                           "tj": "тан, саломатӣ"},
        {"no": 12, "zh": "准备", "pinyin": "zhǔnbèi",  "pos": "v.",    "uz": "tayyorlanmoq, tayyorlamoq",                "ru": "готовиться, подготавливать",               "tj": "омода шудан, тайёр кардан"},
        {"no": 13, "zh": "报纸", "pinyin": "bàozhǐ",   "pos": "n.",    "uz": "gazeta",                                   "ru": "газета",                                   "tj": "рӯзнома"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "别看电视了，明天上午还有汉语课呢。", "pinyin": "Bié kàn diànshì le，míngtiān shàngwǔ hái yǒu Hànyǔ kè ne.", "uz": "Televizor ko'rishni bas qil, ertaga ertalab yana xitoy tili darsi bor.", "ru": "Хватит смотреть телевизор, завтра утром ещё есть урок китайского.", "tj": "Дигар телевизор нагард, фардо субҳ боз дарси чинӣ аст."},
                {"speaker": "B", "zh": "看电视对学汉语有帮助。", "pinyin": "Kàn diànshì duì xué Hànyǔ yǒu bāngzhù.", "uz": "Televizor ko'rish xitoy tili o'rganishga yordam beradi.", "ru": "Просмотр телевизора помогает в изучении китайского.", "tj": "Тамошои телевизор дар омӯхтани чинӣ кӯмак мекунад."},
                {"speaker": "A", "zh": "明天的课你都准备好了吗？", "pinyin": "Míngtiān de kè nǐ dōu zhǔnbèi hǎo le ma?", "uz": "Ertangi darsga to'liq tayyorlandingizmi?", "ru": "Ты полностью подготовился к завтрашнему уроку?", "tj": "Оё ту ба дарси фардо пурра омода шудӣ?"},
                {"speaker": "B", "zh": "都准备好了。", "pinyin": "Dōu zhǔnbèi hǎo le.", "uz": "Hammasi tayyor.", "ru": "Всё готово.", "tj": "Ҳама омода."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Kasalxonada",
            "scene_ru": "В больнице",
            "scene_tj": "Дар беморхона",
            "dialogue": [
                {"speaker": "A", "zh": "别看报纸了，医生说你要多休息。", "pinyin": "Bié kàn bàozhǐ le，yīshēng shuō nǐ yào duō xiūxi.", "uz": "Gazeta o'qishni bas qil, shifokor ko'proq dam olishing kerak dedi.", "ru": "Хватит читать газету, доктор сказал, что тебе нужно больше отдыхать.", "tj": "Дигар рӯзнома нахон, духтур гуфт, ки ту бояд бештар истироҳат кунӣ."},
                {"speaker": "B", "zh": "好，不看了。给我一杯茶吧。", "pinyin": "Hǎo，bù kàn le. Gěi wǒ yì bēi chá ba.", "uz": "Yaxshi, o'qimayman. Menga bir piyola choy bering.", "ru": "Хорошо, не буду читать. Дайте мне чашку чая.", "tj": "Хуб, нахонам. Ба ман як коса чой диҳед."},
                {"speaker": "A", "zh": "医生说吃药后的两个小时不要喝茶。", "pinyin": "Yīshēng shuō chī yàohòu de liǎng ge xiǎoshí búyào hē chá.", "uz": "Shifokor dori ichganidan keyin ikki soat choy ichmaslik kerak dedi.", "ru": "Доктор сказал, что два часа после приёма лекарства нельзя пить чай.", "tj": "Духтур гуфт, ки ду соат баъд аз доруи хӯрдан чой нӯшидан мумкин нест."},
                {"speaker": "B", "zh": "医生还说什么了？", "pinyin": "Yīshēng hái shuō shénme le?", "uz": "Shifokor yana nima dedi?", "ru": "Что ещё сказал доктор?", "tj": "Духтур боз чӣ гуфт?"},
                {"speaker": "A", "zh": "医生让你听我的。", "pinyin": "Yīshēng ràng nǐ tīng wǒ de.", "uz": "Shifokor menga quloq soling dedi.", "ru": "Доктор сказал слушаться меня.", "tj": "Духтур гуфт, ки ба ман гӯш кун."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "你怎么买了这么多东西啊？", "pinyin": "Nǐ zěnme mǎi le zhème duō dōngxi a?", "uz": "Nima uchun bu qadar ko'p narsa sotib oldingiz?", "ru": "Почему ты купил так много всего?", "tj": "Чаро ту ин қадар зиёд чиз харидӣ?"},
                {"speaker": "B", "zh": "哥哥今天中午回来吃饭。", "pinyin": "Gēge jīntiān zhōngwǔ huílái chīfàn.", "uz": "Aka bugun tushlikka keladi.", "ru": "Старший брат сегодня придёт на обед.", "tj": "Бародари калонӣ имрӯз барои нисфирӯзӣ меояд."},
                {"speaker": "A", "zh": "我看看买什么了。羊肉，鸡蛋，面条，西瓜……真不少！妈妈呢？", "pinyin": "Wǒ kànkan mǎi shénme le. Yángròu，jīdàn，miàntiáo，xīguā…… zhēn bù shǎo! Māma ne?", "uz": "Ko'ray-chi nima olibsiz. Qo'y go'shti, tuxum, erişta, tarvuz… juda ko'p! Ona-chi?", "ru": "Дай посмотрю, что купил. Баранина, яйца, лапша, арбуз… действительно много! А мама?", "tj": "Биё бинам чӣ харидӣ. Гӯшти гӯсфанд, тухм, лоғмон, тарбуз… воқеан зиёд! Модар чӣ?"},
                {"speaker": "B", "zh": "正在准备午饭呢！", "pinyin": "Zhèngzài zhǔnbèi wǔfàn ne!", "uz": "Hozir tushlikni tayyorlayapti!", "ru": "Сейчас готовит обед!", "tj": "Ҳоло нисфирӯзиро тайёр мекунад!"},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "你在找什么？", "pinyin": "Nǐ zài zhǎo shénme?", "uz": "Siz nima qidiryapsiz?", "ru": "Что ты ищешь?", "tj": "Ту чӣ мекобӣ?"},
                {"speaker": "B", "zh": "你看见我的手机了吗？白色的。", "pinyin": "Nǐ kànjian wǒ de shǒujī le ma? Báisè de.", "uz": "Mening telefonim ko'rdingizmi? Oq rangli.", "ru": "Ты видел мой телефон? Белый.", "tj": "Ту телефони маро дидӣ? Сафеди."},
                {"speaker": "A", "zh": "别找了，手机在桌子上呢，电脑旁边。", "pinyin": "Bié zhǎo le，shǒujī zài zhuōzi shang ne，diànnǎo pángbiān.", "uz": "Qidirishni bas qil, telefon stol ustida, kompyuter yonida.", "ru": "Хватит искать, телефон на столе, рядом с компьютером.", "tj": "Дигар накоб, телефон рӯи мизи аст, паҳлӯи компютер."},
                {"speaker": "B", "zh": "你看见我的衣服了吗？红色的那件。", "pinyin": "Nǐ kànjian wǒ de yīfu le ma? Hóngsè de nà jiàn.", "uz": "Kiyimlarimni ko'rdingizmi? O'sha qizil ranglisini.", "ru": "Ты видел мою одежду? Ту красную.", "tj": "Ту либосамро дидӣ? Онро, ки сурх аст."},
                {"speaker": "A", "zh": "那件衣服我帮你洗了，在外边呢。", "pinyin": "Nà jiàn yīfu wǒ bāng nǐ xǐ le，zài wàibian ne.", "uz": "O'sha kiyimni sizga yuvib qo'ydim, tashqarida.", "ru": "Я постирал ту одежду за тебя, она на улице.", "tj": "Ман он либосро барои ту шустам, берун аст."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "祈使句：不要……了；别……了",
            "title_uz": "Buyruq gapi: 不要……了; 别……了 (endi …qilma)",
            "title_ru": "Побудительное предложение: 不要……了; 别……了 (хватит, не делай)",
            "title_tj": "Ҷумлаи фармоишӣ: 不要……了; 别……了 (дигар накун)",
            "rule_uz": (
                "Biror harakatni to'xtatishni buyurish uchun 'bié……le' yoki 'búyào……le' ishlatiladi.\n"
                "Bu ikkalasi ham 'endi …qilma' ma'nosini beradi.\n"
                "'Bié' so'zlashuv tilida ko'proq qo'llanadi.\n"
                "Gap oxiridagi 'le' holatning o'zgarganligini yoki da'vatni kuchaytiradi."
            ),
            "rule_ru": (
                "Для приказания прекратить действие используется 'bié……le' или 'búyào……le'.\n"
                "Оба означают 'больше не делай, хватит'.\n"
                "'Bié' чаще используется в разговорной речи.\n"
                "Частица 'le' в конце предложения усиливает призыв или сигнализирует об изменении ситуации."
            ),
            "rule_tj": (
                "Барои дастур додан ба қатъи амал 'bié……le' ё 'búyào……le' истифода мешавад.\n"
                "Ҳар ду маъноии 'дигар накун' доранд.\n"
                "'Bié' дар забони гуфтугӯӣ бештар истифода мешавад.\n"
                "Ҷузъаи 'le' дар охири ҷумла даъватро тақвият медиҳад ё тағйири вазъиятро нишон медиҳад."
            ),
            "examples": [
                {"zh": "别看电视了，去睡觉吧。", "pinyin": "Bié kàn diànshì le, qù shuìjiào ba.", "uz": "Endi televizor ko'rma, uxlash vaqti.", "ru": "Хватит смотреть телевизор, иди спать.", "tj": "Дигар телевизор нагард, барав бихоб."},
                {"zh": "不要喝茶了，吃药吧。", "pinyin": "Búyào hē chá le, chī yào ba.", "uz": "Choy ichmay, dori ich.", "ru": "Не пей чай, прими лекарство.", "tj": "Дигар чой нанӯш, дору хӯр."},
            ]
        },
        {
            "no": 2,
            "title_zh": '介词"对"',
            "title_uz": "Old ko'makchi 对 (uchun, bo'yicha, nisbatan)",
            "title_ru": "Предлог 对 (для, по отношению к, относительно)",
            "title_tj": "Пешоянди 对 (барои, нисбат ба)",
            "rule_uz": (
                "'Duì' old ko'makchisi 'uchun, bo'yicha, nisbatan' ma'nolarini beradi.\n"
                "'A duì B (yǒu) C' ko'rinishida: A B uchun C (ta'sirga ega/yaxshi/yomon).\n"
                "Masalan: 看电视对眼睛不好 (televizor ko'rish ko'z uchun yaxshi emas)."
            ),
            "rule_ru": (
                "Предлог '对' означает 'для, по отношению к, относительно'.\n"
                "В конструкции 'A 对 B (有) C': A для B (имеет влияние/хорошо/плохо).\n"
                "Например: 看电视对眼睛不好 (смотреть телевизор вредно для глаз)."
            ),
            "rule_tj": (
                "Пешоянди '对' маъноии 'барои, нисбат ба'-ро медиҳад.\n"
                "Дар сохтори 'A 对 B (有) C': A барои B (таъсир дорад/хуб аст/бад аст).\n"
                "Масалан: 看电视对眼睛不好 (тамошои телевизор барои чашм зиёновар аст)."
            ),
            "examples": [
                {"zh": "看电视对学汉语有帮助。", "pinyin": "Kàn diànshì duì xué Hànyǔ yǒu bāngzhù.", "uz": "Televizor ko'rish xitoy tili o'rganishga yordam beradi.", "ru": "Просмотр телевизора помогает в изучении китайского.", "tj": "Тамошои телевизор дар омӯхтани чинӣ кӯмак мекунад."},
                {"zh": "早睡早起对身体好。", "pinyin": "Zǎo shuì zǎo qǐ duì shēntǐ hǎo.", "uz": "Erta yotib erta turish sog'liq uchun foydali.", "ru": "Ложиться и вставать рано полезно для здоровья.", "tj": "Барвақт хобидан ва барвақт хестан барои саломатӣ хуб аст."},
            ]
        },
        {
            "no": 3,
            "title_zh": "副词\"正在\"和语气助词\"呢\"",
            "title_uz": "'Zhèngzài' ravishi va 'ne' yuklama (davom etayotgan harakat)",
            "title_ru": "Наречие 'zhèngzài' и частица 'ne' (продолжающееся действие)",
            "title_tj": "Зарфи 'zhèngzài' ва зарраи 'ne' (амали ҷорӣ)",
            "rule_uz": (
                "'正在' ravishi fe'l oldidan kelib, harakatning aynan hozir davom etayotganini bildiradi.\n"
                "Ingliz tilidagi 'am/is/are …-ing' ga o'xshaydi.\n"
                "Gap oxiriga '呢' yuklama qo'shilsa, davom etayotgan holat yanada ta'kidlanadi.\n"
                "Tuzilish: 正在 + fe'l (+呢). Shuningdek, faqat '在 + fe'l' yoki 'fe'l + 着 + 呢' ham ishlatiladi."
            ),
            "rule_ru": (
                "Наречие '正在' стоит перед глаголом и указывает, что действие происходит прямо сейчас.\n"
                "Аналог английского 'am/is/are …-ing'.\n"
                "Если в конце добавляется частица '呢', продолжение состояния подчёркивается.\n"
                "Структура: 正在 + глагол (+呢). Также используется: 在 + глагол или глагол + 着 + 呢."
            ),
            "rule_tj": (
                "Зарфи '正在' пеш аз феъл меояд ва нишон медиҳад амал айни ҳол ҷараён дорад.\n"
                "Ба 'am/is/are …-ing' дар забони англисӣ монанд аст.\n"
                "Агар дар охири ҷумла зарраи '呢' илова шавад, ҷараёни ҳолат бештар таъкид мешавад.\n"
                "Сохтор: 正在 + феъл (+呢). Инчунин: 在 + феъл ё феъл + 着 + 呢 истифода мешавад."
            ),
            "examples": [
                {"zh": "妈妈正在准备午饭呢！", "pinyin": "Māma zhèngzài zhǔnbèi wǔfàn ne!", "uz": "Ona hozir tushlikni tayyorlayapti!", "ru": "Мама сейчас готовит обед!", "tj": "Модар ҳоло нисфирӯзиро тайёр мекунад!"},
                {"zh": "你在找什么？", "pinyin": "Nǐ zài zhǎo shénme?", "uz": "Siz nima qidiryapsiz?", "ru": "Что ты ищешь?", "tj": "Ту чӣ мекобӣ?"},
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
                {"prompt_uz": "telefon",       "prompt_ru": "мобильный телефон", "prompt_tj": "телефони мобилӣ",   "answer": "手机", "pinyin": "shǒujī"},
                {"prompt_uz": "tuxum",          "prompt_ru": "яйцо",              "prompt_tj": "тухм",              "answer": "鸡蛋", "pinyin": "jīdàn"},
                {"prompt_uz": "tarvuz",         "prompt_ru": "арбуз",             "prompt_tj": "тарбуз",            "answer": "西瓜", "pinyin": "xīguā"},
                {"prompt_uz": "yuvmoq",         "prompt_ru": "мыть, стирать",     "prompt_tj": "шустан",            "answer": "洗",   "pinyin": "xǐ"},
                {"prompt_uz": "yordam bermoq",  "prompt_ru": "помогать",          "prompt_tj": "кӯмак кардан",      "answer": "帮助", "pinyin": "bāngzhù"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Ҷойи холиро пур кунед:",
            "items": [
                {"prompt_uz": "你的病已经好了，___找了。（别）", "prompt_ru": "你的病已经好了，___找了。（别）", "prompt_tj": "你的病已经好了，___找了。（别）", "answer": "别", "pinyin": "bié"},
                {"prompt_uz": "___看电视了，明天还要上课呢。（别）", "prompt_ru": "___看电视了，明天还要上课呢。（别）", "prompt_tj": "___看电视了，明天还要上课呢。（别）", "answer": "别", "pinyin": "bié"},
                {"prompt_uz": "跑步___身体很好。（对）", "prompt_ru": "跑步___身体很好。（对）", "prompt_tj": "跑步___身体很好。（对）", "answer": "对", "pinyin": "duì"},
                {"prompt_uz": "妈妈___准备午饭呢。（正在）", "prompt_ru": "妈妈___准备午饭呢。（正在）", "prompt_tj": "妈妈___准备午饭呢。（正在）", "answer": "正在", "pinyin": "zhèngzài"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_native",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на русский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони тоҷикӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "别找了，手机在桌子上呢，电脑旁边。", "prompt_ru": "别找了，手机在桌子上呢，电脑旁边。", "prompt_tj": "别找了，手机在桌子上呢，电脑旁边。", "answer": "Qidirishni bas qil, telefon stol ustida, kompyuter yonida.", "pinyin": "Bié zhǎo le, shǒujī zài zhuōzi shang ne, diànnǎo pángbiān."},
                {"prompt_uz": "看电视对学汉语有帮助。", "prompt_ru": "看电视对学汉语有帮助。", "prompt_tj": "看电视对学汉语有帮助。", "answer": "Televizor ko'rish xitoy tili o'rganishga yordam beradi.", "pinyin": "Kàn diànshì duì xué Hànyǔ yǒu bāngzhù."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["手机", "鸡蛋", "西瓜", "洗", "帮助"]},
        {"no": 2, "answers": ["别", "别", "对", "正在"]},
        {"no": 3, "answers": [
            "Qidirishni bas qil, telefon stol ustida, kompyuter yonida.",
            "Televizor ko'rish xitoy tili o'rganishga yordam beradi.",
        ]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib 'bié……le' yoki 'búyào……le' bilan jumla tuzing: 看电视, 喝咖啡, 找, 吃药",
            "instruction_ru": "Составьте предложения с 'bié……le' или 'búyào……le', используя: 看电视, 喝咖啡, 找, 吃药",
            "instruction_tj": "Бо истифода аз 'bié……le' ё 'búyào……le' ҷумла тартиб диҳед: 看电视, 喝咖啡, 找, 吃药",
            "words": ["别……了", "不要……了"],
            "example": "别喝咖啡了，喝茶吧。",
        },
        {
            "no": 2,
            "instruction_uz": "'Duì' old ko'makchisidan foydalanib, sog'lig'ingiz uchun nima foydali yoki zararli ekanini yozing (kamida 3 jumla).",
            "instruction_ru": "Используя предлог 'duì', напишите, что полезно или вредно для вашего здоровья (не менее 3 предложений).",
            "instruction_tj": "Бо истифода аз пешоянди 'duì' нависед, ки чӣ барои саломатии шумо фоиданок ё зиёновар аст (на камтар аз 3 ҷумла).",
            "topic_uz": "Sog'liq uchun foydali va zararli narsalar",
            "topic_ru": "Полезные и вредные для здоровья вещи",
            "topic_tj": "Чизҳои фоиданок ва зиёновар барои саломатӣ",
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
