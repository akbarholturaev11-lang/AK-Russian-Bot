import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 7,
    "lesson_code": "HSK3-L07",
    "title": json.dumps({"zh": "我跟她都认识五年了", "uz": "Men u bilan tanishganimga besh yil bo'ldi", "ru": "Мы знакомы уже пять лет", "tj": "Ман бо вай панҷ сол боз ошно ҳастам"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "Vaqt davomiyligini ifodalash, qiziqishni bildirish va soat vaqtlarini o'rganish", "ru": "Выражать продолжительность времени, интерес и обозначение времени", "tj": "Ифода кардани давомнокии вақт, изҳор кардани шавқ ва таъйин кардани вақт"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda vaqt davomiyligini, qiziqishni bildirish usullarini va soatning chorak, yarim kabi iboralarini o'rganamiz.", "ru": "В этом уроке мы изучим выражение продолжительности времени, выражение интереса и обозначение четверти и половины в часах.", "tj": "Дар ин дарс мо ифодаи давомнокии вақт, изҳори шавқ ва ибораҳои чорак ва нимро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "同事", "pinyin": "tóngshì", "pos": "n", "uz": "hamkasb", "ru": "коллега", "tj": "ҳамкор"},
        {"no": 2, "zh": "以前", "pinyin": "yǐqián", "pos": "n", "uz": "ilgari, avval", "ru": "раньше, прежде", "tj": "пештар, қабл"},
        {"no": 3, "zh": "银行", "pinyin": "yínháng", "pos": "n", "uz": "bank", "ru": "банк", "tj": "бонк"},
        {"no": 4, "zh": "久", "pinyin": "jiǔ", "pos": "adj", "uz": "uzoq (vaqt)", "ru": "долго", "tj": "дер, дуру дароз"},
        {"no": 5, "zh": "感兴趣", "pinyin": "gǎn xìngqù", "pos": "v", "uz": "qiziqish his qilmoq", "ru": "интересоваться", "tj": "шавқ доштан"},
        {"no": 6, "zh": "结婚", "pinyin": "jiéhūn", "pos": "v", "uz": "uylanmoq / turmushga chiqmoq", "ru": "жениться / выйти замуж", "tj": "издивоҷ кардан"},
        {"no": 7, "zh": "欢迎", "pinyin": "huānyíng", "pos": "v", "uz": "xush kelibsiz, qabul qilmoq", "ru": "добро пожаловать; принимать", "tj": "хуш омадед; истиқбол кардан"},
        {"no": 8, "zh": "迟到", "pinyin": "chídào", "pos": "v", "uz": "kechikmoq", "ru": "опаздывать", "tj": "дер омадан"},
        {"no": 9, "zh": "半", "pinyin": "bàn", "pos": "num", "uz": "yarim", "ru": "половина", "tj": "ним"},
        {"no": 10, "zh": "接", "pinyin": "jiē", "pos": "v", "uz": "kutib olmoq; qabul qilmoq", "ru": "встречать; принимать", "tj": "пешвоз гирифтан"},
        {"no": 11, "zh": "刻", "pinyin": "kè", "pos": "m", "uz": "chorak soat (15 daqiqa)", "ru": "четверть часа (15 минут)", "tj": "чорак соат (15 дақиқа)"},
        {"no": 12, "zh": "差", "pinyin": "chà", "pos": "v", "uz": "kam bo'lmoq, yetishmovchi", "ru": "не хватать, до (времени)", "tj": "кам будан"},
        {"no": 13, "zh": "周末", "pinyin": "zhōumò", "pos": "n", "uz": "dam olish kuni (shanba-yakshanba)", "ru": "выходные дни", "tj": "охири ҳафта"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Eski hamkasblar uchrashishi", "ru": "Встреча старых коллег", "tj": "Мулоқоти ҳамкорони қадимӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "你好！好久不见，你还好吗？", "pinyin": "Nǐ hǎo! Hǎojiǔ bújiàn, nǐ hái hǎo ma?", "uz": "Salom! Ko'rishmaganimizga ancha bo'ldi, yaxshimisiz?", "ru": "Привет! Давно не виделись, как ты?", "tj": "Салом! Муддатест надидаем, чӣ ҳол доред?"},
                {"speaker": "B", "zh": "挺好的！我们认识多久了？", "pinyin": "Tǐng hǎo de! Wǒmen rènshi duō jiǔ le?", "uz": "Yaxshi! Biz tanishganimizga qancha bo'ldi?", "ru": "Всё хорошо! Сколько лет мы уже знакомы?", "tj": "Хуб! Мо чанд вақт боз ошно ҳастем?"},
                {"speaker": "A", "zh": "我跟你都认识五年了，时间过得真快！", "pinyin": "Wǒ gēn nǐ dōu rènshi wǔ nián le, shíjiān guò de zhēn kuài!", "uz": "Men siz bilan tanishganimizga besh yil bo'ldi, vaqt juda tez o'tadi!", "ru": "Мы с тобой знакомы уже пять лет, время летит так быстро!", "tj": "Ман бо шумо панҷ сол боз ошно ҳастем, вақт чӣ қадар тез мегузарад!"},
                {"speaker": "B", "zh": "是啊，你现在在哪儿工作？", "pinyin": "Shì a, nǐ xiànzài zài nǎr gōngzuò?", "uz": "Ha, siz hozir qayerda ishlaysiz?", "ru": "Да, ты сейчас где работаешь?", "tj": "Ҳа, шумо ҳоло дар куҷо кор мекунед?"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Bankdagi ish haqida", "ru": "О работе в банке", "tj": "Дар бораи кор дар бонк"},
            "dialogue": [
                {"speaker": "A", "zh": "我在银行工作，做了三年了。", "pinyin": "Wǒ zài yínháng gōngzuò, zuò le sān nián le.", "uz": "Men bankda ishlayman, uch yil bo'ldi.", "ru": "Я работаю в банке, уже три года.", "tj": "Ман дар бонк кор мекунам, се сол шуд."},
                {"speaker": "B", "zh": "你对这份工作感兴趣吗？", "pinyin": "Nǐ duì zhè fèn gōngzuò gǎn xìngqù ma?", "uz": "Siz bu ishga qiziqasizmi?", "ru": "Вас интересует эта работа?", "tj": "Оё шумо ба ин кор шавқ доред?"},
                {"speaker": "A", "zh": "很感兴趣！我对金融特别感兴趣。", "pinyin": "Hěn gǎn xìngqù! Wǒ duì jīnróng tèbié gǎn xìngqù.", "uz": "Juda qiziqaman! Men moliyaga ayniqsa qiziqaman.", "ru": "Очень интересует! Я особенно интересуюсь финансами.", "tj": "Хеле шавқ дорам! Ман ба молия хусусан шавқ дорам."},
                {"speaker": "B", "zh": "太好了！我以前也想在银行工作。", "pinyin": "Tài hǎo le! Wǒ yǐqián yě xiǎng zài yínháng gōngzuò.", "uz": "Juda yaxshi! Men ham ilgari bankda ishlashni xohlardim.", "ru": "Отлично! Я раньше тоже хотел работать в банке.", "tj": "Олӣ! Ман ҳам қабл мехостам дар бонк кор кунам."}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "To'y yangiliklari", "ru": "Свадебные новости", "tj": "Хабарҳои арӯсӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "对了，你结婚了吗？", "pinyin": "Duì le, nǐ jiéhūn le ma?", "uz": "Ha aytgancha, siz uylandingizmi?", "ru": "Кстати, ты женился?", "tj": "Дар ҳар сурат, шумо издивоҷ кардед?"},
                {"speaker": "B", "zh": "结婚两年了，你呢？", "pinyin": "Jiéhūn liǎng nián le, nǐ ne?", "uz": "Ikki yil bo'ldi, siz-chi?", "ru": "Уже два года в браке, а ты?", "tj": "Ду сол шуд, шумо чӣ?"},
                {"speaker": "A", "zh": "我还没结婚，欢迎你们来我的婚礼！", "pinyin": "Wǒ hái méi jiéhūn, huānyíng nǐmen lái wǒ de hūnlǐ!", "uz": "Men hali uylanmadim, to'yimga marhamat keling!", "ru": "Я ещё не женился, добро пожаловать на мою свадьбу!", "tj": "Ман ҳанӯз издивоҷ накардаам, ба арӯсиям хуш омадед!"},
                {"speaker": "B", "zh": "好的，一定去！什么时候？", "pinyin": "Hǎo de, yīdìng qù! Shénme shíhou?", "uz": "Yaxshi, albatta boraman! Qachon?", "ru": "Хорошо, обязательно придём! Когда?", "tj": "Хуб, албатта меоям! Кай?"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Poyezdga kechikish", "ru": "Опоздание на поезд", "tj": "Дер расидан ба қатора"},
            "dialogue": [
                {"speaker": "A", "zh": "火车几点开？", "pinyin": "Huǒchē jǐ diǎn kāi?", "uz": "Poyezd soat nechada jo'naydi?", "ru": "Во сколько отправляется поезд?", "tj": "Қатора соати чанд рафт мекунад?"},
                {"speaker": "B", "zh": "差一刻八点，我们快点儿吧！", "pinyin": "Chà yī kè bā diǎn, wǒmen kuài diǎnr ba!", "uz": "Soat sakkizga chorak qoldi, tezroq boraylik!", "ru": "Без четверти восемь, давай поторопимся!", "tj": "Соати ҳашт чорак монда, зудтар биравем!"},
                {"speaker": "A", "zh": "你去接他们，我去买票。", "pinyin": "Nǐ qù jiē tāmen, wǒ qù mǎi piào.", "uz": "Siz ularni kutib oling, men chipta sotib olaman.", "ru": "Ты встречай их, а я куплю билеты.", "tj": "Шумо онҳоро пешвоз гиред, ман чиптаро мехарам."},
                {"speaker": "B", "zh": "好，但是别迟到，半小时后在这儿见！", "pinyin": "Hǎo, dànshì bié chídào, bàn xiǎoshí hòu zài zhèr jiàn!", "uz": "Yaxshi, lekin kechikma, yarim soatdan keyin shu yerda ko'rishamiz!", "ru": "Хорошо, но не опаздывай, через полчаса встретимся здесь!", "tj": "Хуб, аммо дер наоед, баъди ним соат дар ин ҷо вомехӯрем!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "时段的表达：V + 了 + 时段 + 了",
            "title_uz": "Vaqt davomiyligini ifodalash: F + le + muddat + le",
            "title_ru": "Выражение продолжительности: Гл + 了 + период + 了",
            "title_tj": "Ифодаи давомнокии вақт: Ф + 了 + муддат + 了",
            "rule_uz": "Biror harakat qancha davom etganini bildirishda 'V + 了 + vaqt davomiyligi + 了' tuzilmasi ishlatiladi. Birinchi 了 harakatning tugaganini, ikkinchisi hozirgi holatni bildiradi.",
            "rule_ru": "Для выражения продолжительности действия используется конструкция 'Гл + 了 + период времени + 了'. Первое 了 обозначает завершённость действия, второе — текущее состояние.",
            "rule_tj": "Барои ифодаи давомнокии амал сохтори 'Ф + 了 + муддати вақт + 了' истифода мешавад. Аввалин 了 тамомшавии амалро, дуввумаш ҳолати кунуниро нишон медиҳад.",
            "examples": [
                {"zh": "我们认识五年了。", "pinyin": "Wǒmen rènshi wǔ nián le.", "uz": "Biz tanishganimizga besh yil bo'ldi.", "ru": "Мы знакомы уже пять лет.", "tj": "Мо панҷ сол боз ошно ҳастем."},
                {"zh": "他在银行工作三年了。", "pinyin": "Tā zài yínháng gōngzuò sān nián le.", "uz": "U bankda uch yildan beri ishlaydi.", "ru": "Он работает в банке уже три года.", "tj": "Вай се сол боз дар бонк кор мекунад."}
            ]
        },
        {
            "no": 2,
            "title_zh": "对……感兴趣",
            "title_uz": "…ga qiziqish his qilmoq",
            "title_ru": "Интересоваться …",
            "title_tj": "Ба … шавқ доштан",
            "rule_uz": "'对……感兴趣' - biror narsaga qiziqishni ifodalash uchun ishlatiladi. '对' + ob'ekt + '感兴趣' tuzilmasi mavjud. '特别感兴趣' esa 'ayniqsa qiziqish' ma'nosini beradi.",
            "rule_ru": "'对……感兴趣' используется для выражения интереса к чему-либо. Структура: '对' + объект + '感兴趣'. '特别感兴趣' означает 'особенно интересоваться'.",
            "rule_tj": "'对……感兴趣' барои ифодаи шавқ ба чизе истифода мешавад. Сохтор: '对' + объект + '感兴趣'. '特别感兴趣' маънои 'хусусан шавқ доштан'-ро дорад.",
            "examples": [
                {"zh": "我对音乐很感兴趣。", "pinyin": "Wǒ duì yīnyuè hěn gǎn xìngqù.", "uz": "Men musiqaga juda qiziqaman.", "ru": "Мне очень интересна музыка.", "tj": "Ман ба мусиқӣ хеле шавқ дорам."},
                {"zh": "她对历史特别感兴趣。", "pinyin": "Tā duì lìshǐ tèbié gǎn xìngqù.", "uz": "U tarixga ayniqsa qiziqadi.", "ru": "Она особенно интересуется историей.", "tj": "Вай ба таърих хусусан шавқ дорад."}
            ]
        },
        {
            "no": 3,
            "title_zh": "\"半\"\"刻\"\"差\"表示时间",
            "title_uz": "\"Yarim\", \"chorak\" va \"kam\" vaqt ifodalovchi so'zlar",
            "title_ru": "\"Половина\", \"четверть\" и \"без\" для обозначения времени",
            "title_tj": "\"Ним\", \"чорак\" ва \"кам\" барои ифодаи вақт",
            "rule_uz": "Soat vaqtini ifodalashda: '半' = soat va yarim (masalan: 两点半 = 2:30), '刻' = 15 daqiqa (一刻 = :15, 三刻 = :45), '差' = vaqtdan oldin 'kam' (差五分八点 = 7:55).",
            "rule_ru": "Для обозначения времени: '半' = полчаса (两点半 = 2:30), '刻' = 15 минут (一刻 = :15, 三刻 = :45), '差' = без (差五分八点 = без пяти восемь = 7:55).",
            "rule_tj": "Барои таъйин кардани вақт: '半' = ним соат (两点半 = 2:30), '刻' = 15 дақиқа (一刻 = :15, 三刻 = :45), '差' = кам (差五分八点 = панҷ дақиқа ба ҳашт = 7:55).",
            "examples": [
                {"zh": "现在差一刻八点。", "pinyin": "Xiànzài chà yī kè bā diǎn.", "uz": "Hozir soat sakkizga chorak qoldi (7:45).", "ru": "Сейчас без четверти восемь (7:45).", "tj": "Ҳоло чорак ба ҳашт монда (7:45)."},
                {"zh": "我们三点半见面吧。", "pinyin": "Wǒmen sān diǎn bàn jiànmiàn ba.", "uz": "Biz soat uch yarimda uchrashaylik.", "ru": "Давай встретимся в половине четвёртого.", "tj": "Биё соати се ва ним вохӯрем."}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Biz tanishganimizga besh yil bo'ldi.", "ru": "Мы знакомы уже пять лет.", "tj": "Мо панҷ сол боз ошно ҳастем."},
                {"no": 2, "uz": "Men musiqaga juda qiziqaman.", "ru": "Мне очень интересна музыка.", "tj": "Ман ба мусиқӣ хеле шавқ дорам."},
                {"no": 3, "uz": "Hozir soat sakkizga chorak qoldi.", "ru": "Сейчас без четверти восемь.", "tj": "Ҳоло чорак ба ҳашт монда."},
                {"no": 4, "uz": "Kechikma, yarım soatdan keyin ko'rishamiz!", "ru": "Не опаздывай, встретимся через полчаса!", "tj": "Дер наоед, баъди ним соат вомехӯрем!"},
                {"no": 5, "uz": "U tarixga ayniqsa qiziqadi.", "ru": "Она особенно интересуется историей.", "tj": "Вай ба таърих хусусан шавқ дорад."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "我们认识___年了。", "sentence_uz": "Biz tanishganimizga ___ yil bo'ldi.", "sentence_ru": "Мы знакомы уже ___ лет.", "sentence_tj": "Мо ___ сол боз ошно ҳастем.", "hint": "пять / besh / панҷ"},
                {"no": 2, "sentence_zh": "她___音乐特别感兴趣。", "sentence_uz": "U musiqaga ayniqsa ___.", "sentence_ru": "Она особенно ___ музыкой.", "sentence_tj": "Вай ба мусиқӣ хусусан ___.", "hint": "对 / ga qiziqadi / шавқ дорад"},
                {"no": 3, "sentence_zh": "现在___一刻八点。", "sentence_uz": "Hozir soat sakkizga chorak ___.", "sentence_ru": "Сейчас ___ четверти восемь.", "sentence_tj": "Ҳоло ___ ба ҳашт чорак монда.", "hint": "差 / qoldi / монда"},
                {"no": 4, "sentence_zh": "我们三点___见面。", "sentence_uz": "Biz soat uch ___ uchrashaylik.", "sentence_ru": "Давай встретимся в ___ четвёртого.", "sentence_tj": "Биё соати се ___ вохӯрем.", "hint": "半 / yarim / ва ним"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "你对这份工作感兴趣吗？", "pinyin": "Nǐ duì zhè fèn gōngzuò gǎn xìngqù ma?"},
                {"no": 2, "zh": "差五分两点，我们快点儿走吧！", "pinyin": "Chà wǔ fēn liǎng diǎn, wǒmen kuài diǎnr zǒu ba!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "我们认识五年了。"},
                {"no": 2, "zh": "我对音乐很感兴趣。"},
                {"no": 3, "zh": "现在差一刻八点。"},
                {"no": 4, "zh": "别迟到，半小时后见！"},
                {"no": 5, "zh": "她对历史特别感兴趣。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "五"},
                {"no": 2, "answer": "对"},
                {"no": 3, "answer": "差"},
                {"no": 4, "answer": "半"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Siz bu ishga qiziqasizmi?", "ru": "Вас интересует эта работа?", "tj": "Оё шумо ба ин кор шавқ доред?"},
                {"no": 2, "uz": "Soat ikkiga besh daqiqa qoldi, tezroq yuraylik!", "ru": "Без пяти два, давай поторопимся!", "tj": "Панҷ дақиқа ба ду монда, зудтар биравем!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "Bugun tanishingiz bilan qancha vaqtdan beri tanishligingizni aytib, 5 ta gap tuzing (V+了+vaqt+了 tuzilmasini ishlating).", "ru": "Составьте 5 предложений о том, как долго вы знакомы с кем-то, используя конструкцию V+了+период+了.", "tj": "5 ҷумла тартиб диҳед, ки чанд муддат боз бо касе ошно ҳастед (сохтори V+了+муддат+了 истифода баред)."},
        {"task_no": 2, "uz": "'对……感兴趣' tuzilmasidan foydalanib, o'z qiziqishlaringiz haqida 3 ta gap yozing va soat vaqtlarini ham qo'shing.", "ru": "Напишите 3 предложения о своих интересах, используя '对……感兴趣', и добавьте обозначения времени (半/刻/差).", "tj": "3 ҷумла дар бораи шавқҳои худ бо '对……感兴趣' нависед ва нишондоди вақт (半/刻/差) ҳам илова кунед."}
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
