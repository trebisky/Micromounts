# Makefile to fetch stuff from rails project

all:
	echo "?"

# This is not strictly needed
schema.sql:
	sqlite3 minerals.sqlite3 .schema >schema.sql

# This can be used to regenerate my database via:

backup.sql:
#	sqlite3 minerals.sqlite3 .dump >minerals.sql
	sqlite3 minerals.sqlite3 .dump >backup.sql

# If we ever need to restore the database, this will do it.
# I am taking care to not restore to the actual file "minerals.sqlite3"
# to avoid foolish and accidental overwriting of the active database.
restore:
	sqlite3 restore.db < backup.sql

gui:
	sqliteman minerals.sqlite3

# ================
# ================

# The following are things I should never need to do again,
# but serve to document how I migrated from my old rails project
rails_fetch:
	cp /u1/rails/micromounts/db/schema.rb ./rails
	cp /u1/rails/micromounts/db/migrate/*create_mounts.rb rails/create_mounts.rb
	cp /u1/rails/micromounts/db/migrate/*create_labels.rb rails/create_labels.rb

# fetch the database from the old rails project
db_rails_fetch:
	cp /u1/rails/micromounts/db/development.sqlite3 minerals.sqlite3

# verify our copy
db_rails_verify:
	cmp /u1/rails/micromounts/db/development.sqlite3 minerals.sqlite3

# ================
# ================

# The following gets Dicks database

dickt_fetch:
	cp ../Dickt/dt_2_2018.csv .

# THE END
