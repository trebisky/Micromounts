#!/bin/python3

# Micros.py
# database access for the micromount database

# Tom Trebisky  7-25-2024

import os
import sqlite3
import datetime

##micro_db = "minerals.sqlite3"

# I am double minded.  We could always convert to a hash and
# reference fields by name in that way, or we can leave the row
# data in a tuple and use these indices.
#
# Never mind what they say, the only sane way to deal with this is
# to use "from Micros import *" in each file that needs this.
# I have no remorse.  I am the only one who will use this, AND
# there is a small and well known set of items that will get
# imported.
m_ID = 0
m_MYID = 1
m_SPECIES = 2
m_ASSOCIATIONS = 3
m_ASS = 3
m_LOCATION = 4
m_LOC = 4
m_NOTES = 5
m_ORIGIN = 6
m_SOURCE = 7
m_OWNER = 8
m_STATUS = 9
m_LABEL = 10
m_CREATED = 11
m_UPDATED = 12

# Convert array to hash.
# A more general way would use the schema for this.
#def to_hash ( mount ) :
#        hash = {}
#        hash['id'] = mount[0]
#        hash['myid'] = mount[1]
#        hash['species'] = mount[2]
#        hash['associations'] = mount[3]
#        hash['location'] = mount[4]
#        hash['notes'] = mount[5]
#        hash['origin'] = mount[6]
#        hash['source'] = mount[7]
#        hash['owner'] = mount[8]
#        hash['status'] = mount[9]
#        hash['label_info'] = mount[10]
#        hash['created_at'] = mount[11]
#        hash['updated_at'] = mount[12]
#        return hash

# We now simplify things by fetching all database records into memory
# when this class initializes.  All requests will be served from this
# list in memory.  This is certainly no problem whatsoever with 1300
# records, and it is hard to imagine it will be a problem even with 10,000
#
# This does require some care to refresh this list when records are
# inserted or updated.

class Micros :
    def __init__ ( self ) :
        self.conn = None
        self.data = []

        self.mypath = Micros.grog_path ()
        #print ( "Running from: ", self.mypath )

        db_path = self.mypath + "/" + "minerals.sqlite3"

        print ( "Database: ", db_path )

        # Prototype for every new mount
        # We now set "TT" always for the owner,
        # but the database has many records where
        # we have "" (40 of them) or None (137 of them).
        # This should get fixed someday.
        # currently this field is unused, but it might
        # someday be used to denote subcollections
        self.proto = [
            None,
            "",
            "new",      # species
            '',
            "somewhere",
            "",
            "collected",
            "",
            "TT",
            "ok"
            "",
            None,
            None ]

        try:
            self.conn = sqlite3.connect ( db_path )
        except OSError as e:
            print(e)

        self.__get_tags ()
        self.__get_all ()
        #print ( f"{len(self.data)} entries in database"  )

        # Handy place to call this for debugging
        # x = self.__gen_myid ()
        # print ( "Next myid = ", x )

    # Generate next ID number for clone or new insert
    def __gen_myid ( self ) :
        last = self.data[-1]
        last_id = last[m_MYID]
        (year,index) = last_id.split ( '-' )
        #print ( "last: ", year, index )

        today = datetime.datetime.now()
        #print ( today.year )
        #print ( today.year - 2000 )
        cur_year = str ( today.year - 2000 )
        if year != cur_year :
            return f'{cur_year}-1'
        else :
            return f'{year}-{int(index)+1}'

    # Return the names for fields in a database record.
    # This can be indexed by m_ID and such as per the
    # definitions at the start of this file
    def get_tags ( self ) :
        return self.tags

    def __get_tags ( self ) :
        schema = self.schema ( 'mounts' )
        rv = []
        for s in schema :
            rv.append ( s[1] )
        self.tags = rv

    def __get_all ( self ) :
        cur = self.conn.cursor ()
        cur.execute ( "SELECT * from mounts" )
        self.data = cur.fetchall ()
        cur.close ()

    # We call this after an insert or update,
    # so it needs to reread the database.
    def all ( self ) :
        self.__get_all ()
        return self.data

    # A one time check.
    # look for duplicate values among myid
    def validate ( self ) :
        for x in self.data :
            count = 0
            for y in self.data :
                if x[1] == y[1] :
                    count += 1
                    if count > 1 :
                        print ( "Dup: ", x[1] )
                        print ( x )
                        print ( y )

    # Someday this may do more that __get_all()
    # We call this after every update or insert
    #def refresh ( self ) :
    #    self.__get_all ()

    # The idea here is to find out where this script is running
    # in order to generate an absolute path to find the database
    # as well as other resources
    # This currently gives me:
    # /u1/Minerals/Micromounts/python/labels
    @classmethod
    def grog_path ( cls ) :
        my_path = os.path.realpath ( __file__ )
        (path, file) = os.path.split ( my_path )
        #print ( path )
        return path


    def close ( self ) :
        self.conn.close ()

    # tables gives:
    # ('schema_migrations',)
    # ('mounts',)
    # ('sqlite_sequence',)
    # ('labels',)

    def tables ( self ) :
        cur = self.conn.cursor ()
        cmd = "SELECT name FROM sqlite_master WHERE type='table';"
        cur.execute ( cmd )
        tables = cur.fetchall ()
        cur.close ()

        for t in tables :
            print ( t )

    # schema gives:
    # (0, 'id', 'INTEGER', 1, None, 1)
    # (1, 'myid', 'varchar(255)', 0, None, 0)
    # (2, 'species', 'varchar(255)', 0, None, 0)
    # (3, 'associations', 'varchar(255)', 0, None, 0)
    # (4, 'location', 'varchar(255)', 0, None, 0)
    # (5, 'notes', 'TEXT', 0, None, 0)
    # (6, 'origin', 'varchar(255)', 0, None, 0)
    # (7, 'source', 'varchar(255)', 0, None, 0)
    # (8, 'owner', 'varchar(255)', 0, None, 0)
    # (9, 'status', 'varchar(255)', 0, None, 0)
    # (10, 'label_info', 'varchar(255)', 0, None, 0)
    # (11, 'created_at', 'datetime', 0, None, 0)
    # (12, 'updated_at', 'datetime', 0, None, 0)

    def schema ( self, table_name ) :
        cur = self.conn.cursor ()
        result = cur.execute ( "PRAGMA table_info('%s')" % table_name).fetchall()
        cur.close ()
        return result

        #for r in result :
        #    print ( r )

    def get_id ( self, id ) :
        cmd = f"SELECT * from mounts WHERE myid='{id}'"
        print ( cmd )
        cur = self.conn.cursor ()
        cur.execute ( cmd )
        row = cur.fetchone()
        cur.close ()

        #cursor.fetchone()[0]
        print ( row )


    def show_all ( self ) :
        for r in self.data :
            print ( r )

    # return data array for id
    def lookup ( self, id ) :
        n = len ( self.data )
        for i in range(n) :
            if self.data[i][1] == id :
                return self.data[i]
        return None

