import os
import threading
import time
from flask import Flask

# استدعاء مرن للمكتبة لتجنب ImportError
try:
    # المحاولة الأولى: الاستدعاء المباشر
    from pyquotex import Quotex
except ImportError:
    try:
        # المحاولة الثانية: من المسار الفرعي
        from pyquotex.api import Quotex
    except ImportError:
        # المحاولة الثالثة: إذا كانت المكتبة مخزنة داخل كلاس مجهول
        import pyquotex
        Quotex = getattr(pyquotex, 'Quotex', None)

app = Flask(__name__)

# --- بيانات حسابك (تأكد من صحتها) ---
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"
ASSET = "USDMXN_otc"

current_price = "في انتظار البيانات..."

def fetch_price():
    global current_price
    if not Quotex:
        current_price = "خطأ: لم يتم العثور على Quotex داخل المكتبة"
        return

    try:
        client = Quotex(email=EMAIL, password=PASSWORD)
        check, message = client.connect()
        
        if check:
            client.subscribe_realtime_candle(ASSET, 1)
            while True:
                candles = client.get_realtime_candles(ASSET)
                if candles:
                    # جلب آخر سعر محدث
                    last_ts = list(candles.keys())[-1]
                    current_price = f"{candles[last_ts]['close']}"
                # التزاماً بوقت الانتظار الخاص بك (18 ثانية)
                time.sleep(18)
        else:
            current_price = f"فشل الدخول: {message}"
    except Exception as e:
        current_price = f"خطأ تقني: {str(e)}"

# تشغيل المهمة في الخلفية
threading.Thread(target=fetch_price, daemon=True).start()

@app.route('/')
def home():
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="18">
            <title>USD/MXN Monitor</title>
        </head>
        <body style="background-color: #0e1117; color: white; text-align: center; font-family: sans-serif; padding-top: 20vh;">
            <div style="font-size: 20px; color: #888;">{ASSET} Live Price</div>
            <div style="font-size: 80px; font-weight: bold; color: #00ff88;">{current_price}</div>
            <p style="color: #444;">يتم التحديث كل 18 ثانية</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
