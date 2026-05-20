import json
import re
from typing import Any
from app.services.ai_service import AIService

COURSE_MODEL = "o4-mini"

# Steps where "press button below" hint is appended — exercise is handled separately (no hint)
_CONVERSATIONAL_STEPS = {
    "intro", "vocab", "vocabulary", "dialogue", "grammar",
    # V2 steps:
    "vocab_1", "vocab_2",
    "dialogue_1", "dialogue_2", "dialogue_3", "dialogue_4",
}

_PRESS_BUTTON_HINT = {
    "uz": "\n\n✅ <i>Tushundingiz bo'lsa, pastdagi tugmani bosing.</i>",
    "ru": "\n\n✅ <i>Если поняли — нажмите кнопку ниже.</i>",
    "tj": "\n\n✅ <i>Агар фаҳмидед, тугмаи поёниро пахш кунед.</i>",
}

# MUHIM QOIDA — barcha tushuntirish bulimlari uchun (intro/vocab/dialogue/grammar)
_EXPLANATION_RULE = """
MUHIM QOIDA (ASOSIY VAZIFA):
- Sen HECH QACHON foydalanuvchiga mashq, savol yoki test bermaysan
- Sening vazifang: foydalanuvchiga hozirgi mavzuni tushuntirish
- Agar foydalanuvchi savol bersa — tushuntir, misollar keltir
- Javob oxirida qo'shimcha savol yoki taklif yozma
- Aslo: "Endi mashq qilamiz", "Quyidagi savolga javob bering", "Sinab ko'ring" dema
"""

_VOCAB_BLOCK_RULE = """
FORMAT QOIDASI (JUDA MUHIM):
- Har bir so'zni FAQAT shu ko'rinishda yoz:

1. <b>汉字</b>
<code>pīnyīn</code>
Tarjima: qisqa tarjima
Misollar:
- 汉字 bilan oddiy gap — tarjimasi
- 汉字 bilan yana bitta oddiy gap — tarjimasi

- Har bir so'z alohida blok bo'lsin
- Iyeroglif, pinyin, tarjima va misollarni bitta qatorda aralashtirma
- Dars lug'atidan tashqariga chiqma
- Foydalanuvchi "nima", "tushunmadim", "qanaqa" kabi noaniq yozsa ham shu formatda qayta tushuntir
- Javob oxirida "Yana misollar xohlaysizmi?" kabi savol yozma
"""


class CourseTutorService:
    def __init__(self):
        self.ai_service = AIService()
        self.last_ai_result = None

    def _parse(self, value: Any, default: Any):
        if value is None or value == "":
            return default
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except Exception:
            return default

    def _safe(self, value: Any) -> str:
        return str(value).strip() if value else ""

    # ─── STEP PROMPTS ───────────────────────────────────────────

    def _prompt_intro(self, lesson, user_language, user_level) -> tuple:
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        dialogue = self._parse(getattr(lesson, "dialogue_json", None), [])
        grammar = self._parse(getattr(lesson, "grammar_json", None), [])
        intro_text = self._safe(getattr(lesson, "intro_text", ""))
        title = self._safe(getattr(lesson, "title", ""))

        data = {
            "lesson_title": title,
            "intro_text": intro_text,
            "vocabulary_preview": vocab[:3],
            "grammar_preview": grammar[:1],
            "dialogue_preview": dialogue[:1],
        }

        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Talabani bu darsga iliq kutib ol.

