#!/bin/bash

# تابع برای نمایش خطای کاربر و خروج
function error_exit {
    echo "$1" 1>&2
    exit 1
}

# 1. نصب پیش‌نیازهای سیستمی (در صورتی که نصب نشده باشند)
sudo apt update
sudo apt install -y python3 python3-pip || error_exit "Failed to install Python3 and pip."

# 2. نصب پکیج‌های پایتون مورد نیاز
pip3 install requests jdatetime || error_exit "Failed to install required Python packages."

# 3. دریافت TOKEN از کاربر
read -p "Enter your Telegram Bot Token: " TOKEN
if [ -z "$TOKEN" ]; then
    error_exit "Token is required!"
fi

# 4. دریافت CHAT_ID از کاربر
read -p "Enter your Telegram Chat ID: " CHAT_ID
if [ -z "$CHAT_ID" ]; then
    error_exit "Chat ID is required!"
fi

# 5. دریافت فاصله زمانی کرون جاب از کاربر (به ساعت)
read -p "Enter the number of hours between each backup (for every 2 hours): " CRON_INTERVAL
if ! [[ "$CRON_INTERVAL" =~ ^[0-9]+$ ]]; then
    error_exit "Invalid input for cron interval. Must be a positive number."
fi

# 6. دانلود اسکریپت اصلی از GitHub
REPO_URL="https://github.com/nursemazloom/backup-script.git"
git clone $REPO_URL || error_exit "Failed to clone the repository."

# 7. وارد پوشه اسکریپت شویم
cd backup-script || error_exit "Failed to access the script directory."

# 8. جایگذاری TOKEN و CHAT_ID در فایل پایتون
sed -i "s/TOKEN = .*/TOKEN = \"$TOKEN\"/" backup_script.py
sed -i "s/CHAT_ID = .*/CHAT_ID = \"$CHAT_ID\"/" backup_script.py

# 9. ایجاد cron job برای اجرای اسکریپت
CRON_JOB="0 */$CRON_INTERVAL * * * /usr/bin/python3 $(pwd)/backup_script.py"
(crontab -l; echo "$CRON_JOB") | crontab - || error_exit "Failed to create cron job."

echo "Setup complete. The script will run every $CRON_INTERVAL hours."

# 10. حذف فایل Bash Script بعد از اتمام پیکربندی
SCRIPT_PATH="$(realpath $0)"
rm -- "$SCRIPT_PATH" || error_exit "Failed to remove the setup script."
