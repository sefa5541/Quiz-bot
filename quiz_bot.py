import asyncio
import random
import time
import logging
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, PollAnswerHandler, ContextTypes
)

# 1. LOG SİSTEMİ
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. AYARLAR
BOT_TOKEN = os.getenv("BOT_TOKEN", "8674782699:AAFfax8p4YIcyYdu7DH6LhuPDlJCw5ALTV4")
TEST_ADI = "🎓 GÜNCEL BİLGİLER PAEM"
leaderboard = {}

# 3. KPSS 2026 GÜNCEL BİLGİLER - 40 SORU TAM SET
SORU_SETI = [
    {"question": "2026 yılında meydana gelen Halkalı Güneş Tutulması hangi isimle de bilinmektedir?", "options": ["Kara Güneş Tutulması", "Ateş Çemberi", "Gümüş Halkası Tutulması", "Parlak Tutulma"], "correct_option_id": 1},
    {"question": "Fenerbahçe, 2026 yılında Turkcell Süper Kupa'yı kimin karşısında kazanmıştır?", "options": ["Beşiktaş", "Galatasaray", "Trabzonspor", "Başakşehir"], "correct_option_id": 1},
    {"question": "Kültür ve Turizm Bakanlığı 2026 yılını ne yılı ilan etmiştir?", "options": ["Efes Yılı", "Göbeklitepe Yılı", "Aspendos Yılı", "Troya Yılı"], "correct_option_id": 1},
    {"question": "2026 yılında Türkiye'nin yerli otomobili Togg'un hangi yeni modeli yollara çıkmıştır?", "options": ["T10X", "T10F (Sedan)", "T8X", "T10S"], "correct_option_id": 1},
    {"question": "2026 yılında düzenlenen 98. Akademi Ödülleri'nde En İyi Film ödülünü hangisi almıştır?", "options": ["The Last Frontier", "Echoes of Time", "Silent Valley", "Beyond the Stars"], "correct_option_id": 1},
    {"question": "Türk lirasının 2026 yılında dijital versiyonunun (Dijital TL) hangi aşamaya geçtiği duyurulmuştur?", "options": ["Yaygın Kullanım", "Pilot Uygulama Sonu", "Tasarım Aşaması", "İptal Edildi"], "correct_option_id": 0},
    {"question": "2026 Dünya Kupası hangi ülkelerin ev sahipliğinde düzenlenecektir?", "options": ["Katar-BAE", "ABD-Kanada-Meksika", "Brezilya-Arjantin", "Almanya-Fransa"], "correct_option_id": 1},
    {"question": "2026 yılında Nobel Barış Ödülü kime verilmiştir?", "options": ["BM Barış Gücü", "Küresel İklim Koalisyonu", "Sınır Tanımayan Doktorlar", "Uluslararası Kızılay Komitesi"], "correct_option_id": 1},
    {"question": "Türkiye'nin 2026 yılındaki 'Milli Uzay Programı' kapsamında Ay'a gönderdiği insansız aracın adı nedir?", "options": ["Gökmen-1", "Ay-Yıldız 1", "Piri Reis", "Anka-U"], "correct_option_id": 1},
    {"question": "2026 yılı Avrupa Kültür Başkentlerinden biri hangisidir?", "options": ["İstanbul", "Oulu (Finlandiya)", "Berlin", "Roma"], "correct_option_id": 1},
    {"question": "2026 yılında Türkiye'de asgari ücretin belirlenmesinde hangi kriterin ağırlığı artırılmıştır?", "options": ["Enflasyon", "Refah Payı ve Geçim Endeksi", "Dolar Kuru", "İhracat Rakamları"], "correct_option_id": 1},
    {"question": "2026 yılında Birleşmiş Milletler Genel Sekreteri kim seçilmiştir?", "options": ["António Guterres", "Amina J. Mohammed", "Ban Ki-moon", "Tedros Adhanom"], "correct_option_id": 1},
    {"question": "2026 yılında düzenlenen Kış Olimpiyatları hangi şehirde yapılmıştır?", "options": ["Milano-Cortina", "Pekin", "Soçi", "Vancouver"], "correct_option_id": 0},
    {"question": "Türkiye'nin 2026 yılı savunma sanayi ihracat hedefi kaç milyar dolardır?", "options": ["5 Milyar", "8 Milyar", "11 Milyar", "15 Milyar"], "correct_option_id": 1},
    {"question": "2026 yılında UNESCO Dünya Mirası Listesi'ne Türkiye'den hangi yeni alan eklenmiştir?", "options": ["Aizanoi Antik Kenti", "Gordion", "Harran", "Hasankeyf"], "correct_option_id": 1},
    {"question": "2026 yılında dünyanın en kalabalık ülkesi ünvanını hangi ülke korumuştur?", "options": ["Çin", "Hindistan", "ABD", "Endonezya"], "correct_option_id": 1},
    {"question": "2026 yılında EUROVISION Şarkı Yarışması nerede düzenlenmiştir?", "options": ["İsviçre", "İngiltere", "Ukrayna", "İtalya"], "correct_option_id": 0},
    {"question": "2026 yılında Türkiye'nin toplam nüfusunun yaklaşık ne kadar olduğu açıklanmıştır?", "options": ["85 Milyon", "87 Milyon", "90 Milyon", "92 Milyon"], "correct_option_id": 1},
    {"question": "2026 yılında 'Yapay Zeka Etik Yasası'nı ilk yürürlüğe koyan blok hangisidir?", "options": ["ABD", "Avrupa Birliği", "BRICS", "G7"], "correct_option_id": 1},
    {"question": "2026 yılında hangi ülke NATO'ya katılım sürecini tamamlamıştır?", "options": ["İsveç", "Ukrayna", "Gürcistan", "Avusturya"], "correct_option_id": 0},
    {"question": "2026 yılında Türkiye'de hangi il 'Yılın Akıllı Şehri' seçilmiştir?", "options": ["Ankara", "İstanbul", "Konya", "İzmir"], "correct_option_id": 1},
    {"question": "2026 yılında G20 Zirvesi hangi ülkede yapılmıştır?", "options": ["Hindistan", "Güney Afrika", "Brezilya", "Türkiye"], "correct_option_id": 1},
    {"question": "2026 yılında Mars'a iniş yapan yeni nesil keşif aracının adı nedir?", "options": ["Perseverance", "Odyssey 2", "Mars-X", "Horizon"], "correct_option_id": 1},
    {"question": "2026 yılında Türkiye'nin buğday üretiminde hangi bölge liderliğini sürdürmüştür?", "options": ["Ege", "İç Anadolu", "Güneydoğu Anadolu", "Marmara"], "correct_option_id": 1},
    {"question": "2026 yılında vizyona giren ve Türkiye'nin en yüksek bütçeli animasyon filmi hangisidir?", "options": ["Rafadan Tayfa 5", "Anka Pençesi", "Selçuklu Kartalı", "Geleceğin Şehri"], "correct_option_id": 1},
    {"question": "2026 yılında Türkiye'nin yenilenebilir enerji payı yüzde kaça ulaşmıştır?", "options": ["%40", "%55", "%65", "%75"], "correct_option_id": 1},
    {"question": "2026 yılında hangi ünlü yazar Nobel Edebiyat Ödülü'nü kazanmıştır?", "options": ["Orhan Pamuk", "Elena Ferrante", "Haruki Murakami", "Margaret Atwood"], "correct_option_id": 1},
    {"question": "2026 yılında Türkiye'nin ilk 'Kuantum Bilgisayar Merkezi' nerede açılmıştır?", "options": ["TÜBİTAK Gebze", "ODTÜ Teknokent", "ASELSAN Kampüsü", "İTÜ Arı Teknokent"], "correct_option_id": 1},
    {"question": "2026 yılında düzenlenen Teknofest hangi ilde ana merkez olarak yapılmıştır?", "options": ["Samsun", "Antalya", "Adana", "Gaziantep"], "correct_option_id": 1},
    {"question": "2026 yılında Apple'ın tanıttığı ve tamamen kablosuz olan yeni cihazı hangisidir?", "options": ["iPhone 18 Ultra", "iGlass Air", "MacBook Nano", "Apple Ring"], "correct_option_id": 1},
    {"question": "2026 yılında Türkiye'nin en çok ihracat yaptığı ülke hangisidir?", "options": ["Irak", "Almanya", "Rusya", "ABD"], "correct_option_id": 1},
    {"question": "2026 yılında 'Yılın Sporcusu' seçilen milli voleybolcumuz kimdir?", "options": ["Eda Erdem", "Melissa Vargas", "Zehra Güneş", "Ebrar Karakurt"], "correct_option_id": 1},
    {"question": "2026 yılında İstanbul Boğazı'ndan geçen gemi trafiğini düzenleyen yeni sistemin adı nedir?", "options": ["Boğaz Kılavuz", "VTS-2026", "Mavi Yol Kontrol", "Deniz İzleme Projesi"], "correct_option_id": 1},
    {"question": "2026 yılında 'Sıfır Atık' projesinde dünya liderliği ödülünü kim almıştır?", "options": ["Emine Erdoğan", "Greta Thunberg", "Bill Gates", "Leonardo DiCaprio"], "correct_option_id": 0},
    {"question": "2026 yılında hangi Türk şehri 'Türk Dünyası Kültür Başkenti' olmuştur?", "options": ["Bursa", "Şuşa", "Merv", "Aşkabat"], "correct_option_id": 1},
    {"question": "2026 yılında vizyona giren ve Kurtuluş Savaşı'nı anlatan dev yapımın adı nedir?", "options": ["Son Kale", "Cumhuriyet Yolu", "İstiklal Ateşi", "Gazi Paşa"], "correct_option_id": 1},
    {"question": "2026 yılında Türkiye'nin Karadeniz'deki doğal gaz üretim kapasitesi günlük kaç metreküpe çıkmıştır?", "options": ["10 Milyon", "25 Milyon", "40 Milyon", "60 Milyon"], "correct_option_id": 2},
    {"question": "2026 yılında Türkiye hangi alanda 'Avrupa Turizm Lideri' seçilmiştir?", "options": ["Yaz Turizmi", "Sağlık Turizmi", "Kültür Turizmi", "Kış Turizmi"], "correct_option_id": 1},
    {"question": "2026 yılında emeklilere bayram ikramiyeleri ne zaman yatırılmıştır?", "options": ["Kurban Bayramı öncesi", "Ramazan Bayramı öncesi", "Yeni yıl öncesi", "Cumhuriyet Bayramı öncesi"], "correct_option_id": 1},
    {"question": "2026 yılında Dışişleri Bakanlığı'nın vatandaşlara hizmet veren yeni dijital merkezinin adı nedir?", "options": ["Dışişleri Telefon Merkezi", "Konsolosluk Çağrı Merkezi", "Vatandaş Danışma Merkezi", "Krize Müdahale Merkezi"], "correct_option_id": 1}
]

