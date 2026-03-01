import asyncio
import random
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    PollAnswerHandler, ContextTypes
)

# Loglama
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

# LİDERLİK TABLOSU
leaderboard = {}

# ─────────────────────────────────────────────
#  CMK SORU BANKASI (Tam Liste)
# ─────────────────────────────────────────────

CMK_SORULAR = [
    {"question": "CMK'ya göre 'şüpheli' hangi evrede suç şüphesi altındaki kişidir?", "options": ["Kovuşturma evresi", "Soruşturma evresi", "İstinaf evresi", "Temyiz evresi"], "correct_option_id": 1, "explanation": "📖 Madde 2/a: Soruşturma evresidir."},
    {"question": "CMK'ya göre 'sanık' kimdir?", "options": ["Soruşturma evresinde suç şüphesi altındaki kişi", "Kovuşturmanın başlamasından hükmün kesinleşmesine kadar kişi", "Kesinleşmiş mahkûmiyet kararı bulunan kişi", "Gözaltına alınan kişi"], "correct_option_id": 1, "explanation": "📖 Madde 2/b: Kovuşturma evresindeki kişidir."},
    {"question": "CMK'ya göre 'müdafi' kimdir?", "options": ["Katılanı temsil eden avukat", "Malen sorumluyu temsil eden avukat", "Şüpheli veya sanığın savunmasını yapan avukat", "Savcı yardımcısı"], "correct_option_id": 2, "explanation": "📖 Madde 2/c: Savunma yapan avukattır."},
    {"question": "CMK'ya göre 'kovuşturma' evresi ne zaman başlar?", "options": ["Suçun öğrenilmesiyle", "Gözaltı kararıyla", "İddianamenin kabulüyle", "Tutuklama kararıyla"], "correct_option_id": 2, "explanation": "📖 Madde 2/f: İddianamenin kabulüyle başlar."},
    {"question": "Toplu suç için kaç veya daha fazla kişi gerekir?", "options": ["2 kişi", "3 kişi", "4 kişi", "5 kişi"], "correct_option_id": 1, "explanation": "📖 Madde 2/k: 3 veya daha fazla kişi gerekir."},
    {"question": "CMK Madde 4'e göre mahkeme görevli olup olmadığına hangi aşamada karar verebilir?", "options": ["İddianame öncesi", "Duruşma başında", "Kovuşturma evresinin her aşamasında re'sen", "Yalnızca taleple"], "correct_option_id": 2, "explanation": "📖 Madde 4/1: Her aşamada re'sen karar verebilir."},
    {"question": "CMK'ya göre yetkili mahkeme kural olarak hangi yer mahkemesidir?", "options": ["Sanığın yeri", "Suçun işlendiği yer", "Mağdurun yeri", "Savcı görev yeri"], "correct_option_id": 1, "explanation": "📖 Madde 12/1: Suçun işlendiği yer mahkemesidir."},
    {"question": "Teşebbüs suçlarında yetkili mahkeme hangi yer mahkemesidir?", "options": ["İlk icra hareketinin yapıldığı yer", "Son icra hareketinin yapıldığı yer", "Hazırlık hareketlerinin yapıldığı yer", "Sanığın yakalandığı yer"], "correct_option_id": 1, "explanation": "📖 Madde 12/2: Son icra hareketinin yapıldığı yerdir."},
    {"question": "CMK'ya göre 'ifade alma' kimin tarafından gerçekleştirilir?", "options": ["Yalnızca hâkim", "Yalnızca mahkeme", "Kolluk görevlileri veya Cumhuriyet savcısı", "Yalnızca Cumhuriyet savcısı"], "correct_option_id": 2, "explanation": "📖 Madde 2/g: Kolluk veya Savcı tarafından yapılır."},
    {"question": "CMK Madde 7'ye göre görevli olmayan hâkimin işlemleri ne olur?", "options": ["Hepsi geçerli", "Yenilenmesi mümkün olmayanlar dışındakiler hükümsüz", "Hepsi hükümsüz", "İtirazla geçerli olur"], "correct_option_id": 1, "explanation": "📖 Madde 7/1: Yenilenemeyenler hariç hükümsüzdür."},
    {"question": "CMK Madde 5'e göre görevsizlik kararına karşı hangi yola başvurulabilir?", "options": ["Temyiz", "İtiraz", "İstinaf", "Yargılamanın yenilenmesi"], "correct_option_id": 1, "explanation": "📖 Madde 5/2: Adlî yargı içerisindeki görevsizlik kararlarına itiraz edilebilir."},
    {"question": "Suçun işlendiği yer belli değilse önce hangi yer mahkemesi yetkilidir?", "options": ["Mağdurun yeri", "Savcılığın yeri", "Şüpheli/sanığın yakalandığı yer", "İlk işlemin yapıldığı yer"], "correct_option_id": 2, "explanation": "📖 Madde 13/1: Yakalandığı yer mahkemesi yetkilidir."},
    {"question": "Bilişim suçlarında mağdurun yerleşim yeri yetkisi hangi maddedir?", "options": ["Madde 12/3", "Madde 12/5", "Madde 12/6", "Madde 13/2"], "correct_option_id": 2, "explanation": "📖 Madde 12/6: Bilişim suçlarında mağdurun yeri yetkilidir."},
    {"question": "Diplomatik bağışıklığı olan kamu görevlilerinin suçlarında yetkili yer?", "options": ["İstanbul", "İzmir", "Ankara", "Suç yeri"], "correct_option_id": 2, "explanation": "📖 Madde 14/4: Ankara mahkemeleri yetkilidir."},
    {"question": "CMK'ya göre 'sorgu' kimin tarafından yapılır?", "options": ["Kolluk", "Savcı", "Hâkim veya mahkeme", "Müdafi"], "correct_option_id": 2, "explanation": "📖 Madde 2/h: Sorgu hâkim veya mahkemece yapılır."},
    {"question": "Suçluyu kayırma fiili CMK'ya göre ne sayılır?", "options": ["Ayrı suç", "Bağlantılı suç", "Toplu suç", "Suç değildir"], "correct_option_id": 1, "explanation": "📖 Madde 8/2: Bağlantılı suç sayılır."},
    {"question": "Disiplin hapsi hakkında hangisi doğrudur?", "options": ["Tekerrüre esas olur", "Ertelenebilir", "Adlî sicile geçirilmez", "Şartla salıverme uygulanır"], "correct_option_id": 2, "explanation": "📖 Madde 2/l: Adlî sicile geçirilmez."},
    {"question": "CMK'ya göre 'malen sorumlu' kimdir?", "options": ["Zarar gören", "Maddi sorumluluk taşıyan kişi", "Mali destek sağlayan", "Tazminatçı avukat"], "correct_option_id": 1, "explanation": "📖 Madde 2/i: Maddi sorumluluk taşıyan kişidir."},
    {"question": "Duruşmada suçun niteliği değişirse mahkeme ne yapamaz?", "options": ["Dosyayı gönderebilir", "Davayı durdurur", "Dosyayı alt mahkemeye gönderemez", "Ek iddianame ister"], "correct_option_id": 2, "explanation": "📖 Madde 6: Alt mahkemeye gönderemez."},
    {"question": "Zincirleme suçlarda yetkili mahkeme hangisidir?", "options": ["İlk suç yeri", "En ağır suç yeri", "Son suçun işlendiği yer", "Sanığın yeri"], "correct_option_id": 2, "explanation": "📖 Madde 12/2: Son suçun işlendiği yerdir."},
    {"question": "Gözaltı süresi yakalama anından itibaren en fazla kaç saattir?", "options": ["12", "24", "48", "72"], "correct_option_id": 1, "explanation": "📖 Madde 91: 24 saati geçemez."},
    {"question": "Arama kararı normal şartlarda kim tarafından verilir?", "options": ["Vali", "Kolluk Amiri", "Hâkim", "Savcı"], "correct_option_id": 2, "explanation": "📖 Madde 119: Hâkim kararı gerekir."},
    {"question": "İfade almada en çok kaç müdafi hazır bulunabilir?", "options": ["1", "2", "3", "Sınırsız"], "correct_option_id": 2, "explanation": "📖 Madde 150: En çok 3 müdafi hazır bulunabilir."},
    {"question": "Hangi suçta müdafi görevlendirilmesi zorunludur?", "options": ["Tüm suçlar", "Üst sınır 5 yıl", "Alt sınırı 5 yıldan fazla hapis", "Sadece cinayet"], "correct_option_id": 2, "explanation": "📖 Alt sınırı 5 yıldan fazla hapis cezası gerektiren suçlarda."},
    {"question": "Tutuklama kararını kim verir?", "options": ["Savcı", "Kolluk", "Hâkim", "Vali"], "correct_option_id": 2, "explanation": "📖 Sadece hâkim kararıyla tutuklama yapılır."}
]

