import asyncio
import random
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    PollAnswerHandler, ContextTypes
)

# Hata takibi için loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

# ─────────────────────────────────────────────
#  LİDERLİK TABLOLARI
# ─────────────────────────────────────────────
leaderboard = {"cmk": {}, "vatandaslik": {}}

# ─────────────────────────────────────────────
#  SORU BANKALARI (Eksiksiz Tam Liste)
# ─────────────────────────────────────────────
CMK_SORULAR = [
    {"question": "CMK'ya göre 'şüpheli' hangi evrede suç şüphesi altındaki kişidir?", "options": ["Kovuşturma evresi", "Soruşturma evresi", "İstinaf evresi", "Temyiz evresi"], "correct_option_id": 1, "explanation": "📖 Madde 2/a: Şüpheli, soruşturma evresinde suç şüphesi altında bulunan kişidir."},
    {"question": "CMK'ya göre 'sanık' kimdir?", "options": ["Soruşturma evresinde suç şüphesi altındaki kişi", "Kovuşturmanın başlamasından hükmün kesinleşmesine kadar suç şüphesi altındaki kişi", "Kesinleşmiş mahkûmiyet kararı bulunan kişi", "Gözaltına alınan kişi"], "correct_option_id": 1, "explanation": "📖 Madde 2/b: Sanık, kovuşturmanın başlamasından hükmün kesinleşmesine kadar suç şüphesi altındaki kişidir."},
    {"question": "CMK'ya göre 'müdafi' kimdir?", "options": ["Katılanı temsil eden avukat", "Malen sorumluyu temsil eden avukat", "Şüpheli veya sanığın savunmasını yapan avukat", "Cumhuriyet savcısının yardımcısı"], "correct_option_id": 2, "explanation": "📖 Madde 2/c: Müdafi, şüpheli veya sanığın ceza muhakemesinde savunmasını yapan avukattır."},
    {"question": "CMK'ya göre 'vekil' kimdir?", "options": ["Şüpheliyi temsil eden avukat", "Sanığı temsil eden avukat", "Katılan, suçtan zarar gören veya malen sorumluyu temsil eden avukat", "Tanığı temsil eden avukat"], "correct_option_id": 2, "explanation": "📖 Madde 2/d: Vekil; katılan, suçtan zarar gören veya malen sorumluyu ceza muhakemesinde temsil eden avukattır."},
    {"question": "CMK'ya göre 'soruşturma' evresi ne zaman sona erer?", "options": ["Suç duyurusuyla", "Gözaltı bitimiyle", "İddianamenin kabulüyle", "Hükmün açıklanmasıyla"], "correct_option_id": 2, "explanation": "📖 Madde 2/e: Soruşturma, kanuna göre yetkili mercilerce suç şüphesinin öğrenilmesinden iddianamenin kabulüne kadar geçen evredir."},
    {"question": "CMK'ya göre 'kovuşturma' evresi ne zaman başlar?", "options": ["Suç şüphesinin öğrenilmesiyle", "Gözaltı kararıyla", "İddianamenin kabulüyle", "Tutuklama kararıyla"], "correct_option_id": 2, "explanation": "📖 Madde 2/f: Kovuşturma, iddianamenin kabulüyle başlayıp hükmün kesinleşmesine kadar geçen evredir."},
    {"question": "CMK'ya göre 'ifade alma' kimin tarafından gerçekleştirilir?", "options": ["Yalnızca hâkim", "Yalnızca mahkeme", "Kolluk görevlileri veya Cumhuriyet savcısı", "Yalnızca Cumhuriyet savcısı"], "correct_option_id": 2, "explanation": "📖 Madde 2/g: İfade alma, şüphelinin kolluk görevlileri veya Cumhuriyet savcısı tarafından dinlenmesidir."},
    {"question": "CMK'ya göre 'sorgu' kimin tarafından yapılır?", "options": ["Kolluk görevlileri", "Cumhuriyet savcısı", "Hâkim veya mahkeme", "Müdafi"], "correct_option_id": 2, "explanation": "📖 Madde 2/h: Sorgu, şüpheli veya sanığın hâkim veya mahkeme tarafından dinlenmesidir."},
    {"question": "CMK'ya göre 'malen sorumlu' kişi kim olarak tanımlanır?", "options": ["Suçtan maddi zarar gören kişi", "Hükmün sonuçlarından maddi sorumluluk taşıyarak etkilenecek kişi", "Suçun işlenmesine mali destek sağlayan kişi", "Tazminat ödemekle yükümlü avukat"], "correct_option_id": 1, "explanation": "📖 Madde 2/i: Malen sorumlu, hükmün kesinleşmesinden sonra maddi sorumluluk taşıyarak hükmün sonuçlarından etkilenecek kişidir."},
    {"question": "Toplu suç için kaç veya daha fazla kişi gerekir?", "options": ["2 kişi", "3 kişi", "4 kişi", "5 kişi"], "correct_option_id": 1, "explanation": "📖 Madde 2/k: Toplu suç, aralarında iştirak iradesi bulunmasa da 3 veya daha fazla kişi tarafından işlenen suçtur."},
    {"question": "Disiplin hapsi hakkında aşağıdakilerden hangisi doğrudur?", "options": ["Tekerrüre esas olur", "Ertelenebilir", "Adlî sicil kayıtlarına geçirilmez", "Şartla salıverilme hükümleri uygulanır"], "correct_option_id": 2, "explanation": "📖 Madde 2/l: Disiplin hapsi adlî sicil kayıtlarına geçirilmeyen, tekerrüre esas olmayan, ertelenemeyen bir yaptırımdır."},
    {"question": "CMK Madde 4'e göre mahkeme görevli olup olmadığına hangi aşamada karar verebilir?", "options": ["Yalnızca iddianamenin kabulünden önce", "Yalnızca duruşmanın başında", "Kovuşturma evresinin her aşamasında re'sen", "Yalnızca tarafların talebiyle"], "correct_option_id": 2, "explanation": "📖 Madde 4/1: Davaya bakan mahkeme, görevli olup olmadığına kovuşturma evresinin her aşamasında re'sen karar verebilir."},
    {"question": "CMK Madde 5'e göre görevsizlik kararına karşı hangi yola başvurulabilir?", "options": ["Temyiz", "İtiraz", "İstinaf", "Yargılamanın yenilenmesi"], "correct_option_id": 1, "explanation": "📖 Madde 5/2: Adlî yargı içerisindeki mahkemeler bakımından verilen görevsizlik kararlarına karşı itiraz yoluna gidilebilir."},
    {"question": "Duruşmada suçun hukuki niteliği değişirse mahkeme ne yapabilir?", "options": ["Görevsizlik kararıyla dosyayı alt mahkemeye gönderebilir", "Davayı durdurabilir", "Görevsizlik kararı vererek dosyayı alt mahkemeye gönderemez", "Cumhuriyet savcısından ek iddianame isteyebilir"], "correct_option_id": 2, "explanation": "📖 Madde 6: Duruşmada suçun hukuki niteliğinin değiştiğinden bahisle görevsizlik kararı verilerek dosya alt dereceli mahkemeye gönderilemez."},
    {"question": "CMK Madde 7'ye göre görevli olmayan hâkimin işlemleri ne olur?", "options": ["Hepsi geçerlidir", "Yenilenmesi mümkün olmayanlar dışında hükümsüzdür", "Hepsi hükümsüzdür", "İtirazla geçerli hale gelir"], "correct_option_id": 1, "explanation": "📖 Madde 7/1: Yenilenmesi mümkün olmayanlar dışında, görevli olmayan hâkim veya mahkemece yapılan işlemler hükümsüzdür."},
    {"question": "Suçun işlenmesinden sonra suçluyu kayırma fiili CMK'ya göre ne sayılır?", "options": ["Ayrı bir suç", "Bağlantılı suç", "Toplu suç", "Suç değildir"], "correct_option_id": 1, "explanation": "📖 Madde 8/2: Suçun işlenmesinden sonra suçluyu kayırma, suç delillerini yok etme, gizleme veya değiştirme fiilleri bağlantılı suç sayılır."},
    {"question": "CMK'ya göre yetkili mahkeme kural olarak hangi yer mahkemesidir?", "options": ["Sanığın yerleşim yeri", "Suçun işlediği yer", "Mağdurun yerleşim yeri", "Cumhuriyet savcısının görev yeri"], "correct_option_id": 1, "explanation": "📖 Madde 12/1: Davaya bakmak yetkisi, suçun işlendiği yer mahkemesine aittir."},
    {"question": "Teşebbüs suçlarında yetkili mahkeme hangi yer mahkemesidir?", "options": ["İlk icra hareketinin yapıldığı yer", "Son icra hareketinin yapıldığı yer", "Hazırlık hareketlerinin yapıldığı yer", "Sanığın yakalandığı yer"], "correct_option_id": 1, "explanation": "📖 Madde 12/2: Teşebbüste son icra hareketinin yapıldığı yer mahkemesi yetkilidir."},
    {"question": "Zincirleme suçlarda yetkili mahkeme hangisidir?", "options": ["İlk suçun işlendiği yer", "En ağır suçun işlendiği yer", "Son suçun işlendiği yer", "Sanığın yerleşim yeri"], "correct_option_id": 2, "explanation": "📖 Madde 12/2: Zincirleme suçlarda son suçun işlendiği yer mahkemesi yetkilidir."},
    {"question": "CMK'ya göre suçun işlendiği yer belli değilse önce hangi yer mahkemesi yetkilidir?", "options": ["Mağdurun yerleşim yeri", "Savcılığın bulunduğu yer", "Şüpheli veya sanığın yakalandığı yer", "İlk usul işleminin yapıldığı yer"], "correct_option_id": 2, "explanation": "📖 Madde 13/1: Suçun işlendiği yer belli değilse şüpheli veya sanığın yakalandığı yer mahkemesi yetkilidir."},
]

