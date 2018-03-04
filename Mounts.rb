#!/usr/bin/ruby

# Tom Trebisky 3-1-2018
#   db_read

# This is sort of a test pilot as I ponder how to
#  migrate my old micromount database out of rails.
# It is tempting to continue to use activerecord
#  outside of rails, but I have seen plenty of API
#  changes with activerecord.
# Biting the bullet and kissing activerecord goodbye
#  will probably yield great stability benefits.
# I will roll my own class that embeds any necessary SQL.

require 'sqlite3'

#$db = "minerals.sqlite3"

# This is one mount
class Mount
#    attr_accessor :myid
#    attr_accessor :species
#    attr_accessor "location"

    def Mount.setup ( index, name, type )
	stmt = "def #{name}; @data[#{index}]; end\n"
	self.class_eval stmt
	stmt = "def #{name}=(x); @data[#{index}]=x; end\n"
	self.class_eval stmt
    end

    def initialize ( db_row )
	@data = db_row
#	@myid = @data[1]
#	@species = @data[2]
#	@location = @data[4]
    end
    def show
	print "TT-#{myid} #{species}  #{location}\n"
    end
end

# We have one instance of this for all database access
class Mounts
    def initialize
# either way works
#	$db = SQLite3::Database.new( $db )
	$db = SQLite3::Database.open( $db )
#	$db.results_as_hash = true
	setup_mount
    end
    def db_version
	return $db.get_first_value 'SELECT SQLITE_VERSION()'
    end

    def setup_mount
	stm = $db.prepare "PRAGMA table_info('Mounts')"
	rs = stm.execute

	# This yields one row per database column
	rs.each { |row|
	    Mount.setup row[0], row[1], row[2]
	}
    end

    def show_pragma

# This pragma business is sqlite specific.
# It almost certainly won't exist in other databases.
# It also could change in the future.

#    PRAGMA schema.table_info(table-name);
#
#	This pragma returns one row for each column in the named table.
#	Columns in the result set include:
#		column name,
#		data type,
#		whether or not the column can be NULL,
#		and the default value for the column.
#		The "pk" column in the result set is zero for columns that are not part of the primary key,
#		and is the index of the column in the primary key for columns that are part of the primary key.
#
# What I get is an array of 6 values per column
#  [tom@trona Newdb]$ sqlite3 minerals.sqlite3
#  SQLite version 3.20.1 2017-08-24 16:21:36
#  sqlite> PRAGMA table_info('Mounts');
#  0|id|INTEGER|1||1
#  1|myid|varchar(255)|0||0
#  2|species|varchar(255)|0||0
#  3|associations|varchar(255)|0||0
#  4|location|varchar(255)|0||0
#  5|notes|text|0||0
#  6|origin|varchar(255)|0||0
#  7|source|varchar(255)|0||0
#  8|owner|varchar(255)|0||0
#  9|status|varchar(255)|0||0
# 10|label_info|varchar(255)|0||0
# 11|created_at|datetime|0||0
# 12|updated_at|datetime|0||0

# No idea what the empty second to last item is (Ruby returns a nil here).
# It doesn't really matter.  All I want is the field names and the
# corresponding data types.

# What is the difference between text and varchar(255) you ask?
# Essentially nothing.  Sqlite ignores the count and makes it the
# same as text, however text can include odd UTF characters that
# varchar will prohibit, but this does not matter to me.
# Note that this is VERY different from other databases.


	stm = $db.prepare "PRAGMA table_info('Mounts')"
	rs = stm.execute

	rs.each { |row|
	    #puts row
	    # puts row.length (6)
	    row.each { |x|
		puts x.class
	    }
	    puts row.join "\s"
	    exit
	}
    end

    def show_first
	$db.execute("select * from mounts") do |result|
	  puts result
	  $save = result
	  break
	end
    end
    def show_class
	$save.each { |x|
	    puts x.class
	}
    end
    def fetch ( id )
	row = $db.get_first_row "SELECT * FROM Mounts WHERE Id=#{id}"
	return Mount.new row
    end
    def fetch_species ( species )
	stm = $db.prepare "SELECT * FROM Mounts WHERE species like '%#{species}%'"
	rs = stm.execute

	rv = Array.new
	rs.each { |row|
	    rv << Mount.new( row )
	}
	rv
    end
    def fetch_species_count ( species )
#	row = $db.get_first_row "SELECT count(*) FROM mounts WHERE species like '%#{species}%'"
#	return row[0]
	return $db.get_first_value "SELECT count() FROM mounts WHERE species like '%#{species}%'"
    end
    def fetch_total_count
#	row = $db.get_first_row "SELECT count(*) FROM mounts"
#	return row[0]
#	return $db.get_first_value "SELECT count(*) FROM mounts"
	return $db.get_first_value "SELECT count() FROM mounts"
    end
    def get_last_row
	# always returns 0
	return $db.last_insert_row_id
    end
end

# THE END