# ─────────────────────────────────────────────
#  FONKSİYONLAR
# ─────────────────────────────────────────────

def format_sure(saniye):
    saniye = int(saniye)
    return f"{saniye // 60} dk {saniye % 60} sn" if saniye >= 60 else f"{saniye} sn"

def build_leaderboard_text():
    if not leaderboard: return "🏆 *LİDERLİK TABLOSU (CMK)*\n\nHenüz kayıt yok."
    sirali = sorted(leaderboard.values(), key=lambda x: (-x["score"], x["sure"]))
    satirlar = [f"🏆 *LİDERLİK TABLOSU (CMK)*\n"]
    for i, kayit in enumerate(sirali[:10]):
        emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
        satirlar.append(f"{emoji} {kayit['name']} — ✅ {kayit['score']}/25 | ⏱ {format_sure(kayit['sure'])}")
    return "\n".join(satirlar)

async def send_next_question(context, data):
    q = data["questions"][data["current"]]
    await context.bot.send_poll(
        chat_id=data["chat_id"],
        question=f"❓ Soru {data['current'] + 1}/25\n\n{q['question']}",
        options=q["options"],
        type="quiz",
        correct_option_id=q["correct_option_id"],
        explanation=q["explanation"],
        is_anonymous=False,
        open_period=30
    )

