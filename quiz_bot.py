import asyncio
import random
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    PollAnswerHandler, ContextTypes
)

# Hata ayıklama için loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

# LİDERLİK TABLOLARI
leaderboard = {
    "cmk": {},
    "vatandaslik": {},
    "iyuk": {} # İYUK eklendi
}

# SORU BANKALARI (Senin kodundaki içerik aynen korundu)
CMK_SORULAR = [
    {"question": "CMK'ya göre 'şüpheli' hangi evrede suç şüphesi altındaki kişidir?", "options": ["Kovuşturma evresi", "Soruşturma evresi", "İstinaf evresi", "Temyiz evresi"], "correct_option_id": 1, "explanation": "📖 Madde 2/a: Soruşturma evresidir."},
    {"question": "CMK'ya göre 'sanık' kimdir?", "options": ["Soruşturma evresinde suç şüphesi altındaki kişi", "Kovuşturmanın başlamasından hükmün kesinleşmesine kadar kişi", "Kesinleşmiş mahkûmiyet kararı bulunan kişi", "Gözaltına alınan kişi"], "correct_option_id": 1, "explanation": "📖 Madde 2/b: Kovuşturma evresindeki kişidir."},
    {"question": "CMK'ya göre 'müdafi' kimdir?", "options": ["Katılanı temsil eden avukat", "Malen sorumluyu temsil eden avukat", "Şüpheli veya sanığın savunmasını yapan avukat", "Savcı yardımcısı"], "correct_option_id": 2, "explanation": "📖 Madde 2/c: Savunma yapan avukattır."},
    {"question": "CMK'ya göre 'kovuşturma' evresi ne zaman başlar?", "options": ["Suçun öğrenilmesiyle", "Gözaltı kararıyla", "İddianamenin kabulüyle", "Tutuklama kararıyla"], "correct_option_id": 2, "explanation": "📖 Madde 2/f: İddianamenin kabulüyle başlar."},
    {"question": "Toplu suç için kaç veya daha fazla kişi gerekir?", "options": ["2 kişi", "3 kişi", "4 kişi", "5 kişi"], "correct_option_id": 1, "explanation": "📖 Madde 2/k: 3 veya daha fazla kişi gerekir."},
    {"question": "CMK Madde 4'e göre mahkeme görevli olup olmadığına hangi aşamada karar verebilir?", "options": ["İddianame öncesi", "Duruşma başında", "Kovuşturma evresinin her aşamasında re'sen", "Yalnızca taleple"], "correct_option_id": 2, "explanation": "📖 Madde 4/1: Her aşamada re'sen karar verebilir."},
    {"question": "CMK'ya göre yetkili mahkeme kural olarak hangi yer mahkemesidir?", "options": ["Sanığın yeri", "Suçun işlendiği yer", "Mağdurun yeri", "Savcı görev yeri"], "correct_option_id": 1, "explanation": "📖 Madde 12/1: Suçun işlendiği yer mahkemesidir."},
    {"question": "Teşebbüs suçlarında yetkili mahkeme hangi yer mahkemesidir?", "options": ["İlk icra hareketinin yapıldığı yer", "Son icra hareketinin yapıldığı yer", "Hazırlık hareketlerinin yapıldığı yer", "Sanığın yakalandığı yer"], "correct_option_id": 1, "explanation": "📖 Madde 12/2: Son icra hareketinin yapıldığı yerdir."},
    {"question": "CMK'ya göre 'ifade alma' kimin tarafından gerçekleştirilir?", "options": ["Yalnızca hâkim", "Yalnızca mahkeme", "Kolluk veya Cumhuriyet savcısı", "Yalnızca savcı"], "correct_option_id": 2, "explanation": "📖 Madde 2/g: Kolluk veya savcı tarafından yapılır."},
    {"question": "CMK Madde 7'ye göre görevli olmayan hâkimin işlemleri ne olur?", "options": ["Hepsi geçerli", "Yenilenmesi mümkün olmayanlar dışındakiler hükümsüz", "Hepsi hükümsüz", "İtirazla geçerli olur"], "correct_option_id": 1, "explanation": "📖 Madde 7/1: Yenilenemeyenler hariç hükümsüzdür."},
    {"question": "CMK Madde 5'e göre görevsizlik kararına karşı hangi yola başvurulabilir?", "options": ["Temyiz", "İtiraz", "İstinaf", "Yargılamanın yenilenmesi"], "correct_option_id": 1, "explanation": "📖 Madde 5/2: İtiraz yoluna gidilebilir."},
    {"question": "CMK'ya göre suçun işlendiği yer belli değilse önce hangi yer mahkemesi yetkilidir?", "options": ["Mağdurun yeri", "Savcılık yeri", "Şüpheli veya sanığın yakalandığı yer", "İlk usul işlemi yeri"], "correct_option_id": 2, "explanation": "📖 Madde 13/1: Yakalandığı yer mahkemesi yetkilidir."}
]

