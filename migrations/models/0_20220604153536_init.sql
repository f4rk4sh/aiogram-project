-- upgrade --
CREATE TABLE IF NOT EXISTS "customer" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "chat_id" BIGINT  UNIQUE,
    "name" VARCHAR(100) NOT NULL,
    "phone" VARCHAR(13) NOT NULL
);
CREATE TABLE IF NOT EXISTS "master" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "chat_id" BIGINT NOT NULL UNIQUE,
    "name" VARCHAR(100) NOT NULL,
    "phone" VARCHAR(13) NOT NULL,
    "info" VARCHAR(200) NOT NULL,
    "photo_id" VARCHAR(200),
    "is_active" BOOL NOT NULL  DEFAULT True
);
CREATE TABLE IF NOT EXISTS "portfoliophoto" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "photo_id" VARCHAR(200) NOT NULL,
    "master_id" INT NOT NULL REFERENCES "master" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "timeslot" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "date" DATE,
    "time" TIMETZ,
    "datetime" TIMESTAMPTZ,
    "customer_id" INT REFERENCES "customer" ("id") ON DELETE CASCADE,
    "master_id" INT NOT NULL REFERENCES "master" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_timeslot_date_e08cce" UNIQUE ("date", "time", "master_id"),
    CONSTRAINT "uid_timeslot_date_b5a8fd" UNIQUE ("date", "time", "customer_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
