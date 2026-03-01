import asyncio, random, time, logging, json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, PollAnswerHandler, ContextTypes

# Loglama ayarı
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# BURAYA KENDİ BOT TOKENİNİZİ YAZIN
BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

def sorulari_yukle():
    try:
        if not os.path.exists('sorular.json'):
            return []
        with open('sorular.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Hata: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚖️ *Emniyet Sınav Hazırlık Botu Aktif!*\n/quiz yazarak başlayın.", parse_mode="Markdown")

async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tum_sorular = sorulari_yukle()
    if not tum_sorular:
        await update.message.reply_text("❌ Soru bulunamadı!")
        return
    kategoriler = sorted(list(set([s['kategori'] for s in tum_sorular])))
    keyboard = [[InlineKeyboardButton(f"📂 {kat}", callback_data=f"quiz_{kat}")] for kat in kategoriler]
    await update.message.reply_text("📚 *Konu seçin:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def quiz_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kat_adi = query.data.split("_")[1]
    secilen_sorular = [s for s in sorulari_yukle() if s['kategori'] == kat_adi]
    random.shuffle(secilen_sorular)

    context.user_data["quiz"] = {
        "active": True, "questions": secilen_sorular, "current": 0,
        "score": 0, "wrong": 0, "chat_id": query.message.chat_id, 
        "start_time": time.time(), "user_name": query.from_user.first_name
    }
    await query.edit_message_text(f"🚀 *{kat_adi}* testi başlıyor! Her soru için süreniz 30 saniye.")
    await sonraki_soruyu_gonder(context)

async def sonraki_soruyu_gonder(context):
    data = context.user_data["quiz"]
    soru = data["questions"][data["current"]]
    
    await context.bot.send_poll(
        chat_id=data["chat_id"],
        question=f"❓ {soru['question']}",
        options=soru["options"],
        type="quiz",
        correct_option_id=soru["correct_option_id"],
        explanation=soru["explanation"],
        open_period=30, # HER SORU İÇİN 30 SANİYE SÜRE
        is_anonymous=False
    )

async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = update.poll_answer
    data = context.user_data.get("quiz")
    if not data or not data["active"]: return

    if ans.option_ids[0] == data["questions"][data["current"]]["correct_option_id"]:
        data["score"] += 1
    else:
        data["wrong"] += 1

    data["current"] += 1
    await asyncio.sleep(1.5)

    if data["current"] < len(data["questions"]):
        await sonraki_soruyu_gonder(context)
    else:
        # TEST BİTİŞ VE LİDERLİK TABLOSU FORMATI
        bitis_zamani = time.time()
        sure_saniye = int(bitis_zamani - data["start_time"])
        dakika = sure_saniye // 60
        saniye = sure_saniye % 60
        basari_yuzde = int((data["score"] / len(data["questions"])) * 100)

        mesaj = (
            f"👤 *{data['user_name']}*\n\n"
            f"✅ Doğru: {data['score']}\n"
            f"❌ Yanlış: {data['wrong']}\n"
            f"📊 Başarı: %{basari_yuzde}\n"
            f"⏱ Süre: {dakika} dakika {saniye} saniye\n\n"
            f"🏆 *LİDERLİK TABLOSU*\n"
            f"🥇 {data['user_name']} — ✅ {data['score']} doğru | ❌ {data['wrong']} yanlış | ⏱ {dakika} dk {saniye} sn"
        )
        
        await context.bot.send_message(data["chat_id"], mesaj, parse_mode="Markdown")
        data["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_menu))
    app.add_handler(CallbackQueryHandler(quiz_sec, pattern="^quiz_"))
    app.add_handler(PollAnswerHandler(poll_answer))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
