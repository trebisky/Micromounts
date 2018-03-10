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

# Mount.setup 0 id INTEGER
# Mount.setup 1 myid varchar(255)
# Mount.setup 2 species varchar(255)
# Mount.setup 3 associations varchar(255)
# Mount.setup 4 location varchar(255)
# Mount.setup 5 notes text
# Mount.setup 6 origin varchar(255)
# Mount.setup 7 source varchar(255)
# Mount.setup 8 owner varchar(255)
# Mount.setup 9 status varchar(255)
# Mount.setup 10 label_info varchar(255)
# Mount.setup 11 created_at datetime
# Mount.setup 12 updated_at datetime

# At this point label_info is bogus and is never used.

require 'sqlite3'

#$db = "minerals.sqlite3"

# This is one mount
class Mount

    @@num_cols = nil

    # Called for each row when the database is initialized
    # at this point, I am ignoring type.
    # everything is saved as a string.
    # Except "id", which is an autoincrement field.
    def Mount.setup ( index, name, type )
	stmt = "def #{name}; @data[#{index}]; end\n"
	self.class_eval stmt
	stmt = "def #{name}=(x); @data[#{index}]=x; end\n"
	self.class_eval stmt
	#puts "Mount.setup #{index} #{name} #{type}"
	# Assuming here that we get called with the
	# rows in order, so the last is the largest.
	@@num_cols = index + 1
    end

    # This gets called when we read a row from
    # the database
    def initialize ( db_row )
	@data = db_row
    end

    # Read accessor
    def data
	@data
    end

    def mk_id ( njust=10 )
	if njust == nil
	    "TT-#{myid}"
	else
	    "TT-#{myid}".ljust njust
	end
    end

    def mk_desc ( nfill=nil )
	sp = species.sub /^\s*/, ""
	sp = species.sub /\s*$/, ""
#	puts sp
	as = associations.sub /^\s*/, ""
	as = associations.sub /\s*$/, ""
#	puts as
	loc = location.sub /^\s*/, ""
	loc = location.sub /\s*$/, ""
#	puts loc
#	exit
	if ( as != "" )
	    sp += ", " + as
	end

	rv = sp.ljust 40
	if nfill
	    rv += " #{loc}".ljust nfill
	    rv += "_"
	else
	    rv += " #{loc}"
	end
	rv
    end

    def mk_line
	rv = mk_id 11
	rv += " "
	rv += mk_desc
	rv
    end
    def show
#	print "TT-#{myid} #{species}  #{location}\n"
	print mk_line + "\n"
    end
end

# We have one instance of this for all database access
class Mounts
    def initialize
# either way works
#	$db = SQLite3::Database.new( $db )
	$db = SQLite3::Database.open( $db )
