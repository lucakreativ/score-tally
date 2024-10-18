from flask import render_template, redirect, request, send_file, url_for
from io import BytesIO
import flask
import time
import datetime
import credentials
import os
import requests
import imgkit

from database_management import Database
from DayData import DayData
import secrets

app = flask.Flask(__name__)

scoreTallyUrl = os.environ.get('SCORE_TALLY_URL')
botToken = os.environ.get('BOT_TOKEN')

app.secret_key = secrets.token_hex()

db_manager = Database()

def initialisation():
    credentials.scoreTallyUrl = credentials.scoreTallyUrl[::-1].strip("/")[::-1]

    response = requests.post(f"https://api.telegram.org/bot{credentials.botToken}/setWebhook", data = {'url' : credentials.scoreTallyUrl + '/webhook', 'secret_token' : app.secret_key})
    print(response.text)


def add_missing_days(data):
    max = len(data[0])
    for i in range(1, 7):
        if (len(data[i]) < max):
            for j in range(max - len(data[i])):
                data[i].append({'humanTime': '0', 'value': 0})

    return data

def get_data():
    days = db_manager.get_last_weeks(10)


    dataToReturn = []
    for i in range(7):
        dataToReturn.append([])


    for i in range(len(days)):
        day = days[i]
        dataToReturn[i%7].append(day.export_to_dict())

    #data = add_missing_days(dataToReturn)

    return dataToReturn

def get_days_for_input_form():
    today = datetime.datetime.now() - datetime.timedelta(hours=4)
    days = []
    for i in range(7):
        date = today - datetime.timedelta(days=i)
        dateDatabase = date.strftime("%Y-%m-%d")
        dateHuman = date.strftime("%d.%m.%Y")
        dayOfWeek = date.strftime("%A")
        formattedDate = f"{dayOfWeek:<10}{dateHuman}"
        days.append({'database': dateDatabase, 'human': formattedDate})

    return days


@app.route('/')
def index():
    return render_template('index.html', data=get_data())


@app.route('/webhook', methods=['POST'])
def hello():
    data = request.get_json()

    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') == app.secret_key:
        unixTime = data['message']['date']
        text = data['message']['text']

        try:
            if text.find(" ") != -1:
                value = float(text.split(" ")[0])
                value += float((int(text.split(" ")[1])%4) * 0.25)
            else:
                text = text.replace(",", ".")
                value = float(text)
                
            db_manager.add_day_telegram_addition(unixTime, value)
        except ValueError:
            re = requests.post(f"https://api.telegram.org/bot{credentials.botToken}/sendMessage", data = {'chat_id' : data['message']['from']['id'], 'text' : "Could not parse value."})
    
    

    return "success", 200

@app.route('/add-day')
def add_day():
    return render_template('add-day.html', days=get_days_for_input_form())


@app.route('/get-image')
def get_image():
    path = "images/" + str(time.time()) + ".png"

    config = {
        "width": "1920",
        "height": "1080",
    }

    imgkit.from_url('https://scoretally.eckenfels.xyz', path, options=config)

    return send_file(path, mimetype='image/png', download_name='scoretally.png')


@app.route('/add-day-save', methods=['POST'])
def add_day_save():
    
    date = request.form['days']
    hours = int(request.form['hours'])
    minutes = 0
    if request.form["minutes"] != "":
        minutes = int(request.form['minutes'])
    
    value = hours + minutes / 60.0

    print(f"Date: {date}, Hours: {hours}, Minutes: {minutes}")

    db_manager.add_day(date, value)

    return redirect(url_for('index'))

if __name__ == '__main__':
    initialisation()
    app.run(host="0.0.0.0", debug=False, port=5003)