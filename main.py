"""
Start Daily Bot - To'liq versiya 2.0
@Startdaily_bot | Admin: @Rustamjonoff1
"""
import asyncio
import logging
import os
import json
import aiohttp
import random
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand, BotCommandScopeDefault
)
from database import init_db, get_user, update_user, get_all_users
# ============================================================
# SOZLAMALAR  (server uchun environment variable orqali o'qiladi)
# ============================================================
BOT_TOKEN        = os.getenv("BOT_TOKEN", "")
OPENWEATHER_API  = os.getenv("OPENWEATHER_API", "")
EXCHANGERATE_API = os.getenv("EXCHANGERATE_API", "")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
ADMIN_ID         = int(os.getenv("ADMIN_ID", "5236920689"))
ADMIN_USERNAME   = os.getenv("ADMIN_USERNAME", "@Rustamjonoff1")
BOT_NAME         = "Start Daily"
GROQ_MODEL       = "llama3-70b-8192"
GROQ_URL         = "https://api.groq.com/openai/v1/chat/completions"
ALADHAN_API      = "https://api.aladhan.com/v1"
DATA_FILE        = "user_data.json"
SETTINGS_FILE    = "bot_settings.json"

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi! Environment variable o'rnating: "
        "export BOT_TOKEN='...'"
    )

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())
user_msg_times = defaultdict(list)

LANGUAGES = {
    "uz": "🇺🇿 O'zbek", "en": "🇬🇧 English", "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية", "tr": "🇹🇷 Türkçe", "es": "🇪🇸 Español", "hi": "🇮🇳 हिन्दी"
}
TG_LANG_MAP = {
    "uz":"uz","en":"en","ru":"ru","ar":"ar","tr":"tr","es":"es","hi":"hi",
    "uk":"ru","be":"ru","kk":"ru","az":"ru"
}

# ============================================================
# TARJIMALAR
# ============================================================
TR = {
    "choose_lang": {
        "uz":"🌍 Tilni tanlang:","en":"🌍 Choose your language:","ru":"🌍 Выберите язык:",
        "ar":"🌍 اختر لغتك:","tr":"🌍 Dil seçin:","es":"🌍 Elige tu idioma:","hi":"🌍 भाषा चुनें:"
    },
    "enter_name": {
        "uz":"👋 Ismingizni kiriting:","en":"👋 Enter your name:","ru":"👋 Введите ваше имя:",
        "ar":"👋 أدخل اسمك:","tr":"👋 Adınızı girin:","es":"👋 Ingresa tu nombre:","hi":"👋 अपना नाम दर्ज करें:"
    },
    "enter_city": {
        "uz":"🏙 Shahringizni kiriting.\nOb-havo shu shahar uchun avtomatik chiqadi.\n\nMisol: Toshkent",
        "en":"🏙 Enter your city.\nWeather will be displayed automatically for this city.\n\nExample: London",
        "ru":"🏙 Введите ваш город.\nПогода для этого города будет отображаться автоматически.\n\nПример: Москва",
        "ar":"🏙 أدخل مدينتك.\nسيتم عرض الطقس لهذه المدينة تلقائيًا.\n\nمثال: القاهرة",
        "tr":"🏙 Şehrinizi girin.\nHava durumu bu şehir için otomatik olarak gösterilecektir.\n\nÖrnek: İstanbul",
        "es":"🏙 Ingresa tu ciudad.\nEl clima se mostrará automáticamente para esta ciudad.\n\nEjemplo: Madrid",
        "hi":"🏙 अपना शहर दर्ज करें।\nइस शहर के लिए मौसम स्वचालित रूप से दिखाया जाएगा।\n\nउदाहरण: Delhi"
    },
    "sub_required": {
        "uz":"📢 Botdan foydalanish uchun quyidagi kanal(lar)ga obuna bo'ling:",
        "en":"📢 Please subscribe to the following channel(s) to use the bot:",
        "ru":"📢 Для использования бота подпишитесь на каналы:",
        "ar":"📢 يرجى الاشتراك في القنوات التالية لاستخدام البوت:",
        "tr":"📢 Botu kullanmak için kanallara abone olun:",
        "es":"📢 Suscríbase a los canales para usar el bot:",
        "hi":"📢 बॉट का उपयोग करने के लिए चैनलों की सदस्यता लें:"
    },
    "check_sub":     {"uz":"✅ Tekshirish","en":"✅ Check","ru":"✅ Проверить","ar":"✅ تحقق","tr":"✅ Kontrol et","es":"✅ Verificar","hi":"✅ जांचें"},
    "oferta_accept": {"uz":"✅ Qabul qilaman","en":"✅ I Accept","ru":"✅ Принимаю","ar":"✅ أقبل","tr":"✅ Kabul ediyorum","es":"✅ Acepto","hi":"✅ स्वीकार करता हूं"},
    "oferta_ok":     {"uz":"✅ Shartlar qabul qilindi!","en":"✅ Terms accepted!","ru":"✅ Условия приняты!","ar":"✅ تم قبول الشروط!","tr":"✅ Şartlar kabul edildi!","es":"✅ ¡Términos aceptados!","hi":"✅ शर्तें स्वीकार!"},
    "welcome": {
        "uz":"🌟 Start Daily ga xush kelibsiz, {name}!\n\nKunlik hayotingizni osonlashtirish uchun yaratilgan aqlli yordamchingizman.\n\nQuyidagi bo'limlardan birini tanlang 👇",
        "en":"🌟 Welcome to Start Daily, {name}!\n\nI'm your smart assistant created to simplify your daily life.\n\nChoose a section below 👇",
        "ru":"🌟 Добро пожаловать в Start Daily, {name}!\n\nЯ ваш умный помощник для упрощения повседневной жизни.\n\nВыберите раздел 👇",
        "ar":"🌟 مرحباً بك في Start Daily، {name}!\n\nأنا مساعدك الذكي لتبسيط حياتك اليومية.\n\nاختر قسماً 👇",
        "tr":"🌟 Start Daily'e hoş geldiniz, {name}!\n\nGünlük hayatınızı kolaylaştırmak için yaratıldım.\n\nBir bölüm seçin 👇",
        "es":"🌟 ¡Bienvenido a Start Daily, {name}!\n\nSoy tu asistente inteligente para simplificar tu vida.\n\nElige una sección 👇",
        "hi":"🌟 Start Daily में आपका स्वागत है, {name}!\n\nमैं आपका स्मार्ट सहायक हूं।\n\nनीचे एक अनुभाग चुनें 👇"
    },
    "main_menu": {
        "uz":"Quyidagi bo'limlardan birini tanlang 👇",
        "en":"Choose a section below 👇",
        "ru":"Выберите раздел 👇",
        "ar":"اختر قسماً 👇",
        "tr":"Bir bölüm seçin 👇",
        "es":"Elige una sección 👇",
        "hi":"नीचे एक अनुभाग चुनें 👇"
    },
    "blocked": {
        "uz":f"🚫 Hisobingiz bloklandi.\n📩 {ADMIN_USERNAME}",
        "en":f"🚫 Your account is blocked.\n📩 {ADMIN_USERNAME}",
        "ru":f"🚫 Ваш аккаунт заблокирован.\n📩 {ADMIN_USERNAME}",
        "ar":f"🚫 تم حظر حسابك.\n📩 {ADMIN_USERNAME}",
        "tr":f"🚫 Hesabınız engellendi.\n📩 {ADMIN_USERNAME}",
        "es":f"🚫 Tu cuenta está bloqueada.\n📩 {ADMIN_USERNAME}",
        "hi":f"🚫 आपका खाता ब्लॉक है।\n📩 {ADMIN_USERNAME}"
    },
    "warning_msg": {
        "uz":"⚠️ Ogohlantirish {n}/3\n\nSiz botning foydalanish shartlarini buzayotgansiz.\nYana {left} ta ogohlantirishdan so'ng bloklansiz.\n\n/oferta",
        "en":"⚠️ Warning {n}/3\n\nYou are violating the bot's terms.\nAfter {left} more warning(s) you will be blocked.\n\n/oferta",
        "ru":"⚠️ Предупреждение {n}/3\n\nВы нарушаете правила бота.\nЕщё {left} — и аккаунт заблокируют.\n\n/oferta",
        "ar":"⚠️ تحذير {n}/3\n\nأنت تنتهك شروط البوت.\nبعد {left} تحذير سيتم الحظر.\n\n/oferta",
        "tr":"⚠️ Uyarı {n}/3\n\nBot şartlarını ihlal ediyorsunuz.\n{left} uyarı daha — engel.\n\n/oferta",
        "es":"⚠️ Advertencia {n}/3\n\nEstás violando los términos.\n{left} más y serás bloqueado.\n\n/oferta",
        "hi":"⚠️ चेतावनी {n}/3\n\nआप शर्तों का उल्लंघन कर रहे हैं।\n{left} और — ब्लॉक।\n\n/oferta"
    },
    "spam_warning": {
        "uz":"⚠️ Juda tez xabar yuboryapsiz! Biroz kuting.",
        "en":"⚠️ You are sending messages too fast! Please wait.",
        "ru":"⚠️ Слишком быстро! Подождите.",
        "ar":"⚠️ أنت ترسل بسرعة! انتظر.",
        "tr":"⚠️ Çok hızlı! Lütfen bekleyin.",
        "es":"⚠️ ¡Demasiado rápido! Espera.",
        "hi":"⚠️ बहुत तेज़! कृपया प्रतीक्षा करें।"
    },
    "back":       {"uz":"🔙 Asosiy menyu","en":"🔙 Main menu","ru":"🔙 Главное меню","ar":"🔙 القائمة الرئيسية","tr":"🔙 Ana menü","es":"🔙 Menú principal","hi":"🔙 मुख्य मेनू"},
    "stay_hint":  {"uz":"➕ Yana kiriting yoki 🔙 tugmani bosing","en":"➕ Enter another or press 🔙","ru":"➕ Введите ещё или нажмите 🔙","ar":"➕ أدخل آخر أو اضغط 🔙","tr":"➕ Başka girin veya 🔙","es":"➕ Ingrese otro o presione 🔙","hi":"➕ और दर्ज करें या 🔙"},
    "once_btn":   {"uz":"1️⃣ Bir marta","en":"1️⃣ Once","ru":"1️⃣ Один раз","ar":"1️⃣ مرة","tr":"1️⃣ Bir kez","es":"1️⃣ Una vez","hi":"1️⃣ एक बार"},
    "daily_btn":  {"uz":"🔄 Har kuni","en":"🔄 Every day","ru":"🔄 Каждый день","ar":"🔄 كل يوم","tr":"🔄 Her gün","es":"🔄 Cada día","hi":"🔄 हर दिन"},
    "rem_type":   {"uz":"Qanday bo'lsin?","en":"What type?","ru":"Какой тип?","ar":"ما النوع؟","tr":"Tür?","es":"¿Qué tipo?","hi":"किस प्रकार?"},
    "rem_ok":     {"uz":"✅ Eslatma o'rnatildi!\n📅 {dt}\n📝 {text}\n🔁 {rep}","en":"✅ Reminder set!\n📅 {dt}\n📝 {text}\n🔁 {rep}","ru":"✅ Напоминание!\n📅 {dt}\n📝 {text}\n🔁 {rep}","ar":"✅ تذكير!\n📅 {dt}\n📝 {text}\n🔁 {rep}","tr":"✅ Hatırlatıcı!\n📅 {dt}\n📝 {text}\n🔁 {rep}","es":"✅ ¡Recordatorio!\n📅 {dt}\n📝 {text}\n🔁 {rep}","hi":"✅ अनुस्मारक!\n📅 {dt}\n📝 {text}\n🔁 {rep}"},
    "rem_notify": {"uz":"⏰ Eslatma!\n📝 {text}","en":"⏰ Reminder!\n📝 {text}","ru":"⏰ Напоминание!\n📝 {text}","ar":"⏰ تذكير!\n📝 {text}","tr":"⏰ Hatırlatıcı!\n📝 {text}","es":"⏰ ¡Recordatorio!\n📝 {text}","hi":"⏰ अनुस्मारक!\n📝 {text}"},
    "morning_q":  {"uz":"🌅 Yangi kun muborak!\n\n💬 {quote}\n\n— Start Daily","en":"🌅 Good morning!\n\n💬 {quote}\n\n— Start Daily","ru":"🌅 Доброе утро!\n\n💬 {quote}\n\n— Start Daily","ar":"🌅 صباح الخير!\n\n💬 {quote}\n\n— Start Daily","tr":"🌅 Günaydın!\n\n💬 {quote}\n\n— Start Daily","es":"🌅 ¡Buenos días!\n\n💬 {quote}\n\n— Start Daily","hi":"🌅 शुभ प्रभात!\n\n💬 {quote}\n\n— Start Daily"},
    "weekly_rep": {"uz":"📊 Haftalik hisobot\n\n💸 Xarajatlar:\n{exp}\n\n📋 {n} ta\n\nYaxshi hafta! 💪\n— Start Daily","en":"📊 Weekly Report\n\n💸 Expenses:\n{exp}\n\n📋 {n} records\n\nGreat week! 💪\n— Start Daily","ru":"📊 Еженедельный отчёт\n\n💸 Расходы:\n{exp}\n\n📋 {n} записей\n\nХорошей недели! 💪\n— Start Daily","ar":"📊 التقرير الأسبوعي\n\n💸 المصروفات:\n{exp}\n\n📋 {n}\n\nأسبوع سعيد! 💪\n— Start Daily","tr":"📊 Haftalık Rapor\n\n💸 Harcamalar:\n{exp}\n\n📋 {n}\n\nİyi haftalar! 💪\n— Start Daily","es":"📊 Informe Semanal\n\n💸 Gastos:\n{exp}\n\n📋 {n}\n\n¡Buena semana! 💪\n— Start Daily","hi":"📊 साप्ताहिक रिपोर्ट\n\n💸 खर्च:\n{exp}\n\n📋 {n}\n\nशुभ सप्ताह! 💪\n— Start Daily"},
    "menu": {
        "uz":  ["💸 Xarajatlar","📅 Kunlik reja","⏰ Eslatmalar","💱 Valyuta","🌤 Ob-havo","🤖 AI Yordamchi","👤 Profil","👨‍💼 Admin","⚙️ Sozlamalar"],
        "en":  ["💸 Expenses","📅 Daily Plan","⏰ Reminders","💱 Currency","🌤 Weather","🤖 AI Assistant","👤 Profile","👨‍💼 Admin","⚙️ Settings"],
        "ru":  ["💸 Расходы","📅 Дневной план","⏰ Напоминания","💱 Валюта","🌤 Погода","🤖 AI Помощник","👤 Профиль","👨‍💼 Админ","⚙️ Настройки"],
        "ar":  ["💸 المصروفات","📅 الخطة اليومية","⏰ التذكيرات","💱 العملة","🌤 الطقس","🤖 مساعد AI","👤 الملف","👨‍💼 المشرف","⚙️ الإعدادات"],
        "tr":  ["💸 Harcamalar","📅 Günlük Plan","⏰ Hatırlatıcılar","💱 Döviz","🌤 Hava Durumu","🤖 AI Asistan","👤 Profil","👨‍💼 Yönetici","⚙️ Ayarlar"],
        "es":  ["💸 Gastos","📅 Plan Diario","⏰ Recordatorios","💱 Moneda","🌤 Clima","🤖 Asistente AI","👤 Perfil","👨‍💼 Admin","⚙️ Ajustes"],
        "hi":  ["💸 खर्च","📅 दैनिक योजना","⏰ अनुस्मारक","💱 मुद्रा","🌤 मौसम","🤖 AI सहायक","👤 प्रोफ़ाइल","👨‍💼 व्यवस्थापक","⚙️ सेटिंग्स"]
    },
    "sec_expense": {
        "uz":"💸 Xarajatlar\n\nBugun nimalarga pul sarfladingiz?\nHar bir xarajatni quyidagicha kiriting:\n\n📝 Yo'nalish  Miqdor  Valyuta\n\nMisol:\n▪️ Tushlik 25000 UZS\n▪️ Taksi 5 USD\n▪️ Kiyim 50 dollar\n▪️ Oziq-ovqat 200 rubl\n\n💡 Valyutani istalgan tilda yozsa bo'ladi",
        "en":"💸 Expenses\n\nWhat did you spend money on today?\nEnter each expense like this:\n\n📝 Category  Amount  Currency\n\nExample:\n▪️ Lunch 25 USD\n▪️ Taxi 5 EUR\n▪️ Clothes 50 dollars\n▪️ Groceries 200 rubles\n\n💡 You can write currency in any language",
        "ru":"💸 Расходы\n\nНа что потратили деньги сегодня?\nВведите каждый расход:\n\n📝 Категория  Сумма  Валюта\n\nПример:\n▪️ Обед 500 RUB\n▪️ Такси 5 USD\n▪️ Одежда 50 долларов\n\n💡 Валюту можно писать на любом языке",
        "ar":"💸 المصروفات\n\nماذا أنفقت اليوم؟\nأدخل كل مصروف:\n\n📝 الفئة  المبلغ  العملة\n\nمثال:\n▪️ غداء 25 USD\n▪️ تاكسي 5 EUR\n\n💡 يمكن كتابة العملة بأي لغة",
        "tr":"💸 Harcamalar\n\nBugün nelere para harcadınız?\nHer harcamayı girin:\n\n📝 Kategori  Miktar  Para\n\nÖrnek:\n▪️ Öğle 25 USD\n▪️ Taksi 5 EUR\n▪️ Kıyafet 50 dolar\n\n💡 Para birimini istediğiniz dilde yazın",
        "es":"💸 Gastos\n\n¿En qué gastaste hoy?\nIngresa cada gasto:\n\n📝 Categoría  Monto  Moneda\n\nEjemplo:\n▪️ Almuerzo 25 USD\n▪️ Taxi 5 EUR\n▪️ Ropa 50 dólares\n\n💡 Puedes escribir la moneda en cualquier idioma",
        "hi":"💸 खर्च\n\nआज आपने किस पर पैसे खर्च किए?\nप्रत्येक खर्च दर्ज करें:\n\n📝 श्रेणी  राशि  मुद्रा\n\nउदाहरण:\n▪️ दोपहर 25 USD\n▪️ टैक्सी 5 EUR\n\n💡 किसी भी भाषा में मुद्रा लिखें"
    },
    "sec_plan": {
        "uz":"📅 Kunlik reja\n\nBugungi vazifalaringizni rejalashtiring!\nVaqt yozsangiz — o'sha vaqtda eslatma keladi.\n\n📝 Vaqt  Vazifa  yoki  shunchaki  Vazifa\n\nMisol:\n▪️ 07:00 Ertalabki yugurish\n▪️ 09:00 Muhim uchrashuv\n▪️ 13:00 Tushlik\n▪️ Kitob o'qish\n\n💡 Bir necha vazifani yangi qatordan yozing",
        "en":"📅 Daily Plan\n\nPlan your tasks for today!\nAdd a time and you'll get a reminder.\n\n📝 Time  Task  or  just  Task\n\nExample:\n▪️ 07:00 Morning run\n▪️ 09:00 Important meeting\n▪️ 13:00 Lunch\n▪️ Read a book\n\n💡 Write multiple tasks on separate lines",
        "ru":"📅 Дневной план\n\nЗапланируйте задачи на сегодня!\nДобавьте время — придёт напоминание.\n\n📝 Время  Задача  или  просто  Задача\n\nПример:\n▪️ 07:00 Пробежка\n▪️ 09:00 Встреча\n▪️ 13:00 Обед\n▪️ Читать книгу\n\n💡 Несколько задач — каждую с новой строки",
        "ar":"📅 الخطة اليومية\n\nخطط لمهامك اليوم!\nأضف وقتاً وستصلك تذكرة.\n\n📝 الوقت  المهمة  أو  فقط  المهمة\n\nمثال:\n▪️ 07:00 الركض\n▪️ 09:00 اجتماع\n▪️ قراءة\n\n💡 كل مهمة في سطر جديد",
        "tr":"📅 Günlük Plan\n\nBugünkü görevlerinizi planlayın!\nSaat ekleyin — hatırlatıcı gelir.\n\n📝 Saat  Görev  veya  Görev\n\nÖrnek:\n▪️ 07:00 Koşu\n▪️ 09:00 Toplantı\n▪️ Kitap oku\n\n💡 Birden fazla görevi ayrı satırlara yazın",
        "es":"📅 Plan Diario\n\n¡Planifica tus tareas!\nAgrega hora y recibirás recordatorio.\n\n📝 Hora  Tarea  o  Tarea\n\nEjemplo:\n▪️ 07:00 Carrera\n▪️ 09:00 Reunión\n▪️ Leer\n\n💡 Múltiples tareas en líneas separadas",
        "hi":"📅 दैनिक योजना\n\nआज के कार्यों की योजना बनाएं!\nसमय जोड़ें — अनुस्मारक मिलेगा।\n\n📝 समय  कार्य  या  कार्य\n\nउदाहरण:\n▪️ 07:00 दौड़\n▪️ 09:00 बैठक\n▪️ किताब पढ़ें\n\n💡 कई कार्य अलग पंक्तियों में"
    },
    "sec_reminder": {
        "uz":"⏰ Eslatmalar\n\nMuhim ishlaringizni unutmang!\nQuyidagi formatlardan birida yozing:\n\n✅Misol:\n\n1️⃣ Bugun uchun:\n▪️ 14:30 Dori ichish\n\n2️⃣ Aniq sana uchun:\n▪️ 25.06.2026 09:00 Tug'ilgan kun\n\n3️⃣ Har kuni uchun:\n▪️ Yuqoridagicha yozing\n▪️ Keyin Har kuni tugmasini bosing\n\n💡 Eslatma vaqti kelganda avtomatik xabar keladi",
        "en":"⏰ Reminders\n\nDon't forget important tasks!\nWrite in one of these formats:\n\n1️⃣ For today:\n▪️ 14:30 Take medicine\n\n2️⃣ For a specific date:\n▪️ 25.06.2026 09:00 Birthday\n\n3️⃣ For every day:\n▪️ Write as above\n▪️ Then press Every day\n\n💡 Auto message when it's time",
        "ru":"⏰ Напоминания\n\nНе забывайте важное!\nФорматы:\n\n1️⃣ Сегодня:\n▪️ 14:30 Лекарство\n\n2️⃣ Дата:\n▪️ 25.06.2026 09:00 День рождения\n\n3️⃣ Каждый день:\n▪️ Напишите как выше\n▪️ Нажмите Каждый день\n\n💡 Придёт сообщение в нужное время",
        "ar":"⏰ التذكيرات\n\nلا تنسَ المهام!\nالتنسيقات:\n\n1️⃣ اليوم:\n▪️ 14:30 دواء\n\n2️⃣ تاريخ:\n▪️ 25.06.2026 09:00 عيد\n\n3️⃣ يومياً:\n▪️ اكتب كما سبق\n▪️ اضغط كل يوم\n\n💡 رسالة تلقائية في الوقت",
        "tr":"⏰ Hatırlatıcılar\n\nÖnemli şeyleri unutmayın!\nFormatlar:\n\n1️⃣ Bugün:\n▪️ 14:30 İlaç\n\n2️⃣ Tarih:\n▪️ 25.06.2026 09:00 Doğum günü\n\n3️⃣ Her gün:\n▪️ Yukarıdaki gibi\n▪️ Her gün'e bas\n\n💡 Zamanında otomatik mesaj",
        "es":"⏰ Recordatorios\n\n¡No olvides lo importante!\nFormatos:\n\n1️⃣ Hoy:\n▪️ 14:30 Medicina\n\n2️⃣ Fecha:\n▪️ 25.06.2026 09:00 Cumpleaños\n\n3️⃣ Cada día:\n▪️ Escribe como arriba\n▪️ Presiona Cada día\n\n💡 Mensaje automático a tiempo",
        "hi":"⏰ अनुस्मारक\n\nमहत्वपूर्ण काम न भूलें!\nफॉर्मेट:\n\n1️⃣ आज:\n▪️ 14:30 दवा\n\n2️⃣ तारीख:\n▪️ 25.06.2026 09:00 जन्मदिन\n\n3️⃣ हर दिन:\n▪️ ऊपर की तरह\n▪️ हर दिन दबाएं\n\n💡 समय पर स्वचालित संदेश"
    },

    "sec_weather": {
        "uz":"🌤 Ob-havo\n\nIstalgan shahar ob-havosini real vaqtda bilib oling.\n\n📍 Shahar nomini kiriting:\n\nMisol:\n▪️ Toshkent\n▪️ Samarqand\n▪️ Dubai\n▪️ Moskva",
        "en":"🌤 Weather\n\nFind out the current weather for any city.\n\n📍 Enter city name:\n\nExample:\n▪️ London\n▪️ New York\n▪️ Dubai\n▪️ Tokyo",
        "ru":"🌤 Погода\n\nТекущая погода для любого города.\n\n📍 Введите город:\n\nПример:\n▪️ Москва\n▪️ Лондон\n▪️ Дубай",
        "ar":"🌤 الطقس\n\nالطقس الحالي لأي مدينة.\n\n📍 المدينة:\n\nمثال:\n▪️ القاهرة\n▪️ دبي\n▪️ لندن",
        "tr":"🌤 Hava Durumu\n\nHerhangi bir şehir için güncel hava.\n\n📍 Şehir:\n\nÖrnek:\n▪️ Istanbul\n▪️ Dubai\n▪️ Londra",
        "es":"🌤 Clima\n\nClima actual para cualquier ciudad.\n\n📍 Ciudad:\n\nEjemplo:\n▪️ Madrid\n▪️ Dubai\n▪️ Londres",
        "hi":"🌤 मौसम\n\nकिसी भी शहर का वर्तमान मौसम।\n\n📍 शहर:\n\nउदाहरण:\n▪️ Delhi\n▪️ Dubai\n▪️ London"
    },
    "sec_currency": {
    "uz": (
        "💱 Valyuta kursi\n\n160+ valyuta orasida konvertatsiya qiling.\n\n📝 Miqdor  Valyuta1  Valyuta2\n\nMisol:\n\n▪️ 100 dollar so'm\n\n▪️ 50 USD UZS\n\n▪️ 200 euro rubl\n\n▪️ 1000 so'm dollar\n\n💡 Davlat nomini yozsangiz ham bo'ladi\n\n▪ Valyuta shablonlarini ko'rish uchun tugmani bosing 👇"
    ),
    "en": (
        "💱 Currency Rate\n\nConvert between 160+ currencies.\n\n📝 Amount  Currency1  Currency2\n\nExample:\n\n▪️ 100 USD UZS\n\n▪️ 50 dollars som\n\n▪️ 200 euros rubles\n\n💡 Country name works too\n\n▪ Press button to see currency templates 👇"
    ),
    "ru": (
        "💱 Курс валют\n\nКонвертация 160+ валют.\n\n📝 Сумма  Валюта1  Валюта2\n\nПример:\n\n▪️ 100 доллар рубль\n\n▪️ 50 USD RUB\n\n▪️ 200 евро рублей\n\n💡 Можно писать название страны\n\n▪ Нажмите кнопку для шаблонов 👇"
    ),
        "ar": (
            "💱 سعر الصرف\n\n160+ عملة.\n\n📝 المبلغ  العملة1  العملة2\n\nمثال:\n\n▪️ 100 دولار درهم\n\n▪️ 50 USD SAR\n\n💡 يمكن كتابة اسم الدولة أيضًا\n\n▪ اضغط لرؤية القوالب 👇"
        ),
    "tr": (
        "💱 Döviz Kuru\n\n160+ para birimi.\n\n📝 Miktar  Para1  Para2\n\nÖrnek:\n\n▪️ 100 dolar lira\n\n▪️ 50 USD TRY\n\n💡 Ülke adı da yazabilirsiniz\n\n▪ Şablonlar için butona basın 👇"
    ),
    "es": (
        "💱 Tipo de Cambio\n\n160+ monedas.\n\n📝 Monto  Moneda1  Moneda2\n\nEjemplo:\n\n▪️ 100 dólares euros\n\n▪️ 50 USD EUR\n\n💡 Nombre del país también funciona\n\n▪ Presiona para ver plantillas 👇"
    ),
    "hi": (
        "💱 मुद्रा दर\n\n160+ मुद्राएं।\n\n📝 राशि  मुद्रा1  मुद्रा2\n\nउदाहरण:\n\n▪️ 100 dollar rupee\n\n▪️ 50 USD INR\n\n💡 देश का नाम भी काम करता है\n\n▪ टेम्पलेट देखने के लिए दबाएं 👇"
    ),
},
    "sec_ai": {
        "uz":"🤖 AI Yordamchi\n\nMenga istalgan savolni bering —\ntarjima, maslahat, tushuntirish,\nhisob-kitob va boshqa ko'p narsalar.\n\n💬 Savolingizni yozing...\n\n💡 Bu bo'limda qolasiz —\nxohlagan qadar savol bera olasiz",
        "en":"🤖 AI Assistant\n\nAsk me anything —\ntranslation, advice, explanations,\ncalculations and much more.\n\n💬 Write your question...\n\n💡 You stay in this section —\nask as many questions as you want",
        "ru":"🤖 AI Помощник\n\nЗадайте любой вопрос —\nперевод, советы, объяснения,\nвычисления и многое другое.\n\n💬 Напишите вопрос...\n\n💡 Остаётесь в разделе —\nзадавайте сколько угодно",
        "ar":"🤖 مساعد AI\n\nاسألني أي شيء —\nترجمة، نصائح، شرح،\nحسابات وأكثر.\n\n💬 اكتب سؤالك...\n\n💡 ستبقى في هذا القسم",
        "tr":"🤖 AI Asistan\n\nHerhangi bir soru sorun —\nçeviri, tavsiye, açıklama,\nhesaplama ve daha fazlası.\n\n💬 Sorunuzu yazın...\n\n💡 Bu bölümde kalırsınız",
        "es":"🤖 Asistente AI\n\nHazme cualquier pregunta —\ntraducción, consejos, cálculos.\n\n💬 Escribe tu pregunta...\n\n💡 Te quedas en esta sección",
        "hi":"🤖 AI सहायक\n\nकुछ भी पूछें —\nअनुवाद, सलाह, गणना।\n\n💬 प्रश्न लिखें...\n\n💡 इस अनुभाग में रहते हैं"
    },
    "sec_settings": {
        "uz":"⚙️ Sozlamalar\n\nTilni o'zgartirmoqchimisiz?\nQuyidagi tillardan birini tanlang 👇",
        "en":"⚙️ Settings\n\nWant to change the language?\nChoose a language below 👇",
        "ru":"⚙️ Настройки\n\nХотите изменить язык?\nВыберите язык ниже 👇",
        "ar":"⚙️ الإعدادات\n\nتريد تغيير اللغة؟\nاختر أدناه 👇",
        "tr":"⚙️ Ayarlar\n\nDil değiştirmek ister misiniz?\nAşağıdan seçin 👇",
        "es":"⚙️ Ajustes\n\n¿Cambiar idioma?\nElige abajo 👇",
        "hi":"⚙️ सेटिंग्स\n\nभाषा बदलनी है?\nनीचे चुनें 👇",
    },
    "sec_profile": {
        "uz":"👤 Mening profilim",
        "en":"👤 My Profile",
        "ru":"👤 Мой профиль",
        "ar":"👤 ملفي",
        "tr":"👤 Profilim",
        "es":"👤 Mi Perfil",
        "hi":"👤 मेरी प्रोफाइल"},
    "p_name": {
        "uz":"Ism",
        "en":"Name",
        "ru":"Имя",
        "ar":"الاسم",
        "tr":"Ad",
        "es":"Nombre",
        "hi":"नाम"},
    "p_city": {
        "uz":"Shahar",
        "en":"City",
        "ru":"Город",
        "ar":"المدينة",
        "tr":"Şehir",
        "es":"Ciudad",
        "hi":"शहर"},
    "p_joined": {
        "uz":"Qo'shilgan",
        "en":"Joined",
        "ru":"Присоединился",
        "ar":"انضم",
        "tr":"Katıldı",
        "es":"Unido",
        "hi":"शामिल"},
    "p_activity": {
        "uz":"Faollik",
        "en":"Activity",
        "ru":"Активность",
        "ar":"النشاط",
        "tr":"Aktivite",
        "es":"Actividad",
        "hi":"गतिविधि"},
    "p_expenses": {
        "uz":"Xarajatlar",
        "en":"Expenses",
        "ru":"Расходы",
        "ar":"المصروفات",
        "tr":"Harcamalar",
        "es":"Gastos",
        "hi":"खर्च"},
    "p_tasks": {
        "uz":"Vazifalar",
        "en":"Tasks",
        "ru":"Задачи",
        "ar":"المهام",
        "tr":"Görevler",
        "es":"Tareas",
        "hi":"कार्य"},
    "p_reminders":{
        "uz":"Eslatmalar",
        "en":"Reminders",
        "ru":"Напоминания",
        "ar":"التذكيرات",
        "tr":"Hatırlatıcılar",
        "es":"Recordatorios",
        "hi":"अनुस्मारक"},
    "p_warnings": {
        "uz":"Ogohlantirishlar",
        "en":"Warnings",
        "ru":"Предупреждения",
        "ar":"التحذيرات",
        "tr":"Uyarılar",
        "es":"Advertencias",
        "hi":"चेतावनियां"},
    "p_edit_name":{
        "uz":"✏️ Ismni o'zgartirish",
        "en":"✏️ Edit name",
        "ru":"✏️ Изменить имя",
        "ar":"✏️ تعديل الاسم",
        "tr":"✏️ Adı düzenle",
        "es":"✏️ Editar nombre",
        "hi":"✏️ नाम संपादित"},
    "p_edit_city":{
        "uz":"📍 Shaharni o'zgartirish",
        "en":"📍 Edit city",
        "ru":"📍 Изменить город",
        "ar":"📍 تعديل المدينة",
        "tr":"📍 Şehri düzenle",
        "es":"📍 Editar ciudad",
        "hi":"📍 शहर संपादित"}, }
