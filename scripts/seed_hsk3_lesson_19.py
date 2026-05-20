import asyncio
import json

from sqlalchemy import select

from app.db.session import async_session_maker as SessionLocal
from app.db.models.course_lessons import CourseLesson

LESSON = {
    "level": "hsk3",
    "lesson_order": 19,
    "lesson_code": "HSK3-L19",
    "title": json.dumps({"zh": "你没看出来吗", "uz": "Siz sezib qolmadingizmi", "ru": "Ты разве не заметил?", "tj": "Шумо пай набурдед?"}, ensure_ascii=False),
    "goal": json.dumps({"uz": "Yo'nalish to'ldiruvchilarining ko'chma ma'nolari (出来/起来/下去), '使/叫/让' kauzativ fe'llari va '经过+joy' iborasi", "ru": "Переносное значение направленных дополнений (出来/起来/下去), каузативные глаголы '使/叫/让' и выражение '经过+место'", "tj": "Маъноҳои маҷозии пуркунандаҳои самтӣ (出来/起来/下去), феълҳои каузативии '使/叫/让' ва ибораи '经过+ҷой'"}, ensure_ascii=False),
    "intro_text": json.dumps({"uz": "Bu darsda yo'nalish to'ldiruvchilarining majoziy ma'nolarini (出来 = paydo bo'lmoq, 起来 = boshlanmoq, 下去 = davom etmoq), '使/叫/让' ning farqlarini va '经过' iborasini o'rganamiz.", "ru": "В этом уроке мы изучим переносное значение направленных дополнений (出来 = обнаружить, 起来 = начать, 下去 = продолжить), разницу '使/叫/让' и выражение '经过'.", "tj": "Дар ин дарс мо маъноҳои маҷозии пуркунандаҳои самтӣ (出来 = ошкор кардан, 起来 = оғоз кардан, 下去 = идома додан), фарқи '使/叫/让' ва ибораи '经过'-ро меомӯзем."}, ensure_ascii=False),
    "vocabulary_json": json.dumps([
        {"no": 1, "zh": "发现", "pinyin": "fāxiàn", "pos": "v", "uz": "kashf qilmoq, topmoq", "ru": "обнаруживать, находить", "tj": "кашф кардан, ёфтан"},
        {"no": 2, "zh": "认出", "pinyin": "rèn chū", "pos": "v", "uz": "tanib olmoq", "ru": "узнавать (опознать)", "tj": "шинохтан"},
        {"no": 3, "zh": "变化", "pinyin": "biànhuà", "pos": "n/v", "uz": "o'zgarish; o'zgarmoq", "ru": "изменение; изменяться", "tj": "тағйирот; тағйир ёфтан"},
        {"no": 4, "zh": "经过", "pinyin": "jīngguò", "pos": "v/prep", "uz": "o'tmoq; ...orqali", "ru": "проходить; через (место)", "tj": "гузаштан; тавассути (ҷой)"},
        {"no": 5, "zh": "使", "pinyin": "shǐ", "pos": "v", "uz": "majbur qilmoq (rasmiy)", "ru": "заставлять (официальный стиль)", "tj": "маҷбур кардан (расмӣ)"},
        {"no": 6, "zh": "叫", "pinyin": "jiào", "pos": "v", "uz": "buyurmoq, chaqirmoq; ism", "ru": "велеть, звать; имя", "tj": "фармондан, даъват кардан; ном"},
        {"no": 7, "zh": "想起来", "pinyin": "xiǎng qǐ lái", "pos": "v", "uz": "eslab qolmoq, xotirlash", "ru": "вспомнить", "tj": "дар ёд овардан"},
        {"no": 8, "zh": "看出来", "pinyin": "kàn chū lái", "pos": "v", "uz": "sezib/payqab olmoq", "ru": "заметить, разглядеть", "tj": "пай бурдан"},
        {"no": 9, "zh": "坚持下去", "pinyin": "jiānchí xià qù", "pos": "v", "uz": "davom ettirmoq (yiqilmasdan)", "ru": "продолжать (не сдаваться)", "tj": "идома додан (таслим нашудан)"},
        {"no": 10, "zh": "笑起来", "pinyin": "xiào qǐ lái", "pos": "v", "uz": "kulib yubormoq (boshlanish)", "ru": "засмеяться (начало)", "tj": "хандидан сар кардан (оғоз)"},
        {"no": 11, "zh": "秘密", "pinyin": "mìmì", "pos": "n/adj", "uz": "sir, maxfiy", "ru": "тайна, секрет; секретный", "tj": "сир, махфӣ"},
        {"no": 12, "zh": "样子", "pinyin": "yàngzi", "pos": "n", "uz": "ko'rinish, qiyofa", "ru": "вид, внешность", "tj": "намуд, қиёфа"},
        {"no": 13, "zh": "街道", "pinyin": "jiēdào", "pos": "n", "uz": "ko'cha, mahalla", "ru": "улица, квартал", "tj": "кӯча, маҳалла"}
    ], ensure_ascii=False),
    "dialogue_json": json.dumps([
        {
            "block_no": 1,
            "section_label": "课文 1",
            "title": {"uz": "O'zgarishni payqash", "ru": "Замечаю изменение", "tj": "Тағйиротро мушоҳида кардан"},
            "dialogue": [
                {"speaker": "A", "zh": "你没看出来吗？她变了！", "pinyin": "Nǐ méi kàn chū lái ma? Tā biàn le!", "uz": "Siz sezib qolmadingizmi? U o'zgardi!", "ru": "Ты разве не заметил? Она изменилась!", "tj": "Шумо пай набурдед? Вай тағйир ёфт!"},
                {"speaker": "B", "zh": "真的吗？我没看出来任何变化。", "pinyin": "Zhēn de ma? Wǒ méi kàn chū lái rènhé biànhuà.", "uz": "Chinmi? Men hech qanday o'zgarishni sezmadim.", "ru": "Правда? Я не заметил никаких изменений.", "tj": "Ростан? Ман ҳеҷ тағйироте надидам."},
                {"speaker": "A", "zh": "她的样子变化很大，连我都认出来了！", "pinyin": "Tā de yàngzi biànhuà hěn dà, lián wǒ dōu rèn chū lái le!", "uz": "Uning qiyofasi juda o'zgardi, hatto men ham tanib oldim!", "ru": "Её внешность сильно изменилась, даже я её узнал!", "tj": "Қиёфаи вай хеле тағйир ёфт, ҳатто ман ҳам вайро шинохтам!"},
                {"speaker": "B", "zh": "啊，对！我想起来了，她换了发型！", "pinyin": "À, duì! Wǒ xiǎng qǐ lái le, tā huàn le fàxíng!", "uz": "Oh, ha! Esladim, u soch turmagi o'zgartirdi!", "ru": "О, да! Вспомнил, она сменила причёску!", "tj": "О, ҳа! Дар ёд овардам, вай сарушонаро иваз кард!"}
            ]
        },
        {
            "block_no": 2,
            "section_label": "课文 2",
            "title": {"uz": "Ko'cha orqali o'tish", "ru": "Проход мимо улицы", "tj": "Гузаштан аз кӯча"},
            "dialogue": [
                {"speaker": "A", "zh": "你是怎么到这里来的？", "pinyin": "Nǐ shì zěnme dào zhèlǐ lái de?", "uz": "Siz bu yerga qanday keldingiz?", "ru": "Как ты сюда добрался?", "tj": "Шумо чӣ тавр ин ҷо омадед?"},
                {"speaker": "B", "zh": "我是经过那条街道来的，看到了新的咖啡店！", "pinyin": "Wǒ shì jīngguò nà tiáo jiēdào lái de, kàndào le xīn de kāfēidiàn!", "uz": "Men u ko'cha orqali keldim, yangi qahvaxona ko'rdim!", "ru": "Я прошёл через ту улицу и увидел новую кофейню!", "tj": "Ман аз он кӯча гузашта омадам ва қаҳвахонаи нав дидам!"},
                {"speaker": "A", "zh": "哦！你经过公园了吗？", "pinyin": "Ó! Nǐ jīngguò gōngyuán le ma?", "uz": "Oh! Siz parkdan o'tdingizmi?", "ru": "О! Ты проходил через парк?", "tj": "О! Шумо аз боғ гузаштед?"},
                {"speaker": "B", "zh": "经过了！公园里笑起来的孩子们好可爱！", "pinyin": "Jīngguò le! Gōngyuán lǐ xiào qǐ lái de háizimen hǎo kě'ài!", "uz": "O'tdim! Parkda kulib yuborgan bolalar juda chiroyli!", "ru": "Прошёл! Засмеявшиеся дети в парке такие милые!", "tj": "Гузаштам! Кӯдаконе ки дар боғ хандидан гирифтаанд хеле зебо буданд!"}
            ]
        },
        {
            "block_no": 3,
            "section_label": "课文 3",
            "title": {"uz": "Sirni bilish", "ru": "Узнать тайну", "tj": "Донистани сир"},
            "dialogue": [
                {"speaker": "A", "zh": "你看出来他有什么秘密吗？", "pinyin": "Nǐ kàn chū lái tā yǒu shénme mìmì ma?", "uz": "Sizga uning qanday siri borligini payqadingizmi?", "ru": "Ты заметил, что у него есть какая-то тайна?", "tj": "Пай бурдед, ки сири вай чист?"},
                {"speaker": "B", "zh": "没看出来，但是使我觉得他很奇怪。", "pinyin": "Méi kàn chū lái, dànshì shǐ wǒ juéde tā hěn qíguài.", "uz": "Sezmadim, lekin meni uni g'alati deb o'ylashga majbur qildi.", "ru": "Не заметил, но это заставило меня думать, что он странный.", "tj": "Пай набурдам, аммо ин маро маҷбур кард, ки вайро аҷиб ҳис кунам."},
                {"speaker": "A", "zh": "他叫你不要告诉别人，对吗？", "pinyin": "Tā jiào nǐ bú yào gàosù biérén, duì ma?", "uz": "U sizga boshqalarga aytmaslikni buyurdimi, to'g'rimi?", "ru": "Он велел тебе никому не говорить, да?", "tj": "Вай ба шумо фармод, ки ба дигарон нагӯед, дуруст аст?"},
                {"speaker": "B", "zh": "是的，所以我坚持下去，一直没说出来！", "pinyin": "Shì de, suǒyǐ wǒ jiānchí xià qù, yīzhí méi shuō chū lái!", "uz": "Ha, shuning uchun men davom etdim, doim aytmadim!", "ru": "Да, поэтому я держался, так и не рассказал!", "tj": "Ҳа, аз ин рӯ ман идома додам, ҳамеша нагуфтам!"}
            ]
        },
        {
            "block_no": 4,
            "section_label": "课文 4",
            "title": {"uz": "Mashq davom ettirish", "ru": "Продолжение тренировки", "tj": "Идомаи машқ"},
            "dialogue": [
                {"speaker": "A", "zh": "你能坚持下去吗？已经锻炼了一个小时了！", "pinyin": "Nǐ néng jiānchí xià qù ma? Yǐjīng duànliàn le yī gè xiǎoshí le!", "uz": "Davom ettira olasizmi? Allaqachon bir soat mashq qildingiz!", "ru": "Ты можешь продолжать? Уже час тренировался!", "tj": "Идома дода метавонед? Аллакай як соат варзиш кардед!"},
                {"speaker": "B", "zh": "能！只要坚持下去，就能看出来效果！", "pinyin": "Néng! Zhǐyào jiānchí xià qù, jiù néng kàn chū lái xiàoguǒ!", "uz": "Ha! Faqat davom etsam, natijani ko'raman!", "ru": "Да! Только продолжая, можно заметить результат!", "tj": "Метавонам! Танҳо идома диҳам, натиҷаро мебинам!"},
                {"speaker": "A", "zh": "这使我很受鼓励！", "pinyin": "Zhè shǐ wǒ hěn shòu gǔlì!", "uz": "Bu meni juda ilhomlantirdi!", "ru": "Это очень меня воодушевляет!", "tj": "Ин маро хеле илҳом бахшид!"},
                {"speaker": "B", "zh": "一起坚持下去吧，经过努力就能成功！", "pinyin": "Yīqǐ jiānchí xià qù ba, jīngguò nǔlì jiù néng chénggōng!", "uz": "Birga davom etaylik, harakat orqali muvaffaqiyat qozonish mumkin!", "ru": "Давай продолжим вместе, через усилия — к успеху!", "tj": "Якҷо идома диҳем, тавассути кӯшиш муваффақ мешавем!"}
            ]
        }
    ], ensure_ascii=False),
    "grammar_json": json.dumps([
        {
            "no": 1,
            "title_zh": "趋向补语引申义：出来/起来/下去",
            "title_uz": "Yo'nalish to'ldiruvchilarining ko'chma ma'nolari: 出来/起来/下去",
            "title_ru": "Переносное значение направленных дополнений: 出来/起来/下去",
            "title_tj": "Маъноҳои маҷозии пуркунандаҳои самтӣ: 出来/起来/下去",
            "rule_uz": "出来 = nimadir oshkor bo'lmoq/paydo bo'lmoq (看出来 = sezib olmoq); 起来 = harakat yoki holat boshlanmoq (笑起来 = kulib yubormoq); 下去 = harakat davom etmoq (坚持下去 = davom ettirmoq). Bular ko'chma/majoziy ma'nolar.",
            "rule_ru": "出来 = что-то обнаруживается/появляется (看出来 = заметить); 起来 = действие или состояние начинается (笑起来 = засмеяться); 下去 = действие продолжается (坚持下去 = продолжать держаться). Это переносные значения.",
            "rule_tj": "出来 = чизе ошкор мешавад/пайдо мешавад (看出来 = пай бурдан); 起来 = амал ё ҳолат оғоз меёбад (笑起来 = хандидан гирифтан); 下去 = амал идома меёбад (坚持下去 = идома додан). Инҳо маъноҳои маҷозӣ ҳастанд.",
            "examples": [
                {"zh": "你没看出来她变了吗？", "pinyin": "Nǐ méi kàn chū lái tā biàn le ma?", "uz": "Siz uning o'zgarganini sezmadingizmi?", "ru": "Ты разве не заметил, что она изменилась?", "tj": "Шумо пай набурдед, ки вай тағйир ёфт?"},
                {"zh": "只要坚持下去，就能成功！", "pinyin": "Zhǐyào jiānchí xià qù, jiù néng chénggōng!", "uz": "Faqat davom etsangiz, muvaffaqiyat qozonasiz!", "ru": "Только продолжай — и добьёшься успеха!", "tj": "Танҳо идома диҳед, муваффақ мешавед!"}
            ]
        },
        {
            "no": 2,
            "title_zh": "使/叫/让（使役）的比较",
            "title_uz": "使/叫/让 kauzativ fe'llari taqqoslash",
            "title_ru": "Сравнение каузативных глаголов 使/叫/让",
            "title_tj": "Муқоисаи феълҳои каузативии 使/叫/让",
            "rule_uz": "Uchtasi ham 'biror kishini biror narsa qilishga majbur qilmoq' ma'nosida. Farq: '使' = rasmiy, yozma uslub (bu holat meni majbur qildi); '叫' = buyurish, ko'proq og'zaki, kichiklarga; '让' = ruxsat berish YOKI majbur qilish — eng ko'p ishlatiladigan.",
            "rule_ru": "Все три означают 'заставить/позволить кому-то сделать что-то'. Разница: '使' = официальный, письменный стиль (это обстоятельство меня заставило); '叫' = приказать, больше устный, к подчинённым; '让' = позволить ИЛИ заставить — наиболее употребительный.",
            "rule_tj": "Ҳарсе маъноеро доранд, ки 'ба касе иҷозат додан ё маҷбур кардан'. Фарқ: '使' = расмӣ, услуби хаттӣ (ин ҳолат маро маҷбур кард); '叫' = фармондан, бештар шифоҳӣ, ба зердастон; '让' = иҷозат додан ЁД маҷбур кардан — бештар истифодашаванда.",
            "examples": [
                {"zh": "这使我很受鼓励！", "pinyin": "Zhè shǐ wǒ hěn shòu gǔlì!", "uz": "Bu meni juda ilhomlantirdi! (rasmiy)", "ru": "Это очень меня воодушевляет! (официальный)", "tj": "Ин маро хеле илҳом бахшид! (расмӣ)"},
                {"zh": "他叫我不要告诉别人。", "pinyin": "Tā jiào wǒ bú yào gàosù biérén.", "uz": "U menga boshqalarga aytmaslikni buyurdi.", "ru": "Он велел мне никому не говорить.", "tj": "Вай ба ман фармод, ки ба дигарон нагӯям."}
            ]
        },
        {
            "no": 3,
            "title_zh": "经过 + 地点（路过/经历）",
            "title_uz": "经过 + joy (orqali o'tmoq / tajribadan o'tmoq)",
            "title_ru": "经过 + место (проходить через / через опыт)",
            "title_tj": "经过 + ҷой (гузаштан аз / тавассути таҷриба)",
            "rule_uz": "'经过' ikki ma'noda: (1) joy bo'ylab o'tmoq (经过公园 = parkdan o'tmoq); (2) biror jarayon/tajribadan o'tmoq (经过努力 = harakat orqali). Predlog sifatida joy yoki jarayondan oldin keladi.",
            "rule_ru": "'经过' имеет два значения: (1) проходить через место (经过公园 = проходить через парк); (2) проходить через процесс/опыт (经过努力 = через усилия). В качестве предлога стоит перед местом или процессом.",
            "rule_tj": "'经过' ду маъно дорад: (1) аз ҷое гузаштан (经过公园 = аз боғ гузаштан); (2) аз раванде/таҷрибае гузаштан (经过努力 = тавассути кӯшиш). Ҳамчун пешоянд пеш аз ҷой ё раванд меояд.",
            "examples": [
                {"zh": "我经过那条街道来的。", "pinyin": "Wǒ jīngguò nà tiáo jiēdào lái de.", "uz": "Men u ko'cha orqali keldim.", "ru": "Я пришёл через ту улицу.", "tj": "Ман аз он кӯча гузашта омадам."},
                {"zh": "经过努力，他终于成功了！", "pinyin": "Jīngguò nǔlì, tā zhōngyú chénggōng le!", "uz": "Harakat orqali u nihoyat muvaffaqiyat qozondi!", "ru": "Через усилия он наконец добился успеха!", "tj": "Тавассути кӯшиш, вай дар охир муваффақ шуд!"}
            ]
        }
    ], ensure_ascii=False),
    "exercise_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "title": {"uz": "Xitoy tiliga tarjima qiling", "ru": "Переведите на китайский", "tj": "Ба забони чинӣ тарҷума кунед"},
            "items": [
                {"no": 1, "uz": "Siz uning o'zgarganini sezmadingizmi?", "ru": "Ты разве не заметил, что она изменилась?", "tj": "Шумо пай набурдед, ки вай тағйир ёфт?"},
                {"no": 2, "uz": "Faqat davom etsangiz, muvaffaqiyat qozonasiz!", "ru": "Только продолжай — и добьёшься успеха!", "tj": "Танҳо идома диҳед, муваффақ мешавед!"},
                {"no": 3, "uz": "Men u ko'cha orqali keldim.", "ru": "Я пришёл через ту улицу.", "tj": "Ман аз он кӯча гузашта омадам."},
                {"no": 4, "uz": "U menga boshqalarga aytmaslikni buyurdi.", "ru": "Он велел мне никому не говорить.", "tj": "Вай ба ман фармод, ки ба дигарон нагӯям."},
                {"no": 5, "uz": "Harakat orqali u nihoyat muvaffaqiyat qozondi!", "ru": "Через усилия он наконец добился успеха!", "tj": "Тавассути кӯшиш, вай дар охир муваффақ шуд!"}
            ]
        },
        {
            "type": "fill_blank",
            "title": {"uz": "Bo'sh joyni to'ldiring", "ru": "Заполните пропуск", "tj": "Ҷойи холиро пур кунед"},
            "items": [
                {"no": 1, "sentence_zh": "你没看___来她变了吗？", "sentence_uz": "Siz uning o'zgarganini sez___ qolmadingizmi?", "sentence_ru": "Ты разве не замет___ что она изменилась?", "sentence_tj": "Шумо пай нaбу___ ки вай тағйир ёфт?", "hint": "出"},
                {"no": 2, "sentence_zh": "孩子们笑___来了！", "sentence_uz": "Bolalar kulib ___!", "sentence_ru": "Дети ___смеялись!", "sentence_tj": "Кӯдакон хандидан ___!", "hint": "起"},
                {"no": 3, "sentence_zh": "我___那条街道来的。", "sentence_uz": "Men u ko'cha ___ keldim.", "sentence_ru": "Я ___ той улицей пришёл.", "sentence_tj": "Ман аз он кӯча ___ омадам.", "hint": "经过"},
                {"no": 4, "sentence_zh": "这___我很受鼓励！", "sentence_uz": "Bu meni juda ___!", "sentence_ru": "Это ___ меня воодушевило!", "sentence_tj": "Ин маро ___ кард!", "hint": "使"}
            ]
        },
        {
            "type": "translate_to_native",
            "title": {"uz": "Ona tiliga tarjima qiling", "ru": "Переведите на родной язык", "tj": "Ба забони модарӣ тарҷума кунед"},
            "items": [
                {"no": 1, "zh": "只要坚持下去，就能看出来效果！", "pinyin": "Zhǐyào jiānchí xià qù, jiù néng kàn chū lái xiàoguǒ!"},
                {"no": 2, "zh": "经过公园的时候，我想起来了一首歌。", "pinyin": "Jīngguò gōngyuán de shíhou, wǒ xiǎng qǐ lái le yī shǒu gē."}
            ]
        }
    ], ensure_ascii=False),
    "answers_json": json.dumps([
        {
            "type": "translate_to_chinese",
            "answers": [
                {"no": 1, "zh": "你没看出来她变了吗？"},
                {"no": 2, "zh": "只要坚持下去，就能成功！"},
                {"no": 3, "zh": "我经过那条街道来的。"},
                {"no": 4, "zh": "他叫我不要告诉别人。"},
                {"no": 5, "zh": "经过努力，他终于成功了！"}
            ]
        },
        {
            "type": "fill_blank",
            "answers": [
                {"no": 1, "answer": "出"},
                {"no": 2, "answer": "起"},
                {"no": 3, "answer": "经过"},
                {"no": 4, "answer": "使"}
            ]
        },
        {
            "type": "translate_to_native",
            "answers": [
                {"no": 1, "uz": "Faqat davom etsangiz, natijani ko'rish mumkin!", "ru": "Только продолжая, можно заметить результат!", "tj": "Танҳо идома диҳед, натиҷаро мебинед!"},
                {"no": 2, "uz": "Parkdan o'tayotganda, bir qo'shiq esimga tushdi.", "ru": "Проходя через парк, я вспомнил одну песню.", "tj": "Ҳангоми гузаштан аз боғ, як суруд ба ёдам омад."}
            ]
        }
    ], ensure_ascii=False),
    "homework_json": json.dumps([
        {"task_no": 1, "uz": "'看出来', '想起来', '坚持下去' iboralarini ishlatib, 3 ta jumla yozing, har birida ko'chma ma'no bo'lsin.", "ru": "Напишите 3 предложения с '看出来', '想起来', '坚持下去', используя переносное значение.", "tj": "3 ҷумла бо '看出来', '想起来', '坚持下去' нависед, ҳар кадом бо маъноҳои маҷозӣ."},
        {"task_no": 2, "uz": "'使', '叫', '让' larning farqini ko'rsatib, har biridan 1 ta jumla tuzing va '经过+joy' ni ham qo'shing.", "ru": "Покажите разницу '使', '叫', '让', составив по 1 предложению с каждым, добавьте '经过+место'.", "tj": "Фарқи '使', '叫', '让'-ро нишон дода, аз ҳар кадом 1 ҷумла тартиб диҳед ва '经过+ҷой'-ро ҳам илова кунед."}
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
