import os
import zipfile
import requests
import jdatetime
from datetime import datetime

# تنظیمات
TOKEN = "YOUR-BOT-TOKEN"
CHAT_ID = "YOUR-CHAT-ID"
FOLDERS = {
    "/opt/marzban": "/opt/marzban",  # مسیر فولدر اول و مقصد بازگردانی
    "/var/lib/marzban": "/var/lib/marzban"   # مسیر فولدر دوم و مقصد بازگردانی
}
BACKUP_DIR = "/root/backup-script"  # مسیر برای ذخیره فایل‌های پشتیبان

# تابع برای بررسی و ایجاد دایرکتوری بکاپ
def ensure_backup_dir_exists(backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Backup directory created: {backup_dir}")
    else:
        print(f"Backup directory exists: {backup_dir}")

# تابع برای حذف فایل بکاپ قبلی
def remove_old_backup(backup_dir):
    files = os.listdir(backup_dir)
    zip_files = [f for f in files if f.endswith('.zip')]
    
    if len(zip_files) > 0:
        # پیدا کردن فایل قدیمی‌ترین بکاپ
        old_backup = min(zip_files, key=lambda f: os.path.getctime(os.path.join(backup_dir, f)))
        old_backup_path = os.path.join(backup_dir, old_backup)
        
        # حذف فایل قدیمی
        os.remove(old_backup_path)
        print(f"Old backup removed: {old_backup_path}")
    else:
        print("No previous backup found to remove.")

# تابع برای زیپ کردن فولدرها با حفظ مسیر کامل
def create_backup(folders, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for folder, _ in folders.items():
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, '/')  # حفظ مسیر کامل از ریشه
                    zipf.write(file_path, arcname)
    print(f"Backup created: {output_zip}")

# تابع برای ارسال فایل زیپ به تلگرام
def send_file(file_path, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        return
    
    with open(file_path, 'rb') as file:
        response = requests.post(url, data={'chat_id': CHAT_ID, 'caption': caption}, files={'document': file})
    
    if response.status_code == 200:
        print("Backup sent successfully.")
    else:
        print(f"Failed to send backup. Error: {response.text}")

# ساخت فایل زیپ با تاریخ شمسی فعلی
now_jalali = jdatetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_zip = os.path.join(BACKUP_DIR, f"backup_{now_jalali}.zip")

# اطمینان از وجود دایرکتوری بکاپ
ensure_backup_dir_exists(BACKUP_DIR)

# حذف بکاپ قدیمی (در صورت وجود)
remove_old_backup(BACKUP_DIR)

# ایجاد بکاپ جدید و ارسال آن به تلگرام
create_backup(FOLDERS, backup_zip)

# تاریخ و ساعت به شمسی برای درج در پیام
now_jalali_text = jdatetime.datetime.now().strftime("%Y/%m/%d")
time_jalali_text = jdatetime.datetime.now().strftime("%H:%M:%S")
send_file(backup_zip, f"بکاپ سرو\nتاریخ: {now_jalali_text}\nساعت: {time_jalali_text}\n.")
