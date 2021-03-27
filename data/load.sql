DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS stations;

CREATE TABLE schedules (
	arrival time,
	day int,
	train_name text,
	station_name text,
	station_code text,
	id int PRIMARY KEY,
	train_number text,
	departure time
);

\copy schedules from '/home/manoj/Desktop/sem_6/COL362-dbms/project/project/data/schedules.csv' delimiter ',' csv header;

CREATE TABLE stations (
	Xcoordinate decimal,
	Ycoordinate decimal,
	state text,
	code text PRIMARY KEY,
	name text,
	zone text,
	address text
);

\copy stations from '/home/manoj/Desktop/sem_6/COL362-dbms/project/project/data/stations.csv' delimiter ',' csv header;

CREATE TABLE trains (
	third_ac int,
	arrival time,
	from_station_code text,
	name text,
	zone text,
	chair_car int,
	first_class int,
	duration_m int,
	sleeper int,
	from_station_name yext,
	number int PRIMARY KEY,
	departure time,
	return_train int,
	to_station_code text,
	second_ac int,
	classes text,
	to_station_name text,
	duration_h int,
	type text,
	first_ac int,
	distance int
);

\copy stations from '/home/manoj/Desktop/sem_6/COL362-dbms/project/project/data/trains.csv' delimiter ',' csv header;