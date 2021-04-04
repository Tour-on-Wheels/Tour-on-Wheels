DROP VIEW IF EXISTS total_seats_available;
DROP TABLE IF EXISTS PNR;
DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS trains;
DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS coach;


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

CREATE TABLE coach (
	coach_name text primary key,
	class text not null,
	total_seats int,
	coach_type text not null
);

insert into coach values ('H1', '1AC', 24, 'Upper Lower');
insert into coach values ('H2', '1AC', 24, 'Upper Lower');
insert into coach values ('H3', '1AC', 24, 'Upper Lower');
insert into coach values ('A1', '2AC', 45, 'Upper Lower SUpper SLower');
insert into coach values ('A2', '2AC', 45, 'Upper Lower SUpper SLower');
insert into coach values ('A3', '2AC', 53, 'Upper Lower SUpper SLower');
insert into coach values ('B1', '3AC', 63, 'Upper Middle Lower SUpper SLower');
insert into coach values ('B2', '3AC', 63, 'Upper Middle Lower SUpper SLower');
insert into coach values ('B3', '3AC', 63, 'Upper Middle Lower SUpper SLower');
insert into coach values ('S1', 'SL', 71, 'Upper Middle Lower SUpper SLower');
insert into coach values ('S2', 'SL', 71, 'Upper Middle Lower SUpper SLower');
insert into coach values ('S3', 'SL', 71, 'Upper Middle Lower SUpper SLower');
insert into coach values ('C1', 'CC', 73, 'Aisle Middle Window');
insert into coach values ('C2', 'CC', 73, 'Aisle Middle Window');
insert into coach values ('C3', 'CC', 73, 'Aisle Middle Window');
insert into coach values ('E1', 'EC', 54, 'Aisle Window');
insert into coach values ('E2', 'EC', 54, 'Aisle Window');
insert into coach values ('E3', 'EC', 54, 'Aisle Window');
insert into coach values ('D1', '2S', 73, 'Aisle Middle Window');
insert into coach values ('D2', '2S', 73, 'Aisle Middle Window');
insert into coach values ('D3', '2S', 73, 'Aisle Middle Window');
insert into coach values ('F1', 'FC', 26, 'Upper Lower');
insert into coach values ('F2', 'FC', 26, 'Upper Lower');
insert into coach values ('F3', 'FC', 26, 'Upper Lower');

CREATE TABLE PNR (
	PNR_no text ,
	train_number text not null,
	date date not null,
	coach_no text not null,
	seat_no int not null,
	birth_type text not null,
	name text not null,
	age int not null,
	gender text not null,
	mobile text null,
	email text null,
	src text not null,
	dest text not null,
	delete int default 0,
	constraint train_PNR_constraint foreign key (train_number) references trains(number),
	constraint coach_PNR_constraint foreign key (coach_no) references coach(coach_name),
	constraint seat_coach_PNR_constraint primary key (train_number, date, coach_no, seat_no)
);

insert into PNR values ('0000000000', '12547', '2020-01-01', '2S', 0, 0, '0', 0, '0', '0', '0', '0', '0', 1);

CREATE VIEW total_seats_available AS
SELECT trains.number as train_id, coach.class as class, SUM(coach.total_seats) as seats_available
FROM trains, coach
WHERE coach.class = '2S' 
OR (coach.class = '1AC' AND trains.first_ac = 1)
OR (coach.class = '2AC' AND trains.second_ac = 1)
OR (coach.class = '3AC' AND trains.third_ac = 1)
OR (coach.class = 'SL' AND trains.sleeper = 1)
OR (coach.class = 'FC' AND trains.first_class = 1)
OR (coach.class IN ('CC', 'EC') AND trains.chair_car = 1)
GROUP BY trains.number, coach.class;