#    def get_hash ( self, id ) :
#        m = self.lookup ( id )
#        if m == None :
#            return None
#        return to_hash ( m )

    # return index for id (internal only -- private)
    def lookup_i ( self, id ) :
        n = len ( self.data )
        for i in range(n) :
            if self.data[i][m_MYID] == id :
                #print ( "found: ", self.data[i] )
                return i
        return None

    # Original version -- fill sheet with labels
    # starting with the given id
    def mk_label_OLD ( self, id, num ) :
        i = self.lookup_i ( id )
        if i == None :
            return None
        #print ( "index: ", i )
        stop = i+num
        labels = self.data[i:stop]
        #for l in labels :
        #    print ( l )
        return labels

    # return a list of "records" that will fill a sheet
    # The list given will start things off,
    # then we fill from the last entry.
    def mk_label ( self, id_list, num ) :
        rv = []
        for id in id_list :
            x = self.lookup ( id )
            #print ( id, x )
            if x != None :
                rv.append ( x )

        if len(rv) == 0 :
            return None

        # get myid of last item added above
        last_id = rv[-1][1]
        i = self.lookup_i ( last_id )
        nadd = num - len(rv) + 1
        rv.extend ( self.data[i+1:i+nadd] )
        return rv

    def update_one ( self, id, name, val ) :
        cmd = "UPDATE mounts SET "
        cmd += f"{name}='{val}',"
        cmd += "updated_at=CURRENT_TIMESTAMP "
        cmd += f"WHERE id={id}"

        print ( cmd )
        cur = self.conn.cursor ()

        try:
            cur.execute ( cmd )
        except sqlite3.Error as er:
            print ( "Update One gave SQL error" )
            print(er.sqlite_errorcode)
            print(er.sqlite_errorname)

        cur.close ()
        self.conn.commit ()

        # Caller will use "all() to reread data
        #self.refresh ()

        print ( "Update ONE done" )

    def update ( self, id, update_hash ) :
        cmd = "UPDATE mounts SET "
        for (name,val) in update_hash.items() :
            cmd += f"{name}='{val}',"
        cmd += "updated_at=CURRENT_TIMESTAMP "
        cmd += f"WHERE id={id}"

        print ( cmd )

        cur = self.conn.cursor ()

        try:
            cur.execute ( cmd )
        except sqlite3.Error as er:
            print ( "Update gave SQL error" )
            print(er.sqlite_errorcode)
            print(er.sqlite_errorname)

        cur.close ()
        self.conn.commit ()

        # Caller will use "all() to reread data
        #self.refresh ()

        print ( "Update done" )

    # Add an entirely new record
    def mk_new ( self ) :
        self.insert ( self.proto )

    # Ruby
    # everything is saved as a string.
    # Except "id", which is an autoincrement field.
    #
    # @ins_cols = @num_cols - 3
    # @ins_names = @names[1,@ins_cols].join(",")
    # @ins_markers = Array.new(@ins_cols,"?").join(",")

    def insert ( self, new ) :
        # The -3 skips "id" and the two "_at" timestamps
        nin = len ( self.tags ) - 3
        stuff1 = ",".join ( self.tags[1:] )
        print ( "INSERT: ", stuff1 )
        stuff2 = ",".join ( ["?"]*nin )
        stuff2 += ",CURRENT_TIMESTAMP"
        stuff2 += ",CURRENT_TIMESTAMP"

        print ( "INSERT: ", stuff2 )

        # SQL will look sorta like this:
        # INSERT INTO projects(name,species,loc) VALUES(?,?,?)
        cmd = f"INSERT into mounts({stuff1}) VALUES ({stuff2})"
        print ( "INSERT: ", cmd )

        # skip db-id and the last two "_at" timestamps
        values = list ( new[1:1+nin] )
        print ( "VALUES: ", values )
        print ( len ( values ) )

        # Generate new my_id
        values[0] = self.__gen_myid ()

        if len(values) != nin :
            print ( "Values broken" )
            exit ()

        cur = self.conn.cursor ()

        try:
            cur.execute ( cmd, values )
        except sqlite3.Error as er:
            print ( "Insert gave SQL error" )
            print(er.sqlite_errorcode)
            print(er.sqlite_errorname)

        cur.close ()
        self.conn.commit ()

        print ( "Insert done" )

# THE END
