import os
from flask import Flask
from threading import Thread
import telebot
from google import genai

# Render port hatası vermesin diye minik web sunucusu
app = Flask('')

@app.route('/')
def home():
    return "Bot aktif!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot ve Gemini Ayarları
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

PROMPT = """Sana verilen futbol verilerini ve istatistiklerini analiz et.
Aşağıda belirtilen 31 başlığın TAMAMINI eksiksiz ve sırasıyla yanıtla:

1. Maç Sonucu
2. Toplam Gol Sayısı
3. Her iki takım da gol atar
4. Çifte Şans
5. İlk Yarı sonucu
6. İlk Yarı/Maç Sonucu
7. Asya Toplam Gol Sayısı
8. İki yarıda da gol olur
9. Toplam Şut Sayısı
10. Ev sahibi - Toplam Şut
11. Deplasman - Toplam Şut
12. Toplam İsabetli Şut Sayısı
13. Ev sahibi - Toplam İsabetli Şut
14. Deplasman - Toplam İsabetli Şut Sayısı
15. Toplam Korner Sayısı
16. Ev sahibi - Toplam Korner
17. Deplasman - Toplam Korner
18. Toplam Kart Sayısı
19. Oyuncuya Yapılan Fauller
20. Oyuncu Ofsaytta Kalma
21. Toplam Faul Sayısı
22. Ev sahibi - Toplam Faul
23. Deplasman - Toplam Faul
24. Toplam Ofsayt Sayısı
25. Ev sahibi - Toplam Ofsayt
26. Deplasman - Toplam Ofsayt
27. Toplam Top Çalma Sayısı
28. Ev sahibi - Toplam Top Çalma
29. Deplasman - Toplam Top Çalma
30. Toplam Taç Atışı Sayısı
31. Toplam Kale Vuruşu

Yanıtı net, okunabilir ve tam olarak bu 31 maddeye sadık kalarak ver."""

@bot.message_handler(func=lambda message: True)
def analyze(message):
    bot.reply_to(message, "⏳ Veriler Gemini ile analiz ediliyor...")
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[PROMPT, f"ANALİZ EDİLECEK MAÇ VERİLERİ:\n{message.text}"]
        )
        
        reply_text = response.text
        
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