DARS MA'LUMOTLARI:
{json.dumps(data, ensure_ascii=False, indent=2)}

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasiga moslashtirilgan
- Xitoy belgilari uchun <b>...</b>, pinyin uchun <code>...</code> ishlatilsin
- Jami 4 qatordan oshmasin
- 2-3 ta so'z va asosiy grammatika mavzusini qiziqarli tarzda tanishtir
- Hali o'qitma — faqat tanishtir
- Oxirida "Tayyor? Ketdik! 🚀" kabi quvnoq gap bilan tugat ({user_language} tilida)
{_EXPLANATION_RULE}"""

        return prompt, data

    def _prompt_vocab(self, lesson, user_language, user_level) -> tuple:
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        title = self._safe(getattr(lesson, "title", ""))

        data = {"lesson_title": title, "vocabulary": vocab}

        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Bu darsning so'zlarini qiziqarli tarzda o'rgat.

SO'ZLAR MA'LUMOTI:
{json.dumps(data, ensure_ascii=False, indent=2)}

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Xitoy belgilari uchun <b>...</b>, pinyin uchun <code>...</code>
- O'xshash so'zlar bo'lsa (masalan 我/你, 大/小), ularni yonma-yon solishtir
- Maksimal 8 ta so'zni tushuntir
{_VOCAB_BLOCK_RULE}
{_EXPLANATION_RULE}"""

        return prompt, data

    def _prompt_dialogue(self, lesson, user_language, user_level) -> tuple:
        dialogue = self._parse(getattr(lesson, "dialogue_json", None), [])
        title = self._safe(getattr(lesson, "title", ""))

        data = {"lesson_title": title, "dialogue": dialogue}

        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Bu dialogni qadamma-qadam o'rgat.

DIALOG MA'LUMOTI:
{json.dumps(data, ensure_ascii=False, indent=2)}

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Xitoy: <b>...</b>, pinyin: <code>...</code>
- Har bir qator: <b>Xitoycha</b> [<code>pinyin</code>] — {user_language}dagi ma'nosi
- Taqdimotdan keyin kontekstni qisqacha tushuntir (bu suhbat qayerda/qachon bo'ladi)
- Dialogdan 1-2 ta foydali iboralarni amaliy hayot bilan solishtirgan holda tushuntir
- Jami 12 qatordan oshmasin
- Foydalanuvchi dialog haqida savol bersa — tushuntir va TAKLIF qil (masalan: "Ushbu ibora boshqa situatsiyalarda qanday ishlatiladi, ko'rmoqchimisiz?")
{_EXPLANATION_RULE}"""

        return prompt, data

    def _prompt_grammar(self, lesson, user_language, user_level) -> tuple:
        grammar = self._parse(getattr(lesson, "grammar_json", None), [])
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        title = self._safe(getattr(lesson, "title", ""))

        data = {
            "lesson_title": title,
            "grammar_points": grammar,
            "lesson_vocabulary": vocab[:5],
        }

        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Grammatika qoidalarini aniq va qisqa tushuntir.

GRAMMATIKA MA'LUMOTI:
{json.dumps(data, ensure_ascii=False, indent=2)}

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Xitoy: <b>...</b>, pinyin: <code>...</code>
- Har bir grammatika nuqtasi: qoida → bo'sh joy bilan naqsh → dars lug'atidan 2 ta misol
- O'xshash tuzilmalar bo'lsa (masalan 的/地/得, 吗/呢, 在/有), tezkor maslahat bilan solishtir
- Misollar FAQAT lesson_vocabulary so'zlaridan foydalansin
- Jami 10 qatordan oshmasin
- Foydalanuvchi savol bersa tushuntir va TAKLIF qil (masalan: "Bu qoidani boshqa misollar bilan ko'rmoqchimisiz?")
{_EXPLANATION_RULE}"""

        return prompt, data

    def _prompt_exercise(self, lesson, user_language, user_level) -> tuple:
        exercise = self._parse(getattr(lesson, "exercise_json", None), [])
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        grammar = self._parse(getattr(lesson, "grammar_json", None), [])
        answers = self._parse(getattr(lesson, "answers_json", None), [])
        title = self._safe(getattr(lesson, "title", ""))

        if not exercise:
            exercise = {
                "instruction": "Create 3 exercises from the lesson vocabulary and grammar only.",
                "allowed_vocabulary": [w.get("zh","") for w in vocab[:8] if isinstance(w,dict)],
                "allowed_grammar": [g.get("title_zh","") for g in grammar[:3] if isinstance(g,dict)],
            }

        data = {
            "lesson_title": title,
            "exercises": exercise,
            "correct_answers": answers,
            "allowed_vocabulary": vocab[:8],
            "allowed_grammar": grammar[:3],
        }

        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Foydalanuvchi mashq javoblarini tekshir.

MASHQ MA'LUMOTI:
{json.dumps(data, ensure_ascii=False, indent=2)}

ASOSIY VAZIFA — JAVOBNI MAZMUN BO'YICHA TEKSHIR (FORMAT BO'YICHA EMAS):
- Foydalanuvchi xitoy belgilari, pinyin yoki ma'no yozishi mumkin — BARCHASI QABUL QILINADI
- HTML teglari (<b>, <code>) talab qilinmaydi — foydalanuvchi oddiy matn yozadi
- Har bir javobni FAQAT MAZMUN bo'yicha tekshir:
  * ✅ — ma'no/so'z to'g'ri bo'lsa
  * ❌ — ma'no/so'z noto'g'ri bo'lsa
