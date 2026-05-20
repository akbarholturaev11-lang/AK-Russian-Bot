import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 10,
    "lesson_code": "HSK4-L10",
    "title": "幸福的标准",
    "goal": json.dumps({"uz": "baxt va hayot maqsadlari haqida gapirish; 不过, 确实, 在...看来, 由于, 比如 grammatik qoliplarini o'zlashtirish", "ru": "говорить о счастье и жизненных целях; освоить грамматические конструкции 不过, 确实, 在...看来, 由于, 比如", "tj": "дар бораи хушбахтӣ ва мақсадҳои зиндагӣ гуфтугӯ кардан; азхуд кардани қолабҳои грамматикии 不过, 确实, 在...看来, 由于, 比如"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Baxt mezoni' mavzusiga bag'ishlangan. Unda baxtning ta'rifi, hayot maqsadlari va shaxsiy qadriyatlar haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 不过, 确实, 在...看来, 由于, 比如.", "ru": "Этот урок посвящён теме «Мерило счастья». В нём изучается, как говорить об определении счастья, жизненных целях и личных ценностях. Основные грамматические конструкции: 不过, 确实, 在...看来, 由于, 比如.", "tj": "Ин дарс ба мавзӯи «Меъёри хушбахтӣ» бахшида шудааст. Дар он гуфтугӯ дар бораи таърифи хушбахтӣ, мақсадҳои зиндагӣ ва арзишҳои шахсӣ омӯхта мешавад. Қолабҳои асосии грамматикӣ: 不过, 确实, 在...看来, 由于, 比如."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "礼拜天", "pinyin": "lǐbàitiān", "pos": "n.", "uz": "yakshanba kuni", "ru": "воскресенье", "tj": "якшанбе"},
            {"no": 2, "zh": "空儿", "pinyin": "kòngr", "pos": "n.", "uz": "bo'sh vaqt, fursat", "ru": "свободное время, возможность", "tj": "вақти холӣ, фурсат"},
            {"no": 3, "zh": "母亲", "pinyin": "mǔqīn", "pos": "n.", "uz": "ona (rasmiy)", "ru": "мать (официально)", "tj": "модар (расмӣ)"},
            {"no": 4, "zh": "不过", "pinyin": "búguò", "pos": "conj.", "uz": "lekin, biroq, ammo", "ru": "однако, но (мягкое противопоставление)", "tj": "аммо, лекин (муқобили мулоим)"},
            {"no": 5, "zh": "永远", "pinyin": "yǒngyuǎn", "pos": "adv.", "uz": "abadiy, doim, hamisha", "ru": "навсегда, всегда", "tj": "абадӣ, ҳамеша"},
            {"no": 6, "zh": "方向", "pinyin": "fāngxiàng", "pos": "n.", "uz": "yo'nalish, toraf", "ru": "направление, сторона", "tj": "самт, тараф"},
            {"no": 7, "zh": "优秀", "pinyin": "yōuxiù", "pos": "adj.", "uz": "a'lo, ajoyib, yuqori darajali", "ru": "отличный, превосходный", "tj": "аъло, бошукӯҳ, дараҷаи баланд"},
            {"no": 8, "zh": "硕士", "pinyin": "shuòshì", "pos": "n.", "uz": "magistr, magistratura bitiruvchisi", "ru": "магистр, выпускник магистратуры", "tj": "магистр, хатмкардаи магистратура"},
            {"no": 9, "zh": "翻译", "pinyin": "fānyì", "pos": "n./v.", "uz": "tarjimon; tarjima qilmoq", "ru": "переводчик; переводить", "tj": "тарҷумон; тарҷума кардан"},
            {"no": 10, "zh": "确实", "pinyin": "quèshí", "pos": "adv.", "uz": "haqiqatan ham, chindan", "ru": "действительно, в самом деле", "tj": "воқеан, дар ҳақиқат"},
            {"no": 11, "zh": "兴奋", "pinyin": "xīngfèn", "pos": "adj.", "uz": "hayajonlangan, shodon", "ru": "взволнованный, возбуждённый", "tj": "ҳаяҷонзада, шод"},
            {"no": 12, "zh": "拉", "pinyin": "lā", "pos": "v.", "uz": "tortmoq, sudramoq; torta bermoq", "ru": "тянуть, тащить; играть (на струнном)", "tj": "кашидан, бурдан; навохтан"},
            {"no": 13, "zh": "由于", "pinyin": "yóuyú", "pos": "conj.", "uz": "chunki, ...sababli", "ru": "из-за, вследствие, благодаря", "tj": "аз сабаби, бо сабаби"},
            {"no": 14, "zh": "比如", "pinyin": "bǐrú", "pos": "conj.", "uz": "masalan, misol uchun", "ru": "например, к примеру", "tj": "масалан, барои мисол"},
            {"no": 15, "zh": "标准", "pinyin": "biāozhǔn", "pos": "n./adj.", "uz": "mezon, standart; standart darajadagi", "ru": "критерий, стандарт; стандартный", "tj": "меъёр, стандарт; стандартӣ"},
            {"no": 16, "zh": "幸运", "pinyin": "xìngyùn", "pos": "adj./n.", "uz": "omadli; omad, baxt", "ru": "удачливый; удача, везение", "tj": "бахтёр; бахт, иқбол"},
            {"no": 17, "zh": "满足", "pinyin": "mǎnzú", "pos": "v./adj.", "uz": "qondirilmoq, qanoat qilmoq; mamnun", "ru": "удовлетворять; довольный", "tj": "қонеъ шудан, қаноат кардан; мамнун"},
            {"no": 18, "zh": "生命", "pinyin": "shēngmìng", "pos": "n.", "uz": "hayot, umr", "ru": "жизнь, существование", "tj": "ҳаёт, умр"},
            {"no": 19, "zh": "态度", "pinyin": "tàidu", "pos": "n.", "uz": "munosabat, pozitsiya", "ru": "отношение, позиция", "tj": "муносибат, мавқеъ"},
            {"no": 20, "zh": "实现", "pinyin": "shíxiàn", "pos": "v.", "uz": "amalga oshirmoq, ro'yobga chiqarmoq", "ru": "осуществлять, реализовывать", "tj": "амалӣ кардан, ба амал овардан"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "Sun Yue va Van Czing yakshanbadagi turmush haqida suhbatlashmoqda",
                "scene_ru": "Сунь Юэ и Ван Цзин разговаривают о воскресной жизни Ван Цзин",
                "scene_tj": "Сун Юэ ва Ван Ҷин дар бораи зиндагии якшанбаи Ван Ҷин сӯҳбат мекунанд",
                "dialogue": [
                    {"speaker": "孙月", "zh": "礼拜天有空儿吗？你在忙什么呢？", "pinyin": "", "uz": "Yakshanba kuni bo'sh vaqting bormi? Nima bilan shug'ullanayapsan?", "ru": "В воскресенье есть свободное время? Чем ты сейчас занята?", "tj": "Якшанбе вақти холӣ дорӣ? Бо чӣ машғулӣ?"},
                    {"speaker": "王静", "zh": "我可能去买东西，顺便把衣服送去干洗，最近家里事儿太多了。", "pinyin": "", "uz": "Ehtimol xarid qilgani boraman, yo'l-yo'lakay kiyimlarni kimyoviy tozalashga topshiraman, so'nggi paytlarda uy ishi juda ko'paydi.", "ru": "Наверное, пойду за покупками, заодно сдам одежду в химчистку — в последнее время домашних дел стало очень много.", "tj": "Эҳтимол барои харид мераям, дар роҳ либосҳоро ба химчистка мебарам, охирон корҳои хона хеле зиёд шудааст."},
                    {"speaker": "孙月", "zh": "你现在在上班，还有孩子和老母亲要照顾，确实挺忙的。", "pinyin": "", "uz": "Sen hozir ishda ham ishlaysan, farzand va qarigan onangni ham boqasan, chindan ham juda band.", "ru": "Ты сейчас работаешь и ещё должна заботиться о детях и пожилой маме — действительно очень занята.", "tj": "Ту ҳоло кор мекунӣ, ва ҳамчунин бояд аз фарзанд ва модари пиронсолат нигоҳубин кунӣ — воқеан хеле банд ҳастӣ."},
                    {"speaker": "王静", "zh": "不过，虽然忙，但我感觉很幸福。因为我有一个好的家庭，家人永远是我最重要的方向。", "pinyin": "", "uz": "Biroq, garchi band bo'lsam ham, o'zimni baxtli his qilaman. Chunki yaxshi oilam bor, oila hamisha uchun eng muhim yo'nalishim.", "ru": "Однако, несмотря на занятость, я чувствую себя счастливой. Ведь у меня хорошая семья, а семья — это навсегда мой главный ориентир.", "tj": "Аммо, гарчанде банд бошам ҳам, худро хушбахт эҳсос мекунам. Зеро оилаи хуб дорам, оила ҳамеша муҳимтарин самти ман аст."},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "Gao o'qituvchi va Li o'qituvchi baxt haqida suhbatlashmoqda",
                "scene_ru": "Учитель Гао и учитель Ли рассуждают о счастье",
                "scene_tj": "Муаллим Гао ва муаллим Ли дар бораи хушбахтӣ сӯҳбат мекунанд",
                "dialogue": [
                    {"speaker": "高老师", "zh": "你有没有人说你家儿子你也是老师，现在还有个好妻子，真让人羡慕。", "pinyin": "", "uz": "Kimdir dedi, sizning o'g'lingiz ham o'qituvchi, hozir yaxshi xotiningiz ham bor, rostdan hasad qilinadi.", "ru": "Кто-то говорил, что ваш сын тоже учитель, и сейчас ещё есть хорошая жена — действительно завидное положение.", "tj": "Касе гуфт, ки писарти ҳам муаллим аст, ва ҳоло зани хуб ҳам дорӣ — воқеан ҳасад мешавад."},
                    {"speaker": "李老师", "zh": "是呀，你说的没错，我确实是幸福的人。只是，幸福的标准对每个人来说是不一样的。", "pinyin": "", "uz": "Ha, to'g'ri aytasiz, men chindan ham baxtli odamman. Faqat baxtning mezoni har bir kishi uchun har xil.", "ru": "Да, вы правы, я действительно счастливый человек. Только критерии счастья у каждого разные.", "tj": "Бале, шумо дуруст мегӯед, ман воқеан одами хушбахтам. Танҳо меъёри хушбахтӣ барои ҳар кас фарқ мекунад."},
                    {"speaker": "高老师", "zh": "你觉得幸福的标准是什么？", "pinyin": "", "uz": "Sizningcha baxtning mezoni nima?", "ru": "По-вашему, каков критерий счастья?", "tj": "Ба ақидаи шумо, меъёри хушбахтӣ чист?"},
                    {"speaker": "李老师", "zh": "在我看来，幸福就是做自己喜欢做的事，由于每个人不同，比如有人觉得有钱就是幸福，有人觉得家庭和睦才是幸福。不过，我觉得最重要的是心里满足。", "pinyin": "", "uz": "Mening nazmimda, baxt — o'zingiz yaxshi ko'rgan narsani qilishdir. Har bir kishi boshqacha bo'lgani uchun, masalan, ba'zilar puli bo'lsa baxtli, ba'zilar oila baxtli bo'lsa baxtli. Biroq, menimcha eng muhimi — qalbdagi qanoat.", "ru": "На мой взгляд, счастье — это делать то, что тебе нравится. Поскольку все люди разные — например, одни считают счастьем богатство, другие — гармонию в семье. Однако, по-моему, самое важное — это душевная удовлетворённость.", "tj": "Аз нуқтаи назари ман, хушбахтӣ ин кор кардани чизест, ки дӯст дорӣ. Азбаски ҳар кас фарқ мекунад — масалан, баъзеҳо бо доштани пул хушбахтанд, баъзеҳо бо хушии оила. Аммо, ба ақидаи ман, муҳимтарин чиз — қаноати дилӣ аст."},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "不过",
                "title_uz": "不过 (lekin, biroq, ammo)",
                "title_ru": "不过 (однако, но)",
                "title_tj": "不过 (аммо, лекин)",
                "rule_uz": "'Lekin, biroq, ammo' ma'nosini beradi. Oldingi fikrga yumshoq ziddiyat bildiradi (但是 dan kamroq kuchli).",
                "rule_ru": "Означает «однако, но». Выражает мягкое противопоставление предыдущей мысли (слабее, чем 但是).",
                "rule_tj": "Маънои «аммо, лекин»-ро медиҳад. Муқобили мулоимро нисбат ба фикри қаблӣ нишон медиҳад (аз 但是 заифтар).",
                "examples": [
                    {"zh": "虽然很忙，不过感觉很幸福。", "pinyin": "", "uz": "Garchi juda band bo'lsam ham, biroq o'zimni baxtli his qilaman.", "ru": "Хотя очень занята, однако чувствую себя счастливой.", "tj": "Гарчанде хеле банд бошам ҳам, аммо худро хушбахт эҳсос мекунам."},
                    {"zh": "这道菜好吃，不过有点儿辣。", "pinyin": "", "uz": "Bu taom mazali, lekin biroz achchiq.", "ru": "Это блюдо вкусное, однако немного острое.", "tj": "Ин таом лазиз аст, аммо каме тунд аст."},
                ],
            },
            {
                "no": 2,
                "title_zh": "确实",
                "title_uz": "确实 (haqiqatan ham, chindan)",
                "title_ru": "确实 (действительно, в самом деле)",
                "title_tj": "确实 (воқеан, дар ҳақиқат)",
                "rule_uz": "'Haqiqatan ham, chindan' ma'nosini beradi. Biror narsa to'g'riligini qat'iy tasdiqlaydi.",
                "rule_ru": "Означает «действительно, в самом деле». Решительно подтверждает правильность чего-либо.",
                "rule_tj": "Маънои «воқеан, дар ҳақиқат»-ро медиҳад. Дурустии чизеро қатъиона тасдиқ мекунад.",
                "examples": [
                    {"zh": "我确实是幸福的人。", "pinyin": "", "uz": "Men chindan ham baxtli odamman.", "ru": "Я действительно счастливый человек.", "tj": "Ман воқеан одами хушбахтам."},
                    {"zh": "这里的天气确实很好。", "pinyin": "", "uz": "Bu yerdagi havo haqiqatan ham yaxshi.", "ru": "Погода здесь действительно хорошая.", "tj": "Ҳавои ин ҷо воқеан хуб аст."},
                ],
            },
            {
                "no": 3,
                "title_zh": "在……看来",
                "title_uz": "在……看来 (...ning nazmida, ...nuqtai nazaridan)",
                "title_ru": "在……看来 (с точки зрения..., по мнению...)",
                "title_tj": "在……看来 (аз нуқтаи назари..., ба ақидаи...)",
                "rule_uz": "'...ning nazmida, ...ning nuqtayi nazaridan' ma'nosini beradi. Biror kishining shaxsiy fikri yoki qarashini bildiradi.",
                "rule_ru": "Означает «с точки зрения..., по мнению...». Выражает личное мнение или взгляды кого-либо.",
                "rule_tj": "Маънои «аз нуқтаи назари..., ба ақидаи...»-ро медиҳад. Фикр ё нуқтаи назари шахсии касеро нишон медиҳад.",
                "examples": [
                    {"zh": "在我看来，幸福就是做自己喜欢做的事。", "pinyin": "", "uz": "Mening nazmimda, baxt — o'zingiz yaxshi ko'rgan narsani qilishdir.", "ru": "С моей точки зрения, счастье — это делать то, что тебе нравится.", "tj": "Аз нуқтаи назари ман, хушбахтӣ ин кор кардани чизест, ки дӯст дорӣ."},
                    {"zh": "在他看来，钱不是最重要的。", "pinyin": "", "uz": "Uning nazmida, pul eng muhim narsa emas.", "ru": "С его точки зрения, деньги — не самое важное.", "tj": "Аз нуқтаи назари ӯ, пул муҳимтарин чиз нест."},
                ],
            },
            {
                "no": 4,
                "title_zh": "由于",
                "title_uz": "由于 (...sababli, chunki)",
                "title_ru": "由于 (из-за, вследствие)",
                "title_tj": "由于 (аз сабаби, бо сабаби)",
                "rule_uz": "'...sababli, chunki' ma'nosini beradi. Sabab-natija munosabatida sabab qismini bildiradi (因为 dan rasmiyroq).",
                "rule_ru": "Означает «из-за, вследствие». Указывает на причину в причинно-следственной связи (более официально, чем 因为).",
                "rule_tj": "Маънои «аз сабаби, бо сабаби»-ро медиҳад. Қисми сабабро дар робитаи сабабу натиҷа нишон медиҳад (аз 因为 расмитар).",
                "examples": [
                    {"zh": "由于每个人不同，幸福的标准也不一样。", "pinyin": "", "uz": "Har bir kishi boshqacha bo'lgani sababli, baxtning mezoni ham har xil.", "ru": "Поскольку все люди разные, критерии счастья тоже отличаются.", "tj": "Азбаски ҳар кас фарқ мекунад, меъёри хушбахтӣ ҳам фарқ мекунад."},
                    {"zh": "由于下雨，比赛推迟了。", "pinyin": "", "uz": "Yomg'ir yog'gani sababli, musobaqa kechiktirildi.", "ru": "Из-за дождя соревнование перенесли.", "tj": "Аз сабаби борон, мусобиқа ба таъхир афтод."},
                ],
            },
            {
                "no": 5,
                "title_zh": "比如",
                "title_uz": "比如 (masalan, misol uchun)",
                "title_ru": "比如 (например, к примеру)",
                "title_tj": "比如 (масалан, барои мисол)",
                "rule_uz": "'Masalan, misol uchun' ma'nosini beradi. Umumiy fikrni aniqlashtirish uchun misol keltiradi.",
                "rule_ru": "Означает «например, к примеру». Приводит пример для уточнения общей мысли.",
                "rule_tj": "Маънои «масалан, барои мисол»-ро медиҳад. Мисол меорад барои равшантар кардани фикри умумӣ.",
                "examples": [
                    {"zh": "比如有人觉得有钱就是幸福。", "pinyin": "", "uz": "Masalan, ba'zilar puli bo'lsa baxtli deb o'ylaydi.", "ru": "Например, некоторые считают, что богатство — это счастье.", "tj": "Масалан, баъзеҳо фикр мекунанд, ки доштани пул хушбахтӣ аст."},
                    {"zh": "我喜欢运动，比如跑步和游泳。", "pinyin": "", "uz": "Men sportni yaxshi ko'raman, masalan yugurish va suzish.", "ru": "Я люблю спорт, например бег и плавание.", "tj": "Ман варзишро дӯст дорам, масалан давидан ва шиноварӣ."},
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
                "instruction_ru": "Напишите китайский вариант следующих слов:",
                "instruction_tj": "Тарҷумаи хитоии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "abadiy, doim", "prompt_ru": "навсегда, всегда", "prompt_tj": "абадӣ, ҳамеша", "answer": "永远", "pinyin": "yǒngyuǎn"},
                    {"prompt_uz": "mezon, standart", "prompt_ru": "критерий, стандарт", "prompt_tj": "меъёр, стандарт", "answer": "标准", "pinyin": "biāozhǔn"},
                    {"prompt_uz": "amalga oshirmoq", "prompt_ru": "осуществлять, реализовывать", "prompt_tj": "амалӣ кардан", "answer": "实现", "pinyin": "shíxiàn"},
                    {"prompt_uz": "mamnun, qanoat qilmoq", "prompt_ru": "довольный, удовлетворять", "prompt_tj": "мамнун, қаноат кардан", "answer": "满足", "pinyin": "mǎnzú"},
                    {"prompt_uz": "munosabat, pozitsiya", "prompt_ru": "отношение, позиция", "prompt_tj": "муносибат, мавқеъ", "answer": "态度", "pinyin": "tàidu"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский перевод следующих слов:",
                "instruction_tj": "Тарҷумаи ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "不过", "prompt_ru": "不过", "prompt_tj": "不过", "answer": "lekin, biroq", "pinyin": "búguò"},
                    {"prompt_uz": "确实", "prompt_ru": "确实", "prompt_tj": "确实", "answer": "haqiqatan ham, chindan", "pinyin": "quèshí"},
                    {"prompt_uz": "由于", "prompt_ru": "由于", "prompt_tj": "由于", "answer": "...sababli, chunki", "pinyin": "yóuyú"},
                    {"prompt_uz": "比如", "prompt_ru": "比如", "prompt_tj": "比如", "answer": "masalan, misol uchun", "pinyin": "bǐrú"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (不过、确实、在...看来、由于、比如):",
                "instruction_ru": "Выберите подходящее слово (不过、确实、在...看来、由于、比如):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (不过、确实、在...看来、由于、比如):",
                "items": [
                    {"prompt_uz": "______我______，家庭是最重要的。", "prompt_ru": "______我______，家庭是最重要的。", "prompt_tj": "______我______，家庭是最重要的。", "answer": "在 / 看来", "pinyin": "zài / kànlái"},
                    {"prompt_uz": "______天气不好，我们只好待在家里。", "prompt_ru": "______天气不好，我们只好待在家里。", "prompt_tj": "______天气不好，我们只好待在家里。", "answer": "由于", "pinyin": "yóuyú"},
                    {"prompt_uz": "我喜欢中国文化，______书法和京剧。", "prompt_ru": "我喜欢中国文化，______书法和京剧。", "prompt_tj": "我喜欢中国文化，______书法和京剧。", "answer": "比如", "pinyin": "bǐrú"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["永远", "标准", "实现", "满足", "态度"]},
            {"no": 2, "answers": ["lekin, biroq", "haqiqatan ham, chindan", "...sababli, chunki", "masalan, misol uchun"]},
            {"no": 3, "answers": ["在 / 看来", "由于", "比如"]},
        ],
        ensure_ascii=False,
    ),
    "homework_json": json.dumps(
        [
            {
                "no": 1,
                "instruction_uz": "Quyidagi so'zlardan foydalanib 3 ta gap tuzing:",
                "instruction_ru": "Составьте 3 предложения, используя следующие слова:",
                "instruction_tj": "Бо истифодаи калимаҳои зерин 3 ҷумла тартиб диҳед:",
                "words": ["幸福", "标准", "确实", "永远"],
                "example": "在我看来，幸福的标准确实因人而异，家人永远是最重要的。",
            },
            {
                "no": 2,
                "instruction_uz": "'在...看来' va '由于...所以...' qoliplaridan foydalanib har biridan 2 ta gap tuzing.",
                "instruction_ru": "Напишите по 2 предложения с конструкциями '在...看来' и '由于...所以...'.",
                "instruction_tj": "Бо қолабҳои '在...看来' ва '由于...所以...' аз ҳар кадом 2 ҷумла нависед.",
                "topic_uz": "baxt va hayot maqsadlari mavzusida",
                "topic_ru": "на тему счастья и жизненных целей",
                "topic_tj": "дар мавзӯи хушбахтӣ ва мақсадҳои зиндагӣ",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Siz uchun baxtning mezoni nima? 你幸福的标准是什么？",
                "topic_ru": "Каков для вас критерий счастья? 你幸福的标准是什么？",
                "topic_tj": "Барои шумо меъёри хушбахтӣ чист? 你幸福的标准是什么？",
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
