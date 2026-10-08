import os
from flask import Flask
from threading import Thread
import telebot
from google import genai

# Render port ayarı için Flask web sunucusu
app = Flask('')

@app.route('/')
def home():
    return "Bot aktif!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Ortam Değişkenleri
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

PROMPT = """Sen dünyaca ünlü, profesyonel bir Futbol Analisti ve Bahis Matematiği Uzmanısın.

Sana verilen kuponlar, maç listeleri veya özel bahisler için derinlemesine bir BAŞA BAŞ (IMPLIED PROBABILITY) VE MODEL ANALİZİ yapacaksın.

ANALİZ METHODUN VE ŞABLONUN (HER MAÇ İÇİN BİREBİR UYGULA):

1. **Oran ve Başa Baş İhtimali Hesabı:**
   - Verilen bahsin oranının gerektirdiği teorik kazanma yüzdesini hesapla (1 / Oran).
   - Takımın güncel form durumu, son 5-10 maç trendleri, gol/köşe ortalamaları ve H2H geçmişini incele.
   - İstatistiki veriler ile oran arasındaki farkı değerlendir (Value var mı, yoksa oran değersiz mi?).

2. **Kategori ve Karar Ver:**
   Her seçim için kesin bir karar ver ve simgeleri kullan:
   - 🟢 TUT / TUTULABİLİR (Güven Skoru: X/10)
   - 🟠 SINIRDA / RİSKLİ (Güven Skoru: X/10)
   - 🔴 ÇIKAR / ÇIKARILMALI (Nedeniyle birlikte)

3. **NİHAİ KUPON ÖZETİ VE ÇEKİRDEK KUPON:**
   Analizin en sonunda şunları sun:
   - **Genel Kupon Değerlendirmesi Tablosu:** (Sıra | Maç | Bahis | Oran | Karar | Güven)
   - **Tavsiye Edilen Çekirdek Kupon:** Kupondan çıkarılması gereken riskli/değersiz maçları eleyip elindeki en sağlam 3-5 maçlık kombinasyonu oluştur.

Lütfen yüzeysel veya geçiştirme yanıtlar verme. Tıpkı profesyonel bir finansal/istatistiki rapor sunar gibi net sayılar, olasılık karşılaştırmaları ve açık kararlarla analiz üret."""

@bot.message_handler(func=lambda message: True)
def analyze(message):
    bot.reply_to(message, "📊 Derin matematiksel analiz yapılıyor ve model verileri hesaplanıyor, lütfen bekleyin...")
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[PROMPT, f"ANALİZ EDİLECEK MAÇLAR VE BAHİSLER:\n{message.text}"]
        )
        
        reply_text = response.text
        
        # Telegram mesaj sınırı (4000 karakter) kontrolü
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                bot.send_message(message.chat.id, reply_text[i:i+4000])
        else:
            bot.reply_to(message, reply_text)
            
    except Exception as e:
        bot.reply_to(message, f"Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    bot.polling(non_stop=True)