- Noto'g'ri bo'lsa: TO'G'RI JAVOBNI ko'rsat (faqat bot o'zi <b>汉字</b> [<code>pinyin</code>] — ma'no formatida yozadi)
- Xatolarni qisqa tushuntir
- Rag'batlantiruvchi bo'l: "Yaxshi! 👏" yoki "Deyarli to'g'ri! Mana maslahat..."

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Bot o'z javobida xitoy: <b>...</b>, pinyin: <code>...</code> ishlatadi
- Jami 10 qatordan oshmasin
- Keyingi bo'limga o'tish haqida HECH NARSA dema — tizim o'zi o'tkazadi"""

        return prompt, data

    def _prompt_quiz(self, lesson, user_language, user_level) -> tuple:
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        grammar = self._parse(getattr(lesson, "grammar_json", None), [])
        title = self._safe(getattr(lesson, "title", ""))

        data = {
            "lesson_title": title,
            "test_vocabulary": vocab[:10],
            "test_grammar": grammar[:3],
        }

        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Foydalanuvchiga TEST savollarini ber.

TEST MA'LUMOTI:
{json.dumps(data, ensure_ascii=False, indent=2)}

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Xitoy: <b>...</b>, pinyin: <code>...</code>
- BIRINCHI CHAQIRUVDA (foydalanuvchi xabari yo'q bo'lsa):
  * FAQAT 3-4 ta TEST SAVOLI ber — raqamlangan (1, 2, 3, 4)
  * Savol turlari: ko'p tanlovli (A/B/C/D) YOKI bo'sh to'ldirish
  * FAQAT test_vocabulary va test_grammar dan — tashqi so'z yo'q
  * Tushuntirma, izoh, so'z ma'nolari BERMA — faqat savollar
- FOYDALANUVCHI JAVOB YUBORGANDA:
  * Har bir javobni tekshir: ✅ to'g'ri yoki ❌ noto'g'ri
  * Noto'g'ri bo'lsa: TO'G'RI JAVOBNI ko'rsat
  * Umumiy ball ber (masalan: 3/4 ✅)
  * Xatolarni 1 qatorda qisqa tushuntir
- Rag'batlantiruvchi bo'l
- Jami 12 qatordan oshmasin"""

        return prompt, data

    def _prompt_satisfaction_check(self, lesson, user_language, user_level) -> tuple:
        title = self._safe(getattr(lesson, "title", ""))
        data = {"lesson_title": title}

        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Talaba bu darsni tushunganini tekshir.

DARS: {title}

