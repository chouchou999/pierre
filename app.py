import os
import threading
import time
import importlib
from flask import Flask

app = Flask(__name__)

# --- بيانات حسابك (تأكد من كتابتها بدقة) ---
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"
ASSET = "USDMXN_otc"

current_price = "جاري بدء الاتصال..."
debug_status = "بدء النظام..."

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
        current_price = "خطأ في المكتبة"
        debug_status = "لم يتم العثور على محرك الاتصال"
        return

    try:
        debug_status = "محاولة تسجيل الدخول..."
        client = QuotexClass(email=EMAIL, password=PASSWORD)
        check, message = client.connect()
        
        if check:
            debug_status = f"تم الاتصال! جاري طلب سعر {ASSET}"
            client.subscribe_realtime_candle(ASSET, 1)
            
            # محاولة جلب البيانات لمدة دقيقة
            start_time = time.time()
            while True:
                candles = client.get_realtime_candles(ASSET)
                if candles:
                    last_ts = list(candles.keys())[-1]
                    current_price = f"{candles[last_ts]['close']}"
                    debug_status = "البيانات تصل بنجاح ✅"
                else:
                    # إذا مر وقت طويل ولم تصل بيانات الزوج
                    if time.time() - start_time > 30:
                        debug_status = f"خطأ: الزوج {ASSET} لا يعيد بيانات. تأكد من الاسم."
                
                time.sleep(18) # وقت الانتظار الخاص بك [cite: 2026-02-09]
        else:
            current_price = "فشل تسجيل الدخول"
            debug_status = f"السبب: {message}"
    except Exception as e:
        current_price = "خطأ تقني"
        debug_status = str(e)

threading.Thread(target=fetch_price, daemon=True).start()

@app.route('/')
def home():
    return f"""
    <html>
        <head><meta http-equiv="refresh" content="10"></head>
        <body style="background-color: #0b0e11; color: white; text-align: center; font-family: sans-serif; padding-top: 15vh;">
            <div style="font-size: 20px; color: #848e9c;">{ASSET} PRICE</div>
            <div style="font-size: 70px; font-weight: bold; color: #00ff88;">{current_price}</div>
            <hr style="width: 50%; border: 0.5px solid #222; margin: 30px auto;">
            <div style="font-size: 18px; color: #f0b90b;">حالة السيرفر: {debug_status}</div>
            <p style="color: #474d57; font-size: 12px;">تحديث تلقائي كل 10 ثوانٍ لفحص الحالة</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
