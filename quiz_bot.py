import asyncio
import random
import time
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    PollAnswerHandler,
    ContextTypes
)

# LOG SİSTEMİ
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# BOT AYARLARI
BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"
leaderboard = {}

# ─────────────────────────────────────────────
#  İYUK TAM SORU SETİ (25 SORU - GENİŞ FORMAT)
# ─────────────────────────────────────────────
IYUK_SORU_SETI = [
    {
        "question": "İdari davalar hangi şekilde görülmektedir?",
        "options": ["Sözlü duruşmalar ile", "Yazılı yargılama usulü ile", "Bilgisayar üzerinden", "Mahkemenin seçtiği yöntemle"],
        "correct_option_id": 1,
        "explanation": "📖 İdari mahkemelerde yazılı yargılama esastır."
    },
    {
        "question": "Vergiye karşı dava açmak istenirse, süre ne zaman başlar?",
        "options": ["Rapor verildiğinde", "Verginin tahsil/ödendiği tarihten", "İtiraz yapıldığında", "Bildirimden sonraki gün"],
        "correct_option_id": 1,
        "explanation": "📖 Süre; tahsil, ödeme veya bildirimden itibaren başlar."
    },
    {
        "question": "İdareye başvurup 30 gün cevap alınmazsa ne olur?",
        "options": ["Başvuru kabul edilmiş sayılır", "Başvuru reddedilmiş sayılır", "İdareye 30 gün ek süre verilir", "Hukuki sonuç doğmaz"],
        "correct_option_id": 1,
        "explanation": "📖 30 gün sessizlik red (zımni ret) sayılır."
    },
    {
        "question": "Dava dilekçesi ilk olarak hangi noktalardan incelenir?",
        "options": ["İmza ve adres kontrolü", "Görev, yetki, süre ve usul kuralları", "Tarafların kimlik bilgileri", "Davacının ekonomik durumu"],
        "correct_option_id": 1,
        "explanation": "📖 İlk inceleme görev, yetki ve süre üzerinden yapılır."
    },
    {
        "question": "Tam yargı davasında uyuşmazlık miktarı nasıl artırılabilir?",
        "options": ["Hiçbir şekilde artırılamaz", "Yeni harç ödeyerek bir defaya mahsus", "Yeni dava açarak", "Hakimden izin alarak"],
        "correct_option_id": 1,
        "explanation": "📖 Harcı ödenerek miktar bir kez artırılabilir."
    },
    {
        "question": "Duruşma yapılması zorunlu olan davalarda sınır kaçtır?",
        "options": ["10.000 TL üzeri", "30.000 TL üzeri", "25.000 TL üzeri", "50.000 TL üzeri"],
        "correct_option_id": 2,
        "explanation": "📖 25.000 TL ve üzeri davalarda duruşma zorunludur."
    },
    {
        "question": "İvedi (Hızlı) yargılamaya tabi davalar hangileridir?",
        "options": ["Tazminat davaları", "İhale, kamulaştırma ve çevre kararları", "Vergilendirme işlemleri", "Emeklilik davaları"],
        "correct_option_id": 1,
        "explanation": "📖 İhale ve özelleştirme işleri ivedidir."
    },
    {
        "question": "Yürütmenin durdurulması kararı ne zaman verilir?",
        "options": ["İstendiği her zaman", "Ağır zarar ve açık hukuka aykırılık varsa", "İdare izin verirse", "Hiçbir zaman"],
        "correct_option_id": 1,
        "explanation": "📖 İki şartın birlikte gerçekleşmesi gerekir."
    },
    {
        "question": "Atama/görev değişikliği işlemleri neden özel şartlara tabidir?",
        "options": ["İşlemler çok önemli olduğu için", "Uygulanmakla etkisi tükenecek işlem sayılmadığı için", "İdare hızlı yaptığı için", "Gelir kaybı olacağı için"],
        "correct_option_id": 1,
        "explanation": "📖 Etkisi tükenecek işlem sayılmadığı için savunma alınmadan karar verilmez."
    },
    {
        "question": "Mahkeme kararı idarece en geç kaç günde uygulanmalıdır?",
        "options": ["15 gün", "30 gün", "60 gün", "90 gün"],
        "correct_option_id": 1,
        "explanation": "📖 İdare kararı 30 gün içinde uygulamalıdır."
    },
    {
        "question": "İdari davada genel yetkili mahkeme hangisidir?",
        "options": ["Danıştay", "Davanın açıldığı il", "İşlemi yapan idari birimin yeri", "Davacının oturduğu yer"],
        "correct_option_id": 2,
        "explanation": "📖 Yetki kuralı: İşlemi yapan mercinin yeridir."
    },
    {
        "question": "Taşınmaz (ev, arsa) davalarında yetkili mahkeme neresidir?",
        "options": ["Davacının bulunduğu yer", "Taşınmazın bulunduğu yer", "En yakın büyükşehir", "Danıştay"],
        "correct_option_id": 1,
        "explanation": "📖 Taşınmazın bulunduğu yer yetkilidir."
    },
    {
        "question": "Bağlantılı davalar ne demektir?",
        "options": ["Aynı davacının tüm davaları", "Aynı anda açılan davalar", "Birbirinin sonucunu etkileyen davalar", "Aynı idareye karşı tüm davalar"],
        "correct_option_id": 2,
        "explanation": "📖 Birbirinin sonucuna bağlı davalardır."
    },
    {
        "question": "İstinaf (yüksek mahkeme) yolu hangi davalar için kapalıdır?",
        "options": ["Hiçbir dava için", "Belirli parasal limit altındaki davalar", "Sadece emeklilik", "Sadece taşınmaz"],
        "correct_option_id": 1,
        "explanation": "📖 Limit altındaki davalar kesin karardır."
    },
    {
        "question": "Temyiz (Danıştay) hakkı hangi konularda sınırlıdır?",
        "options": ["Tüm davalarda", "Çevre, kültür ve seçim gibi önemli konular", "Sadece emeklilik", "Sadece vergi"],
        "correct_option_id": 1,
        "explanation": "📖 Sadece kanunda sayılan konular temyiz edilebilir."
    },
    {
        "question": "Temyiz dilekçesi eksiklikleri kaç günde tamamlanmalıdır?",
        "options": ["7 gün", "15 gün", "30 gün", "60 gün"],
        "correct_option_id": 1,
        "explanation": "📖 Eksiklik tamamlama süresi 15 gündür."
    },
    {
        "question": "Danıştay mahkeme kararını hangi sebeple bozabilir?",
        "options": ["Asla bozamaz", "Yetki dışı işe bakma veya hukuka aykırılık", "Davacının isteğiyle", "Gerekçe yazılmamışsa"],
        "correct_option_id": 1,
        "explanation": "📖 Hukuka aykırılık ve görev hatası bozma sebebidir."
    },
    {
        "question": "Kanun yararına temyiz hakkı kime verilmiştir?",
        "options": ["Davacılara", "Danıştay hakimlerine", "Başsavcı ve ilgili bakanlıklara", "Mahkeme başkanlarına"],
        "correct_option_id": 2,
        "explanation": "📖 Başsavcı veya Bakanlık bu yolu kullanabilir."
    },
    {
        "question": "Yargılamanın yenilenmesi ne zaman istenir?",
        "options": ["Asla istenmez", "Sahte belge veya bilirkişi yalanı gibi durumlarda", "Her zaman", "Sadece 1 yıl içinde"],
        "correct_option_id": 1,
        "explanation": "📖 Ağır usul hataları ve sahtecilik durumunda istenir."
    },
    {
        "question": "Merkezi sınavlara (KPSS vb.) karşı davalar nasıl ilerler?",
        "options": ["30 günde", "Hızlı sonuçlandırılır (10 gün ilk inceleme)", "Çabuk işlem yok", "Dava açılamaz"],
        "correct_option_id": 1,
        "explanation": "📖 Sınav davaları ivedi usule tabidir."
    },
    {
        "question": "Askerlik işlemlerine karşı dava nerede açılmalıdır?",
        "options": ["Danıştay", "Davacının evi", "Görev yaptığı bölge mahkemesinde", "Ankara"],
        "correct_option_id": 2,
        "explanation": "📖 Personelin görev yeri mahkemesi yetkilidir."
    },
    {
        "question": "İYUK'ta hüküm yoksa hangi kanun kuralları geçerlidir?",
        "options": ["Ceza Kanunu", "Medeni Kanun", "Hukuk Usulü Muhakemeleri Kanunu", "Hakimin kendi yargısı"],
        "correct_option_id": 2,
        "explanation": "📖 İYUK'ta hüküm yoksa HMK uygulanır."
    },
    {
        "question": "Emekli edilen memurun davası nerede açılmalıdır?",
        "options": ["Ankara", "Son çalıştığı yer mahkemesi", "En yakın büyükşehir", "İkametgahı"],
        "correct_option_id": 1,
        "explanation": "📖 Son görev yeri yetkilidir."
    },
    {
        "question": "Mahkemeler hangi tarihlerde çalışmaya ara verir?",
        "options": ["Haziran-Ağustos", "Temmuz-Eylül", "20 Temmuz - 31 Ağustos", "Mayıs-Haziran"],
        "correct_option_id": 2,
        "explanation": "📖 Ara verme 20 Temmuz - 31 Ağustos arasıdır."
    },
    {
        "question": "Deprem bölgesi hasar davalarında istinaf süresi kaçtır?",
        "options": ["30 gün", "20 gün", "15 gün", "10 gün"],
        "correct_option_id": 2,
        "explanation": "📖 Özel düzenleme gereği 15 gündür."
    }
]

