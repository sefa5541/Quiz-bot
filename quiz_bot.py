import asyncio
import random
import time
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, PollAnswerHandler, ContextTypes
)

# LOGLAMA - Hataları Railway panelinden takip edebilirsiniz
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

# LİDERLİK TABLOSU
leaderboard = {}

# ─────────────────────────────────────────────
#  FINAL GAME: İDARİ YARGILAMA (ANLAŞILIR) SORULARI
# ─────────────────────────────────────────────
# JSON dosyanızdaki tüm 25 soru, seçenekler ve açıklamalar buraya entegre edildi.

FINAL_GAME_SORULAR = [
    {"question": "İdari davalar hangi şekilde görülmektedir?", "options": ["Sözlü duruşmalar ile", "Yazılı yargılama usulü ile", "Bilgisayar üzerinden", "Mahkemenin seçtiği yöntemle"], "correct_option_id": 1, "explanation": "📖 İdari mahkemelerde yazılı yargılama esastır, inceleme evrak üzerinden yapılır."},
    {"question": "Vergiye karşı dava açmak istenirse, süre ne zaman başlar?", "options": ["Rapor verildiğinde", "Verginin tahsil/ödendiği tarihten", "İtiraz yapıldığında", "Bildirimden sonraki gün"], "correct_option_id": 1, "explanation": "📖 Vergi davalarında süre, tahsil, ödeme veya bildirimden itibaren başlar."},
    {"question": "İdareye başvurup 30 gün cevap alınmazsa ne olur?", "options": ["Başvuru kabul edilmiş sayılır", "Başvuru reddedilmiş sayılır", "İdareye 30 gün ek süre verilir", "Hukuki sonuç doğmaz"], "correct_option_id": 1, "explanation": "📖 30 gün içinde cevap gelmezse red sayılır ve dava açma hakkı doğar."},
    {"question": "Dava dilekçesi ilk olarak hangi noktalardan incelenir?", "options": ["İmza ve adres kontrolü", "Görev, yetki, süre ve usul kuralları", "Tarafların kimlik bilgileri", "Davacının ekonomik durumu"], "correct_option_id": 1, "explanation": "📖 Dilekçe; görev, yetki, ehliyet ve süre gibi kapsamlı usul kontrolünden geçer."},
    {"question": "Tam yargı davasında uyuşmazlık miktarı nasıl artırılabilir?", "options": ["Hiçbir şekilde artırılamaz", "Yeni harç ödeyerek bir defaya mahsus", "Yeni dava açarak", "Hakimden izin alarak"], "correct_option_id": 1, "explanation": "📖 Davacı harcını ödeyerek miktar artırımı (ıslah benzeri) yapabilir."},
    {"question": "Duruşma yapılması zorunlu olan davalarda sınır kaçtır?", "options": ["10.000 TL üzeri", "30.000 TL üzeri", "25.000 TL üzeri", "50.000 TL üzeri"], "correct_option_id": 2, "explanation": "📖 25.000 TL üzerindeki iptal ve tam yargı davalarında duruşma zorunludur."},
    {"question": "İvedi (Hızlı) yargılamaya tabi davalar hangileridir?", "options": ["Tazminat davaları", "İhale, kamulaştırma ve çevre kararları", "Vergilendirme işlemleri", "Emeklilik davaları"], "correct_option_id": 1, "explanation": "📖 İhale ve özelleştirme gibi konular hızlı yargılama usulüne tabidir."},
    {"question": "Yürütmenin durdurulması kararı ne zaman verilir?", "options": ["İstendiği her zaman", "Ağır zarar ve açık hukuka aykırılık varsa", "İdare izin verirse", "Hiçbir zaman"], "correct_option_id": 1, "explanation": "📖 Telafisi güç zarar VE açık hukuka aykırılık şartlarının birlikte oluşması gerekir."},
    {"question": "Atama/görev değişikliği işlemleri neden özel şartlara tabidir?", "options": ["İşlemler çok önemli olduğu için", "Uygulanmakla etkisi tükenecek işlem sayılmadığı için", "İdare hızlı yaptığı için", "Gelir kaybı olacağı için"], "correct_option_id": 1, "explanation": "📖 Kamu görevlisi atamaları, uygulanmakla etkisi tükenecek işlemler kategorisinde değildir."},
    {"question": "Mahkeme kararı idarece en geç kaç günde uygulanmalıdır?", "options": ["15 gün", "30 gün", "60 gün", "90 gün"], "correct_option_id": 1, "explanation": "📖 İdare mahkeme kararlarını maksimum 30 gün içinde yerine getirmek zorundadır."},
    {"question": "İdari davada genel yetkili mahkeme hangisidir?", "options": ["Danıştay", "Davanın açıldığı il", "İşlemi yapan idari birimin yeri", "Davacının oturduğu yer"], "correct_option_id": 2, "explanation": "📖 Genel kural: İşlemi yapan idari merciin bulunduğu yer mahkemesi yetkilidir."},
    {"question": "Taşınmaz (ev, arsa) davalarında yetkili mahkeme neresidir?", "options": ["Davacının bulunduğu yer", "Taşınmazın bulunduğu yer", "En yakın büyükşehir", "Danıştay"], "correct_option_id": 1, "explanation": "📖 Taşınmazla ilgili ruhsat, imar gibi davalar taşınmazın olduğu yerde görülür."},
    {"question": "Bağlantılı davalar ne demektir?", "options": ["Aynı davacının tüm davaları", "Aynı anda açılan davalar", "Birbirinin sonucunu etkileyen davalar", "Aynı idareye karşı tüm davalar"], "correct_option_id": 2, "explanation": "📖 Aynı sebepten doğan veya sonucu birbirini etkileyen davalardır."},
    {"question": "İstinaf (yüksek mahkeme) yolu hangi davalar için kapalıdır?", "options": ["Hiçbir dava için", "Belirli parasal limit altındaki davalar", "Sadece emeklilik", "Sadece taşınmaz"], "correct_option_id": 1, "explanation": "📖 Konusu belirli bir miktarı geçmeyen davalar kesinleşir, istinafa gidilemez."},
    {"question": "Temyiz (Danıştay) hakkı hangi konularda sınırlıdır?", "options": ["Tüm davalarda", "Çevre, kültür ve seçim gibi önemli konular", "Sadece emeklilik", "Sadece vergi"], "correct_option_id": 1, "explanation": "📖 Temyiz yolu sadece kanunda sayılan sınırlı ve önemli konularda açıktır."},
    {"question": "Temyiz dilekçesi eksiklikleri kaç günde tamamlanmalıdır?", "options": ["7 gün", "15 gün", "30 gün", "60 gün"], "correct_option_id": 1, "explanation": "📖 Eksikliklerin tamamlanması için ilgilisine 15 günlük süre verilir."},
    {"question": "Danıştay mahkeme kararını hangi sebeple bozabilir?", "options": ["Asla bozamaz", "Yetki dışı işe bakma veya hukuka aykırılık", "Davacının isteğiyle", "Gerekçe yazılmamışsa"], "correct_option_id": 1, "explanation": "📖 Görev/yetki hataları, usul yanlışları ve hukuka aykırılık bozma sebebidir."},
    {"question": "Kanun yararına temyiz hakkı kime verilmiştir?", "options": ["Davacılara", "Danıştay hakimlerine", "Başsavcı ve ilgili bakanlıklara", "Mahkeme başkanlarına"], "correct_option_id": 2, "explanation": "📖 İstisnai bir yol olan kanun yararına temyizi Başsavcı veya Bakanlık isteyebilir."},
    {"question": "Yargılamanın yenilenmesi ne zaman istenir?", "options": ["Asla istenmez", "Sahte belge veya bilirkişi yalanı gibi durumlarda", "Her zaman", "Sadece 1 yıl içinde"], "correct_option_id": 1, "explanation": "📖 Hükmü etkileyen sahtecilik veya çelişkili karar gibi ağır durumlarda istenir."},
    {"question": "Merkezi sınavlara (KPSS vb.) karşı davalar nasıl ilerler?", "options": ["30 günde", "Hızlı sonuçlandırılır (10 gün ilk inceleme)", "Çabuk işlem yok", "Dava açılamaz"], "correct_option_id": 1, "explanation": "📖 Sınav davaları ivedilikle incelenir ve kısa sürede karara bağlanır."},
    {"question": "Askerlik işlemlerine karşı dava nerede açılmalıdır?", "options": ["Danıştay", "Davacının evi", "Görev yaptığı bölge mahkemesinde", "Ankara"], "correct_option_id": 2, "explanation": "📖 Askeri hizmete ilişkin davalar, personelin görev yeri bölgesindeki mahkemede görülür."},
    {"question": "İYUK'ta hüküm yoksa hangi kanun kuralları geçerlidir?", "options": ["Ceza Kanunu", "Medeni Kanun", "Hukuk Usulü Muhakemeleri Kanunu", "Hakimin kendi yargısı"], "correct_option_id": 2, "explanation": "📖 Kanunda açıklanmayan usul hususlarında HUMK/HMK hükümleri uygulanır."},
    {"question": "Emekli edilen memurun davası nerede açılmalıdır?", "options": ["Ankara", "Son çalıştığı yer mahkemesi", "En yakın büyükşehir", "İkametgahı"], "correct_option_id": 1, "explanation": "📖 Görevden uzaklaştırma ve emeklilikte son görev yeri mahkemesi yetkilidir."},
    {"question": "Mahkemeler hangi tarihlerde çalışmaya ara verir?", "options": ["Haziran-Ağustos", "Temmuz-Eylül", "20 Temmuz - 31 Ağustos", "Mayıs-Haziran"], "correct_option_id": 2, "explanation": "📖 Her yıl 20 Temmuz'da başlar, 1 Eylül'de yeni dönem açılır."},
    {"question": "Deprem bölgesi hasar davalarında istinaf süresi kaçtır?", "options": ["30 gün", "20 gün", "15 gün", "10 gün"], "correct_option_id": 2, "explanation": "📖 Deprem afetiyle ilgili özel düzenlemede istinaf süresi 15 güne indirilmiştir."}
]

