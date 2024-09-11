import flask
from flask import render_template, redirect, request, url_for
import datetime
from database_management import Database
from DayData import DayData

app = flask.Flask(__name__)

db_manager = Database()

def add_missing_days(data):
    max = len(data[0])
    for i in range(1, 7):
        if (len(data[i]) < max):
            for j in range(max - len(data[i])):
                data[i].append({'humanTime': '0', 'value': 0})

    return data

def get_data():
    days = db_manager.get_last_weeks(7)


    dataToReturn = []
    for i in range(7):
        dataToReturn.append([])


    for i in range(len(days)):
        day = days[i]
        dataToReturn[i%7].append(day.export_to_dict())

    data = add_missing_days(dataToReturn)

    return data

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


@app.route('/add-day')
def add_day():
    return render_template('add-day.html', days=get_days_for_input_form())


@app.route('/add-day-save', methods=['POST'])
def add_day_save():
    
    date = request.form['days']
    hours = int(request.form['hours'])
    minutes = int(request.form['minutes'])
    value = hours + minutes / 60.0

    print(f"Date: {date}, Hours: {hours}, Minutes: {minutes}")

    db_manager.add_day(date, value)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)