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

