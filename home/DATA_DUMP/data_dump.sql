DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS trains;
DROP TABLE IF EXISTS stations;


CREATE TABLE stations (
	Xcoordinate decimal,
	Ycoordinate decimal,
	state text,
	code text PRIMARY KEY,
	name text,
	zone text,
	address text
);

\copy stations from 'data/stations.csv' delimiter ',' csv header;

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
	from_station_name text,
	number text PRIMARY KEY,
	departure time,
	return_train text,
	to_station_code text,
	second_ac int,
	classes text,
	to_station_name text,
	duration_h int,
	type text,
	first_ac int,
	distance int,
	constraint from_station_constraint foreign key (from_station_code) references stations(code),
	constraint to_station_constraint foreign key (to_station_code) references stations(code)
);

\copy trains from 'data/trains.csv' delimiter ',' csv header;

CREATE TABLE schedules (
	arrival time,
	day int,
	train_name text,
	station_name text,
	station_code text,
	id int PRIMARY KEY,
	train_number text,
	departure time,
	constraint train_constraint foreign key (train_number) references trains(number),
	constraint station_constraint foreign key (station_code) references stations(code)
);

\copy schedules from 'data/schedules.csv' delimiter ',' csv header;