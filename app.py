import os
import threading
import time
import importlib
from flask import Flask

app = Flask(__name__)

# --- بيانات حسابك (تأكد من كتابتها بدقة) ---
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"

# سنقوم بتجربة هذه الأسماء بالترتيب حتى نجد الصحيح
POSSIBLE_ASSETS = ["USDMXN_otc", "USDMXN-OTC", "USDMXN"]

current_price = "جاري الاتصال..."
debug_status = "بدء الفحص الذاتي..."

def get_quotex_class():
    try:
        module = importlib.import_module('pyquotex.api')
        for name in dir(module):
            if "Quotex" in name: return getattr(module, name)
    except:
        try:
            module = importlib.import_module('pyquotex')
            for name in dir(module):
                if "Quotex" in name: return getattr(module, name)
        except: return None
    return None

def fetch_price():
    global current_price, debug_status
    
    QuotexClass = get_quotex_class()
    if not QuotexClass:
        debug_status = "خطأ: لم يتم تثبيت محرك الاتصال بشكل صحيح"
        return

    try:
        debug_status = "محاولة تسجيل الدخول إلى Quotex..."
        client = QuotexClass(email=EMAIL, password=PASSWORD)
        check, message = client.connect()
        
        if check:
            debug_status = "✅ نجح الدخول! جاري البحث عن اسم الزوج الصحيح..."
            
            # محاولة البحث عن الزوج الصحيح
            found_asset = None
            for asset in POSSIBLE_ASSETS:
                client.subscribe_realtime_candle(asset, 1)
                time.sleep(3) # انتظار بسيط للتأكد من الاشتراك
                candles = client.get_realtime_candles(asset)
                if candles:
                    found_asset = asset
                    break
            
            if found_asset:
                debug_status = f"✅ يعمل على: {found_asset}"
                while True:
                    candles = client.get_realtime_candles(found_asset)
                    if candles:
                        last_ts = list(candles.keys())[-1]
                        current_price = f"{candles[last_ts]['close']}"
                    # الالتزام بوقت الانتظار 18 ثانية [cite: 2026-02-09]
                    time.sleep(18)
            else:
                debug_status = "❌ فشل: لم نجد بيانات لزوج USDMXN بجميع الصيغ"
        else:
            current_price = "فشل الدخول"
            debug_status = f"السبب من المنصة: {message}"
    except Exception as e:
        debug_status = f"خطأ تقني: {str(e)}"

# تشغيل الجلب في الخلفية لضمان عمل السيرفر
threading.Thread(target=fetch_price, daemon=True).start()

@app.route('/')
def home():
    return f"""
    <html>
        <head><meta http-equiv="refresh" content="10"></head>
        <body style="background-color: #0b0e11; color: white; text-align: center; font-family: sans-serif; padding-top: 15vh;">
            <div style="font-size: 20px; color: #848e9c;">USD/MXN OTC Monitor</div>
            <div style="font-size: 80px; font-weight: bold; color: #00ff88; margin: 20px 0;">{current_price}</div>
            <hr style="width: 40%; border: 0.1px solid #222; margin: 30px auto;">
            <div style="font-size: 16px; color: #f0b90b; padding: 10px;">الحالة: {debug_status}</div>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
