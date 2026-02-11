import time
from pyquotex.api import Quotex

# --- إعدادات الحساب ---
EMAIL = "your_email@example.com"
PASSWORD = "your_password"

# الزوج المطلوب: الدولار مقابل البيزو المكسيكي OTC
ASSET = "USDMXN_otc" 

client = Quotex(email=EMAIL, password=PASSWORD)
check, message = client.connect()

if check:
    print(f"✅ Connected! Monitoring {ASSET}...")
    client.subscribe_realtime_candle(ASSET, 1)

    try:
        while True:
            candles = client.get_realtime_candles(ASSET)
            if candles:
                # جلب آخر سعر (Close Price)
                last_price = list(candles.values())[-1]['close']
                print(f"🕒 {time.strftime('%H:%M:%S')} | {ASSET}: {last_price}")
            
            # وقت الانتظار المفضل لديك هو 18 ثانية
            time.sleep(18) 
            
    except Exception as e:
        print(f"⚠️ Error: {e}")
else:
    print(f"❌ Login Failed: {message}")
