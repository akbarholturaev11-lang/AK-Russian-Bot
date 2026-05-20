import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 5,
    "lesson_code": "HSK4-L05",
    "title": "只买对的，不买贵的",
    "goal": json.dumps({"uz": "xarid qilish, narx va sifat haqida gapirish; 的确, 再说, 实际上, 对...来说, 尤其 grammatik qoliplarini o'zlashtirish", "ru": "говорить о покупках, цене и качестве; освоить конструкции 的确, 再说, 实际上, 对...来说, 尤其", "tj": "гуфтугӯ дар бораи харид, нарх ва сифат; аз худ кардани қолипҳои 的确, 再说, 实际上, 对...来说, 尤其"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'To'g'risini sotib ol, qimmatini emas' mavzusiga bag'ishlangan. Unda do'konda xarid qilish, narx solishtirish va onlayn xarid haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 的确, 再说, 实际上, 对...来说, 尤其.", "ru": "Этот урок посвящён теме 'Покупай подходящее, а не дорогое'. В нём вы научитесь говорить о покупках в магазине, сравнении цен и онлайн-покупках. Основные грамматические конструкции: 的确, 再说, 实际上, 对...来说, 尤其.", "tj": "Ин дарс ба мавзӯи 'Дурустро бихар, гаронро не' бахшида шудааст. Дар он харид дар дӯкон, муқоисаи нарх ва харид дар интернет омӯхта мешавад. Қолипҳои асосии грамматикӣ: 的确, 再说, 实际上, 对...来说, 尤其."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "家具", "pinyin": "jiājù", "pos": "n.", "uz": "mebel", "ru": "мебель", "tj": "мебел"},
            {"no": 2, "zh": "沙发", "pinyin": "shāfā", "pos": "n.", "uz": "divan, sofa", "ru": "диван, софа", "tj": "диван, сӯфа"},
            {"no": 3, "zh": "打折", "pinyin": "dǎzhé", "pos": "v.", "uz": "chegirma qilmoq, narx tushirmoq", "ru": "делать скидку, снижать цену", "tj": "тахфиф додан, нарх кам кардан"},
            {"no": 4, "zh": "价格", "pinyin": "jiàgé", "pos": "n.", "uz": "narx, baho", "ru": "цена, стоимость", "tj": "нарх, баҳо"},
            {"no": 5, "zh": "质量", "pinyin": "zhìliàng", "pos": "n.", "uz": "sifat", "ru": "качество", "tj": "сифат"},
            {"no": 6, "zh": "肯定", "pinyin": "kěndìng", "pos": "adv.", "uz": "albatta, shubhasiz", "ru": "обязательно, без сомнения", "tj": "албатта, бешак"},
            {"no": 7, "zh": "流行", "pinyin": "liúxíng", "pos": "v./adj.", "uz": "mashhur bo'lmoq, tarqalmoq; modali", "ru": "быть популярным, распространяться; модный", "tj": "маъмул шудан, паҳн шудан; модӣ"},
            {"no": 8, "zh": "顺便", "pinyin": "shùnbiàn", "pos": "adv.", "uz": "yo'l-yo'lakay, bir zumda", "ru": "заодно, по пути", "tj": "дар роҳ, баробари он"},
            {"no": 9, "zh": "台", "pinyin": "tái", "pos": "m.", "uz": "dona (mashina, televizor uchun)", "ru": "единица (для машин, телевизоров)", "tj": "дона (барои мошин, телевизор)"},
            {"no": 10, "zh": "光", "pinyin": "guāng", "pos": "adv.", "uz": "faqat, shunchaki", "ru": "только, одного лишь", "tj": "танҳо, фақат"},
            {"no": 11, "zh": "实在", "pinyin": "shízài", "pos": "adv.", "uz": "haqiqatan, chindan ham", "ru": "действительно, по-настоящему", "tj": "воқеан, дар ҳақиқат"},
            {"no": 12, "zh": "冷冻", "pinyin": "lěngdòng", "pos": "v.", "uz": "muzlatmoq, sovutmoq", "ru": "замораживать, охлаждать", "tj": "яхмос кардан, хунук кардан"},
            {"no": 13, "zh": "效果", "pinyin": "xiàoguǒ", "pos": "n.", "uz": "natija, samara", "ru": "результат, эффект", "tj": "натиҷа, самара"},
            {"no": 14, "zh": "现金", "pinyin": "xiànjīn", "pos": "n.", "uz": "naqd pul", "ru": "наличные деньги", "tj": "пули нақд"},
            {"no": 15, "zh": "的确", "pinyin": "díquè", "pos": "adv.", "uz": "haqiqatan ham, rostdan", "ru": "действительно, в самом деле", "tj": "воқеан, ҳақиқатан"},
            {"no": 16, "zh": "再说", "pinyin": "zàishuō", "pos": "conj.", "uz": "bundan tashqari, yana ham", "ru": "к тому же, помимо этого", "tj": "ғайр аз ин, боз ҳам"},
            {"no": 17, "zh": "实际上", "pinyin": "shíjì shàng", "pos": "adv.", "uz": "aslida, haqiqatda", "ru": "на самом деле, в действительности", "tj": "дар асл, дар воқеъият"},
            {"no": 18, "zh": "尤其", "pinyin": "yóuqí", "pos": "adv.", "uz": "ayniqsa, xususan", "ru": "особенно, в особенности", "tj": "махсусан, бахусус"},
            {"no": 19, "zh": "信用卡", "pinyin": "xìnyòngkǎ", "pos": "n.", "uz": "kredit karta", "ru": "кредитная карта", "tj": "корти кредитӣ"},
            {"no": 20, "zh": "比较", "pinyin": "bǐjiào", "pos": "adv./v.", "uz": "nisbatan, ancha; solishtirmoq", "ru": "относительно, довольно; сравнивать", "tj": "нисбатан, кам-кам; муқоиса кардан"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "王静 va sotuvchi mebel do'konida divan sotib oladi",
                "scene_ru": "王静 и продавец в магазине мебели покупают диван",
                "scene_tj": "王静 ва фурӯшанда дар дӯкони мебел диван мехаранд",
                "dialogue": [
                    {"speaker": "售货员", "zh": "小姐，您好！您想看什么家具？需要我为您介绍一下吗？", "pinyin": "",
                     "uz": "Xonim, salom! Qanday mebel qidiryapsiz? Taqdim etishim kerakmi?",
                     "ru": "Здравствуйте! Какую мебель вы ищете? Могу я вам помочь?",
                     "tj": "Хонум, салом! Кадом мебелро мехоҳед? Муаррифӣ кунам?"},
                    {"speaker": "王静", "zh": "谢谢，我想买沙发。", "pinyin": "",
                     "uz": "Rahmat, divan sotib olmoqchi edim.",
                     "ru": "Спасибо, я хочу купить диван.",
                     "tj": "Ташаккур, мехоҳам диван харам."},
                    {"speaker": "售货员", "zh": "您看这款怎么样？现在正在打折，比平时便宜一些，就是今年最流行的款式。", "pinyin": "",
                     "uz": "Bu modelga qarang. Hozir chegirma, odatdagidan arzonroq, bu yilning eng mashhur modeli.",
                     "ru": "Посмотрите на эту модель. Сейчас идёт скидка, дешевле обычного — это самая популярная модель этого года.",
                     "tj": "Ба ин намуна нигаред. Ҳоло тахфиф аст, аз одат арзонтар — ин маъмултарин намудаи имсол аст."},
                    {"speaker": "王静", "zh": "价格还可以，就是不知道质量怎么样？", "pinyin": "",
                     "uz": "Narxi yomon emas, faqat sifati qanday ekanini bilmadim.",
                     "ru": "Цена ничего, только вот не знаю, какое качество.",
                     "tj": "Нарх кам-кам аст, фақат сифати он чист намедонам."},
                    {"speaker": "售货员", "zh": "质量肯定没问题！实在不满意，一周内可以退换。", "pinyin": "",
                     "uz": "Sifatiga shubha yo'q! Chindan ham mamnun bo'lmasangiz, bir hafta ichida qaytarib almashtirishingiz mumkin.",
                     "ru": "С качеством точно нет проблем! Если вправду не понравится, в течение недели можно вернуть или обменять.",
                     "tj": "Сифат албатта бе мушкил аст! Агар воқеан норозӣ бошед, дар тӯли як ҳафта метавонед баргардонед ё иваз кунед."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "王静 va 李进 do'konda xarid qiladi",
                "scene_ru": "王静 и 李进 делают покупки в магазине",
                "scene_tj": "王静 ва 李进 дар мағоза харид мекунанд",
                "dialogue": [
                    {"speaker": "王静", "zh": "喝家里的冰箱买太旧了，再说冷冻效果也不太好，还是买个新的吧。", "pinyin": "",
                     "uz": "Uyimizdagi muzlatgich juda eski bo'lib qoldi, bundan tashqari muzlatish samarasi ham yaxshi emas, yangi sotib olgan ma'qul.",
                     "ru": "Домашний холодильник уже совсем старый, к тому же и эффект заморозки неважный — лучше купим новый.",
                     "tj": "Яхдони хонагии мо хеле кӯҳна шудааст, ғайр аз ин самараи яхмос кардан ҳам чандон хуб нест — беҳтар аст нав харем."},
                    {"speaker": "李进", "zh": "这么多钱，你带够现金了吗？", "pinyin": "",
                     "uz": "Bu qadar pul, naqd pul etarlimi?",
                     "ru": "Столько денег — ты взяла достаточно наличных?",
                     "tj": "Ин қадар пул — пули нақди кофӣ бурдӣ?"},
                    {"speaker": "王静", "zh": "光带现金不够，我用信用卡吧。对了，顺便再看看那台洗衣机。", "pinyin": "",
                     "uz": "Faqat naqd pul bilan yetmaydi, kredit karta ishlataman. Aytganday, yo'l-yo'lakay kir yuvgich ham ko'rib o'tay.",
                     "ru": "Только наличных не хватит, воспользуюсь кредитной картой. Кстати, заодно посмотрю и на ту стиральную машину.",
                     "tj": "Танҳо пули нақд кифоя намешавад, аз корти кредитӣ истифода мебарам. Ба ҷониб, дар роҳ он мошини ҷомашӯиро ҳам бубинем."},
                    {"speaker": "李进", "zh": "好，不过买东西的确要货比三家，尤其是买家具这样的大件。", "pinyin": "",
                     "uz": "Yaxshi, lekin xarid qilishda haqiqatan ham bozorni o'rganish kerak, ayniqsa mebel kabi katta narsalarni.",
                     "ru": "Хорошо, но при покупках действительно нужно сравнивать цены в нескольких местах, особенно когда покупаешь крупные вещи вроде мебели.",
                     "tj": "Хуб, аммо ҳангоми харид воқеан бояд нарх дар якчанд ҷо муқоиса шавад, махсусан вақти харидани чизҳои калон ба монанди мебел."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "的确",
                "title_uz": "haqiqatan ham, rostdan",
                "title_ru": "действительно, в самом деле",
                "title_tj": "воқеан, ҳақиқатан",
                "rule_uz": "'Haqiqatan ham, rostdan' ma'nosini beradi. Biror narsa to'g'riligini ta'kidlash uchun ishlatiladi.",
                "rule_ru": "Означает 'действительно, в самом деле'. Используется для подтверждения истинности чего-либо.",
                "rule_tj": "Маънои 'воқеан, ҳақиқатан' дорад. Барои таъкиди дурустии чизе истифода мешавад.",
                "examples": [
                    {"zh": "买东西的确要货比三家。", "pinyin": "",
                     "uz": "Xarid qilishda haqiqatan ham narx solishtirilishi kerak.",
                     "ru": "При покупках действительно нужно сравнивать цены.",
                     "tj": "Ҳангоми харид воқеан бояд нарх муқоиса шавад."},
                    {"zh": "这件事的确很难。", "pinyin": "",
                     "uz": "Bu ish haqiqatan ham qiyin.",
                     "ru": "Это дело действительно очень сложное.",
                     "tj": "Ин кор воқеан хеле душвор аст."},
                ],
            },
            {
                "no": 2,
                "title_zh": "再说",
                "title_uz": "bundan tashqari, qolaverson",
                "title_ru": "к тому же, помимо этого",
                "title_tj": "ғайр аз ин, боз ҳам",
                "rule_uz": "'Bundan tashqari, qolaverson' ma'nosini beradi. Birinchi sababdan keyin ikkinchi sabab yoki mulohaza qo'shiladi.",
                "rule_ru": "Означает 'к тому же, помимо этого'. После первой причины добавляется вторая или дополнительное соображение.",
                "rule_tj": "Маънои 'ғайр аз ин, боз ҳам' дорад. Пас аз сабаби аввал сабаби дуввум ё мулоҳизаи иловагӣ илова мешавад.",
                "examples": [
                    {"zh": "冰箱太旧了，再说冷冻效果也不好。", "pinyin": "",
                     "uz": "Muzlatgich juda eski, bundan tashqari muzlatish samarasi ham yaxshi emas.",
                     "ru": "Холодильник совсем старый, к тому же и эффект заморозки плохой.",
                     "tj": "Яхдон хеле кӯҳна аст, ғайр аз ин самараи яхмос кардан ҳам бад аст."},
                    {"zh": "现在太晚了，再说我也累了。", "pinyin": "",
                     "uz": "Hozir juda kech, bundan tashqari men ham charchadim.",
                     "ru": "Уже очень поздно, к тому же я тоже устал.",
                     "tj": "Ҳоло хеле дер аст, ғайр аз ин ман ҳам хаста шудам."},
                ],
            },
            {
                "no": 3,
                "title_zh": "实际上",
                "title_uz": "aslida, haqiqatda",
                "title_ru": "на самом деле, в действительности",
                "title_tj": "дар асл, дар воқеъият",
                "rule_uz": "'Aslida, haqiqatda' ma'nosini beradi. Ko'rinish bilan haqiqat o'rtasidagi farqni bildiradi.",
                "rule_ru": "Означает 'на самом деле, в действительности'. Указывает на разницу между видимостью и реальностью.",
                "rule_tj": "Маънои 'дар асл, дар воқеъият' дорад. Фарқи байни намуд ва ҳақиқатро нишон медиҳад.",
                "examples": [
                    {"zh": "看起来便宜，实际上质量不好。", "pinyin": "",
                     "uz": "Ko'rinishda arzon, aslida sifati yaxshi emas.",
                     "ru": "На вид дёшево, но на самом деле качество плохое.",
                     "tj": "Ба назар арзон менамояд, аммо дар асл сифат бад аст."},
                    {"zh": "实际上这件事没那么难。", "pinyin": "",
                     "uz": "Aslida bu ish o'ylaganchalik qiyin emas.",
                     "ru": "На самом деле это дело не так сложно, как кажется.",
                     "tj": "Дар асл ин кор он қадар душвор нест, ки тасаввур мешуд."},
                ],
            },
            {
                "no": 4,
                "title_zh": "对……来说",
                "title_uz": "...uchun, ...nuqtayi nazaridan",
                "title_ru": "для..., с точки зрения...",
                "title_tj": "барои..., аз нигоҳи...",
                "rule_uz": "'...uchun, ...nuqtayi nazaridan' ma'nosini beradi. Biror kishi yoki guruh nuqtayi nazarini bildiradi.",
                "rule_ru": "Означает 'для..., с точки зрения...'. Выражает точку зрения определённого человека или группы.",
                "rule_tj": "Маънои 'барои..., аз нигоҳи...' дорад. Нуқтаи назари шахс ё гурӯҳи муайянро ифода мекунад.",
                "examples": [
                    {"zh": "对我来说，质量比价格更重要。", "pinyin": "",
                     "uz": "Men uchun sifat narxdan muhimroq.",
                     "ru": "Для меня качество важнее цены.",
                     "tj": "Барои ман сифат аз нарх муҳимтар аст."},
                    {"zh": "对学生来说，时间很宝贵。", "pinyin": "",
                     "uz": "Talabalar uchun vaqt juda qimmatli.",
                     "ru": "Для студентов время очень ценно.",
                     "tj": "Барои донишҷӯён вақт хеле қимматбаҳо аст."},
                ],
            },
            {
                "no": 5,
                "title_zh": "尤其",
                "title_uz": "ayniqsa, xususan",
                "title_ru": "особенно, в особенности",
                "title_tj": "махсусан, бахусус",
                "rule_uz": "'Ayniqsa, xususan' ma'nosini beradi. Biror narsani alohida ajratib ko'rsatish uchun ishlatiladi.",
                "rule_ru": "Означает 'особенно, в особенности'. Используется для выделения чего-либо из общего.",
                "rule_tj": "Маънои 'махсусан, бахусус' дорад. Барои ҷудо кардани чизе аз умумӣ истифода мешавад.",
                "examples": [
                    {"zh": "买大件尤其要注意质量。", "pinyin": "",
                     "uz": "Katta narsa sotib olishda ayniqsa sifatga e'tibor berish kerak.",
                     "ru": "При покупке крупных вещей особенно важно обращать внимание на качество.",
                     "tj": "Ҳангоми харидани чизҳои калон махсусан бояд ба сифат диққат дод."},
                    {"zh": "她喜欢运动，尤其喜欢游泳。", "pinyin": "",
                     "uz": "U sport qilishni yaxshi ko'radi, ayniqsa suzishni.",
                     "ru": "Она любит спорт, особенно плавание.",
                     "tj": "Вай варзишро дӯст медорад, махсусан шиноварӣро."},
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
                    {"prompt_uz": "narx, baho", "prompt_ru": "цена, стоимость", "prompt_tj": "нарх, баҳо", "answer": "价格", "pinyin": "jiàgé"},
                    {"prompt_uz": "sifat", "prompt_ru": "качество", "prompt_tj": "сифат", "answer": "质量", "pinyin": "zhìliàng"},
                    {"prompt_uz": "chegirma qilmoq", "prompt_ru": "делать скидку", "prompt_tj": "тахфиф додан", "answer": "打折", "pinyin": "dǎzhé"},
                    {"prompt_uz": "natija, samara", "prompt_ru": "результат, эффект", "prompt_tj": "натиҷа, самара", "answer": "效果", "pinyin": "xiàoguǒ"},
                    {"prompt_uz": "naqd pul", "prompt_ru": "наличные деньги", "prompt_tj": "пули нақд", "answer": "现金", "pinyin": "xiànjīn"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский эквивалент следующих слов:",
                "instruction_tj": "Муодили ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "的确", "prompt_ru": "的确", "prompt_tj": "的确", "answer": "haqiqatan ham, rostdan", "pinyin": "díquè"},
                    {"prompt_uz": "尤其", "prompt_ru": "尤其", "prompt_tj": "尤其", "answer": "ayniqsa, xususan", "pinyin": "yóuqí"},
                    {"prompt_uz": "实际上", "prompt_ru": "实际上", "prompt_tj": "实际上", "answer": "aslida, haqiqatda", "pinyin": "shíjì shàng"},
                    {"prompt_uz": "再说", "prompt_ru": "再说", "prompt_tj": "再说", "answer": "bundan tashqari", "pinyin": "zàishuō"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (的确、再说、实际上、对...来说、尤其):",
                "instruction_ru": "Выберите подходящее слово (的确、再说、实际上、对...来说、尤其):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (的确、再说、实际上、对...来说、尤其):",
                "items": [
                    {"prompt_uz": "______我来______，质量比价格更重要。", "prompt_ru": "______我来______，质量比价格更重要。", "prompt_tj": "______我来______，质量比价格更重要。", "answer": "对 / 来说", "pinyin": "duì / lái shuō"},
                    {"prompt_uz": "这件衣服______很贵，______质量也不怎么样。", "prompt_ru": "这件衣服______很贵，______质量也不怎么样。", "prompt_tj": "这件衣服______很贵，______质量也不怎么样。", "answer": "的确 / 再说", "pinyin": "díquè / zàishuō"},
                    {"prompt_uz": "她喜欢吃甜食，______喜欢巧克力。", "prompt_ru": "她喜欢吃甜食，______喜欢巧克力。", "prompt_tj": "她喜欢吃甜食，______喜欢巧克力。", "answer": "尤其", "pinyin": "yóuqí"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["价格", "质量", "打折", "效果", "现金"]},
            {"no": 2, "answers": ["haqiqatan ham, rostdan", "ayniqsa, xususan", "aslida, haqiqatda", "bundan tashqari"]},
            {"no": 3, "answers": ["对 / 来说", "的确 / 再说", "尤其"]},
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
                "words": ["价格", "质量", "的确", "尤其"],
                "example": "对我来说，的确质量比价格更重要，尤其是买家具的时候。",
            },
            {
                "no": 2,
                "instruction_uz": "'对...来说' va '尤其' qoliplaridan foydalanib har biridan 2 ta gap tuzing.",
                "instruction_ru": "Составьте по 2 предложения с конструкциями '对...来说' и '尤其'.",
                "instruction_tj": "Бо истифода аз қолипҳои '对...来说' ва '尤其' аз ҳар кадоме 2 ҷумла созед.",
                "topic_uz": "xarid qilish va pul sarflash mavzusida",
                "topic_ru": "на тему покупок и трат денег",
                "topic_tj": "дар мавзӯи харид ва харҷ кардани пул",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Siz xarid qilishda nimalarga e'tibor berasiz? 你买东西时最注重什么？",
                "topic_ru": "На что вы обращаете внимание при покупках? 你买东西时最注重什么？",
                "topic_tj": "Ҳангоми харид ба чӣ диққат медиҳед? 你买东西时最注重什么？",
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