def t(key, lang):
    # Custom matnlarni tekshiramiz
    try:
        settings = load_settings()
        custom = settings.get("custom_section_texts", {})
        # sec_ prefixi bor bo'lsa tekshiramiz
        sec_key = key.replace("sec_", "") if key.startswith("sec_") else key
        if sec_key in custom and lang in custom[sec_key]:
            return custom[sec_key][lang]
    except:
        pass
    d = TR.get(key,{})
    return d.get(lang, d.get("en",""))

BACK_TEXTS = set(TR["back"].values())
ACTIONS    = ["expense","plan","reminder","currency","weather","ai","profile","admin","settings"]
CURRENCY_TEMPLATE_TEXTS = {
    "uz": "▪ Valyuta shablonlari",
    "en": "▪ Currency templates",
    "ru": "▪ Шаблоны валют",
    "ar": "▪ قوالب العملات",
    "tr": "▪ Para şablonları",
    "es": "▪ Plantillas de moneda",
    "hi": "▪ मुद्रा टेम्पलेट",
}

def get_action(text, lang):
    # Avval custom nomlarni tekshiramiz
    sett   = load_settings()
    custom = sett.get("custom_section_texts", {})
    btn_keys = ["btn_expense","btn_plan","btn_reminder","btn_currency",
                "btn_weather","btn_ai","btn_profile","btn_admin","btn_settings"]
    for i, key in enumerate(btn_keys):
        custom_name = custom.get(key, {}).get(lang, "")
        if custom_name and text == custom_name and i < len(ACTIONS):
            return ACTIONS[i]
    # Standart nomlarni tekshiramiz
    menu = TR["menu"].get(lang, [])
    for i, item in enumerate(menu):
        if text == item and i < len(ACTIONS):
            return ACTIONS[i]
    return None


# ============================================================
# SHAHAR VA VALYUTA
# ============================================================
CITY_MAP = {
    "toshkent":"Tashkent","toshkend":"Tashkent","ташкент":"Tashkent",
    "samarqand":"Samarkand","самарканд":"Samarkand","buxoro":"Bukhara","бухара":"Bukhara",
    "namangan":"Namangan","andijon":"Andijan","farg'ona":"Fergana","fargona":"Fergana",
    "qarshi":"Karshi","termiz":"Termez","nukus":"Nukus","urganch":"Urgench",
    "moskva":"Moscow","москва":"Moscow","موسكو":"Moscow",
    "paris":"Paris","باريس":"Paris","berlin":"Berlin","madrid":"Madrid","مدريد":"Madrid",
    "dubai":"Dubai","дубай":"Dubai","dubay":"Dubai","دبي":"Dubai",
    "istanbul":"Istanbul","إسطنبول":"Istanbul","ankara":"Ankara",
    "delhi":"Delhi","دلهي":"Delhi","mumbai":"Mumbai",
    "beijing":"Beijing","بكين":"Beijing","tokyo":"Tokyo","طوكيو":"Tokyo",
    "cairo":"Cairo","قاهرة":"Cairo","قاهره":"Cairo",
    "makka":"Mecca","مكة":"Mecca","مكه":"Mecca","madina":"Medina","المدينة":"Medina",
    "riyadh":"Riyadh","الرياض":"Riyadh",
    "rossiya":"Moscow","россия":"Moscow","russia":"Moscow",
    "france":"Paris","germany":"Berlin","spain":"Madrid",
    "turkey":"Istanbul","india":"Delhi","china":"Beijing","japan":"Tokyo","egypt":"Cairo",
}

def normalize_city(c):
    return CITY_MAP.get(c.lower().strip(), c.strip())

CURRENCY_MAP = {
    "dollar":"USD","dollarlar":"USD","som":"UZS","so'm":"UZS","soum":"UZS",
    "euro":"EUR","yevro":"EUR","funt":"GBP","yuan":"CNY","yen":"JPY",
    "rubl":"RUB","ruble":"RUB","tenge":"KZT","lira":"TRY","dirham":"AED",
    "riyal":"SAR","rupiya":"INR","won":"KRW","frank":"CHF",
    "rossiya puli":"RUB","america puli":"USD","xitoy puli":"CNY","yaponiya puli":"JPY",
    "hindiston puli":"INR","turkiya puli":"TRY","ingliz puli":"GBP",
    "dollars":"USD","pound":"GBP","euros":"EUR","ruble":"RUB","rupee":"INR",
    "russian money":"RUB","american money":"USD","chinese money":"CNY","british money":"GBP",
    "доллар":"USD","доллары":"USD","фунт":"GBP","евро":"EUR","юань":"CNY","иена":"JPY",
    "рубль":"RUB","рубли":"RUB","тенге":"KZT","лира":"TRY","дирхам":"AED","риял":"SAR",
    "рупия":"INR","сум":"UZS","российские деньги":"RUB","американские деньги":"USD",
    "دولار":"USD","يورو":"EUR","جنيه":"GBP","يوان":"CNY","روبل":"RUB",
    "ليرة":"TRY","درهم":"AED","ريال":"SAR","روبية":"INR",
    "dolar":"USD","sterlin":"GBP","dirhem":"AED",
    "dólar":"USD","dólares":"USD","libra":"GBP","rublo":"RUB","rupia":"INR",
    "डॉलर":"USD","यूरो":"EUR","पाउंड":"GBP","रूबल":"RUB","रुपया":"INR",
}
POPULAR = ["UZS","USD","EUR","RUB","TRY","AED","GBP","CNY","JPY","KZT","SAR","INR"]


def parse_amount(s):
    if s is None:
        return None
    s = str(s).strip().lower()

    # Arab raqamlarini oddiy raqamlarga o'girish
    arabic_nums = {'٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'}
    for ar, en in arabic_nums.items():
        s = s.replace(ar, en)

    # Hind raqamlari
    hindi_nums = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
    for hi, en in hindi_nums.items():
        s = s.replace(hi, en)

    s = s.replace(",", "").replace(" ", "")
    # ... qolgan kod

    multipliers = {
        "ming": 1000, "тысяча": 1000, "тысяч": 1000, "thousand": 1000, "bin": 1000,
        "ألف": 1000, "mil": 1000, "हजार": 1000, "k": 1000, "हज़ार": 1000, "हजार": 1000,
        "million": 1000000, "mln": 1000000, "млн": 1000000, "миллион": 1000000,
        "milyon": 1000000, "millón": 1000000, "millones": 1000000, "مليون": 1000000,
        "मिलियन": 1000000, "लाख": 100000, "m": 1000000,
        "milliard": 1000000000, "mlrd": 1000000000, "миллиард": 1000000000, "млрд": 1000000000,
        "milyar": 1000000000, "مليار": 1000000000, "करोड़": 10000000, "अरब": 1000000000,
    }

    for word, mult in multipliers.items():
        if s.endswith(word):
            num_str = s[:-len(word)].strip()
            try:
                return float(num_str) * mult
            except:
                pass
        if s.startswith(word):
            num_str = s[len(word):].strip()
            try:
                return float(num_str) * mult
            except:
                pass
    try:
        return float(s)
    except:
        return None



