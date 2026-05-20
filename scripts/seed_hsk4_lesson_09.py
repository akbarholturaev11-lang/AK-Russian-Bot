import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson


LESSON = {
    "level": "hsk4",
    "lesson_order": 9,
    "lesson_code": "HSK4-L09",
    "title": "阳光总在风雨后",
    "goal": json.dumps({"uz": "sport, qiyinchiliklar va muvaffaqiyat haqida gapirish; 渐渐, 通过, 结果, 坚持 grammatik qoliplarini o'zlashtirish", "ru": "говорить о спорте, трудностях и успехе; освоить грамматические конструкции 渐渐, 通过, 结果, 坚持", "tj": "дар бораи варзиш, душвориҳо ва муваффақият гуфтугӯ кардан; азхуд кардани қолабҳои грамматикии 渐渐, 通过, 结果, 坚持"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu dars 'Quyosh yomg'irdan keyin chiqadi' mavzusiga bag'ishlangan. Unda sport musobaqalari, qiyinchiliklarga bardosh berish va muvaffaqiyat sari harakat haqida gaplashish o'rganiladi. Asosiy grammatik qoliplar: 渐渐, 通过, 可是, 结果, 上.", "ru": "Этот урок посвящён теме «После дождя выходит солнце». В нём изучается, как говорить о спортивных соревнованиях, преодолении трудностей и движении к успеху. Основные грамматические конструкции: 渐渐, 通过, 可是, 结果, 上.", "tj": "Ин дарс ба мавзӯи «Офтоб пас аз борон мебарояд» бахшида шудааст. Дар он гуфтугӯ дар бораи мусобиқаҳои варзишӣ, тоқат кардан ба душвориҳо ва кӯшиш ба сӯи муваффақият омӯхта мешавад. Қолабҳои асосии грамматикӣ: 渐渐, 通过, 可是, 结果, 上."}, ensure_ascii=False),
    "vocabulary_json": json.dumps(
        [
            {"no": 1, "zh": "饼干", "pinyin": "bǐnggān", "pos": "n.", "uz": "pechenye, biskvit", "ru": "печенье, бисквит", "tj": "печенье, бисквит"},
            {"no": 2, "zh": "难道", "pinyin": "nándào", "pos": "adv.", "uz": "masa, axir (ritorik savol uchun)", "ru": "неужели, разве (для риторического вопроса)", "tj": "магар, ҳатто (барои саволи риторикӣ)"},
            {"no": 3, "zh": "得", "pinyin": "děi", "pos": "modal", "uz": "kerak, shart (majburiyat)", "ru": "нужно, необходимо (обязанность)", "tj": "бояд, лозим аст (ҳатмӣ)"},
            {"no": 4, "zh": "坚持", "pinyin": "jiānchí", "pos": "v.", "uz": "davom ettirmoq, chidamoq, qat'iy turmoq", "ru": "настаивать, продолжать, упорствовать", "tj": "давом додан, тоқат кардан, устувор истодан"},
            {"no": 5, "zh": "放弃", "pinyin": "fàngqì", "pos": "v.", "uz": "voz kechmoq, tashlab ketmoq", "ru": "отказываться, бросать", "tj": "даст кашидан, тарк кардан"},
            {"no": 6, "zh": "主意", "pinyin": "zhǔyì", "pos": "n.", "uz": "fikr, g'oya, qaror", "ru": "идея, мысль, решение", "tj": "фикр, ғоя, қарор"},
            {"no": 7, "zh": "网球", "pinyin": "wǎngqiú", "pos": "n.", "uz": "tennis", "ru": "теннис", "tj": "теннис"},
            {"no": 8, "zh": "国际", "pinyin": "guójì", "pos": "adj.", "uz": "xalqaro", "ru": "международный", "tj": "байналмилалӣ"},
            {"no": 9, "zh": "轻松", "pinyin": "qīngsōng", "pos": "adj.", "uz": "yengil, oson, erkin", "ru": "лёгкий, непринуждённый", "tj": "сабук, осон, озод"},
            {"no": 10, "zh": "赢", "pinyin": "yíng", "pos": "v.", "uz": "g'alaba qozonmoq, yutmoq", "ru": "выигрывать, побеждать", "tj": "ғалаба кардан, бурдан"},
            {"no": 11, "zh": "随便", "pinyin": "suíbiàn", "pos": "adj./adv.", "uz": "befarq, ixtiyoriy; istalgan vaqt", "ru": "беспечный, произвольный; как угодно", "tj": "беэтиноӣ, ихтиёрӣ; ҳар вақт"},
            {"no": 12, "zh": "汗", "pinyin": "hàn", "pos": "n.", "uz": "ter", "ru": "пот", "tj": "арақ"},
            {"no": 13, "zh": "通过", "pinyin": "tōngguò", "pos": "prep./v.", "uz": "orqali, vositasida; o'tmoq", "ru": "через, посредством; проходить", "tj": "тавассути, воситаи; гузаштан"},
            {"no": 14, "zh": "渐渐", "pinyin": "jiànjiàn", "pos": "adv.", "uz": "asta-sekin, sekin-asta", "ru": "постепенно, мало-помалу", "tj": "оҳиста-оҳиста, тадриҷан"},
            {"no": 15, "zh": "结果", "pinyin": "jiéguǒ", "pos": "n./conj.", "uz": "natija; natijada, oxir-oqibat", "ru": "результат; в результате, в итоге", "tj": "натиҷа; дар натиҷа, дар охир"},
            {"no": 16, "zh": "加油", "pinyin": "jiā yóu", "pos": "v.", "uz": "kuch qo'shmoq, rag'batlantirmoq", "ru": "давай, поддерживать, болеть (за кого-то)", "tj": "рӯҳбаланд кардан, дастгирӣ кардан"},
            {"no": 17, "zh": "比赛", "pinyin": "bǐsài", "pos": "n./v.", "uz": "musobaqa; musobaqalashmoq", "ru": "соревнование; соревноваться", "tj": "мусобиқа; мусобиқа кардан"},
            {"no": 18, "zh": "失败", "pinyin": "shībài", "pos": "v./n.", "uz": "mag'lub bo'lmoq; mag'lubiyat", "ru": "проигрывать, терпеть поражение; поражение", "tj": "мағлуб шудан; мағлубият"},
            {"no": 19, "zh": "成绩", "pinyin": "chéngjì", "pos": "n.", "uz": "natija, ball, ko'rsatkich", "ru": "результат, балл, показатель", "tj": "натиҷа, балл, нишондод"},
            {"no": 20, "zh": "相信", "pinyin": "xiāngxìn", "pos": "v.", "uz": "ishonmoq", "ru": "доверять, верить", "tj": "бовар кардан, эътимод кардан"},
        ],
        ensure_ascii=False,
    ),
    "dialogue_json": json.dumps(
        [
            {
                "block_no": 1,
                "section_label": "课文 1",
                "scene_uz": "Xiao Li va Xiao Lin tennis mashg'ulotini tashlab ketish haqida suhbatlashmoqda",
                "scene_ru": "Сяо Ли и Сяо Линь разговаривают об идее бросить теннис",
                "scene_tj": "Сяо Ли ва Сяо Лин дар бораи тарк кардани теннис сӯҳбат мекунанд",
                "dialogue": [
                    {"speaker": "小李", "zh": "这里的饼干好吃吗？你不要太随便，一分钱一分货嘛。", "pinyin": "", "uz": "Bu yerdagi pechenye mazalimi? Siz juda befarq bo'lmang, narx sifatga mos-da.", "ru": "Печенье здесь вкусное? Не будьте такими беспечными — цена соответствует качеству.", "tj": "Печенье дар ин ҷо лазиз аст? Чунон беэтино набошед — нарх ба сифат мувофиқ аст."},
                    {"speaker": "小林", "zh": "难道你不相信我的眼光？我觉得打网球得坚持，不能放弃。", "pinyin": "", "uz": "Masa, menga ishonmaysizmi? Menimcha tennis o'ynash davom ettirilishi kerak, voz kechmaslik lozim.", "ru": "Неужели вы не доверяете моему вкусу? Я считаю, что теннисом нужно продолжать заниматься, нельзя бросать.", "tj": "Магар ба завқи ман бовар надоред? Ба ақидаи ман, теннис бозиро бояд давом дод, тарк кардан намешавад."},
                    {"speaker": "小李", "zh": "你练了多长时间了？成绩怎么样？", "pinyin": "", "uz": "Qancha vaqtdan beri mashq qilyapsiz? Natijalaringiz qanday?", "ru": "Как долго вы тренируетесь? Каковы результаты?", "tj": "Шумо чӣ қадар вақт тамрин мекунед? Натиҷаҳоятон чӣ гуна аст?"},
                    {"speaker": "小林", "zh": "练了一年多了，可是成绩还不是很好，有时候我都想放弃这个主意了。", "pinyin": "", "uz": "Bir yildan ko'proq mashq qildim, lekin natijam hali yaxshi emas, ba'zan bu fikrdan voz kechmoqchiman.", "ru": "Тренируюсь уже больше года, но результаты пока не очень хорошие, иногда хочу вообще бросить эту идею.", "tj": "Зиёда аз як сол тамрин мекунам, аммо натиҷаам ҳанӯз хуб нест, баъзан мехоҳам ин фикрро тарк кунам."},
                    {"speaker": "小李", "zh": "不能放弃！通过努力，成绩渐渐会好起来的，阳光总在风雨后嘛！", "pinyin": "", "uz": "Voz kechmaslik kerak! Harakat orqali natijalar asta-sekin yaxshilanadi, quyosh yomg'irdan keyin chiqadi-da!", "ru": "Нельзя бросать! Благодаря усилиям результаты постепенно улучшатся — после дождя всегда выходит солнце!", "tj": "Тарк кардан мумкин нест! Тавассути кӯшиш натиҷаҳо оҳиста-оҳиста беҳтар мешаванд — офтоб ҳамеша пас аз борон мебарояд!"},
                ],
            },
            {
                "block_no": 2,
                "section_label": "课文 2",
                "scene_uz": "Xiao Xia va Xiao Yu o'tgan futbol musobaqasidagi taassurotlari haqida suhbatlashmoqda",
                "scene_ru": "Сяо Ся и Сяо Юй разговаривают о впечатлениях от прошлого футбольного матча",
                "scene_tj": "Сяо Ся ва Сяо Юй дар бораи таассуроти мусобиқаи гузаштаи футбол сӯҳбат мекунанд",
                "dialogue": [
                    {"speaker": "小夏", "zh": "上次比赛你们赢了吗？", "pinyin": "", "uz": "O'tgan gal musobaqada g'alaba qozonganmisiz?", "ru": "Вы выиграли прошлый матч?", "tj": "Шумо дар мусобиқаи гузашта ғалаба кардед?"},
                    {"speaker": "小雨", "zh": "没有，我们输了，但这次比赛让我们学到了很多，失败了不要紧，重要的是继续坚持。", "pinyin": "", "uz": "Yo'q, mag'lub bo'ldik, lekin bu musobaqa bizga ko'p narsa o'rgatdi, mag'lubiyat muhim emas, muhimi davom ettirishdir.", "ru": "Нет, мы проиграли, но этот матч многому нас научил — поражение не страшно, главное — продолжать.", "tj": "Не, мо мағлуб шудем, аммо ин мусобиқа моро бисёр чизҳо омӯхт — мағлубият муҳим нест, муҳим он аст, ки давом диҳем."},
                    {"speaker": "小夏", "zh": "说得对！通过这次比赛，大家渐渐明白了团队合作的重要性，结果对大家都有好处。", "pinyin": "", "uz": "To'g'ri aytdingiz! Bu musobaqa orqali hammamiz asta-sekin jamoa ishining muhimligini tushundik, natija hammamizga foydali bo'ldi.", "ru": "Верно сказано! Благодаря этому матчу все мы постепенно поняли важность командной работы — в итоге это пошло на пользу всем.", "tj": "Дуруст гуфтед! Тавассути ин мусобиқа ҳамаи мо оҳиста-оҳиста аҳамияти кори якҷоягиро фаҳмидем — дар натиҷа ба ҳама фоида расид."},
                    {"speaker": "小雨", "zh": "国际比赛真的很不轻松，每次都出很多汗，但这种感觉很好，加油吧！", "pinyin": "", "uz": "Xalqaro musobaqa haqiqatan ham oson emas, har safar ko'p ter to'kiladi, lekin bu his juda yaxshi, rag'batlantiraylik!", "ru": "Международные соревнования действительно непростые — каждый раз проливаешь много пота, но это ощущение замечательное, давайте продолжать!", "tj": "Мусобиқаҳои байналмилалӣ воқеан осон нест — ҳар бор арақи зиёд мерезад, аммо ин ҳис бисёр хуб аст, пеш равем!"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "grammar_json": json.dumps(
        [
            {
                "no": 1,
                "title_zh": "渐渐",
                "title_uz": "渐渐 (asta-sekin, sekin-asta)",
                "title_ru": "渐渐 (постепенно, мало-помалу)",
                "title_tj": "渐渐 (оҳиста-оҳиста, тадриҷан)",
                "rule_uz": "'Asta-sekin, sekin-asta' ma'nosini beradi. Biror o'zgarish yoki jarayon sekin-asta sodir bo'lishini bildiradi.",
                "rule_ru": "Означает «постепенно, мало-помалу». Указывает на то, что некоторое изменение или процесс происходит медленно.",
                "rule_tj": "Маънои «оҳиста-оҳиста, тадриҷан»-ро медиҳад. Нишон медиҳад, ки тағйирот ё раванде оҳиста рӯй медиҳад.",
                "examples": [
                    {"zh": "通过努力，成绩渐渐会好起来的。", "pinyin": "", "uz": "Harakat orqali natijalar asta-sekin yaxshilanadi.", "ru": "Благодаря усилиям результаты постепенно улучшатся.", "tj": "Тавассути кӯшиш натиҷаҳо оҳиста-оҳиста беҳтар мешаванд."},
                    {"zh": "来中国以后，他的汉语渐渐进步了。", "pinyin": "", "uz": "Xitoyga kelgandan so'ng, uning xitoy tili asta-sekin rivojlandi.", "ru": "После приезда в Китай его китайский постепенно улучшился.", "tj": "Пас аз омадан ба Чин, забони чинии ӯ оҳиста-оҳиста пешрафт кард."},
                ],
            },
            {
                "no": 2,
                "title_zh": "通过",
                "title_uz": "通过 (orqali, vositasida)",
                "title_ru": "通过 (через, посредством)",
                "title_tj": "通过 (тавассути, воситаи)",
                "rule_uz": "'Orqali, vositasida' ma'nosini beradi. Biror usul yoki vosita yordamida maqsadga erishishni bildiradi.",
                "rule_ru": "Означает «через, посредством». Указывает на достижение цели с помощью какого-либо метода или средства.",
                "rule_tj": "Маънои «тавассути, воситаи»-ро медиҳад. Нишон медиҳад, ки ба мақсад бо кӯмаки усул ё воситае мерасанд.",
                "examples": [
                    {"zh": "通过这次比赛，大家学到了很多。", "pinyin": "", "uz": "Bu musobaqa orqali hammamiz ko'p narsa o'rgandik.", "ru": "Благодаря этому матчу все мы многому научились.", "tj": "Тавассути ин мусобиқа ҳамаи мо бисёр чизҳо омӯхтем."},
                    {"zh": "通过学习，他的成绩提高了。", "pinyin": "", "uz": "O'qish orqali uning natijalari ko'tarildi.", "ru": "Благодаря учёбе его результаты улучшились.", "tj": "Тавассути таҳсил натиҷаҳои ӯ баланд шуданд."},
                ],
            },
            {
                "no": 3,
                "title_zh": "可是",
                "title_uz": "可是 (lekin, ammo)",
                "title_ru": "可是 (но, однако)",
                "title_tj": "可是 (аммо, лекин)",
                "rule_uz": "'Lekin, ammo' ma'nosini beradi. Oldingi gapga zid ma'noni bildiradi.",
                "rule_ru": "Означает «но, однако». Выражает противопоставление предыдущему высказыванию.",
                "rule_tj": "Маънои «аммо, лекин»-ро медиҳад. Муқобилро нисбат ба ҳукми қаблӣ нишон медиҳад.",
                "examples": [
                    {"zh": "我练了一年多，可是成绩还不太好。", "pinyin": "", "uz": "Men bir yildan ko'proq mashq qildim, lekin natijam hali yaxshi emas.", "ru": "Я тренировался больше года, но результаты пока не очень хорошие.", "tj": "Ман зиёда аз як сол тамрин кардам, аммо натиҷаам ҳанӯз хуб нест."},
                    {"zh": "他很努力，可是没有时间休息。", "pinyin": "", "uz": "U juda tirishqoq, lekin dam olishga vaqti yo'q.", "ru": "Он очень старается, но у него нет времени отдохнуть.", "tj": "Ӯ хеле кӯшиш мекунад, аммо вақт барои истироҳат надорад."},
                ],
            },
            {
                "no": 4,
                "title_zh": "结果",
                "title_uz": "结果 (natija; natijada)",
                "title_ru": "结果 (результат; в результате)",
                "title_tj": "结果 (натиҷа; дар натиҷа)",
                "rule_uz": "'Natija; natijada, oxir-oqibat' ma'nosida ishlatiladi. Bir holat yoki harakatning natijasini bildiradi.",
                "rule_ru": "Означает «результат; в результате, в итоге». Указывает на итог какого-либо состояния или действия.",
                "rule_tj": "Маънои «натиҷа; дар натиҷа»-ро дорад. Натиҷаи ҳолат ё амалеро нишон медиҳад.",
                "examples": [
                    {"zh": "他努力练习，结果赢了比赛。", "pinyin": "", "uz": "U qattiq mashq qildi, natijada musobaqada g'alaba qozondi.", "ru": "Он усердно тренировался, в результате выиграл соревнование.", "tj": "Ӯ сахт тамрин кард, дар натиҷа дар мусобиқа ғалаба кард."},
                    {"zh": "比赛的结果对大家都有好处。", "pinyin": "", "uz": "Musobaqaning natijasi hammamizga foydali bo'ldi.", "ru": "Результат соревнования пошёл на пользу всем.", "tj": "Натиҷаи мусобиқа ба ҳама фоида расонд."},
                ],
            },
            {
                "no": 5,
                "title_zh": "动词 + 上（趋向补语）",
                "title_uz": "Fe'l + 上 (yo'nalish to'ldiruvchisi)",
                "title_ru": "Глагол + 上 (результативное дополнение направления)",
                "title_tj": "Феъл + 上 (иловаи самтӣ)",
                "rule_uz": "Ba'zi fe'llarga 上 qo'shilganda 'boshlash, o'rganish, yaxshi ko'rib qolish' ma'nosini beradi.",
                "rule_ru": "При добавлении 上 к некоторым глаголам появляется значение «начать, пристраститься, полюбить».",
                "rule_tj": "Вақти илова шудани 上 ба баъзе феълҳо маънои «оғоз кардан, дӯст доштан» пайдо мешавад.",
                "examples": [
                    {"zh": "他慢慢爱上了打网球。", "pinyin": "", "uz": "U asta-sekin tennis o'ynashni yaxshi ko'rib qoldi.", "ru": "Он постепенно полюбил играть в теннис.", "tj": "Ӯ оҳиста-оҳиста теннис бозиро дӯст дошт."},
                    {"zh": "成绩好起来了。", "pinyin": "", "uz": "Natijalar yaxshilana boshladi.", "ru": "Результаты начали улучшаться.", "tj": "Натиҷаҳо беҳтар шудан гирифтанд."},
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
                    {"prompt_uz": "davom ettirmoq, chidamoq", "prompt_ru": "настаивать, продолжать", "prompt_tj": "давом додан, тоқат кардан", "answer": "坚持", "pinyin": "jiānchí"},
                    {"prompt_uz": "voz kechmoq", "prompt_ru": "отказываться, бросать", "prompt_tj": "даст кашидан", "answer": "放弃", "pinyin": "fàngqì"},
                    {"prompt_uz": "g'alaba qozonmoq", "prompt_ru": "выигрывать, побеждать", "prompt_tj": "ғалаба кардан", "answer": "赢", "pinyin": "yíng"},
                    {"prompt_uz": "natija", "prompt_ru": "результат", "prompt_tj": "натиҷа", "answer": "结果", "pinyin": "jiéguǒ"},
                    {"prompt_uz": "xalqaro", "prompt_ru": "международный", "prompt_tj": "байналмилалӣ", "answer": "国际", "pinyin": "guójì"},
                ],
            },
            {
                "no": 2,
                "type": "translate_to_uzbek",
                "instruction_uz": "Quyidagi so'zlarning o'zbekchasini yozing:",
                "instruction_ru": "Напишите узбекский перевод следующих слов:",
                "instruction_tj": "Тарҷумаи ӯзбекии калимаҳои зеринро нависед:",
                "items": [
                    {"prompt_uz": "渐渐", "prompt_ru": "渐渐", "prompt_tj": "渐渐", "answer": "asta-sekin, sekin-asta", "pinyin": "jiànjiàn"},
                    {"prompt_uz": "通过", "prompt_ru": "通过", "prompt_tj": "通过", "answer": "orqali, vositasida", "pinyin": "tōngguò"},
                    {"prompt_uz": "难道", "prompt_ru": "难道", "prompt_tj": "难道", "answer": "masa, axir (ritorik savol)", "pinyin": "nándào"},
                    {"prompt_uz": "相信", "prompt_ru": "相信", "prompt_tj": "相信", "answer": "ishonmoq", "pinyin": "xiāngxìn"},
                ],
            },
            {
                "no": 3,
                "type": "fill_blank",
                "instruction_uz": "Mos so'zni tanlang (渐渐、通过、可是、结果、坚持):",
                "instruction_ru": "Выберите подходящее слово (渐渐、通过、可是、结果、坚持):",
                "instruction_tj": "Калимаи мувофиқро интихоб кунед (渐渐、通过、可是、结果、坚持):",
                "items": [
                    {"prompt_uz": "他练了很久，______还是没赢。", "prompt_ru": "他练了很久，______还是没赢。", "prompt_tj": "他练了很久，______还是没赢。", "answer": "可是", "pinyin": "kěshì"},
                    {"prompt_uz": "______努力学习，他______进步了很多。", "prompt_ru": "______努力学习，他______进步了很多。", "prompt_tj": "______努力学习，他______进步了很多。", "answer": "通过 / 渐渐", "pinyin": "tōngguò / jiànjiàn"},
                    {"prompt_uz": "不管多难，都要______下去。", "prompt_ru": "不管多难，都要______下去。", "prompt_tj": "不管多难，都要______下去。", "answer": "坚持", "pinyin": "jiānchí"},
                ],
            },
        ],
        ensure_ascii=False,
    ),
    "answers_json": json.dumps(
        [
            {"no": 1, "answers": ["坚持", "放弃", "赢", "结果", "国际"]},
            {"no": 2, "answers": ["asta-sekin, sekin-asta", "orqali, vositasida", "masa, axir (ritorik savol)", "ishonmoq"]},
            {"no": 3, "answers": ["可是", "通过 / 渐渐", "坚持"]},
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
                "words": ["坚持", "通过", "渐渐", "结果"],
                "example": "通过每天坚持练习，他的网球水平渐渐提高了，结果赢得了比赛。",
            },
            {
                "no": 2,
                "instruction_uz": "'通过...就...' va '渐渐' qoliplaridan foydalanib har biridan 2 ta gap tuzing.",
                "instruction_ru": "Напишите по 2 предложения с конструкциями '通过...就...' и '渐渐'.",
                "instruction_tj": "Бо қолабҳои '通过...就...' ва '渐渐' аз ҳар кадом 2 ҷумла нависед.",
                "topic_uz": "sport, muvaffaqiyat va qiyinchiliklar mavzusida",
                "topic_ru": "на тему спорта, успеха и трудностей",
                "topic_tj": "дар мавзӯи варзиш, муваффақият ва душвориҳо",
            },
            {
                "no": 3,
                "instruction_uz": "5-6 gapdan iborat kichik matn yozing:",
                "instruction_ru": "Напишите небольшой текст из 5-6 предложений:",
                "instruction_tj": "Матни хурди 5-6 ҷумлагӣ нависед:",
                "topic_uz": "Siz qachondir qiyinchilikdan o'tib muvaffaqiyat qozonganmisiz? 你有过坚持并取得成功的经历吗？",
                "topic_ru": "Был ли у вас опыт, когда вы преодолели трудности и добились успеха? 你有过坚持并取得成功的经历吗？",
                "topic_tj": "Оё шумо таҷрибаи аз душворӣ гузаштан ва муваффақ шудан доштед? 你有过坚持并取得成功的经历吗？",
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
