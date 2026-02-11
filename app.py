import os
import threading
import time
import importlib
from flask import Flask

app = Flask(__name__)

# --- إعدادات الحساب ---
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"
ASSET = "USDMXN_otc"

current_price = "جاري الاتصال بالسيرفر..."

def get_quotex_class():
    """وظيفة ذكية لاستخراج الكلاس الصحيح من المكتبة مهما كانت هيكلتها"""
    try:
        # محاولة الاستيراد الديناميكي
        module = importlib.import_module('pyquotex.api')
        # البحث عن أي كلاس يبدأ اسمه بـ Quotex (سواء Quotex أو QuotexAPI)
        for name in dir(module):
            if "Quotex" in name:
                return getattr(module, name)
    except Exception:
        try:
            module = importlib.import_module('pyquotex')
            for name in dir(module):
                if "Quotex" in name:
                    return getattr(module, name)
        except Exception:
            return None
    return None

def fetch_price():
    global current_price
    time.sleep(5)  # انتظار بسيط للتأكد من استقرار السيرفر عند البدء
    
    QuotexClass = get_quotex_class()
    
    if not QuotexClass:
        current_price = "خطأ: لم يتم العثور على محرك Quotex داخل المكتبة"
        return

    try:
        client = QuotexClass(email=EMAIL, password=PASSWORD)
        check, message = client.connect()
        
        if check:
            # الاشتراك في الزوج (البيزو المكسيكي OTC)
            client.subscribe_realtime_candle(ASSET, 1)
            while True:
                candles = client.get_realtime_candles(ASSET)
                if candles:
                    # جلب السعر الأحدث
                    last_ts = list(candles.keys())[-1]
                    price = candles[last_ts]['close']
                    current_price = f"{price}"
                time.sleep(18) # الانتظار المبرمج الخاص بك
        else:
            current_price = f"فشل تسجيل الدخول: {message}"
    except Exception as e:
        current_price = f"خطأ في جلب البيانات: {str(e)}"

# تشغيل عملية جلب السعر في الخلفية لكي لا يتوقف موقع Flask
threading.Thread(target=fetch_price, daemon=True).start()

@app.route('/')
def home():
    # تصميم بسيط وجذاب يعرض السعر بوضوح
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="18">
            <title>USD/MXN OTC Live</title>
            <style>
                body {{ background-color: #0b0e11; color: #e9ecef; text-align: center; font-family: sans-serif; padding-top: 20vh; }}
                .price {{ font-size: 90px; font-weight: bold; color: #00ff88; text-shadow: 0 0 20px rgba(0,255,136,0.3); }}
                .label {{ font-size: 20px; color: #848e9c; margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="label">{ASSET} LIVE PRICE</div>
            <div class="price">{current_price}</div>
            <p style="color: #474d57;">تحديث تلقائي كل 18 ثانية</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    # الحصول على البورت من Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
