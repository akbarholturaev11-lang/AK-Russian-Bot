from app.services.ai_service import AIService


ANALYZER_PROMPT = """
Ту ассистенти таҳлили тасвир ҳастӣ.

Вазифа:
Аз рӯи акс танҳо матни дар дохили тасвир бударо муайян кун.

Қоидаҳои қатъӣ:

1. Аксро бодиққат таҳлил кун.
2. Агар дар акс матн, калима, ҷумла, ҳарф ё рақам бошад — онҳоро айнан навис.
3. Ҳеҷ чизро аз худ илова накун.
4. Матнро ислоҳ накун.
5. Агар матн норавшан бошад, танҳо ҳамон қисми равшанро навис.
6. Агар дар акс ҳеҷ матн набошад, танҳо навис:

TEXT:
No text found

ELEMENTS:
None

Формати ҷавоб:

TEXT:
(ҳамон матне ки дар акс ҳаст)

ELEMENTS:
— ҳар калима, ҷумла ё қисми ҷудогона дар сатри алоҳида

Муҳим:
— Тарҷума накун
— Шарҳ надиҳ
— Дарс накун
— Танҳо матни дар акс бударо барор
"""


class ImageAnalyzerService:
    def __init__(self):
        self.ai_service = AIService()
        self.last_ai_result = None

    async def analyze_image(
        self,
        image_bytes: bytes,
        mime_type: str,
    ) -> str:
        self.last_ai_result = await self.ai_service.generate_vision_reply_with_usage(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=ANALYZER_PROMPT,
        )
        return self.last_ai_result.content