def normalize_currency(c):
    return CURRENCY_MAP.get(c.lower().strip(), c.upper().strip())

# ============================================================
# MA'LUMOTLAR
# ============================================================
# Foydalanuvchi ma'lumotlari endi SQLite'da (database.py).
# get_user / update_user / get_all_users — database.py dan import qilingan.
# load_data() — eski kod (schedulerlar) bilan moslik uchun SQLite'dan
# {str(uid): user} ko'rinishidagi lug'at qaytaradi.
def load_data():
    return {str(u["uid"]): u for u in get_all_users()}

def load_settings():
    default = {
        "welcome_text":   {l:"" for l in LANGUAGES},
        "oferta_text":    {l:"" for l in LANGUAGES},
        "donation_text": {
            "uz":f"☕ Botni qo'llab-quvvatlang!\n📩 {ADMIN_USERNAME}",
            "en":f"☕ Support the bot!\n📩 {ADMIN_USERNAME}",
            "ru":f"☕ Поддержите бота!\n📩 {ADMIN_USERNAME}",
            "ar":f"☕ ادعم البوت!\n📩 {ADMIN_USERNAME}",
            "tr":f"☕ Botu destekleyin!\n📩 {ADMIN_USERNAME}",
            "es":f"☕ ¡Apoya el bot!\n📩 {ADMIN_USERNAME}",
            "hi":f"☕ बॉट का समर्थन करें!\n📩 {ADMIN_USERNAME}"
        },
        "required_channels":[],
        "banned_words":["terror","bomba","наркотик","убью","drug","kill","bomb","porno","xxx"],
        "motivational_quotes":{
            "uz":["Har bir yangi kun — yangi imkoniyat! 🌟","Maqsadingga qadam tashla! 💪","Kichik qadamlar katta natijalarga! 🚀"],
            "en":["Every new day is a new opportunity! 🌟","Take a step toward your goal! 💪","Small steps lead to great results! 🚀"],
            "ru":["Каждый день — новая возможность! 🌟","Шаг к цели! 💪","Маленькие шаги — великие результаты! 🚀"],
            "ar":["كل يوم فرصة جديدة! 🌟","خطوة نحو هدفك! 💪","خطوات صغيرة نتائج عظيمة! 🚀"],
            "tr":["Her gün yeni fırsat! 🌟","Hedefe adım at! 💪","Küçük adımlar büyük sonuçlar! 🚀"],
            "es":["¡Cada día es una oportunidad! 🌟","¡Un paso hacia tu meta! 💪","¡Pequeños pasos grandes resultados! 🚀"],
            "hi":["हर दिन नया अवसर! 🌟","लक्ष्य की ओर कदम! 💪","छोटे कदम बड़े परिणाम! 🚀"],
        },
        "quote_time":"08:00","quote_enabled":True,
        "weekly_report_enabled":True,
        "spam_limit":20,"spam_seconds":10,
        "scheduled_ads":[],
    }
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE,"r",encoding="utf-8") as f:
            saved = json.load(f)
            for k,v in saved.items():
                if isinstance(v,dict) and isinstance(default.get(k),dict):
                    default[k].update(v)
                else:
                    default[k] = v
    return default

def save_settings(s):
    with open(SETTINGS_FILE,"w",encoding="utf-8") as f:
        json.dump(s,f,ensure_ascii=False,indent=2)

DEFAULT_OFERTA = {
    "uz":"📋 Foydalanish shartlari\n\nStart Daily botidan foydalanish uchun:\n\n✅ Xizmatlar: xarajat kuzatish, kunlik reja, eslatmalar, valyuta, ob-havo, AI yordamchi.\n\n❌ Taqiqlangan:\n▪️ Spam yuborish\n▪️ Zo'ravonlik va terrorchilik\n▪️ Diniy tahqir va kamsitish\n▪️ Axloqsiz kontent\n▪️ Giyohvandlik va qurol reklama\n▪️ Firibgarlik\n\n⚠️ Ogohlantirish tizimi:\n▪️ 1-3 ogohlantirish\n▪️ 4-qoidabuzarlik — avtomatik blok\n\n📩 Murojaat: @Rustamjonoff1",
    "en":"📋 Terms of Use\n\nStart Daily bot terms:\n\n✅ Services: expense tracking, daily planning, reminders, times, currency, weather, AI assistant.\n\n❌ Prohibited:\n▪️ Spam\n▪️ Violence & terrorism\n▪️ Religious insults & discrimination\n▪️ Immoral content\n▪️ Drug & weapon advertising\n▪️ Fraud\n\n⚠️ Warning system:\n▪️ 1-3 warnings\n▪️ 4th violation — auto block\n\n📩 Contact: @Rustamjonoff1",
    "ru":"📋 Условия использования\n\nПравила бота Start Daily:\n\n✅ Услуги: расходы, план, напоминания, намаз, валюта, погода, AI.\n\n❌ Запрещено:\n▪️ Спам\n▪️ Насилие и терроризм\n▪️ Оскорбления и дискриминация\n▪️ Аморальный контент\n▪️ Реклама наркотиков и оружия\n▪️ Мошенничество\n\n⚠️ Предупреждения:\n▪️ 1-3 предупреждения\n▪️ 4-е — автоблокировка\n\n📩 @Rustamjonoff1",
    "ar":"📋 شروط الاستخدام\n\nشروط بوت Start Daily:\n\n✅ الخدمات: مصروفات، خطة، تذكيرات، صلاة، عملة، طقس، AI.\n\n❌ محظور:\n▪️ الرسائل المزعجة\n▪️ العنف والإرهاب\n▪️ الإهانات الدينية\n▪️ المحتوى غير الأخلاقي\n\n⚠️ التحذيرات:\n▪️ 1-3 تحذيرات\n▪️ الرابع — حظر\n\n📩 @Rustamjonoff1",
    "tr":"📋 Kullanım Koşulları\n\nStart Daily bot kuralları:\n\n✅ Hizmetler: harcamalar, plan, hatırlatıcılar, namaz, döviz, hava, AI.\n\n❌ Yasak:\n▪️ Spam\n▪️ Şiddet ve terör\n▪️ Dini hakaret\n▪️ Ahlaka aykırı içerik\n\n⚠️ Uyarılar:\n▪️ 1-3 uyarı\n▪️ 4. — engel\n\n📩 @Rustamjonoff1",
    "es":"📋 Términos de Uso\n\nReglas del bot Start Daily:\n\n✅ Servicios: gastos, plan, recordatorios, oración, moneda, clima, AI.\n\n❌ Prohibido:\n▪️ Spam\n▪️ Violencia y terrorismo\n▪️ Insultos religiosos\n▪️ Contenido inmoral\n\n⚠️ Advertencias:\n▪️ 1-3 advertencias\n▪️ 4a — bloqueo\n\n📩 @Rustamjonoff1",
    "hi":"📋 उपयोग की शर्तें\n\nStart Daily बॉट के नियम:\n\n✅ सेवाएं: खर्च, योजना, अनुस्मारक, नमाज़, मुद्रा, मौसम, AI.\n\n❌ प्रतिबंधित:\n▪️ स्पैम\n▪️ हिंसा और आतंकवाद\n▪️ धार्मिक अपमान\n▪️ अनैतिक सामग्री\n\n⚠️ चेतावनियां:\n▪️ 1-3 चेतावनियां\n▪️ 4वां — ब्लॉक\n\n📩 @Rustamjonoff1",
}

# ============================================================
# KLAVIATURALAR
# ============================================================
def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name,callback_data=f"lang_{code}")]
        for code,name in LANGUAGES.items()
    ])

def menu_kb(lang):
    sett = load_settings()
    custom = sett.get("custom_section_texts", {})

    def gbtn(key, default):
        return custom.get(key, {}).get(lang, default)

    default_items = TR["menu"][lang]
    btn_keys = ["btn_expense", "btn_plan", "btn_reminder", "btn_currency",
                "btn_weather", "btn_ai", "btn_profile", "btn_admin", "btn_settings"]
    items = [gbtn(btn_keys[i], default_items[i]) for i in range(len(default_items))]

    kb = []
    for i in range(0,len(items)-1,2):
        kb.append([KeyboardButton(text=items[i]),KeyboardButton(text=items[i+1])])
    if len(items)%2:
        kb.append([KeyboardButton(text=items[-1])])
    # Yangi tugmalar
    tariff_btn_default = {"uz": "💎 Tariflar", "en": "💎 Tariffs", "ru": "💎 Тарифы", "ar": "💎 الباقات",
                          "tr": "💎 Tarifler", "es": "💎 Tarifas", "hi": "💎 टैरिफ"}
    referral_btn_default = {"uz": "🎁 Referal", "en": "🎁 Referral", "ru": "🎁 Реферал", "ar": "🎁 الإحالة",
                            "tr": "🎁 Referans", "es": "🎁 Referido", "hi": "🎁 रेफरल"}
    balance_btn_default = {"uz": "💰 Balans", "en": "💰 Balance", "ru": "💰 Баланс", "ar": "💰 الرصيد", "tr": "💰 Bakiye",
                           "es": "💰 Saldo", "hi": "💰 बैلेंس"}

    tariff_text = gbtn("btn_tariffs", tariff_btn_default.get(lang, "💎 Tariffs"))
    referral_text = gbtn("btn_referral", referral_btn_default.get(lang, "🎁 Referral"))
    balance_text = gbtn("btn_balance", balance_btn_default.get(lang, "💰 Balance"))

    kb.append([
        KeyboardButton(text=tariff_text),
        KeyboardButton(text=referral_text),
    ])
    kb.append([
        KeyboardButton(text=balance_text),
    ])

    return ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True)
def back_kb(lang):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t("back",lang))]],resize_keyboard=True)
def currency_kb(lang):
    template_btn = {
        "uz": "▪ Valyuta shablonlari",
        "en": "▪ Currency templates",
        "ru": "▪ Шаблоны валют",
        "ar": "▪ قوالب العملات",
        "tr": "▪ Para şablonları",
        "es": "▪ Plantillas de moneda",
        "hi": "▪ मुद्रा टेम्पलेट",
    }
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=template_btn.get(lang, "▪ Currency templates"))],
        [KeyboardButton(text=t("back", lang))],
    ], resize_keyboard=True)
def oferta_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("oferta_accept",lang),callback_data="accept_oferta")]
    ])

