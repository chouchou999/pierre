from flask import Flask
import threading
import time
import pyquotex  # استدعاء المكتبة بشكل عام أولاً

app = Flask(__name__)

# إعدادات الحساب
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"
ASSET = "USDMXN_otc"

current_price = "جاري جلب السعر..."

def fetch_price():
    global current_price
    # التعديل هنا: الوصول لـ Quotex عبر المسار الصحيح المكتشف في السجلات
    try:
        from pyquotex.api import Quotex
        client = Quotex(email=EMAIL, password=PASSWORD)
    except (ImportError, AttributeError):
        # محاولة بديلة إذا كان المسار مختلفاً
        try:
            from pyquotex import Quotex
            client = Quotex(email=EMAIL, password=PASSWORD)
        except:
            current_price = "خطأ في هيكلة المكتبة"
            return

    check, message = client.connect()
    
    if check:
        client.subscribe_realtime_candle(ASSET, 1)
        while True:
            candles = client.get_realtime_candles(ASSET)
            if candles:
                current_price = list(candles.values())[-1]['close']
            time.sleep(18) 
    else:
        current_price = f"فشل تسجيل الدخول: {message}"

threading.Thread(target=fetch_price, daemon=True).start()

@app.route('/')
def home():
    return f"""
    <html>
        <head><meta http-equiv="refresh" content="18"></head>
        <body style="background-color: #1a1a1a; color: #00ff88; text-align: center; font-family: sans-serif; padding-top: 100px;">
            <h1>USD/MXN OTC Price</h1>
            <div style="font-size: 80px; font-weight: bold;">{current_price}</div>
            <p style="color: #666;">يتم التحديث تلقائياً كل 18 ثانية</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