VATANDASLIK_SORULAR = [
    {"question": "Milletvekili seçilebilmek için kaç yaşını doldurmuş olmak gerekir?", "options": ["21", "25", "18", "30"], "correct_option_id": 2, "explanation": "📖 Seçilme yaşı 18'dir."},
    {"question": "Cumhurbaşkanı adayı olabilmek için kaç yaşını doldurmuş olmak gerekir?", "options": ["30", "35", "40", "45"], "correct_option_id": 2, "explanation": "📖 Adaylık yaşı 40'tır."},
    {"question": "Türk hukukuna göre olağan evlenme yaşı kaçtır?", "options": ["16", "17", "18", "15"], "correct_option_id": 1, "explanation": "📖 Olağan evlenme yaşı 17'dir."},
    {"question": "Kaza-i rüşt kararı kaç yaşından itibaren alınabilir?", "options": ["12", "14", "15", "16"], "correct_option_id": 2, "explanation": "📖 Kaza-i rüşt yaşı 15'tir."},
    {"question": "Devlet memurlarına tanınan babalık izni kaç gündür?", "options": ["5 gün", "7 gün", "10 gün", "14 gün"], "correct_option_id": 2, "explanation": "📖 Babalık izni 10 gündür."},
    {"question": "TBMM toplam kaç milletvekilinden oluşur?", "options": ["450", "500", "550", "600"], "correct_option_id": 3, "explanation": "📖 TBMM 600 milletvekilinden oluşur."},
    {"question": "Türkiye'de seçim barajı yüzde kaçtır?", "options": ["%5", "%7", "%10", "%3"], "correct_option_id": 1, "explanation": "📖 Seçim barajı %7'dir."},
    {"question": "Anayasa Mahkemesi kaç üyeden oluşur?", "options": ["11", "13", "15", "17"], "correct_option_id": 2, "explanation": "📖 AYM 15 üyeden oluşur."}
]

IYUK_SORULAR = [
    {"question": "İdari yargıda genel dava açma süresi kaç gündür?", "options": ["15", "30", "60", "90"], "correct_option_id": 2, "explanation": "📖 Genel dava açma süresi 60 gündür."},
    {"question": "Vergi mahkemelerinde dava açma süresi kaç gündür?", "options": ["15", "30", "45", "60"], "correct_option_id": 1, "explanation": "📖 Vergi mahkemelerinde süre 30 gündür."}
]

KATEGORILER = {
    "cmk": {"ad": "⚖️ CMK", "sorular": CMK_SORULAR},
    "vatandaslik": {"ad": "🇹🇷 Vatandaşlık", "sorular": VATANDASLIK_SORULAR},
    "iyuk": {"ad": "📂 İYUK", "sorular": IYUK_SORULAR}
}

