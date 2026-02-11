import os
import subprocess
import sys

# وظيفة لإجبار السيرفر على تثبيت المكتبة من GitHub عند البدء
def install_pyquotex():
    try:
        import pyquotex
    except ImportError:
        print("Installing pyquotex library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/cleitonleonel/pyquotex.git"])

# تنفيذ التثبيت قبل بدء تشغيل Flask
install_pyquotex()

from flask import Flask
import threading
import time
from pyquotex.api import Quotex

app = Flask(__name__)

# --- بيانات حسابك (تأكد من كتابتها بشكل صحيح) ---
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"
ASSET = "USDMXN_otc"

current_price = "في انتظار أول تحديث (18 ثانية)..."

def fetch_price():
    global current_price
    try:
        client = Quotex(email=EMAIL, password=PASSWORD)
        check, message = client.connect()
        
        if check:
            client.subscribe_realtime_candle(ASSET, 1)
            while True:
                candles = client.get_realtime_candles(ASSET)
                if candles:
                    # جلب آخر سعر متاح من القائمة
                    last_time = list(candles.keys())[-1]
                    current_price = f"{candles[last_time]['close']}"
                time.sleep(18)
        else:
            current_price = f"فشل تسجيل الدخول: {message}"
    except Exception as e:
        current_price = f"خطأ تقني: {str(e)}"

# بدء عملية جلب الأسعار في الخلفية
threading.Thread(target=fetch_price, daemon=True).start()

@app.route('/')
def home():
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="18">
            <title>USD/MXN OTC Monitor</title>
        </head>
        <body style="background-color: #0e1117; color: white; text-align: center; font-family: sans-serif; padding-top: 20vh;">
            <div style="font-size: 20px; color: #888;">Live Price for {ASSET}</div>
            <div style="font-size: 80px; font-weight: bold; color: #00ff88; margin: 20px 0;">{current_price}</div>
            <p style="color: #444;">يتم التحديث تلقائياً كل 18 ثانية</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
