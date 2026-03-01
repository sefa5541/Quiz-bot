import asyncio
import random
import time
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, PollAnswerHandler, ContextTypes
)

# 1. LOG SİSTEMİ
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. TOKEN
BOT_TOKEN = "8674782699:AAFfax8p4YIcyYdu7DH6LhuPDlJCw5ALTV4"
leaderboard = {}

# 3. İYUK TAM SORU SETİ (25 SORU)
IYUK_SORU_SETI = [
    {"question": "İdari davalar hangi şekilde görülmektedir?", "options": ["Sözlü duruşmalar", "Yazılı yargılama usulü", "Bilgisayar üzerinden", "Sözlü beyan"], "correct_option_id": 1, "explanation": "📖 İdari mahkemelerde yazılı yargılama esastır."},
    {"question": "Vergiye karşı dava açma süresi ne zaman başlar?", "options": ["Rapor tarihinde", "Tahsil/Ödeme/Tebliğ tarihinde", "İtiraz tarihinde", "Yıl sonunda"], "correct_option_id": 1, "explanation": "📖 Süre tebliğ veya ödeme ile başlar."},
    {"question": "İdareye başvurup 30 gün cevap alınmazsa ne olur?", "options": ["Kabul sayılır", "Reddedilmiş (zımni ret) sayılır", "Ek süre verilir", "Dava düşer"], "correct_option_id": 1, "explanation": "📖 30 gün sessizlik reddetmek demektir."},
    {"question": "Dilekçeler ilk olarak neye göre incelenir?", "options": ["İmza kontrolü", "Görev, yetki, süre ve usul", "Davacı geliri", "Avukat bilgisi"], "correct_option_id": 1, "explanation": "📖 İlk inceleme usul ve yetki üzerinden yapılır."},
    {"question": "Tam yargı davasında miktar nasıl artırılır?", "options": ["Artırılamaz", "Harcı ödenerek 1 defaya mahsus", "Yeni dava ile", "Dilekçe vererek her zaman"], "correct_option_id": 1, "explanation": "📖 Islah (miktar artırımı) bir kez yapılabilir."},
    {"question": "Duruşma zorunluluğu olan parasal sınır nedir?", "options": ["10.000 TL", "30.000 TL", "25.000 TL", "50.000 TL"], "correct_option_id": 2, "explanation": "📖 25.000 TL üzeri davalarda duruşma zorunludur."},
    {"question": "İvedi yargılamaya tabi işler hangileridir?", "options": ["Tazminat", "İhale, kamulaştırma ve çevre", "Vergi", "Memur atama"], "correct_option_id": 1, "explanation": "📖 İhale ve özelleştirme işleri ivedidir."},
    {"question": "Yürütmenin durdurulması şartları nelerdir?", "options": ["Sadece talep", "Ağır zarar ve açık hukuka aykırılık", "İdare onayı", "Hakim kararı"], "correct_option_id": 1, "explanation": "📖 İki şartın birlikte gerçekleşmesi şarttır."},
    {"question": "Mahkeme kararı idarece en geç kaç günde uygulanır?", "options": ["15 gün", "30 gün", "60 gün", "90 gün"], "correct_option_id": 1, "explanation": "📖 Kararlar 30 gün içinde uygulanmalıdır."},
    {"question": "Taşınmaz davalarında yetkili mahkeme neresidir?", "options": ["Davacının yeri", "Taşınmazın bulunduğu yer", "Ankara", "Danıştay"], "correct_option_id": 1, "explanation": "📖 Taşınmaz nerede ise mahkeme oradadır."},
    {"question": "Bağlantılı davalar nedir?", "options": ["Aynı davacı", "Aynı anda açılanlar", "Sonucu birbirini etkileyenler", "Aynı hakimdekiler"], "correct_option_id": 2, "explanation": "📖 Birbirine bağlı davalardır."},
    {"question": "İstinaf yolu hangi davalarda kapalıdır?", "options": ["Hiçbirinde", "Belirli sınırın altındaki davalarda", "Sadece vergi", "Sadece memur"], "correct_option_id": 1, "explanation": "📖 Parasal sınırın altı kesin karardır."},
    {"question": "Temyiz (Danıştay) süresi genellikle kaç gündür?", "options": ["15 gün", "30 gün", "60 gün", "7 gün"], "correct_option_id": 1, "explanation": "📖 Temyiz süresi genellikle 30 gündür."},
    {"question": "Temyiz dilekçesi eksikliği kaç günde giderilir?", "options": ["7 gün", "15 gün", "30 gün", "10 gün"], "correct_option_id": 1, "explanation": "📖 Eksiklik tamamlama süresi 15 gündür."},
    {"question": "Danıştay kararı hangi halde bozar?", "options": ["Her zaman", "Hukuka aykırılık ve görev hatası", "Keyfi olarak", "Gerekçe yoksa"], "correct_option_id": 1, "explanation": "📖 Kanuna aykırılık ana bozma sebebidir."},
    {"question": "Kanun yararına temyizi kim isteyebilir?", "options": ["Taraflar", "Hakimler", "Başsavcı ve Bakanlıklar", "Baro başkanı"], "correct_option_id": 2, "explanation": "📖 Bakanlık veya Başsavcı yetkilidir."},
    {"question": "Yargılamanın yenilenmesi ne zaman istenir?", "options": ["Karar beğenilmezse", "Sahtecilik ve ağır hata varsa", "Her yıl", "İdare isterse"], "correct_option_id": 1, "explanation": "📖 Sahte belge veya yalan beyan gerekir."},
    {"question": "Merkezi sınav davaları hangi usule tabidir?", "options": ["Normal", "İvedi (Hızlı) yargılama", "Sözlü", "Gizli"], "correct_option_id": 1, "explanation": "📖 Sınav davaları çok hızlı sonuçlandırılır."},
    {"question": "Askerlik işlemleri davası nerede açılır?", "options": ["Milli Savunma Bakanlığı", "Ankara", "Görev yeri mahkemesi", "Ev adresi"], "correct_option_id": 2, "explanation": "📖 Görev yapılan yer yetkilidir."},
    {"question": "İYUK'ta hüküm yoksa ne uygulanır?", "options": ["Anayasa", "Medeni Kanun", "Hukuk Muhakemeleri Kanunu (HMK)", "Ceza Kanunu"], "correct_option_id": 2, "explanation": "📖 İYUK madde 31 gereği HMK uygulanır."},
    {"question": "Emeklilik davası nerede açılır?", "options": ["Ankara", "Son görev yeri mahkemesi", "Davacının ikametgahı", "Danıştay"], "correct_option_id": 1, "explanation": "📖 Son görev yeri mahkemesi yetkilidir."},
    {"question": "Mahkemeler ne zaman ara verir?", "options": ["1 Ocak", "1 Temmuz", "20 Temmuz - 31 Ağustos", "15 Ağustos"], "correct_option_id": 2, "explanation": "📖 Adli tatil 20 Temmuz'da başlar."},
    {"question": "Deprem bölgesi davalarında istinaf süresi?", "options": ["30 gün", "20 gün", "15 gün", "10 gün"], "correct_option_id": 2, "explanation": "📖 Özel durumdan dolayı 15 gündür."},
    {"question": "İdari sözleşmelerden doğan davalar nerede görülür?", "options": ["Asliye Hukuk", "İdari Yargı", "Tahkim", "Danıştay"], "correct_option_id": 1, "explanation": "📖 İdari sözleşmeler idari yargının işidir."},
    {"question": "Yürütmenin durdurulması kararına itiraz süresi?", "options": ["15 gün", "7 gün", "30 gün", "10 gün"], "correct_option_id": 1, "explanation": "📖 İtiraz süresi 7 gündür."}
]

