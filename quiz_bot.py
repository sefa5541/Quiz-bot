import asyncio
import random
import time
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, PollAnswerHandler, ContextTypes
)

# LOGLAMA
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# BURAYA KENDİ TOKENİNİZİ YAZIN
BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

leaderboard = {}

# ─────────────────────────────────────────────
#  FINAL GAME: İYUK (ANLAŞILIR) TAM SET
# ─────────────────────────────────────────────
IYUK_SORU_SETI = [
    {"question": "İdari davalar hangi şekilde görülmektedir?", "options": ["Sözlü duruşmalar ile", "Yazılı yargılama usulü ile", "Bilgisayar üzerinden", "Mahkemenin seçtiği yöntemle"], "correct_option_id": 1, "explanation": "📖 İdari mahkemelerde yazılı yargılama esastır."},
    {"question": "Vergiye karşı dava açmak istenirse, süre ne zaman başlar?", "options": ["Rapor verildiğinde", "Verginin tahsil/ödendiği tarihten", "İtiraz yapıldığında", "Bildirimden sonraki gün"], "correct_option_id": 1, "explanation": "📖 Süre; tahsil, ödeme veya bildirimden itibaren başlar."},
    {"question": "İdareye başvurup 30 gün cevap alınmazsa ne olur?", "options": ["Başvuru kabul edilmiş sayılır", "Başvuru reddedilmiş sayılır", "İdareye 30 gün ek süre verilir", "Hukuki sonuç doğmaz"], "correct_option_id": 1, "explanation": "📖 30 gün sessizlik red (zımni ret) sayılır."},
    {"question": "Mahkemeye açılan dava dilekçesi ilk olarak hangi noktalardan incelenir?", "options": ["İmza ve adres kontrolü", "Görev, yetki, süre ve usul kuralları", "Tarafların kimlik bilgileri", "Davacının ekonomik durumu"], "correct_option_id": 1, "explanation": "📖 İlk inceleme görev, yetki ve süre üzerinden yapılır."},
    {"question": "Tam yargı davasında davacı uyuşmazlık miktarını nasıl artırabilir?", "options": ["Hiçbir şekilde artırılamaz", "Yeni harç ödeyerek bir defaya mahsus", "Yeni dava açarak", "Hakimden izin alarak"], "correct_option_id": 1, "explanation": "📖 Harcı ödenerek miktar bir kez artırılabilir."},
    {"question": "Duruşma yapılması zorunlu olan davalar hangi parasal sınırı aşmalıdır?", "options": ["10.000 TL üzeri", "30.000 TL üzeri", "25.000 TL üzeri", "50.000 TL üzeri"], "correct_option_id": 2, "explanation": "📖 25.000 TL ve üzeri davalarda duruşma zorunludur."},
    {"question": "İvedi (Hızlı) yargılamaya tabi davalar hangileridir?", "options": ["Tazminat davaları", "İhale, kamulaştırma ve çevre kararları", "Vergilendirme işlemleri", "Emeklilik davaları"], "correct_option_id": 1, "explanation": "📖 İhale ve özelleştirme işleri ivedidir."},
    {"question": "Yürütmenin durdurulması kararı ne zaman verilir?", "options": ["İstendiği her zaman", "Ağır zarar ve açık hukuka aykırılık varsa", "İdare izin verirse", "Hiçbir zaman"], "correct_option_id": 1, "explanation": "📖 İki şartın birlikte gerçekleşmesi gerekir."},
    {"question": "Atama/görev değişikliği işlemleri neden özel şartlara tabidir?", "options": ["İşlemler çok önemli olduğu için", "Uygulanmakla etkisi tükenecek işlem sayılmadığı için", "İdare hızlı yaptığı için", "Gelir kaybı olacağı için"], "correct_option_id": 1, "explanation": "📖 Etkisi tükenecek işlem sayılmadığı için savunma alınmadan karar verilmez."},
    {"question": "Mahkeme kararı idarece en geç kaç günde uygulanmalıdır?", "options": ["15 gün", "30 gün", "60 gün", "90 gün"], "correct_option_id": 1, "explanation": "📖 İdare kararı 30 gün içinde uygulamalıdır."},
    {"question": "İdari davada hangi mahkeme yetkilidir? (Genel kural)", "options": ["Her zaman Danıştay", "Davanın açıldığı il", "İşlemi yapan idari birimin yeri", "Davacının oturduğu yer"], "correct_option_id": 2, "explanation": "📖 Yetki kuralı: İşlemi yapan mercinin yeridir."},
    {"question": "Bir evle ilgili belediye işleminden (ruhsat, imar) dava nerede açılır?", "options": ["Davacının evinin olduğu yer", "Evin bulunduğu yerdeki mahkemede", "En yakın büyükşehir", "Danıştayda"], "correct_option_id": 1, "explanation": "📖 Taşınmazın bulunduğu yer mahkemesi yetkilidir."},
    {"question": "Bağlantılı davalar ne demektir?", "options": ["Aynı davacının tüm davaları", "Aynı anda açılan davalar", "Aynı nedenlerden doğan veya sonucu birbirini etkileyen davalar", "Aynı idareye karşı tüm davalar"], "correct_option_id": 2, "explanation": "📖 Birbirinin sonucuna bağlı davalardır."},
    {"question": "İstinaf (yüksek mahkeme) yolu hangi davalar için kapalıdır?", "options": ["Hiçbir dava için", "Belirli parasal limit altındaki davalar", "Sadece emeklilik", "Sadece taşınmaz"], "correct_option_id": 1, "explanation": "📖 Limit altındaki davalar kesin karardır."},
    {"question": "Danıştay'da (TEMYİZ) başvuru yapılabilen davalar nelerdir?", "options": ["Tüm davalar", "Çevre, kültür, seçim gibi önemli konular", "Sadece emeklilik", "Sadece vergi"], "correct_option_id": 1, "explanation": "📖 Sadece kanunda sayılan konular temyiz edilebilir."},
    {"question": "Temyiz dilekçesi eksiklikleri kaç günde tamamlanmalıdır?", "options": ["7 gün", "15 gün", "30 gün", "60 gün"], "correct_option_id": 1, "explanation": "📖 Eksiklik tamamlama süresi 15 gündür."},
    {"question": "Danıştay, mahkeme kararını hangi sebeple bozabilir?", "options": ["Asla bozamaz", "Yetki hatası veya yasalara aykırılık", "Davacının isteğiyle", "Gerekçe yazılmamışsa"], "correct_option_id": 1, "explanation": "📖 Hukuka aykırılık ve görev hatası bozma sebebidir."},
    {"question": "Kanun yararına temyiz hakkı kime verilmiştir?", "options": ["Davacılara", "Danıştay hakim ve savcılarına", "Başsavcı ve ilgili bakanlıklara", "Mahkeme başkanlarına"], "correct_option_id": 2, "explanation": "📖 Başsavcı veya Bakanlık bu yolu kullanabilir."},
    {"question": "Yargılamanın yeniden yapılması ne zaman istenir?", "options": ["Asla istenmez", "Sahte belge, yalan beyan gibi ciddi sebeplerde", "Her zaman", "Sadece 1 yıl içinde"], "correct_option_id": 1, "explanation": "📖 Ağır usul hataları ve sahtecilik durumunda istenir."},
    {"question": "Merkezi sınavlara (KPSS vb.) karşı davalar ne kadar çabuk sonuçlandırılır?", "options": ["30 günde", "Hızlı sonuçlandırılır (10 gün ilk inceleme)", "Çabuk işlem yok", "Dava açılamaz"], "correct_option_id": 1, "explanation": "📖 Sınav davaları ivedi usule tabidir."},
    {"question": "Askerlik işlemlerine karşı dava nerede açılmalıdır?", "options": ["Danıştay", "Davacının evi", "Görev yaptığı yerin bölgesi mahkemesinde", "Ankara"], "correct_option_id": 2, "explanation": "📖 Personelin görev yeri mahkemesi yetkilidir."},
    {"question": "Kanunun açıklamadığı bir konu çıkarsa ne uygulanır?", "options": ["Ceza Kanunu", "Medeni Kanun", "Hukuk Usulü Muhakemeleri Kanunu", "Hakimin kendi yargısı"], "correct_option_id": 2, "explanation": "📖 İYUK'ta hüküm yoksa HMK uygulanır."},
    {"question": "Emekli edilen memurun davası nerede açılmalıdır?", "options": ["Ankara", "Son çalıştığı yer mahkemesi", "En yakın büyükşehir", "Evinin olduğu yer"], "correct_option_id": 1, "explanation": "📖 Son görev yeri yetkilidir."},
    {"question": "Mahkemeler her yıl hangi dönemde kapalı olur?", "options": ["Haziran-Ağustos", "Temmuz-Eylül", "20 Temmuz - 31 Ağustos", "Mayıs-Haziran"], "correct_option_id": 2, "explanation": "📖 Ara verme 20 Temmuz - 31 Ağustos arasıdır."},
    {"question": "Deprem bölgesi hasar davalarında istinaf süresi kaçtır?", "options": ["30 gün", "20 gün", "15 gün", "10 gün"], "correct_option_id": 2, "explanation": "📖 Özel düzenleme gereği 15 gündür."}
]

