import asyncio
import random
import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    PollAnswerHandler, ContextTypes
)

# Hata ayıklama logları
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

# LİDERLİK TABLOLARI
leaderboard = {
    "cmk": {},
    "vatandaslik": {},
    "iyuk": {}
}

# ─────────────────────────────────────────────
#  TÜM SORULAR BURADA (DOĞRUDAN KODUN İÇİNDE)
# ─────────────────────────────────────────────

CMK_SORULAR = [
    {"question": "CMK'ya göre 'şüpheli' hangi evrede suç şüphesi altındaki kişidir?", "options": ["Kovuşturma evresi", "Soruşturma evresi", "İstinaf evresi", "Temyiz evresi"], "correct_option_id": 1, "explanation": "📖 Madde 2/a: Soruşturma evresidir."},
    {"question": "CMK'ya göre 'sanık' kimdir?", "options": ["Soruşturma evresinde suç şüphesi altındaki kişi", "Kovuşturmanın başlamasından hükmün kesinleşmesine kadar kişi", "Kesinleşmiş mahkûmiyet kararı bulunan kişi", "Gözaltına alınan kişi"], "correct_option_id": 1, "explanation": "📖 Madde 2/b: Kovuşturma evresindeki kişidir."},
    {"question": "CMK'ya göre 'müdafi' kimdir?", "options": ["Katılanı temsil eden avukat", "Malen sorumluyu temsil eden avukat", "Şüpheli veya sanığın savunmasını yapan avukat", "Savcı yardımcısı"], "correct_option_id": 2, "explanation": "📖 Madde 2/c: Savunma yapan avukattır."},
    {"question": "CMK'ya göre 'kovuşturma' evresi ne zaman başlar?", "options": ["Suçun öğrenilmesiyle", "Gözaltı kararıyla", "İddianamenin kabulüyle", "Tutuklama kararıyla"], "correct_option_id": 2, "explanation": "📖 Madde 2/f: İddianamenin kabulüyle başlar."},
    {"question": "Toplu suç için kaç veya daha fazla kişi gerekir?", "options": ["2 kişi", "3 kişi", "4 kişi", "5 kişi"], "correct_option_id": 1, "explanation": "📖 Madde 2/k: 3 veya daha fazla kişi gerekir."},
    {"question": "CMK Madde 4'e göre mahkeme görevli olup olmadığına hangi aşamada karar verebilir?", "options": ["İddianame öncesi", "Duruşma başında", "Kovuşturma evresinin her aşamasında re'sen", "Yalnızca taleple"], "correct_option_id": 2, "explanation": "📖 Madde 4/1: Her aşamada re'sen karar verebilir."},
    {"question": "CMK'ya göre yetkili mahkeme kural olarak hangi yer mahkemesidir?", "options": ["Sanığın yeri", "Suçun işlendiği yer", "Mağdurun yeri", "Savcı görev yeri"], "correct_option_id": 1, "explanation": "📖 Madde 12/1: Suçun işlendiği yer mahkemesidir."},
    {"question": "Gözaltı süresi, yakalama anından itibaren en fazla kaç saattir?", "options": ["12 saat", "24 saat", "48 saat", "72 saat"], "correct_option_id": 1, "explanation": "📖 Gözaltı süresi 24 saati geçemez."},
    {"question": "İfade almada en çok kaç müdafi (avukat) hazır bulunabilir?", "options": ["1", "2", "3", "Sınırsız"], "correct_option_id": 2, "explanation": "📖 İfade almada en çok 3 müdafi hazır bulunabilir."}
]

VATANDASLIK_SORULAR = [
    {"question": "Milletvekili seçilebilmek için kaç yaşını doldurmuş olmak gerekir?", "options": ["21", "25", "18", "30"], "correct_option_id": 2, "explanation": "📖 Seçilme yaşı 18'dir."},
    {"question": "Cumhurbaşkanı adayı olabilmek için kaç yaşını doldurmuş olmak gerekir?", "options": ["30", "35", "40", "45"], "correct_option_id": 2, "explanation": "📖 Adaylık yaşı 40'tır."},
    {"question": "TBMM toplam kaç milletvekilinden oluşur?", "options": ["450", "500", "550", "600"], "correct_option_id": 3, "explanation": "📖 TBMM 600 milletvekilinden oluşur."},
    {"question": "Türkiye'de seçim barajı yüzde kaçtır?", "options": ["%5", "%7", "%10", "%3"], "correct_option_id": 1, "explanation": "📖 Seçim barajı %7'dir."},
    {"question": "Anayasa Mahkemesi kaç üyeden oluşur?", "options": ["11", "13", "15", "17"], "correct_option_id": 2, "explanation": "📖 AYM 15 üyeden oluşur."},
    {"question": "Devlet memurlarına tanınan babalık izni kaç gündür?", "options": ["5 gün", "7 gün", "10 gün", "14 gün"], "correct_option_id": 2, "explanation": "📖 Babalık izni 10 gündür."}
]