VATANDASLIK_SORULAR = [
    {"question": "Türkiye'de milletvekili seçilebilmek için kaç yaşını doldurmuş olmak gerekir?", "options": ["21", "25", "18", "30"], "correct_option_id": 2, "explanation": "📖 Milletvekili seçilebilme yaşı 18'dir."},
    {"question": "Cumhurbaşkanı adayı olabilmek için kaç yaşını doldurmuş olmak gerekir?", "options": ["30", "35", "40", "45"], "correct_option_id": 2, "explanation": "📖 Cumhurbaşkanı adayı olabilmek için 40 yaşını doldurmuş olmak gerekir."},
    {"question": "Türk hukukuna göre olağan evlenme yaşı kaçtır?", "options": ["16", "17", "18", "15"], "correct_option_id": 1, "explanation": "📖 Olağan evlenme yaşı 17'dir."},
    {"question": "Kaza-i rüşt kararı kaç yaşından itibaren alınabilir?", "options": ["12", "14", "15", "16"], "correct_option_id": 2, "explanation": "📖 Kaza-i rüşt 15 yaşından itibaren alınabilir."},
    {"question": "Vasiyetname düzenleyebilmek için kaç yaşını doldurmuş olmak gerekir?", "options": ["12", "15", "18", "21"], "correct_option_id": 1, "explanation": "📖 Vasiyetname yazabilmek için 15 yaşını doldurmuş olmak gerekir."},
    {"question": "Tam ceza ehliyeti kaç yaşında başlar?", "options": ["12", "15", "16", "18"], "correct_option_id": 3, "explanation": "📖 Tam ceza ehliyeti 18 yaşında başlar."},
    {"question": "Devlet memurlarına tanınan babalık izni kaç gündür?", "options": ["5 gün", "7 gün", "10 gün", "14 gün"], "correct_option_id": 2, "explanation": "📖 Babalık izni 10 gündür."},
    {"question": "Devlet memurlarına tanınan evlilik izni kaç gündür?", "options": ["3 gün", "5 gün", "7 gün", "10 gün"], "correct_option_id": 2, "explanation": "📖 Evlilik izni 7 gündür."},
    {"question": "Analık izni toplam kaç haftadır?", "options": ["8 hafta", "12 hafta", "16 hafta", "24 hafta"], "correct_option_id": 2, "explanation": "📖 Toplam 16 haftadır."},
    {"question": "Türkiye'de seçim barajı yüzde kaçtır?", "options": ["%5", "%7", "%10", "%3"], "correct_option_id": 1, "explanation": "📖 Türkiye'de seçim barajı %7'dir."},
]

