import asyncio
import random
import time
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, PollAnswerHandler, ContextTypes
)

# LOG SİSTEMİ
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# 🔑 YENİ VE GÜNCEL TOKEN
BOT_TOKEN = "8674782699:AAFfax8p4YIcyYdu7DH6LhuPDlJCw5ALTV4"
leaderboard = {}

# ─────────────────────────────────────────────
#  İYUK TAM SORU LİSTESİ (25/25)
# ─────────────────────────────────────────────
IYUK_SORU_SETI = [
    {"question": "İdari davalar hangi şekilde görülmektedir?", "options": ["Sözlü duruşmalar ile", "Yazılı yargılama usulü ile", "Bilgisayar üzerinden", "Mahkemenin seçtiği yöntemle"], "correct_option_id": 1, "explanation": "📖 İdari mahkemelerde yazılı yargılama esastır."},
    {"question": "Vergiye karşı dava açmak istenirse, süre ne zaman başlar?", "options": ["Rapor verildiğinde", "Verginin tahsil/ödendiği tarihten", "İtiraz yapıldığında", "Bildirimden sonraki gün"], "correct_option_id": 1, "explanation": "📖 Süre; tahsil, ödeme veya bildirimden itibaren başlar."},
    {"question": "İdareye başvurup 30 gün cevap alınmazsa ne olur?", "options": ["Başvuru kabul edilmiş sayılır", "Başvuru reddedilmiş sayılır", "İdareye 30 gün ek süre verilir", "Hukuki sonuç doğmaz"], "correct_option_id": 1, "explanation": "📖 30 gün sessizlik red (zımni ret) sayılır."},
    {"question": "Dava dilekçesi ilk olarak hangi noktalardan incelenir?", "options": ["İmza ve adres kontrolü", "Görev, yetki, süre ve usul kuralları", "Tarafların kimlik bilgileri", "Davacının ekonomik durumu"], "correct_option_id": 1, "explanation": "📖 İlk inceleme görev, yetki ve süre üzerinden yapılır."},
    {"question": "Tam yargı davasında uyuşmazlık miktarı nasıl artırılabilir?", "options": ["Hiçbir şekilde artırılamaz", "Yeni harç ödeyerek bir defaya mahsus", "Yeni dava açarak", "Hakimden izin alarak"], "correct_option_id": 1, "explanation": "📖 Harcı ödenerek miktar bir kez artırılabilir."},
    {"question": "Duruşma yapılması zorunlu olan davalarda sınır kaçtır?", "options": ["10.000 TL üzeri", "30.000 TL üzeri", "25.000 TL üzeri", "50.000 TL üzeri"], "correct_option_id": 2, "explanation": "📖 25.000 TL ve üzeri davalarda duruşma zorunludur."},
    {"question": "İvedi (Hızlı) yargılamaya tabi davalar hangileridir?", "options": ["Tazminat davaları", "İhale, kamulaştırma ve çevre kararları", "Vergilendirme işlemleri", "Emeklilik davaları"], "correct_option_id": 1, "explanation": "📖 İhale ve özelleştirme işleri ivedidir."},
    {"question": "Yürütmenin durdurulması kararı ne zaman verilir?", "options": ["İstendiği her zaman", "Ağır zarar ve açık hukuka aykırılık varsa", "İdare izin verirse", "Hiçbir zaman"], "correct_option_id": 1, "explanation": "📖 İki şartın birlikte gerçekleşmesi gerekir."},
    {"question": "Atama/görev değişikliği işlemleri neden özel şartlara tabidir?", "options": ["İşlemler çok önemli olduğu için", "Uygulanmakla etkisi tükenecek işlem sayılmadığı için", "İdare hızlı yaptığı için", "Gelir kaybı olacağı için"], "correct_option_id": 1, "explanation": "📖 Etkisi tükenecek işlem sayılmadığı için savunma alınmadan karar verilmez."},
    {"question": "Mahkeme kararı idarece en geç kaç günde uygulanmalıdır?", "options": ["15 gün", "30 gün", "60 gün", "90 gün"], "correct_option_id": 1, "explanation": "📖 İdare kararı 30 gün içinde uygulamalıdır."},
    {"question": "İdari davada genel yetkili mahkeme hangisidir?", "options": ["Danıştay", "Davanın açıldığı il", "İşlemi yapan idari birimin yeri", "Davacının oturduğu yer"], "correct_option_id": 2, "explanation": "📖 Yetki kuralı: İşlemi yapan mercinin yeridir."},
    {"question": "Taşınmaz (ev, arsa) davalarında yetkili mahkeme neresidir?", "options": ["Davacının bulunduğu yer", "Taşınmazın bulunduğu yer", "En yakın büyükşehir", "Danıştay"], "correct_option_id": 1, "explanation": "📖 Taşınmazın bulunduğu yer yetkilidir."},
    {"question": "Bağlantılı davalar ne demektir?", "options": ["Aynı davacının tüm davaları", "Aynı anda açılan davalar", "Birbirinin sonucunu etkileyen davalar", "Aynı idareye karşı tüm davalar"], "correct_option_id": 2, "explanation": "📖 Birbirinin sonucuna bağlı davalardır."},
    {"question": "İstinaf (yüksek mahkeme) yolu hangi davalar için kapalıdır?", "options": ["Hiçbir dava için", "Belirli parasal limit altındaki davalar", "Sadece emeklilik", "Sadece taşınmaz"], "correct_option_id": 1, "explanation": "📖 Limit altındaki davalar kesin karardır."},
    {"question": "Temyiz (Danıştay) hakkı hangi konularda sınırlıdır?", "options": ["Tüm davalarda", "Çevre, kültür ve seçim gibi önemli konular", "Sadece emeklilik", "Sadece vergi"], "correct_option_id": 1, "explanation": "📖 Sadece kanunda sayılan konular temyiz edilebilir."},
    {"question": "Temyiz dilekçesi eksiklikleri kaç günde tamamlanmalıdır?", "options": ["7 gün", "15 gün", "30 gün", "60 gün"], "correct_option_id": 1, "explanation": "📖 Eksiklik tamamlama süresi 15 gündür."},
    {"question": "Danıştay mahkeme kararını hangi sebeple bozabilir?", "options": ["Asla bozamaz", "Yetki dışı işe bakma veya hukuka aykırılık", "Davacının isteğiyle", "Gerekçe yazılmamışsa"], "correct_option_id": 1, "explanation": "📖 Hukuka aykırılık ve görev hatası bozma sebebidir."},
    {"question": "Kanun yararına temyiz hakkı kime verilmiştir?", "options": ["Davacılara", "Danıştay hakimlerine", "Başsavcı ve ilgili bakanlıklara", "Mahkeme başkanlarına"], "correct_option_id": 2, "explanation": "📖 Başsavcı veya Bakanlık bu yolu kullanabilir."},
    {"question": "Yargılamanın yenilenmesi ne zaman istenir?", "options": ["Asla istenmez", "Sahte belge veya bilirkişi yalanı gibi durumlarda", "Her zaman", "Sadece 1 yıl içinde"], "correct_option_id": 1, "explanation": "📖 Ağır usul hataları ve sahtecilik durumunda istenir."},
    {"question": "Merkezi sınavlara (KPSS vb.) karşı davalar nasıl ilerler?", "options": ["30 günde", "Hızlı sonuçlandırılır (10 gün ilk inceleme)", "Çabuk işlem yok", "Dava açılamaz"], "correct_option_id": 1, "explanation": "📖 Sınav davaları ivedi usule tabidir."},
    {"question": "Askerlik işlemlerine karşı dava nerede açılmalıdır?", "options": ["Danıştay", "Davacının evi", "Görev yaptığı bölge mahkemesinde", "Ankara"], "correct_option_id": 2, "explanation": "📖 Personelin görev yeri mahkemesi yetkilidir."},
    {"question": "İYUK'ta hüküm yoksa hangi kanun kuralları geçerlidir?", "options": ["Ceza Kanunu", "Medeni Kanun", "Hukuk Usulü Muhakemeleri Kanunu", "Hakimin kendi yargısı"], "correct_option_id": 2, "explanation": "📖 İYUK'ta hüküm yoksa HMK uygulanır."},
    {"question": "Emekli edilen memurun davası nerede açılmalıdır?", "options": ["Ankara", "Son çalıştığı yer mahkemesi", "En yakın büyükşehir", "İkametgahı"], "correct_option_id": 1, "explanation": "📖 Son görev yeri yetkilidir."},
    {"question": "Mahkemeler hangi tarihlerde çalışmaya ara verir?", "options": ["Haziran-Ağustos", "Temmuz-Eylül", "20 Temmuz - 31 Ağustos", "Mayıs-Haziran"], "correct_option_id": 2, "explanation": "📖 Ara verme 20 Temmuz - 31 Ağustos arasıdır."},
    {"question": "Deprem bölgesi hasar davalarında istinaf süresi kaçtır?", "options": ["30 gün", "20 gün", "15 gün", "10 gün"], "correct_option_id": 2, "explanation": "📖 Özel düzenleme gereği 15 gündür."}
]