# ─────────────────────────────────────────────
#  KOMUTLAR
# ─────────────────────────────────────────────

async def quiz_hazirlik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Bilgilendirme mesajı
    msg = await update.message.reply_text(
        f"⏳ *Hazır mısın {user.full_name}?*\nCMK Sınavı 15 saniye sonra başlıyor...\n\n_Odaklanın komiserim!_ 🫡",
        parse_mode="Markdown"
    )
    
    # 15 Saniye Geri Sayım (Her 5 saniyede bir güncelleme yapabiliriz ama sadelik için bekletiyoruz)
    await asyncio.sleep(15)
    
    # Mesajı güncelle ve testi başlat
    await msg.edit_text("🚀 *Süre Doldu! Sınav Başlıyor!*")
    
    shuffled = CMK_SORULAR.copy()
    random.shuffle(shuffled)
    
    context.user_data["quiz"] = {
        "active": True, "questions": shuffled, "current": 0,
        "score": 0, "chat_id": chat_id,
        "start_time": time.time(), "user_id": user.id, "user_name": user.full_name
    }
    
    await send_next_question(context, context.user_data["quiz"])

async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    data = context.user_data.get("quiz")
    if not data or not data.get("active"): return

    q = data["questions"][data["current"]]
    if answer.option_ids[0] == q["correct_option_id"]: 
        data["score"] += 1

    data["current"] += 1
    await asyncio.sleep(1.2)

    if data["current"] < len(data["questions"]):
        await send_next_question(context, data)
    else:
        sure = int(time.time() - data["start_time"])
        if data["user_id"] not in leaderboard or leaderboard[data["user_id"]]["score"] < data["score"]:
            leaderboard[data["user_id"]] = {"name": data["user_name"], "score": data["score"], "sure": sure}
        
        await context.bot.send_message(data["chat_id"], build_leaderboard_text(), parse_mode="Markdown")
        data["active"] = False

async def iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Quiz durduruldu.")

async def siralama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(build_leaderboard_text(), parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", quiz_hazirlik))
    app.add_handler(CommandHandler("quiz", quiz_hazirlik))
    app.add_handler(CommandHandler("iptal", iptal))
    app.add_handler(CommandHandler("siralama", siralama))
    app.add_handler(PollAnswerHandler(poll_answer))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
