import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 11,
    "lesson_code": "HSK3-L11",
    "title": json.dumps({"zh": "别忘了把空调关了", "uz": "Konditsionerni o'chirishni unutma", "ru": "Не забудь выключить кондиционер", "tj": "Фаромӯш накун ки кондитсионерро хомӯш кунӣ"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "把-konstruktsiyasi (1-qism), taxminiy sonlar '左右' va fe'l+了+ob'ekt+了 o'rganish", "ru": "Изучить конструкцию 把 (часть 1), приблизительные числа '左右' и Гл+了+объект+了", "tj": "Омӯхтани сохтори 把 (қисми 1), рақамҳои тахминии '左右' ва Ф+了+объект+了"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda '把'-konstruktsiyasining asosiy qo'llanishini, '左右' taxminiy ko'rsatkichini va 'F+了+OB+了' iborasini o'rganamiz.", "ru": "В этом уроке мы изучим основное использование конструкции '把', показатель приблизительности '左右' и выражение 'Гл+了+объект+了'.", "tj": "Дар ин дарс мо истифодаи асосии сохтори '把', нишондиҳандаи тахминии '左右' ва ибораи 'Ф+了+объект+了'-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "空调", "pinyin": "kōngtiáo", "pos": "n", "uz": "konditsioner", "ru": "кондиционер", "tj": "кондитсионер"},
        {"no": 2, "zh": "关", "pinyin": "guān", "pos": "v", "uz": "o'chirmoq, yopmoq", "ru": "выключать, закрывать", "tj": "хомӯш кардан, бастан"},
        {"no": 3, "zh": "开", "pinyin": "kāi", "pos": "v", "uz": "yoqmoq, ochmoq", "ru": "включать, открывать", "tj": "даровардан, кушодан"},
        {"no": 4, "zh": "忘", "pinyin": "wàng", "pos": "v", "uz": "unutmoq", "ru": "забывать", "tj": "фаромӯш кардан"},
        {"no": 5, "zh": "左右", "pinyin": "zuǒyòu", "pos": "n", "uz": "taxminan, atrofida", "ru": "приблизительно, около", "tj": "тахминан, ҳудуди"},
        {"no": 6, "zh": "窗户", "pinyin": "chuānghù", "pos": "n", "uz": "deraza", "ru": "окно", "tj": "тиреза"},
        {"no": 7, "zh": "灯", "pinyin": "dēng", "pos": "n", "uz": "chiroq", "ru": "лампа, свет", "tj": "чароғ"},
        {"no": 8, "zh": "电脑", "pinyin": "diànnǎo", "pos": "n", "uz": "kompyuter", "ru": "компьютер", "tj": "компютер"},
        {"no": 9, "zh": "东西", "pinyin": "dōngxi", "pos": "n", "uz": "narsa, buyum", "ru": "вещь, предмет", "tj": "чиз, мол"},
        {"no": 10, "zh": "收拾", "pinyin": "shōushi", "pos": "v", "uz": "tartibga solmoq, yig'moq", "ru": "убирать, приводить в порядок", "tj": "тартиб додан, ҷамъ кардан"},
        {"no": 11, "zh": "房间", "pinyin": "fángjiān", "pos": "n", "uz": "xona", "ru": "комната", "tj": "хона"},
        {"no": 12, "zh": "锁", "pinyin": "suǒ", "pos": "v/n", "uz": "qulflamoq; qulf", "ru": "запирать; замок", "tj": "қулф задан; қулф"},
        {"no": 13, "zh": "门", "pinyin": "mén", "pos": "n", "uz": "eshik", "ru": "дверь", "tj": "дар"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Uydan chiqishdan oldin", "ru": "Перед выходом из дома", "tj": "Пеш аз баромадан аз хона"},
            "dialogue": [
                {"speaker": "A", "zh": "你走了吗？别忘了把空调关了！", "pinyin": "Nǐ zǒu le ma? Bié wàng le bǎ kōngtiáo guān le!", "uz": "Ketayapsizmi? Konditsionerni o'chirishni unutma!", "ru": "Ты уходишь? Не забудь выключить кондиционер!", "tj": "Шумо меравед? Фаромӯш накунед ки кондитсионерро хомӯш кунед!"},
                {"speaker": "B", "zh": "已经关了，你放心吧。", "pinyin": "Yǐjīng guān le, nǐ fàngxīn ba.", "uz": "Allaqachon o'chirdim, xotirjam bo'ling.", "ru": "Уже выключил, не беспокойся.", "tj": "Аллакай хомӯш кардам, хотирҷамъ бошед."},
                {"speaker": "A", "zh": "窗户呢？把窗户也关上了吗？", "pinyin": "Chuānghù ne? Bǎ chuānghù yě guānshang le ma?", "uz": "Derazachi? Derazani ham yopdingizmi?", "ru": "А окно? Окно тоже закрыл?", "tj": "Тирезаро чӣ? Тирезаро ҳам бастед?"},
                {"speaker": "B", "zh": "哎，忘了！我去把它关上。", "pinyin": "Āi, wàng le! Wǒ qù bǎ tā guānshang.", "uz": "Voy, unutibman! Boriy uni yopaman.", "ru": "Ой, забыл! Пойду закрою.", "tj": "Воҳ, фаромӯш кардам! Меравам онро мебандам."}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Xonani tartibga solish", "ru": "Уборка комнаты", "tj": "Тартиб додани хона"},
            "dialogue": [
                {"speaker": "A", "zh": "你把房间收拾一下吧，太乱了！", "pinyin": "Nǐ bǎ fángjiān shōushi yīxià ba, tài luàn le!", "uz": "Xonangni bir tartibga sol, juda tarqoq!", "ru": "Убери комнату, слишком беспорядок!", "tj": "Хонаатро тартиб деҳ, хеле барҳам хӯрда!"},
                {"speaker": "B", "zh": "好，我大概需要一个小时左右。", "pinyin": "Hǎo, wǒ dàgài xūyào yī gè xiǎoshí zuǒyòu.", "uz": "Yaxshi, menga taxminan bir soat kerak bo'ladi.", "ru": "Хорошо, мне нужно примерно около часа.", "tj": "Хуб, ба ман тахминан як соат лозим мешавад."},
                {"speaker": "A", "zh": "先把东西都放到原来的地方。", "pinyin": "Xiān bǎ dōngxi dōu fàng dào yuánlái de dìfāng.", "uz": "Avval hamma narsani o'z joyiga qo'y.", "ru": "Сначала положи все вещи на место.", "tj": "Аввал ҳама чизро ба ҷои аслиаш монд."},
                {"speaker": "B", "zh": "明白了，我把灯也打开，看得清楚些。", "pinyin": "Míngbái le, wǒ bǎ dēng yě dǎkāi, kàn de qīngchu xiē.", "uz": "Tushundim, chiroqni ham yoqaman, aniqroq ko'rinsin.", "ru": "Понял, включу и свет, чтобы было лучше видно.", "tj": "Фаҳмидам, чароғро ҳам меафрӯзам, равшантар шавад."}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Kompyuterni o'chirish", "ru": "Выключение компьютера", "tj": "Хомӯш кардани компютер"},
            "dialogue": [
                {"speaker": "A", "zh": "你用完电脑了吗？把电脑关了吧。", "pinyin": "Nǐ yòng wán diànnǎo le ma? Bǎ diànnǎo guān le ba.", "uz": "Kompyuterni ishlatib bo'ldingizmi? Kompyuterni o'chiring.", "ru": "Ты закончил с компьютером? Выключи его.", "tj": "Шумо компютерро тамом истифода бурдед? Компютерро хомӯш кунед."},
                {"speaker": "B", "zh": "还没，还需要二十分钟左右。", "pinyin": "Hái méi, hái xūyào èrshí fēnzhōng zuǒyòu.", "uz": "Hali yo'q, yana taxminan yigirma daqiqa kerak.", "ru": "Ещё нет, нужно ещё около двадцати минут.", "tj": "Ҳанӯз не, боз тахминан бист дақиқа лозим аст."},
                {"speaker": "A", "zh": "好，用完了记得把文件保存了再关。", "pinyin": "Hǎo, yòng wán le jìde bǎ wénjiàn bǎocún le zài guān.", "uz": "Yaxshi, tugatgach faylni saqlashni eslab, keyin o'chiring.", "ru": "Ладно, когда закончишь, не забудь сохранить файл перед закрытием.", "tj": "Хуб, тамом шуд, ёд кун ки фоилро сабт кун, баъд хомӯш кун."},
                {"speaker": "B", "zh": "放心！我不会忘的。", "pinyin": "Fàngxīn! Wǒ bú huì wàng de.", "uz": "Xotirjam bo'ling! Men unutmayman.", "ru": "Не беспокойтесь! Я не забуду.", "tj": "Хотирҷамъ бошед! Ман фаромӯш намекунам."}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Eshikni qulflash", "ru": "Запирание двери", "tj": "Қулф задани дар"},
            "dialogue": [
                {"speaker": "A", "zh": "出门的时候把门锁上了吗？", "pinyin": "Chū mén de shíhou bǎ mén suǒshang le ma?", "uz": "Chiqayotganda eshikni qulfladingizmi?", "ru": "Когда выходил, дверь запер?", "tj": "Вақти баромадан дарро қулф задед?"},
                {"speaker": "B", "zh": "锁了！我把门锁了，钥匙在包里。", "pinyin": "Suǒ le! Wǒ bǎ mén suǒ le, yàoshi zài bāo lǐ.", "uz": "Qulflash! Men eshikni qulflash, kalit sumkada.", "ru": "Запер! Я запер дверь, ключ в сумке.", "tj": "Қулф задам! Ман дарро қулф задам, калид дар сумка."},
                {"speaker": "A", "zh": "好，那我们走吧，大约三十分钟左右到。", "pinyin": "Hǎo, nà wǒmen zǒu ba, dàyuē sānshí fēnzhōng zuǒyòu dào.", "uz": "Yaxshi, unda ketaylik, taxminan o'ttiz daqiqada yetamiz.", "ru": "Хорошо, тогда пойдём, примерно за тридцать минут доберёмся.", "tj": "Хуб, пас биравем, тахминан сӣ дақиқа мерасем."},
                {"speaker": "B", "zh": "好的，出发！", "pinyin": "Hǎo de, chūfā!", "uz": "Yaxshi, ketdik!", "ru": "Хорошо, поехали!", "tj": "Хуб, рафтем!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "把字句①：把 + O + V + 结果/趋向补语",
            "title_uz": "把-konstruktsiyasi①: 把 + OB + F + natija/yo'nalish to'ldiruvchisi",
            "title_ru": "Конструкция 把①: 把 + объект + Гл + результатное/направленное дополнение",
            "title_tj": "Сохтори 把①: 把 + объект + Ф + пуркунандаи натиҷа/самт",
            "rule_uz": "'把'-konstruktsiyasi ob'ektga nisbatan harakatning natijasini ta'kidlaydi. Tuzilma: Subekt + 把 + ob'ekt + fe'l + natija. Fe'l yolg'iz kelmaydi, oldida yoki keyin qo'shimcha element bo'lishi kerak.",
            "rule_ru": "Конструкция '把' подчёркивает результат действия над объектом. Структура: Подлежащее + 把 + объект + глагол + результат. Глагол не стоит один, нужен дополнительный элемент.",
            "rule_tj": "Сохтори '把' натиҷаи амал нисбат ба объектро таъкид мекунад. Сохтор: Мубтадо + 把 + объект + феъл + натиҷа. Феъл танҳо намеояд, унсури иловагӣ лозим аст.",
            "examples": [
                {"zh": "把空调关了！", "pinyin": "Bǎ kōngtiáo guān le!", "uz": "Konditsionerni o'chir!", "ru": "Выключи кондиционер!", "tj": "Кондитсионерро хомӯш кун!"},
                {"zh": "他把书放到桌子上了。", "pinyin": "Tā bǎ shū fàng dào zhuōzi shàng le.", "uz": "U kitobni stolga qo'ydi.", "ru": "Он положил книгу на стол.", "tj": "Вай китобро ба болои миз монд."}
            ]
        },
        {
            "no": 2,
            "title_zh": "概数②：数词 + 左右",
            "title_uz": "Taxminiy sonlar②: son + 左右",
            "title_ru": "Приблизительные числа②: число + 左右",
            "title_tj": "Рақамҳои тахминӣ②: рақам + 左右",
            "rule_uz": "'左右' so'z ma'nosi 'chap-o'ng' bo'lib, taxminiy miqdorni bildiradi. Son yoki vaqt so'zidan keyin qo'shiladi: 三十分钟左右 = taxminan 30 daqiqa. 'cha' so'ziga o'xshaydi.",
            "rule_ru": "'左右' буквально означает 'лево-право' и выражает приблизительное количество. Ставится после числа или слова времени: 三十分钟左右 = около 30 минут. Аналог русского 'примерно'.",
            "rule_tj": "'左右' аслан маънои 'чап-рост'-ро дорад ва миқдори тахминиро ифода мекунад. Баъди рақам ё вожаи вақт мегузорад: 三十分钟左右 = тахминан 30 дақиқа. Ба 'тахминан' монанд аст.",
            "examples": [
                {"zh": "我大概需要一个小时左右。", "pinyin": "Wǒ dàgài xūyào yī gè xiǎoshí zuǒyòu.", "uz": "Menga taxminan bir soat kerak bo'ladi.", "ru": "Мне нужно примерно около часа.", "tj": "Ба ман тахминан як соат лозим мешавад."},
                {"zh": "这个房间三十平米左右。", "pinyin": "Zhège fángjiān sānshí píngmǐ zuǒyòu.", "uz": "Bu xona taxminan o'ttiz kvadrat metr.", "ru": "Эта комната около тридцати квадратных метров.", "tj": "Ин хона тахминан си метри мураббаъ аст."}
            ]
        },
        {
            "no": 3,
            "title_zh": "动词 + 了 + 宾语 + 了",
            "title_uz": "Fe'l + le + ob'ekt + le (harakat tugallangan)",
            "title_ru": "Глагол + 了 + объект + 了 (действие завершено)",
            "title_tj": "Феъл + 了 + объект + 了 (амал тамом шудааст)",
            "rule_uz": "Bu tuzilma harakatning allaqachon tugallanganini yoki o'zgarish yuz berganini bildiradi. Birinchi 了 fe'ldan keyin, ikkinchisi gap oxirida keladi. Masalan: 关了门了 = eshikni allaqachon yopdim.",
            "rule_ru": "Эта конструкция указывает на то, что действие уже завершено или произошло изменение. Первое 了 ставится после глагола, второе — в конце предложения. Например: 关了门了 = уже закрыл дверь.",
            "rule_tj": "Ин сохтор нишон медиҳад, ки амал аллакай тамом шудааст ё тағйироте рух додааст. Аввалин 了 баъди феъл, дуввум — охири ҷумла меояд. Масалан: 关了门了 = аллакай дарро бастам.",
            "examples": [
                {"zh": "我把空调关了。", "pinyin": "Wǒ bǎ kōngtiáo guān le.", "uz": "Men konditsionerni o'chirdim.", "ru": "Я выключил кондиционер.", "tj": "Ман кондитсионерро хомӯш кардам."},
                {"zh": "他吃了饭了，不饿了。", "pinyin": "Tā chī le fàn le, bú è le.", "uz": "U ovqat yedi, endi och emas.", "ru": "Он уже поел, больше не голоден.", "tj": "Вай хӯрок хӯрд, дигар гурусна нест."}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Konditsionerni o'chirishni unutma!", "ru": "Не забудь выключить кондиционер!", "tj": "Фаромӯш накун ки кондитсионерро хомӯш кунӣ!"},
                {"no": 2, "uz": "U kitobni stolga qo'ydi.", "ru": "Он положил книгу на стол.", "tj": "Вай китобро ба болои миз монд."},
                {"no": 3, "uz": "Menga taxminan bir soat kerak bo'ladi.", "ru": "Мне нужно примерно около часа.", "tj": "Ба ман тахминан як соат лозим мешавад."},
                {"no": 4, "uz": "Avval hamma narsani o'z joyiga qo'y.", "ru": "Сначала положи все вещи на место.", "tj": "Аввал ҳама чизро ба ҷои аслиаш монд."},
                {"no": 5, "uz": "U ovqat yedi, endi och emas.", "ru": "Он уже поел, больше не голоден.", "tj": "Вай хӯрок хӯрд, дигар гурусна нест."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "别忘了___空调关了！", "sentence_uz": "Konditsionerni o'chirishni ___!", "sentence_ru": "Не забудь ___ кондиционер!", "sentence_tj": "Фаромӯш накун ки кондитсионерро ___!", "hint": "把"},
                {"no": 2, "sentence_zh": "我大概需要一个小时___。", "sentence_uz": "Menga taxminan bir soat ___ kerak.", "sentence_ru": "Мне нужно примерно час ___.", "sentence_tj": "Ба ман тахминан як соат ___ лозим аст.", "hint": "左右"},
                {"no": 3, "sentence_zh": "他把书___到桌子上了。", "sentence_uz": "U kitobni stolga ___.", "sentence_ru": "Он ___ книгу на стол.", "sentence_tj": "Вай китобро ба болои миз ___.", "hint": "放"},
                {"no": 4, "sentence_zh": "他吃___饭了，不饿了。", "sentence_uz": "U ovqat ___, endi och emas.", "sentence_ru": "Он уже ___ еду, больше не голоден.", "sentence_tj": "Вай хӯрок ___, дигар гурусна нест.", "hint": "了"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "你把房间收拾一下吧，太乱了！", "pinyin": "Nǐ bǎ fángjiān shōushi yīxià ba, tài luàn le!"},
                {"no": 2, "zh": "出门的时候别忘了把门锁上。", "pinyin": "Chū mén de shíhou bié wàng le bǎ mén suǒshang."}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "别忘了把空调关了！"},
                {"no": 2, "zh": "他把书放到桌子上了。"},
                {"no": 3, "zh": "我大概需要一个小时左右。"},
                {"no": 4, "zh": "先把东西都放到原来的地方。"},
                {"no": 5, "zh": "他吃了饭了，不饿了。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "把"},
                {"no": 2, "answer": "左右"},
                {"no": 3, "answer": "放"},
                {"no": 4, "answer": "了"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Xonangni tartibga sol, juda tarqoq!", "ru": "Убери комнату, слишком беспорядок!", "tj": "Хонаатро тартиб деҳ, хеле барҳам хӯрда!"},
                {"no": 2, "uz": "Chiqayotganda eshikni qulflashni unutma.", "ru": "Когда выходишь, не забудь запереть дверь.", "tj": "Вақти баромадан фаромӯш накун ки дарро қулф занӣ."}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'把'-konstruktsiyasidan foydalanib, uyda bajariladigan 5 ta ish haqida jumla tuzing (masalan: eshikni yopish, chiroqni o'chirish).", "ru": "Составьте 5 предложений о домашних делах, используя конструкцию '把' (например: закрыть дверь, выключить свет).", "tj": "5 ҷумла дар бораи корҳои хонагӣ бо сохтори '把' тартиб диҳед (масалан: бастани дар, хомӯш кардани чароғ)."},
        {"task_no": 2, "uz": "'左右' ishlatib, 3 ta jumla yozing: qancha vaqt, qancha masofa yoki qancha narsangiz borligini aytib bering.", "ru": "Напишите 3 предложения с '左右' о времени, расстоянии или количестве чего-либо.", "tj": "3 ҷумла бо '左右' нависед: дар бораи вақт, масофа ё миқдори чизе."}
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