async def start_final_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Hafızayı temizle
    context.user_data.clear()
    
    msg = await update.message.reply_text(f"⏳ *Hazırlan komiserim {user.first_name}!* \nFinal Game (İYUK) 15 saniye içinde başlıyor...", parse_mode="Markdown")
    await asyncio.sleep(15)
    try: await msg.delete()
    except: pass
    
    shuffled = IYUK_SORU_SETI.copy()
    random.shuffle(shuffled)
    
    context.user_data["quiz"] = {
        "active": True, "questions": shuffled, "current": 0, "score": 0,
        "chat_id": update.effective_chat.id, "start_time": time.time(), "user_id": user.id, "user_name": user.full_name
    }
    await send_q(context)

async def send_q(context):
    data = context.user_data["quiz"]
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

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("quiz")
    if not data or not data.get("active"): return

    if update.poll_answer.option_ids[0] == data["questions"][data["current"]]["correct_option_id"]:
        data["score"] += 1

    data["current"] += 1
    await asyncio.sleep(2.0)

    if data["current"] < 25:
        await send_q(context)
    else:
        # BİTİŞ
        sure = int(time.time() - data["start_time"])
        leaderboard[data["user_id"]] = {"name": data["user_name"], "score": data["score"], "sure": sure}
        sirali = sorted(leaderboard.values(), key=lambda x: (-x["score"], x["sure"]))
        tablo = ["🏆 *LİDERLİK TABLOSU (İYUK)*\n"]
        for i, k in enumerate(sirali[:10]):
            e = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
            tablo.append(f"{e} {k['name']} — ✅ {k['score']}/25 | ⏱ {k['sure']} sn")
        await context.bot.send_message(data["chat_id"], "\n".join(tablo), parse_mode="Markdown")
        data["active"] = False

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("quiz", start_final_game))
    app.add_handler(CommandHandler("start", start_final_game))
    app.add_handler(PollAnswerHandler(handle_answer))
    # 'drop_pending_updates=True' sayesinde bot açılırken eski takılan soruları çöpe atar.
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