def sub_kb(channels,lang):
    btns = [[InlineKeyboardButton(text=f"📢 {ch['name']}",url=ch["url"])] for ch in channels]
    btns.append([InlineKeyboardButton(text=t("check_sub",lang),callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=btns)

# ============================================================
# FSM
# ============================================================
class S(StatesGroup):
    profile_name  = State()
    profile_city  = State()
    expense       = State()
    plan          = State()
    plan_edit     = State()
    reminder      = State()
    reminder_edit = State()
    weather       = State()
    currency      = State()
    ai_chat       = State()
    balance_amount = State()
    balance_check = State()
# ============================================================
# YORDAMCHILAR
# ============================================================
def is_admin(uid): return uid == ADMIN_ID

async def check_sub(uid, lang):
    settings = load_settings()
    channels = settings.get("required_channels",[])
    if not channels: return True,[]
    not_sub  = []
    for ch in channels:
        ch_langs = ch.get("langs",[])
        if ch_langs and lang not in ch_langs: continue
        try:
            m = await bot.get_chat_member(ch["id"],uid)
            if m.status in ["left","kicked"]: not_sub.append(ch)
        except: pass
    return len(not_sub)==0, not_sub

async def check_spam(uid):
    settings = load_settings()
    limit    = settings.get("spam_limit",20)
    secs     = settings.get("spam_seconds",10)
    now      = datetime.now().timestamp()
    times    = [x for x in user_msg_times[uid] if now-x<secs]
    times.append(now)
    user_msg_times[uid] = times
    return len(times) >= limit

async def check_banned(text):
    settings = load_settings()
    tl       = text.lower()
    return any(w.lower() in tl for w in settings.get("banned_words",[]))

async def send_warning(uid, lang):
    user     = get_user(uid)
    warnings = user.get("warnings",0)+1
    update_user(uid,{"warnings":warnings})
    if warnings >= 4:
        update_user(uid,{"blocked":True})
        await bot.send_message(uid, t("blocked",lang))
        await bot.send_message(ADMIN_ID,
            f"🚫 Auto blocked!\nID: {uid}\n@{user.get('username','')}\n{user.get('name','')}")
    else:
        left = 3-warnings
        msg  = t("warning_msg",lang).replace("{n}",str(warnings)).replace("{left}",str(left))
        await bot.send_message(uid, msg)
        await bot.send_message(ADMIN_ID,
            f"⚠️ Warning {warnings}/3\nID: {uid}\n@{user.get('username','')}")

# ============================================================
# BOT BUYRUQLARI
# ============================================================
async def set_commands():
    cmds = [
        BotCommand(command="start",     description="Start the bot"),
        BotCommand(command="help",      description="Help"),
        BotCommand(command="settings",  description="Settings"),
        BotCommand(command="profile",   description="My profile"),
        BotCommand(command="oferta",    description="Terms of use"),
        BotCommand(command="expenses",  description="Expenses"),
        BotCommand(command="plan",      description="Daily plan"),
        BotCommand(command="reminders", description="Reminders"),
        BotCommand(command="weather",   description="Weather"),
        BotCommand(command="currency",  description="Currency"),
        BotCommand(command="ai",        description="AI Assistant"),
        BotCommand(command="tariffs",   description="Tariffs"),
        BotCommand(command="balance",   description="Balance"),
        BotCommand(command="referral",  description="Referral"),
    ]
    await bot.set_my_commands(cmds, scope=BotCommandScopeDefault())

# ============================================================
# START VA TIL
# ============================================================
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    uid  = message.from_user.id

    # Referal tekshirish
    args        = message.text.split()
    start_param = args[1] if len(args) > 1 else ""
    if start_param.startswith("ref_"):
            from referral import check_referral_start
            await check_referral_start(uid, start_param, bot)
            import sys
            main_module = sys.modules.get('__main__')
            if main_module and hasattr(main_module, '_check_referral_start'):
                await main_module._check_referral_start(uid, start_param, bot)


    user = get_user(uid)
    lang = user.get("lang","en")

    if user.get("blocked"):
        await message.answer(t("blocked",lang))
        return

    if not user.get("name"):
        tg_lang = message.from_user.language_code or "en"
        lang    = TG_LANG_MAP.get(tg_lang,"en")
        update_user(uid,{"lang":lang})
        await message.answer(t("choose_lang",lang), reply_markup=lang_kb())
        return

    ok,not_sub = await check_sub(uid,lang)
    if not ok:
        await message.answer(t("sub_required",lang), reply_markup=sub_kb(not_sub,lang))
        return

    settings = load_settings()
    wt = settings["welcome_text"].get(lang,"").strip()
    wc = wt if wt else t("welcome",lang).replace("{name}",user.get("name",""))
    await message.answer(wc, reply_markup=menu_kb(lang))

@dp.callback_query(F.data.startswith("lang_"))
async def cb_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    uid  = callback.from_user.id
    update_user(uid, {"lang": lang})
    await callback.message.delete()
    user = get_user(uid)
    if not user.get("name"):
        await state.set_state(S.profile_name)
        await callback.message.answer(t("enter_name", lang))
        return
    ok, not_sub = await check_sub(uid, lang)
    if not ok:
        await state.clear()
        await callback.message.answer(t("sub_required", lang), reply_markup=sub_kb(not_sub, lang))
        return
    await state.clear()
    settings = load_settings()
    wt = settings["welcome_text"].get(lang, "").strip()
    wc = wt if wt else t("welcome", lang).replace("{name}", user.get("name", ""))
    await callback.message.answer(wc, reply_markup=menu_kb(lang))


@dp.callback_query(F.data=="check_sub")
async def cb_check_sub(callback: types.CallbackQuery):
    uid  = callback.from_user.id
    user = get_user(uid)
    lang = user.get("lang","en")
    ok,not_sub = await check_sub(uid,lang)
    if ok:
        await callback.message.delete()
        settings = load_settings()
        of_raw_data = settings.get("oferta_text", {})
        of_raw = of_raw_data.get(lang, "") if isinstance(of_raw_data, dict) else ""
        if isinstance(of_raw,str) and of_raw.strip():
            oferta_text = of_raw
        else:
            oferta_text = DEFAULT_OFERTA.get(lang,DEFAULT_OFERTA["en"])
        await callback.message.answer(oferta_text, reply_markup=oferta_kb(lang))
    else:
        await callback.answer(t("sub_required",lang)[:200],show_alert=True)

@dp.callback_query(F.data=="accept_oferta")
async def cb_accept(callback: types.CallbackQuery):
    uid  = callback.from_user.id
    user = get_user(uid)
    lang = user.get("lang","en")
    update_user(uid,{"oferta_accepted":True})
    await callback.message.edit_text(t("oferta_ok",lang))
    settings = load_settings()
    wt = settings["welcome_text"].get(lang,"").strip()
    wc = wt if wt else t("welcome",lang).replace("{name}",user.get("name",""))
    await callback.message.answer(wc, reply_markup=menu_kb(lang))

# ============================================================
# BUYRUQLAR
# ============================================================
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    helps = {
        "uz":f"📖 Yordam\n\n💸 Tushlik 25000 UZS\n📅 09:00 Kitob o'qish\n⏰ 14:30 Dori ichish\n🕌 Toshkent\n💱 100 dollar so'm\n🌤 Toshkent\n🤖 Istalgan savol\n\n📩 {ADMIN_USERNAME}",
        "en":f"📖 Help\n\n💸 Lunch 25 USD\n📅 09:00 Read book\n⏰ 14:30 Take medicine\n🕌 London\n💱 100 USD UZS\n🌤 London\n🤖 Any question\n\n📩 {ADMIN_USERNAME}",
        "ru":f"📖 Помощь\n\n💸 Обед 500 RUB\n📅 09:00 Читать\n⏰ 14:30 Лекарство\n🕌 Москва\n💱 100 доллар рубль\n🌤 Москва\n🤖 Любой вопрос\n\n📩 {ADMIN_USERNAME}",
        "ar":f"📖 مساعدة\n\n💸 غداء 25 USD\n📅 09:00 قراءة\n⏰ 14:30 دواء\n🕌 القاهرة\n💱 100 USD SAR\n🌤 القاهرة\n🤖 أي سؤال\n\n📩 {ADMIN_USERNAME}",
        "tr":f"📖 Yardım\n\n💸 Öğle 25 USD\n📅 09:00 Kitap\n⏰ 14:30 İlaç\n🕌 Istanbul\n💱 100 dolar lira\n🌤 Istanbul\n🤖 Herhangi soru\n\n📩 {ADMIN_USERNAME}",
        "es":f"📖 Ayuda\n\n💸 Almuerzo 25 USD\n📅 09:00 Leer\n⏰ 14:30 Medicina\n🕌 Madrid\n💱 100 USD EUR\n🌤 Madrid\n🤖 Cualquier pregunta\n\n📩 {ADMIN_USERNAME}",
        "hi":f"📖 सहायता\n\n💸 दोपहर 25 USD\n📅 09:00 पढ़ें\n⏰ 14:30 दवा\n🕌 Delhi\n💱 100 USD INR\n🌤 Delhi\n🤖 कोई भी प्रश्न\n\n📩 {ADMIN_USERNAME}",
    }
    await message.answer(helps.get(lang,helps["en"]))

@dp.message(Command("settings"))
async def cmd_settings(message: types.Message, state: FSMContext):
    await state.clear()
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    await message.answer(t("sec_settings",lang), reply_markup=lang_kb())

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    await show_profile(message,user,lang)

@dp.message(Command("oferta"))
async def cmd_oferta(message: types.Message):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    settings = load_settings()
    of_raw_data = settings.get("oferta_text", {})
    of_raw = of_raw_data.get(lang, "") if isinstance(of_raw_data, dict) else ""
    oferta_text = (of_raw.strip() if isinstance(of_raw,str) and of_raw.strip()
                   else DEFAULT_OFERTA.get(lang,DEFAULT_OFERTA["en"]))
    await message.answer(oferta_text, reply_markup=oferta_kb(lang))

@dp.message(Command("expenses"))
async def cmd_expenses(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    await state.set_state(S.expense)
    await show_expense_menu(message,user,lang)

@dp.message(Command("plan"))
async def cmd_plan(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    await state.set_state(S.plan)
    await show_plan_menu(message,user,lang)

@dp.message(Command("reminders"))
async def cmd_reminders(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    await state.set_state(S.reminder)
    await show_reminder_menu(message,user,lang)

@dp.message(Command("weather"))
async def cmd_weather_c(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    await state.set_state(S.weather)
    await message.answer(t("sec_weather",lang), reply_markup=back_kb(lang))

@dp.message(Command("currency"))
async def cmd_currency_c(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    await state.set_state(S.currency)
    await message.answer(t("sec_currency",lang), reply_markup=back_kb(lang))


@dp.message(Command("ai"))
async def cmd_ai_c(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("lang","en")
    await state.set_state(S.ai_chat)
    await message.answer(t("sec_ai",lang), reply_markup=back_kb(lang))
@dp.message(Command("tariffs"))
async def cmd_tariffs(message: types.Message):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    from tariffs import tariffs_kb, TARIFF_NAMES, TARIFF_FEATURES
    from database import check_subscription
    sub         = check_subscription(uid)
    tariff_name = TARIFF_NAMES.get(lang, TARIFF_NAMES["en"]).get(sub, sub)
    cur_plan    = {"uz":"Joriy tarifingiz","en":"Current plan","ru":"Ваш план","ar":"خطتك الحالية","tr":"Mevcut planınız","es":"Tu plan actual","hi":"आपकी योजना"}
    title       = {"uz":"💎 Tariflar","en":"💎 Tariffs","ru":"💎 Тарифы","ar":"💎 الباقات","tr":"💎 Tarifler","es":"💎 Tarifas","hi":"💎 टैरिफ"}
    await message.answer(
        f"{title.get(lang,'💎 Tariffs')}\n\n{cur_plan.get(lang,'')}: {tariff_name}",
        reply_markup=tariffs_kb(lang, uid)
    )

@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    from database import get_balance
    bal  = get_balance(uid)
    bal_text = {
        "uz": f"💰 Balansingiz: {bal:,} so'm",
        "en": f"💰 Your balance: {bal:,} UZS",
        "ru": f"💰 Ваш баланс: {bal:,} UZS",
        "ar": f"💰 رصيدك: {bal:,} UZS",
        "tr": f"💰 Bakiyeniz: {bal:,} UZS",
        "es": f"💰 Tu saldo: {bal:,} UZS",
        "hi": f"💰 आपका बैलेंस: {bal:,} UZS",
    }
    sett_b = load_settings()
    custom_b = sett_b.get("custom_section_texts", {})
    topup_text = custom_b.get("btn_topup", {}).get(lang, {"uz": "💳 Balansni to'ldirish", "en": "💳 Top up",
                                                          "ru": "💳 Пополнить", "ar": "💳 شحن", "tr": "💳 Yükle",
                                                          "es": "💳 Recargar", "hi": "💳 टॉप अप"}.get(lang, "💳 Top up"))

    topup_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=topup_text,
            callback_data="balance_topup"
        )
    ]])

    await message.answer(bal_text.get(lang, bal_text["en"]), reply_markup=topup_kb)

@dp.message(Command("referral"))
async def cmd_referral(message: types.Message):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    from referral import get_referral, REF_TEXTS, referral_kb
    ref           = get_referral(uid)
    ref_code      = ref.get("ref_code","")
    link          = f"https://t.me/Startdaily_bot?start=ref_{ref_code}"
    std_disc      = ref.get("discount_standard", 0)
    prem_disc     = ref.get("discount_premium", 0)
    no_disc       = {"uz":"Hozircha yo'q","en":"None yet","ru":"Пока нет","ar":"لا يوجد","tr":"Henüz yok","es":"Aún no","hi":"अभी नहीं"}
    disc_std_text  = f"{std_disc}%"  if std_disc  else no_disc.get(lang,"—")
    disc_prem_text = f"{prem_disc}%" if prem_disc else no_disc.get(lang,"—")
    carried        = ref.get("carried_refs", 0)
    carried_text   = f"\n{REF_TEXTS['carried_refs'].get(lang,'')}: {carried}" if carried > 0 else ""
    text_out = (
        f"{REF_TEXTS['title'].get(lang,'')}\n\n"
        f"{REF_TEXTS['your_link'].get(lang,'')}\n"
        f"`{link}`\n\n"
        f"{REF_TEXTS['your_stats'].get(lang,'')}\n"
        f"👥 {REF_TEXTS['total_refs'].get(lang,'')}: {ref.get('total_refs',0)}\n"
        f"📅 {REF_TEXTS['month_refs'].get(lang,'')}: {ref.get('month_refs',0)}"
        f"{carried_text}\n\n"
        f"⭐ {REF_TEXTS['discount_std'].get(lang,'')}: {disc_std_text}\n"
        f"💎 {REF_TEXTS['discount_prem'].get(lang,'')}: {disc_prem_text}"
    )
    await message.answer(text_out, reply_markup=referral_kb(lang), parse_mode="Markdown")


CURRENCY_TEMPLATE_TEXTS = {
    "uz": "▪ Valyuta shablonlari",
    "en": "▪ Currency templates",
    "ru": "▪ Шаблоны валют",
    "ar": "▪ قوالب العملات",
    "tr": "▪ Para şablonları",
    "es": "▪ Plantillas de moneda",
    "hi": "▪ मुद्रा टेम्पलेट",
}


@dp.message(F.text.in_(set(CURRENCY_TEMPLATE_TEXTS.values())))
async def currency_template_handler(message: types.Message):
    user = get_user(message.from_user.id)
    lang = user.get("lang", "en")
    await message.answer(t("sec_currency", lang), reply_markup=currency_kb(lang))
    templates = {
        "uz": (
"💱 Valyuta shablonlari\n\n🇺🇿 O'zbekiston: so'm | UZS\n\n🇺🇸 Amerika: dollar | USD\n\n🇷🇺 Rossiya: rubl | RUB\n\n🇪🇺 Yevropa: euro | EUR\n\n🇬🇧 Angliya: funt | GBP\n\n🇨🇳 Xitoy: yuan | CNY\n\n🇯🇵 Yaponiya: yen | JPY\n\n🇹🇷 Turkiya: lira | TRY\n\n🇦🇪 BAA: dirham | AED\n\n🇸🇦 Saudiya: riyal | SAR\n\n🇰🇿 Qozog'iston: tenge | KZT\n\n🇮🇳 Hindiston: rupiya | INR\n\n🇨🇭 Shveytsariya: frank | CHF\n\n🇰🇷 Koreya: won | KRW\n\n🇧🇷 Braziliya: real | BRL\n\n🇲🇽 Meksika: peso | MXN\n\n🇿🇦 Janubiy Afrika: rand | ZAR\n\n🇸🇬 Singapur: dollar | SGD\n\n🇭🇰 Gonkong: dollar | HKD\n\n🇳🇴 Norvegiya: krona | NOK\n\n🇸🇪 Shvetsiya: krona | SEK\n\n🇩🇰 Daniya: krona | DKK\n\n🇵🇱 Polsha: zloty | PLN\n\n🇨🇿 Chexiya: krona | CZK\n\n🇭🇺 Vengriya: forint | HUF\n\n🇷🇴 Ruminiya: leu | RON\n\n🇦🇿 Ozarbayjon: manat | AZN\n\n🇬🇪 Gruziya: lari | GEL\n\n🇺🇦 Ukraina: grivna | UAH\n\n🇧🇾 Belarus: rubl | BYN\n\n🇰🇬 Qirg'iziston: som | KGS\n\n🇹🇯 Tojikiston: somoni | TJS\n\n🇹🇲 Turkmaniston: manat | TMT\n\n🇲🇾 Malayziya: ringgit | MYR\n\n🇮🇩 Indoneziya: rupiya | IDR\n\n🇹🇭 Tailand: baht | THB\n\n🇵🇭 Filippin: peso | PHP\n\n🇻🇳 Vyetnam: dong | VND\n\n🇵🇰 Pokiston: rupiya | PKR\n\n🇧🇩 Bangladesh: taka | BDT\n\n🇪🇬 Misr: funt | EGP\n\n🇳🇬 Nigeriya: naira | NGN\n\n🇰🇪 Keniya: shilling | KES\n\n🇦🇷 Argentina: peso | ARS\n\n🇨🇱 Chili: peso | CLP\n\n🇨🇴 Kolumbiya: peso | COP\n\n🇵🇪 Peru: sol | PEN\n\n🇮🇱 Isroil: shekel | ILS\n\n🇶🇦 Qatar: riyal | QAR\n\n🇰🇼 Quvayt: dinar | KWD\n\n🇧🇭 Bahrayn: dinar | BHD\n\n🇴🇲 Ummon: riyal | OMR\n\n🇳🇿 Yangi Zelandiya: dollar | NZD\n\n🇦🇺 Avstraliya: dollar | AUD\n\n🇨🇦 Kanada: dollar | CAD\n\n📝 Misol: 100 dollar so'm"
),

        "en": (
            "💱 Currency Templates\n\n🇺🇿 Uzbekistan: som | UZS\n\n🇺🇸 United States: dollar | USD\n\n🇷🇺 Russia: ruble | RUB\n\n🇪🇺 Europe: euro | EUR\n\n🇬🇧 United Kingdom: pound | GBP\n\n🇨🇳 China: yuan | CNY\n\n🇯🇵 Japan: yen | JPY\n\n🇹🇷 Turkey: lira | TRY\n\n🇦🇪 UAE: dirham | AED\n\n🇸🇦 Saudi Arabia: riyal | SAR\n\n🇰🇿 Kazakhstan: tenge | KZT\n\n🇮🇳 India: rupee | INR\n\n🇨🇭 Switzerland: franc | CHF\n\n🇰🇷 South Korea: won | KRW\n\n🇧🇷 Brazil: real | BRL\n\n🇲🇽 Mexico: peso | MXN\n\n🇿🇦 South Africa: rand | ZAR\n\n🇸🇬 Singapore: dollar | SGD\n\n🇭🇰 Hong Kong: dollar | HKD\n\n🇳🇴 Norway: krone | NOK\n\n🇸🇪 Sweden: krona | SEK\n\n🇩🇰 Denmark: krone | DKK\n\n🇵🇱 Poland: zloty | PLN\n\n🇨🇿 Czech Republic: koruna | CZK\n\n🇭🇺 Hungary: forint | HUF\n\n🇷🇴 Romania: leu | RON\n\n🇦🇿 Azerbaijan: manat | AZN\n\n🇬🇪 Georgia: lari | GEL\n\n🇺🇦 Ukraine: hryvnia | UAH\n\n🇧🇾 Belarus: ruble | BYN\n\n🇰🇬 Kyrgyzstan: som | KGS\n\n🇹🇯 Tajikistan: somoni | TJS\n\n🇹🇲 Turkmenistan: manat | TMT\n\n🇲🇾 Malaysia: ringgit | MYR\n\n🇮🇩 Indonesia: rupiah | IDR\n\n🇹🇭 Thailand: baht | THB\n\n🇵🇭 Philippines: peso | PHP\n\n🇻🇳 Vietnam: dong | VND\n\n🇵🇰 Pakistan: rupee | PKR\n\n🇧🇩 Bangladesh: taka | BDT\n\n🇪🇬 Egypt: pound | EGP\n\n🇳🇬 Nigeria: naira | NGN\n\n🇰🇪 Kenya: shilling | KES\n\n🇦🇷 Argentina: peso | ARS\n\n🇨🇱 Chile: peso | CLP\n\n🇨🇴 Colombia: peso | COP\n\n🇵🇪 Peru: sol | PEN\n\n🇮🇱 Israel: shekel | ILS\n\n🇶🇦 Qatar: riyal | QAR\n\n🇰🇼 Kuwait: dinar | KWD\n\n🇧🇭 Bahrain: dinar | BHD\n\n🇴🇲 Oman: rial | OMR\n\n🇳🇿 New Zealand: dollar | NZD\n\n🇦🇺 Australia: dollar | AUD\n\n🇨🇦 Canada: dollar | CAD\n\n📝 Example: 100 USD UZS"
        ),

        "ru": (
"💱 Шаблоны валют\n\n🇺🇿 Узбекистан: сум | UZS\n\n🇺🇸 США: доллар | USD\n\n🇷🇺 Россия: рубль | RUB\n\n🇪🇺 Европа: евро | EUR\n\n🇬🇧 Великобритания: фунт | GBP\n\n🇨🇳 Китай: юань | CNY\n\n🇯🇵 Япония: иена | JPY\n\n🇹🇷 Турция: лира | TRY\n\n🇦🇪 ОАЭ: дирхам | AED\n\n🇸🇦 Саудовская Аравия: риял | SAR\n\n🇰🇿 Казахстан: тенге | KZT\n\n🇮🇳 Индия: рупия | INR\n\n🇨🇭 Швейцария: франк | CHF\n\n🇰🇷 Южная Корея: вона | KRW\n\n🇧🇷 Бразилия: реал | BRL\n\n🇲🇽 Мексика: песо | MXN\n\n🇿🇦 Южная Африка: рэнд | ZAR\n\n🇸🇬 Сингапур: доллар | SGD\n\n🇭🇰 Гонконг: доллар | HKD\n\n🇳🇴 Норвегия: крона | NOK\n\n🇸🇪 Швеция: крона | SEK\n\n🇩🇰 Дания: крона | DKK\n\n🇵🇱 Польша: злотый | PLN\n\n🇨🇿 Чехия: крона | CZK\n\n🇭🇺 Венгрия: форинт | HUF\n\n🇷🇴 Румыния: лей | RON\n\n🇦🇿 Азербайджан: манат | AZN\n\n🇬🇪 Грузия: лари | GEL\n\n🇺🇦 Украина: гривна | UAH\n\n🇧🇾 Беларусь: рубль | BYN\n\n🇰🇬 Кыргызстан: сом | KGS\n\n🇹🇯 Таджикистан: сомони | TJS\n\n🇹🇲 Туркменистан: манат | TMT\n\n🇲🇾 Малайзия: ринггит | MYR\n\n🇮🇩 Индонезия: рупия | IDR\n\n🇹🇭 Таиланд: бат | THB\n\n🇵🇭 Филиппины: песо | PHP\n\n🇻🇳 Вьетнам: донг | VND\n\n🇵🇰 Пакистан: рупия | PKR\n\n🇧🇩 Бангладеш: така | BDT\n\n🇪🇬 Египет: фунт | EGP\n\n🇳🇬 Нигерия: найра | NGN\n\n🇰🇪 Кения: шиллинг | KES\n\n🇦🇷 Аргентина: песо | ARS\n\n🇨🇱 Чили: песо | CLP\n\n🇨🇴 Колумбия: песо | COP\n\n🇵🇪 Перу: соль | PEN\n\n🇮🇱 Израиль: шекель | ILS\n\n🇶🇦 Катар: риял | QAR\n\n🇰🇼 Кувейт: динар | KWD\n\n🇧🇭 Бахрейн: динар | BHD\n\n🇴🇲 Оман: риял | OMR\n\n🇳🇿 Новая Зеландия: доллар | NZD\n\n🇦🇺 Австралия: доллар | AUD\n\n🇨🇦 Канада: доллар | CAD\n\n📝 Пример: 100 доллар рубль"
),
        "ar": (
            "💱 قوالب العملات\n\n🇺🇿 أوزبكستان: سوم | UZS\n\n🇺🇸 الولايات المتحدة: دولار | USD\n\n🇷🇺 روسيا: روبل | RUB\n\n🇪🇺 أوروبا: يورو | EUR\n\n🇬🇧 المملكة المتحدة: جنيه إسترليني | GBP\n\n🇨🇳 الصين: يوان | CNY\n\n🇯🇵 اليابان: ين | JPY\n\n🇹🇷 تركيا: ليرة | TRY\n\n🇦🇪 الإمارات العربية المتحدة: درهم | AED\n\n🇸🇦 المملكة العربية السعودية: ريال | SAR\n\n🇰🇿 كازاخستان: تنغه | KZT\n\n🇮🇳 الهند: روبية | INR\n\n🇨🇭 سويسرا: فرنك | CHF\n\n🇰🇷 كوريا الجنوبية: وون | KRW\n\n🇧🇷 البرازيل: ريال | BRL\n\n🇲🇽 المكسيك: بيزو | MXN\n\n🇿🇦 جنوب أفريقيا: راند | ZAR\n\n🇸🇬 سنغافورة: دولار | SGD\n\n🇭🇰 هونغ كونغ: دولار | HKD\n\n🇳🇴 النرويج: كرونة | NOK\n\n🇸🇪 السويد: كرونة | SEK\n\n🇩🇰 الدنمارك: كرونة | DKK\n\n🇵🇱 بولندا: زلوتي | PLN\n\n🇨🇿 التشيك: كرونة | CZK\n\n🇭🇺 المجر: فورنت | HUF\n\n🇷🇴 رومانيا: ليو | RON\n\n🇦🇿 أذربيجان: مانات | AZN\n\n🇬🇪 جورجيا: لاري | GEL\n\n🇺🇦 أوكرانيا: هريفنيا | UAH\n\n🇧🇾 بيلاروسيا: روبل | BYN\n\n🇰🇬 قيرغيزستان: سوم | KGS\n\n🇹🇯 طاجيكستان: سوموني | TJS\n\n🇹🇲 تركمانستان: مانات | TMT\n\n🇲🇾 ماليزيا: رينغيت | MYR\n\n🇮🇩 إندونيسيا: روبية | IDR\n\n🇹🇭 تايلاند: بات | THB\n\n🇵🇭 الفلبين: بيزو | PHP\n\n🇻🇳 فيتنام: دونغ | VND\n\n🇵🇰 باكستان: روبية | PKR\n\n🇧🇩 بنغلاديش: تاكا | BDT\n\n🇪🇬 مصر: جنيه | EGP\n\n🇳🇬 نيجيريا: نايرا | NGN\n\n🇰🇪 كينيا: شلن | KES\n\n🇦🇷 الأرجنتين: بيزو | ARS\n\n🇨🇱 تشيلي: بيزو | CLP\n\n🇨🇴 كولومبيا: بيزو | COP\n\n🇵🇪 بيرو: سول | PEN\n\n🇮🇱 إسرائيل: شيكل | ILS\n\n🇶🇦 قطر: ريال | QAR\n\n🇰🇼 الكويت: دينار | KWD\n\n🇧🇭 البحرين: دينار | BHD\n\n🇴🇲 عُمان: ريال | OMR\n\n🇳🇿 نيوزيلندا: دولار | NZD\n\n🇦🇺 أستراليا: دولار | AUD\n\n🇨🇦 كندا: دولار | CAD\n\n📝 مثال: 100 دولار ريال"
        ),

        "tr": (
            "💱 Para Şablonları\n\n🇺🇿 Özbekistan: som | UZS\n\n🇺🇸 Amerika Birleşik Devletleri: dolar | USD\n\n🇷🇺 Rusya: ruble | RUB\n\n🇪🇺 Avrupa: euro | EUR\n\n🇬🇧 Birleşik Krallık: sterlin | GBP\n\n🇨🇳 Çin: yuan | CNY\n\n🇯🇵 Japonya: yen | JPY\n\n🇹🇷 Türkiye: lira | TRY\n\n🇦🇪 Birleşik Arap Emirlikleri: dirhem | AED\n\n🇸🇦 Suudi Arabistan: riyal | SAR\n\n🇰🇿 Kazakistan: tenge | KZT\n\n🇮🇳 Hindistan: rupi | INR\n\n🇨🇭 İsviçre: frank | CHF\n\n🇰🇷 Güney Kore: won | KRW\n\n🇧🇷 Brezilya: real | BRL\n\n🇲🇽 Meksika: peso | MXN\n\n🇿🇦 Güney Afrika: rand | ZAR\n\n🇸🇬 Singapur: dolar | SGD\n\n🇭🇰 Hong Kong: dolar | HKD\n\n🇳🇴 Norveç: kron | NOK\n\n🇸🇪 İsveç: krona | SEK\n\n🇩🇰 Danimarka: kron | DKK\n\n🇵🇱 Polonya: zloti | PLN\n\n🇨🇿 Çekya: koruna | CZK\n\n🇭🇺 Macaristan: forint | HUF\n\n🇷🇴 Romanya: leu | RON\n\n🇦🇿 Azerbaycan: manat | AZN\n\n🇬🇪 Gürcistan: lari | GEL\n\n🇺🇦 Ukrayna: grivna | UAH\n\n🇧🇾 Belarus: ruble | BYN\n\n🇰🇬 Kırgızistan: som | KGS\n\n🇹🇯 Tacikistan: somoni | TJS\n\n🇹🇲 Türkmenistan: manat | TMT\n\n🇲🇾 Malezya: ringgit | MYR\n\n🇮🇩 Endonezya: rupi | IDR\n\n🇹🇭 Tayland: baht | THB\n\n🇵🇭 Filipinler: peso | PHP\n\n🇻🇳 Vietnam: dong | VND\n\n🇵🇰 Pakistan: rupi | PKR\n\n🇧🇩 Bangladeş: taka | BDT\n\n🇪🇬 Mısır: pound | EGP\n\n🇳🇬 Nijerya: naira | NGN\n\n🇰🇪 Kenya: şilin | KES\n\n🇦🇷 Arjantin: peso | ARS\n\n🇨🇱 Şili: peso | CLP\n\n🇨🇴 Kolombiya: peso | COP\n\n🇵🇪 Peru: sol | PEN\n\n🇮🇱 İsrail: şekel | ILS\n\n🇶🇦 Katar: riyal | QAR\n\n🇰🇼 Kuveyt: dinar | KWD\n\n🇧🇭 Bahreyn: dinar | BHD\n\n🇴🇲 Umman: riyal | OMR\n\n🇳🇿 Yeni Zelanda: dolar | NZD\n\n🇦🇺 Avustralya: dolar | AUD\n\n🇨🇦 Kanada: dolar | CAD\n\n📝 Örnek: 100 dolar lira"
        ),

            "es": (
                "💱 Plantillas de Moneda\n\n🇺🇿 Uzbekistán: som | UZS\n\n🇺🇸 EE.UU.: dólar | USD\n\n🇷🇺 Rusia: rublo | RUB\n\n🇪🇺 Europa: euro | EUR\n\n🇬🇧 Reino Unido: libra | GBP\n\n🇨🇳 China: yuan | CNY\n\n🇯🇵 Japón: yen | JPY\n\n🇹🇷 Turquía: lira | TRY\n\n🇦🇪 EAU: dírham | AED\n\n🇸🇦 Arabia Saudita: riyal | SAR\n\n🇰🇿 Kazajistán: tenge | KZT\n\n🇮🇳 India: rupia | INR\n\n🇨🇭 Suiza: franco | CHF\n\n🇰🇷 Corea: won | KRW\n\n🇧🇷 Brasil: real | BRL\n\n🇲🇽 México: peso | MXN\n\n🇿🇦 Sudáfrica: rand | ZAR\n\n🇸🇬 Singapur: dólar | SGD\n\n🇭🇰 Hong Kong: dólar | HKD\n\n🇳🇴 Noruega: corona | NOK\n\n🇸🇪 Suecia: corona | SEK\n\n🇩🇰 Dinamarca: corona | DKK\n\n🇵🇱 Polonia: zloty | PLN\n\n🇨🇿 Chequia: corona | CZK\n\n🇭🇺 Hungría: forint | HUF\n\n🇷🇴 Rumania: leu | RON\n\n🇦🇿 Azerbaiyán: manat | AZN\n\n🇬🇪 Georgia: lari | GEL\n\n🇺🇦 Ucrania: grivna | UAH\n\n🇧🇾 Bielorrusia: rublo | BYN\n\n🇰🇬 Kirguistán: som | KGS\n\n🇹🇯 Tayikistán: somoni | TJS\n\n🇹🇲 Turkmenistán: manat | TMT\n\n🇲🇾 Malasia: ringgit | MYR\n\n🇮🇩 Indonesia: rupia | IDR\n\n🇹🇭 Tailandia: baht | THB\n\n🇵🇭 Filipinas: peso | PHP\n\n🇻🇳 Vietnam: dong | VND\n\n🇵🇰 Pakistán: rupia | PKR\n\n🇧🇩 Bangladés: taka | BDT\n\n🇪🇬 Egipto: libra | EGP\n\n🇳🇬 Nigeria: naira | NGN\n\n🇰🇪 Kenia: chelín | KES\n\n🇦🇷 Argentina: peso | ARS\n\n🇨🇱 Chile: peso | CLP\n\n🇨🇴 Colombia: peso | COP\n\n🇵🇪 Perú: sol | PEN\n\n🇮🇱 Israel: shekel | ILS\n\n🇶🇦 Catar: riyal | QAR\n\n🇰🇼 Kuwait: dinar | KWD\n\n🇧🇭 Baréin: dinar | BHD\n\n🇴🇲 Omán: riyal | OMR\n\n🇳🇿 Nueva Zelanda: dólar | NZD\n\n🇦🇺 Australia: dólar | AUD\n\n🇨🇦 Canadá: dólar | CAD\n\n📝 Ejemplo: 100 dólares som"
            ),
            "hi": (
                "💱 मुद्रा टेम्पलेट\n\n🇺🇿 उज़्बेकिस्तान: सोम | UZS\n\n🇺🇸 अमेरिका: डॉलर | USD\n\n🇷🇺 रूस: रूबल | RUB\n\n🇪🇺 यूरोप: यूरो | EUR\n\n🇬🇧 यूनाइटेड किंगडम: पाउंड | GBP\n\n🇨🇳 चीन: युआन | CNY\n\n🇯🇵 जापान: येन | JPY\n\n🇹🇷 तुर्की: लीरा | TRY\n\n🇦🇪 यूएई: दिरहम | AED\n\n🇸🇦 सऊदी अरब: रियाल | SAR\n\n🇰🇿 कज़ाखस्तान: टेंगे | KZT\n\n🇮🇳 भारत: रुपया | INR\n\n🇨🇭 स्विट्ज़रलैंड: फ्रैंक | CHF\n\n🇰🇷 कोरिया: वोन | KRW\n\n🇧🇷 ब्राज़ील: रियाल | BRL\n\n🇲🇽 मेक्सिको: पेसो | MXN\n\n🇿🇦 दक्षिण अफ्रीका: रैंड | ZAR\n\n🇸🇬 सिंगापुर: डॉलर | SGD\n\n🇭🇰 हांगकांग: डॉलर | HKD\n\n🇳🇴 नॉर्वे: क्रोन | NOK\n\n🇸🇪 स्वीडन: क्रोन | SEK\n\n🇩🇰 डेनमार्क: क्रोन | DKK\n\n🇵🇱 पोलैंड: ज़्लॉटी | PLN\n\n🇨🇿 चेक गणराज्य: क्रोन | CZK\n\n🇭🇺 हंगरी: फोरिंट | HUF\n\n🇷🇴 रोमानिया: ल्यू | RON\n\n🇦🇿 अज़रबैजान: मनात | AZN\n\n🇬🇪 जॉर्जिया: लारी | GEL\n\n🇺🇦 यूक्रेन: ग्रिव्ना | UAH\n\n🇧🇾 बेलारूस: रूबल | BYN\n\n🇰🇬 किर्गिस्तान: सोम | KGS\n\n🇹🇯 ताजिकिस्तान: सोमोनी | TJS\n\n🇹🇲 तुर्कमेनिस्तान: मनात | TMT\n\n🇲🇾 मलेशिया: रिंग्गित | MYR\n\n🇮🇩 इंडोनेशिया: रुपिया | IDR\n\n🇹🇭 थाईलैंड: बाट | THB\n\n🇵🇭 फिलीपींस: पेसो | PHP\n\n🇻🇳 वियतनाम: डोंग | VND\n\n🇵🇰 पाकिस्तान: रुपया | PKR\n\n🇧🇩 बांग्लादेश: टका | BDT\n\n🇪🇬 मिस्र: पाउंड | EGP\n\n🇳🇬 नाइजीरिया: नायरा | NGN\n\n🇰🇪 केन्या: शिलिंग | KES\n\n🇦🇷 अर्जेंटीना: पेसो | ARS\n\n🇨🇱 चिली: पेसो | CLP\n\n🇨🇴 कोलंबिया: पेसो | COP\n\n🇵🇪 पेरू: सोल | PEN\n\n🇮🇱 इज़राइल: शेकेल | ILS\n\n🇶🇦 क़तर: रियाल | QAR\n\n🇰🇼 कुवैत: दिनार | KWD\n\n🇧🇭 बहरीन: दिनार | BHD\n\n🇴🇲 ओमान: रियाल | OMR\n\n🇳🇿 न्यूज़ीलैंड: डॉलर | NZD\n\n🇦🇺 ऑस्ट्रेलिया: डॉलर | AUD\n\n🇨🇦 कनाडा: डॉलर | CAD\n\n📝 उदाहरण: 100 डॉलर सोम"
            ),
}
    await message.answer(templates.get(lang, templates["en"]))


# ============================================================
# ASOSIY ROUTER
# ============================================================
@dp.message(F.text.in_(BACK_TEXTS))
async def back_handler(message: types.Message, state: FSMContext):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    await state.clear()
    ok, not_sub = await check_sub(uid, lang)
    if not ok:
        await message.answer(t("sub_required", lang), reply_markup=sub_kb(not_sub, lang))
        return
    await message.answer(t("main_menu", lang), reply_markup=menu_kb(lang))
@dp.callback_query(F.data == "balance_accept")
async def cb_balance_accept(callback: types.CallbackQuery, state: FSMContext):
    uid  = callback.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    await state.set_state(S.balance_amount)
    await state.update_data(lang=lang)
    ask_msg = {
        "uz": "💰 Qancha so'm kiritmoqchisiz?\n\nFaqat raqam yozing:\nMisol: 50000",
        "en": "💰 How much would you like to add?\n\nEnter number only:\nExample: 50000",
        "ru": "💰 Сколько хотите пополнить?\n\nВведите только цифры:\nПример: 50000",
        "ar": "💰 كم تريد إضافة؟\n\nأدخل رقماً فقط:\nمثال: 50000",
        "tr": "💰 Ne kadar yüklemek istiyorsunuz?\n\nSadece rakam girin:\nÖrnek: 50000",
        "es": "💰 ¿Cuánto desea agregar?\n\nIngrese solo número:\nEjemplo: 50000",
        "hi": "💰 आप कितना जोड़ना चाहते हैं?\n\nकेवल संख्या दर्ज करें:\nउदाहरण: 50000",
    }
    await callback.message.edit_text(ask_msg.get(lang, ask_msg["en"]))


@dp.message(S.balance_amount)
async def handle_balance_amount(message: types.Message, state: FSMContext):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    try:
        amount = int(message.text.strip().replace(",","").replace(" ",""))
        if amount < 1000:
            err = {
                "uz":"❌ Minimal summa 1,000 so'm","en":"❌ Minimum 1,000 UZS",
                "ru":"❌ Минимум 1,000 UZS","ar":"❌ الحد الأدنى 1,000 UZS",
                "tr":"❌ Minimum 1,000 UZS","es":"❌ Mínimo 1,000 UZS","hi":"❌ न्यूनतम 1,000 UZS"
            }
            await message.answer(err.get(lang, err["en"]))
            return
        await state.update_data(amount=amount)
        await state.set_state(S.balance_check)
        # Rekvizitni settings dan olish
        sett = load_settings()
        requisite = sett.get("custom_section_texts", {}).get("balance_requisite", {}).get(lang,
                                                                                          "Humo: 9860 1234 5678 9012\nUzcard: 8600 1234 5678 9012")

        send_msg = {
            "uz": f"💳 Summa: {amount:,} so'm\n\n{requisite}\n\nTo'lovni amalga oshirib, chek rasmini yuboring 👇",
            "en": f"💳 Amount: {amount:,} UZS\n\n{requisite}\n\nMake payment and send receipt photo 👇",
            "ru": f"💳 Сумма: {amount:,} UZS\n\n{requisite}\n\nОплатите и отправьте фото чека 👇",
            "ar": f"💳 المبلغ: {amount:,} UZS\n\n{requisite}\n\nادفع وأرسل صورة الإيصال 👇",
            "tr": f"💳 Tutar: {amount:,} UZS\n\n{requisite}\n\nÖdeyin ve makbuz fotoğrafı gönderin 👇",
            "es": f"💳 Monto: {amount:,} UZS\n\n{requisite}\n\nPaga y envía foto del recibo 👇",
            "hi": f"💳 राशि: {amount:,} UZS\n\n{requisite}\n\nभुगतान करें और रसीद फ़ोटो भेजें 👇",
        }
        await message.answer(send_msg.get(lang, send_msg["en"]))
    except:
        err = {
            "uz":"❌ Faqat raqam kiriting","en":"❌ Enter numbers only",
            "ru":"❌ Введите только цифры","ar":"❌ أدخل أرقاماً فقط",
            "tr":"❌ Sadece rakam girin","es":"❌ Solo números","hi":"❌ केवल संख्या दर्ज करें"
        }
        await message.answer(err.get(lang, err["en"]))


@dp.message(S.balance_check)
async def handle_balance_check(message: types.Message, state: FSMContext, bot: Bot):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")

    if not message.photo:
        err = {
            "uz":"📸 Chek rasmini yuboring","en":"📸 Send receipt photo",
            "ru":"📸 Отправьте фото чека","ar":"📸 أرسل صورة الإيصال",
            "tr":"📸 Makbuz fotoğrafı gönderin","es":"📸 Envía foto del recibo","hi":"📸 रसीद फ़ोटो भेजें"
        }
        await message.answer(err.get(lang, err["en"]))
        return

    data    = await state.get_data()
    amount  = data.get("amount", 0)
    file_id = message.photo[-1].file_id

    from database import create_payment, update_payment
    from tariffs import PAYMENT_CHANNEL, channel_payment_kb
    payment_id = create_payment(uid, "balance", "topup", amount)
    update_payment(payment_id, {"check_file_id": file_id})

    channel_text = (
        f"💰 BALANS TO'LDIRISH #{payment_id}\n\n"
        f"👤 {user.get('name','?')}\n"
        f"🆔 ID: {uid}\n"
        f"👤 @{user.get('username','—')}\n"
        f"💰 Summa: {amount:,} so'm\n"
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

    # Bu qatorni O'ZGARTIRING:
    ch_msg = await bot.send_photo(
        PAYMENT_CHANNEL,
        file_id,
        caption=channel_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✓ Tasdiqlash", callback_data=f"bal_confirm_{payment_id}_{amount}_{uid}"),
            InlineKeyboardButton(text="✗ Rad etish", callback_data=f"bal_reject_{payment_id}_{uid}"),
        ]])
    )
    update_payment(payment_id, {"channel_msg_id": ch_msg.message_id})
    await state.clear()

    sent = {
        "uz": "✅ Chekingiz yuborildi! Admin tekshirib tasdiqlagach balansingiz to'ldiriladi.",
        "en": "✅ Receipt sent! Balance will be added after admin confirmation.",
        "ru": "✅ Чек отправлен! Баланс пополнится после подтверждения.",
        "ar": "✅ تم إرسال الإيصال! سيُضاف الرصيد بعد التأكيد.",
        "tr": "✅ Makbuz gönderildi! Onaydan sonra bakiye yüklenecek.",
        "es": "✅ ¡Recibo enviado! El saldo se añadirá tras confirmación.",
        "hi": "✅ रसीद भेजी गई! पुष्टि के बाद बैलेंस जुड़ेगा।",
    }
    await message.answer(sent.get(lang, sent["en"]))


@dp.callback_query(F.data.startswith("bal_confirm_"))
async def cb_bal_confirm(callback: types.CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        return
    parts      = callback.data.split("_")
    payment_id = int(parts[2])
    amount     = int(parts[3])
    uid        = int(parts[4])

    from database import add_balance, update_payment, get_balance
    add_balance(uid, amount)
    update_payment(payment_id, {"status": "confirmed"})

    await callback.message.edit_caption(
        caption=callback.message.caption + f"\n\n✅ TASDIQLANDI +{amount:,} so'm",
        reply_markup=None
    )

    user = get_user(uid)
    lang = user.get("lang", "en")
    bal  = get_balance(uid)
    conf = {
        "uz": f"✅ Balansingiz to'ldirildi!\n\n+{amount:,} so'm\n💰 Joriy balans: {bal:,} so'm",
        "en": f"✅ Balance topped up!\n\n+{amount:,} UZS\n💰 Current balance: {bal:,} UZS",
        "ru": f"✅ Баланс пополнен!\n\n+{amount:,} UZS\n💰 Текущий баланс: {bal:,} UZS",
        "ar": f"✅ تم شحن الرصيد!\n\n+{amount:,} UZS\n💰 الرصيد الحالي: {bal:,} UZS",
        "tr": f"✅ Bakiye yüklendi!\n\n+{amount:,} UZS\n💰 Mevcut bakiye: {bal:,} UZS",
        "es": f"✅ ¡Saldo recargado!\n\n+{amount:,} UZS\n💰 Saldo actual: {bal:,} UZS",
        "hi": f"✅ बैलेंस जोड़ा गया!\n\n+{amount:,} UZS\n💰 वर्तमान बैलेंस: {bal:,} UZS",
    }
    try:
        await bot.send_message(uid, conf.get(lang, conf["en"]))
    except:
        pass
    await callback.answer("✅ Tasdiqlandi!")


@dp.callback_query(F.data.startswith("bal_reject_"))
async def cb_bal_reject(callback: types.CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        return
    parts      = callback.data.split("_")
    payment_id = int(parts[2])
    uid        = int(parts[3])

    from database import update_payment
    update_payment(payment_id, {"status": "rejected"})

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ RAD ETILDI",
        reply_markup=None
    )

    user = get_user(uid)
    lang = user.get("lang", "en")
    rej  = {
        "uz": "❌ Balans to'ldirilmadi.\nSumma noto'g'ri yoki chek yaroqsiz.\nQayta urinib ko'ring: 📩 @Rustamjonoff1",
        "en": "❌ Balance not added.\nIncorrect amount or invalid receipt.\nTry again: 📩 @Rustamjonoff1",
        "ru": "❌ Баланс не пополнен.\nНеверная сумма или чек недействителен.\nПовторите: 📩 @Rustamjonoff1",
        "ar": "❌ لم يُضف الرصيد.\nمبلغ خاطئ أو إيصال غير صالح.\nحاول مجدداً: 📩 @Rustamjonoff1",
        "tr": "❌ Bakiye eklenmedi.\nYanlış tutar veya geçersiz makbuz.\nTekrar deneyin: 📩 @Rustamjonoff1",
        "es": "❌ Saldo no añadido.\nMonto incorrecto o recibo inválido.\nIntenta de nuevo: 📩 @Rustamjonoff1",
        "hi": "❌ बैलेंस नहीं जोड़ा गया।\nगलत राशि या अमान्य रसीद।\nफिर प्रयास करें: 📩 @Rustamjonoff1",
    }
    try:
        await bot.send_message(uid, rej.get(lang, rej["en"]))
    except:
        pass
    await callback.answer("❌ Rad etildi!")

async def on_startup():
    asyncio.create_task(morning_quotes_scheduler())
    asyncio.create_task(weekly_report_scheduler())
    asyncio.create_task(scheduled_ads_checker())
    asyncio.create_task(evening_report_scheduler())
    asyncio.create_task(restore_reminders())


dp.startup.register(on_startup)
@dp.message(StateFilter(S.profile_name))
async def handle_profile_name(message: types.Message, state: FSMContext):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    await profile_name_input(message, user, lang, state)

@dp.message(StateFilter(S.profile_city))
async def handle_profile_city(message: types.Message, state: FSMContext):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    await profile_city_input(message, user, lang, state)

@dp.message(StateFilter(S.weather))
async def handle_weather(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("lang", "en")
    await weather_input(message, lang)


@dp.message(StateFilter(S.currency))
async def handle_currency(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    data = await state.get_data()
    convert_mode = data.get("convert_mode", False)
    if not convert_mode:
        await currency_input(message, lang)
        return
    period = data.get("conv_period", "month")

    to_curr = normalize_currency(message.text.strip())
    expenses = user.get("expenses", [])
    now = datetime.now()
    labels = {
        "today": {"uz": "📅 Bugun", "en": "📅 Today", "ru": "📅 Сегодня", "ar": "📅 اليوم", "tr": "📅 Bugün", "es": "📅 Hoy",
                  "hi": "📅 आज"},
        "week": {"uz": "📆 Hafta", "en": "📆 Week", "ru": "📆 Неделя", "ar": "📆 الأسبوع", "tr": "📆 Hafta",
                 "es": "📆 Semana", "hi": "📆 सप्ताह"},
        "month": {"uz": "🗓 Oy", "en": "🗓 Month", "ru": "🗓 Месяц", "ar": "🗓 الشهر", "tr": "🗓 Ay", "es": "🗓 Mes",
                  "hi": "🗓 महीना"},
        "year": {"uz": "▪ Yil", "en": "▪ Year", "ru": "▪ Год", "ar": "▪ السنة", "tr": "▪ Yıl", "es": "▪ Año",
                 "hi": "▪ वर्ष"},
    }
    if period == "today":
        filtered = [e for e in expenses if e.get("date", "").startswith(now.strftime("%Y-%m-%d"))]
    elif period == "week":
        filtered = [e for e in expenses if e.get("date", "") >= (now - timedelta(days=7)).strftime("%Y-%m-%d")]
    elif period == "month":
        filtered = [e for e in expenses if e.get("date", "").startswith(now.strftime("%Y-%m"))]
    else:
        filtered = [e for e in expenses if e.get("date", "").startswith(now.strftime("%Y"))]

    label = labels.get(period, {}).get(lang, period)

    if not filtered:
        await message.answer("Xarajatlar yo'q")
        await state.update_data(convert_mode=False)
        return
    by_curr = {}
    for e in filtered:
        c = e.get("currency", "UZS")
        by_curr[c] = by_curr.get(c, 0) + e["amount"]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://api.exchangerate-api.com/v4/latest/" + to_curr
            ) as r:
                rate_data = await r.json()
        rates = rate_data.get("rates", {})
        if not rates:
            raise Exception("no rates")

        text  = "💱 " + label + " → " + to_curr + "\n\n"
        total = 0
        for c, amt in by_curr.items():
            if c == to_curr:
                conv = amt
            elif c in rates:
                # baza = to_curr, demak rates[c] = 1 to_curr uchun nechta c
                conv = amt / rates.get(c, 1)
            else:
                conv = 0
            total += conv
            text += f"▪️ {fmt(amt)} {c} = {round(conv, 2):,} {to_curr}\n"
        text += f"\n💰 Jami: {round(total, 2):,} {to_curr}"
        await message.answer(text, reply_markup=back_kb(lang))
    except:
        await message.answer("✗ Xatolik. Valyuta nomini tekshiring.", reply_markup=back_kb(lang))

    await state.update_data(convert_mode=False)
    await state.set_state(S.expense)


@dp.message(StateFilter(S.expense))
async def handle_expense(message: types.Message, state: FSMContext):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    await expense_input(message, user, lang)

@dp.message(StateFilter(None))
async def router(message: types.Message, state: FSMContext):
    uid  = message.from_user.id
    user = get_user(uid)
    lang = user.get("lang","en")
    text = message.text or ""

    # Custom tugma nomlarini olish
    sett_r = load_settings()
    custom_r = sett_r.get("custom_section_texts", {})

    def gbtn_r(key, default):
        return custom_r.get(key, {}).get(lang, default)

    update_user(uid,{
        "username": message.from_user.username or "",
        "last_active": datetime.now().strftime("%Y-%m-%d")
    })

    if user.get("blocked"):
        await message.answer(t("blocked",lang))
        return

    if text.startswith("/admin"):
        if is_admin(uid):
            from admin import send_admin_panel
            await send_admin_panel(message,bot)
        return

    if await check_spam(uid):
        await message.answer(t("spam_warning",lang))
        return

    if text and await check_banned(text):
        await send_warning(uid,lang)
        return

    ok,not_sub = await check_sub(uid,lang)
    if not ok:
        await message.answer(t("sub_required",lang), reply_markup=sub_kb(not_sub,lang))
        return

    cur = await state.get_state()

    handlers = {
        S.profile_name.state:  lambda: profile_name_input(message,user,lang,state),
        S.profile_city.state:  lambda: profile_city_input(message,user,lang,state),
        S.expense.state:       lambda: expense_input(message,user,lang),
        S.plan.state:          lambda: plan_input(message,user,lang),
        S.plan_edit.state:     lambda: plan_edit_input(message,user,lang,state),
        S.reminder.state:      lambda: reminder_input(message,user,lang),
        S.reminder_edit.state: lambda: reminder_edit_input(message,user,lang,state),
        S.weather.state:       lambda: weather_input(message,lang),
        S.currency.state:      lambda: currency_input(message,lang),
        S.ai_chat.state:       lambda: ai_input(message,user,lang),
    }
    if cur in handlers:
        await handlers[cur]()
        return

    action = get_action(text,lang)
    if action == "expense":
        await state.set_state(S.expense)
        await show_expense_menu(message, user, lang)
    elif action == "plan":
        await state.set_state(S.plan)
        await show_plan_menu(message, user, lang)
    elif action == "reminder":
        await state.set_state(S.reminder)
        await show_reminder_menu(message, user, lang)
    elif action == "weather":
        await state.set_state(S.weather)
        await message.answer(t("sec_weather", lang), reply_markup=back_kb(lang))
    elif action == "currency":
        await state.set_state(S.currency)
        await message.answer(t("sec_currency", lang), reply_markup=currency_kb(lang))
    elif action == "ai":
        from ai_functions import ai_menu_kb, AI_MENU_TITLE
        sett = load_settings()
        custom_ai = sett.get("custom_section_texts", {}).get("ai_menu_title", {}).get(lang, "")
        ai_title = custom_ai if custom_ai else AI_MENU_TITLE.get(lang, AI_MENU_TITLE["en"])
        await message.answer(ai_title, reply_markup=ai_menu_kb(lang))

    elif action == "profile":
        await show_profile(message,user,lang)
    elif action == "admin":
        settings = load_settings()
        dt = settings.get("donation_text", {})
        if isinstance(dt, dict):
            donation = dt.get(lang, dt.get("en", ""))
        else:
            donation = str(dt) if dt else ""
        admin_texts = {
            "uz":f"👨‍💼 Murojaat va Qo'llab-quvvatlash\n\nHurmatli foydalanuvchi!\n\nSavollar, takliflar yoki shikoyatlar bo'lsa — biz bilan bog'lanishdan tortinmang. Har bir murojaatingiz botimizni yanada yaxshilashimizga yordam beradi!\n\n📩 Admin: {ADMIN_USERNAME}\n⏱ Javob vaqti: 24 soat ichida",
            "en":f"👨‍💼 Contact & Support\n\nDear user!\n\nFor questions, suggestions or complaints — don't hesitate to reach out. Every message helps us improve!\n\n📩 Admin: {ADMIN_USERNAME}\n⏱ Response: within 24 hours",
            "ru":f"👨‍💼 Связь и поддержка\n\nУважаемый пользователь!\n\nПо вопросам, предложениям или жалобам — обращайтесь. Каждое обращение помогает нам улучшаться!\n\n📩 Админ: {ADMIN_USERNAME}\n⏱ Ответ: в течение 24 часов",
            "ar":f"👨‍💼 التواصل والدعم\n\nعزيزي المستخدم!\n\nللأسئلة والاقتراحات والشكاوى — لا تتردد في التواصل.\n\n📩 المشرف: {ADMIN_USERNAME}\n⏱ الرد: خلال 24 ساعة",
            "tr":f"👨‍💼 İletişim ve Destek\n\nSevgili kullanıcı!\n\nSoru, öneri veya şikayetler için iletişime geçin.\n\n📩 Admin: {ADMIN_USERNAME}\n⏱ Yanıt: 24 saat içinde",
            "es":f"👨‍💼 Contacto y Soporte\n\nEstimado usuario!\n\nPara preguntas, sugerencias o quejas — contáctenos.\n\n📩 Admin: {ADMIN_USERNAME}\n⏱ Respuesta: en 24 horas",
            "hi":f"👨‍💼 संपर्क और सहायता\n\nप्रिय उपयोगकर्ता!\n\nप्रश्नों, सुझावों या शिकायतों के लिए संपर्क करें।\n\n📩 Admin: {ADMIN_USERNAME}\n⏱ जवाब: 24 घंटे में",
        }
        out = admin_texts.get(lang,admin_texts["en"])
        if donation:
            out += f"\n\n{'—'*20}\n{donation}"
        await message.answer(out, reply_markup=menu_kb(lang))
    elif action == "settings":
        await message.answer(t("sec_settings", lang), reply_markup=lang_kb())
    else:
        # Tarif tugmasi
        sett = load_settings()
        custom = sett.get("custom_section_texts", {})

        def gbtn(key, default):
            return custom.get(key, {}).get(lang, default)

        tariff_name = gbtn("btn_tariffs", {"uz": "💎 Tariflar", "en": "💎 Tariffs", "ru": "💎 Тарифы", "ar": "💎 الباقات","tr": "💎 Tarifler", "es": "💎 Tarifas", "hi": "💎 टैरिफ"}.get(lang, "💎 Tariffs"))
        referral_name = gbtn("btn_referral",{"uz": "🎁 Referal", "en": "🎁 Referral", "ru": "🎁 Реферал", "ar": "🎁 الإحالة","tr": "🎁 Referans", "es": "🎁 Referido", "hi": "🎁 रेफरल"}.get(lang, "🎁 Referral"))
        balance_name = gbtn("btn_balance",{"uz": "💰 Balans", "en": "💰 Balance", "ru": "💰 Баланс", "ar": "💰 الرصيد", "tr": "💰 Bakiye","es": "💰 Saldo", "hi": "💰 बैलेंस"}.get(lang, "💰 Balance"))

        if text == tariff_name or text in {"💎 Tariflar", "💎 Tariffs", "💎 Тарифы", "💎 الباقات", "💎 Tarifler",
                                           "💎 Tarifas", "💎 टैरिफ"}:
            from tariffs import tariffs_kb, TARIFF_NAMES, TARIFF_FEATURES
            from database import check_subscription

            sub = check_subscription(uid)

            tariff_name_display = (
                TARIFF_NAMES.get(lang, TARIFF_NAMES["en"]).get(sub, sub)
            )

            cur = {
                "uz": "Joriy tarifingiz",
                "en": "Current plan",
                "ru": "Ваш план",
                "ar": "خطتك الحالية",
                "tr": "Mevcut planınız",
                "es": "Tu plan actual",
                "hi": "आपकी योजना"
            }

            await message.answer(
                f"💎 {tariff_name}\n"
                f"{cur.get(lang, '')}: {tariff_name_display}\n"
                f"{TARIFF_FEATURES.get(lang, TARIFF_FEATURES['en']).get(sub, '')}",
                reply_markup=tariffs_kb(lang, uid)
            )

        elif text == balance_name or text in {"💰 Balans", "💰 Balance", "💰 Баланс", "💰 الرصيد", "💰 Bakiye", "💰 Saldo","💰 बैलेंस"}:
            from database import get_balance

            bal = get_balance(uid)

            sett2 = load_settings()

            custom_bal = (
                sett2.get("custom_section_texts", {})
                .get("balance_page", {})
                .get(lang, "")
            )

            topup_text = custom.get("btn_topup", {}).get(lang, {
                "uz": "💳 Balansni to'ldirish", "en": "💳 Top up", "ru": "💳 Пополнить",
                "ar": "💳 شحن", "tr": "💳 Yükle", "es": "💳 Recargar", "hi": "💳 टॉप अप"
            }.get(lang, "💳 Top up"))

            topup_kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=topup_text, callback_data="balance_topup")
            ]])

            if custom_bal:
                await message.answer(
                    custom_bal.replace("{bal}", str(bal)),
                    reply_markup=topup_kb
                )
                return

            bal_text = {
                "uz": f"💰 Balansingiz: {bal:,} so'm Balansni to'ldirish uchun quyidagi tugmani bosing.",
                "en": f"💰 Your balance: {bal:,} UZS Press button below to top up.",
                "ru": f"💰 Ваш баланс: {bal:,} UZS Нажмите кнопку для пополнения.",
                "ar": f"💰 رصيدك: {bal:,} UZS اضغط الزر للشحن.",
                "tr": f"💰 Bakiyeniz: {bal:,} UZS Yüklemek için butona basın.",
                "es": f"💰 Tu saldo: {bal:,} UZS Presiona el botón para recargar.",
                "hi": f"💰 आपका बैलेंस: {bal:,} UZS टॉपअप के लिए बटन दबाएं।"
            }

            await message.answer(
                bal_text.get(lang, bal_text["en"]),
                reply_markup=topup_kb
            )

        elif text == referral_name or text in {"🎁 Referal", "🎁 Referral", "🎁 Реферал", "🎁 الإحالة", "🎁 Referans", "🎁 Referido","🎁 रेफरल"}:
            from referral import get_referral, REF_TEXTS, referral_kb

            sett3 = load_settings()

            custom_ref = (
                sett3.get("custom_section_texts", {})
                .get("referral_text", {})
                .get(lang, "")
            )

            if custom_ref:
                await message.answer(
                    custom_ref,
                    reply_markup=referral_kb(lang),
                    parse_mode="Markdown"
                )
                return

            ref = get_referral(uid)

            ref_code = ref.get("ref_code", "")
            link = f"https://t.me/Startdaily_bot?start=ref_{ref_code}"

            std_disc = ref.get("discount_standard", 0)
            prem_disc = ref.get("discount_premium", 0)

            no_disc = {
                "uz": "Hozircha yo'q",
                "en": "None yet",
                "ru": "Пока нет",
                "ar": "لا يوجد",
                "tr": "Henüz yok",
                "es": "Aún no",
                "hi": "अभी नहीं"
            }

            disc_std_text = (
                f"{std_disc}%"
                if std_disc
                else no_disc.get(lang, "—")
            )

            disc_prem_text = (
                f"{prem_disc}%"
                if prem_disc
                else no_disc.get(lang, "—")
            )

            carried = ref.get("carried_refs", 0)

            carried_text = (
                f"\n{REF_TEXTS['carried_refs'].get(lang, '')}: {carried}"
                if carried > 0
                else ""
            )

            text_out = (
                f"{REF_TEXTS['title'].get(lang, '')}\n\n"
                f"{REF_TEXTS['your_link'].get(lang, '')}\n"
                f"`{link}`\n\n"
                f"{REF_TEXTS['your_stats'].get(lang, '')}\n"
                f"👥 {REF_TEXTS['total_refs'].get(lang, '')}: {ref.get('total_refs', 0)}\n"
                f"📅 {REF_TEXTS['month_refs'].get(lang, '')}: {ref.get('month_refs', 0)}"
                f"{carried_text}\n\n"
                f"▪ {REF_TEXTS['discount_std'].get(lang, '')}: {disc_std_text}\n"
                f"💎 {REF_TEXTS['discount_prem'].get(lang, '')}: {disc_prem_text}"
            )

            await message.answer(
                text_out,
                reply_markup=referral_kb(lang),
                parse_mode="Markdown"
            )

        else:
            await message.answer(
                t("main_menu", lang),
                reply_markup=menu_kb(lang)
            )