#	$db.results_as_hash = true
	@limit = 25

	setup_mount
    end
    def set_limit ( n )
	@limit = n
    end

    def db_version
	return $db.get_first_value 'SELECT SQLITE_VERSION()'
    end

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

    def show_pragma
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

    # called once during initialization
    def setup_mount
	stm = $db.prepare "PRAGMA table_info('Mounts')"
	rs = stm.execute

	# This yields one row per database column
	# we have index, name, and type
	# index runs from 0 to 12 currently
	@names = Array.new
	rs.each { |row|
	    Mount.setup row[0], row[1], row[2]
	    @names[row[0].to_i] = row[1]
	}
	@num_cols = @names.size

	# generate comma delimited list for insert
	# omit first item (autoincrement ID) and
	# the last two (timestamps)
	@ins_cols = @num_cols - 3
	@ins_names = @names[1,@ins_cols].join(",")
	@ins_markers = Array.new(@ins_cols,"?").join(",")
    end

    # we avoid the first item in the data array (the autoincrement ID)
    # and the last two (we set them to the current timestamp)
    # XXX danger here if schema changes
    def insert ( m )
	data = m.data
	names = @ins_names
	names += ",created_at"
	names += ",updated_at"
	marks = @ins_markers
	marks += ",CURRENT_TIMESTAMP"
	marks += ",CURRENT_TIMESTAMP"
	sql = "INSERT INTO mounts(#{names}) VALUES (#{marks})"

	puts sql
	$db.execute sql, data[1,@ins_cols]
    end

    # update an existing record.
    # we always leave the ID alone
    # We also leave the next to last timestamp alone (created_at)
    # We do want to update the updated_at timestamp to the current time
    #
    # There is a whole nuther API for this, like:
    #  stm = db.prepare "UPDATE mounts SET species=? WHERE ID=?"
    #  stm.bind_param 1, $species
    #  stm.bind_param 2, $key
    #  stm.execute
    #  stm.close

    def update ( m )
	data = m.data
	sql = "UPDATE mounts SET "

	last = @ins_cols + 1
	(1..last).each { |col|
	    name = @names[col]
	    val = data[col]
	    sql += "#{name}='#{val}',"
	}
	sql += "updated_at=CURRENT_TIMESTAMP "
	sql += "WHERE id=#{m.id.to_s}"
	puts sql
	$db.execute sql
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

    # Fetch a single record given the id
    def fetch ( id )
	row = $db.get_first_row "SELECT * FROM Mounts WHERE Id=#{id}"
	return Mount.new row
    end

    def fetch_last
	row = $db.get_first_row "SELECT * FROM mounts ORDER BY id DESC LIMIT 1"
	return Mount.new row
    end

    # Fetch a batch of rows given a starting id
    def fetch_all ( id )
	cmd = "SELECT * FROM Mounts LIMIT #{@limit} OFFSET #{id-1}"
	# puts cmd
	stm = $db.prepare cmd
	rs = stm.execute

	rv = Array.new
	rs.each { |row|
	    rv << Mount.new( row )
	}
	rv
    end

    # New unified search code.
    def mk_sql ( species, loc, ass )
	# everything - we refuse this because this would
	# yield an array the size of the database.
	# This works perfectly.  The search fails and the
	# display falls back to browsing the whole database.
	if ( loc == "" and species == "" )
	    return nil
	end
	if ( loc == "" )
	    if ass
		return "FROM mounts WHERE species like '%#{species}%' OR associations LIKE '%#{species}%'"
	    else
		return "FROM mounts WHERE species like '%#{species}%'"
	    end
	end
	if ( species == "" )
	    return "FROM mounts WHERE location like '%#{loc}%'"
	end
	# both location and species
	if ass
	    return "FROM mounts WHERE (species like '%#{species}%' OR associations LIKE '%#{species}%') AND location like '%#{loc}%'"
	else
	    return "FROM mounts WHERE species like '%#{species}%' AND location like '%#{loc}%'"
	end
    end

    def fetch_mounts ( sql )
	stm = $db.prepare sql
	rs = stm.execute

	rv = Array.new
	rs.each { |row|
	    rv << Mount.new( row )
	}
	rv
    end

    def fetch_u_count ( species, loc, ass )
	sql = mk_sql species, loc, ass
	if ( sql == nil )
	    return 0
	else
	    return $db.get_first_value "SELECT count() " + sql
	end
    end

    def fetch_u ( species, loc, ass )
	sql = mk_sql species, loc, ass
	if ( sql == nil )
	    return Array.new
	else
	    return fetch_mounts "SELECT * " + sql
	end
    end

    def fetch_total_count
#	row = $db.get_first_row "SELECT count() FROM mounts"
#	return row[0]
	return $db.get_first_value "SELECT count() FROM mounts"
    end

    # I never use this
    def get_last_row
	# always returns 0
	return $db.last_insert_row_id
    end

    # generate the next TT number for a new insert
    def mk_next_id
	lastid = fetch_last.myid
	nn = lastid.split "-"
	ly = nn[0].to_i
	ln = nn[1].to_i
	cyear = Time.now.year.to_i - 2000
	ycode = "%02d" % cyear
	if ly == cyear
	    ncode = (ln+1).to_s
	else
	    ncode = "1"
	end
	return ycode + "-" + ncode
    end

    # Called to create a new empty mount
    # that we can fill in, then insert.
    def alloc
	# XXX generate new TT number here.
	init = Array.new( @num_cols, "" )
	nu = Mount.new( init )
	nu.myid = mk_next_id
	nu.owner = "TT"
	nu.status = "ok"
	nu.origin = "bought"
	nu.label_info = ""	# never used.
	return nu
    end

    def clone orig
	m_new = alloc

	m_new.species = orig.species
	m_new.associations = orig.associations
	m_new.location = orig.location

	m_new.notes = orig.notes
	m_new.origin = orig.origin
	m_new.source = orig.source
	m_new.owner = orig.owner
	m_new.status = orig.status

	insert m_new
    end

end

# THE END
