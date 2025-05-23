import requests
import secrets
import credentials
import os
from activity_diagram import set_activity, init_db
import datetime
import time
import smtplib
from email.message import EmailMessage

botToken = credentials.botToken

newMessageAvailable = True
offset = 0
last_chat_id = None

def process_messages():
    global last_chat_id
    offset = 0
    newMessageAvailable = True
    while newMessageAvailable:
        response = requests.get(f"https://api.telegram.org/bot{botToken}/getUpdates", data = {'offset' : offset, 'limit' : 1, 'timeout' : 0})
        data = response.json()
        if len(data['result']) == 0:
            newMessageAvailable = False
        else:
            message = data['result'][0]
            text = message['message']['text']
            offset = message['update_id'] + 1
            chat_id = message['message']['chat']['id']
            last_chat_id = chat_id
            try:
                data  = text.split(' ')
                for i in range(3-len(data)):
                    data.append("0")
                day, hour, minute = int(data[0]), int(data[1]), int(data[2])
                time_val = hour + minute / 60
                
                # Calculate the date string for the given day offset
                date = (datetime.date.today() - datetime.timedelta(days=day)).isoformat()

                print(date, time_val)
                set_activity(date, time_val)
                print(f"Saved {time_val} hours for {date}")
            except ValueError:
                print("Invalid input format. Please use 'day hour minute'.")
                response_text = "Invalid format. Please use day hour minute."
                response = requests.post(f"https://api.telegram.org/bot{botToken}/sendMessage", data = {'chat_id' : chat_id, 'text' : response_text})
                continue


def send_image_via_telegram(chat_id, image_path, caption=None):
    url = f"https://api.telegram.org/bot{botToken}/sendPhoto"
    with open(image_path, 'rb') as img_file:
        files = {'photo': img_file}
        data = {'chat_id': chat_id}
        if caption:
            data['caption'] = caption
        response = requests.post(url, files=files, data=data)
    print(f"Telegram sendPhoto response: {response.text}")

def loop():
    last_process_messages = time.time()
    # Calculate the next 5 o'clock (05:00) time
    now = datetime.datetime.now()
    next_five = now.replace(hour=5, minute=0, second=0, microsecond=0)
    if now >= next_five:
        next_five += datetime.timedelta(days=1)
    

    while True:
        # Process messages every hour
        if time.time() - last_process_messages > 60 * 60:
            process_messages()
            last_process_messages = time.time()
        # Check if it's time to print at 5 o'clock
        now = datetime.datetime.now()
        if now >= next_five:
            print("hi it's 5 o clock")
            # Generate activity diagram for current year
            from activity_diagram import plot_activity
            year = now.year
            plot_activity(year)
            img_path = f'activity_{year}.png'
            # Send email with the generated image
            


            print(f"Sent activity diagram for {year} via email.")
            # Send image via Telegram to the last chat_id if available
            try:
                if last_chat_id:
                    send_image_via_telegram(last_chat_id, img_path, caption=f"Activity Diagram {year}")
            except Exception as e:
                print(f"Could not send image via Telegram: {e}")
            next_five += datetime.timedelta(days=1)
        time.sleep(10)


if __name__ == "__main__":
    process_messages()
    init_db()
    loop()