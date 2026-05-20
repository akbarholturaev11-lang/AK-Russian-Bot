import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 17,
    "lesson_code": "HSK3-L17",
    "title": json.dumps({"zh": "谁都有办法看好你的\"病\"", "uz": "Hammaning sizning \"kasalingizni\" davolashga yo'li bor", "ru": "У каждого есть способ вылечить твою \"болезнь\"", "tj": "Ҳар кас усул дорад \"бемориатонро\" табобат кунад"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "Ikki bo'g'inli fe'l takrori, so'roq olmoshlarining uchinchi maxsus qo'llanishi va '根据' predlogi", "ru": "Удвоение двусложных глаголов, третье особое употребление вопросительных местоимений и предлог '根据'", "tj": "Такрори феълҳои дутаяко, истифодаи сеюми хоси зомирҳои саволӣ ва пешояни '根据'"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda ikki bo'g'inli fe'llarning takrorini (ABAB shakli), so'roq olmoshlarining yana bir maxsus qo'llanishini va '根据' (asosida, ko'ra) predlogini o'rganamiz.", "ru": "В этом уроке мы изучим удвоение двусложных глаголов (форма ABAB), ещё одно особое употребление вопросительных местоимений и предлог '根据' (на основании, согласно).", "tj": "Дар ин дарс мо такрори феълҳои дутаяко (шакли ABAB), боз як истифодаи хоси зомирҳои саволӣ ва пешояни '根据' (дар асоси, мувофиқ)-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "办法", "pinyin": "bànfǎ", "pos": "n", "uz": "yo'l, usul, chora", "ru": "способ, метод, средство", "tj": "усул, роҳ, чора"},
        {"no": 2, "zh": "根据", "pinyin": "gēnjù", "pos": "prep/n", "uz": "asosida, ko'ra; asos", "ru": "согласно, на основании; основание", "tj": "дар асоси, мувофиқ; асос"},
        {"no": 3, "zh": "情况", "pinyin": "qíngkuàng", "pos": "n", "uz": "holat, vaziyat", "ru": "ситуация, обстановка", "tj": "вазъ, ҳолат"},
        {"no": 4, "zh": "建议", "pinyin": "jiànyì", "pos": "n/v", "uz": "taklif; taklif qilmoq", "ru": "предложение; предлагать", "tj": "пешниҳод; пешниҳод кардан"},
        {"no": 5, "zh": "讨论", "pinyin": "tǎolùn", "pos": "v/n", "uz": "muhokama qilmoq; muhokama", "ru": "обсуждать; обсуждение", "tj": "муҳокима кардан; муҳокима"},
        {"no": 6, "zh": "研究", "pinyin": "yánjiū", "pos": "v/n", "uz": "o'rganmoq, tadqiq qilmoq; tadqiqot", "ru": "изучать, исследовать; исследование", "tj": "омӯхтан, таҳқиқ кардан; таҳқиқот"},
        {"no": 7, "zh": "解释", "pinyin": "jiěshì", "pos": "v/n", "uz": "tushuntirmoq; tushuntirish", "ru": "объяснять; объяснение", "tj": "шарҳ додан; шарҳ"},
        {"no": 8, "zh": "介绍", "pinyin": "jièshào", "pos": "v/n", "uz": "tanishtirmoq; taqdimot", "ru": "представлять; представление", "tj": "муаррифӣ кардан; муаррифӣ"},
        {"no": 9, "zh": "检查", "pinyin": "jiǎnchá", "pos": "v", "uz": "tekshirmoq", "ru": "проверять, осматривать", "tj": "санҷидан, тафтиш кардан"},
        {"no": 10, "zh": "锻炼", "pinyin": "duànliàn", "pos": "v", "uz": "mashq qilmoq, jismoniy tarbiya", "ru": "тренироваться, заниматься физкультурой", "tj": "варзиш кардан, машқ кардан"},
        {"no": 11, "zh": "饮食", "pinyin": "yǐnshí", "pos": "n", "uz": "ovqatlanish, taom-ichimlik", "ru": "питание, рацион", "tj": "хӯрок ва нӯшокӣ, парҳез"},
        {"no": 12, "zh": "习惯", "pinyin": "xíguàn", "pos": "n/v", "uz": "odat; odatlanmoq", "ru": "привычка; привыкать", "tj": "одат; одат кардан"},
        {"no": 13, "zh": "病", "pinyin": "bìng", "pos": "n/v", "uz": "kasallik; kasal bo'lmoq", "ru": "болезнь; болеть", "tj": "беморӣ; бемор шудан"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "Kasallik uchun maslahat", "ru": "Совет при болезни", "tj": "Маслиҳат ҳангоми беморӣ"},
            "dialogue": [
                {"speaker": "A", "zh": "我最近老是头疼，有什么办法吗？", "pinyin": "Wǒ zuìjìn lǎoshi tóuténg, yǒu shénme bànfǎ ma?", "uz": "Yaqinda boshim doimo og'riyapti, biror chora bormi?", "ru": "У меня в последнее время постоянно болит голова, есть какой-нибудь способ?", "tj": "Охирон сари ман ҳамеша дард мекунад, чорае ҳаст?"},
                {"speaker": "B", "zh": "根据你的情况，建议你好好休息！", "pinyin": "Gēnjù nǐ de qíngkuàng, jiànyì nǐ hǎohǎo xiūxi!", "uz": "Sizning holatingizga ko'ra, yaxshilab dam olishingizni tavsiya etaman!", "ru": "Исходя из вашей ситуации, советую хорошенько отдохнуть!", "tj": "Мувофиқи ҳолати шумо, тавсия медиҳам хуб-хуб истироҳат кунед!"},
                {"speaker": "A", "zh": "谁都有办法看好你的\"病\"，对吗？", "pinyin": "Shéi dōu yǒu bànfǎ kàn hǎo nǐ de \"bìng\", duì ma?", "uz": "Hammaning sizning \"kasalingizni\" davolashga yo'li bor, to'g'rimi?", "ru": "У каждого есть способ вылечить твою \"болезнь\", правда?", "tj": "Ҳар кас усул дорад \"бемориатонро\" табобат кунад, дуруст аст?"},
                {"speaker": "B", "zh": "是的！你的病不复杂，注意饮食就好了！", "pinyin": "Shì de! Nǐ de bìng bù fùzá, zhùyì yǐnshí jiù hǎo le!", "uz": "Ha! Sizning kasalingiz murakkab emas, ovqatlanishga e'tibor bersangiz yaxshi bo'ladi!", "ru": "Да! Твоя болезнь не сложная, следи за питанием и всё пройдёт!", "tj": "Ҳа! Бемории шумо мураккаб нест, ба хӯрок диққат диҳед, хуб мешавад!"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Shifokor bilan muhokama", "ru": "Обсуждение с врачом", "tj": "Муҳокима бо духтур"},
            "dialogue": [
                {"speaker": "A", "zh": "根据检查结果，我的身体怎么样？", "pinyin": "Gēnjù jiǎnchá jiéguǒ, wǒ de shēntǐ zěnme yàng?", "uz": "Tekshiruv natijalariga ko'ra, sog'ligim qanday?", "ru": "По результатам осмотра, как моё здоровье?", "tj": "Мувофиқи натиҷаи муоина, саломатиам чӣ тавр аст?"},
                {"speaker": "B", "zh": "你的身体还不错，但要注意一些习惯。", "pinyin": "Nǐ de shēntǐ hái bú cuò, dàn yào zhùyì yīxiē xíguàn.", "uz": "Sog'ligingiz yomon emas, lekin ba'zi odatlarga e'tibor bering.", "ru": "Здоровье у тебя ещё ничего, но нужно обратить внимание на привычки.", "tj": "Саломатиатон бад нест, аммо ба баъзе одатҳо диққат диҳед."},
                {"speaker": "A", "zh": "我每天都锻炼锻炼，这样可以吗？", "pinyin": "Wǒ měitiān dōu duànliàn duànliàn, zhèyàng kěyǐ ma?", "uz": "Men har kuni mashq qilib-qilib ko'raman, bu yaxshimi?", "ru": "Я каждый день немного занимаюсь физкультурой, это нормально?", "tj": "Ман ҳар рӯз каме варзиш мекунам, ин хуб аст?"},
                {"speaker": "B", "zh": "好！根据你的情况，继续锻炼就行！", "pinyin": "Hǎo! Gēnjù nǐ de qíngkuàng, jìxù duànliàn jiù xíng!", "uz": "Yaxshi! Holatiga ko'ra, mashqni davom ettiring!", "ru": "Отлично! По вашей ситуации, продолжайте заниматься!", "tj": "Хуб! Мувофиқи ҳолататон, варзишро идома диҳед!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Loyiha haqida muhokama", "ru": "Обсуждение проекта", "tj": "Муҳокимаи лоиҳа"},
            "dialogue": [
                {"speaker": "A", "zh": "我们来讨论讨论这个项目吧！", "pinyin": "Wǒmen lái tǎolùn tǎolùn zhège xiàngmù ba!", "uz": "Keling, bu loyihani bir oz muhokama qilaylik!", "ru": "Давайте немного обсудим этот проект!", "tj": "Биё ин лоиҳаро каме муҳокима кунем!"},
                {"speaker": "B", "zh": "好，根据上次的结果，我有一些新建议。", "pinyin": "Hǎo, gēnjù shàng cì de jiéguǒ, wǒ yǒu yīxiē xīn jiànyì.", "uz": "Yaxshi, o'tgan safar natijalariga ko'ra, bir necha yangi takliflarim bor.", "ru": "Хорошо, на основании прошлых результатов, у меня есть несколько новых предложений.", "tj": "Хуб, дар асоси натиҷаҳои дафъаи гузашта, ман чанд пешниҳоди нав дорам."},
                {"speaker": "A", "zh": "好，我们研究研究这些建议。", "pinyin": "Hǎo, wǒmen yánjiū yánjiū zhèxiē jiànyì.", "uz": "Yaxshi, keling bu takliflarni bir oz tadqiq qilaylik.", "ru": "Ладно, давайте немного изучим эти предложения.", "tj": "Хуб, биё ин пешниҳодҳоро каме таҳқиқ кунем."},
                {"speaker": "B", "zh": "好，什么时候都可以讨论，随时找我！", "pinyin": "Hǎo, shénme shíhou dōu kěyǐ tǎolùn, suíshí zhǎo wǒ!", "uz": "Yaxshi, har qachon muhokama qilish mumkin, har doim menga murojaat qiling!", "ru": "Хорошо, в любое время можно обсудить, обращайтесь ко мне в любой момент!", "tj": "Хуб, ҳар вақт муҳокима кардан мумкин, ҳар лаҳза ба ман муроҷиат кунед!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Yangi tanishuv", "ru": "Новое знакомство", "tj": "Шиносоии нав"},
            "dialogue": [
                {"speaker": "A", "zh": "我来介绍介绍，这是我的朋友李明。", "pinyin": "Wǒ lái jièshào jièshào, zhè shì wǒ de péngyou Lǐ Míng.", "uz": "Men tanishtirib qo'yay, bu mening do'stim Li Min.", "ru": "Позвольте представить, это мой друг Ли Мин.", "tj": "Биё муаррифӣ кунам, ин дӯстам Ли Мин аст."},
                {"speaker": "B", "zh": "你好，根据你朋友的介绍，你是医生？", "pinyin": "Nǐ hǎo, gēnjù nǐ péngyou de jièshào, nǐ shì yīshēng?", "uz": "Salom, do'stingizning tanishtirishiga ko'ra, siz shifokormiсiz?", "ru": "Привет, по представлению вашего друга, вы врач?", "tj": "Салом, мувофиқи муаррифии дӯстатон, шумо духтур ҳастед?"},
                {"speaker": "A", "zh": "是的！需要的话，随时可以来解释解释病情。", "pinyin": "Shì de! Xūyào de huà, suíshí kěyǐ lái jiěshì jiěshì bìngqíng.", "uz": "Ha! Kerak bo'lsa, har doim kelib kasallik holatini tushuntirish mumkin.", "ru": "Да! Если нужно, в любое время приходите, немного объясню состояние болезни.", "tj": "Ҳа! Лозим бошад, ҳар вақт биёед, каме вазъи бемориро шарҳ медиҳам."},
                {"speaker": "B", "zh": "太好了！谁都可以找你吗？", "pinyin": "Tài hǎo le! Shéi dōu kěyǐ zhǎo nǐ ma?", "uz": "Zo'r! Har kim murojaat qila oladimi?", "ru": "Отлично! Каждый может к вам обратиться?", "tj": "Олӣ! Ҳар кас муроҷиат карда метавонад?"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "双音节动词重叠：ABAB式",
            "title_uz": "Ikki bo'g'inli fe'l takrori: ABAB shakli",
            "title_ru": "Удвоение двусложных глаголов: форма ABAB",
            "title_tj": "Такрори феълҳои дутаяко: шакли ABAB",
            "rule_uz": "Ikki bo'g'inli fe'llar (AB) ABAB shaklida takrorlanadi: 讨论讨论 (muho-muho qilmoq), 研究研究, 介绍介绍. Bu shakl harakatni biroz sinab ko'rish yoki engil bajarish ma'nosini bildiradi.",
            "rule_ru": "Двусложные глаголы (AB) удваиваются по форме ABAB: 讨论讨论 (немного обсудить), 研究研究, 介绍介绍. Эта форма означает попробовать сделать что-то или сделать это немного.",
            "rule_tj": "Феълҳои дутаяко (AB) ба шакли ABAB такрор мешаванд: 讨论讨论 (каме муҳокима кардан), 研究研究, 介绍介绍. Ин шакл маъно медиҳад, ки чизеро каме санҷед ё каме анҷом диҳед.",
            "examples": [
                {"zh": "我们来讨论讨论这个问题吧。", "pinyin": "Wǒmen lái tǎolùn tǎolùn zhège wèntí ba.", "uz": "Keling, bu muammoni bir oz muhokama qilaylik.", "ru": "Давайте немного обсудим эту проблему.", "tj": "Биё ин масъаларо каме муҳокима кунем."},
                {"zh": "我来介绍介绍我的朋友。", "pinyin": "Wǒ lái jièshào jièshào wǒ de péngyou.", "uz": "Keling, do'stimni tanishtirib qo'yay.", "ru": "Позвольте немного представить моего друга.", "tj": "Биё дӯстамро каме муаррифӣ кунам."}
            ]
        },
        {
            "no": 2,
            "title_zh": "疑问代词活用③：什么时候都/谁都/哪儿都（肯定）",
            "title_uz": "So'roq olmoshlarining maxsus qo'llanishi③: har qachon/har kim/hamma joyda (tasdiq)",
            "title_ru": "Особое употребление вопросительных местоимений③: всегда/каждый/везде (утверждение)",
            "title_tj": "Истифодаи хоси зомирҳои саволӣ③: ҳар вақт/ҳар кас/ҳама ҷо (тасдиқ)",
            "rule_uz": "So'roq olmoshlari + 都 + tasdiq fe'l = mutlaq umumlashtirish (tasdiq). Masalan: 什么时候都可以 = har doim mumkin; 谁都可以来 = har kim kela oladi; 哪儿都有 = hamma joyda bor.",
            "rule_ru": "Вопросительное местоимение + 都 + утвердительный глагол = абсолютное обобщение (утверждение). Например: 什么时候都可以 = всегда можно; 谁都可以来 = каждый может прийти; 哪儿都有 = везде есть.",
            "rule_tj": "Зомири саволӣ + 都 + феъли тасдиқӣ = умумикунонии мутлақ (тасдиқ). Масалан: 什么时候都可以 = ҳар вақт мумкин; 谁都可以来 = ҳар кас омада метавонад; 哪儿都有 = ҳама ҷо ҳаст.",
            "examples": [
                {"zh": "什么时候都可以来找我！", "pinyin": "Shénme shíhou dōu kěyǐ lái zhǎo wǒ!", "uz": "Har doim menga murojaat qilish mumkin!", "ru": "В любое время можно приходить ко мне!", "tj": "Ҳар вақт ба ман муроҷиат кардан мумкин!"},
                {"zh": "谁都有办法解决这个问题。", "pinyin": "Shéi dōu yǒu bànfǎ jiějué zhège wèntí.", "uz": "Har kimning bu muammoni hal qilishga yo'li bor.", "ru": "У каждого есть способ решить эту проблему.", "tj": "Ҳар кас роҳе дорад ин масъаларо ҳал кунад."}
            ]
        },
        {
            "no": 3,
            "title_zh": "根据 + N（根据情况/结果/建议……）",
            "title_uz": "根据 + ot (holat/natija/taklif asosida)",
            "title_ru": "根据 + существительное (на основании ситуации/результата/предложения)",
            "title_tj": "根据 + исм (дар асоси ҳолат/натиҷа/пешниҳод)",
            "rule_uz": "'根据' predlogi = asosida, ko'ra, muvofiq. Tuzilma: 根据 + ot/gap + predikativ. Ingilizcha 'based on / according to' ga o'xshaydi. Ko'pincha tavsiya, qaror yoki tahlilda ishlatiladi.",
            "rule_ru": "Предлог '根据' = на основании, согласно, исходя из. Структура: 根据 + существительное/предложение + предикат. Похоже на английское 'based on / according to'. Часто используется при советах, решениях или анализе.",
            "rule_tj": "Пешоянди '根据' = дар асоси, мувофиқ, аз рӯи. Сохтор: 根据 + исм/ҷумла + хабар. Ба 'based on / according to'-и инглисӣ монанд аст. Зиёдтар дар тавсия, қарор ё таҳлил истифода мешавад.",
            "examples": [
                {"zh": "根据你的情况，建议你多休息。", "pinyin": "Gēnjù nǐ de qíngkuàng, jiànyì nǐ duō xiūxi.", "uz": "Holatingizga ko'ra, ko'proq dam olishingizni tavsiya qilaman.", "ru": "Исходя из вашей ситуации, рекомендую больше отдыхать.", "tj": "Мувофиқи ҳолататон, тавсия медиҳам бештар истироҳат кунед."},
                {"zh": "根据检查结果，你的身体很健康。", "pinyin": "Gēnjù jiǎnchá jiéguǒ, nǐ de shēntǐ hěn jiànkāng.", "uz": "Tekshiruv natijalariga ko'ra, sog'ligingiz juda yaxshi.", "ru": "По результатам осмотра, ваше здоровье очень хорошее.", "tj": "Мувофиқи натиҷаи муоина, саломатиатон хеле хуб аст."}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Keling, bu muammoni bir oz muhokama qilaylik.", "ru": "Давайте немного обсудим эту проблему.", "tj": "Биё ин масъаларо каме муҳокима кунем."},
                {"no": 2, "uz": "Holatingizga ko'ra, ko'proq dam olishingizni tavsiya qilaman.", "ru": "Исходя из вашей ситуации, рекомендую больше отдыхать.", "tj": "Мувофиқи ҳолататон, тавсия медиҳам бештар истироҳат кунед."},
                {"no": 3, "uz": "Har doim menga murojaat qilish mumkin!", "ru": "В любое время можно приходить ко мне!", "tj": "Ҳар вақт ба ман муроҷиат кардан мумкин!"},
                {"no": 4, "uz": "Har kimning bu muammoni hal qilishga yo'li bor.", "ru": "У каждого есть способ решить эту проблему.", "tj": "Ҳар кас роҳе дорад ин масъаларо ҳал кунад."},
                {"no": 5, "uz": "Tekshiruv natijalariga ko'ra, sog'ligingiz juda yaxshi.", "ru": "По результатам осмотра, ваше здоровье очень хорошее.", "tj": "Мувофиқи натиҷаи муоина, саломатиатон хеле хуб аст."}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "我们来讨论___这个问题吧。", "sentence_uz": "Keling, bu muammoni ___ muhokama qilaylik.", "sentence_ru": "Давайте ___ обсудим эту проблему.", "sentence_tj": "Биё ин масъаларо ___ муҳокима кунем.", "hint": "讨论（ABAB）"},
                {"no": 2, "sentence_zh": "___你的情况，建议你多休息。", "sentence_uz": "Holatingizga ___, ko'proq dam olishingizni tavsiya qilaman.", "sentence_ru": "___ вашей ситуации, рекомендую больше отдыхать.", "sentence_tj": "___ ҳолататон, тавсия медиҳам бештар истироҳат кунед.", "hint": "根据"},
                {"no": 3, "sentence_zh": "什么时候___可以来找我！", "sentence_uz": "Har doim ___ murojaat qilish mumkin!", "sentence_ru": "В любое время ___ можно приходить!", "sentence_tj": "Ҳар вақт ___ муроҷиат кардан мумкин!", "hint": "都"},
                {"no": 4, "sentence_zh": "谁___有办法解决这个问题。", "sentence_uz": "Har kimning bu muammoni hal qilishga ___ bor.", "sentence_ru": "У каждого ___ есть способ решить эту проблему.", "sentence_tj": "Ҳар кас ___ роҳе дорад ин масъаларо ҳал кунад.", "hint": "都"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "根据上次的结果，我有一些新建议。", "pinyin": "Gēnjù shàng cì de jiéguǒ, wǒ yǒu yīxiē xīn jiànyì."},
                {"no": 2, "zh": "谁都有办法看好你的\"病\"！", "pinyin": "Shéi dōu yǒu bànfǎ kàn hǎo nǐ de \"bìng\"!"}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "我们来讨论讨论这个问题吧。"},
                {"no": 2, "zh": "根据你的情况，建议你多休息。"},
                {"no": 3, "zh": "什么时候都可以来找我！"},
                {"no": 4, "zh": "谁都有办法解决这个问题。"},
                {"no": 5, "zh": "根据检查结果，你的身体很健康。"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "讨论（ABAB: 讨论讨论）"},
                {"no": 2, "answer": "根据"},
                {"no": 3, "answer": "都"},
                {"no": 4, "answer": "都"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "O'tgan safar natijalariga ko'ra, bir necha yangi takliflarim bor.", "ru": "На основании прошлых результатов, у меня есть несколько новых предложений.", "tj": "Дар асоси натиҷаҳои дафъаи гузашта, ман чанд пешниҳоди нав дорам."},
                {"no": 2, "uz": "Hammaning sizning \"kasalingizni\" davolashga yo'li bor!", "ru": "У каждого есть способ вылечить твою \"болезнь\"!", "tj": "Ҳар кас усул дорад \"бемориатонро\" табобат кунад!"}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'根据' predlogini ishlatib, biror tahlil yoki tavsiyaga asoslangan 3 ta jumla yozing (masalan: natijalariga ko'ra, holatiga ko'ra).", "ru": "Напишите 3 предложения с предлогом '根据', основанных на каком-либо анализе или рекомендации.", "tj": "3 ҷумла бо пешоянди '根据' нависед, дар асоси таҳлил ё тавсияе (масалан: аз рӯи натиҷаҳо, аз рӯи ҳолат)."},
        {"task_no": 2, "uz": "Ikki bo'g'inli fe'llarni ABAB shaklida takrorlab 3 ta jumla tuzing va '什么时候/谁/哪儿+都' iboralaridan ham foydalaning.", "ru": "Составьте 3 предложения с ABAB-удвоением двусложных глаголов и используйте '什么时候/谁/哪儿+都'.", "tj": "3 ҷумла бо такрори ABAB-феълҳои дутаяко тартиб диҳед ва '什么时候/谁/哪儿+都'-ро ҳам истифода баред."}
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