IYUK_SORULAR = [
    {"question": "İdari yargıda genel dava açma süresi kaç gündür?", "options": ["15", "30", "60", "90"], "correct_option_id": 2, "explanation": "📖 Madde 7/1: Genel süre 60 gündür."},
    {"question": "Vergi mahkemelerinde dava açma süresi kaç gündür?", "options": ["15", "30", "45", "60"], "correct_option_id": 1, "explanation": "📖 Madde 7/1: Vergi mahkemelerinde süre 30 gündür."},
    {"question": "İvedi yargılama usulünde savunma verme süresi kaç gündür?", "options": ["7 gün", "15 gün", "30 gün", "60 gün"], "correct_option_id": 1, "explanation": "📖 Madde 20/A: Savunma süresi 15 gündür."},
    {"question": "Yürütmenin durdurulması kararına karşı itiraz süresi kaç gündür?", "options": ["7 gün", "15 gün", "30 gün", "60 gün"], "correct_option_id": 0, "explanation": "📖 Madde 27/7: İtiraz süresi 7 gündür."},
    {"question": "İdari makamlara yapılan başvuruya kaç gün içinde cevap verilmezse reddedilmiş sayılır?", "options": ["15", "30", "60", "90"], "correct_option_id": 1, "explanation": "📖 Madde 10: 30 gün içinde cevap verilmezse reddedilmiş sayılır."},
    {"question": "Tam yargı davalarında tazminat miktarı kaç kez artırılabilir?", "options": ["Hiç", "1 kez", "2 kez", "Sınırsız"], "correct_option_id": 1, "explanation": "📖 Madde 16: Miktar bir defaya mahsus olmak üzere artırılabilir."},
    {"question": "Bölge İdare Mahkemesi kararlarına karşı hangi yola başvurulur?", "options": ["İstinaf", "Temyiz", "İtiraz", "Karar düzeltme"], "correct_option_id": 1, "explanation": "📖 Madde 46: Bölge İdare Mahkemesi kararları Danıştay'da temyiz edilir."}
]

KATEGORILER = {
    "cmk": {"ad": "⚖️ CMK", "sorular": CMK_SORULAR},
    "vatandaslik": {"ad": "🇹🇷 Vatandaşlık", "sorular": VATANDASLIK_SORULAR},
    "iyuk": {"ad": "📂 İYUK", "sorular": IYUK_SORULAR}
}

# ─────────────────────────────────────────────
#  YARDIMCI ARAÇLAR
# ─────────────────────────────────────────────

def format_sure(saniye):
    saniye = int(saniye)
    if saniye < 60: return f"{saniye} sn"
    return f"{saniye // 60} dk {saniye % 60} sn"

def build_leaderboard_text(kategori_key):
    kategori_ad = KATEGORILER[kategori_key]["ad"]
    tablo = leaderboard[kategori_key]
    if not tablo: return f"🏆 *LİDERLİK TABLOSU*\n_{kategori_ad}_\n\nHenüz kayıt yok."
    
    sirali = sorted(tablo.values(), key=lambda x: (-x["score"], x["sure"]))
    satirlar = [f"🏆 *LİDERLİK TABLOSU*\n_{kategori_ad}_\n"]
    for i, kayit in enumerate(sirali[:10]):
        emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
        satirlar.append(f"{emoji} {kayit['name']} — ✅ {kayit['score']} | ❌ {kayit['wrong']} | ⏱ {format_sure(kayit['sure'])}")
    return "\n".join(satirlar)

async def send_next_question(context, data):
    q = data["questions"][data["current"]]
    toplam = len(data["questions"])
    msg = await context.bot.send_poll(
        chat_id=data["chat_id"],
        question=f"❓ Soru {data['current'] + 1}/{toplam}\n\n{q['question']}",
        options=q["options"],
        type="quiz",
        correct_option_id=q["correct_option_id"],
        explanation=q["explanation"],
        is_anonymous=False,
        open_period=30
    )
    data["poll_map"][msg.poll.id] = data["current"]

# ─────────────────────────────────────────────
#  KOMUT VE CEVAP İŞLEME
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 *Emniyet Sınav Hazırlık Botu Aktif!*\n\nTesti başlatmak için /quiz yazın.", parse_mode="Markdown")

async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v["ad"], callback_data=f"quiz_{k}")] for k, v in KATEGORILER.items()]
    await update.message.reply_text("📚 *Lütfen bir konu seçin:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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
    
    await query.edit_message_text(f"🚀 *{KATEG
    
