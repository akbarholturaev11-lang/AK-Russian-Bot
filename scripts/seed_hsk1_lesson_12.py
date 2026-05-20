import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk1",
    "lesson_order": 12,
    "lesson_code": "HSK1-L12",
    "title": "明天天气怎么样",
    "goal": json.dumps({
        "uz": "Ob-havo haqida gaplashish, 怎么样 so'roq so'zi va 太...了 tuzilmasi",
        "ru": "Говорить о погоде, вопросительное слово 怎么样 и конструкция 太...了",
        "tj": "Сухан дар бораи обу ҳаво, калимаи суолии 怎么样 ва сохтори 太...了",
    }, ensure_ascii=False),
    "intro_text": json.dumps({
        "uz": "O'n ikkinchi darsda siz ob-havo haqida gaplashishni, 怎么样 bilan holat so'rashni va 太...了 tuzilmasini o'rganasiz. 13 ta yangi so'z, 3 ta dialog.",
        "ru": "В двенадцатом уроке вы научитесь говорить о погоде, спрашивать о состоянии с 怎么样 и использовать конструкцию 太...了. 13 новых слов, 3 диалога.",
        "tj": "Дар дарси дувоздаҳум шумо ёд мегиред, ки дар бораи обу ҳаво сухан ронед, бо 怎么样 ҳолро пурсед ва сохтори 太...了 -ро истифода баред. 13 калимаи нав, 3 муколама.",
    }, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1,  "zh": "天气",  "pinyin": "tiānqì",   "pos": "n.",
         "uz": "ob-havo",
         "ru": "погода",
         "tj": "обу ҳаво"},
        {"no": 2,  "zh": "怎么样","pinyin": "zěnmeyàng","pos": "pron.",
         "uz": "qanday, qanaqa",
         "ru": "как, какой",
         "tj": "чӣ тавр, чӣ хел"},
        {"no": 3,  "zh": "太",    "pinyin": "tài",      "pos": "adv.",
         "uz": "juda, haddan tashqari",
         "ru": "слишком, очень",
         "tj": "хеле зиёд, аз ҳад зиёд"},
        {"no": 4,  "zh": "热",    "pinyin": "rè",       "pos": "adj.",
         "uz": "issiq",
         "ru": "жарко, горячий",
         "tj": "гарм, гармо"},
        {"no": 5,  "zh": "冷",    "pinyin": "lěng",     "pos": "adj.",
         "uz": "sovuq",
         "ru": "холодно, холодный",
         "tj": "сард, хунук"},
        {"no": 6,  "zh": "下雨",  "pinyin": "xià yǔ",   "pos": "v.",
         "uz": "yomg'ir yog'moq",
         "ru": "идти дождю",
         "tj": "борон боридан"},
        {"no": 7,  "zh": "小姐",  "pinyin": "xiǎojiě",  "pos": "n.",
         "uz": "xonim, mademoiselle",
         "ru": "мисс, барышня",
         "tj": "хонум, духтар (мурофиа)"},
        {"no": 8,  "zh": "来",    "pinyin": "lái",      "pos": "v.",
         "uz": "kelmoq",
         "ru": "приходить, приезжать",
         "tj": "омадан"},
        {"no": 9,  "zh": "身体",  "pinyin": "shēntǐ",   "pos": "n.",
         "uz": "tana, sog'liq",
         "ru": "тело, здоровье",
         "tj": "бадан, саломатӣ"},
        {"no": 10, "zh": "爱",    "pinyin": "ài",       "pos": "v.",
         "uz": "sevmoq, yaxshi ko'rmoq",
         "ru": "любить",
         "tj": "дӯст доштан, ишқ доштан"},
        {"no": 11, "zh": "些",    "pinyin": "xiē",      "pos": "m.",
         "uz": "bir oz, bir nechta",
         "ru": "немного, несколько",
         "tj": "каме, чанд"},
        {"no": 12, "zh": "水果",  "pinyin": "shuǐguǒ",  "pos": "n.",
         "uz": "meva",
         "ru": "фрукты",
         "tj": "мева"},
        {"no": 13, "zh": "水",    "pinyin": "shuǐ",     "pos": "n.",
         "uz": "suv",
         "ru": "вода",
         "tj": "об"},
    ], ensure_ascii=False),

    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "scene_uz": "Yo'lda — ob-havo muhokamasi",
            "scene_ru": "На улице — обсуждение погоды",
            "scene_tj": "Дар роҳ — муҳокимаи обу ҳаво",
            "dialogue": [
                {"speaker": "A", "zh": "昨天北京的天气怎么样？",    "pinyin": "Zuótiān Běijīng de tiānqì zěnmeyàng?",
                 "uz": "Kecha Pekindagi ob-havo qanday edi?",
                 "ru": "Какая вчера была погода в Пекине?",
                 "tj": "Дирӯз дар Пекин обу ҳаво чӣ хел буд?"},
                {"speaker": "B", "zh": "太热了。",                  "pinyin": "Tài rè le.",
                 "uz": "Juda issiq edi.",
                 "ru": "Было очень жарко.",
                 "tj": "Хеле гарм буд."},
                {"speaker": "A", "zh": "明天呢？明天天气怎么样？",  "pinyin": "Míngtiān ne? Míngtiān tiānqì zěnmeyàng?",
                 "uz": "Ertaga-chi? Ertaga ob-havo qanday bo'ladi?",
                 "ru": "А завтра? Какая будет погода?",
                 "tj": "Фардо чӣ? Фардо обу ҳаво чӣ хел мешавад?"},
                {"speaker": "B", "zh": "明天天气很好，不冷不热。",  "pinyin": "Míngtiān tiānqì hěn hǎo, bù lěng bú rè.",
                 "uz": "Ertaga ob-havo yaxshi bo'ladi, na sovuq na issiq.",
                 "ru": "Завтра погода будет хорошей, ни холодно ни жарко.",
                 "tj": "Фардо обу ҳаво хуб мешавад, на сард на гарм."},
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "scene_uz": "Sport zalda — yomg'ir va sovuq",
            "scene_ru": "В спортзале — дождь и холод",
            "scene_tj": "Дар варзишгоҳ — борон ва сармо",
            "dialogue": [
                {"speaker": "A", "zh": "今天会下雨吗？",        "pinyin": "Jīntiān huì xià yǔ ma?",
                 "uz": "Bugun yomg'ir yog'adimi?",
                 "ru": "Сегодня будет дождь?",
                 "tj": "Имрӯз борон меборад?"},
                {"speaker": "B", "zh": "今天不会下雨。",        "pinyin": "Jīntiān bú huì xià yǔ.",
                 "uz": "Bugun yomg'ir yog'maydi.",
                 "ru": "Сегодня дождя не будет.",
                 "tj": "Имрӯз борон намеборад."},
                {"speaker": "A", "zh": "王小姐今天会来吗？",    "pinyin": "Wáng xiǎojiě jīntiān huì lái ma?",
                 "uz": "Xonim Van bugun keladimi?",
                 "ru": "Мисс Ван сегодня придёт?",
                 "tj": "Хонум Ван имрӯз меояд?"},
                {"speaker": "B", "zh": "不会来，天气太冷了。",  "pinyin": "Bú huì lái, tiānqì tài lěng le.",
                 "uz": "Kelmaydi, ob-havo juda sovuq.",
                 "ru": "Не придёт — погода слишком холодная.",
                 "tj": "Намеояд, обу ҳаво хеле сард аст."},
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "scene_uz": "Kasalxonada — sog'liq haqida",
            "scene_ru": "В больнице — о здоровье",
            "scene_tj": "Дар беморхона — дар бораи саломатӣ",
            "dialogue": [
                {"speaker": "A", "zh": "你身体怎么样？",                      "pinyin": "Nǐ shēntǐ zěnmeyàng?",
                 "uz": "Sog'ligingiz qanday?",
                 "ru": "Как ваше здоровье?",
                 "tj": "Саломатии шумо чӣ хел аст?"},
                {"speaker": "B", "zh": "我身体不太好。天气太热了，不爱吃饭。", "pinyin": "Wǒ shēntǐ bú tài hǎo. Tiānqì tài rè le, bú ài chī fàn.",
                 "uz": "Sog'ligim unchalik yaxshi emas. Ob-havo juda issiq, ovqat yegim kelmayapti.",
                 "ru": "Здоровье не очень. Погода слишком жаркая, есть не хочется.",
                 "tj": "Саломатиям зияд хуб нест. Обу ҳаво хеле гарм аст, хӯрок хӯрданам намеояд."},
                {"speaker": "A", "zh": "你多吃些水果，多喝水。",              "pinyin": "Nǐ duō chī xiē shuǐguǒ, duō hē shuǐ.",
                 "uz": "Ko'proq meva yeng, ko'proq suv iching.",
                 "ru": "Ешьте больше фруктов и пейте больше воды.",
                 "tj": "Бештар мева хӯред, бештар об нӯшед."},
                {"speaker": "B", "zh": "谢谢你，医生。",                     "pinyin": "Xièxie nǐ, yīshēng.",
                 "uz": "Rahmat, doktor.",
                 "ru": "Спасибо, доктор.",
                 "tj": "Ташаккур, духтур."},
            ]
        },
    ], ensure_ascii=False),

    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "怎么样",
            "title_uz": "Holat so'roq olmoshi 怎么样",
            "title_ru": "Вопросительное слово состояния 怎么样",
            "title_tj": "Калимаи суолии ҳол 怎么样",
            "rule_uz": (
                "怎么样(zěnmeyàng) — holat, sifat yoki fikrni so'rash uchun ishlatiladi.\n"
                "Tuzilish: Ega + 怎么样?\n\n"
                "天气怎么样？— Ob-havo qanday?\n"
                "你身体怎么样？— Sog'ligingiz qanday?\n"
                "你的汉语怎么样？— Xitoy tilingiz qanday?"
            ),
            "rule_ru": (
                "怎么样(zěnmeyàng) — используется для спроса о состоянии, качестве или мнении.\n"
                "Структура: Подлежащее + 怎么样?\n\n"
                "天气怎么样？— Какая погода?\n"
                "你身体怎么样？— Как ваше здоровье?\n"
                "你的汉语怎么样？— Как ваш китайский?"
            ),
            "rule_tj": (
                "怎么样(zěnmeyàng) — барои пурсидани ҳол, сифат ё андеша истифода мешавад.\n"
                "Сохтор: Муб. + 怎么样?\n\n"
                "天气怎么样？— Обу ҳаво чӣ хел аст?\n"
                "你身体怎么样？— Саломатии шумо чӣ хел аст?\n"
                "你的汉语怎么样？— Забони чинии шумо чӣ хел аст?"
            ),
            "examples": [
                {"zh": "明天天气怎么样？", "pinyin": "Míngtiān tiānqì zěnmeyàng?",
                 "uz": "Ertaga ob-havo qanday bo'ladi?", "ru": "Какая будет погода завтра?", "tj": "Фардо обу ҳаво чӣ хел мешавад?"},
                {"zh": "你身体怎么样？",   "pinyin": "Nǐ shēntǐ zěnmeyàng?",
                 "uz": "Sog'ligingiz qanday?", "ru": "Как ваше здоровье?", "tj": "Саломатии шумо чӣ хел аст?"},
            ]
        },
        {
            "no": 2,
            "title_zh": "太……了",
            "title_uz": "Haddan tashqari: 太……了",
            "title_ru": "Конструкция 太……了 (слишком, очень)",
            "title_tj": "Сохтори 太……了 (хеле зиёд)",
            "rule_uz": (
                "太(tài) + Sifat + 了 — 'juda, haddan tashqari'\n"
                "Inkor: 不太 + Sifat (了 ishlatilmaydi)\n\n"
                "天气太热了。— Ob-havo juda issiq.\n"
                "太冷了！— Juda sovuq!\n"
                "我身体不太好。— Sog'ligim unchalik yaxshi emas."
            ),
            "rule_ru": (
                "太(tài) + Прилагательное + 了 — 'слишком, очень'\n"
                "Отрицание: 不太 + Прилагательное (без 了)\n\n"
                "天气太热了。— Погода слишком жаркая.\n"
                "太冷了！— Слишком холодно!\n"
                "我身体不太好。— Здоровье не очень хорошее."
            ),
            "rule_tj": (
                "太(tài) + Сифат + 了 — 'хеле зиёд, аз ҳад зиёд'\n"
                "Инкор: 不太 + Сифат (بدуни 了)\n\n"
                "天气太热了。— Обу ҳаво хеле гарм аст.\n"
                "太冷了！— Хеле сард аст!\n"
                "我身体不太好。— Саломатиям зияд хуб нест."
            ),
            "examples": [
                {"zh": "太热了！",      "pinyin": "Tài rè le!",
                 "uz": "Juda issiq!", "ru": "Слишком жарко!", "tj": "Хеле гарм аст!"},
                {"zh": "天气太冷了。",  "pinyin": "Tiānqì tài lěng le.",
                 "uz": "Ob-havo juda sovuq.", "ru": "Погода слишком холодная.", "tj": "Обу ҳаво хеле сард аст."},
                {"zh": "我不太好。",    "pinyin": "Wǒ bú tài hǎo.",
                 "uz": "Men unchalik yaxshi emasman.", "ru": "Я не очень хорошо.", "tj": "Ман зияд хуб нестам."},
            ]
        },
        {
            "no": 3,
            "title_zh": "能愿动词 会 (2)",
            "title_uz": "Modal fe'l 会 — ehtimollik bildiradi",
            "title_ru": "Модальный глагол 会 (2) — вероятность",
            "title_tj": "Феъли модалии 会 (2) — эҳтимол",
            "rule_uz": (
                "会 — kelajakda biror narsa sodir bo'lish ehtimolini bildiradi.\n\n"
                "今天会下雨吗？— Bugun yomg'ir yog'adimi?\n"
                "她会来吗？— U keladimi?\n"
                "不会 — bo'lmaydi, sodir bo'lmaydi"
            ),
            "rule_ru": (
                "会 — указывает на вероятность наступления события в будущем.\n\n"
                "今天会下雨吗？— Сегодня будет дождь?\n"
                "她会来吗？— Она придёт?\n"
                "不会 — не произойдёт, не будет"
            ),
            "rule_tj": (
                "会 — эҳтимоли рӯй додани чизеро дар оянда нишон медиҳад.\n\n"
                "今天会下雨吗？— Имрӯз борон меборад?\n"
                "她会来吗？— Ӯ меояд?\n"
                "不会 — намешавад, рӯй намедиҳад"
            ),
            "examples": [
                {"zh": "今天会下雨吗？", "pinyin": "Jīntiān huì xià yǔ ma?",
                 "uz": "Bugun yomg'ir yog'adimi?", "ru": "Сегодня будет дождь?", "tj": "Имрӯз борон меборад?"},
                {"zh": "明天会冷吗？",   "pinyin": "Míngtiān huì lěng ma?",
                 "uz": "Ertaga sovuq bo'ladimi?", "ru": "Завтра будет холодно?", "tj": "Фардо сард мешавад?"},
                {"zh": "她今天不会来。", "pinyin": "Tā jīntiān bú huì lái.",
                 "uz": "U bugun kelmaydi.", "ru": "Она сегодня не придёт.", "tj": "Ӯ имрӯз намеояд."},
            ]
        },
    ], ensure_ascii=False),

    "exercise_json": json.dumps([
        {
            "no": 1,
            "type": "translate_to_chinese",
            "instruction_uz": "Quyidagilarni xitoycha yozing:",
            "instruction_ru": "Напишите по-китайски:",
            "instruction_tj": "Ба хитоӣ нависед:",
            "items": [
                {"prompt_uz": "Ertaga ob-havo qanday bo'ladi?",  "prompt_ru": "Какая будет погода завтра?",    "prompt_tj": "Фардо обу ҳаво чӣ хел мешавад?",  "answer": "明天天气怎么样？", "pinyin": "Míngtiān tiānqì zěnmeyàng?"},
                {"prompt_uz": "Ob-havo juda issiq.",             "prompt_ru": "Погода слишком жаркая.",        "prompt_tj": "Обу ҳаво хеле гарм аст.",          "answer": "天气太热了。",     "pinyin": "Tiānqì tài rè le."},
                {"prompt_uz": "Bugun yomg'ir yog'adimi?",        "prompt_ru": "Сегодня будет дождь?",          "prompt_tj": "Имрӯз борон меборад?",             "answer": "今天会下雨吗？",   "pinyin": "Jīntiān huì xià yǔ ma?"},
                {"prompt_uz": "Sog'ligingiz qanday?",            "prompt_ru": "Как ваше здоровье?",            "prompt_tj": "Саломатии шумо чӣ хел аст?",       "answer": "你身体怎么样？",   "pinyin": "Nǐ shēntǐ zěnmeyàng?"},
                {"prompt_uz": "Ko'proq meva yeng.",              "prompt_ru": "Ешьте больше фруктов.",         "prompt_tj": "Бештар мева хӯред.",               "answer": "多吃些水果。",     "pinyin": "Duō chī xiē shuǐguǒ."},
            ]
        },
        {
            "no": 2,
            "type": "fill_blank",
            "instruction_uz": "Bo'sh joyni to'ldiring:",
            "instruction_ru": "Заполните пропуск:",
            "instruction_tj": "Холигиро пур кунед:",
            "items": [
                {"prompt": "天气___热了。",    "answer": "太",     "pinyin": "tài"},
                {"prompt": "明天天气___？",    "answer": "怎么样", "pinyin": "zěnmeyàng"},
                {"prompt": "今天会___雨吗？",  "answer": "下",     "pinyin": "xià"},
                {"prompt": "我身体不___好。",  "answer": "太",     "pinyin": "tài"},
            ]
        },
    ], ensure_ascii=False),

    "answers_json": json.dumps([
        {"no": 1, "answers": ["明天天气怎么样？", "天气太热了。", "今天会下雨吗？", "你身体怎么样？", "多吃些水果。"]},
        {"no": 2, "answers": ["太", "怎么样", "下", "太"]},
    ], ensure_ascii=False),

    "homework_json": json.dumps([
        {
            "no": 1,
            "instruction_uz": "Bugungi ob-havo haqida 3-4 ta gap yozing:",
            "instruction_ru": "Напишите 3–4 предложения о сегодняшней погоде:",
            "instruction_tj": "3-4 ҷумла дар бораи обу ҳавои имрӯзӣ нависед:",
            "words": ["天气", "太", "了", "热", "冷", "下雨", "怎么样"],
            "example": "今天天气___。天气___了。今天会___吗？",
        },
    ], ensure_ascii=False),

    "is_active": True,
}


async def seed():
    async with SessionLocal() as session:
        result = await session.execute(
            select(CourseLesson).where(CourseLesson.lesson_code == LESSON["lesson_code"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in LESSON.items():
                setattr(existing, key, value)
            await session.commit()
            print(f"Updated Lesson {LESSON['lesson_code']} — {LESSON['title']}.")
        else:
            lesson = CourseLesson(**LESSON)
            session.add(lesson)
            await session.commit()
            print(f"Created Lesson {LESSON['lesson_code']} — {LESSON['title']}.")


if __name__ == "__main__":
    asyncio.run(seed())
