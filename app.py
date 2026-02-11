from flask import Flask
import threading
import time
from pyquotex.api import Quotex

app = Flask(__name__)

# --- إعدادات الحساب ---
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"
ASSET = "USDMXN_otc"

# متغير عالمي لتخزين السعر
current_price = "جاري جلب السعر..."

def fetch_price():
    global current_price
    client = Quotex(email=EMAIL, password=PASSWORD)
    check, message = client.connect()
    
    if check:
        client.subscribe_realtime_candle(ASSET, 1)
        while True:
            candles = client.get_realtime_candles(ASSET)
            if candles:
                current_price = list(candles.values())[-1]['close']
            # تحديث كل 18 ثانية حسب استراتيجيتك
            time.sleep(18) 
    else:
        current_price = f"خطأ في الاتصال: {message}"

# تشغيل جلب الأسعار في خلفية السيرفر
threading.Thread(target=fetch_price, daemon=True).start()

@app.route('/')
def home():
    return f"""
    <html>
        <head><meta http-equiv="refresh" content="18"><title>Quotex Price</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>السعر الحالي لزوج {ASSET}</h1>
            <div style="font-size: 48px; color: #2ecc71;">{current_price}</div>
            <p>يتم التحديث تلقائياً كل 18 ثانية</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    # Render يتطلب التسمع على البورت 10000 أو المتغير البيئي
    app.run(host='0.0.0.0', port=10000)