QOIDALAR:
- Faqat {user_language} tilida javob ber
- BITTA oddiy savol ber: darsni tushundingizmi?
- Maksimal 2 qator
- Yangi kontent o'qitma
- Oldinga siljima — talabaning tugmalar orqali javobini kut"""

        return prompt, data

    def _prompt_homework(self, lesson, user_language, user_level) -> tuple:
        homework = self._parse(getattr(lesson, "homework_json", None), [])
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        grammar = self._parse(getattr(lesson, "grammar_json", None), [])
        title = self._safe(getattr(lesson, "title", ""))

        if not homework:
            homework = {
                "instruction": "Create 1 homework task using only lesson vocabulary and grammar.",
                "allowed_vocabulary": [w.get("zh","") for w in vocab[:8] if isinstance(w,dict)],
                "allowed_grammar": [g.get("title_zh","") for g in grammar[:3] if isinstance(g,dict)],
            }

        data = {
            "lesson_title": title,
            "homework": homework,
            "allowed_vocabulary": vocab[:8],
            "allowed_grammar": grammar[:3],
        }

        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Uy vazifasini baholash.

UY VAZIFASI MA'LUMOTI:
{json.dumps(data, ensure_ascii=False, indent=2)}

ASOSIY VAZIFA — FOYDALANUVCHI JAVOBINI TEKSHIR:
- Har bir bandni tekshir: ✅ to'g'ri yoki ❌ noto'g'ri
- Noto'g'ri bo'lsa: TO'G'RI JAVOBNI va TO'G'RI FORMATNI ko'rsat
- Ball ber: 0-100
- Nimasi yaxshi va nimani yaxshilash kerakligini aniq ayt
- Rag'batlantiruvchi va aniq bo'l

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Xitoy: <b>...</b>, pinyin: <code>...</code>
- Maksimal 8 qator"""

        return prompt, data

    def _prompt_vocab_1(self, lesson, user_language, user_level) -> tuple:
        """V2: birinchi 8 ta so'z."""
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        vocab_page = vocab[:8]
        title = self._safe(getattr(lesson, "title", ""))
        data = {"lesson_title": title, "vocabulary": vocab_page}
        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Bu darsning birinchi qismidagi so'zlarni qiziqarli tarzda o'rgat.

SO'ZLAR (1–8):
{json.dumps(data, ensure_ascii=False, indent=2)}

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Xitoy belgilari uchun <b>...</b>, pinyin uchun <code>...</code>
- Maksimal 8 ta so'zni tushuntir
{_VOCAB_BLOCK_RULE}
{_EXPLANATION_RULE}"""
        return prompt, data

    def _prompt_vocab_2(self, lesson, user_language, user_level) -> tuple:
        """V2: 9+ so'zlar."""
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        vocab_page = vocab[8:]
        title = self._safe(getattr(lesson, "title", ""))
        data = {"lesson_title": title, "vocabulary": vocab_page}
        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Bu darsning ikkinchi qismidagi so'zlarni o'rgat.

SO'ZLAR (9+):
{json.dumps(data, ensure_ascii=False, indent=2)}

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Xitoy belgilari uchun <b>...</b>, pinyin uchun <code>...</code>
- Maksimal 8 ta so'zni tushuntir
{_VOCAB_BLOCK_RULE}
{_EXPLANATION_RULE}"""
        return prompt, data

    def _prompt_dialogue_n(self, lesson, user_language, user_level, n: int = 1) -> tuple:
        """V2: n-chi dialog bloki (grammar_notes inline)."""
        import json as _json
        dialogues = self._parse(getattr(lesson, "dialogue_json", None), [])
        block = dialogues[n - 1] if isinstance(dialogues, list) and len(dialogues) >= n else {}
        title = self._safe(getattr(lesson, "title", ""))
        data = {"lesson_title": title, "dialogue_block": block, "block_number": n}
        prompt = f"""Sen do'stona HSK xitoy tili o'qituvchisisан. Bu dialogni va unga bog'liq grammatikani qisqa tushuntir.

DIALOG MA'LUMOTI:
{_json.dumps(data, ensure_ascii=False, indent=2)}

