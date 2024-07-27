#!/bin/python3

# Micros.py
# database access for the micromount database

# Tom Trebisky  7-25-2024

import os
import sqlite3

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
def to_hash ( mount ) :
        hash = {}
        hash['id'] = mount[0]
        hash['myid'] = mount[1]
        hash['species'] = mount[2]
        hash['associations'] = mount[3]
        hash['location'] = mount[4]
        hash['notes'] = mount[5]
        hash['origin'] = mount[6]
        hash['source'] = mount[7]
        hash['owner'] = mount[8]
        hash['status'] = mount[9]
        hash['label_info'] = mount[10]
        hash['created_at'] = mount[11]
        hash['updated_at'] = mount[12]
        return hash

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
        self.rows = []

        self.mypath = Micros.grog_path ()
        print ( "Running from: ", self.mypath )

        db_path = self.mypath + "/" + "minerals.sqlite3"

        print ( "Database: ", db_path )

        try:
            self.conn = sqlite3.connect ( db_path )
        except OSError as e:
            print(e)

        self.__get_all ()
        print ( f"{len(self.rows)} entries in database"  )

    def __get_all ( self ) :
        cur = self.conn.cursor ()
        cur.execute ( "SELECT * from mounts" )
        self.rows = cur.fetchall ()
        cur.close ()

    def all ( self ) :
        return self.rows

    # A one time check.
    # look for duplicate values among myid
    def validate ( self ) :
        for x in self.rows :
            count = 0
            for y in self.rows :
                if x[1] == y[1] :
                    count += 1
                    if count > 1 :
                        print ( "Dup: ", x[1] )
                        print ( x )
                        print ( y )

    # Someday this may do more that __get_all()
    def refresh ( self ) :
        self.__get_all ()

    # The idea here is to find out where this script is running
    # in order to generate an absolute path to find the database
    # as well as other resources
    # This currently gives me:
    # /u1/Minerals/Micromounts/python/labels
    @classmethod
    def grog_path ( cls ) :
        my_path = os.path.realpath ( __file__ )
        (path, file) = os.path.split ( my_path )
        print ( path )
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

        for r in result :
            print ( r )

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
        for r in self.rows :
            print ( r )

    # return data array for id
    def lookup ( self, id ) :
        n = len ( self.rows )
        for i in range(n) :
            if self.rows[i][1] == id :
                return self.rows[i]
        return None

    def get_hash ( self, id ) :
        m = self.lookup ( id )
        if m == None :
            return None
        return to_hash ( m )

    # return index for id (internal only -- private)
    def lookup_i ( self, id ) :
        n = len ( self.rows )
        for i in range(n) :
            if self.rows[i][m_MYID] == id :
                #print ( "found: ", self.rows[i] )
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
        labels = self.rows[i:stop]
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
        rv.extend ( self.rows[i+1:i+nadd] )
        return rv

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
            print(er.sqlite_errorcode)
            print(er.sqlite_errorname)

        cur.close ()
        self.conn.commit ()

        self.refresh ()

        print ( "Update done" )

# THE END
