CREATE TABLE urls (
	nick	text,
	url	text PRIMARY KEY,
	time	bigint,
	count	int DEFAULT 0
);

CREATE TABLE whitelist (
	url	text PRIMARY KEY
);

CREATE TABLE lastseen (
	nick	text,
	time	bigint,
	count	int DEFAULT 0
);

CREATE TABLE reminders (
	sender  text,
	nick	text,
	time	bigint,
	msg     text
);

CREATE TABLE karma (
	name	text,
	karma	bigint
);
