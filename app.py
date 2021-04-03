from flask import Flask, render_template,request,session,redirect,flash
from datetime import datetime
import psycopg2
import os

# connection = psycopg2.connect(
#     host = "10.17.50.232",
#     database = "group_40",
#     user = "group_40",
#     password = "CgegedIYggdx1",
#     port = 5432
# )
# cursor = connection.cursor()

connection = psycopg2.connect(
    host = "localhost",
    database = "railway",
    user = "postgres",
    password = "1907",
    port = 5432
)
cursor = connection.cursor()

app = Flask(__name__)
app.secret_key=os.urandom(30)

@app.route('/', methods=['POST', 'GET'])
def index():
    if(request.method == 'POST'):
        task_content1 = request.form['source']
        task_content2 = request.form['destination']
        date = request.form['date']
        print(date)
        cursor.execute(f"SELECT s1.arrival, s1.departure, s1.train_name, s1.train_number, s2.arrival FROM schedules as s1, schedules as s2 where s1.station_name = '{task_content1}' AND s2.station_name = '{task_content1}' and s1.train_number = s2.train_number ORDER BY s1.arrival;" )
        tasks = cursor.fetchall()
        print(type(tasks[0])) #src, dest, arrival on src, arrival on dest, train_number, train_name
        return render_template('index.html', tasks = tasks, date = date, src=task_content1, dest=task_content2)
    elif(request.method == 'GET'):
    #     tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html')

@app.route('/booking/<string:src>/<string:dest>/<string:train_number>/<string:date>')
def booking(src, dest, train_number, date):
    print(train_number)
    print(src)
    print(dest)
    
    return render_template('booking.html', train_number=train_number, src=src, dest=dest, date=date)

if __name__ == "__main__":
    app.run(debug=True)