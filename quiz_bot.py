import asyncio
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    PollAnswerHandler, ContextTypes
)

BOT_TOKEN = "8674782699:AAHcpRwEJkET_R4HUkfh_-ar3d35fbL-_10"

# ─────────────────────────────────────────────
#  LİDERLİK TABLOLARI (her kategori için ayrı)
# ─────────────────────────────────────────────
leaderboard = {
    "cmk": {},
    "vatandaslik": {}
}

# ─────────────────────────────────────────────
#  SORU BANKALARI
# ─────────────────────────────────────────────

CMK_SORULAR = [
    {
        "question": "CMK'ya göre 'şüpheli' hangi evrede suç şüphesi altındaki kişidir?",
        "options": ["Kovuşturma evresi", "Soruşturma evresi", "İstinaf evresi", "Temyiz evresi"],
        "correct_option_id": 1,
        "explanation": "📖 Madde 2/a: Şüpheli, soruşturma evresinde suç şüphesi altında bulunan kişidir."
    },
    {
        "question": "CMK'ya göre 'sanık' kimdir?",
        "options": [
            "Soruşturma evresinde suç şüphesi altındaki kişi",
            "Kovuşturmanın başlamasından hükmün kesinleşmesine kadar suç şüphesi altındaki kişi",
            "Kesinleşmiş mahkûmiyet kararı bulunan kişi",
            "Gözaltına alınan kişi"
        ],
        "correct_option_id": 1,
        "explanation": "📖 Madde 2/b: Sanık, kovuşturmanın başlamasından hükmün kesinleşmesine kadar suç şüphesi altındaki kişidir."
    },
    {
        "question": "CMK'ya göre 'müdafi' kimdir?",
        "options": [
            "Katılanı temsil eden avukat",
            "Malen sorumluyu temsil eden avukat",
            "Şüpheli veya sanığın savunmasını yapan avukat",
            "Cumhuriyet savcısının yardımcısı"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 2/c: Müdafi, şüpheli veya sanığın ceza muhakemesinde savunmasını yapan avukattır."
    },
    {
        "question": "CMK'ya göre 'kovuşturma' evresi ne zaman başlar?",
        "options": [
            "Suç şüphesinin öğrenilmesiyle",
            "Gözaltı kararıyla",
            "İddianamenin kabulüyle",
            "Tutuklama kararıyla"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 2/f: Kovuşturma, iddianamenin kabulüyle başlayıp hükmün kesinleşmesine kadar geçen evredir."
    },
    {
        "question": "Toplu suç için kaç veya daha fazla kişi gerekir?",
        "options": ["2 kişi", "3 kişi", "4 kişi", "5 kişi"],
        "correct_option_id": 1,
        "explanation": "📖 Madde 2/k: Toplu suç, aralarında iştirak iradesi bulunmasa da 3 veya daha fazla kişi tarafından işlenen suçtur."
    },
    {
        "question": "CMK Madde 4'e göre mahkeme görevli olup olmadığına hangi aşamada karar verebilir?",
        "options": [
            "Yalnızca iddianamenin kabulünden önce",
            "Yalnızca duruşmanın başında",
            "Kovuşturma evresinin her aşamasında re'sen",
            "Yalnızca tarafların talebiyle"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 4/1: Davaya bakan mahkeme, görevli olup olmadığına kovuşturma evresinin her aşamasında re'sen karar verebilir."
    },
    {
        "question": "CMK'ya göre yetkili mahkeme kural olarak hangi yer mahkemesidir?",
        "options": [
            "Sanığın yerleşim yeri",
            "Suçun işlendiği yer",
            "Mağdurun yerleşim yeri",
            "Cumhuriyet savcısının görev yeri"
        ],
        "correct_option_id": 1,
        "explanation": "📖 Madde 12/1: Davaya bakmak yetkisi, suçun işlendiği yer mahkemesine aittir."
    },
    {
        "question": "Teşebbüs suçlarında yetkili mahkeme hangi yer mahkemesidir?",
        "options": [
            "İlk icra hareketinin yapıldığı yer",
            "Son icra hareketinin yapıldığı yer",
            "Hazırlık hareketlerinin yapıldığı yer",
            "Sanığın yakalandığı yer"
        ],
        "correct_option_id": 1,
        "explanation": "📖 Madde 12/2: Teşebbüste son icra hareketinin yapıldığı yer mahkemesi yetkilidir."
    },
    {
        "question": "CMK'ya göre 'ifade alma' kimin tarafından gerçekleştirilir?",
        "options": [
            "Yalnızca hâkim",
            "Yalnızca mahkeme",
            "Kolluk görevlileri veya Cumhuriyet savcısı",
            "Yalnızca Cumhuriyet savcısı"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 2/g: İfade alma, şüphelinin kolluk görevlileri veya Cumhuriyet savcısı tarafından dinlenmesidir."
    },
    {
        "question": "CMK Madde 7'ye göre görevli olmayan hâkimin işlemleri ne olur?",
        "options": [
            "Hepsi geçerlidir",
            "Yenilenmesi mümkün olmayanlar dışında hükümsüzdür",
            "Hepsi hükümsüzdür",
            "İtirazla geçerli hale gelir"
        ],
        "correct_option_id": 1,
        "explanation": "📖 Madde 7/1: Yenilenmesi mümkün olmayanlar dışında, görevli olmayan hâkim veya mahkemece yapılan işlemler hükümsüzdür."
    },
    {
        "question": "CMK Madde 5'e göre görevsizlik kararına karşı hangi yola başvurulabilir?",
        "options": ["Temyiz", "İtiraz", "İstinaf", "Yargılamanın yenilenmesi"],
        "correct_option_id": 1,
        "explanation": "📖 Madde 5/2: Adlî yargı içerisindeki mahkemeler bakımından verilen görevsizlik kararlarına karşı itiraz yoluna gidilebilir."
    },
    {
        "question": "CMK'ya göre suçun işlendiği yer belli değilse önce hangi yer mahkemesi yetkilidir?",
        "options": [
            "Mağdurun yerleşim yeri",
            "Savcılığın bulunduğu yer",
            "Şüpheli veya sanığın yakalandığı yer",
            "İlk usul işleminin yapıldığı yer"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 13/1: Suçun işlendiği yer belli değilse şüpheli veya sanığın yakalandığı yer mahkemesi yetkilidir."
    },
    {
        "question": "Bilişim suçlarında mağdurun yerleşim yeri mahkemesinin yetkisi CMK'nın hangi maddesiyle düzenlenmiştir?",
        "options": ["Madde 12/3", "Madde 12/5", "Madde 12/6", "Madde 13/2"],
        "correct_option_id": 2,
        "explanation": "📖 Madde 12/6 (Ek: 8/7/2021): Bilişim sistemleri araç kullanılarak işlenen suçlarda mağdurun yerleşim yeri mahkemeleri de yetkilidir."
    },
    {
        "question": "Yabancı ülkede diplomatik bağışıklıktan yararlanan Türk kamu görevlilerinin suçlarında yetkili mahkeme hangisidir?",
        "options": ["İstanbul", "İzmir", "Ankara", "Suçun işlendiği yer"],
        "correct_option_id": 2,
        "explanation": "📖 Madde 14/4: Yabancı ülkelerde diplomatik bağışıklıktan yararlanan Türk kamu görevlilerinin suçlarında yetkili mahkeme Ankara mahkemesidir."
    },
    {
        "question": "CMK'ya göre 'sorgu' kimin tarafından yapılır?",
        "options": [
            "Kolluk görevlileri",
            "Cumhuriyet savcısı",
            "Hâkim veya mahkeme",
            "Müdafi"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 2/h: Sorgu, şüpheli veya sanığın hâkim veya mahkeme tarafından dinlenmesidir."
    },
    {
        "question": "Suçun işlenmesinden sonra suçluyu kayırma fiili CMK'ya göre ne sayılır?",
        "options": ["Ayrı bir suç", "Bağlantılı suç", "Toplu suç", "Suç değildir"],
        "correct_option_id": 1,
        "explanation": "📖 Madde 8/2: Suçun işlenmesinden sonra suçluyu kayırma, suç delillerini yok etme, gizleme veya değiştirme fiilleri bağlantılı suç sayılır."
    },
    {
        "question": "Disiplin hapsi hakkında aşağıdakilerden hangisi doğrudur?",
        "options": [
            "Tekerrüre esas olur",
            "Ertelenebilir",
            "Adlî sicil kayıtlarına geçirilmez",
            "Şartla salıverilme hükümleri uygulanır"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 2/l: Disiplin hapsi adlî sicil kayıtlarına geçirilmeyen, tekerrüre esas olmayan, ertelenemeyen bir yaptırımdır."
    },
    {
        "question": "CMK'ya göre 'malen sorumlu' kişi kim olarak tanımlanır?",
        "options": [
            "Suçtan maddi zarar gören kişi",
            "Hükmün sonuçlarından maddi sorumluluk taşıyarak etkilenecek kişi",
            "Suçun işlenmesine mali destek sağlayan kişi",
            "Tazminat ödemekle yükümlü avukat"
        ],
        "correct_option_id": 1,
        "explanation": "📖 Madde 2/i: Malen sorumlu, hükmün kesinleşmesinden sonra maddi sorumluluk taşıyarak hükmün sonuçlarından etkilenecek kişidir."
    },
    {
        "question": "Duruşmada suçun hukuki niteliği değişirse mahkeme ne yapabilir?",
        "options": [
            "Görevsizlik kararıyla dosyayı alt mahkemeye gönderebilir",
            "Davayı durdurabilir",
            "Görevsizlik kararı vererek dosyayı alt mahkemeye gönderemez",
            "Cumhuriyet savcısından ek iddianame isteyebilir"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 6: Duruşmada suçun hukuki niteliğinin değiştiğinden bahisle görevsizlik kararı verilerek dosya alt dereceli mahkemeye gönderilemez."
    },
    {
        "question": "Zincirleme suçlarda yetkili mahkeme hangisidir?",
        "options": [
            "İlk suçun işlendiği yer",
            "En ağır suçun işlendiği yer",
            "Son suçun işlendiği yer",
            "Sanığın yerleşim yeri"
        ],
        "correct_option_id": 2,
        "explanation": "📖 Madde 12/2: Zincirleme suçlarda son suçun işlendiği yer mahkemesi yetkilidir."
    },
]

VATANDASLIK_SORULAR = [
    # YAŞLAR
    {
        "question": "Türkiye'de milletvekili seçilebilmek için kaç yaşını doldurmuş olmak gerekir?",
        "options": ["21", "25", "18", "30"],
        "correct_option_id": 2,
        "explanation": "📖 Milletvekili seçilebilme yaşı 18'dir."
    },
    {
        "question": "Cumhurbaşkanı adayı olabilmek için kaç yaşını doldurmuş olmak gerekir?",
        "options": ["30", "35", "40", "45"],
        "correct_option_id": 2,
        "explanation": "📖 Cumhurbaşkanı adayı olabilmek için 40 yaşını doldurmuş olmak gerekir."
    },
    {
        "question": "Türk hukukuna göre olağan evlenme yaşı kaçtır?",
        "options": ["16", "17", "18", "15"],
        "correct_option_id": 1,
        "explanation": "📖 Olağan evlenme yaşı 17'dir."
    },
    {
        "question": "Kaza-i rüşt kararı kaç yaşından itibaren alınabilir?",
        "options": ["12", "14", "15", "16"],
        "correct_option_id": 2,
        "explanation": "📖 Kaza-i rüşt (mahkeme kararıyla erginlik) 15 yaşından itibaren alınabilir."
    },
    {
        "question": "Vasiyetname düzenleyebilmek için kaç yaşını doldurmuş olmak gerekir?",
        "options": ["12", "15", "18", "21"],
        "correct_option_id": 1,
        "explanation": "📖 Vasiyetname yazabilmek için 15 yaşını doldurmuş olmak gerekir."
    },
    {
        "question": "Tam ceza ehliyeti kaç yaşında başlar?",
        "options": ["12", "15", "16", "18"],
        "correct_option_id": 3,
        "explanation": "📖 Tam ceza ehliyeti 18 yaşında başlar."
    },
    # İZİNLER
    {
        "question": "Devlet memurlarına tanınan babalık izni kaç gündür?",
        "options": ["5 gün", "7 gün", "10 gün", "14 gün"],
        "correct_option_id": 2,
        "explanation": "📖 Babalık izni 10 gündür."
    },
    {
        "question": "Devlet memurlarına tanınan evlilik izni kaç gündür?",
        "options": ["3 gün", "5 gün", "7 gün", "10 gün"],
        "correct_option_id": 2,
        "explanation": "📖 Evlilik izni 7 gündür."
    },
    {
        "question": "Devlet memurlarına tanınan ölüm izni kaç gündür?",
        "options": ["3 gün", "5 gün", "7 gün", "10 gün"],
        "correct_option_id": 2,
        "explanation": "📖 Ölüm izni 7 gündür."
    },
    {
        "question": "Analık izni toplam kaç haftadır?",
        "options": ["8 hafta", "12 hafta", "16 hafta", "24 hafta"],
        "correct_option_id": 2,
        "explanation": "📖 Analık izni doğumdan önce 8, doğumdan sonra 8 hafta olmak üzere toplam 16 haftadır."
    },
    {
        "question": "İlk 6 ayda süt izni günde kaç saattir?",
        "options": ["1 saat", "2 saat", "3 saat", "4 saat"],
        "correct_option_id": 2,
        "explanation": "📖 İlk 6 ayda süt izni günde 3 saattir."
    },
    # SİYASİ VE YARGI
    {
        "question": "Türkiye Büyük Millet Meclisi toplam kaç milletvekili sayısından oluşur?",
        "options": ["450", "500", "550", "600"],
        "correct_option_id": 3,
        "explanation": "📖 TBMM toplam 600 milletvekilinden oluşur."
    },
    {
        "question": "TBMM'de karar alınabilmesi için gereken yeter sayısı kaçtır?",
        "options": ["151", "200", "276", "301"],
        "correct_option_id": 0,
        "explanation": "📖 TBMM karar yeter sayısı 151'dir."
    },
    {
        "question": "Türkiye'de seçim barajı yüzde kaçtır?",
        "options": ["%5", "%7", "%10", "%3"],
        "correct_option_id": 1,
        "explanation": "📖 Türkiye'de seçim barajı %7'dir."
    },
    {
        "question": "Anayasa Mahkemesi kaç üyeden oluşur?",
        "options": ["11", "13", "15", "17"],
        "correct_option_id": 2,
        "explanation": "📖 Anayasa Mahkemesi (AYM) 15 üyeden oluşur."
    },
    {
        "question": "Yargıtay kaç daireden oluşur?",
        "options": ["32", "36", "40", "45"],
        "correct_option_id": 2,
        "explanation": "📖 Yargıtay 40 daireden oluşur."
    },
    # DİĞER SAYILAR
    {
        "question": "Türkiye'nin yüzölçümü yaklaşık kaç km²'dir?",
        "options": ["583.000 km²", "683.000 km²", "783.000 km²", "883.000 km²"],
        "correct_option_id": 2,
        "explanation": "📖 Türkiye'nin yüzölçümü yaklaşık 783.000 km²'dir."
    },
    {
        "question": "Türkiye'nin en uzun kara sınırı hangi ülkeyle, kaç km'dir?",
        "options": ["Irak - 384 km", "İran - 560 km", "Suriye - 911 km", "Yunanistan - 206 km"],
        "correct_option_id": 2,
        "explanation": "📖 Türkiye'nin en uzun kara sınırı Suriye ile olup 911 km'dir."
    },
    {
        "question": "1-5 yıl arasında çalışan bir devlet memuruna yıllık kaç gün izin verilir?",
        "options": ["10 gün", "14 gün", "20 gün", "26 gün"],
        "correct_option_id": 1,
        "explanation": "📖 1-5 yıl arası çalışanlara yıllık 14 gün izin verilir."
    },
    {
        "question": "NATO'nun toplam üye sayısı kaçtır?",
        "options": ["28", "30", "32", "35"],
        "correct_option_id": 2,
        "explanation": "📖 NATO'nun toplam üye sayısı 32'dir."
    },
]

# ─────────────────────────────────────────────
#  KATEGORİ TANIMI
# ─────────────────────────────────────────────
KATEGORILER = {
    "cmk": {
        "ad": "⚖️ CMK - Ceza Muhakemesi Kanunu",
        "sorular": CMK_SORULAR
    },
    "vatandaslik": {
        "ad": "🇹🇷 Vatandaşlık Genel Bilgiler",
        "sorular": VATANDASLIK_SORULAR
    }
}

# ─────────────────────────────────────────────
#  YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────

def format_sure(saniye):
    saniye = int(saniye)
    if saniye < 60:
        return f"{saniye} saniye"
    dakika = saniye // 60
    kalan = saniye % 60
    if kalan == 0:
        return f"{dakika} dakika"
    return f"{dakika} dakika {kalan} saniye"


def get_quiz_data(context):
    if "quiz" not in context.user_data:
        context.user_data["quiz"] = {
            "active": False,
            "kategori": None,
            "questions": [],
            "current": 0,
            "score": 0,
            "wrong": 0,
            "poll_map": {},
            "chat_id": None,
            "start_time": None,
            "user_name": "",
            "user_id": None
        }
    return context.user_data["quiz"]


def build_leaderboard_text(kategori_key):
    kategori_ad = KATEGORILER[kategori_key]["ad"]
    tablo = leaderboard[kategori_key]

    if not tablo:
        return f"🏆 *{kategori_ad}*\n\nHenüz kimse bu quizi tamamlamadı."

    sirali = sorted(tablo.values(), key=lambda x: (-x["score"], x["sure"]))
    madalyalar = ["🥇", "🥈", "🥉"]
    satirlar = [f"🏆 *LİDERLİK TABLOSU*\n_{kategori_ad}_\n"]

    for i, kayit in enumerate(sirali[:10]):
        sure_str = format_sure(kayit["sure"])
        emoji = madalyalar[i] if i < 3 else f"{i + 1}."
        satirlar.append(
            f"{emoji} {kayit['name']} — "
            f"✅ {kayit['score']} | "
            f"❌ {kayit['wrong']} | "
            f"⏱ {sure_str}"
        )

    return "\n".join(satirlar)


async def send_next_question(chat_id, context, data):
    idx = data["current"]
    q = data["questions"][idx]
    total = len(data["questions"])

    msg = await context.bot.send_poll(
        chat_id=chat_id,
        question=f"❓ Soru {idx + 1}/{total}\n\n{q['question']}",
        options=q["options"],
        type="quiz",
        correct_option_id=q["correct_option_id"],
        explanation=q["explanation"],
        is_anonymous=False,
        open_period=30
    )
    data["poll_map"][msg.poll.id] = idx


# ─────────────────────────────────────────────
#  KOMUTLAR
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Sınava Hazırlık Quiz Botu*\n\n"
        "Merhaba! Bilgini test etmek için bir konu seç.\n\n"
        "▶️ Quiz başlatmak için /quiz\n"
        "🏆 Sıralamayı görmek için /siralama",
        parse_mode="Markdown"
    )


async def quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_quiz_data(context)

    if data["active"]:
        await update.message.reply_text(
            "⚠️ Zaten aktif bir quiz var! Önce /iptal yazın."
        )
        return

    keyboard = [
        [InlineKeyboardButton("⚖️ CMK - Ceza Muhakemesi Kanunu", callback_data="quiz_cmk")],
        [InlineKeyboardButton("🇹🇷 Vatandaşlık Genel Bilgiler", callback_data="quiz_vatandaslik")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📚 *Hangi konuyu çalışmak istersiniz?*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def quiz_kategori_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    kategori_key = query.data.replace("quiz_", "")
    if kategori_key not in KATEGORILER:
        return

    data = get_quiz_data(context)
    if data["active"]:
        await query.message.reply_text("⚠️ Zaten aktif bir quiz var! Önce /iptal yazın.")
        return

    kategori = KATEGORILER[kategori_key]
    user = update.effective_user
    shuffled = kategori["sorular"].copy()
    random.shuffle(shuffled)

    data["active"] = True
    data["kategori"] = kategori_key
    data["questions"] = shuffled
    data["current"] = 0
    data["score"] = 0
    data["wrong"] = 0
    data["poll_map"] = {}
    data["chat_id"] = update.effective_chat.id
    data["start_time"] = time.time()
    data["user_id"] = user.id
    data["user_name"] = user.full_name

    await query.edit_message_text(
        f"🚀 *{kategori['ad']}* quizi başlıyor!\n"
        f"👤 Oyuncu: {user.full_name}\n"
        f"📋 {len(shuffled)} soru | ⏳ Her soru 30 saniye\n\n"
        f"Çıkmak için /iptal yazın.",
        parse_mode="Markdown"
    )
    await asyncio.sleep(1)
    await send_next_question(update.effective_chat.id, context, data)


async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    poll_id = answer.poll_id

    data = context.user_data.get("quiz")
    if not data or not data.get("active"):
        return
    if poll_id not in data["poll_map"]:
        return

    idx = data["poll_map"][poll_id]
    q = data["questions"][idx]
    selected = answer.option_ids[0] if answer.option_ids else -1

    if selected == q["correct_option_id"]:
        data["score"] += 1
    else:
        data["wrong"] += 1

    data["current"] += 1
    chat_id = data["chat_id"]

    await asyncio.sleep(2)

    if data["current"] < len(data["questions"]):
        await send_next_question(chat_id, context, data)
    else:
        await show_results(chat_id, context, data)


async def show_results(chat_id, context, data):
    score = data["score"]
    wrong = data["wrong"]
    total = len(data["questions"])
    pct = (score / total) * 100
    gecen_sure = time.time() - data["start_time"]
    sure_str = format_sure(gecen_sure)
    user_name = data["user_name"]
    user_id = data["user_id"]
    kategori_key = data["kategori"]

    if pct >= 85:
        emoji, yorum = "🏆", "Mükemmel! Gerçek bir uzman olduğunuzu kanıtladınız!"
    elif pct >= 70:
        emoji, yorum = "🥈", "Çok iyi! Biraz daha çalışmayla mükemmele ulaşabilirsiniz."
    elif pct >= 50:
        emoji, yorum = "🥉", "İdare eder. Konuyu tekrar gözden geçirmenizi öneririm."
    else:
        emoji, yorum = "📚", "Daha fazla çalışma gerekiyor!"

    if user_id not in leaderboard[kategori_key] or leaderboard[kategori_key][user_id]["score"] < score:
        leaderboard[kategori_key][user_id] = {
            "name": user_name,
            "score": score,
            "wrong": wrong,
            "sure": int(gecen_sure)
        }

    sonuc_metni = (
        f"{emoji} *{user_name}*\n\n"
        f"✅ Doğru: *{score}*\n"
        f"❌ Yanlış: *{wrong}*\n"
        f"📊 Başarı: *%{pct:.0f}*\n"
        f"⏱ Süre: *{sure_str}*\n\n"
        f"💬 {yorum}\n\n"
        f"Tekrar oynamak için /quiz\n"
        f"Sıralamayı görmek için /siralama"
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=sonuc_metni,
        parse_mode="Markdown"
    )

    await asyncio.sleep(1)
    await context.bot.send_message(
        chat_id=chat_id,
        text=build_leaderboard_text(kategori_key),
        parse_mode="Markdown"
    )

    data["active"] = False


async def siralama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚖️ CMK Sıralaması", callback_data="siralama_cmk")],
        [InlineKeyboardButton("🇹🇷 Vatandaşlık Sıralaması", callback_data="siralama_vatandaslik")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏆 *Hangi kategorinin sıralamasını görmek istersiniz?*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def siralama_goster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kategori_key = query.data.replace("siralama_", "")
    await query.edit_message_text(
        text=build_leaderboard_text(kategori_key),
        parse_mode="Markdown"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Quiz iptal edildi. Yeniden başlamak için /quiz yazın."
    )


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_menu))
    app.add_handler(CommandHandler("iptal", cancel))
    app.add_handler(CommandHandler("siralama", siralama))
    app.add_handler(CallbackQueryHandler(quiz_kategori_sec, pattern="^quiz_"))
    app.add_handler(CallbackQueryHandler(siralama_goster, pattern="^siralama_"))
    app.add_handler(PollAnswerHandler(poll_answer))
    print("✅ Quiz Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
