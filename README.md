# 🚀 MJA OpenResolver Scanner

**سریع‌ترین و هوشمندترین اسکنر Open DNS Resolver - بدون نیاز به کتابخانه**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Android-orange)](https://github.com)

## ✨ ویژگی‌ها

- ⚡ **AsyncIO Engine** - سرعت بالا با مصرف کم حافظه
- 🧠 **Smart Sampling** - اسکن هوشمند با نمونه‌گیری
- 🔄 **Resume Capability** - ادامه اسکن از نقطه قطع شده
- 📊 **Real-time Dashboard** - داشبورد نمایش لحظه‌ای
- 🎯 **Adaptive Workers** - تنظیم خودکار تعداد کارگرها
- 💾 **Memory Friendly** - مصرف بهینه حافظه حتی برای میلیون‌ها IP
- 🎲 **Random Scan** - اسکن تصادفی برای جلوگیری از تشخیص
- 📈 **Scoring System** - امتیازدهی خودکار به رزولورها
- 📁 **CSV Report** - گزارش کامل با تمام جزئیات
- 🔒 **Safe Stop** - توقف امن با ذخیره وضعیت
- ✅ **بدون نیاز به هیچ کتابخانه خارجی** - فقط Python خالص
- ✅ **خروجی فقط IP** - بدون پورت ۵۳

## 📦 نصب

### روش ۱: نصب خودکار (پیشنهادی)

#### برای Linux / macOS / Termux (اندروید):
```bash
git clone https://github.com/mja89/MJA-OpenResolver-Scanner.git
cd MJA-OpenResolver-Scanner
chmod +x install.sh
./install.sh
```

#### برای Windows:
```cmd
git clone https://github.com/mja89/MJA-OpenResolver-Scanner.git
cd MJA-OpenResolver-Scanner
install.bat
```

### روش ۲: نصب دستی

```bash
# 1. Clone کردن پروژه
git clone https://github.com/mja89/MJA-OpenResolver-Scanner.git
cd MJA-OpenResolver-Scanner

# 2. ایجاد فایل‌های مورد نیاز
touch client_resolvers.txt scan.log   # Linux/macOS/Termux
# یا در ویندوز:
type nul > client_resolvers.txt
type nul > scan.log

# 3. اجرا
python3 run.py   # یا python run.py در ویندوز
```

## 🚀 اجرا

```bash
python3 run.py
```

## 📋 دستورات مفید

### مشاهده نتایج اسکن

```bash
# مشاهده لیست Resolverهای پیدا شده
cat client_resolvers.txt

# مشاهده تعداد Resolverهای پیدا شده
cat client_resolvers.txt | wc -l

# مشاهده ۱۰ خط اول
head -10 client_resolvers.txt

# مشاهده ۱۰ خط آخر
tail -10 client_resolvers.txt
```

### مشاهده گزارش کامل

```bash
# مشاهده گزارش CSV
cat scan_report.csv

# مشاهده با فرمت جدول (اگر column نصب باشد)
column -t -s, scan_report.csv | less

# مشاهده لاگ
cat scan.log

# مشاهده آخرین خطوط لاگ
tail -20 scan.log

# مشاهده لاگ در حال تغییر (实时)
tail -f scan.log
```

### مشاهده وضعیت اسکن

```bash
# مشاهده وضعیت ذخیره شده
cat state.json

# مشاهده وضعیت با فرمت خوانا
python3 -m json.tool state.json
```

### پاک کردن نتایج

```bash
# پاک کردن همه نتایج (شروع از اول)
rm client_resolvers.txt scan_report.csv scan.log state.json

# یا پاک کردن تک تک فایل‌ها
rm client_resolvers.txt   # فقط لیست Resolverها
rm scan_report.csv        # فقط گزارش
rm scan.log               # فقط لاگ
rm state.json             # فقط وضعیت (برای شروع از اول)
```

### ادامه اسکن از نقطه قبلی

```bash
# اگر state.json وجود داشته باشد، اسکن از همان نقطه ادامه می‌یابد
python3 run.py
```

### شروع مجدد اسکن از اول

```bash
# 1. پاک کردن وضعیت
rm state.json

# 2. اجرا
python3 run.py
```

### مشاهده فضای مصرفی

```bash
# مشاهده حجم فایل‌ها
ls -lh client_resolvers.txt scan_report.csv scan.log state.json

# مشاهده حجم کل پوشه
du -sh .
```

### پشتیبان‌گیری از نتایج

```bash
# ایجاد پوشه برای بکاپ
mkdir -p backup

# کپی نتایج در پوشه بکاپ
cp client_resolvers.txt backup/client_resolvers_$(date +%Y%m%d_%H%M%S).txt
cp scan_report.csv backup/scan_report_$(date +%Y%m%d_%H%M%S).csv
```

### اجرا با تنظیمات مختلف

```bash
# اجرا با حالت Battery (مصرف کمتر)
python3 -c "import json; c=open('config.json').read(); d=json.loads(c); d['profile']='battery'; open('config.json','w').write(json.dumps(d, indent=2))"
python3 run.py

# اجرا با حالت Turbo (سرعت بیشتر)
python3 -c "import json; c=open('config.json').read(); d=json.loads(c); d['profile']='turbo'; open('config.json','w').write(json.dumps(d, indent=2))"
python3 run.py
```

## ⚙️ پیکربندی

فایل `config.json` را ویرایش کنید:

```json
{
  "profile": "balanced",
  "targets": [
    "8.8.8.8",
    "1.1.1.0/24",
    "45.0.0.0/8",
    "94.140.14.14:53"
  ],
  "initial_workers": 100,
  "min_workers": 20,
  "max_workers": 500,
  "initial_timeout": 3.0,
  "min_timeout": 1.0,
  "max_timeout": 10.0,
  "batch_size": 1000,
  "save_interval": 60,
  "smart_sampling": true,
  "random_scan": true,
  "dns_query": "google.com"
}
```

### توضیحات تنظیمات:

| پارامتر | توضیحات | مقدار پیش‌فرض |
|---------|---------|---------------|
| `profile` | حالت عملکرد: battery, balanced, turbo | balanced |
| `targets` | لیست آی‌پی‌ها یا رنج‌های مورد نظر | ["8.8.8.8"] |
| `initial_workers` | تعداد کارگرهای اولیه | 100 |
| `min_workers` | حداقل کارگرها | 20 |
| `max_workers` | حداکثر کارگرها | 500 |
| `initial_timeout` | تایم‌اوت اولیه (ثانیه) | 3.0 |
| `batch_size` | تعداد IP در هر دسته | 1000 |
| `smart_sampling` | فعال/غیرفعال کردن نمونه‌گیری هوشمند | true |
| `random_scan` | فعال/غیرفعال کردن اسکن تصادفی | true |
| `dns_query` | دامنه برای تست DNS | google.com |

## 🎮 حالت‌های عملکرد

| حالت | کارگرها | تایم‌اوت | مناسب برای |
|------|---------|----------|------------|
| 🔋 Battery | 50 | 3.0s | گوشی موبایل، تبلت |
| ⚖️ Balanced | 100 | 2.0s | استفاده روزمره |
| 🚀 Turbo | 300 | 1.0s | سرورهای قوی، VPS |

## 📁 خروجی‌ها

پس از اجرا، فایل‌های زیر ایجاد می‌شوند:

| فایل | توضیحات |
|------|----------|
| `client_resolvers.txt` | لیست IP رزولورهای پیدا شده (فقط IP) |
| `scan_report.csv` | گزارش کامل با IP، latency، loss، score |
| `scan.log` | لاگ کامل تمام عملیات |
| `state.json` | وضعیت اسکن برای ادامه از نقطه قطع |

## 📊 مثال خروجی

### داشبورد در حین اسکن:
```
======================================================================
  🚀 MJA OpenResolver Scanner v1.0 (Socket Edition)
======================================================================
  Platform: Android (Termux)
  Profile: Balanced
  Workers: 100
──────────────────────────────────────────────────────────────────────
  Scanned: 1,234,567
  Healthy: 89,234 🟢
  Dead: 1,145,333 🔴
──────────────────────────────────────────────────────────────────────
  Speed: 1,234.56 IPs/sec
  Elapsed: 00:16:40
  Remaining: 02:30:15
======================================================================
  Press Ctrl+C to stop safely
```

### فایل client_resolvers.txt (فقط IP):
```
8.8.8.8
1.1.1.1
94.140.14.14
45.33.22.11
```

### فایل scan_report.csv:
```csv
IP,Latency,Loss,Score,Alive,Timestamp
8.8.8.8,12.5,0,98.6,True,2026-06-29T10:30:15
1.1.1.1,15.2,0,97.4,True,2026-06-29T10:30:16
```

## ⌨️ میانبرهای کیبورد

| کلید | عملکرد |
|------|--------|
| `Ctrl+C` | توقف امن و ذخیره وضعیت |

## 🔧 عیب‌یابی

### خطای "Python not found"
- Python 3.7+ را از [python.org](https://python.org) نصب کنید
- در Termux: `pkg install python`

### خطای "Permission denied"
```bash
chmod +x run.py install.sh
./install.sh
```

### خطای "No module named 'aiodns'"
**نیازی نیست!** این نسخه بدون هیچ کتابخانه خارجی کار می‌کند.

### برنامه هنگ کرد؟
اجازه دهید چند دقیقه کار کند. اگر واقعاً هنگ کرد، `Ctrl+C` بزنید و دوباره اجرا کنید (ادامه می‌دهد).

### خطای "unsupported operand type"
```bash
# پاک کردن state.json و اجرا مجدد
rm state.json
python3 run.py
```

## 🛡️ نکات امنیتی

- این ابزار فقط برای **تست امنیتی** و **تحقیقاتی** طراحی شده است
- استفاده از آن برای اسکن بدون اجازه ممکن است غیرقانونی باشد
- لطفاً مسئولانه و با رعایت قوانین استفاده کنید

## ❓ سوالات متداول

**س: آیا نیاز به نصب کتابخانه خاصی دارم؟**
ج: خیر! این پروژه با Python خالص نوشته شده و هیچ کتابخانه خارجی نیاز ندارد.

**س: در Termux کار می‌کند؟**
ج: بله! کاملاً سازگار است.

**س: چه سرعتی دارد؟**
ج: با تنظیمات پیش‌فرض، حدود ۱۰۰۰ تا ۵۰۰۰ IP در ثانیه (بستگی به اینترنت و سخت‌افزار دارد).

**س: چقدر حافظه مصرف می‌کند؟**
ج: بسیار کم! حتی برای میلیون‌ها IP کمتر از ۱۰۰ مگابایت.

**س: چرا پورت در خروجی نیست؟**
ج: چون همه رزولورها روی پورت ۵۳ هستند و نیازی به نمایش پورت نیست.

**س: چگونه اسکن را متوقف کنم؟**
ج: کلید `Ctrl+C` را بزنید، برنامه به صورت امن متوقف می‌شود و وضعیت ذخیره می‌شود.

## 🤝 مشارکت در توسعه

1. پروژه را Fork کنید
2. تغییرات خود را اعمال کنید
3. Pull Request ارسال کنید

## 📝 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است.

## 📞 ارتباط با ما

- GitHub Issues: [Create Issue](https://github.com/mja89/MJA-OpenResolver-Scanner/issues)

---

**⭐ اگر پروژه را مفید دیدید، به ما ستاره دهید!**

**ساخته شده با ❤️ توسط تیم MJA**
