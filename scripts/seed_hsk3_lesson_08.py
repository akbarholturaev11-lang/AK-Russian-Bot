import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 8,
    "lesson_code": "HSK3-L08",
    "title": json.dumps({"zh": "你去哪儿我就去哪儿", "uz": "Siz qayerga borsangiz, men ham boraman", "ru": "Куда ты, туда и я", "tj": "Шумо ба куҷо равед, ман ҳам меравам"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "Shartli bog'lovchi jumlalar, qayta bajarish va umumlashtirish iboralarini o'rganish", "ru": "Изучить условные предложения, повторное действие и обобщение", "tj": "Омӯхтани ҷумлаҳои шартӣ, такрори амал ва умумикунонӣ"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda '……就……' shartli bog'lovchisi, '又' va '再' farqi hamda '谁/什么+都/也' umumlashtiruvchi iboralarini o'rganamiz.", "ru": "В этом уроке мы изучим условное союзное слово '……就……', разницу между '又' и '再', а также обобщающее выражение '谁/什么+都/也'.", "tj": "Дар ин дарс мо пайвандаки шартии '……就……', фарқи '又' ва '再' ва ибораҳои умумикунандаи '谁/什么+都/也'-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "护照", "pinyin": "hùzhào", "pos": "n", "uz": "pasport", "ru": "паспорт", "tj": "шиноснома"},
        {"no": 2, "zh": "签证", "pinyin": "qiānzhèng", "pos": "n", "uz": "viza", "ru": "виза", "tj": "виза"},
        {"no": 3, "zh": "行李", "pinyin": "xíngli", "pos": "n", "uz": "bagaj", "ru": "багаж", "tj": "бор"},
        {"no": 4, "zh": "机场", "pinyin": "jīchǎng", "pos": "n", "uz": "aeroport", "ru": "аэропорт", "tj": "фурудгоҳ"},
        {"no": 5, "zh": "航班", "pinyin": "hángbān", "pos": "n", "uz": "reys", "ru": "рейс", "tj": "парвоз"},
        {"no": 6, "zh": "再", "pinyin": "zài", "pos": "adv", "uz": "yana (kelgusida)", "ru": "ещё раз (в будущем)", "tj": "боз (оянда)"},
        {"no": 7, "zh": "又", "pinyin": "yòu", "pos": "adv", "uz": "yana (o'tganda/takroran)", "ru": "снова (в прошлом/повторно)", "tj": "боз (гузашта)"},
        {"no": 8, "zh": "谁", "pinyin": "shéi", "pos": "pron", "uz": "kim (umumlashtiruvchi)", "ru": "кто (обобщающее)", "tj": "кӣ (умумикунанда)"},
        {"no": 9, "zh": "随便", "pinyin": "suíbiàn", "pos": "adj/adv", "uz": "ixtiyoriy; bemalol", "ru": "любой; как угодно", "tj": "ихтиёрӣ; ба хоҳиш"},
        {"no": 10, "zh": "打折", "pinyin": "dǎzhé", "pos": "v", "uz": "chegirma bermoq", "ru": "делать скидку", "tj": "тахфиф додан"},
        {"no": 11, "zh": "附近", "pinyin": "fùjìn", "pos": "n", "uz": "atrofida, yaqinida", "ru": "поблизости, рядом", "tj": "наздикӣ, атроф"},
        {"no": 12, "zh": "方便", "pinyin": "fāngbiàn", "pos": "adj", "uz": "qulay, oson", "ru": "удобно, легко", "tj": "қулай, осон"},
        {"no": 13, "zh": "直接", "pinyin": "zhíjiē", "pos": "adv", "uz": "to'g'ridan-to'g'ri", "ru": "прямо, напрямую", "tj": "мустақиман"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Sayohat rejalari", "ru": "Планы на поездку", "tj": "Нақшаҳои сафар"},
            "dialogue": [
                {"speaker": "A", "zh": "你打算去哪儿旅游？", "pinyin": "Nǐ dǎsuàn qù nǎr lǚyóu?", "uz": "Siz qayerga sayohat qilmoqchi?", "ru": "Куда ты планируешь поехать?", "tj": "Шумо ба куҷо сафар карданӣ ҳастед?"},
                {"speaker": "B", "zh": "你去哪儿我就去哪儿，一起走吧！", "pinyin": "Nǐ qù nǎr wǒ jiù qù nǎr, yīqǐ zǒu ba!", "uz": "Siz qayerga borsangiz, men ham boraman, birga ketaylik!", "ru": "Куда ты, туда и я, пойдём вместе!", "tj": "Шумо ба куҷо равед, ман ҳам меравам, якҷо меравем!"},
                {"speaker": "A", "zh": "好的！那你把护照和签证准备好。", "pinyin": "Hǎo de! Nà nǐ bǎ hùzhào hé qiānzhèng zhǔnbèi hǎo.", "uz": "Yaxshi! Unda pasport va vizangizni tayyorlab qo'ying.", "ru": "Хорошо! Тогда приготовь паспорт и визу.", "tj": "Хуб! Пас шиноснома ва визаатонро тайёр кунед."},
                {"speaker": "B", "zh": "没问题，我去哪儿都会带着护照的。", "pinyin": "Méi wèntí, wǒ qù nǎr dōu huì dàizhe hùzhào de.", "uz": "Muammo yo'q, men qayerga borsam ham pasport olib boraman.", "ru": "Без проблем, куда бы я ни пошёл, я всегда беру паспорт.", "tj": "Мушкиле нест, ба куҷо равам, ҳамеша шиноснома мебарам."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Aeroportda bagaj", "ru": "Багаж в аэропорту", "tj": "Бор дар фурудгоҳ"},
            "dialogue": [
                {"speaker": "A", "zh": "我们什么时候去机场？", "pinyin": "Wǒmen shénme shíhou qù jīchǎng?", "uz": "Biz aeroportga qachon boramiz?", "ru": "Когда мы поедем в аэропорт?", "tj": "Мо кай ба фурудгоҳ меравем?"},
                {"speaker": "B", "zh": "航班八点，我们七点就出发吧。", "pinyin": "Hángbān bā diǎn, wǒmen qī diǎn jiù chūfā ba.", "uz": "Reys soat sakkizda, biz soat yettida jo'naraylik.", "ru": "Рейс в восемь, давай выедем в семь.", "tj": "Парвоз соати ҳашт, биё соати ҳафт рафт кунем."},
                {"speaker": "A", "zh": "行李太重了，你又带了那么多东西！", "pinyin": "Xíngli tài zhòng le, nǐ yòu dài le nàme duō dōngxi!", "uz": "Bagaj juda og'ir, siz yana shuncha narsa oldingiz!", "ru": "Багаж слишком тяжёлый, ты снова взял столько вещей!", "tj": "Бор хеле вазнин аст, шумо боз инқадар чиз гирифтед!"},
                {"speaker": "B", "zh": "好，下次我再也不带这么多了。", "pinyin": "Hǎo, xià cì wǒ zài yě bú dài zhème duō le.", "uz": "Yaxshi, keyingi safar men boshqa buncha narsani olmayman.", "ru": "Ладно, в следующий раз я больше не возьму столько.", "tj": "Хуб, дафъаи дигар ман дигар ин қадар намегирам."}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Bozorda xarid qilish", "ru": "Покупки на рынке", "tj": "Харид дар бозор"},
            "dialogue": [
                {"speaker": "A", "zh": "这件衣服怎么样？随便看看吧。", "pinyin": "Zhè jiàn yīfu zěnme yàng? Suíbiàn kànkan ba.", "uz": "Bu kiyim qanday? Bemalol qarang.", "ru": "Как тебе эта одежда? Смотри свободно.", "tj": "Ин либос чӣ тавр аст? Озодона бинед."},
                {"speaker": "B", "zh": "什么都行，你买哪件我就买哪件。", "pinyin": "Shénme dōu xíng, nǐ mǎi nǎ jiàn wǒ jiù mǎi nǎ jiàn.", "uz": "Hammasi bo'ladi, siz qaysi birini olsangiz, men ham o'shani olaman.", "ru": "Всё подходит, какую ты купишь, такую же и я куплю.", "tj": "Ҳама мешавад, кадомро шумо харед, манҳам ҳамонро мехарам."},
                {"speaker": "A", "zh": "这件打折吗？", "pinyin": "Zhè jiàn dǎzhé ma?", "uz": "Bu chegirmami?", "ru": "На это есть скидка?", "tj": "Ин тахфиф дорад?"},
                {"speaker": "B", "zh": "打八折，买两件更便宜！", "pinyin": "Dǎ bā zhé, mǎi liǎng jiàn gèng piányí!", "uz": "20% chegirma, ikkita olsangiz yanada arzonroq!", "ru": "Скидка 20%, если купите два — ещё дешевле!", "tj": "Тахфифи 20%, ду адад харед — арзонтар мешавад!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Yo'l so'rash", "ru": "Уточнение дороги", "tj": "Пурсидани роҳ"},
            "dialogue": [
                {"speaker": "A", "zh": "请问，附近有地铁站吗？", "pinyin": "Qǐngwèn, fùjìn yǒu dìtiě zhàn ma?", "uz": "Kechirasiz, yaqin atrofda metro stantsiyasi bormi?", "ru": "Извините, есть ли поблизости станция метро?", "tj": "Бубахшед, дар наздикӣ истгоҳи метро ҳаст?"},
                {"speaker": "B", "zh": "有，谁都知道那个地方，很方便。", "pinyin": "Yǒu, shéi dōu zhīdào nà ge dìfāng, hěn fāngbiàn.", "uz": "Bor, u joyni hamma biladi, juda qulay.", "ru": "Есть, это место знают все, очень удобно.", "tj": "Ҳаст, ҳама он ҷоро медонад, хеле қулай."},
                {"speaker": "A", "zh": "怎么走比较方便？", "pinyin": "Zěnme zǒu bǐjiào fāngbiàn?", "uz": "Qanday yo'l borish qulayroq?", "ru": "Как удобнее добраться?", "tj": "Кадом роҳ қулайтар аст?"},
                {"speaker": "B", "zh": "直接往前走，五分钟就到了。", "pinyin": "Zhíjiē wǎng qián zǒu, wǔ fēnzhōng jiù dào le.", "uz": "To'g'ri oldinga yuring, besh daqiqada yetasiz.", "ru": "Идите прямо, через пять минут будете на месте.", "tj": "Мустақиман пеш равед, дар панҷ дақиқа мерасед."}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "\"又\"和\"再\"的区别",
            "title_uz": "\"又\" va \"再\" farqi",
            "title_ru": "Разница между \"又\" и \"再\"",
            "title_tj": "Фарқи \"又\" ва \"再\"",
            "rule_uz": "'又' o'tgan vaqtdagi takroran bajarilgan harakatni bildiradi (u yana kechikdi — o'tgan zamonda). '再' kelajakdagi takroran bajariladigan harakatni bildiradi (keyingi safar yana borayman).",
            "rule_ru": "'又' обозначает повторное действие в прошлом (он снова опоздал). '再' обозначает повторное действие в будущем (в следующий раз поеду ещё раз).",
            "rule_tj": "'又' амали такроршавандаи гузаштаро ифода мекунад (вай боз дер омад). '再' амали такроршавандаи оянда мебошад (дафъаи дигар боз меравам).",
            "examples": [
                {"zh": "他又迟到了！", "pinyin": "Tā yòu chídào le!", "uz": "U yana kechikdi! (o'tgan)", "ru": "Он снова опоздал! (прошлое)", "tj": "Вай боз дер омад! (гузашта)"},
                {"zh": "下次再来吧。", "pinyin": "Xià cì zài lái ba.", "uz": "Keyingi safar yana keling. (kelajak)", "ru": "В следующий раз приходи ещё раз. (будущее)", "tj": "Дафъаи дигар боз биё. (оянда)"}
            ]
        },
        {
            "no": 2,
            "title_zh": "疑问代词活用①：谁/什么+都/也+V",
            "title_uz": "So'roq olmoshlarining maxsus qo'llanishi: kim/nima + ham + F",
            "title_ru": "Особое употребление вопросительных местоимений: кто/что + тоже/все + Гл",
            "title_tj": "Истифодаи хоси зомирҳои саволӣ: кӣ/чӣ + ҳам + Ф",
            "rule_uz": "So'roq olmoshlari (谁、什么、哪儿) umumlashtiruvchi ma'noda ishlatilganda '都' yoki '也' bilan keladi va 'hamma / hech kim emas' ma'nosini bildiradi.",
            "rule_ru": "Вопросительные местоимения (谁、什么、哪儿) в обобщающем значении используются с '都' или '也' и означают 'все / никто'.",
            "rule_tj": "Зомирҳои саволӣ (谁、什么、哪儿) дар маънои умумикунанда бо '都' ё '也' меоянд ва маънои 'ҳама / ҳеҷ кас нест'-ро доранд.",
            "examples": [
                {"zh": "谁都知道这件事。", "pinyin": "Shéi dōu zhīdào zhè jiàn shì.", "uz": "Bu hodisani hamma biladi.", "ru": "Все знают об этом.", "tj": "Ҳама ин корро медонад."},
                {"zh": "什么都可以，随便吃吧。", "pinyin": "Shénme dōu kěyǐ, suíbiàn chī ba.", "uz": "Hamma narsa bo'ladi, bemalol yeng.", "ru": "Можно всё, ешь как хочешь.", "tj": "Ҳама чиз мешавад, ба хоҳиш бихӯред."}
            ]
        },
        {
            "no": 3,
            "title_zh": "条件句：……就……",
            "title_uz": "Shartli gap: …… bo'lsa …… bo'ladi",
            "title_ru": "Условное предложение: если …, то …",
            "title_tj": "Ҷумлаи шартӣ: агар … пас …",
            "rule_uz": "'……就……' tuzilmasi shartni bildiradi: shartli qism + 就 + natija. Shartli qismda ko'pincha '如果'、'要是'、'只要' kabi so'zlar ishlatiladi, lekin ba'zan qo'yilmaydi.",
            "rule_ru": "Конструкция '……就……' выражает условие: условная часть + 就 + результат. В условной части часто используются '如果'、'要是'、'只要', но они могут опускаться.",
            "rule_tj": "Сохтори '……就……' шартро ифода мекунад: қисми шартӣ + 就 + натиҷа. Дар қисми шартӣ '如果'、'要是'、'只要' зиёд истифода мешаванд, аммо гоҳо ҳазф мешаванд.",
            "examples": [
                {"zh": "你去哪儿我就去哪儿。", "pinyin": "Nǐ qù nǎr wǒ jiù qù nǎr.", "uz": "Siz qayerga borsangiz, men ham boraman.", "ru": "Куда ты, туда и я.", "tj": "Шумо ба куҷо равед, ман ҳам меравам."},
                {"zh": "你买哪件我就买哪件。", "pinyin": "Nǐ mǎi nǎ jiàn wǒ jiù mǎi nǎ jiàn.", "uz": "Siz qaysi birini olsangiz, men ham o'shani olaman.", "ru": "Какую ты купишь, такую же и я.", "tj": "Кадомро шумо харед, манҳам ҳамонро мехарам."}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Siz qayerga borsangiz, men ham boraman.", "ru": "Куда ты, туда и я.", "tj": "Шумо ба куҷо равед, ман ҳам меравам."},
                {"no": 2, "uz": "Bu hodisani hamma biladi.", "ru": "Все знают об этом.", "tj": "Ҳама ин корро медонад."},
                {"no": 3, "uz": "U yana kechikdi!", "ru": "Он снова опоздал!", "tj": "Вай боз дер омад!"},
                {"no": 4, "uz": "Keyingi safar yana keling.", "ru": "В следующий раз приходи ещё раз.", "tj": "Дафъаи дигар боз биё."},
                {"no": 5, "uz": "Hamma narsa bo'ladi, bemalol yeng.", "ru": "Можно всё, ешь как хочешь.", "tj": "Ҳама чиз мешавад, ба хоҳиш бихӯред."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "他___迟到了！（表示过去重复）", "sentence_uz": "U ___ kechikdi! (o'tgan)", "sentence_ru": "Он ___ опоздал! (прошлое)", "sentence_tj": "Вай ___ дер омад! (гузашта)", "hint": "又"},
                {"no": 2, "sentence_zh": "下次___来看我。（表示将来）", "sentence_uz": "Keyingi safar ___ keling. (kelajak)", "sentence_ru": "В следующий раз ___ приходи. (будущее)", "sentence_tj": "Дафъаи дигар ___ биё. (оянда)", "hint": "再"},
                {"no": 3, "sentence_zh": "谁___知道这件事。", "sentence_uz": "Bu hodisani hamma ___.", "sentence_ru": "Все ___ знают об этом.", "sentence_tj": "Ҳама ин корро ___.", "hint": "都"},
                {"no": 4, "sentence_zh": "你去哪儿我___去哪儿。", "sentence_uz": "Siz qayerga borsangiz, men ham ___.", "sentence_ru": "Куда ты, туда ___ и я.", "sentence_tj": "Шумо ба куҷо равед, ман ҳам ___.", "hint": "就"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "你买什么我就买什么。", "pinyin": "Nǐ mǎi shénme wǒ jiù mǎi shénme."},
                {"no": 2, "zh": "谁都不知道他去哪儿了。", "pinyin": "Shéi dōu bù zhīdào tā qù nǎr le."}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "你去哪儿我就去哪儿。"},
                {"no": 2, "zh": "谁都知道这件事。"},
                {"no": 3, "zh": "他又迟到了！"},
                {"no": 4, "zh": "下次再来吧。"},
                {"no": 5, "zh": "什么都可以，随便吃吧。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "又"},
                {"no": 2, "answer": "再"},
                {"no": 3, "answer": "都"},
                {"no": 4, "answer": "就"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Siz nima olsangiz, men ham o'shani olaman.", "ru": "Что ты купишь, то и я куплю.", "tj": "Шумо чӣ харед, манҳам ҳамонро мехарам."},
                {"no": 2, "uz": "U qayerga ketganini hech kim bilmaydi.", "ru": "Никто не знает, куда он ушёл.", "tj": "Ҳеҷ кас намедонад ки вай ба куҷо рафт."}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'……就……' tuzilmasidan foydalanib, 5 ta shartli gap tuzing va o'sha gaplarda '谁/什么+都' iboralarini ham qo'llab ko'ring.", "ru": "Составьте 5 условных предложений с '……就……', попробуйте включить в них '谁/什么+都'.", "tj": "5 ҷумлаи шартӣ бо '……就……' тартиб диҳед ва дар онҳо '谁/什么+都'-ро низ санҷед."},
        {"task_no": 2, "uz": "'又' va '再' dan foydalanib, 4 ta jumla yozing: 2 tasida o'tgan zamondagi takroriy harakat, 2 tasida kelajakdagi niyat bo'lsin.", "ru": "Напишите 4 предложения с '又' и '再': 2 с повторным действием в прошлом, 2 с намерением в будущем.", "tj": "4 ҷумла бо '又' ва '再' нависед: 2 бо амали такроршаванда дар гузашта, 2 бо нияти оянда."}
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