@dp.callback_query(F.data == "balance_topup")
async def cb_balance_topup(callback: types.CallbackQuery, state: FSMContext):
    uid  = callback.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    sett = load_settings()
    custom_topup = sett.get("custom_section_texts", {}).get("balance_topup_text", {}).get(lang, "")
    if custom_topup:
        await callback.message.edit_text(custom_topup)
        return
    oferta_msg = {
        "uz": (
            "📋 Balans to'ldirish shartlari\n\n"
            "✅ Balans faqat AI funksiyalari uchun ishlatiladi\n"
            "❌ To'langan pulni qaytarib olish mumkin emas\n"
            "❌ Balansni boshqaga o'tkazib bo'lmaydi\n"
            "⚠️ Noto'g'ri summa yuborsangiz admin tekshiradi\n\n"
            "Davom etish uchun qabul qiling 👇"
        ),
        "en": (
            "📋 Balance top up terms\n\n"
            "✅ Balance is used only for AI functions\n"
            "❌ Payments are non-refundable\n"
            "❌ Balance cannot be transferred\n"
            "⚠️ Wrong amount will be checked by admin\n\n"
            "Accept to continue 👇"
        ),
        "ru": (
            "📋 Условия пополнения баланса\n\n"
            "✅ Баланс используется только для AI функций\n"
            "❌ Оплата не возвращается\n"
            "❌ Баланс нельзя передать другому\n"
            "⚠️ Неверная сумма будет проверена админом\n\n"
            "Примите для продолжения 👇"
        ),
        "ar": (
            "📋 شروط شحن الرصيد\n\n"
            "✅ الرصيد للوظائف AI فقط\n"
            "❌ المدفوعات غير قابلة للاسترداد\n"
            "❌ لا يمكن نقل الرصيد\n"
            "⚠️ المبلغ الخاطئ سيتحقق منه المشرف\n\n"
            "اقبل للمتابعة 👇"
        ),
        "tr": (
            "📋 Bakiye yükleme şartları\n\n"
            "✅ Bakiye sadece AI işlevleri için\n"
            "❌ Ödemeler iade edilmez\n"
            "❌ Bakiye transfer edilemez\n"
            "⚠️ Yanlış tutar admin tarafından kontrol edilir\n\n"
            "Kabul et 👇"
        ),
        "es": (
            "📋 Términos de recarga\n\n"
            "✅ El saldo es solo para funciones AI\n"
            "❌ Los pagos no son reembolsables\n"
            "❌ El saldo no se puede transferir\n"
            "⚠️ Monto incorrecto será verificado por admin\n\n"
            "Acepta para continuar 👇"
        ),
        "hi": (
            "📋 बैलेंस टॉप अप शर्तें\n\n"
            "✅ बैलेंस केवल AI फ़ंक्शन के लिए\n"
            "❌ भुगतान वापस नहीं होगा\n"
            "❌ बैलेंस ट्रांसफर नहीं होगा\n"
            "⚠️ गलत राशि एडमिन द्वारा जांची जाएगी\n\n"
            "जारी रखने के लिए स्वीकार करें 👇"
        ),
    }
    accept_btn = {
        "uz":"✅ Qabul qilaman","en":"✅ I Accept","ru":"✅ Принимаю",
        "ar":"✅ أقبل","tr":"✅ Kabul ediyorum","es":"✅ Acepto","hi":"✅ स्वीकार करता हूं"
    }
    await callback.message.edit_text(
        oferta_msg.get(lang, oferta_msg["en"]),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=accept_btn.get(lang, accept_btn["en"]),
                callback_data="balance_accept"
            )
        ]])
    )