# ─────────────────────────────────────────────
#  FINAL GAME MEKANİĞİ
# ─────────────────────────────────────────────

def build_leaderboard():
    if not leaderboard: return "🏆 *LİDERLİK TABLOSU (FINAL GAME)*\n\nKayıt yok."
    sirali = sorted(leaderboard.values(), key=lambda x: (-x["score"], x["sure"]))
    res = ["🏆 *LİDERLİK TABLOSU (İYUK)*\n"]
    for i, k in enumerate(sirali[:10]):
        e = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
        res.append(f"{e} {k['name']} — ✅ {k['score']}/25 | ⏱ {k['sure']} sn")
    return "\n".join(res)

async def start_final_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = await update.message.reply_text(f"⏳ *Hazırlan komiserim {user.first_name}!* \n**FINAL GAME (Anlaşılır İYUK)** 15 saniye içinde başlıyor... 🫡", parse_mode="Markdown")
    await asyncio.sleep(15)
    await msg.delete()
    
    shuffled = FINAL_GAME_SORULAR.copy()
    random.shuffle(shuffled)
    context.user_data["quiz"] = {"active": True, "questions": shuffled, "current": 0, "score": 0, "chat_id": update.effective_chat.id, "start_time": time.time(), "user_id": user.id, "user_name": user.full_name}
    await send_q(context)

async def send_q(context):
    data = context.user_data["quiz"]
    q = data["questions"][data["current"]]
    await context.bot.send_poll(chat_id=data["chat_id"], question=f"❓ Soru {data['current'] + 1}/25\n\n{q['question']}", options=q["options"], type="quiz", correct_option_id=q["correct_option_id"], explanation=q["explanation"], is_anonymous=False, open_period=30)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("quiz")
    if not data or not data["active"]: return
    if update.poll_answer.option_ids[0] == data["questions"][data["current"]]["correct_option_id"]: data["score"] += 1
    data["current"] += 1
    await asyncio.sleep(1.5)
    if data["current"] < 25: await send_q(context)
    else:
        sure = int(time.time() - data["start_time"])
        if data["user_id"] not in leaderboard or leaderboard[data["user_id"]]["score"] < data["score"]:
            leaderboard[data["user_id"]] = {"name": data["user_name"], "score": data["score"], "sure": sure}
        await context.bot.send_message(data["chat_id"], build_leaderboard(), parse_mode="Markdown")
        data["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("quiz", start_final_game))
    app.add_handler(CommandHandler("start", start_final_game))
    app.add_handler(PollAnswerHandler(handle_answer))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__": main()
    