KATEGORILER = {
    "cmk": {"ad": "⚖️ CMK - Ceza Muhakemesi Kanunu", "sorular": CMK_SORULAR},
    "vatandaslik": {"ad": "🇹🇷 Vatandaşlık Genel Bilgiler", "sorular": VATANDASLIK_SORULAR}
}

# ─────────────────────────────────────────────
#  TEKNİK FONKSİYONLAR
# ─────────────────────────────────────────────

def get_quiz_data(context):
    if "quiz" not in context.user_data:
        context.user_data["quiz"] = {"active": False, "poll_map": {}}
    return context.user_data["quiz"]

async def send_next_question(chat_id, context, data):
    idx = data["current"]
    q = data["questions"][idx]
    msg = await context.bot.send_poll(
        chat_id=chat_id,
        question=f"❓ Soru {idx + 1}/{len(data['questions'])}\n\n{q['question']}",
        options=q["options"],
        type="quiz",
        correct_option_id=q["correct_option_id"],
        explanation=q["explanation"],
        is_anonymous=False,
        open_period=45
    )
    data["poll_map"][msg.poll.id] = idx

# ─────────────────────────────────────────────
#  YAKALAYICILAR (Handlers)
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 *Quiz Bot Hazır!*\n\n/quiz yazarak başla.", parse_mode="Markdown")

