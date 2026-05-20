import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 16,
    "lesson_code": "HSK3-L16",
    "title": json.dumps({"zh": "我现在累得下了班就想睡觉", "uz": "Hozir shu qadar charchaganmanki, ishdan chiqqanimdan so'ng uxlashni xohlayman", "ru": "Сейчас я так устал, что после работы сразу хочу спать", "tj": "Ҳоло ман ончунон хастаам, ки баъд аз кор фавран хоб кардан мехоҳам"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "'Agar…u holda…' shartli gap, murakkab holat to'ldiruvchisi va bir bo'g'inli sifat takrori o'rganish", "ru": "Условные предложения 'если…то…', сложное дополнение состояния и удвоение односложных прилагательных", "tj": "Ҷумлаҳои шартии 'агар…пас…', пуркунандаи мураккаби ҳол ва такрори сифатҳои яктарафа"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda '如果…就…' shartli iborasi, 'F + 得 + murakkab holat' va bir bo'g'inli sifatlarning takrorini (好好 → yaxshilab) o'rganamiz.", "ru": "В этом уроке мы изучим условное выражение '如果…就…', 'Гл + 得 + сложное состояние' и удвоение односложных прилагательных (好好 → хорошенько).", "tj": "Дар ин дарс мо ибораи шартии '如果…就…', 'Ф + 得 + ҳоли мураккаб' ва такрори сифатҳои яктаяко (好好 → хуб-хуб)-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "下班", "pinyin": "xià bān", "pos": "v", "uz": "ishdan chiqmoq", "ru": "заканчивать работу", "tj": "аз кор баромадан"},
        {"no": 2, "zh": "累", "pinyin": "lèi", "pos": "adj", "uz": "charchagan", "ru": "устал, утомлён", "tj": "хаста"},
        {"no": 3, "zh": "如果", "pinyin": "rúguǒ", "pos": "conj", "uz": "agar", "ru": "если", "tj": "агар"},
        {"no": 4, "zh": "压力", "pinyin": "yālì", "pos": "n", "uz": "bosim, stress", "ru": "давление, стресс", "tj": "фишор, стресс"},
        {"no": 5, "zh": "放松", "pinyin": "fàngsōng", "pos": "v", "uz": "dam olmoq, bo'shashmoq", "ru": "расслабиться, отдохнуть", "tj": "истироҳат кардан, шул шудан"},
        {"no": 6, "zh": "加班", "pinyin": "jiābān", "pos": "v", "uz": "qo'shimcha vaqt ishlash, ortiqcha ishlash", "ru": "работать сверхурочно", "tj": "изофа кор кардан"},
        {"no": 7, "zh": "好好", "pinyin": "hǎohǎo", "pos": "adv", "uz": "yaxshilab, to'liq", "ru": "хорошенько, как следует", "tj": "хуб-хуб, сариҳол"},
        {"no": 8, "zh": "慢慢", "pinyin": "mànmàn", "pos": "adv", "uz": "sekin-sekin, asta", "ru": "медленно, постепенно", "tj": "оҳиста-оҳиста, тадриҷан"},
        {"no": 9, "zh": "早早", "pinyin": "zǎozǎo", "pos": "adv", "uz": "juda erta, ertaroq", "ru": "пораньше, заблаговременно", "tj": "барвақт-барвақт, аввалтар"},
        {"no": 10, "zh": "睡觉", "pinyin": "shuìjiào", "pos": "v", "uz": "uxlamoq", "ru": "спать", "tj": "хобидан"},
        {"no": 11, "zh": "坚持", "pinyin": "jiānchí", "pos": "v", "uz": "davom ettirmoq, qat'iy turmoq", "ru": "упорствовать, продолжать", "tj": "идома додан, устувор мондан"},
        {"no": 12, "zh": "减少", "pinyin": "jiǎnshǎo", "pos": "v", "uz": "kamaytirmoq", "ru": "уменьшать, сокращать", "tj": "кам кардан"},
        {"no": 13, "zh": "注意", "pinyin": "zhùyì", "pos": "v", "uz": "e'tibor bermoq, ehtiyot bo'lmoq", "ru": "обращать внимание, быть осторожным", "tj": "диққат додан, эҳтиёт кардан"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Ish zo'riqishi haqida", "ru": "О стрессе на работе", "tj": "Дар бораи стресси корӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "你看起来很累，怎么了？", "pinyin": "Nǐ kàn qǐlái hěn lèi, zěnme le?", "uz": "Siz juda charchagan ko'rinasiz, nima bo'ldi?", "ru": "Ты выглядишь очень уставшим, что случилось?", "tj": "Шумо хеле хаста менамоед, чӣ шуд?"},
                {"speaker": "B", "zh": "我现在累得下了班就想睡觉！", "pinyin": "Wǒ xiànzài lèi de xià le bān jiù xiǎng shuìjiào!", "uz": "Hozir shu qadar charchaganmanki, ishdan chiqqanimdan so'ng darhol uxlashni xohlayman!", "ru": "Сейчас я так устал, что после работы сразу хочу спать!", "tj": "Ҳоло ман ончунон хастаам, ки баъд аз кор фавран хоб кардан мехоҳам!"},
                {"speaker": "A", "zh": "如果每天都这么累，你要好好休息！", "pinyin": "Rúguǒ měitiān dōu zhème lèi, nǐ yào hǎohǎo xiūxi!", "uz": "Agar har kuni bu qadar charchangan bo'lsangiz, yaxshilab dam olishingiz kerak!", "ru": "Если каждый день так устаёшь, тебе нужно хорошенько отдохнуть!", "tj": "Агар ҳар рӯз ин қадар хаста шавед, бояд хуб-хуб истироҳат кунед!"},
                {"speaker": "B", "zh": "是，如果压力不减少，我就受不了了！", "pinyin": "Shì, rúguǒ yālì bù jiǎnshǎo, wǒ jiù shòu bù liǎo le!", "uz": "Ha, agar bosim kamaymasа, men bardosh bera olmayman!", "ru": "Да, если стресс не уменьшится, я не выдержу!", "tj": "Ҳа, агар фишор кам нашавад, ман тоқат карда наметавонам!"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Ortiqcha ish haqida", "ru": "О сверхурочной работе", "tj": "Дар бораи изофа кор"},
            "dialogue": [
                {"speaker": "A", "zh": "你最近经常加班吗？", "pinyin": "Nǐ zuìjìn jīngcháng jiābān ma?", "uz": "Yaqinda tez-tez ortiqcha ishlamoqdasizmi?", "ru": "Ты в последнее время часто работаешь сверхурочно?", "tj": "Охирон шумо зиёд изофа кор мекунед?"},
                {"speaker": "B", "zh": "是的，累得连饭都吃不下去了！", "pinyin": "Shì de, lèi de lián fàn dōu chī bù xiàqù le!", "uz": "Ha, shu qadar charchaganmanki hatto ovqat ham yutolmayapman!", "ru": "Да, так устал, что даже есть не могу!", "tj": "Ҳа, ончунон хастаам, ки ҳатто хӯрок хӯрда наметавонам!"},
                {"speaker": "A", "zh": "如果你慢慢减少加班，身体会好很多。", "pinyin": "Rúguǒ nǐ mànmàn jiǎnshǎo jiābān, shēntǐ huì hǎo hěn duō.", "uz": "Agar sekin-sekin ortiqcha ishni kamaytirsangiz, salomatligingiz ancha yaxshilanadi.", "ru": "Если постепенно сокращать сверхурочную работу, здоровье намного улучшится.", "tj": "Агар оҳиста-оҳиста изофа корро кам кунед, саломатиатон хеле беҳтар мешавад."},
                {"speaker": "B", "zh": "你说得对，我要注意健康！", "pinyin": "Nǐ shuō de duì, wǒ yào zhùyì jiànkāng!", "uz": "Siz to'g'ri aytdingiz, salomatligimga e'tibor bermoqchiman!", "ru": "Ты прав, буду следить за здоровьем!", "tj": "Шумо дуруст гуфтед, ман ба саломатиам диққат медиҳам!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Dam olish maslahatlar", "ru": "Советы по отдыху", "tj": "Тавсияҳои истироҳат"},
            "dialogue": [
                {"speaker": "A", "zh": "如果你好好放松，压力就会减少。", "pinyin": "Rúguǒ nǐ hǎohǎo fàngsōng, yālì jiù huì jiǎnshǎo.", "uz": "Agar yaxshilab dam olsangiz, bosim kamayadi.", "ru": "Если хорошенько расслабиться, стресс уменьшится.", "tj": "Агар хуб-хуб истироҳат кунед, фишор кам мешавад."},
                {"speaker": "B", "zh": "我打算早早回家，好好睡一觉。", "pinyin": "Wǒ dǎsuàn zǎozǎo huí jiā, hǎohǎo shuì yī jiào.", "uz": "Men ertaroq uyga qaytib, yaxshilab uxlamoqchi.", "ru": "Я собираюсь пораньше вернуться домой и хорошенько поспать.", "tj": "Ман барвақт ба хона баргашта, хуб-хуб хобидан мехоҳам."},
                {"speaker": "A", "zh": "对，如果你坚持早睡早起，精神会好很多！", "pinyin": "Duì, rúguǒ nǐ jiānchí zǎo shuì zǎo qǐ, jīngshén huì hǎo hěn duō!", "uz": "Ha, agar erta uxlab erta turish odatini saqlab qolsangiz, ruhingiz ancha yaxshi bo'ladi!", "ru": "Да, если привыкнуть рано ложиться и рано вставать, самочувствие намного улучшится!", "tj": "Ҳа, агар одати барвақт хобидан ва барвақт хестанро нигоҳ доред, ҳисси бошед хеле беҳтар мешавад!"},
                {"speaker": "B", "zh": "好，我慢慢改变生活习惯吧！", "pinyin": "Hǎo, wǒ mànmàn gǎibiàn shēnghuó xíguàn ba!", "uz": "Yaxshi, sekin-sekin hayot odatlarimi o'zgartiraman!", "ru": "Хорошо, буду постепенно менять привычки жизни!", "tj": "Хуб, ман оҳиста-оҳиста одатҳои ҳаётиамро тағйир медиҳам!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Shartli rejalar haqida", "ru": "О планах при условии", "tj": "Дар бораи нақшаҳои шартӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "如果周末有时间，你想去哪儿放松？", "pinyin": "Rúguǒ zhōumò yǒu shíjiān, nǐ xiǎng qù nǎr fàngsōng?", "uz": "Agar dam olish kunlari vaqt bo'lsa, qayerda dam olmoqchi?", "ru": "Если на выходных будет время, куда хочешь пойти отдохнуть?", "tj": "Агар охири ҳафта вақт бошад, ба куҷо рафтан мехоҳед?"},
                {"speaker": "B", "zh": "如果天气好，就好好在公园走走！", "pinyin": "Rúguǒ tiānqì hǎo, jiù hǎohǎo zài gōngyuán zǒuzou!", "uz": "Agar havo yaxshi bo'lsa, parkda yaxshilab yurib kelaman!", "ru": "Если погода будет хорошей, хорошенько погуляю в парке!", "tj": "Агар ҳаво хуб бошад, дар боғ хуб-хуб гаштам мекунам!"},
                {"speaker": "A", "zh": "对，慢慢走，好好看看风景！", "pinyin": "Duì, mànmàn zǒu, hǎohǎo kànkan fēngjǐng!", "uz": "Ha, sekin-sekin yuring, manzarani yaxshilab ko'ring!", "ru": "Да, иди медленно, хорошенько посмотри на пейзаж!", "tj": "Ҳа, оҳиста-оҳиста биравед, хуб-хуб манзараро бубинед!"},
                {"speaker": "B", "zh": "好主意！如果你有空，一起去！", "pinyin": "Hǎo zhǔyì! Rúguǒ nǐ yǒu kòng, yīqǐ qù!", "uz": "Zo'r fikr! Agar vaqtingiz bo'lsa, birga boramiz!", "ru": "Отличная идея! Если у тебя будет время, пойдём вместе!", "tj": "Ғояи олӣ! Агар вақт дошта бошед, якҷо меравем!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "如果……就……（条件句）",
            "title_uz": "Agar……u holda/bo'lsa……（shartli gap）",
            "title_ru": "Если……то……（условное предложение）",
            "title_tj": "Агар……пас……（ҷумлаи шартӣ）",
            "rule_uz": "'如果…就…' tuzilmasi agar-u holda shartli gaplarni ifodalaydi. '如果' = agar, '就' = u holda/shunda. '如果' ko'pincha gapning avvalida, '就' esa natijaning avvalida keladi.",
            "rule_ru": "Конструкция '如果…就…' выражает условные предложения 'если-то'. '如果' = если, '就' = то. '如果' обычно стоит в начале предложения, '就' — перед следствием.",
            "rule_tj": "Сохтори '如果…就…' ҷумлаҳои шартии 'агар-пас'-ро ифода мекунад. '如果' = агар, '就' = пас. '如果' одатан аввали ҷумла, '就' — пеш аз натиҷа меояд.",
            "examples": [
                {"zh": "如果你每天锻炼，就会很健康！", "pinyin": "Rúguǒ nǐ měitiān duànliàn, jiù huì hěn jiànkāng!", "uz": "Agar har kuni mashq qilsangiz, juda sog'lom bo'lasiz!", "ru": "Если будешь заниматься каждый день, будешь очень здоровым!", "tj": "Агар ҳар рӯз варзиш кунед, хеле солим мешавед!"},
                {"zh": "如果天气好，我就去公园。", "pinyin": "Rúguǒ tiānqì hǎo, wǒ jiù qù gōngyuán.", "uz": "Agar havo yaxshi bo'lsa, parkka boraman.", "ru": "Если погода будет хорошей, пойду в парк.", "tj": "Агар ҳаво хуб бошад, ба боғ меравам."}
            ]
        },
        {
            "no": 2,
            "title_zh": "复杂状态补语：累得……（极端状态）",
            "title_uz": "Murakkab holat to'ldiruvchisi: charchashdan……",
            "title_ru": "Сложное дополнение состояния: устал настолько, что……",
            "title_tj": "Пуркунандаи мураккаби ҳол: хаста аз……",
            "rule_uz": "'F+得+gap/murakkab ifoda' tuzilmasi harakatning natijasidagi holatni ifodalaydi. Oddiy holatdan farqli ravishda, bu yerda bir butun gap kelishi mumkin. Masalan: 累得睡不着 = charchashdan uxlolmayman.",
            "rule_ru": "Конструкция 'Гл+得+предложение/сложное выражение' описывает состояние в результате действия. В отличие от простого дополнения, здесь может быть целое предложение. Например: 累得睡不着 = так устал, что не могу спать.",
            "rule_tj": "Сохтори 'Ф+得+ҷумла/ибораи мураккаб' ҳолати натиҷаи амалро тасвир мекунад. Баръакси пуркунандаи оддӣ, ин ҷо ҷумлаи пурра омада метавонад. Масалан: 累得睡不着 = ончунон хастаам, ки хобам намебарад.",
            "examples": [
                {"zh": "我累得下了班就想睡觉。", "pinyin": "Wǒ lèi de xià le bān jiù xiǎng shuìjiào.", "uz": "Shu qadar charchaganmanki, ishdan chiqqanimdan so'ng uxlashni xohlayman.", "ru": "Я так устал, что после работы сразу хочу спать.", "tj": "Ман ончунон хастаам, ки баъд аз кор фавран хоб кардан мехоҳам."},
                {"zh": "他高兴得跳起来了！", "pinyin": "Tā gāoxìng de tiào qǐlái le!", "uz": "U shu qadar xurshandki, sakrab ketdi!", "ru": "Он так обрадовался, что подпрыгнул!", "tj": "Вай ончунон хурсанд шуд, ки ҷаҳид!"}
            ]
        },
        {
            "no": 3,
            "title_zh": "单音节形容词重叠：AA式（好好、慢慢……）",
            "title_uz": "Bir bo'g'inli sifat takrori: AA shakli (yaxshi-yaxshi, sekin-sekin...)",
            "title_ru": "Удвоение односложных прилагательных: форма AA (хорошенько, медленно-медленно...)",
            "title_tj": "Такрори сифатҳои яктаяко: шакли AA (хуб-хуб, оҳиста-оҳиста...)",
            "rule_uz": "Bir bo'g'inli sifat takrorlanib ravish sifatida ishlatilsa, kuchaytiruvchi ma'no beradi: 好好 = yaxshilab, 慢慢 = sekin-sekin, 早早 = ertaroq, 快快 = tezroq. Bu shakl ko'pincha fe'ldan oldin keladi.",
            "rule_ru": "Если односложное прилагательное удваивается и используется как наречие, оно приобретает усилительное значение: 好好 = хорошенько, 慢慢 = медленно-медленно, 早早 = пораньше, 快快 = побыстрее. Эта форма обычно стоит перед глаголом.",
            "rule_tj": "Агар сифати яктаяко такрор шуда ба сифати зарф истифода шавад, маънои тақвияткунанда пайдо мекунад: 好好 = хуб-хуб, 慢慢 = оҳиста-оҳиста, 早早 = барвақт-барвақт, 快快 = зуд-зуд. Ин шакл одатан пеш аз феъл меояд.",
            "examples": [
                {"zh": "你要好好休息！", "pinyin": "Nǐ yào hǎohǎo xiūxi!", "uz": "Yaxshilab dam oling!", "ru": "Вам нужно хорошенько отдохнуть!", "tj": "Шумо бояд хуб-хуб истироҳат кунед!"},
                {"zh": "慢慢走，别着急！", "pinyin": "Mànmàn zǒu, bié zháojí!", "uz": "Sekin-sekin yuring, shoshilmang!", "ru": "Идите медленно, не торопитесь!", "tj": "Оҳиста-оҳиста равед, шитоб накунед!"}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Agar har kuni mashq qilsangiz, juda sog'lom bo'lasiz!", "ru": "Если будешь заниматься каждый день, будешь очень здоровым!", "tj": "Агар ҳар рӯз варзиш кунед, хеле солим мешавед!"},
                {"no": 2, "uz": "Yaxshilab dam oling!", "ru": "Хорошенько отдохните!", "tj": "Хуб-хуб истироҳат кунед!"},
                {"no": 3, "uz": "Sekin-sekin yuring, shoshilmang!", "ru": "Идите медленно, не торопитесь!", "tj": "Оҳиста-оҳиста равед, шитоб накунед!"},
                {"no": 4, "uz": "U shu qadar xurshandki, sakrab ketdi!", "ru": "Он так обрадовался, что подпрыгнул!", "tj": "Вай ончунон хурсанд шуд, ки ҷаҳид!"},
                {"no": 5, "uz": "Agar havo yaxshi bo'lsa, parkka boraman.", "ru": "Если погода будет хорошей, пойду в парк.", "tj": "Агар ҳаво хуб бошад, ба боғ меравам."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "___你每天锻炼，___会很健康！", "sentence_uz": "___ har kuni mashq qilsangiz, juda sog'lom ___!", "sentence_ru": "___ будешь заниматься каждый день, ___ будешь здоровым!", "sentence_tj": "___ ҳар рӯз варзиш кунед, ___ хеле солим мешавед!", "hint": "如果…就"},
                {"no": 2, "sentence_zh": "我累___下了班就想睡觉。", "sentence_uz": "Men charchashdan ishdan chiqqanimdan so'ng uxlashni ___.", "sentence_ru": "Я устал ___ что после работы сразу хочу спать.", "sentence_tj": "Ман ончунон хастаам, ___ баъд аз кор фавран хоб кардан мехоҳам.", "hint": "得"},
                {"no": 3, "sentence_zh": "你要___休息！", "sentence_uz": "Siz yaxshi___ dam olishingiz kerak!", "sentence_ru": "Вам нужно ___ отдохнуть!", "sentence_tj": "Шумо бояд ___ истироҳат кунед!", "hint": "好好"},
                {"no": 4, "sentence_zh": "___走，别着急！", "sentence_uz": "Sekin-___ yuring, shoshilmang!", "sentence_ru": "___ идите, не торопитесь!", "sentence_tj": "___ равед, шитоб накунед!", "hint": "慢慢"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "如果压力不减少，我就受不了了！", "pinyin": "Rúguǒ yālì bù jiǎnshǎo, wǒ jiù shòu bù liǎo le!"},
                {"no": 2, "zh": "如果你坚持早睡早起，精神会好很多！", "pinyin": "Rúguǒ nǐ jiānchí zǎo shuì zǎo qǐ, jīngshén huì hǎo hěn duō!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "如果你每天锻炼，就会很健康！"},
                {"no": 2, "zh": "你要好好休息！"},
                {"no": 3, "zh": "慢慢走，别着急！"},
                {"no": 4, "zh": "他高兴得跳起来了！"},
                {"no": 5, "zh": "如果天气好，我就去公园。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "如果…就"},
                {"no": 2, "answer": "得"},
                {"no": 3, "answer": "好好"},
                {"no": 4, "answer": "慢慢"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Agar bosim kamaymasа, men bardosh bera olmayman!", "ru": "Если стресс не уменьшится, я не выдержу!", "tj": "Агар фишор кам нашавад, ман тоқат карда наметавонам!"},
                {"no": 2, "uz": "Agar erta uxlab erta turish odatini saqlab qolsangiz, ruhingiz ancha yaxshi bo'ladi!", "ru": "Если привыкнуть рано ложиться и рано вставать, самочувствие намного улучшится!", "tj": "Агар одати барвақт хобидан ва барвақт хестанро нигоҳ доред, ҳисси бошед хеле беҳтар мешавад!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'如果…就…' tuzilmasini ishlatib, salomatlik, ish yoki o'qish haqida 4 ta shartli gap tuzing.", "ru": "Составьте 4 условных предложения о здоровье, работе или учёбе, используя '如果…就…'.", "tj": "4 ҷумлаи шартӣ дар бораи саломатӣ, кор ё таҳсил бо '如果…就…' тартиб диҳед."},
        {"task_no": 2, "uz": "Bir bo'g'inli sifat takroridan foydalanib (好好、慢慢、早早 kabi), 3 ta maslahat jumla yozing.", "ru": "Напишите 3 предложения с советами, используя удвоение прилагательных (好好、慢慢、早早 и т.д.).", "tj": "3 ҷумлаи тавсиявӣ бо истифодаи такрори сифатҳо (好好、慢慢、早早 ва ғайра) нависед."}
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
