CREATE TABLE IF NOT EXISTS "schema_migrations" ("version" varchar(255) NOT NULL);
CREATE TABLE IF NOT EXISTS "mounts" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "myid" varchar(255), "species" varchar(255), "associations" varchar(255), "location" varchar(255), "notes" text, "origin" varchar(255), "source" varchar(255), "owner" varchar(255), "status" varchar(255), "label_info" varchar(255), "created_at" datetime, "updated_at" datetime);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "labels" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "mount_id" integer, "created_at" datetime, "updated_at" datetime);
CREATE UNIQUE INDEX "unique_schema_migrations" ON "schema_migrations" ("version");
