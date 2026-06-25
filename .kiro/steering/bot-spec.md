# @Startdaily_bot — To'liq Funksional Spetsifikatsiya

> Bu hujjat botning kerakli ish mantig'ini tasvirlaydi (foydalanuvchi tomonidan berilgan).
> Kodlarni tekshirayotganda shu spetsifikatsiyaga moslikni tekshirish kerak.
> Eslatma: bu tavsif koddan biroz farq qilishi mumkin (kodga keyinchalik qo'shimchalar qilingan).

## Umumiy
- Bot nomi: `@Startdaily_bot`
- Ko'p tillilik: **uz, en, ru, ar (arab), tr (turk), es (ispan), hi (hind/india)** — jami 7 til.
- Til tanlash foydalanuvchining Telegram tiliga qarab boshlang'ich taklif qilinadi.

## Foydalanuvchi oqimi (Onboarding)
1. `/start` bosilganda — Telegram tiliga qarab "Tilni tanlang" matni + 7 ta til tugmasi (uz, en, ru, ar, tr, es, hi).
2. Til tanlangach — agar majburiy obuna sozlangan bo'lsa, foydalanuvchi tanlagan tilida majburiy obuna xabari chiqadi.
3. Foydalanuvchi obuna bo'lib "Tekshirish" tugmasini bosadi.
4. Obuna tasdiqlangach — o'z tilida **ommaviy oferta (foydalanish qoidalari)** chiqadi, "Qabul qilish" tugmasi bilan.
5. Qabul qilgach — tiliga mos "Xush kelibsiz" matni chiqadi.
6. Yangi foydalanuvchidan **ismi** va **yashayotgan shahri** so'raladi.

## Menu (chap tarafdagi ko'k "Menu" tugmasi / komandalar)
Buyruqlar: `/start`, `/ofera`, `/help`, `/setting`, `/profile` + bo'limlarni chaqiruvchi komandalar: xarajatlar, eslatmalar, valyuta, AI yordamchi, kunlik reja, namoz vaqti, ob-havo, admin.

## Asosiy tugmalar (foydalanuvchi)
Har bir bo'limda foydalanuvchi shu bo'lim ichida turib ishlaydi; istalgan paytda **"Asosiy menyu"** tugmasi orqali qaytadi.

### 1. Xarajatlar
- Foydalanuvchi xarajatini va summasini yozadi; **dunyoning istalgan valyutasi**.
- Valyutani qisqartma (UZS), nomi (so'm, dollar) yoki **davlat nomi** orqali ham qabul qilish kerak.
- Qanday yozish bo'yicha tushuntirish beriladi.
- Hisobotlar tugmalari: **Bugun, Hafta, Oy, Yil**.
- **Konvertatsiya** alohida tugma — turli valyutadagi xarajatlarni kerakli valyutaga aylantiradi (bu yerda ham qisqartma/nom/davlat qabul qilinadi).
- **Tozalash** tugmasi (oxirgi) — tasdiqlash so'raladi, tasdiqlansa barcha xarajatlar o'chiriladi.

### 2. Eslatmalar
- Foydalanuvchi yil/oy/kun + vaqt + matn kiritadi; belgilangan vaqtda bot matnni yuboradi.
- Faqat vaqt kiritilsa — bugungi kun hisoblanadi.
- So'rov: **bir martalik** yoki **har kuni shu vaqtda**.
- Eslatmalar saqlanadi.
- **Tozalash** tugmasi — tasdiqlash bilan barcha eslatmalarni o'chiradi.

### 3. Valyuta
- Qanday yozish bo'yicha qisqa tushuntirish.
- Qisqartma/nom/davlat nomi orqali valyuta kursi.

### 4. Kunlik reja
- Qanday yozish bo'yicha qisqa tushuntirish.
- Vaqt bilan yozilsa — eslatma kabi belgilangan vaqtda yuboriladi.

### 5. Namoz vaqti
- Istalgan tildagi shahar/davlat nomini qabul qiladi va shu shaharning namoz vaqtlarini beradi.

### 6. Ob-havo
- Istalgan tildagi shahar/davlat nomini qabul qiladi va shu shaharning ob-havosini beradi.

### 7. Profil
- Foydalanuvchining ismi, shahri, xarajatlar soni, eslatmalar soni, kunlik rejalar sonini ko'rsatadi.
- Pastida: **ismni tahrirlash** va **shaharni tahrirlash** tugmalari.

### 8. AI yordamchi
- Suhbatchi AI — foydalanuvchi savollariga javob oladi.

### 9. Admin (foydalanuvchi uchun)
- "Takliflar/murojaat/shikoyat bo'lsa adminga murojaat qiling" matni + admin Telegram username.
- "Bizni qo'llab-quvvatlash uchun donat qilishingiz mumkin" matni + donat havolasi.

### 10. Sozlamalar
- Joriy tilda "Tilni tanlang" + 7 ta til tugmasi — tilni almashtirish.

## ADMIN PANEL (`/admin` — faqat admin uchun)
Tugmalar: Statistika, Hammaga xabar, Reklama, Majburiy obuna, Motivatsion iqtibos, Xush kelibsiz xabarini tahrirlash, Tugmalardagi tushuntirish matnlarini tahrirlash, Ommaviy oferani tahrirlash, Admin matnini tahrirlash, Taqiqlangan so'zlar, Foydalanuvchilar, Ogohlantirish yuborish, Bloklash, Blokdan chiqarish.
Har bir tugma tagida **"Orqaga"** tugmasi (asosiy panelga qaytish).

### 1. Statistika
- Jami foydalanuvchilar, faol, bloklangan, bugungi, oxirgi 7 kun, oylik foydalanuvchilar soni.
- Tillar bo'yicha taqsimot (qaysi tilda nechta odam) — til bo'yicha ko'rish mumkin.
- Shaharlar bo'yicha taqsimot (onboarding'da so'ralgan shahar asosida).

### 2. Hammaga xabar (broadcast)
- Rasm/video/matn — barcha foydalanuvchilarga yuboriladi.

### 3. Reklama
- Til tanlash tugmalari + **"Hammaga"** tugmasi.
- Tanlangan tildagi foydalanuvchilarga rasm/video/matn yuboriladi.
- **Tozalash** tugmasi — tasdiqlash bilan barcha reklamalarni o'chiradi.
- **Vaqtli (rejalashtirilgan) xabarlar**: til + vaqt belgilab reklama kiritiladi, vaqti kelganda avtomatik yuboriladi.

### 4. Majburiy obuna
- Til tanlash + **"Hammaga"** tugmasi.
- Tanlangan tildagi (yoki hammaga) foydalanuvchiga kanal/guruh majburiy obunasi qo'shiladi.
- **Tozalash/belgilab o'chirish** — tasdiqlash bilan kanal/guruhlarni olib tashlash.
- Yangi majburiy obuna eski foydalanuvchilarga ham ta'sir qiladi: istalgan bo'lim bosilganda "Botdan foydalanish uchun obuna bo'ling" chiqadi.
- Har tugma tagida "Orqaga".

### 5. Motivatsion iqtibos
- Til tanlash + vaqt belgilash.
- Matnlar kiritiladi, belgilangan vaqtda (masalan, ertalab) foydalanuvchiga yuboriladi.
- Iqtiboslarni qo'shish/o'chirish/tahrirlash.

### 6. Xush kelibsiz xabarini tahrirlash
- Til tanlash + start'dagi xush kelibsiz matnini tahrirlash.

### 7. Tugmalardagi tushuntirish matnlarini tahrirlash
- Til tanlash + qaysi tugma tushuntirishini tanlash + matnni tahrirlash.

### 8. Ommaviy oferani tahrirlash
- Til tanlash + oferta matnini tahrirlash.

### 9. Admin tugmasi matnini tahrirlash
- Til tanlash + foydalanuvchi "Admin" bosganda chiqadigan matnni tahrirlash.

### 10. Taqiqlangan so'zlar
- So'zlarni qo'shish/tahrirlash/o'chirish.
- Taqiqlangan so'z yuborilsa, foydalanuvchiga o'z tilida ogohlantirish boradi.
- 3 marta ogohlantirish, 4-martada **avtomatik bloklash**.

### 11. Foydalanuvchilar
- Jami foydalanuvchilar soni + ularning Telegram ID lari (va imkon bo'lsa username).

### 12. Ogohlantirish yuborish
- ID yoki username orqali qo'lda ogohlantirish. Avtomatik ogohlantirish ham bor.
- Ogohlantirish foydalanuvchining tanlagan tilida yuboriladi.

### 13. Bloklash
- ID yoki username orqali qo'lda bloklash.
- Bloklanganda (qo'lda yoki avtomatik) foydalanuvchiga o'z tilida "Hisobingiz bloklandi" + adminga murojaat uchun username.

### 14. Blokdan chiqarish
- ID yoki username orqali blokdan chiqarish + foydalanuvchiga o'z tilida xabar.

## Kontent (yozilishi kerak)
- Tugmalar ichidagi tushuntirish matnlari.
- Ommaviy oferta matnlari (7 tilda).
