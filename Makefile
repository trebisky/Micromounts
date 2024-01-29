# Makefile to fetch stuff from rails project
# And to backup the database onto my flash stick
#  7-29-2023
#
# To do a backup:
#
#  1 - plug in the white/blue Lexar stick
#  2 - watch for the "Lexar" icon to appear
#  3 - double click to mount it
#  4 - type "make backup"
#  5 - when done, unmount the stick
#  6 - put the stick back in the drawer

# Note that the backup syncs the whole directory, including the .git subdirectory.

STICK = /run/media/tom/Lexar

all:
	echo "?"

backup:
	make dump
	#cp -var . $(STICK)/Backup
	rsync -auv --size-only ./ $(STICK)/Backup

# This is not strictly needed
schema.sql:
	sqlite3 minerals.sqlite3 .schema >schema.sql

# This generates a dump that could be used to regenerate
# the database.

dump:
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
