import flask
from flask import render_template

app = flask.Flask(__name__)

def add_missing_days(data):
    max = len(data[0])
    for i in range(1, 7):
        if (len(data[i]) < max):
            for j in range(max - len(data[i])):
                data[i].append({'humanTime': '0', 'value': 0})

    return data

def get_data():
    days = []
    for i in range(100):
        days.append(i)


    dataToReturn = []
    for i in range(7):
        dataToReturn.append([])


    for i in range(len(days)):
        minutes = int(days[i] * 60 % 60)
        hours = int(i)
        dataToReturn[i%7].append({'humanTime': f'{hours}:{minutes}', 'value': days[i]})

    data = add_missing_days(dataToReturn)

    return data

@app.route('/')
def index():
    return render_template('index.html', data = get_data())

if __name__ == '__main__':
    app.run(debug=True)