# ─────────────────────────────────────────────
#  YÜKSEK GÜVENLİKLİ MEKANİZMA (CLAUDE KODU)
# ─────────────────────────────────────────────

async def send_next_question(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    quiz = context.user_data.get("quiz")
    if not quiz or not quiz["active"]:
        return

    try:
        current_q = quiz["questions"][quiz["current"]]
        
        # Kullanıcıya soruyu gönder
        await context.bot.send_poll(
            chat_id=chat_id,
            question=f"❓ Soru {quiz['current'] + 1}/25\n\n{current_q['question']}",
            options=current_q["options"],
            type="quiz",
            correct_option_id=current_q["correct_option_id"],
            explanation=current_q["explanation"],
            is_anonymous=False,
            open_period=30
        )
        
        # Bayrağı sıfırla (yeni cevap bekliyoruz)
        quiz["answered"] = False
        
    except Exception as e:
        logging.error(f"Soru gönderim hatası: {e}")
        await asyncio.sleep(2)
        await send_next_question(context, chat_id)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Eski verileri temizle
    context.user_data.clear()
    
    start_msg = await update.message.reply_text(
        f"⏳ *Hazırlan komiserim {user.first_name}!*\n\n"
        f"FINAL GAME (İYUK) 15 saniye içinde başlıyor...\n"
        f"Toplam: 25 Soru\nSüre: Soru başı 30 saniye",
        parse_mode="Markdown"
    )
    
    await asyncio.sleep(15)
    try:
        await start_msg.delete()
    except:
        pass

    # Soruları karıştır
    shuffled_questions = IYUK_SORU_SETI.copy()
    random.shuffle(shuffled_questions)

    # Quiz objesini oluştur
    context.user_data["quiz"] = {
        "active": True,
        "questions": shuffled_questions,
        "current": 0,
        "score": 0,
        "chat_id": chat_id,
        "start_time": time.time(),
        "user_id": user.id,
        "user_name": user.full_name,
        "answered": False
    }

    await send_next_question(context, chat_id)

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz = context.user_data.get("quiz")
    
    # Quiz aktif değilse veya bu soruya zaten cevap verildiyse çık
    if not quiz or not quiz["active"] or quiz["answered"]:
        return

    # Cevabı kilitle
    quiz["answered"] = True
    
    answer = update.poll_answer
    current_q = quiz["questions"][quiz["current"]]

    # Doğru cevabı kontrol et
    if answer.option_ids[0] == current_q["correct_option_id"]:
        quiz["score"] += 1

    # Bir sonraki soruya geçiş
    quiz["current"] += 1
    
    # Telegram hız limitlerini aşmamak için kısa bir bekleme
    await asyncio.sleep(3)

    if quiz["current"] < 25:
        await send_next_question(context, quiz["chat_id"])
    else:
        # Quiz bitti, liderlik tablosunu hazırla
        quiz["active"] = False
        end_time = time.time()
        duration = int(end_time - quiz["start_time"])
        
        # Skor kaydı
        user_id = quiz["user_id"]
        if user_id not in leaderboard or quiz["score"] > leaderboard[user_id]["score"]:
            leaderboard[user_id] = {
                "name": quiz["user_name"],
                "score": quiz["score"],
                "sure": duration
            }

        # Tablo mesajı
        sorted_board = sorted(
            leaderboard.values(),
            key=lambda x: (-x["score"], x["sure"])
        )
        
        msg = "🏆 *FINAL GAME (İYUK) SONUÇLARI*\n\n"
        for i, p in enumerate(sorted_board[:10], 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            msg += f"{medal} {p['name']} — ✅ {p['score']}/25 | ⏱ {p['sure']}sn\n"
        
        await context.bot.send_message(
            chat_id=quiz["chat_id"],
            text=msg,
            parse_mode="Markdown"
        )

def main():
    # Botu kur
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutları bağla
    app.add_handler(CommandHandler("start", start_game))
    app.add_handler(CommandHandler("quiz", start_game))
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    
    # Eski takılan güncellemeleri atla ve botu çalıştır
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