# ─────────────────────────────────────────────
#  TAKILMAZ SİSTEM (CLAUDE FIX)
# ─────────────────────────────────────────────

async def send_next_question(context, chat_id):
    quiz = context.user_data.get("quiz")
    if not quiz or not quiz["active"]: return

    try:
        q = quiz["questions"][quiz["current"]]
        await context.bot.send_poll(
            chat_id=chat_id,
            question=f"⚖️ Soru {quiz['current'] + 1}/25\n\n{q['question']}",
            options=q["options"],
            type="quiz",
            correct_option_id=q["correct_option_id"],
            explanation=q["explanation"],
            is_anonymous=False,
            open_period=30
        )
        quiz["answered"] = False
    except Exception as e:
        logging.error(f"Soru hatası: {e}")
        await asyncio.sleep(2)
        await send_next_question(context, chat_id)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.user_data.clear()
    
    msg = await update.message.reply_text("⏳ *İYUK Final Game Başlıyor...*\n10 saniye sonra ilk soru gelecek.", parse_mode="Markdown")
    await asyncio.sleep(10)
    try: await msg.delete()
    except: pass
    
    shuffled = IYUK_SORU_SETI.copy()
    random.shuffle(shuffled)
    
    context.user_data["quiz"] = {
        "active": True, "questions": shuffled, "current": 0, "score": 0,
        "chat_id": chat_id, "start_time": time.time(), "user_id": update.effective_user.id,
        "user_name": update.effective_user.full_name, "answered": False
    }
    await send_next_question(context, chat_id)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz = context.user_data.get("quiz")
    if not quiz or not quiz["active"] or quiz.get("answered"): return

    quiz["answered"] = True
    if update.poll_answer.option_ids[0] == quiz["questions"][quiz["current"]]["correct_option_id"]:
        quiz["score"] += 1

    quiz["current"] += 1
    await asyncio.sleep(3) # Telegram limit koruması

    if quiz["current"] < 25:
        await send_next_question(context, quiz["chat_id"])
    else:
        sure = int(time.time() - quiz["start_time"])
        leaderboard[quiz["user_id"]] = {"name": quiz["user_name"], "score": quiz["score"], "sure": sure}
        sorted_board = sorted(leaderboard.values(), key=lambda x: (-x["score"], x["sure"]))
        
        msg = "🏆 *FINAL GAME (İYUK) LİDERLİK TABLOSU*\n\n"
        for i, p in enumerate(sorted_board[:10], 1):
            msg += f"{i}. {p['name']} — ✅ {p['score']}/25 | ⏱ {p['sure']}sn\n"
        
        await context.bot.send_message(quiz["chat_id"], msg, parse_mode="Markdown")
        quiz["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("quiz", start_game))
    app.add_handler(CommandHandler("start", start_game))
    app.add_handler(PollAnswerHandler(handle_answer))
    
    # ESKİ CMK KALINTILARINI TEMİZLEMEK İÇİN EN ÖNEMLİ SATIR:
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
  