# YARDIMCI FONKSİYONLAR
def format_sure(saniye):
    saniye = int(saniye)
    if saniye < 60: return f"{saniye} saniye"
    return f"{saniye // 60} dakika {saniye % 60} saniye"

def build_leaderboard_text(kategori_key):
    kategori_ad = KATEGORILER[kategori_key]["ad"]
    tablo = leaderboard[kategori_key]
    if not tablo: return f"🏆 *{kategori_ad}*\n\nHenüz kayıt yok."
    
    sirali = sorted(tablo.values(), key=lambda x: (-x["score"], x["sure"]))
    satirlar = [f"🏆 *LİDERLİK TABLOSU*\n_{kategori_ad}_\n"]
    for i, kayit in enumerate(sirali[:10]):
        emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
        satirlar.append(f"{emoji} {kayit['name']} — ✅ {kayit['score']} | ❌ {kayit['wrong']} | ⏱ {format_sure(kayit['sure'])}")
    return "\n".join(satirlar)

async def send_next_question(context, data):
    q = data["questions"][data["current"]]
    msg = await context.bot.send_poll(
        chat_id=data["chat_id"],
        question=f"❓ Soru {data['current'] + 1}/{len(data['questions'])}\n\n{q['question']}",
        options=q["options"],
        type="quiz",
        correct_option_id=q["correct_option_id"],
        explanation=q["explanation"],
        is_anonymous=False,
        open_period=30 # 30 SANİYE KURALI
    )
    data["poll_map"][msg.poll.id] = data["current"]

# KOMUTLAR
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 *Sınav Botu Hazır!*\n\n/quiz yazarak başlayın.", parse_mode="Markdown")

async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v["ad"], callback_data=f"quiz_{k}")] for k, v in KATEGORILER.items()]
    await update.message.reply_text("📚 *Konu seçin:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def quiz_kategori_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    k_key = query.data.replace("quiz_", "")
    user = update.effective_user
    shuffled = KATEGORILER[k_key]["sorular"].copy()
    random.shuffle(shuffled)

    context.user_data["quiz"] = {
        "active": True, "kategori": k_key, "questions": shuffled, "current": 0,
        "score": 0, "wrong": 0, "poll_map": {}, "chat_id": update.effective_chat.id,
        "start_time": time.time(), "user_id": user.id, "user_name": user.full_name
    }
    
    await query.edit_message_text(f"🚀 *{KATEGORILER[k_key]['ad']}* başladı!\n⏱ Her soru 30 saniye.", parse_mode="Markdown")
    await send_next_question(context, context.user_data["quiz"])

async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    data = context.user_data.get("quiz")
    if not data or not data["active"] or answer.poll_id not in data["poll_map"]: return

    q = data["questions"][data["current"]]
    if answer.option_ids[0] == q["correct_option_id"]: data["score"] += 1
    else: data["wrong"] += 1

    data["current"] += 1
    await asyncio.sleep(1.5)

    if data["current"] < len(data["questions"]):
        await send_next_question(context, data)
    else:
        # FİNAL VE SIRALAMA
        sure = int(time.time() - data["start_time"])
        leaderboard[data["kategori"]][data["user_id"]] = {
            "name": data["user_name"], "score": data["score"], "wrong": data["wrong"], "sure": sure
        }
        
        sonuc = (f"👤 *{data['user_name']}*\n\n✅ Doğru: {data['score']}\n❌ Yanlış: {data['wrong']}\n"
                 f"📊 Başarı: %{int((data['score']/len(data['questions']))*100)}\n⏱ Süre: {format_sure(sure)}\n\n"
                 f"{build_leaderboard_text(data['kategori'])}")
        
        await context.bot.send_message(data["chat_id"], sonuc, parse_mode="Markdown")
        data["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_menu))
    app.add_handler(CallbackQueryHandler(quiz_kategori_sec, pattern="^quiz_"))
    app.add_handler(PollAnswerHandler(poll_answer))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
