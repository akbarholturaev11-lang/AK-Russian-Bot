import asyncio
import json

from sqlalchemy import select

from app.db.session import SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSONS = [
    {
        "level": "hsk2",
        "lesson_order": 1,
        "lesson_code": "HSK2-L01",
        "title": "九月去北京旅游最好",
        "goal": "",
        "intro_text": "",
        "vocabulary_json": json.dumps([
            {"no": 1, "zh": "旅游", "pinyin": "lǚyóu", "pos": "v."},
            {"no": 2, "zh": "觉得", "pinyin": "juéde", "pos": "v."},
            {"no": 3, "zh": "最", "pinyin": "zuì", "pos": "adv."},
            {"no": 4, "zh": "为什么", "pinyin": "wèi shénme", "pos": ""},
            {"no": 5, "zh": "也", "pinyin": "yě", "pos": "adv."},
            {"no": 6, "zh": "运动", "pinyin": "yùndòng", "pos": "n./v."},
            {"no": 7, "zh": "踢足球", "pinyin": "tī zúqiú", "pos": ""},
            {"no": 8, "zh": "一起", "pinyin": "yìqǐ", "pos": "adv."},
            {"no": 9, "zh": "要", "pinyin": "yào", "pos": "aux."},
            {"no": 10, "zh": "新", "pinyin": "xīn", "pos": "adj."},
            {"no": 11, "zh": "它", "pinyin": "tā", "pos": "pron."},
            {"no": 12, "zh": "眼睛", "pinyin": "yǎnjing", "pos": "n."},
            {"no": 13, "zh": "花花", "pinyin": "Huāhua", "pos": "proper noun"}
        ], ensure_ascii=False),
        "dialogue_json": json.dumps([
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_label_zh": "在学校",
                "dialogue": [
                    {"speaker": "A", "zh": "我想去北京旅游，你觉得什么时候去最好？", "pinyin": "Wǒ xiǎng qù Běijīng lǚyóu, nǐ juéde shénme shíhou qù zuì hǎo?"},
                    {"speaker": "B", "zh": "九月去北京旅游最好。", "pinyin": "Jiǔ yuè qù Běijīng lǚyóu zuì hǎo."},
                    {"speaker": "A", "zh": "为什么？", "pinyin": "Wèi shénme?"},
                    {"speaker": "B", "zh": "九月的北京天气不冷也不热。", "pinyin": "Jiǔ yuè de Běijīng tiānqì bù lěng yě bú rè."}
                ]
            },
            {
                "block_no": 2,
                "section_label": "看照片 2",
                "scene_label_zh": "看照片",
                "dialogue": [
                    {"speaker": "A", "zh": "你喜欢什么运动？", "pinyin": "Nǐ xǐhuan shénme yùndòng?"},
                    {"speaker": "B", "zh": "我最喜欢踢足球。", "pinyin": "Wǒ zuì xǐhuan tī zúqiú."},
                    {"speaker": "A", "zh": "下午我们一起去踢足球吧。", "pinyin": "Xiàwǔ wǒmen yìqǐ qù tī zúqiú ba."},
                    {"speaker": "B", "zh": "好啊！", "pinyin": "Hǎo a!"}
                ]
            },
            {
                "block_no": 3,
                "section_label": "在家里 3",
                "scene_label_zh": "在家里",
                "dialogue": [
                    {"speaker": "A", "zh": "我们要不要买几个新的椅子？", "pinyin": "Wǒmen yào bú yào mǎi jǐ ge xīn de yǐzi?"},
                    {"speaker": "B", "zh": "好啊。什么时候去买？", "pinyin": "Hǎo a. Shénme shíhou qù mǎi?"},
                    {"speaker": "A", "zh": "明天下午怎么样？", "pinyin": "Míngtiān xiàwǔ zěnmeyàng?"},
                    {"speaker": "A", "zh": "你明天几点能回来？", "pinyin": "Nǐ míngtiān jǐ diǎn néng huílái?"},
                    {"speaker": "B", "zh": "三点多。", "pinyin": "Sān diǎn duō."}
                ]
            },
            {
                "block_no": 4,
                "section_label": "在家里 4",
                "scene_label_zh": "在家里",
                "dialogue": [
                    {"speaker": "A", "zh": "桌子下面有个猫。", "pinyin": "Zhuōzi xiàmiàn yǒu ge māo."},
                    {"speaker": "B", "zh": "那是我的猫，它叫花花。", "pinyin": "Nà shì wǒ de māo, tā jiào Huāhua."},
                    {"speaker": "A", "zh": "它很漂亮。", "pinyin": "Tā hěn piàoliang."},
                    {"speaker": "B", "zh": "是啊，我觉得它的眼睛最漂亮。", "pinyin": "Shì a, wǒ juéde tā de yǎnjing zuì piàoliang."},
                    {"speaker": "A", "zh": "它多大了？", "pinyin": "Tā duō dà le?"},
                    {"speaker": "B", "zh": "六个多月。", "pinyin": "Liù ge duō yuè."}
                ]
            }
        ], ensure_ascii=False),
        "grammar_json": json.dumps([
            {"no": 1, "title_zh": "助动词：要"},
            {"no": 2, "title_zh": "程度副词：最"},
            {"no": 3, "title_zh": "概数的表达：几、多"}
        ], ensure_ascii=False),
        "exercise_json": "[]",
        "answers_json": "[]",
        "homework_json": "[]",
        "review_json": "[]",
        "is_active": True
    }
]


async def upsert_lessons():
    async with SessionLocal() as session:
        for item in LESSONS:
            result = await session.execute(
                select(CourseLesson).where(CourseLesson.lesson_code == item["lesson_code"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.level = item["level"]
                existing.lesson_order = item["lesson_order"]
                existing.title = item["title"]
                existing.goal = item["goal"]
                existing.intro_text = item["intro_text"]
                existing.vocabulary_json = item["vocabulary_json"]
                existing.dialogue_json = item["dialogue_json"]
                existing.grammar_json = item["grammar_json"]
                existing.exercise_json = item["exercise_json"]
                existing.answers_json = item["answers_json"]
                existing.homework_json = item["homework_json"]
                existing.review_json = item["review_json"]
                existing.is_active = item["is_active"]
                print(f"updated: {item['lesson_code']}")
            else:
                session.add(CourseLesson(**item))
                print(f"inserted: {item['lesson_code']}")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(upsert_lessons())
