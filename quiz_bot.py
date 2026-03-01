import asyncio
import random
import time
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, PollAnswerHandler, ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# ⚠️ TOKEN'ı değiştirin! Bu token zaten public olmuştur, yeni bir tane alın
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
leaderboard = {}

# İYUK SORU SETİ (25 soru)
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
        "question": "Mahkemeye açılan dava dilekçesi ilk olarak hangi noktalardan incelenir?",
        "options": ["İmza ve adres kontrolü", "Görev, yetki, süre ve usul kuralları", "Tarafların kimlik bilgileri", "Davacının ekonomik durumu"],
        "correct_option_id": 1,
        "explanation": "📖 İlk inceleme görev, yetki ve süre üzerinden yapılır."
    },
    {
        "question": "Tam yargı davasında davacı uyuşmazlık miktarını nasıl artırabilir?",
        "options": ["Hiçbir şekilde artırılamaz", "Yeni harç ödeyerek bir defaya mahsus", "Yeni dava açarak", "Hakimden izin alarak"],
        "correct_option_id": 1,
        "explanation": "📖 Harcı ödenerek miktar bir kez artırılabilir."
    },
    {
        "question": "Duruşma yapılması zorunlu olan davalar hangi parasal sınırı aşmalıdır?",
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
        "question": "İdari davada hangi mahkeme yetkilidir? (Genel kural)",
        "options": ["Her zaman Danıştay", "Davanın açıldığı il", "İşlemi yapan idari birimin yeri", "Davacının oturduğu yer"],
        "correct_option_id": 2,
        "explanation": "📖 Yetki kuralı: İşlemi yapan mercinin yeridir."
    },
    {
        "question": "Bir evle ilgili belediye işleminden (ruhsat, imar) dava nerede açılır?",
        "options": ["Davacının evinin olduğu yer", "Evin bulunduğu yerdeki mahkemede", "En yakın büyükşehir", "Danıştayda"],
        "correct_option_id": 1,
        "explanation": "📖 Taşınmazın bulunduğu yer mahkemesi yetkilidir."
    },
    {
        "question": "Bağlantılı davalar ne demektir?",
        "options": ["Aynı davacının tüm davaları", "Aynı anda açılan davalar", "Aynı nedenlerden doğan veya sonucu birbirini etkileyen davalar", "Aynı idareye karşı tüm davalar"],
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
        "question": "Danıştay'da (TEMYİZ) başvuru yapılabilen davalar nelerdir?",
        "options": ["Tüm davalar", "Çevre, kültür, seçim gibi önemli konular", "Sadece emeklilik", "Sadece vergi"],
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
        "question": "Danıştay, mahkeme kararını hangi sebeple bozabilir?",
        "options": ["Asla bozamaz", "Yetki hatası veya yasalara aykırılık", "Davacının isteğiyle", "Gerekçe yazılmamışsa"],
        "correct_option_id": 1,
        "explanation": "📖 Hukuka aykırılık ve görev hatası bozma sebebidir."
    },
    {
        "question": "Kanun yararına temyiz hakkı kime verilmiştir?",
        "options": ["Davacılara", "Danıştay hakim ve savcılarına", "Başsavcı ve ilgili bakanlıklara", "Mahkeme başkanlarına"],
        "correct_option_id": 2,
        "explanation": "📖 Başsavcı veya Bakanlık bu yolu kullanabilir."
    },
    {
        "question": "Yargılamanın yeniden yapılması ne zaman istenir?",
        "options": ["Asla istenmez", "Sahte belge, yalan beyan gibi ciddi sebeplerde", "Her zaman", "Sadece 1 yıl içinde"],
        "correct_option_id": 1,
        "explanation": "📖 Ağır usul hataları ve sahtecilik durumunda istenir."
    },
    {
        "question": "Merkezi sınavlara (KPSS vb.) karşı davalar ne kadar çabuk sonuçlandırılır?",
        "options": ["30 günde", "Hızlı sonuçlandırılır (10 gün ilk inceleme)", "Çabuk işlem yok", "Dava açılamaz"],
        "correct_option_id": 1,
        "explanation": "📖 Sınav davaları ivedi usule tabidir."
    },
    {
        "question": "Askerlik işlemlerine karşı dava nerede açılmalıdır?",
        "options": ["Danıştay", "Davacının evi", "Görev yaptığı yerin bölgesi mahkemesinde", "Ankara"],
        "correct_option_id": 2,
        "explanation": "📖 Personelin görev yeri mahkemesi yetkilidir."
    },
    {
        "question": "Kanunun açıklamadığı bir konu çıkarsa ne uygulanır?",
        "options": ["Ceza Kanunu", "Medeni Kanun", "Hukuk Usulü Muhakemeleri Kanunu", "Hakimin kendi yargısı"],
        "correct_option_id": 2,
        "explanation": "📖 İYUK'ta hüküm yoksa HMK uygulanır."
    },
    {
        "question": "Emekli edilen memurun davası nerede açılmalıdır?",
        "options": ["Ankara", "Son çalıştığı yer mahkemesi", "En yakın büyükşehir", "Evinin olduğu yer"],
        "correct_option_id": 1,
        "explanation": "📖 Son görev yeri yetkilidir."
    },
    {
        "question": "Mahkemeler her yıl hangi dönemde kapalı olur?",
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

async def send_question(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_data: dict):
    """Soruyu Telegram'a gönderir (spam filtresi için retry mekanizması)"""
    try:
        quiz = user_data.get("quiz")
        if not quiz or not quiz.get("active"):
            return
        
        current_q = quiz["questions"][quiz["current"]]
        
        await context.bot.send_poll(
            chat_id=chat_id,
            question=f"❓ Soru {quiz['current'] + 1}/25\n\n{current_q['question']}",
            options=current_q["options"],
            type="quiz",
            correct_option_id=current_q["correct_option_id"],
            explanation=current_q["explanation"],
            is_anonymous=False,
            open_period=30,  # 30 saniye cevap süresi
            allows_multiple_answers=False
        )
    except Exception as e:
        logging.error(f"Soru gönderimi başarısız: {e}")
        await asyncio.sleep(2)
        # Retry - tekrar gönder
        try:
            await send_question(context, chat_id, user_data)
        except Exception as retry_e:
            logging.error(f"Soru gönderimi retry başarısız: {retry_e}")

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quizi başlatır"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Eski veriyi temizle
    context.user_data.clear()
    
    # Başlangıç mesajı
    msg = await update.message.reply_text(
        f"🚀 *Hoşgeldin {user.first_name}!*\n"
        f"İYUK Quiz'i başlamak üzeresiniz!\n"
        f"⏳ 10 saniye içinde quiz başlayacak...",
        parse_mode="Markdown"
    )
    
    await asyncio.sleep(10)
    
    # Başlangıç mesajını sil
    try:
        await msg.delete()
    except Exception as e:
        logging.warning(f"Mesaj silinemiyor: {e}")
    
    # Soruları karıştır
    shuffled_questions = IYUK_SORU_SETI.copy()
    random.shuffle(shuffled_questions)
    
    # Quiz verilerini oluştur
    context.user_data["quiz"] = {
        "active": True,
        "questions": shuffled_questions,
        "current": 0,
        "score": 0,
        "chat_id": chat_id,
        "start_time": time.time(),
        "user_id": user.id,
        "user_name": user.full_name if user.full_name else user.username,
        "answered": False  # Spam filtresi için
    }
    
    # İlk soruyu gönder
    await send_question(context, chat_id, context.user_data)

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Poll cevaplarını işler"""
    quiz = context.user_data.get("quiz")
    
    # Quiz aktif mi kontrol et
    if not quiz or not quiz.get("active"):
        return
    
    # Çoklu cevap vermeyi önle (spam filtresi)
    if quiz.get("answered"):
        return
    
    quiz["answered"] = True
    
    try:
        # Seçilen cevap ve doğru cevap
        selected_answer = update.poll_answer.option_ids[0]
        correct_answer = quiz["questions"][quiz["current"]]["correct_option_id"]
        
        # Doğru cevap kontrol et
        if selected_answer == correct_answer:
            quiz["score"] += 1
        
        # Sonraki soruya geç
        quiz["current"] += 1
        
        # Spam filtresi için bekleme
        await asyncio.sleep(2.0)
        
        # Quiz bitti mi kontrol et
        if quiz["current"] < len(quiz["questions"]):
            quiz["answered"] = False  # Sonraki soru için reset
            await send_question(context, quiz["chat_id"], context.user_data)
        else:
            # Quiz bitti - Sonuçları göster
            await show_results(context, quiz)
            quiz["active"] = False
            
    except Exception as e:
        logging.error(f"Poll answer handling error: {e}")

async def show_results(context: ContextTypes.DEFAULT_TYPE, quiz: dict):
    """Quiz sonuçlarını gösterir"""
    user_id = quiz["user_id"]
    user_name = quiz["user_name"]
    score = quiz["score"]
    elapsed_time = int(time.time() - quiz["start_time"])
    
    # Leaderboard'a ekle
    leaderboard[user_id] = {
        "name": user_name,
        "score": score,
        "sure": elapsed_time,
        "timestamp": time.time()
    }
    
    # Sıralamayı oluştur (yüksek puan, düşük süre)
    sorted_leaderboard = sorted(
        leaderboard.values(),
        key=lambda x: (-x["score"], x["sure"])
    )
    
    # Sonuç mesajı
    result_msg = (
        f"🎉 *Quiz Tamamlandı!*\n\n"
        f"👤 Oyuncu: {user_name}\n"
        f"✅ Doğru: {score}/25\n"
        f"⏱ Süre: {elapsed_time} saniye\n"
        f"📊 Yüzde: {(score/25)*100:.1f}%\n"
    )
    
    # Emoji ödülü
    if score == 25:
        result_msg += "🏆 *PERFEKTSİN!*"
    elif score >= 20:
        result_msg += "🥇 *Harika!*"
    elif score >= 15:
        result_msg += "🥈 *İyiysin!*"
    elif score >= 10:
        result_msg += "🥉 *Gelişebilirsin!*"
    else:
        result_msg += "📚 *Daha çok çalışmanız gerekiyor!*"
    
    await context.bot.send_message(
        chat_id=quiz["chat_id"],
        text=result_msg,
        parse_mode="Markdown"
    )
    
    # Leaderboard göster
    leaderboard_msg = "🏆 *LİDERLİK TABLOSU*\n\n"
    for i, player in enumerate(sorted_leaderboard[:10], 1):
        medals = ["🥇", "🥈", "🥉"]
        medal = medals[i-1] if i <= 3 else f"{i}."
        leaderboard_msg += (
            f"{medal} {player['name']}\n"
            f"   ✅ {player['score']}/25 | ⏱ {player['sure']}sn\n\n"
        )
    
    await context.bot.send_message(
        chat_id=quiz["chat_id"],
        text=leaderboard_msg,
        parse_mode="Markdown"
    )

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Leaderboard'u gösterir"""
    if not leaderboard:
        await update.message.reply_text("📊 Henüz kimse quiz oynamadı!")
        return
    
    sorted_board = sorted(
        leaderboard.values(),
        key=lambda x: (-x["score"], x["sure"])
    )
    
    msg = "🏆 *GENEL LİDERLİK TABLOSU*\n\n"
    for i, player in enumerate(sorted_board[:10], 1):
        medals = ["🥇", "🥈", "🥉"]
        medal = medals[i-1] if i <= 3 else f"{i}."
        msg += f"{medal} {player['name']} - {player['score']}/25 ({player['sure']}sn)\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    """Bot'u başlatır"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start_game))
    app.add_handler(CommandHandler("quiz", start_game))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("lb", leaderboard_command))
    
    # Poll answer handler
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    
    # Bot'u başlat
    print("✅ Bot başlatılıyor...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