# 4. YARDIMCI FONKSİYONLAR
async def send_q(context, chat_id, data):
    try:
        q = data["questions"][data["current"]]
        await context.bot.send_poll(
            chat_id=chat_id,
            question=f"❓ İYUK Soru {data['current'] + 1}/25\n\n{q['question']}",
            options=q["options"],
            type="quiz",
            correct_option_id=q["correct_option_id"],
            explanation=q["explanation"],
            is_anonymous=False
        )
        data["answered"] = False # Kilidi açtık
    except Exception as e:
        logging.error(f"Soru hatası: {e}")

# 5. ANA KOMUTLAR
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.user_data.clear()
    
    await update.message.reply_text("🚀 *İYUK FINAL GAME BAŞLIYOR!* \nSorular yükleniyor...", parse_mode="Markdown")
    
    shuffled = IYUK_SORU_SETI.copy()
    random.shuffle(shuffled)
    
    context.user_data["quiz"] = {
        "active": True, 
        "questions": shuffled, 
        "current": 0, 
        "score": 0,
        "chat_id": chat_id, 
        "start_time": time.time(), 
        "user_id": update.effective_user.id,
        "user_name": update.effective_user.full_name, 
        "answered": False
    }
    await send_q(context, chat_id, context.user_data["quiz"])

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kullanıcı verisini al
    data = context.user_data.get("quiz")
    
    # Güvenlik Kontrolleri
    if not data or not data.get("active"): return
    if data.get("answered"): return # Eğer bu soruya zaten cevap verildiyse işlem yapma

    # Cevabı işaretle
    data["answered"] = True
    
    # Skoru Güncelle
    if update.poll_answer.option_ids[0] == data["questions"][data["current"]]["correct_option_id"]:
        data["score"] += 1

    # Bir sonraki soruya geçiş
    data["current"] += 1
    
    # Kısa bir bekleme (Kullanıcı açıklamayı okusun)
    await asyncio.sleep(3)

    if data["current"] < len(data["questions"]):
        await send_q(context, data["chat_id"], data)
    else:
        # BİTİŞ PANELİ
        sure = int(time.time() - data["start_time"])
        leaderboard[data["user_id"]] = {"name": data["user_name"], "score": data["score"], "sure": sure}
        res = sorted(leaderboard.values(), key=lambda x: (-x["score"], x["sure"]))
        
        txt = "🏆 *İYUK ŞAMPİYONLARI*\n\n"
        for i, p in enumerate(res[:10], 1):
            txt += f"{i}. {p['name']} — ✅ {p['score']}/25 | ⏱ {p['sure']}sn\n"
        
        await context.bot.send_message(data["chat_id"], txt, parse_mode="Markdown")
        data["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutları Tanımla
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CommandHandler("start", start_quiz))
    app.add_handler(PollAnswerHandler(handle_answer))
    
    print("İYUK Bot Sorunsuz Modda Yayında!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
