import requests
import secrets
import credentials
import os
from activity_diagram import set_activity, init_db
import datetime
import time
import math
import smtplib
from email.message import EmailMessage
from activity_diagram import plot_activity
import logging
import traceback

logging.basicConfig(filename='score_tally.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

botToken = credentials.botToken

newMessageAvailable = True
offset = 0
last_chat_id = None

def process_messages():
    global last_chat_id
    offset = 0
    newMessageAvailable = True
    while newMessageAvailable:
        try:
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
                    date = (datetime.date.today() -datetime.timedelta(hours=4) - datetime.timedelta(days=day)).isoformat()

                    print(date, time_val)
                    set_activity(date, time_val)
                    print(f"Saved {time_val} hours for {date}")
                except ValueError as e:
                    logging.error(f"[PM-1] ValueError: {e}\n{traceback.format_exc()}")
                    print("Invalid input format. Please use 'day hour minute'.")
                    response_text = "Invalid format. Please use day hour minute."
                    response = requests.post(f"https://api.telegram.org/bot{botToken}/sendMessage", data = {'chat_id' : chat_id, 'text' : response_text})
                    continue
                except Exception as e:
                    logging.error(f"[PM-2] Exception: {e}\n{traceback.format_exc()}")
                    exit(1)
        except Exception as e:
            logging.error(f"[PM-3] Exception: {e}\n{traceback.format_exc()}")
            exit(1)

def send_image_via_telegram(chat_id, image_path, caption=None):
    try:
        url = f"https://api.telegram.org/bot{botToken}/sendPhoto"
        with open(image_path, 'rb') as img_file:
            files = {'photo': img_file}
            data = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
            response = requests.post(url, files=files, data=data)
            logging.info(f"[SIVT-1] Sending image {response.status_code} with response:")
            logging.info(response.text)
        print(f"Telegram sendPhoto response: {response.text}")
    except Exception as e:
        logging.error(f"[SIVT-1] Exception: {e}\n{traceback.format_exc()}")
        exit(1)

def time_for_day(day):
    from activity_diagram import get_activity
    yesterday = day - datetime.timedelta(days=1)
    try:
        bonus = 0
        val = get_activity(day.isoformat())
        yes_val = get_activity(yesterday.isoformat())
        weekday = day.weekday()
        if (yesterday.weekday() - 1) % 7 < 5:
            bonus = max(0, 8 - yes_val) * (5/7)
        else:
            bonus = max(0, 3 - yes_val) * (5/7)
        
        return val + bonus
    except Exception as e:
        logging.error(f"[TFD-1] Exception: {e}\n{traceback.format_exc()}")
        return 0

def get_streak():
    from activity_diagram import get_activity
    import datetime
    today = datetime.date.today()
    streak = 0
    for i in range(1, 365):
        day = today - datetime.timedelta(days=i)
        weekday = day.weekday()
        val = time_for_day(day)
        if weekday < 5:
            if val >= 8:
                streak += 1
            else:
                break
        else:
            if val >= 3:
                streak += 1
            else:
                break
    return streak

def loop(chat_id):
    try:
        last_process_messages = time.time()
        # Calculate the next 5 o'clock (05:00) time
        now = datetime.datetime.now()
        next_five = now.replace(hour=5, minute=0, second=0, microsecond=0)
        if now >= next_five:
            next_five += datetime.timedelta(days=1)
        while True:
            try:
                # Process messages every hour
                if time.time() - last_process_messages > 60 * 60:
                    logging.info("Processing Messages")
                    process_messages()
                    last_process_messages = time.time()
                # Check if it's time to print at 5 o'clock
                now = datetime.datetime.now()
                if now >= next_five:
                    print("hi it's 5 o clock")
                    logging.info("[It's 5 o clock]")
                    # Generate activity diagram for current year
                    year = now.year
                    try:
                        plot_activity(year)
                    except Exception as e:
                        logging.error(f"[LOOP-PA-1] Exception: {e}\n{traceback.format_exc()}")
                        exit(1)
                    img_path = f'activity_{year}.png'
                    # Calculate how much time is needed today for a green box, including bonus from yesterday
                    today = datetime.date.today()
                    weekday = today.weekday()
                    from activity_diagram import get_activity
                    try:
                        current_val = get_activity(today.isoformat())
                        # Get yesterday's value
                        yesterday = today - datetime.timedelta(days=1)
                        yesterday_val = get_activity(yesterday.isoformat())
                        bonus = 0
                        if yesterday.weekday() < 5:
                            bonus = max(0, yesterday_val - 8) * (5/7)
                        else:
                            bonus = max(0, yesterday_val - 3) * (5/7)
                        if weekday < 5:
                            needed = max(0, 8 - (current_val + bonus))
                        else:
                            needed = max(0, 3 - (current_val + bonus))
                        hours_n = int(needed)
                        minutes_n = math.ceil((needed * 60) % 60)
                        hours_b = int(bonus)
                        minutes_b = int((bonus * 60) % 60)
                        streak = get_streak()
                        if needed == 0:
                            green_msg = f"Today's box is already green!\nStreak: {streak}"
                        else:
                            green_msg = f"Bonus: {hours_b}h {minutes_b}m\nNeeded: {hours_n}h {minutes_n}m\nStreak: {streak}"
                    except Exception as e:
                        logging.error(f"[LOOP-GREEN-1] Exception: {e}\n{traceback.format_exc()}")
                        green_msg = "Error calculating needed time."

                    # Send image via Telegram to the last chat_id if available, with green box info
                    try:
                        send_image_via_telegram(chat_id, img_path, caption=f"Activity Diagram {year}\n{green_msg}")
                    except Exception as e:
                        logging.error(f"[LOOP-SEND-1] Exception: {e}\n{traceback.format_exc()}")
                        print(f"Could not send image via Telegram: {e}")
                        exit(1)
                    print(f"Sent activity diagram for {year} via email.")
                    next_five += datetime.timedelta(days=1)
                time.sleep(10)
            except Exception as e:
                logging.error(f"[LOOP-1] Exception: {e}\n{traceback.format_exc()}")
                exit(1)
    except Exception as e:
        logging.error(f"[LOOP-2] Exception: {e}\n{traceback.format_exc()}")
        exit(1)

if __name__ == "__main__":
    try:
        init_db()
        process_messages()
        plot_activity(datetime.date.today().year)
        send_image_via_telegram(1037787051, "activity_"+str(datetime.date.today().year) +".png")
        loop(1037787051)
    except Exception as e:
        logging.error(f"[MAIN-1] Exception: {e}\n{traceback.format_exc()}")
        exit(1)