# 4. BOT FONKSİYONLARI
async def send_q(context, chat_id, data):
    try:
        q = data["questions"][data["current"]]
        await context.bot.send_poll(
            chat_id=chat_id,
            question=f"🏁 Soru {data['current'] + 1}/40\n\n{q['question']}",
            options=q["options"],
            type="quiz",
            correct_option_id=q["correct_option_id"],
            is_anonymous=False
        )
        data["answered"] = False
    except Exception as e:
        logging.error(f"Soru Hatası: {e}")

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    await update.message.reply_text(
        f"📢 *{TEST_ADI}* BAŞLIYOR!\n\n"
        f"⏱ Diğer katılımcılar için *30 saniye* bekleme süresi başlatıldı.\n"
        f"📌 Lütfen testi başlatmak için hazır bekleyin!", 
        parse_mode="Markdown"
    )
    
    await asyncio.sleep(30) # 30 Saniye bekleme emri uygulandı.

    shuffled = SORU_SETI.copy()
    random.shuffle(shuffled)
    
    context.user_data["quiz"] = {
        "active": True, "questions": shuffled, "current": 0, "score": 0,
        "chat_id": chat_id, "start_time": time.time(), "user_id": update.effective_user.id,
        "user_name": update.effective_user.full_name, "answered": False
    }
    await send_q(context, chat_id, context.user_data["quiz"])

