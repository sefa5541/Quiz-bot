import asyncio, random, time, logging, json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, PollAnswerHandler, ContextTypes

# Loglama ayarı (Hataları görmek için)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# BURAYA KENDİ BOT TOKENİNİZİ YAZIN
BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

# ---------------------------------------------------------
# JSON DOSYASINDAN SORULARI YÜKLEME FONKSİYONU
# ---------------------------------------------------------
def sorulari_yukle():
    try:
        # Dosya yolu kontrolü
        file_path = 'sorular.json'
        if not os.path.exists(file_path):
            logging.error("HATA: sorular.json dosyası dizinde bulunamadı!")
            return []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Soru dosyası okunurken teknik hata: {e}")
        return []

# ---------------------------------------------------------
# BOT MANTIĞI VE KOMUTLAR
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚖️ *Emniyet Sınav Hazırlık Botu Aktif!*\n\n"
        "Mühimmat deposu (JSON) bağlandı. Testleri başlatmak için /quiz yazın.",
        parse_mode="Markdown"
    )

async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tum_sorular = sorulari_yukle()
    if not tum_sorular:
        await update.message.reply_text("❌ Soru deposu (sorular.json) boş veya hatalı formatta!")
        return

    # Kategorileri (İYUK, CMK vb.) otomatik olarak ayıklar
    kategoriler = sorted(list(set([s['kategori'] for s in tum_sorular])))

    keyboard = []
    for kat in kategoriler:
        # Her kategoride kaç soru olduğunu hesapla
        sayi = len([s for s in tum_sorular if s['kategori'] == kat])
        keyboard.append([InlineKeyboardButton(f"📂 {kat} ({sayi} Soru)", callback_data=f"quiz_{kat}")])

    await update.message.reply_text("📚 *Çalışmak istediğiniz konuyu seçin:*", 
                                   reply_markup=InlineKeyboardMarkup(keyboard), 
                                   parse_mode="Markdown")

async def quiz_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    kat_adi = query.data.split("_")[1]
    tum_sorular = sorulari_yukle()
    secilen_sorular = [s for s in tum_sorular if s['kategori'] == kat_adi]
    
    # Soruları her seferinde farklı sırayla getir
    random.shuffle(secilen_sorular)

    context.user_data["quiz"] = {
        "active": True,
        "questions": secilen_sorular,
        "current": 0,
        "score": 0,
        "chat_id": query.message.chat_id,
        "start_time": time.time()
    }
    
    await query.edit_message_text(f"🚀 *{kat_adi}* mühimmatı hazırlandı. Operasyon başlıyor!")
    await sonraki_soruyu_gonder(context)

async def sonraki_soruyu_gonder(context):
    data = context.user_data["quiz"]
    soru = data["questions"][data["current"]]
    
    await context.bot.send_poll(
        chat_id=data["chat_id"],
        question=f"❓ Soru {data['current'] + 1}/{len(data['questions'])}\n\n{soru['question']}",
        options=soru["options"],
        type="quiz",
        correct_option_id=soru["correct_option_id"],
        explanation=soru["explanation"],
        is_anonymous=False
    )

async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = update.poll_answer
    data = context.user_data.get("quiz")
    
    if not data or not data.get("active"):
        return

    # Cevap doğru mu kontrol et
    if ans.option_ids[0] == data["questions"][data["current"]]["correct_option_id"]:
        data["score"] += 1

    data["current"] += 1
    await asyncio.sleep(1.5) # Sonucu görmesi için kısa bekleme

    if data["current"] < len(data["questions"]):
        await sonraki_soruyu_gonder(context)
    else:
        gecen_sure = int(time.time() - data["start_time"])
        await context.bot.send_message(
            data["chat_id"], 
            f"🏁 *TEST TAMAMLANDI!*\n\n📊 Başarı: {data['score']}/{len(data['questions'])}\n⏱ Süre: {gecen_sure} saniye",
            parse_mode="Markdown"
        )
        data["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_menu))
    app.add_handler(CallbackQueryHandler(quiz_sec, pattern="^quiz_"))
    app.add_handler(PollAnswerHandler(poll_answer))
    
    print("🚀 Soru Fabrikası Mekanizması Çalışıyor...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