# PROFIL
# ============================================================
async def show_profile(message, user, lang):
    name      = user.get("name","—")
    city      = user.get("city","—")
    joined    = user.get("joined","—")
    expenses  = len(user.get("expenses",[]))
    plans     = sum(len(v) for v in user.get("plans",{}).values() if isinstance(v,list))
    reminders = len(user.get("reminders",[]))
    warnings  = user.get("warnings",0)

    sett_p   = load_settings()
    custom_p = sett_p.get("custom_section_texts", {})

    def gbtn_p(key, default):
        return custom_p.get(key, {}).get(lang, default)

    nl =" "
    profile_text = (
        t('sec_profile', lang) + nl + nl +
        "📛 " + t('p_name', lang) + ": " + name + nl +
        "🏙 " + t('p_city', lang) + ": " + city + nl +
        "📅 " + t('p_joined', lang) + ": " + joined + nl + nl +
        "▪ " + t('p_activity', lang) + ":" + nl +
        "💸 " + t('p_expenses', lang) + ": " + str(expenses) + nl +
        "▪ " + t('p_tasks', lang) + ": " + str(plans) + nl +
        "⏰ " + t('p_reminders', lang) + ": " + str(reminders) + nl +
        "⚠️ " + t('p_warnings', lang) + ": " + str(warnings) + "/3"
    )

    await message.answer(
        profile_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=gbtn_p("btn_edit_name", t("p_edit_name", lang)),
                callback_data="profile_name"
            )],
            [InlineKeyboardButton(
                text=gbtn_p("btn_edit_city", t("p_edit_city", lang)),
                callback_data="profile_city"
            )],
        ])
    )