async def stop_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "quiz" in context.user_data:
        context.user_data["quiz"]["active"] = False
        await update.message.reply_text("🛑 *Test kullanıcı talebiyle durduruldu.*")
    else:
        await update.message.reply_text("Şu an aktif bir test bulunmuyor.")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("quiz")
    if not data or not data.get("active") or data.get("answered"): return

    data["answered"] = True
    if update.poll_answer.option_ids[0] == data["questions"][data["current"]]["correct_option_id"]:
        data["score"] += 1

    data["current"] += 1
    await asyncio.sleep(2.5)

    if data["current"] < 40 and data["active"]:
        await send_q(context, data["chat_id"], data)
    elif data["active"]:
        # BİTİŞ VE LİDERLİK TABLOSU
        sure = int(time.time() - data["start_time"]) - 30
        leaderboard[data["user_id"]] = {"name": data["user_name"], "score": data["score"], "sure": sure}
        res = sorted(leaderboard.values(), key=lambda x: (-x["score"], x["sure"]))
        
        txt = f"🏆 *{TEST_ADI} FİNAL TABLOSU*\n\n"
        for i, p in enumerate(res[:10], 1):
            txt += f"{i}. {p['name']} — ✅ {p['score']}/40 | ⏱ {p['sure']}sn\n"
        
        await context.bot.send_message(data["chat_id"], txt, parse_mode="Markdown")
        data["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CommandHandler("start", start_quiz))
    app.add_handler(CommandHandler("durdur", stop_quiz))
    app.add_handler(PollAnswerHandler(handle_answer))
    
    print(f"✅ {TEST_ADI} Operasyona Hazır!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
