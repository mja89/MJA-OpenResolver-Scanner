# 🚀 MJA OpenResolver Scanner

**سریع‌ترین و هوشمندترین اسکنر Open DNS Resolver**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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

## 📦 نصب

### روش ۱: نصب خودکار (پیشنهادی)

#### برای Linux / macOS / Termux:
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

#### مرحله ۱: کلون کردن پروژه
```bash
git clone https://github.com/mja89/MJA-OpenResolver-Scanner.git
cd MJA-OpenResolver-Scanner
```

#### مرحله ۲: نصب پیش‌نیازها
```bash
pip3 install -r requirements.txt
```

#### مرحله ۳: ایجاد فایل‌های مورد نیاز
```bash
touch client_resolvers.txt scan.log
```

## 🚀 اجرا

```bash
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
  "smart_sampling": true,
  "random_scan": true,
  "batch_size": 1000,
  "save_interval": 60
}
```

## 🎮 حالت‌های عملکرد

| حالت | کارگرها | تایم‌اوت | مناسب برای |
|------|---------|----------|------------|
| 🔋 Battery | 50 | 3.0s | گوشی موبایل |
| ⚖️ Balanced | 100 | 2.0s | استفاده روزمره |
| 🚀 Turbo | 300 | 1.0s | سرورهای قوی |

## 📁 خروجی‌ها

| فایل | توضیحات |
|------|----------|
| `client_resolvers.txt` | لیست رزولورهای پیدا شده |
| `scan_report.csv` | گزارش کامل با جزئیات |
| `scan.log` | لاگ کامل عملیات |
| `state.json` | وضعیت برای ادامه اسکن |

## 📊 مثال خروجی

```
==========================================================
  🚀 MJA OpenResolver Scanner v1.0
==========================================================
  Platform: Linux
  Profile: Balanced
  Workers: 100
  CPU: 45.2%
  RAM: 38.7%
──────────────────────────────────────────────────────────
  Scanned: 1,234,567
  Healthy: 89,234 🟢
  Dead: 1,145,333 🔴
──────────────────────────────────────────────────────────
  Speed: 1,234.56 IPs/sec
  Elapsed: 00:16:40
  Remaining: 02:30:15
==========================================================
```

## 🔧 عیب‌یابی

### خطای "unexpected EOF" در install.sh

اگر با خطای زیر مواجه شدید:
```

./install.sh: line 3: unexpected EOF while looking for matching

```

**راه حل:** 
1. فایل install.sh را با یک ویرایشگر متن باز کنید
2. مطمئن شوید محتوا کامل است
3. یا از روش نصب دستی استفاده کنید:
```bash
pip3 install -r requirements.txt
touch client_resolvers.txt scan.log
chmod +x run.py
python3 run.py
```

خطای "pip3 not found"


# در Termux
```bash
pkg install python-pip
```

# در Ubuntu/Debian
```bash
sudo apt install python3-pip
```

# در CentOS/RHEL
```bash
sudo yum install python3-pip
```

خطای "bc: command not found"

# در Termux
```bash
pkg install bc
```

# در Ubuntu/Debian
```bash
sudo apt install bc
```

خطای Permission denied

```bash
chmod +x install.sh run.py
./install.sh
```

```

## 🛡️ نکات امنیتی

- این ابزار فقط برای **تست امنیتی**2 و **تحقیقاتی** طراحی شده است
- استفاده از آن برای اسکن بدون اجازه ممکن است غیرقانونی باشد
- لطفاً مسئولانه و با رعایت قوانین استفاده کنید

## 🤝 مشارکت در توسعه

1. پروژه را Fork کنید
2. تغییرات خود را اعمال کنید
3. Pull Request ارسال کنید

## 📝 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است.

---

**ساخته شده با ❤️ توسط M.J.Ahmadi**
w