@dp.callback_query(F.data=="profile_name")
async def cb_pname(callback: types.CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    lang = user.get("lang","en")
    await state.set_state(S.profile_name)
    await callback.message.answer(t("enter_name",lang), reply_markup=back_kb(lang))

@dp.callback_query(F.data=="profile_city")
async def cb_pcity(callback: types.CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    lang = user.get("lang","en")
    await state.set_state(S.profile_city)
    await callback.message.answer(t("enter_city",lang), reply_markup=back_kb(lang))

async def profile_name_input(message, user, lang, state):
    name = message.text.strip()
    update_user(message.from_user.id, {"name": name})
    if not user.get("city"):
        await state.set_state(S.profile_city)
        await message.answer(t("enter_city", lang))
        return
    await state.clear()
    await message.answer(f"✓ {name}", reply_markup=menu_kb(lang))


async def profile_city_input(message, user, lang, state):
    city = message.text.strip()
    uid  = message.from_user.id
    update_user(uid,{"city":city})
    await state.clear()
    ok,not_sub = await check_sub(uid,lang)
    if not ok:
        await message.answer(t("sub_required",lang), reply_markup=sub_kb(not_sub,lang))
        return
    settings = load_settings()
    of_raw_data = settings.get("oferta_text", {})
    of_raw = of_raw_data.get(lang, "") if isinstance(of_raw_data, dict) else ""
    oferta_text = (of_raw.strip() if isinstance(of_raw,str) and of_raw.strip()
                   else DEFAULT_OFERTA.get(lang,DEFAULT_OFERTA["en"]))
    await message.answer(oferta_text, reply_markup=oferta_kb(lang))

# ============================================================
# XARAJATLAR
# ============================================================
async def show_expense_menu(message, user, lang):
    expenses  = user.get("expenses",[])
    today     = datetime.now().strftime("%Y-%m-%d")
    today_exp = [e for e in expenses if e.get("date","").startswith(today)]
    by_curr   = {}
    for e in today_exp:
        c = e.get("currency","UZS")
        by_curr[c] = by_curr.get(c,0)+e["amount"]

    text = t("sec_expense",lang)
    if by_curr:
        text += "\n\n📊"
        for c,total in by_curr.items():
            text += f"\n▪️ {total:,.0f} {c}"

    sett_e = load_settings()
    custom_e = sett_e.get("custom_section_texts", {})

    def gbtn_e(key, default):
        return custom_e.get(key, {}).get(lang, default)

    await message.answer(text, reply_markup=back_kb(lang))
    exp_btn_labels = {
        "uz": ["📅 Bugun", "📆 Hafta", "🗓 Oy", "📊 Yil", "💱 Konvertatsiya", "🗑 Tozalash"],
        "en": ["📅 Today", "📆 Week", "🗓 Month", "📊 Year", "💱 Convert", "🗑 Clear"],
        "ru": ["📅 Сегодня", "📆 Неделя", "🗓 Месяц", "📊 Год", "💱 Конвертация", "🗑 Очистить"],
        "ar": ["📅 اليوم", "📆 الأسبوع", "🗓 الشهر", "📊 السنة", "💱 تحويل", "🗑 مسح"],
        "tr": ["📅 Bugün", "📆 Hafta", "🗓 Ay", "📊 Yıl", "💱 Dönüştür", "🗑 Temizle"],
        "es": ["📅 Hoy", "📆 Semana", "🗓 Mes", "📊 Año", "💱 Convertir", "🗑 Limpiar"],
        "hi": ["📅 आज", "📆 सप्ताह", "🗓 महीना", "📊 वर्ष", "💱 कनवर्ट", "🗑 साफ़ करें"],
    }
    el = exp_btn_labels.get(lang, exp_btn_labels["en"])
    report_title = {
        "uz": "📊 Hisobot turini tanlang:", "en": "📊 Choose a report:", "ru": "📊 Выберите отчёт:",
        "ar": "📊 اختر التقرير:", "tr": "📊 Rapor seçin:", "es": "📊 Elige un informe:", "hi": "📊 रिपोर्ट चुनें:",
    }
    await message.answer(
        report_title.get(lang, report_title["en"]),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=gbtn_e("btn_exp_today", el[0]), callback_data="ex_today"),
                InlineKeyboardButton(text=gbtn_e("btn_exp_week", el[1]), callback_data="ex_week"),
            ],
            [
                InlineKeyboardButton(text=gbtn_e("btn_exp_month", el[2]), callback_data="ex_month"),
                InlineKeyboardButton(text=gbtn_e("btn_exp_year", el[3]), callback_data="ex_year"),
            ],
            [InlineKeyboardButton(text=gbtn_e("btn_exp_convert", el[4]), callback_data="ex_convert")],
            [InlineKeyboardButton(text=gbtn_e("btn_exp_clear", el[5]), callback_data="ex_clear")],
        ])
    )


def fmt(n):
    return f"{int(n):,}".replace(",", " ")


async def expense_input(message, user, lang):
    try:
        lines      = message.text.strip().splitlines()
        fresh_user = get_user(message.from_user.id)
        expenses   = fresh_user.get("expenses", [])
        added      = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                parts    = line.split()
                if len(parts) < 2:
                    continue

                currency = normalize_currency(parts[-1])
                rest     = parts[:-1]

                num_tokens  = []
                name_tokens = []
                found_name  = False

                for token in reversed(rest):
                    cleaned = token.replace(",", "").replace(".", "")
                    arabic_nums = {'٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7',
                                   '٨': '8', '٩': '9'}
                    hindi_nums = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7',
                                  '८': '8', '९': '9'}
                    cleaned_num = cleaned
                    for ar, en in arabic_nums.items():
                        cleaned_num = cleaned_num.replace(ar, en)
                    for hi, en in hindi_nums.items():
                        cleaned_num = cleaned_num.replace(hi, en)
                    is_num = cleaned_num.isdigit()
                    is_mult = token.lower() in [
                        "ming", "mln", "million", "milliard", "mlrd",
                        "тысяча", "тысяч", "млн", "миллион", "миллиард", "млрд",
                        "thousand", "bin", "milyon", "milyar",
                        "ألف", "مليون", "مليار",
                        "mil", "millón", "millones", "billón",
                        "हजार", "हज़ार", "लाख", "करोड़", "मिलियन", "अरब",
                        "k", "m", "b",
                    ]

                    if not found_name and (is_num or is_mult):
                        num_tokens.insert(0, token)
                    else:
                        found_name = True
                        name_tokens.insert(0, token)

                amount_str = " ".join(num_tokens)
                amount     = parse_amount(amount_str)
                name       = " ".join(name_tokens) if name_tokens else "Xarajat"

                if amount is None or amount <= 0:
                    print(f"AMOUNT NONE: line={line}, num_tokens={num_tokens}, amount_str={amount_str}")
                    continue

                expenses.append({
                    "name":     name,
                    "amount":   amount,
                    "currency": currency,
                    "date":     datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                added.append((name, amount, currency))
            except:
                continue

        update_user(message.from_user.id, {"expenses": expenses})

        today   = datetime.now().strftime("%Y-%m-%d")
        result  = ""
        for name, amount, currency in added:
            result += "✓ " + name + " — " + fmt(amount) + " " + currency + "\n"
        by_curr = {}
        for e in expenses:
            if e.get("date", "").startswith(today):
                c = e.get("currency", "UZS")
                by_curr[c] = by_curr.get(c, 0) + e["amount"]

        if by_curr:
            today_label = {
                "uz": "▪ Bugun jami:",
                "en": "▪ Today total:",
                "ru": "▪ Итого сегодня:",
                "ar": "▪ إجمالي اليوم:",
                "tr": "▪ Bugün toplam:",
                "es": "▪ Total hoy:",
                "hi": "▪ आज कुल:",
            }
            result += "\n" + today_label.get(lang, today_label["en"]) + "\n"
            for c, total in by_curr.items():
                result += "▪️ " + fmt(total) + " " + c + "\n"
        result += "\n" + t("stay_hint", lang)
        await message.answer(result, reply_markup=back_kb(lang))

    except Exception as e:
        print(f"EXPENSE ERROR: {e}")
        await message.answer(t("sec_expense", lang), reply_markup=back_kb(lang))


@dp.callback_query(F.data.startswith("ex_"))
async def cb_expense(callback: types.CallbackQuery, state: FSMContext):
    uid      = callback.from_user.id
    user     = get_user(uid)
    action   = callback.data[3:]
    expenses = user.get("expenses",[])
    now      = datetime.now()

    if action == "clear":
        update_user(uid,{"expenses":[]})
        await callback.answer("✅")
        await callback.message.edit_text("🗑")
        return

    if action == "convert":
        uid = callback.from_user.id
        user = get_user(uid)
        lang = user.get("lang", "en")
        conv_msg = {
        "uz": "💱 Konvertatsiya\n\nQaysi valyutaga o'girish kerak?\n\nValyuta nomini yozing: Misol: USD, dollar, so'm, euro",
        "en": "💱 Convert Which currency to convert to? Write currency name: Example: USD, dollar, som, euro",
        "ru": "💱 Конвертация В какую валюту конвертировать? Напишите название: Пример: USD, доллар, сум, евро",
        "ar": "💱 تحويلأيعملةتريدالتحويلإليها?اكتباسمالعملة:مثال: USD, دولار, سوم",
        "tr": "💱 Dönüştür Hangi para birimine çevirmek istiyorsunuz? Yazın: Örnek: USD, dolar, som, euro",
        "es": "💱 Convertir A qué moneda convertir? Escriba: Ejemplo: USD, dólar, som, euro",
        "hi": "💱 कनवर्ट किस मुद्रा में बदलें? लिखें: उदाहरण: USD, dollar, som, euro",
        }
        await state.set_state(S.currency)
        await state.update_data(convert_mode=True)
        sett_c = load_settings()
        custom_c = sett_c.get("custom_section_texts", {})

        def gbtn_c(key, default):
            return custom_c.get(key, {}).get(lang, default)

        period_labels = {
            "uz": ["📅 Bugun", "📆 Hafta", "🗓 Oy", "▪ Yil"],
            "en": ["📅 Today", "📆 Week", "🗓 Month", "▪ Year"],
            "ru": ["📅 Сегодня", "📆 Неделя", "🗓 Месяц", "▪ Год"],
            "ar": ["📅 اليوم", "📆 الأسبوع", "🗓 الشهر", "▪ السنة"],
            "tr": ["📅 Bugün", "📆 Hafta", "🗓 Ay", "▪ Yıl"],
            "es": ["📅 Hoy", "📆 Semana", "🗓 Mes", "▪ Año"],
            "hi": ["📅 आज", "📆 सप्ताह", "🗓 महीना", "▪ वर्ष"],
        }
        pl = period_labels.get(lang, period_labels["en"])

        await callback.message.answer(
            conv_msg.get(lang, conv_msg["en"]),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=gbtn_c("btn_conv_today", pl[0]), callback_data="conv_period_today")],
                [InlineKeyboardButton(text=gbtn_c("btn_conv_week", pl[1]), callback_data="conv_period_week")],
                [InlineKeyboardButton(text=gbtn_c("btn_conv_month", pl[2]), callback_data="conv_period_month")],
                [InlineKeyboardButton(text=gbtn_c("btn_conv_year", pl[3]), callback_data="conv_period_year")],
            ])
        )

        return

    lang = user.get("lang", "en")
    period_names = {
        "today": {"uz":"📅 Bugun","en":"📅 Today","ru":"📅 Сегодня","ar":"📅 اليوم","tr":"📅 Bugün","es":"📅 Hoy","hi":"📅 आज"},
        "week":  {"uz":"📆 Hafta","en":"📆 Week","ru":"📆 Неделя","ar":"📆 الأسبوع","tr":"📆 Hafta","es":"📆 Semana","hi":"📆 सप्ताह"},
        "month": {"uz":"🗓 Oy","en":"🗓 Month","ru":"🗓 Месяц","ar":"🗓 الشهر","tr":"🗓 Ay","es":"🗓 Mes","hi":"🗓 महीना"},
        "year":  {"uz":"📊 Yil","en":"📊 Year","ru":"📊 Год","ar":"📊 السنة","tr":"📊 Yıl","es":"📊 Año","hi":"📊 वर्ष"},
    }
    if action == "today":
        filtered = [e for e in expenses if e.get("date","").startswith(now.strftime("%Y-%m-%d"))]
        pkey = "today"
    elif action == "week":
        filtered = [e for e in expenses if e.get("date","")>=(now-timedelta(days=7)).strftime("%Y-%m-%d")]
        pkey = "week"
    elif action == "month":
        filtered = [e for e in expenses if e.get("date","").startswith(now.strftime("%Y-%m"))]
        pkey = "month"
    else:
        filtered = [e for e in expenses if e.get("date","").startswith(now.strftime("%Y"))]
        pkey = "year"
    label = period_names[pkey].get(lang, period_names[pkey]["en"])

    records_label = {"uz":"Yozuvlar","en":"Records","ru":"Записей","ar":"السجلات","tr":"Kayıtlar","es":"Registros","hi":"रिकॉर्ड"}
    empty_label = {"uz":"Xarajatlar yo'q","en":"No expenses","ru":"Нет расходов","ar":"لا مصروفات","tr":"Harcama yok","es":"Sin gastos","hi":"कोई खर्च नहीं"}

    if not filtered:
        await callback.message.edit_text(f"{label}\n\n{empty_label.get(lang, empty_label['en'])}")
        return

    by_curr = {}
    for e in filtered:
        c = e.get("currency","UZS")
        by_curr[c] = by_curr.get(c,0)+e["amount"]

    text = f"{label}\n\n"
    for c,total in by_curr.items():
        text += "▪️ " + f"{total:,.0f}".replace(",", " ") + " " + c + "\n"
    text += f"\n{records_label.get(lang, records_label['en'])}: {len(filtered)}\n\n"
    for e in filtered[-5:]:
        text += f"• {e['name']}: {e['amount']:,.0f} {e.get('currency','UZS')} — {e['date'][:10]}\n"
    await callback.message.edit_text(text)

@dp.callback_query(F.data.startswith("conv_") & ~F.data.startswith("conv_period_"))
async def cb_conv(callback: types.CallbackQuery):

    uid     = callback.from_user.id
    user    = get_user(uid)
    to_curr = callback.data[5:]
    now     = datetime.now()
    month   = [e for e in user.get("expenses", []) if e.get("date", "").startswith(now.strftime("%Y-%m"))]
    by_curr = {}
    for e in month:
        c = e.get("currency", "UZS")
        by_curr[c] = by_curr.get(c, 0) + e["amount"]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.exchangerate-api.com/v4/latest/" + to_curr) as r:
                rate_data = await r.json()
        rates = rate_data.get("rates", {})
        if not rates:
            raise Exception("no rates")
        text  = "💱 Oy → " + to_curr + "\n\n"
        total = 0
        for c, amt in by_curr.items():
            if c == to_curr:
                conv = amt
            elif c in rates:
                conv = amt / rates.get(c, 1)
            else:
                conv = 0
            total += conv
            text += "▪️ " + fmt(amt) + " " + c + " = " + fmt(conv) + " " + to_curr + "\n"
        text += "\n💰 Jami: " + fmt(total) + " " + to_curr
        await callback.message.answer(text)
    except:
        await callback.answer("✗ Xatolik", show_alert=True)

