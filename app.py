import os
import asyncio
import threading
import time
from flask import Flask
from pyquotex.stable_api import Quotex

app = Flask(__name__)

# --- بيانات حسابك (تأكد من كتابتها بدقة) ---
EMAIL = "yasinobr000@gmail.com"
PASSWORD = "mmmmmmmm"
ASSET = "USDMXN_otc"

# متغيرات الحالة العالمية
current_price = "جاري الاتصال..."
last_update = ""

async def price_fetcher_task():
    global current_price, last_update
    
    # تهيئة العميل باستخدام الـ Stable API
    client = Quotex(email=EMAIL, password=PASSWORD)
    
    while True:
        try:
            check, reason = await client.connect()
            if check:
                print(f"✅ Connected to Quotex Stable API for {ASSET}")
                
                # بدء مراقبة السعر اللحظي
                await client.start_realtime_price(ASSET)
                
                while True:
                    # جلب البيانات اللحظية
                    price_data = await client.get_realtime_price(ASSET)
                    if price_data:
                        # الحصول على آخر سعر من القائمة
                        latest = price_data[-1]
                        current_price = f"{latest['price']:.5f}"
                        last_update = time.strftime('%H:%M:%S', time.localtime(latest['time']))
                    
                    # الالتزام بوقت الانتظار الخاص بك (18 ثانية) [2026-02-09]
                    await asyncio.sleep(18)
            else:
                current_price = "فشل تسجيل الدخول"
                print(f"❌ Login failed: {reason}")
                await asyncio.sleep(10) # محاولة إعادة الاتصال بعد 10 ثوانٍ
        except Exception as e:
            print(f"⚠️ Error: {e}")
            await asyncio.sleep(5)

def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(price_fetcher_task())

# تشغيل محرك جلب الأسعار في خيط (Thread) منفصل
threading.Thread(target=run_async_loop, daemon=True).start()

@app.route('/')
def home():
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="18">
            <title>USD/MXN Professional Monitor</title>
            <style>
                body {{ background-color: #0b0e11; color: white; text-align: center; font-family: sans-serif; padding-top: 15vh; }}
                .card {{ background: #161a1e; display: inline-block; padding: 40px; border-radius: 15px; border: 1px solid #2b2f36; }}
                .price {{ font-size: 80px; font-weight: bold; color: #00ff88; margin: 20px 0; }}
                .asset {{ font-size: 24px; color: #848e9c; }}
                .time {{ color: #474d57; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="asset">{ASSET} - LIVE PRICE</div>
                <div class="price">{current_price}</div>
                <div class="time">آخر تحديث بتوقيت السيرفر: {last_update}</div>
            </div>
            <p style="color: #2b2f36; font-size: 12px; margin-top: 20px;">Powered by Stable API & Render</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
