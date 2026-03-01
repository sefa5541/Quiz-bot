import asyncio, random, time, logging, json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, PollAnswerHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# BOT TOKENİNİZ
BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

def sorulari_yukle():
    try:
        if not os.path.exists('sorular.json'): return []
        with open('sorular.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Dosya hatası: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚖️ *Sınav Botu Hazır!*\n/quiz yazarak başlayın.", parse_mode="Markdown")

async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tum = sorulari_yukle()
    if not tum:
        await update.message.reply_text("❌ Soru dosyası (sorular.json) hatalı veya boş!")
        return
    kategoriler = sorted(list(set([s['kategori'] for s in tum])))
    kb = [[InlineKeyboardButton(f"📂 {k}", callback_data=f"q_{k}")] for k in kategoriler]
    await update.message.reply_text("📚 *Konu seçiniz:*", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def quiz_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kat = query.data.split("_")[1]
    sorular = [s for s in sorulari_yukle() if s['kategori'] == kat]
    random.shuffle(sorular)

    context.user_data["quiz"] = {
        "active": True, "qs": sorular, "curr": 0, "score": 0, "wrong": 0,
        "cid": query.message.chat_id, "start": time.time(), "name": query.from_user.first_name
    }
    await query.edit_message_text(f"🚀 *{kat}* başladı! Soru başına *30 saniye* süreniz var.")
    await soru_gonder(context)

async def soru_gonder(context):
    data = context.user_data["quiz"]
    s = data["qs"][data["curr"]]
    
    # SÜRELİ ANKET GÖNDERİMİ
    await context.bot.send_poll(
        chat_id=data["cid"],
        question=f"❓ Soru {data['curr']+1}/{len(data['qs'])}\n\n{s['question']}",
        options=s["options"],
        type="quiz",
        correct_option_id=s["correct_option_id"],
        explanation=s["explanation"],
        open_period=30, # BU SATIR 30 SANİYEYİ AKTİF EDER
        is_anonymous=False
    )

async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("quiz")
    if not data or not data["active"]: return

    ans = update.poll_answer
    if ans.option_ids[0] == data["qs"][data["curr"]]["correct_option_id"]:
        data["score"] += 1
    else:
        data["wrong"] += 1

    data["curr"] += 1
    await asyncio.sleep(1.5)

    if data["curr"] < len(data["qs"]):
        await soru_gonder(context)
    else:
        # SENİN İSTEDİĞİN LİDERLİK FORMATI
        sure = int(time.time() - data["start"])
        dk, sn = sure // 60, sure % 60
        msg = (
            f"👤 *{data['name']}*\n\n"
            f"✅ Doğru: {data['score']}\n"
            f"❌ Yanlış: {data['wrong']}\n"
            f"📊 Başarı: %{int((data['score']/len(data['qs']))*100)}\n"
            f"⏱ Süre: {dk} dk {sn} sn\n\n"
            f"🏆 *LİDERLİK TABLOSU*\n"
            f"🥇 {data['name']} — ✅ {data['score']} D | ❌ {data['wrong']} Y | ⏱ {dk} dk {sn} sn"
        )
        await context.bot.send_message(data["cid"], msg, parse_mode="Markdown")
        data["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("quiz", quiz_menu))
    app.add_handler(CallbackQueryHandler(quiz_sec, pattern="^q_"))
    app.add_handler(PollAnswerHandler(poll_answer))
    app.run_polling()

if __name__ == "__main__": main()
    