QOIDALAR:
- Faqat {user_language} tilida javob ber, {user_level} darajasi
- Xitoy: <b>...</b>, pinyin: <code>...</code>
- Har bir qator: <b>Xitoycha</b> [<code>pinyin</code>] — tarjima
- Dialogdan 1-2 ta foydali ibora va grammar_notes ni qisqa tushuntir
- Jami 12 qatordan oshmasin
{_EXPLANATION_RULE}"""
        return prompt, data

    # ─── STEP ROUTER ────────────────────────────────────────────

    def _build_prompt_for_step(self, lesson, step: str, user_language: str, user_level: str) -> tuple:
        # V2 dialogue_N steps
        if step.startswith("dialogue_"):
            try:
                n = int(step.split("_", 1)[1])
            except (ValueError, IndexError):
                n = 1
            return self._prompt_dialogue_n(lesson, user_language, user_level, n)

        handlers = {
            "intro":               self._prompt_intro,
            "vocab":               self._prompt_vocab,
            "vocabulary":          self._prompt_vocab,
            # V2 vocab steps
            "vocab_1":             self._prompt_vocab_1,
            "vocab_2":             self._prompt_vocab_2,
            "dialogue":            self._prompt_dialogue,
            "grammar":             self._prompt_grammar,
            "exercise":            self._prompt_exercise,
            "quiz":                self._prompt_quiz,
            "satisfaction_check":  self._prompt_satisfaction_check,
            "homework":            self._prompt_homework,
        }
        handler = handlers.get(step, self._prompt_intro)
        return handler(lesson, user_language, user_level)

    # ─── PUBLIC METHODS ──────────────────────────────────────────

    async def generate_step_response(
        self,
        user_language: str,
        user_level: str,
        lesson,
        step: str,
        user_message: str = "",
        history: list = None,
    ) -> str:
        prompt, _ = self._build_prompt_for_step(lesson, step, user_language, user_level)

        full_text = prompt
        if user_message:
            full_text += f"\n\nFOYDALANUVCHI XABARI:\n{user_message}"

        self.last_ai_result = await self.ai_service.generate_reply_with_usage(
            text=full_text,
            user_language=user_language,
            user_level=user_level,
            history=history or [],
            model_override=COURSE_MODEL,
        )
        response = self.last_ai_result.content

        if step in _CONVERSATIONAL_STEPS:
            hint = _PRESS_BUTTON_HINT.get(user_language, _PRESS_BUTTON_HINT["ru"])
            response = response.rstrip() + hint

        return response

    def _build_homework_evaluation_prompt(self, user_language, user_level, lesson, submission_text) -> str:
        vocab = self._parse(getattr(lesson, "vocabulary_json", None), [])
        grammar = self._parse(getattr(lesson, "grammar_json", None), [])
        homework = self._parse(getattr(lesson, "homework_json", None), [])
        title = self._safe(getattr(lesson, "title", ""))

        if not homework:
            homework = {
                "instruction": "Evaluate based on lesson vocabulary and grammar.",
                "allowed_vocabulary": [w.get("zh","") for w in vocab[:8] if isinstance(w,dict)],
            }

        payload = {
            "lesson_title": title,
            "homework": homework,
            "allowed_vocabulary": vocab[:8],
            "allowed_grammar": grammar[:3],
            "student_submission": submission_text,
        }

        return f"""You are evaluating a student's homework for an HSK lesson.

DATA:
{json.dumps(payload, ensure_ascii=False, indent=2)}

RULES:
- Evaluate ONLY against the homework and lesson content above
- Give score 0-100
- decided passed = true if score >= 60
- feedback_text must be in {user_language}, short and clear
- Explain what is correct
- If there are mistakes, explain WHY each mistake is wrong
- Show the correct version or a good example answer
- Always include the score clearly, for example: "Ball: 72/100"
- If score is below 60, do NOT tell the student to press menu buttons or reread the lesson.
  The bot will show separate action buttons after your feedback.
- Do not use Markdown or HTML
- Return ONLY valid JSON, nothing else:
{{"score": 0, "passed": false, "feedback_text": "..."}}"""

    async def evaluate_homework(self, user_language, user_level, lesson, submission_text) -> dict:
        submission_text = (submission_text or "").strip()
        if not submission_text:
            return {"score": 0, "passed": False, "feedback_text": "Empty submission."}

        prompt = self._build_homework_evaluation_prompt(user_language, user_level, lesson, submission_text)

        self.last_ai_result = await self.ai_service.generate_reply_with_usage(
            text=prompt,
            user_language=user_language,
            user_level=user_level,
            history=[],
            model_override=COURSE_MODEL,
        )
        raw = self.last_ai_result.content

        try:
            cleaned = raw.strip().replace("```json","").replace("```","")
            data = json.loads(cleaned)
        except Exception:
            data = {"score": 60, "passed": True, "feedback_text": raw.strip()}

        raw_score = data.get("score", 60)
        try:
            score = int(float(raw_score))
        except (TypeError, ValueError):
            match = re.search(r"\d+", str(raw_score))
            score = int(match.group(0)) if match else 60
        score = max(0, min(100, score))
        passed = score >= 60
        feedback = str(data.get("feedback_text", "")).strip()

        if not feedback:
            feedback = f"✅ {score}/100"

        return {"score": score, "passed": passed, "feedback_text": feedback}
