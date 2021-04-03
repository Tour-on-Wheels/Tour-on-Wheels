from flask import Flask, render_template,request,session,redirect,flash
from datetime import datetime
import psycopg2
import os
import re
import numpy as np

# connection = psycopg2.connect(
#     host = "10.17.50.232",
#     database = "group_40",
#     user = "group_40",
#     password = "CgegedIYggdx1",
#     port = 5432
# )
# cursor = connection.cursor()

# connection = psycopg2.connect(
#     host = "127.0.0.1",
#     database = "irctc_db",
#     user = "krdipen",
#     password = "password",
#     port = 5432
# )

connection = psycopg2.connect(
    host = "127.0.0.1",
    database = "railway",
    user = "postgres",
    password = "1907",
    port = 5432
)

cursor = connection.cursor()

regex_email = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
def check_email(email):   
  
    if(re.search(regex_email,email)):   
        print("Valid Email")   
    else:   
        print("Invalid Email")

regex_mobile = '(0/91)?[1-9][0-9]{9}'
def check_mobile(mobile):   
    if(re.search(regex_mobile,mobile)):   
        print("Valid Phone No")   
    else:   
        print("Invalid Phone No")

app = Flask(__name__)
app.secret_key=os.urandom(30)

@app.route('/', methods=['POST', 'GET'])
def index():
    cursor.execute(f"SELECT name from stations")
    stations = [i[0] for i in cursor.fetchall()]
    
    if(request.method == 'POST'):
        
        src = request.form['source']
        dest = request.form['destination']
        date = request.form['date']
        print(date)
        # cursor.execute(f"SELECT s1.arrival, s1.departure, s1.train_name, s1.train_number, s2.arrival FROM schedules as s1, schedules as s2 where s1.station_name = '{src}' AND s2.station_name = '{dest}' and s1.train_number = s2.train_number ORDER BY s1.arrival;")
        cursor.execute(f"SELECT s1.arrival, s1.departure, s1.train_name, s1.train_number, s2.arrival \
            FROM schedules as s1, \
                schedules as s2 \
            where s1.station_name = '{src}' \
            AND s2.station_name = '{dest}'  \
            and s1.train_number = s2.train_number  \
            AND 0 < ( \
                    SELECT (select sum(seats_available) from total_seats_available where train_id = s1.train_number) - \
                    ( \
                        select count(*) from PNR  \
                        where date ='{date}' \
                        AND train_number = s1.train_number \
                    ) \
                ) \
            ORDER BY s1.arrival;" )
        tasks = cursor.fetchall()
        dis = "block"
        print(len(tasks)) #src, dest, arrival on src, arrival on dest, train_number, train_name
        return render_template('index.html', tasks = tasks, date = date, src=src, dest=dest, stations = stations, dis = dis)
    elif(request.method == 'GET'):
    #     tasks = Todo.query.order_by(Todo.date_created).all()
        dis = 'none'
        return render_template('index.html', stations = stations, dis=dis)

@app.route('/booking/<string:src>/<string:dest>/<string:train_number>/<string:date>')
def booking(src, dest, train_number, date):
    print(train_number)
    print(src)
    print(dest)
    cursor.execute(f"SELECT s1.arrival AS arrival_src, s1.departure AS dept_src, s1.train_name, s1.train_number, s2.arrival AS arrival_dest, ts.class,ts.seats_available - COALESCE(pnr.count, 0) seats \
FROM schedules AS s1, \
    schedules AS s2, \
    total_seats_available AS ts \
    LEFT JOIN \
    ( \
        SELECT coach.class, PNR.train_number, count(*) FROM PNR, coach \
        WHERE DATE ='{date}' \
        AND coach.coach_name = PNR.coach_no \
        GROUP BY coach.class, PNR.train_number \
    ) AS pnr \
    ON (pnr.train_number = ts.train_id \
        AND pnr.class = ts.class) \
    WHERE s1.station_name = '{src}' \
    AND s2.station_name = '{dest}'  \
    AND s1.train_number = s2.train_number \
    AND s1.train_number = '{train_number}' \
    AND ts.train_id = s1.train_number \
    ORDER BY s1.arrival;") 
    tasks = cursor.fetchall()
    return render_template('booking.html', tasks = tasks, date=date, src=src, dest=dest)

@app.route('/info/<string:src>/<string:dest>/<string:train_number>/<string:train_class>/<string:date>', methods=['POST', 'GET'])
def details(src, dest, train_number, train_class, date):
    cursor.execute(f"SELECT s1.arrival AS arrival_src, s1.departure AS dept_src, s1.train_name, s1.train_number, s2.arrival AS arrival_dest, ts.class,ts.seats_available - COALESCE(pnr.count, 0) seats \
        FROM schedules AS s1, \
            schedules AS s2, \
            total_seats_available AS ts \
            LEFT JOIN \
            ( \
                SELECT coach.class, PNR.train_number, count(*) FROM PNR, coach \
                WHERE DATE ='{date}' \
                AND coach.coach_name = PNR.coach_no \
                GROUP BY coach.class, PNR.train_number \
            ) AS pnr \
            ON (pnr.train_number = ts.train_id \
                AND pnr.class = ts.class) \
            WHERE s1.station_name = '{src}' \
            AND s2.station_name = '{dest}'  \
            AND s1.train_number = s2.train_number \
            AND s1.train_number = '{train_number}' \
            AND ts.train_id = s1.train_number \
            AND ts.class='{train_class}' \
            ORDER BY s1.arrival;")
    tasks = cursor.fetchone()

    if(request.method == 'GET'):
        cursor.execute(f"SELECT distinct coach_type from coach where class = '{train_class}'")
        seat_type = cursor.fetchall()[0][0].split()
        all_types = len(seat_type)
        cursor.execute(f"SELECT coach_name, total_seats from coach where class = '{train_class}'")
        all_seats = cursor.fetchall()
        cursor.execute(f"SELECT PNR.coach_no, PNR.seat_no from PNR, coach where PNR.train_number = '{train_number}' \
        and coach.class = '{train_class}' and coach.coach_name = PNR.coach_no and PNR.date = '{date}'")
        filled_seats = cursor.fetchall()
        empty_seats = []
        for c, k in all_seats:
            l = np.arange(1, k+1)
            for s in l:
                if (c, s) not in filled_seats:
                    empty_seats.append((c, s, seat_type[(s-1)%all_types]))
        return render_template('info.html', tasks = tasks, date=date, src=src, dest=dest, prefered_seats = empty_seats)

    elif (request.method == 'POST'):
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        mobile = request.form['mobile']
        seat = request.form['pref']
        # check_email(email)
        # check_mobile(mobile)
        return render_template('print.html', name=name, age=age, gender=gender, email=email, mobile=mobile, seat=seat, tasks=tasks, date=date, src=src, dest=dest)


if __name__ == "__main__":
    app.run(debug=True)