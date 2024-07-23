#!/bin/python3

import sqlite3

##micro_db = "minerals.sqlite3"

class Micros :
    def __init__ ( self, path ) :
        self.conn = None
        self.rows = []
        try:
            self.conn = sqlite3.connect ( path )
        except Error as e:
            print(e)

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

    def get_all ( self ) :
        cur = self.conn.cursor ()
        cur.execute ( "SELECT * from mounts" )
        self.rows = cur.fetchall ()
        cur.close ()

        print ( f"{len(self.rows)} entries in database"  )

    def show_all ( self ) :
        for r in self.rows :
            print ( r )

    def lookup ( self, id ) :
        n = len ( self.rows )
        for i in range(n) :
            if self.rows[i][1] == id :
                return self.rows[i]
        return None

    def lookup_i ( self, id ) :
        n = len ( self.rows )
        for i in range(n) :
            if self.rows[i][1] == id :
                #print ( "found: ", self.rows[i] )
                return i
        return None

    def mk_label ( self, id, num ) :
        i = self.lookup_i ( id )
        if i == None :
            return None
        #print ( "index: ", i )
        stop = i+num
        labels = self.rows[i:stop]
        #for l in labels :
        #    print ( l )
        return labels

# m = Micros ( micro_db )
# m.tables ()
# m.schema ( "mounts" )
# m.get_id ( "08-1" )
# m.get_id ( "22-100" )
# m.get_all ()
# #m.show_all ()
# m.mk_label ( "08-110" )
# m.close ()

# THE END