@dp.callback_query(F.data.startswith("conv_period_"))
async def cb_conv_period(callback: types.CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    user = get_user(uid)
    lang = user.get("lang", "en")
    period = callback.data.split("_")[2]
    await state.update_data(conv_period=period)

    ask = {
        "uz": "💱 Qaysi valyutaga o'girish kerak?\n\nYozing: USD, dollar, so'm, euro...",
    "en": "💱 Which currency to convert to? Write: USD, dollar, som, euro...",
    "ru": "💱 В какую валюту? Напишите: USD, доллар, сум, евро... ",
    "ar": "💱 أي عملة؟ اكتب: USD, دولار, سوم...",
    "tr": "💱 Hangi para birimi? Yazın: USD, dolar, som, euro...",
    "es": "💱 ¿A qué moneda? Escriba: USD, dólar, som, euro...",
    "hi": "💱 किस मुद्रा में? लिखें: USD, dollar, som, euro...",
    }
    await callback.message.edit_text(ask.get(lang, ask["en"]))


# ============================================================
# KUNLIK REJA
# ============================================================
async def show_plan_menu(message, user, lang):
    today       = datetime.now().strftime("%Y-%m-%d")
    plans       = user.get("plans",{})
    if isinstance(plans,list): plans = {}
    today_plans = plans.get(today,[])

    text = t("sec_plan",lang)
    if today_plans:
        text += "\n\n📋\n"
        for i,p in enumerate(today_plans,1):
            s  = "✅" if p.get("done") else "⬜"
            tm = f"{p['time']} " if p.get("time") else ""
            text += f"{s} {i}. {tm}{p['task']}\n"

    await message.answer(text, reply_markup=back_kb(lang))
    if today_plans:
        await message.answer("✏️",reply_markup=plan_manage_kb(today_plans))

    old = {d:v for d,v in plans.items() if d!=today and v}
    if old:
        btns = [[InlineKeyboardButton(text=f"📅 {d} ({len(v)})",callback_data=f"plan_day_{d}")]
                for d,v in sorted(old.items(),reverse=True)[:5]]
        await message.answer("📂",reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

def plan_manage_kb(plans):
    buttons = []
    for i,p in enumerate(plans):
        icon  = "↩️" if p.get("done") else "✅"
        label = p["task"][:15]
        buttons.append([
            InlineKeyboardButton(text=icon,callback_data=f"plan_done_{i}"),
            InlineKeyboardButton(text=f"✏️ {label}",callback_data=f"plan_edit_{i}"),
            InlineKeyboardButton(text="🗑",callback_data=f"plan_del_{i}"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def plan_input(message, user, lang):
    today       = datetime.now().strftime("%Y-%m-%d")
    plans       = user.get("plans",{})
    if isinstance(plans,list): plans = {}
    today_plans = plans.get(today,[])
    lines       = [l.strip() for l in message.text.strip().split("\n") if l.strip()]
    added       = []
    for line in lines:
        parts = line.split(" ",1)
        if len(parts)==2 and ":" in parts[0] and parts[0].replace(":","").isdigit():
            task_time,task_name = parts[0],parts[1]
        else:
            task_time,task_name = None,line
        task = {"task":task_name,"done":False,"time":task_time,"date":today}
        today_plans.append(task)
        added.append(task)
        if task_time:
            try:
                h,m = map(int,task_time.split(":"))
                asyncio.create_task(schedule_reminder(message.chat.id,h,m,f"📅 {task_name}",lang=lang))
            except: pass
    plans[today] = today_plans
    update_user(message.from_user.id,{"plans":plans})
    result = f"✅ {len(added)}\n\n"
    for p in added:
        tm = f"{p['time']} " if p["time"] else ""
        result += f"⬜ {tm}{p['task']}\n"
    result += f"\n{t('stay_hint',lang)}"
    await message.answer(result, reply_markup=back_kb(lang))
    if today_plans:
        await message.answer("✏️",reply_markup=plan_manage_kb(today_plans))

@dp.callback_query(F.data.startswith("plan_"))
async def cb_plan(callback: types.CallbackQuery, state: FSMContext):
    uid         = callback.from_user.id
    user        = get_user(uid)
    lang        = user.get("lang","en")
    today       = datetime.now().strftime("%Y-%m-%d")
    plans       = user.get("plans",{})
    if isinstance(plans,list): plans = {}
    today_plans = plans.get(today,[])
    parts       = callback.data.split("_")
    action      = parts[1]
    idx         = int(parts[2]) if len(parts)>2 and parts[2].isdigit() else 0

    if action=="done" and idx<len(today_plans):
        today_plans[idx]["done"] = not today_plans[idx].get("done",False)
        plans[today] = today_plans
        update_user(uid,{"plans":plans})
        await callback.answer("✅")
        await callback.message.edit_reply_markup(reply_markup=plan_manage_kb(today_plans))
    elif action=="del" and idx<len(today_plans):
        today_plans.pop(idx)
        plans[today] = today_plans
        update_user(uid,{"plans":plans})
        await callback.answer("🗑")
        if today_plans:
            await callback.message.edit_reply_markup(reply_markup=plan_manage_kb(today_plans))
        else:
            await callback.message.edit_text("📋")
    elif action=="edit" and idx<len(today_plans):
        await state.set_state(S.plan_edit)
        await state.update_data(plan_idx=idx)
        await callback.message.answer(f"✏️ {today_plans[idx]['task']}\n\n→",reply_markup=back_kb(lang))
    elif action=="day":
        day = "_".join(parts[2:])
        dp2 = plans.get(day,[])
        if not dp2:
            await callback.answer("Empty")
            return
        text = f"📅 {day}\n\n"
        for i,p in enumerate(dp2,1):
            s  = "✅" if p.get("done") else "⬜"
            tm = f"{p['time']} " if p.get("time") else ""
            text += f"{s} {i}. {tm}{p['task']}\n"
        await callback.message.answer(text)

async def plan_edit_input(message, user, lang, state):
    data        = await state.get_data()
    idx         = data.get("plan_idx",0)
    today       = datetime.now().strftime("%Y-%m-%d")
    plans       = user.get("plans",{})
    if isinstance(plans,list): plans = {}
    today_plans = plans.get(today,[])
    if idx<len(today_plans):
        text  = message.text.strip()
        parts = text.split(" ",1)
        if len(parts)==2 and ":" in parts[0]:
            today_plans[idx]["time"] = parts[0]
            today_plans[idx]["task"] = parts[1]
        else:
            today_plans[idx]["task"] = text
        plans[today] = today_plans
        update_user(message.from_user.id,{"plans":plans})
        await message.answer(f"✅ {today_plans[idx]['task']}",reply_markup=back_kb(lang))
    await state.set_state(S.plan)

# ============================================================
# ESLATMALAR
# ============================================================
async def show_reminder_menu(message, user, lang):
    reminders = user.get("reminders",[])
    await message.answer(t("sec_reminder",lang), reply_markup=back_kb(lang))
    if reminders:
        await message.answer("📋",reply_markup=reminder_list_kb(reminders))

def reminder_list_kb(reminders):
    btns = []
    for i,r in enumerate(reminders):
        rep   = " 🔄" if r.get("repeat") else ""
        label = f"{r.get('time','?')} — {r['text'][:12]}{rep}"
        btns.append([
            InlineKeyboardButton(text=label,callback_data=f"rem_view_{i}"),
            InlineKeyboardButton(text="✏️",callback_data=f"rem_edit_{i}"),
            InlineKeyboardButton(text="🗑",callback_data=f"rem_del_{i}"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=btns)

async def reminder_input(message, user, lang):
    text = message.text.strip()
    try:
        parts = text.split(" ",1)
        first = parts[0]
        rtext = parts[1] if len(parts)>1 else "Eslatma"
        hour,minute = 9,0
        if "." in first:
            dp2   = text.split(" ",2)
            d,mo,y = dp2[0].split(".")
            tp    = dp2[1] if len(dp2)>1 else "09:00"
            rtext = dp2[2] if len(dp2)>2 else "Eslatma"
            hour,minute = map(int,tp.split(":"))
            dt    = datetime(int(y),int(mo),int(d),hour,minute)
            dt_str = dt.strftime("%d.%m.%Y %H:%M")
        else:
            hour,minute = map(int,first.split(":"))
            dt    = datetime.now().replace(hour=hour,minute=minute,second=0)
            dt_str = dt.strftime("%d.%m.%Y %H:%M")

        pending = {"text":rtext,"time":f"{hour:02d}:{minute:02d}",
                   "datetime":dt_str,"chat_id":message.chat.id,
                   "hour":hour,"minute":minute,"lang":lang}
        update_user(message.from_user.id,{"pending_reminder":pending})
        await message.answer(
            f"⏰ {dt_str} — {rtext}\n\n{t('rem_type',lang)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=t("once_btn",lang),callback_data="rem_once"),
                InlineKeyboardButton(text=t("daily_btn",lang),callback_data="rem_daily"),
            ]])
        )
    except:
        await message.answer(t("sec_reminder",lang), reply_markup=back_kb(lang))

@dp.callback_query(F.data.in_({"rem_once","rem_daily"}))
async def cb_rem_type(callback: types.CallbackQuery):
    uid     = callback.from_user.id
    user    = get_user(uid)
    lang    = user.get("lang","en")
    repeat  = callback.data=="rem_daily"
    pending = user.get("pending_reminder",{})
    if not pending:
        await callback.answer("Error!")
        return
    pending["repeat"] = repeat
    reminders = user.get("reminders",[])
    reminders.append(pending)
    update_user(uid,{"reminders":reminders,"pending_reminder":None})
    rep_text = t("daily_btn",lang) if repeat else t("once_btn",lang)
    msg = t("rem_ok",lang).replace("{dt}",pending["datetime"]).replace("{text}",pending["text"]).replace("{rep}",rep_text)
    await callback.message.edit_text(msg)
    asyncio.create_task(schedule_reminder(
        pending["chat_id"],pending["hour"],pending["minute"],
        pending["text"],lang=lang,repeat=repeat
    ))

@dp.callback_query(F.data.startswith("rem_"))
async def cb_reminder(callback: types.CallbackQuery, state: FSMContext):
    uid       = callback.from_user.id
    user      = get_user(uid)
    lang      = user.get("lang","en")
    reminders = user.get("reminders",[])
    parts     = callback.data.split("_")
    action    = parts[1]
    idx       = int(parts[2]) if len(parts)>2 and parts[2].isdigit() else 0

    if action=="del" and idx<len(reminders):
        reminders.pop(idx)
        update_user(uid,{"reminders":reminders})
        await callback.answer("🗑")
        if reminders:
            await callback.message.edit_reply_markup(reply_markup=reminder_list_kb(reminders))
        else:
            await callback.message.edit_text("📋")
    elif action=="edit" and idx<len(reminders):
        await state.set_state(S.reminder_edit)
        await state.update_data(reminder_idx=idx)
        r = reminders[idx]
        await callback.message.answer(f"✏️ {r['text']} — {r.get('time','?')}\n\n→",reply_markup=back_kb(lang))
    elif action=="view" and idx<len(reminders):
        r   = reminders[idx]
        rep = t("daily_btn",lang) if r.get("repeat") else t("once_btn",lang)
        await callback.answer(f"{r['text']} | {r.get('datetime',r.get('time','?'))} | {rep}",show_alert=True)

async def reminder_edit_input(message, user, lang, state):
    data      = await state.get_data()
    idx       = data.get("reminder_idx",0)
    reminders = user.get("reminders",[])
    if idx<len(reminders):
        text  = message.text.strip()
        parts = text.split(" ",1)
        if len(parts)==2 and ":" in parts[0]:
            reminders[idx]["time"] = parts[0]
            reminders[idx]["text"] = parts[1]
        else:
            reminders[idx]["text"] = text
        update_user(message.from_user.id,{"reminders":reminders})
        await message.answer("✅",reply_markup=back_kb(lang))
    await state.set_state(S.reminder)

async def schedule_reminder(chat_id, hour, minute, text, lang="en", repeat=False):
    while True:
        now = datetime.now()
        if now.hour==hour and now.minute==minute:
            try:
                msg = t("rem_notify",lang).replace("{text}",text)
                await bot.send_message(chat_id,msg)
            except: pass
            if not repeat: break
            await asyncio.sleep(61)
        await asyncio.sleep(30)


async def restore_reminders():
    """Bot qayta ishga tushganda SQLite'dagi eslatma va bugungi rejalarni
    qayta rejalashtiradi (aks holda restart'dan keyin yuborilmaydi)."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    for user in get_all_users():
        if user.get("blocked"):
            continue
        uid  = user["uid"]
        lang = user.get("lang", "en")

        # Saqlangan eslatmalar
        for r in user.get("reminders", []):
            try:
                hour   = int(r.get("hour", 9))
                minute = int(r.get("minute", 0))
            except (TypeError, ValueError):
                continue
            repeat  = bool(r.get("repeat"))
            chat_id = r.get("chat_id", uid)
            text    = r.get("text", "")
            # Bir martalik bo'lib, vaqti o'tib ketgan bo'lsa — o'tkazamiz
            if not repeat:
                try:
                    dt = datetime.strptime(r.get("datetime", ""), "%d.%m.%Y %H:%M")
                    if dt < now:
                        continue
                except (ValueError, TypeError):
                    pass
            asyncio.create_task(
                schedule_reminder(chat_id, hour, minute, text, lang=lang, repeat=repeat)
            )

        # Bugungi rejalar (faqat hali vaqti kelmaganlari)
        plans = user.get("plans", {})
        if isinstance(plans, dict):
            for p in plans.get(today, []):
                tm = p.get("time")
                if tm and ":" in str(tm):
                    try:
                        h, m = map(int, str(tm).split(":"))
                    except ValueError:
                        continue
                    if (h, m) <= (now.hour, now.minute):
                        continue  # bugun allaqachon o'tgan
                    asyncio.create_task(
                        schedule_reminder(uid, h, m, f"📅 {p.get('task','')}", lang=lang)
                    )


# ============================================================
# OB-HAVO
# ============================================================
W_ICONS  = {"Clear":"☀️","Clouds":"☁️","Rain":"🌧️","Drizzle":"🌦️","Snow":"❄️","Thunderstorm":"⛈️","Mist":"🌫️","Fog":"🌫️"}
W_LABELS = {
    "uz":{"temp":"Harorat","feels":"His qilish","humidity":"Namlik","wind":"Shamol","pressure":"Bosim","desc":"Holat"},
    "en":{"temp":"Temperature","feels":"Feels like","humidity":"Humidity","wind":"Wind","pressure":"Pressure","desc":"Condition"},
    "ru":{"temp":"Температура","feels":"Ощущается","humidity":"Влажность","wind":"Ветер","pressure":"Давление","desc":"Состояние"},
    "ar":{"temp":"الحرارة","feels":"الإحساس","humidity":"الرطوبة","wind":"الريح","pressure":"الضغط","desc":"الحالة"},
    "tr":{"temp":"Sıcaklık","feels":"Hissedilen","humidity":"Nem","wind":"Rüzgar","pressure":"Basınç","desc":"Durum"},
    "es":{"temp":"Temperatura","feels":"Sensación","humidity":"Humedad","wind":"Viento","pressure":"Presión","desc":"Condición"},
    "hi":{"temp":"तापमान","feels":"महसूस","humidity":"आर्द्रता","wind":"हवा","pressure":"दबाव","desc":"स्थिति"},
}
W_API_LANG = {"uz":"en","en":"en","ru":"ru","ar":"ar","tr":"tr","es":"es","hi":"hi"}

async def weather_input(message, lang):
    city_raw = message.text.strip()
    city     = normalize_city(city_raw)
    api_lang = W_API_LANG.get(lang,"en")
    labels   = W_LABELS.get(lang,W_LABELS["en"])
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API}&units=metric&lang={api_lang}"
            ) as r:
                data = await r.json()
        if data.get("cod")!=200: raise Exception()
        await message.answer(
            f"{W_ICONS.get(data['weather'][0]['main'],'🌡️')} {data['name']}\n\n"
            f"🌡️ {labels['temp']}: {data['main']['temp']:.1f}°C\n"
            f"🤔 {labels['feels']}: {data['main']['feels_like']:.1f}°C\n"
            f"💧 {labels['humidity']}: {data['main']['humidity']}%\n"
            f"💨 {labels['wind']}: {data['wind']['speed']} m/s\n"
            f"🔵 {labels['pressure']}: {data['main']['pressure']} hPa\n"
            f"📝 {labels['desc']}: {data['weather'][0]['description'].capitalize()}\n\n"
            f"{t('stay_hint',lang)}",
            reply_markup=back_kb(lang)
        )
    except:
        await message.answer(f"❌ {city_raw}\nToshkent, Moscow, Dubai",reply_markup=back_kb(lang))

# ============================================================
# VALYUTA
# ============================================================
async def currency_input(message, lang):
    try:
        parts  = message.text.strip().split()
        amount = float(parts[-2].replace(",","").replace(" ", ""))
        from_c = normalize_currency(" ".join(parts[1:-1]) if len(parts)>3 else parts[1])
        to_c   = normalize_currency(parts[-1])
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.exchangerate-api.com/v4/latest/{from_c}") as r:
                data = await r.json()
        if "rates" not in data or to_c not in data["rates"]: raise Exception()
        rate   = data["rates"][to_c]
        result = amount*rate
        extra  = "\n"
        for c in POPULAR[:5]:
            if c not in [from_c,to_c] and c in data["rates"]:
                v = amount*data["rates"][c] if from_c=="USD" else amount/data["rates"].get(from_c,1)*data["rates"][c]
                extra += f"▪️ {v:,.2f} {c}\n"
        await message.answer(
            f"💱 {amount:,.2f} {from_c} = {result:,.2f} {to_c}\n"
            f"1 {from_c} = {rate:.4f} {to_c}{extra}\n{t('stay_hint',lang)}",
            reply_markup=back_kb(lang)
        )
    except:
        await message.answer(t("sec_currency",lang), reply_markup=back_kb(lang))

# ============================================================
# AI
# ============================================================
AI_SYSTEM = {
    "uz":"Siz o'zbek tilida javob beradigan yordamchi assistantsiz. Aniq va foydali javob bering. Zararli so'rovlarga javob bermang.",
    "en":"You are a helpful assistant. Give concise and accurate answers in English. Do not respond to harmful requests.",
    "ru":"Вы полезный ассистент. Давайте краткие и точные ответы на русском. Не отвечайте на вредные запросы.",
    "ar":"أنت مساعد مفيد. أعط إجابات موجزة باللغة العربية. لا تجب على الطلبات الضارة.",
    "tr":"Yardımcı bir asistansınız. Türkçe kısa ve doğru cevaplar verin. Zararlı isteklere cevap vermeyin.",
    "es":"Eres un asistente útil. Da respuestas concisas en español. No respondas a solicitudes dañinas.",
    "hi":"आप एक सहायक हैं। हिंदी में संक्षिप्त उत्तर दें। हानिकारक अनुरोधों का जवाब न दें।"
}

async def ai_input(message, user, lang):
    thinking = await message.answer("⏳")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GROQ_URL,
                headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
                json={"model":GROQ_MODEL,"messages":[
                    {"role":"system","content":AI_SYSTEM.get(lang,AI_SYSTEM["en"])},
                    {"role":"user","content":message.text}
                ],"max_tokens":1024,"temperature":0.7}
            ) as r:
                data = await r.json()
        ai_text = data["choices"][0]["message"]["content"]
        await thinking.delete()
        await message.answer(f"🤖 {ai_text}\n\n{t('stay_hint',lang)}",reply_markup=back_kb(lang))
    except:
        await thinking.delete()
        await message.answer("❌",reply_markup=back_kb(lang))

# ============================================================
# SCHEDULERLAR
# ============================================================
async def morning_quotes_scheduler():
    while True:
        now      = datetime.now()
        settings = load_settings()
        if not settings.get("quote_enabled",True):
            await asyncio.sleep(60)
            continue
        h,m = map(int,settings.get("quote_time","08:00").split(":"))
        if now.hour==h and now.minute==m:
            data   = load_data()
            quotes = settings.get("motivational_quotes",{})
            for uid,user in data.items():
                if user.get("blocked"): continue
                lang   = user.get("lang","en")
                q_list = quotes.get(lang,quotes.get("en",[]))
                if q_list:
                    quote = random.choice(q_list)
                    try:
                        msg = t("morning_q",lang).replace("{quote}",quote)
                        await bot.send_message(int(uid),msg)
                    except: pass
            await asyncio.sleep(61)
        await asyncio.sleep(30)

async def weekly_report_scheduler():
    while True:
        now      = datetime.now()
        settings = load_settings()
        if not settings.get("weekly_report_enabled",True):
            await asyncio.sleep(60)
            continue
        if now.weekday()==5 and now.hour==20 and now.minute==0:
            data     = load_data()
            week_ago = (now-timedelta(days=7)).strftime("%Y-%m-%d")
            for uid,user in data.items():
                if user.get("blocked"): continue
                lang     = user.get("lang","en")
                expenses = user.get("expenses",[])
                week_exp = [e for e in expenses if e.get("date","")>=week_ago]
                if not week_exp: continue
                by_curr  = {}
                for e in week_exp:
                    c = e.get("currency","UZS")
                    by_curr[c] = by_curr.get(c,0)+e["amount"]
                exp_text = "\n".join(f"▪️ {tot:,.0f} {c}" for c,tot in by_curr.items())
                msg = t("weekly_rep",lang).replace("{exp}",exp_text).replace("{n}",str(len(week_exp)))
                try:
                    await bot.send_message(int(uid),msg)
                except: pass
            await asyncio.sleep(61)
        await asyncio.sleep(30)

async def scheduled_ads_checker():
    while True:
        settings = load_settings()
        ads      = settings.get("scheduled_ads",[])
        now_str  = datetime.now().strftime("%Y-%m-%d %H:%M")
        updated  = False
        for ad in ads:
            if ad.get("send_at")==now_str and not ad.get("sent"):
                data = load_data()
                for uid,user in data.items():
                    if user.get("blocked"): continue
                    ad_lang = ad.get("lang","all")
                    if ad_lang!="all" and user.get("lang")!=ad_lang: continue
                    try:
                        if ad.get("photo"):
                            await bot.send_photo(int(uid),ad["photo"],caption=ad.get("text",""))
                        elif ad.get("video"):
                            await bot.send_video(int(uid),ad["video"],caption=ad.get("text",""))
                        else:
                            await bot.send_message(int(uid),ad.get("text",""))
                    except: pass
                    await asyncio.sleep(0.05)
                ad["sent"] = True
                updated = True
        if updated:
            save_settings(settings)
        await asyncio.sleep(30)




async def evening_report_scheduler():
    while True:
        now = datetime.now()
        if now.hour == 21 and now.minute == 0:
            today = now.strftime("%Y-%m-%d")
            for user in get_all_users():
                if user.get("blocked"):
                    continue
                uid  = user["uid"]
                lang = user.get("lang", "en")
                expenses = user.get("expenses", [])
                plans    = user.get("plans", {})
                if isinstance(plans, list):
                    plans = {}

                today_exp   = [e for e in expenses if e.get("date", "").startswith(today)]
                today_plans = plans.get(today, [])

                if not today_exp and not today_plans:
                    continue

                by_curr = {}
                for e in today_exp:
                    c = e.get("currency", "UZS")
                    by_curr[c] = by_curr.get(c, 0) + e["amount"]

                done  = sum(1 for p in today_plans if p.get("done"))
                total = len(today_plans)

                if by_curr:
                    exp_text = "\n".join(f"▪️ {v:,.0f} {c}" for c, v in by_curr.items())
                else:
                    exp_text = "—"

                report = {
                    "uz": f"🌙 Kunlik hisobot\n\n💸 Bugungi xarajatlar:\n{exp_text}\n\n📋 Vazifalar: {done}/{total} ✓",
                    "en": f"🌙 Daily Report\n\n💸 Today's expenses:\n{exp_text}\n\n📋 Tasks: {done}/{total} ✓",
                    "ru": f"🌙 Дневной отчёт\n\n💸 Расходы сегодня:\n{exp_text}\n\n📋 Задачи: {done}/{total} ✓",
                    "ar": f"🌙 التقرير اليومي\n\n💸 مصروفات اليوم:\n{exp_text}\n\n📋 المهام: {done}/{total} ✓",
                    "tr": f"🌙 Günlük Rapor\n\n💸 Bugünkü harcamalar:\n{exp_text}\n\n📋 Görevler: {done}/{total} ✓",
                    "es": f"🌙 Informe Diario\n\n💸 Gastos de hoy:\n{exp_text}\n\n📋 Tareas: {done}/{total} ✓",
                    "hi": f"🌙 दैनिक रिपोर्ट\n\n💸 आज के खर्च:\n{exp_text}\n\n📋 कार्य: {done}/{total} ✓",
                }
                try:
                    await bot.send_message(int(uid), report.get(lang, report["en"]))
                except:
                    pass
                await asyncio.sleep(0.05)
            await asyncio.sleep(61)
        await asyncio.sleep(30)
# ============================================================
# MAIN
# ============================================================
async def main():
    from admin import register_admin_handlers
    from tariffs import register_tariff_handlers
    from referral import register_referral_handlers
    from ai_functions import register_ai_handlers

    register_admin_handlers(dp, bot)
    register_tariff_handlers(dp, bot)
    register_referral_handlers(dp, bot)
    register_ai_handlers(dp, bot)
    await set_commands()
    print(f"🚀 {BOT_NAME} ishga tushdi!")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())