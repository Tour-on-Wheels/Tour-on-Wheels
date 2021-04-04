from flask import Flask, render_template,request,session,redirect,flash
import psycopg2
import os
import re
import numpy as np

connection = psycopg2.connect(
    host = "10.17.50.232",
    database = "group_40",
    user = "group_40",
    password = "CgegedIYggdx1",
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
        cursor.execute(f"SELECT s1.arrival, s1.departure, s1.train_name, s1.train_number, s2.arrival, TO_DATE('{date}','YYYY-MM-DD') + s2.day - s1.day AS arrival_date \
            FROM schedules as s1, \
                schedules as s2 \
            where s1.station_name = '{src}' \
            AND s2.station_name = '{dest}'  \
            AND s1.train_number = s2.train_number  \
            AND (s2.day > s1.day OR (s2.day = s1.day AND s2.arrival >= s1.departure)) \
            AND 0 < ( \
                    SELECT (select sum(seats_available) from total_seats_available where train_id = s1.train_number) - \
                    ( \
                        select count(*) from PNR  \
                        where date ='{date}' \
                        AND train_number = s1.train_number \
                        AND delete=0 \
                    ) \
                ) \
            ORDER BY s1.arrival;" )
        tasks = cursor.fetchall()
        dis = "block"
        print(len(tasks))
        return render_template('index.html', tasks = tasks, date = date, src=src, dest=dest, stations = stations, dis = dis)
    elif(request.method == 'GET'):
        dis = 'none'
        return render_template('index.html', stations = stations, dis=dis)

@app.route('/booking/<string:src>/<string:dest>/<string:train_number>/<string:date>')
def booking(src, dest, train_number, date):
    print(train_number)
    print(src)
    print(dest)
    cursor.execute(f"SELECT s1.arrival AS arrival_src, s1.departure AS dept_src, s1.train_name, s1.train_number, s2.arrival AS arrival_dest, ts.class,ts.seats_available - COALESCE(pnr.count, 0) seats, TO_DATE('{date}','YYYY-MM-DD') + s2.day - s1.day AS arrival_date \
    FROM schedules AS s1, \
    schedules AS s2, \
    total_seats_available AS ts \
    LEFT JOIN \
    ( \
        SELECT coach.class, PNR.train_number, count(*) FROM PNR, coach \
        WHERE DATE ='{date}' \
        AND coach.coach_name = PNR.coach_no \
        AND PNR.delete = 0 \
        GROUP BY coach.class, PNR.train_number \
    ) AS pnr \
    ON (pnr.train_number = ts.train_id \
        AND pnr.class = ts.class) \
    WHERE s1.station_name = '{src}' \
    AND s2.station_name = '{dest}'  \
    AND s1.train_number = s2.train_number \
    AND (s2.day > s1.day OR (s2.day = s1.day AND s2.arrival >= s1.departure)) \
    AND s1.train_number = '{train_number}' \
    AND ts.train_id = s1.train_number \
    ORDER BY s1.arrival;") 
    tasks = cursor.fetchall()
    return render_template('booking.html', tasks = tasks, date=date, src=src, dest=dest)

@app.route('/info/<string:src>/<string:dest>/<string:train_number>/<string:train_class>/<string:date>/<string:status>', methods=['POST', 'GET'])
def details(src, dest, train_number, train_class, date, status):
    cursor.execute(f"SELECT s1.arrival AS arrival_src, s1.departure AS dept_src, s1.train_name, s1.train_number, s2.arrival AS arrival_dest, ts.class,ts.seats_available - COALESCE(pnr.count, 0) seats, TO_DATE('{date}','YYYY-MM-DD') + s2.day - s1.day AS arrival_date \
            FROM schedules AS s1, \
            schedules AS s2, \
            total_seats_available AS ts \
            LEFT JOIN \
            ( \
                SELECT coach.class, PNR.train_number, count(*) FROM PNR, coach \
                WHERE DATE ='{date}' \
                AND coach.coach_name = PNR.coach_no \
                AND PNR.delete = 0 \
                GROUP BY coach.class, PNR.train_number \
            ) AS pnr \
            ON (pnr.train_number = ts.train_id \
                AND pnr.class = ts.class) \
            WHERE s1.station_name = '{src}' \
            AND s2.station_name = '{dest}'  \
            AND s1.train_number = s2.train_number \
            AND (s2.day > s1.day OR (s2.day = s1.day AND s2.arrival >= s1.departure)) \
            AND s1.train_number = '{train_number}' \
            AND ts.train_id = s1.train_number \
            AND ts.class='{train_class}' \
            ORDER BY s1.arrival;")
    tasks = cursor.fetchone()
    print(tasks)
    if(request.method == 'GET'):
        cursor.execute(f"SELECT distinct coach_type from coach where class = '{train_class}'")
        seat_type = cursor.fetchall()[0][0].split()
        all_types = len(seat_type)
        cursor.execute(f"SELECT coach_name, total_seats from coach where class = '{train_class}'")
        all_seats = cursor.fetchall()
        cursor.execute(f"SELECT PNR.coach_no, PNR.seat_no from PNR, coach where PNR.train_number = '{train_number}' AND PNR.delete = 0 \
        and coach.class = '{train_class}' and coach.coach_name = PNR.coach_no and PNR.date = '{date}'")
        filled_seats = cursor.fetchall()
        empty_seats = []
        for c, k in all_seats:
            l = np.arange(1, k+1)
            for s in l:
                if (c, s) not in filled_seats:
                    empty_seats.append((c, s, seat_type[(s-1)%all_types]))
        return render_template('info.html', tasks = tasks, date=date, src=src, dest=dest, prefered_seats = empty_seats, status=status)

    elif (request.method == 'POST'):
        name = request.form.getlist('name')
        age = request.form.getlist('age')
        gender = request.form.getlist('gender')
        email = request.form.getlist('email')
        mobile = request.form.getlist('mobile')
        seat = request.form.getlist('pref')
        seat_list = [i.split() for i in seat]
        cursor.execute(f"SELECT pnr_no FROM pnr GROUP BY pnr_no ORDER BY pnr_no DESC LIMIT 1;")
        pnr_number = cursor.fetchone()[0]
        pnr_number = str(int(pnr_number)+1)
        while len(pnr_number) < 10:
            pnr_number = "0"+pnr_number
        try:
            for i in range(len(name)):
                print(f"INSERT INTO pnr VALUES ('{pnr_number}', '{train_number}', '{date}', '{seat_list[i][0]}', {seat_list[i][1]}, '{seat_list[i][2]}', '{name[i]}', {age[i]}, '{gender[i]}', '{mobile[i]}', '{email[i]}', '{src}', '{dest}', 0);")
                cursor.execute(f"INSERT INTO pnr VALUES ('{pnr_number}', '{train_number}', '{date}', '{seat_list[i][0]}', {seat_list[i][1]}, '{seat_list[i][2]}', '{name[i]}', {age[i]}, '{gender[i]}', '{mobile[i]}', '{email[i]}', '{src}', '{dest}', 0);")
        except:
            connection.rollback()
            return redirect(f'/info/{src}/{dest}/{tasks[3]}/{tasks[5]}/{date}/error')
        connection.commit()
        vals = [k for k in zip(name, age, gender, email, mobile, seat_list)]
        print(vals)
        return render_template('print.html', vals=vals, pnr_number=pnr_number, tasks=tasks, date=date, src=src, dest=dest, status="Booked")

@app.route('/enquiry', methods=['POST', 'GET'])
def enquiry():
    if(request.method == 'GET'):
        return render_template('enquiry.html')
    elif (request.method == 'POST'):
        pnr = request.form['pnr']
        cursor.execute(f"SELECT pnr.pnr_no, pnr.name, pnr.age::varchar(10), pnr.gender, pnr.email, pnr.mobile, CONCAT(pnr.coach_no,' ',pnr.seat_no::varchar(10),' ',pnr.birth_type) AS seat, pnr.src, pnr.dest, pnr.train_number, coach.class AS train_class, pnr.date, pnr.delete AS status \
                        FROM pnr \
                        JOIN coach \
                            ON pnr.coach_no = coach.coach_name \
                        WHERE pnr.pnr_no = '{pnr}' \
                        ORDER BY pnr.name;")
        persons = cursor.fetchall()
        vals = [(person[1],person[2],person[3],person[4],person[5],person[6].split()) for person in persons]
        print(vals)
        cursor.execute(f"SELECT s1.arrival AS arrival_src, s1.departure AS dept_src, s1.train_name, s1.train_number, s2.arrival AS arrival_dest, ts.class,ts.seats_available - COALESCE(pnr.count, 0) seats, TO_DATE('{persons[0][11]}','YYYY-MM-DD') + s2.day - s1.day AS arrival_date \
            FROM schedules AS s1, \
            schedules AS s2, \
            total_seats_available AS ts \
            LEFT JOIN \
            ( \
                SELECT coach.class, PNR.train_number, count(*) FROM PNR, coach \
                WHERE DATE ='{persons[0][11]}' \
                AND coach.coach_name = PNR.coach_no \
                AND PNR.delete = 0 \
                GROUP BY coach.class, PNR.train_number \
            ) AS pnr \
            ON (pnr.train_number = ts.train_id \
                AND pnr.class = ts.class) \
            WHERE s1.station_name = '{persons[0][7]}' \
            AND s2.station_name = '{persons[0][8]}'  \
            AND s1.train_number = s2.train_number \
            AND (s2.day > s1.day OR (s2.day = s1.day AND s2.arrival >= s1.departure)) \
            AND s1.train_number = '{persons[0][9]}' \
            AND ts.train_id = s1.train_number \
            AND ts.class='{persons[0][10]}' \
            ORDER BY s1.arrival;")
        tasks = cursor.fetchone()
        print(tasks)
        status = 'Booked' if persons[0][12] == 0 else 'Cancelled'
        return render_template('print.html', vals=vals, pnr_number=persons[0][0], tasks=tasks, date=persons[0][11], src=persons[0][7], dest=persons[0][8], status=status)

@app.route('/cancel', methods=['POST', 'GET'])
def cancel():
    if(request.method == 'GET'):
        return render_template('cancel.html')
    elif (request.method == 'POST'):
        pnr = request.form['pnr']
        cursor.execute(f"UPDATE pnr SET delete = 1 WHERE pnr_no = '{pnr}';")
        connection.commit()
        cursor.execute(f"SELECT pnr.pnr_no, pnr.name, pnr.age::varchar(10), pnr.gender, pnr.email, pnr.mobile, CONCAT(pnr.coach_no,' ',pnr.seat_no::varchar(10),' ',pnr.birth_type) AS seat, pnr.src, pnr.dest, pnr.train_number, coach.class AS train_class, pnr.date, pnr.delete AS status \
                        FROM pnr \
                        JOIN coach \
                            ON pnr.coach_no = coach.coach_name \
                        WHERE pnr.pnr_no = '{pnr}' \
                        ORDER BY pnr.name;")
        persons = cursor.fetchall()
        vals = [(person[1],person[2],person[3],person[4],person[5],person[6].split()) for person in persons]
        print(vals)
        cursor.execute(f"SELECT s1.arrival AS arrival_src, s1.departure AS dept_src, s1.train_name, s1.train_number, s2.arrival AS arrival_dest, ts.class,ts.seats_available - COALESCE(pnr.count, 0) seats, TO_DATE('{persons[0][11]}','YYYY-MM-DD') + s2.day - s1.day AS arrival_date \
            FROM schedules AS s1, \
            schedules AS s2, \
            total_seats_available AS ts \
            LEFT JOIN \
            ( \
                SELECT coach.class, PNR.train_number, count(*) FROM PNR, coach \
                WHERE DATE ='{persons[0][11]}' \
                AND coach.coach_name = PNR.coach_no \
                AND PNR.delete = 0 \
                GROUP BY coach.class, PNR.train_number \
            ) AS pnr \
            ON (pnr.train_number = ts.train_id \
                AND pnr.class = ts.class) \
            WHERE s1.station_name = '{persons[0][7]}' \
            AND s2.station_name = '{persons[0][8]}'  \
            AND s1.train_number = s2.train_number \
            AND (s2.day > s1.day OR (s2.day = s1.day AND s2.arrival >= s1.departure)) \
            AND s1.train_number = '{persons[0][9]}' \
            AND ts.train_id = s1.train_number \
            AND ts.class='{persons[0][10]}' \
            ORDER BY s1.arrival;")
        tasks = cursor.fetchone()
        print(tasks)
        return render_template('print.html', vals=vals, pnr_number=persons[0][0], tasks=tasks, date=persons[0][11], src=persons[0][7], dest=persons[0][8], status="Cancelled")
        
if __name__ == "__main__":
    app.run(host="localhost", port=5040, debug=True)