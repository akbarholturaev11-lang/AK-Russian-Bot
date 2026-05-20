import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk2",
    "lesson_order": 3,
    "lesson_code": "HSK2-L03",
    "title": "左边那个红色的是我的",
    "goal": json.dumps({
        "uz": "Narsalarning egasini, rangini va joylashuvini tasvirlash; '的' qo'shimchasi bilan ot-so'z birikmalarini, 一下 miqdorini va 真 kuchaytiruvchi ravishini o'zlashtirish.",
        "ru": "Научиться описывать владельца, цвет и местоположение предметов; освоить именные словосочетания с 的, количественное слово 一下 и усилительное наречие 真.",
        "tj": "Тасвири соҳиб, ранг ва ҷойгиршавии ашё; азхудкунии ибораҳои исмӣ бо 的, воҳиди 一下 ва зарфи тақвиятии 真.",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "Bu darsda narsalar haqida gapirish: ularning egasi kim, qanday rang, qayerda turishi o'rganiladi. Siz uy, xona va idora muhitida narsalarni tavsiflashni mashq qilasiz. Asosiy grammatik mavzular: '的' qo'shimchasi bilan ot-so'z birikmasi, 一下 miqdor yuklamasi va 真 kuchaytiruvchi ravishi.",
        "ru": "На этом уроке изучается описание предметов: кому принадлежат, какого цвета, где находятся. Вы будете практиковать описание предметов в домашней, комнатной и офисной обстановке. Основные грамматические темы: именное словосочетание с 的, частица количества 一下 и усилительное наречие 真.",
        "tj": "Дар ин дарс гапидан дар бораи ашё омӯхта мешавад: соҳиби онҳо кист, чӣ ранг доранд, дар куҷо қарор доранд. Шумо тавсифи ашёро дар муҳити хона, хона ва идора машқ мекунед. Мавзӯҳои асосии грамматикӣ: ибораи исмӣ бо 的, воҳиди 一下 ва зарфи тақвиятии 真.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "手表",  "pinyin": "shǒubiǎo", "pos": "n.",    "uz": "qo'l soati",                              "ru": "наручные часы",                    "tj": "соати дасти"},
        {"no": 2,  "zh": "千",    "pinyin": "qiān",      "pos": "num.", "uz": "ming (1000)",                             "ru": "тысяча (1000)",                    "tj": "ҳазор (1000)"},
        {"no": 3,  "zh": "报纸",  "pinyin": "bàozhǐ",   "pos": "n.",    "uz": "gazeta",                                  "ru": "газета",                           "tj": "рӯзнома"},
        {"no": 4,  "zh": "送",    "pinyin": "sòng",      "pos": "v.",    "uz": "yetkazib bermoq, sovg'a qilmoq",         "ru": "доставлять, дарить",               "tj": "расондан, тӯҳфа кардан"},
        {"no": 5,  "zh": "一下",  "pinyin": "yíxià",    "pos": "m.",    "uz": "bir oz, bir marta (harakat uchun)",       "ru": "немного, разок (для смягчения глагола)", "tj": "якдафъа, каме (барои нармкунии феъл)"},
        {"no": 6,  "zh": "牛奶",  "pinyin": "niúnǎi",   "pos": "n.",    "uz": "sut (sigir suti)",                        "ru": "молоко (коровье)",                 "tj": "шир (шири гов)"},
        {"no": 7,  "zh": "房间",  "pinyin": "fángjiān", "pos": "n.",    "uz": "xona, uy",                                "ru": "комната",                          "tj": "хона, утоқ"},
        {"no": 8,  "zh": "丈夫",  "pinyin": "zhàngfu",  "pos": "n.",    "uz": "er, turmush o'rtoq (erkak)",             "ru": "муж",                              "tj": "шавҳар"},
        {"no": 9,  "zh": "旁边",  "pinyin": "pángbiān", "pos": "n.",    "uz": "yonida, yon tomonida",                    "ru": "рядом, сбоку",                     "tj": "дар паҳлӯ, назди"},
        {"no": 10, "zh": "真",    "pinyin": "zhēn",      "pos": "adv.", "uz": "haqiqatan, juda (ta'kidlash uchun)",      "ru": "действительно, очень (для усиления)", "tj": "воқеан, хеле (барои тақвият)"},
        {"no": 11, "zh": "粉色",  "pinyin": "fěnsè",    "pos": "n.",    "uz": "pushti rang",                             "ru": "розовый цвет",                     "tj": "ранги гулобӣ"},
        {"no": 12, "zh": "粉",    "pinyin": "fěn",       "pos": "adj.", "uz": "pushti",                                  "ru": "розовый",                          "tj": "гулобӣ"},
        {"no": 13, "zh": "颜色",  "pinyin": "yánsè",    "pos": "n.",    "uz": "rang",                                    "ru": "цвет",                             "tj": "ранг"},
        {"no": 14, "zh": "左边",  "pinyin": "zuǒbian",  "pos": "n.",    "uz": "chap tomon",                              "ru": "левая сторона",                    "tj": "тарафи чап"},
        {"no": 15, "zh": "红色",  "pinyin": "hóngsè",   "pos": "n.",    "uz": "qizil rang",                              "ru": "красный цвет",                     "tj": "ранги сурх"},
        {"no": 16, "zh": "红",    "pinyin": "hóng",      "pos": "adj.", "uz": "qizil",                                   "ru": "красный",                          "tj": "сурх"},
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Xonada",
            "scene_ru": "В комнате",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "这块手表是你的吗？", "pinyin": "Zhè kuài shǒubiǎo shì nǐ de ma?", "uz": "Bu qo'l soati seniki ekanmi?", "ru": "Эти часы твои?", "tj": "Ин соати дасти аз они туст?"},
                {"speaker": "B", "zh": "不是我的。是我爸爸的。", "pinyin": "Bú shì wǒ de. Shì wǒ bàba de.", "uz": "Meniki emas. Bu dadasimniki.", "ru": "Не мои. Это папины.", "tj": "На, аз они ман нест. Аз они падарам аст."},
                {"speaker": "A", "zh": "多少钱买的？", "pinyin": "Duōshao qián mǎi de?", "uz": "Uni qancha pulga sotib oldingiz?", "ru": "За сколько купили?", "tj": "Ба чанд харидаанд?"},
                {"speaker": "B", "zh": "三千多块。", "pinyin": "Sānqiān duō kuài.", "uz": "Uch mingdan ortiq yuan.", "ru": "Больше трёх тысяч юаней.", "tj": "Зиёда аз се ҳазор юань."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "这是今天早上的报纸吗？", "pinyin": "Zhè shì jīntiān zǎoshang de bàozhǐ ma?", "uz": "Bu bugungi ertalabki gazetami?", "ru": "Это сегодняшняя утренняя газета?", "tj": "Ин рӯзномаи субҳи имрӯз аст?"},
                {"speaker": "B", "zh": "不是，是昨天的。", "pinyin": "Bú shì, shì zuótiān de.", "uz": "Yo'q, bu kechagi.", "ru": "Нет, вчерашняя.", "tj": "На, аз дирӯз аст."},
                {"speaker": "A", "zh": "你听，是不是送报纸的来了？", "pinyin": "Nǐ tīng, shì bú shì sòng bàozhǐ de lái le?", "uz": "Eshit, gazeta olib keladiganmi keldi?", "ru": "Слышишь, это не газетчик пришёл?", "tj": "Гӯш кун, оё рӯзнома оварандаи омад?"},
                {"speaker": "B", "zh": "我看一下。不是，是送牛奶的。", "pinyin": "Wǒ kàn yíxià. Bú shì, shì sòng niúnǎi de.", "uz": "Bir qarayayin. Yo'q, sut olib keladigan.", "ru": "Посмотрю. Нет, это молочник.", "tj": "Як нигоҳ мекунам. На, шир оварандаи аст."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Uyda",
            "scene_ru": "Дома",
            "scene_tj": "Дар хона",
            "dialogue": [
                {"speaker": "A", "zh": "这是谁的房间？", "pinyin": "Zhè shì shéi de fángjiān?", "uz": "Bu kimning xonasi?", "ru": "Чья это комната?", "tj": "Ин хонаи кист?"},
                {"speaker": "B", "zh": "这是我和我丈夫的，旁边那个小的房间是我女儿的。", "pinyin": "Zhè shì wǒ hé wǒ zhàngfu de, pángbiān nàge xiǎo de fángjiān shì wǒ nǚ'ér de.", "uz": "Bu men va erimning xonasi, yonidagi kichkina xona esa qizimniki.", "ru": "Это наша с мужем комната, а маленькая комната рядом — дочкина.", "tj": "Ин хонаи ман ва шавҳарам аст, ва хонаи хурде дар паҳлӯ аз они духтарам аст."},
                {"speaker": "A", "zh": "你女儿的房间真漂亮啊！都是粉色的。", "pinyin": "Nǐ nǚ'ér de fángjiān zhēn piàoliang a! Dōu shì fěnsè de.", "uz": "Qizingizning xonasi juda chiroyli! Hammasi pushti rangda.", "ru": "Комната вашей дочки действительно красивая! Всё розовое.", "tj": "Хонаи духтаратон воқеан зебо аст! Ҳама чиз гулобӣ ранг аст."},
                {"speaker": "B", "zh": "是啊，粉色是我女儿最喜欢的颜色。", "pinyin": "Shì a, fěnsè shì wǒ nǚ'ér zuì xǐhuan de yánsè.", "uz": "Ha, pushti rang qizimning eng sevimli rangi.", "ru": "Да, розовый — любимый цвет моей дочки.", "tj": "Бале, гулобӣ ранги дӯстдоштатарини духтарам аст."},
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "scene_uz": "Ofisda",
            "scene_ru": "В офисе",
            "scene_tj": "Дар идора",
            "dialogue": [
                {"speaker": "A", "zh": "你看见我的杯子了吗？", "pinyin": "Nǐ kànjian wǒ de bēizi le ma?", "uz": "Mening stakanimni ko'rdingmi?", "ru": "Ты видел мою кружку?", "tj": "Оё косачаи маро дидӣ?"},
                {"speaker": "B", "zh": "这里有几个杯子，哪个是你的？", "pinyin": "Zhèlǐ yǒu jǐ ge bēizi, nǎge shì nǐ de?", "uz": "Bu yerda bir nechta stakan bor, qaysi biri seniki?", "ru": "Здесь есть несколько кружек, которая твоя?", "tj": "Инҷо чанд косача ҳаст, кадомаш аз они туст?"},
                {"speaker": "A", "zh": "左边那个红色的是我的。", "pinyin": "Zuǒbian nàge hóngsè de shì wǒ de.", "uz": "Chap tomondagi qizil rangi meniki.", "ru": "Вон та красная, слева — моя.", "tj": "Он сурхе, ки тарафи чап аст, аз они ман аст."},
                {"speaker": "B", "zh": "给你。", "pinyin": "Gěi nǐ.", "uz": "Ol, shunga.", "ru": "Держи.", "tj": "Бигир."},
            ]
        },
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "“的”字短语",
            "title_uz": "'的' qo'shimchasi bilan ibora",
            "title_ru": "Именное словосочетание с 的",
            "title_tj": "Ибора бо 的",
            "rule_uz": "'的' qo'shimchasi ot o'rnida ishlatilganda '的' bilan tugagan birikma ot vazifasini bajaradi. Masalan, '红色的' = 'qizil rangli narsa', '送报纸的' = 'gazeta olib keladigan odam'. Bu usul takrorni oldini olish uchun ishlatiladi.",
            "rule_ru": "Когда частица 的 используется вместо существительного, словосочетание, заканчивающееся на 的, выполняет функцию существительного. Например, '红色的' = 'красная вещь', '送报纸的' = 'человек, доставляющий газеты'. Используется для избегания повторений.",
            "rule_tj": "Вақте ки 的 ба ҷои исм истифода мешавад, ибораи хотимаёфта бо 的 нақши исмро мебозад. Масалан, '红色的' = 'чизи сурх', '送报纸的' = 'одами рӯзнома оваранда'. Барои пешгирии такрор истифода мешавад.",
            "examples": [
                {"zh": "左边那个红色的是我的。", "pinyin": "Zuǒbian nàge hóngsè de shì wǒ de.", "uz": "Chap tomondagi qizili meniki.", "ru": "Вон та красная слева — моя.", "tj": "Он сурхе, ки тарафи чап аст, аз они ман аст."},
                {"zh": "是送牛奶的来了。", "pinyin": "Shì sòng niúnǎi de lái le.", "uz": "Sut olib keladigan odam keldi.", "ru": "Пришёл молочник.", "tj": "Шир оварандаи омад."},
            ]
        },
        {
            "no": 2,
            "title_zh": "量词“一下”",
            "title_uz": "Miqdor ko'makchisi '一下'",
            "title_ru": "Счётное слово 一下",
            "title_tj": "Воҳиди 一下",
            "rule_uz": "'一下' fe'ldan keyin kelib harakatning qisqa yoki engil bajarilishini bildiradi. U fe'lni muloyim yoki noaniq qiladi. O'zbek tilidagi 'bir oz, bir qarayin' kabi.",
            "rule_ru": "一下 ставится после глагола и указывает на краткое или лёгкое выполнение действия. Смягчает глагол или делает его неопределённым. Аналог русского «разок, немного».",
            "rule_tj": "一下 баъд аз феъл меояд ва ифодаи кӯтоҳ ё сабуки амалро нишон медиҳад. Феълро нарм ё номуайян мекунад. Ба монанди 'як дафъа, каме' дар забони ӯзбекӣ.",
            "examples": [
                {"zh": "我看一下。", "pinyin": "Wǒ kàn yíxià.", "uz": "Bir qarayayin.", "ru": "Посмотрю.", "tj": "Як нигоҳ мекунам."},
                {"zh": "你等一下。", "pinyin": "Nǐ děng yíxià.", "uz": "Bir oz kutib tur.", "ru": "Подожди немного.", "tj": "Каме интизор шав."},
            ]
        },
        {
            "no": 3,
            "title_zh": "语气副词“真”",
            "title_uz": "Modal ravish '真'",
            "title_ru": "Модальное наречие 真",
            "title_tj": "Зарфи модалии 真",
            "rule_uz": "'真' ravishi sifat yoki fe'l oldidan kelib 'haqiqatan, juda' ma'nosida kuchaytirish bildiradi. Ko'pincha hayrat yoki ta'sir bildiruvchi gaplarda ishlatiladi.",
            "rule_ru": "Наречие 真 ставится перед прилагательным или глаголом и означает усиление «действительно, очень». Часто используется в восклицательных предложениях.",
            "rule_tj": "Зарфи 真 пеш аз сифат ё феъл меояд ва тақвиятро ба маънии 'воқеан, хеле' ифода мекунад. Аксар дар ҷумлаҳои ҳайратии ифодакунанда истифода мешавад.",
            "examples": [
                {"zh": "你女儿的房间真漂亮啊！", "pinyin": "Nǐ nǚ'ér de fángjiān zhēn piàoliang a!", "uz": "Qizingizning xonasi haqiqatan chiroyli!", "ru": "Комната вашей дочки действительно красивая!", "tj": "Хонаи духтаратон воқеан зебо аст!"},
                {"zh": "这个菜真好吃！", "pinyin": "Zhège cài zhēn hǎochī!", "uz": "Bu taom juda mazali!", "ru": "Это блюдо действительно вкусное!", "tj": "Ин хӯрок воқеан хуш мазза аст!"},
            ]
        },
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagi so'zlarning xitoychasini yozing:",
            "instruction_ru": "Напишите китайский эквивалент следующих слов:",
            "instruction_tj": "Калимаҳои зеринро ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "qo'l soati", "prompt_ru": "наручные часы", "prompt_tj": "соати дасти", "answer": "手表", "pinyin": "shǒubiǎo"},
                {"prompt_uz": "gazeta", "prompt_ru": "газета", "prompt_tj": "рӯзнома", "answer": "报纸", "pinyin": "bàozhǐ"},
                {"prompt_uz": "rang", "prompt_ru": "цвет", "prompt_tj": "ранг", "answer": "颜色", "pinyin": "yánsè"},
                {"prompt_uz": "chap tomon", "prompt_ru": "левая сторона", "prompt_tj": "тарафи чап", "answer": "左边", "pinyin": "zuǒbian"},
                {"prompt_uz": "pushti rang", "prompt_ru": "розовый цвет", "prompt_tj": "ранги гулобӣ", "answer": "粉色", "pinyin": "fěnsè"},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyga mos so'zni yozing (真、一下、的、旁边、红色):",
            "instruction_ru": "Вставьте подходящее слово (真、一下、的、旁边、红色):",
            "instruction_tj": "Калимаи мувофиқро нависед (真、一下、的、旁边、红色):",
            "items": [
                {"prompt_uz": "你女儿的房间______漂亮啊！", "answer": "真", "pinyin": "zhēn"},
                {"prompt_uz": "我看______。", "answer": "一下", "pinyin": "yíxià"},
                {"prompt_uz": "左边那个______是我的。", "answer": "红色的", "pinyin": "hóngsè de"},
            ]
        },
        {
            "no": 3,
            "type": "translate_to_uzbek",
            "instruction_uz": "Quyidagi gaplarni o'zbek tiliga tarjima qiling:",
            "instruction_ru": "Переведите следующие предложения на узбекский язык:",
            "instruction_tj": "Ҷумлаҳои зеринро ба забони ӯзбекӣ тарҷума кунед:",
            "items": [
                {"prompt_uz": "这块手表是我爸爸的。", "answer": "Bu qo'l soati dadasimniki.", "pinyin": "Zhè kuài shǒubiǎo shì wǒ bàba de."},
                {"prompt_uz": "粉色是我女儿最喜欢的颜色。", "answer": "Pushti rang qizimning eng sevimli rangi.", "pinyin": "Fěnsè shì wǒ nǚ'ér zuì xǐhuan de yánsè."},
            ]
        },
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {"no": 1, "answers": ["手表", "报纸", "颜色", "左边", "粉色"]},
        {"no": 2, "answers": ["真", "一下", "红色的"]},
        {"no": 3, "answers": ["Bu qo'l soati dadasimniki.", "Pushti rang qizimning eng sevimli rangi."]},
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Quyidagi so'zlardan foydalanib '的' qo'shimchasi bilan 4 ta gap tuzing:",
            "instruction_ru": "Составьте 4 предложения с частицей 的, используя следующие слова:",
            "instruction_tj": "Бо истифода аз калимаҳои зерин 4 ҷумла бо 的 тартиб диҳед:",
            "words": ["红色的", "送报纸的", "旁边的", "我丈夫的"],
            "example": "左边那个红色的杯子是我的。",
        },
        {
            "no": 2,
            "instruction_uz": "O'z xonangizni tasvirlab, 5-6 gapdan iborat kichik matn yozing. Rang, joylashuv va egasi haqida gapirib bering.",
            "instruction_ru": "Опишите свою комнату в небольшом тексте из 5–6 предложений. Расскажите о цвете, расположении и владельце предметов.",
            "instruction_tj": "Хонаи худро тавсиф кунед, матни хурде аз 5-6 ҷумла нависед. Дар бораи ранг, ҷойгиршавӣ ва соҳиби ашё нақл кунед.",
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
