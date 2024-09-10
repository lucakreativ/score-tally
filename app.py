import flask
from flask import render_template

app = flask.Flask(__name__)

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

    return dataToReturn

@app.route('/')
def index():
    return render_template('index.html', data = get_data())

if __name__ == '__main__':
    app.run(debug=True)