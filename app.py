from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1907@localhost/railway'
db = SQLAlchemy(app)

class schedules(db.Model):
    arrival = db.Column(db.TIME())
    day = db.Column(db.Integer)
    train_name = db.Column(db.String)
    station_name = db.Column(db.String)
    id = db.Column(db.Integer, primary_key = True)
    train_number = db.Column(db.String)

class stations(db.Model):
    Xcoordinate = db.Column(db.Float)
    Ycoordinate = db.Column(db.Float)
    state = db.Column(db.String)
    code = db.Column(db.String, primary_key = True)
    name = db.Column(db.String)
    zone = db.Column(db.String)
    address = db.Column(db.String)

@app.route('/', methods=['POST', 'GET'])
def index():
    if(request.method == 'POST'):
        task_content1 = request.form['source']
        task_content2 = request.form['destination']
        tasks = db.engine.execute(text(f"SELECT s1.arrival, s1.departure, s1.train_name, s1.train_number, s2.arrival FROM schedules as s1, schedules as s2 where s1.station_name = '{task_content1}' AND s2.station_name = '{task_content1}' and s1.train_number = s2.train_number ORDER BY s1.arrival" ))
        return render_template('index.html', tasks = tasks, src = task_content1, dest = task_content2)
    elif(request.method == 'GET'):
    #     tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)