async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(cat["ad"], callback_data=f"quiz_{k}")] for k, cat in KATEGORILER.items()]
    await update.message.reply_text("📚 *Konu Seç:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def quiz_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    k_key = query.data.split("_")[1]
    data = get_quiz_data(context)
    shuffled = KATEGORILER[k_key]["sorular"].copy()
    random.shuffle(shuffled)
    data.update({
        "active": True, "kategori": k_key, "questions": shuffled,
        "current": 0, "score": 0, "wrong": 0, "chat_id": query.message.chat_id,
        "start_time": time.time(), "user_name": update.effective_user.full_name
    })
    await query.edit_message_text(f"🚀 *{KATEGORILER[k_key]['ad']}* Başlıyor!")
    await send_next_question(query.message.chat_id, context, data)

async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = update.poll_answer
    data = context.user_data.get("quiz")
    if not data or not data.get("active") or ans.poll_id not in data.get("poll_map", {}): return
    q = data["questions"][data["current"]]
    if ans.option_ids[0] == q["correct_option_id"]: data["score"] += 1
    else: data["wrong"] += 1
    data["current"] += 1
    await asyncio.sleep(1)
    if data["current"] < len(data["questions"]):
        await send_next_question(data["chat_id"], context, data)
    else:
        sure = int(time.time() - data["start_time"])
        await context.bot.send_message(data["chat_id"], f"🏁 *Bitti!* \n✅ Doğru: {data['score']}\n❌ Yanlış: {data['wrong']}\n⏱ Süre: {sure} sn", parse_mode="Markdown")
        data["active"] = False

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ İptal edildi.")

# ─────────────────────────────────────────────
#  ANA MOTOR
# ─────────────────────────────────────────────

def main():
    # Railway'deki python-telegram-bot v20+ hatasını önlemek için sade yapı
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz_menu))
    application.add_handler(CommandHandler("iptal", cancel))
    application.add_handler(CallbackQueryHandler(quiz_sec, pattern="^quiz_"))
    application.add_handler(PollAnswerHandler(poll_answer))
    
    print("✅ Bot Aktif!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
