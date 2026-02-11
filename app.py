import os
import threading
import time
from flask import Flask

# محاولة استدعاء المكتبة بطرق مختلفة لتجنب الخطأ
try:
    from pyquotex.api import Quotex
except ImportError:
    try:
        from pyquotex import Quotex
    except ImportError:
        Quotex = None

app = Flask(__name__)

# --- بيانات حسابك ---
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"
ASSET = "USDMXN_otc"

# متغير لتخزين السعر
current_price = "في انتظار البيانات..."

def fetch_price():
    global current_price
    if Quotex is None:
        current_price = "خطأ: لم يتم العثور على مكتبة Quotex"
        return

    client = Quotex(email=EMAIL, password=PASSWORD)
    check, message = client.connect()
    
    if check:
        client.subscribe_realtime_candle(ASSET, 1)
        while True:
            try:
                candles = client.get_realtime_candles(ASSET)
                if candles:
                    # جلب آخر سعر متاح
                    last_time = list(candles.keys())[-1]
                    current_price = candles[last_time]['close']
                time.sleep(18) # وقت الانتظار الخاص بك
            except Exception as e:
                print(f"Error in loop: {e}")
                time.sleep(5)
    else:
        current_price = f"فشل الاتصال: {message}"

# تشغيل جلب السعر في الخلفية
threading.Thread(target=fetch_price, daemon=True).start()

@app.route('/')
def home():
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="18">
            <style>
                body {{ background-color: #0e1117; color: white; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-top: 15vh; }}
                .price {{ font-size: 80px; font-weight: bold; color: #00ff88; margin: 20px 0; }}
                .asset {{ font-size: 24px; color: #888; text-transform: uppercase; }}
                .status {{ font-size: 14px; color: #555; }}
            </style>
        </head>
        <body>
            <div class="asset">{ASSET} Price Monitor</div>
            <div class="price">{current_price}</div>
            <div class="status">التحديث القادم خلال 18 ثانية...</div>
        </body>
    </html>
    """

if __name__ == "__main__":
    # Render يستخدم المتغير البيئي PORT أو الافتراضي 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
