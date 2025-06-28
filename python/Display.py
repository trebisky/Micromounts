#!/bin/python3

# micros
#
# Tom Trebisky  7-25-2024
# 
# Here it is!  My micromount database GUI written
# in Python using wxWidgets

import wx
import re

from Micros import *
from Text import *
from Labels import *

# =========================

class Display ( wx.Panel ) :

        def __init__ ( self, parent, db, n_lines ):
            wx.Panel.__init__ ( self, parent )

            self.preview = None
            self.labelmaker = Labelsheet ()

            self.db = db
            self.n_lines = n_lines

            # Refresh will redo this, but we need
            # this early
            self.data = self.db.all ()
            self.n_data = len ( self.data )

            ## Now handled by refresh
            ##self.show_search = False
            ##self.search_data = []
            ##self.n_search = 0
            ##self.cur_search = None

            s = wx.BoxSizer ( wx.VERTICAL )
            self.SetSizer ( s )

            n = self.__build_nav ()
            s.Add ( n, 0, wx.EXPAND )
            d = self.__setup_display ()
            s.Add ( d, 0, wx.EXPAND )

            #self.__load_display ( 0 )
            #self.__load_display ( 1270 )
            self.SHOW_END = 99999999

            #self.__load_display ( self.n_data - self.n_lines )
            #self.__load_display ( self.SHOW_END )
            self.refresh ( False )

        # lookup and return entry
        def __lookup_id ( self, my_id ) :
            for m in self.data :
                if m[m_MYID] == my_id :
                    return m
            return None

        # lookup and return index of entry
        def __lookup_I ( self, my_id ) :
            for i in range(len(self.data)) :
                if self.data[i][m_MYID] == my_id :
                    return i
            return None

        def onNav ( self, event ) :
            obj = event.GetEventObject()
            action = obj.GetLabel()
            #print ( "NAV button was pushed for: ", action )

            if action == "Next" :
                if self.show_search :
                    start = self.cur_search + self.n_lines
                    if start < self.n_search :
                        self.__load_display ( start )
                else :
                    start = self.cur + self.n_lines
                    if start < self.n_data :
                        self.__load_display ( start )
                return
            if action == "Prev" :
                if self.show_search :
                    start = self.cur_search - self.n_lines
                else :
                    start = self.cur - self.n_lines
                if start >= 0 :
                    self.__load_display ( start )
                return
            if action == "Start" :
                self.__load_display ( 0 )
                return
            if action == "New" :
                self.db.mk_new ()
                self.refresh ( False )
                index = len(self.data)-1
                edit = Edit_Frame ( self, self, self.data, index, self.db, self.labelmaker )
                edit.Show ( True )
                return
            if action == "End" :
                if self.show_search :
                    start = self.n_search - self.n_lines
                else :
                    # Hack, but we need both here
                    start = self.SHOW_END
                    self.cur = self.SHOW_END
                if start < 0 :
                    start = 0
                self.__load_display ( start )
                return
            if action == "Find" :
                xx = self.find.GetValue()
                #print ( "Look for: ", xx )
                ii = self.__lookup_I ( xx )
                if ii == None :
                    print ( xx, " not found" )
                    return
                self.__load_display ( ii )
                return
            if action == "Search" :
                search = Search_Frame ( self, self.db )
                search.Show ( True )
                return
            # This is a toggle
            # XXX - we also want to change button color
            if action == "All" :
                if self.show_search :
                    self.__show_search ( False )
                    self.__load_display ( self.cur )
                else :
                    if self.n_search > 0 :
                        self.__show_search ( True )
                        self.__load_display ( self.cur_search )
                return

        # Build an H-panel full of navigation controls
        def __build_nav ( self ) :
            pan = wx.Panel ( self, -1 )
            #ms.Add ( pan, 1, wx.EXPAND )
            sz = wx.BoxSizer ( wx.HORIZONTAL )
            pan.SetSizer ( sz )

            b = wx.Button ( pan, wx.ID_ANY, "Start")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "Prev")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "Next")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "End")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            sz.AddSpacer(20)

            b = wx.Button ( pan, wx.ID_ANY, "New")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            sz.AddSpacer(20)

            # Size is in pixels, not characters
            self.find = wx.TextCtrl ( pan, size=(100, -1))
            sz.Add ( self.find, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "Find")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            sz.AddSpacer(20)

            b = wx.Button ( pan, wx.ID_ANY, "Search")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "All")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )
            self.all_button = b

            sz.AddStretchSpacer()

            msg = f"{self.n_data} mounts"
            self.status = EZtext ( pan, sz, msg )

            return pan

        # May also watch for words like "in" and "with"
        def __check_with_assoc ( self, m, what ) :
            if what == self.__tidy ( m[m_SPECIES] ) :
                return True

            if what.casefold() in m[m_ASS].casefold() :
                return True

            # The idea here is to avoid some false matches
            # by splitting into exact species names,
            # but there are many complications, such as the
            # words "in" and "width" and quoted slang names.
            # so just using the above and allowing a few false
            # matches is the best thing.
            #
            # ass_list = re.split ( r',\s*', m[m_ASS] )
            # print ( ass_list )
            # for a in ass_list :
            #     if what == a :
            #         return True
            return False

        # This centralizes transitions and allows
        # the button color to be changed.
        def __show_search ( self, val ) :
            self.show_search = val
            if val == True :
                yellow = wx.Colour ( 255, 255, 33 )
                self.all_button.SetBackgroundColour ( yellow )
            else :
                white = wx.Colour ( 255, 255, 255 )
                self.all_button.SetBackgroundColour ( white )

        # Handle the callback from the Search dialog
        # This keeps the full dataset and the search results
        # both here in this Display object
        #
        # Our species field is cluttered with whitespace,
        # so we do a substring test.  Alternately we
        # could call "__tidy()" to trim all the whitespace
        # The latter avoids some bogus matches
        # TODO -- Handle associations
        def do_search ( self, species, assoc, loc, what ) :
            self.search_data = []
            if species :
                what = what.capitalize ()
                #print ( "Searching for sp ", what )
                if assoc :
                    for m in self.data :
                        if self.__check_with_assoc ( m, what ) :
                            self.search_data.append ( m )
                else :
                    for m in self.data :
                        if what == self.__tidy ( m[m_SPECIES] ) :
                            self.search_data.append ( m )
            else:
                #print ( "Searching for loc ", what )
                for m in self.data :
                    #if what in m[m_LOC] :
                    # The following makes things case invariant
                    if what.casefold() in m[m_LOC].casefold() :
                        self.search_data.append ( m )

            self.n_search = len ( self.search_data )
            #print ( "Found ", self.n_search, " items" )
            # XXX this may be confusing -- if the search fails,
            # we just go back to the full display
            # But, we do show match count on main display
            # This string gets trucated if too long.
            stat = f"{self.n_search} of {self.n_data}"
            self.status.SetLabel ( stat )
            if self.n_search > 0 :
                self.__show_search ( True )
                self.__load_display ( 0 )
            else :
                self.__show_search ( False )
                self.__load_display ( self.cur )
            return

        # This gets called on startup,
        # and whenever we do an insert or update
        def refresh ( self, is_update ) :
            self.data = self.db.all ()
            self.n_data = len ( self.data )

            msg = f"{self.n_data} mounts"
            self.status.SetLabel ( msg )

            if not is_update :
                self.cur = self.SHOW_END

            # abandon any search results
            self.search_data = []
            self.n_search = 0
            self.cur_search = None

            self.__show_search ( False )
            self.__load_display ( self.cur )

        def __load_display ( self, start ) :

            # Clear it all out -- usually not needed,
            #  but this guarantees a clean slate
            for ll in self.labels :
                ll.SetLabel ( "" )
            for bb in self.buttons :
                bb.SetLabel ( "--" )

            if self.show_search :
                self.cur_search = start
                end = start + self.n_lines
                slice = self.search_data[start:end]
            else :
                if self.cur == self.SHOW_END :
                    start = self.n_data - self.n_lines
                # This works fine at the end of data when the
                # slice has less than n_lines
                self.cur = start
                end = start + self.n_lines
                slice = self.data[start:end]

            ii = 0
            for m in slice :
                label = self.__mk_desc ( m )
                self.labels[ii].SetLabel ( label )
                self.buttons[ii].SetLabel ( m[m_MYID] )
                fancy = wx.Colour ( "white" )
                if m[m_STATUS] != "ok" :
                    fancy = wx.Colour ( "pink" )
                if m[m_COLLECTION] != "main" :
                    # fancy = wx.RED
                    # fancy = wx.Colour("light coral")
                    fancy = wx.Colour ( "light blue" )
                self.labels[ii].SetBGColour ( fancy )
                ii += 1

        def Pop_micro ( self, my_id ) :
            index = self.__lookup_I ( my_id )
            if index == None :
                return
            # or, we could keep the existing frame and just
            # change the contents (and hide it as needed)
            if self.preview :
                #self.preview.Destroy ()
                self.preview.Close ()

            self.preview = Preview_Frame ( self, self.data, index, self.db, self.labelmaker )
            self.preview.Show ( True )

        # The "dir" function shows all methods available
        # for an object.
        def onButton ( self, event ) :
            #print ( event )
            #print ( dir(event) )
            obj = event.GetEventObject()
            #print ( obj )
            #print ( dir(obj) )
            #print ( obj.GetLabel() )
            #print ( "button was pushed for: ", obj.GetLabel() )
            self.Pop_micro ( obj.GetLabel() )

        # The idea here is to set up an array of labels and buttons once and
        # for all, and then change their contents as the display changes.
        def __setup_display ( self ) :

            #desc_font = wx.Font ( 12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
            desc_font = wx.Font ( 12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')

            # Display goes into its own panel
            pan = wx.Panel ( self, -1 )

            # XXX - this needs to also become a panel

            ms = wx.BoxSizer ( wx.VERTICAL )
            pan.SetSizer ( ms )

            self.buttons = []
            self.labels = []

            for _ in range(self.n_lines) :
                p = wx.Panel ( pan, -1 )
                ms.Add ( p, 1, wx.EXPAND )
                sz = wx.BoxSizer ( wx.HORIZONTAL )
                p.SetSizer ( sz )

                b = wx.Button ( p, wx.ID_ANY, "08-999")
                b.Bind ( wx.EVT_BUTTON, self.onButton )
                sz.Add ( b, 0, wx.EXPAND )
                self.buttons.append ( b )

                label = " -- sorry --"
                # Eztext does the sizer add for us
                #def __init__ ( self, parent, sizer, message ) :
                t = EZtext ( p, sz, label )
                t.SetFont ( desc_font )
                self.labels.append ( t )
            return pan

        # expunge excess whitespace
        def __tidy ( self, x ) :
            rv = re.sub ( r'^\s*', '', x )
            rv = re.sub ( r'\s*$', '', rv )
            return rv

        # Generate a nice string to describe a mount
        def __mk_desc ( self, m ) :
            sp = self.__tidy ( m[m_SPECIES] )
            ass = self.__tidy ( m[m_ASS] )
            loc = self.__tidy ( m[m_LOC] )
            if ass != "" :
                sp = sp + ", " + ass
            chop = 25
            if len(sp) > chop :
                sp = sp[:chop]
            rv = sp.ljust ( chop )
            #ll = "  " + loc
            # rv += ll.ljust ( nfill ) + "_"
            rv += "  " + loc
            # This final blank pad is to get color at a uniform width
            # when background color is used.
            return rv.ljust ( 100 )

# ========================= SEARCH ===================================

class Search_Frame ( wx.Frame ) :

        def __init__ ( self, parent, db ):
            title = "Search"
            psize = ( 400, 200 )

            # This happens to be the parent, and we will need to call back
            # to actually do the search
            self.display = parent
            self.db = db

            wx.Frame.__init__(self, None, wx.ID_ANY, title, size=psize )

            pan = wx.Panel ( self, -1 )
            sz = wx.BoxSizer ( wx.VERTICAL )
            pan.SetSizer ( sz )

            # species line -- 
            pan2 = wx.Panel ( pan, -1 )
            sz2 = wx.BoxSizer ( wx.HORIZONTAL )
            pan2.SetSizer ( sz2 )

            # Size is in pixels, not characters
            self.find_species = wx.TextCtrl ( pan2, size=(100, -1))
            sz2.Add ( self.find_species, 1, wx.EXPAND )

            b = wx.Button ( pan2, wx.ID_ANY, "Species")
            b.Bind ( wx.EVT_BUTTON, self.onButton )
            sz2.Add ( b, 0, wx.EXPAND )

            # Associations line --
            #  A checkbox labels itself
            pan22 = wx.Panel ( pan, -1 )
            #sz22 = wx.BoxSizer ( wx.HORIZONTAL )
            #pan22.SetSizer ( sz22 )
            self.assoc = wx.CheckBox ( pan22, label = 'Associations' )

            # location line -- 
            pan3 = wx.Panel ( pan, -1 )
            sz2 = wx.BoxSizer ( wx.HORIZONTAL )
            pan3.SetSizer ( sz2 )

            # Size is in pixels, not characters
            self.find_loc = wx.TextCtrl ( pan3, size=(100, -1))
            sz2.Add ( self.find_loc, 1, wx.EXPAND )

            b = wx.Button ( pan3, wx.ID_ANY, "Location")
            b.Bind ( wx.EVT_BUTTON, self.onButton )
            sz2.Add ( b, 0, wx.EXPAND )

            sz.Add ( pan2, 0, wx.EXPAND )
            sz.Add ( pan22, 0, wx.EXPAND )
            sz.Add ( pan3, 0, wx.EXPAND )

        def onButton ( self, event ) :
            obj = event.GetEventObject()
            action = obj.GetLabel()
            if action == "Species" :
                xx = self.find_species.GetValue()
                ass = self.assoc.GetValue ()
                #print ( "Look for species: ", xx )
                #print ( "Assoc: ", ass )
                self.display.do_search ( True, ass, False, xx )
            if action == "Location" :
                xx = self.find_loc.GetValue()
                #print ( "Look for location: ", xx )
                self.display.do_search ( False, False, True, xx )
            #self.Destroy ()
            self.Close ()

# ========================= PREVIEW ===================================

class Preview_Frame ( wx.Frame ) :

        def __init__ ( self, parent, data, index, db, ll ):
            title = "Mount"
            psize = ( 800, 650 )

            wx.Frame.__init__(self, None, wx.ID_ANY, title, size=psize )
            #top = wx.Frame.__init__(self, None, wx.ID_ANY, title, pos=(a,b), size=wsize )

            self.db = db
            self.labelmaker = ll
            self.main_display = parent

            self.data = data
            self.n_data = len(data)
            self.index = None

            pan = wx.Panel ( self, -1 )
            s = wx.BoxSizer ( wx.VERTICAL )
            pan.SetSizer ( s )

            nav = self.__build_nav ( pan )
            s.Add ( nav, 0, wx.EXPAND )

            s.AddSpacer ( 20 )

            # Setup empty framework

            bogus = "-- bogus"
            self.l1 = EZtext ( pan, s, bogus )

            s.AddSpacer ( 20 )

            #t.SetFont ( xxx_font )
            self.l2 = EZtext ( pan, s, bogus )
            self.l3 = EZtext ( pan, s, bogus )
            self.l4 = EZtext ( pan, s, bogus )

            self.l5 = EZtext ( pan, s, bogus )
            self.l6 = EZtext ( pan, s, bogus )
            self.l7 = EZtext ( pan, s, bogus )
            self.l8 = EZtext ( pan, s, bogus )

            # Collection
            self.l88 = EZtext ( pan, s, bogus )

            self.lc = EZtext ( pan, s, bogus )
            self.lu = EZtext ( pan, s, bogus )

            # notes
            self.l9 = EZtext ( pan, s, bogus )

            s.AddStretchSpacer()

            #prev = wx.StaticBitmap ( pan, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
            # This ends up 291 by 290 pixels
            prev = wx.StaticBitmap ( pan, -1 )
            s.Add ( prev, 0, wx.EXPAND )
            self.bitmap = prev

            # fill display with data
            self.refresh ( index )

        def refresh ( self, index ) :
            self.index = index
            mm = self.data[self.index]

            #msg = "My ID = " + mm[m_MYID] + "     database ID = " + mm[m_ID]
            msg = f"My ID = {mm[m_MYID]}      database ID = {mm[m_ID]}"
            self.l1.SetLabel ( msg )
            msg = f"Species: {mm[m_SPECIES]}"
            self.l2.SetLabel ( msg )
            msg = f"Associations: {mm[m_ASS]}"
            self.l3.SetLabel ( msg )
            msg = f"Location: {mm[m_LOC]}"
            self.l4.SetLabel ( msg )

            msg = f"Origin: {mm[m_ORIGIN]}"
            self.l5.SetLabel ( msg )
            msg = f"Source: {mm[m_SOURCE]}"
            self.l6.SetLabel ( msg )
            msg = f"Owner: {mm[m_OWNER]}"
            self.l7.SetLabel ( msg )

            msg = f"Status: {mm[m_STATUS]}"
            if mm[m_STATUS] == "gift" :
                msg = f"Status: given away"
            self.l8.SetLabel ( msg )

            msg = f"Collection: {mm[m_COLLECTION]}"
            self.l88.SetLabel ( msg )

            msg = f"Created: {mm[m_CREATED]}"
            self.lc.SetLabel ( msg )
            msg = f"Updated: {mm[m_UPDATED]}"
            self.lu.SetLabel ( msg )

            # Put notes last so multiple lines have room
            if mm[m_NOTES] == "" :
                msg = f"Notes: -none-"
            else :
                msg = f"Notes: {mm[m_NOTES]}"
            self.l9.SetLabel ( msg )

            p_path = self.labelmaker.preview ( mm )
            #path = "label_preview.png"
            png = wx.Image ( p_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.bitmap.SetBitmap ( png )

        def __onNav ( self, event ) :
            obj = event.GetEventObject()
            action = obj.GetLabel()
            #print ( "NAV2 button was pushed for: ", action )

            if action == "Next" :
                if self.index + 1 < self.n_data :
                    self.refresh ( self.index + 1)
                return
            if action == "Prev" :
                if self.index > 0 :
                    self.refresh ( self.index - 1)
                return
            if action == "Edit" :
                self.edit = Edit_Frame ( self, self.main_display, self.data, self.index, self.db, self.labelmaker )
                self.edit.Show ( True )
                self.Close ();
                return
            if action == "Clone" :
                self.clone ( self.index )
                return
            if action == "Done" :
                self.Close ()
                return

        def __build_nav ( self, pp ) :
            pan = wx.Panel ( pp, -1 )
            sz = wx.BoxSizer ( wx.HORIZONTAL )
            pan.SetSizer ( sz )

            b = wx.Button ( pan, wx.ID_ANY, "Prev")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "Next")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            sz.AddSpacer ( 50 )
            #sz.AddStretchSpacer()

            b = wx.Button ( pan, wx.ID_ANY, "Edit")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            sz.AddSpacer ( 80 )

            b = wx.Button ( pan, wx.ID_ANY, "Clone")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            sz.AddStretchSpacer()

            b = wx.Button ( pan, wx.ID_ANY, "Done")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            return pan

    # ruby code for clone
    # alloc
    # m_new.species = orig.species
    # m_new.associations = orig.associations
    # m_new.location = orig.location

    # m_new.notes = orig.notes
    # m_new.origin = orig.origin
    # m_new.source = orig.source
    # m_new.owner = orig.owner
    # m_new.status = orig.status
    # insert

        def clone ( self, index ) :
            new = self.data[index]
            print ( f"CLONE {new[m_ID]}" )
            self.db.insert ( new )
            self.main_display.refresh ( False )


# ========================= EDIT ===================================

class Edit_Frame ( wx.Frame ) :

        def __init__ ( self, parent, main, data, index, db, ll ):
            title = "Edit mount"
            psize = ( 800, 850 )

            wx.Frame.__init__(self, None, wx.ID_ANY, title, size=psize )
            #top = wx.Frame.__init__(self, None, wx.ID_ANY, title, pos=(a,b), size=wsize )

            self.db = db
            self.labelmaker = ll
            self.main_display = main

            self.tags = db.get_tags ()

            self.data = data
            self.n_data = len(data)
            self.index = None

            #self.origin_vals = %w(collected bought gift trade)
            self.origin_vals = "collected bought gift trade".split()
            #self.origin_labels = %w(Collected Purchased Gift Trade)
            self.origin_labels = "Collected Bought Gift Trade".split()

            self.status_vals = "ok lost gift trade".split()
            self.status_labels = "OK Lost Given Traded".split()

            self.collection_vals = "main other hubbard lundgren eifel".split()
            self.collection_labels = "Main OP Hubbard Lundgren Eifel".split()

            pan = wx.Panel ( self, -1 )
            s = wx.BoxSizer ( wx.VERTICAL )
            pan.SetSizer ( s )

            nav = self.__build_nav ( pan )
            s.Add ( nav, 0, wx.EXPAND )

            s.AddSpacer ( 20 )

            # Setup empty framework

            bogus = "-- bogus"
            self.l1 = EZtext ( pan, s, bogus )
            #t.SetFont ( xxx_font )
            s.AddSpacer ( 20 )

            p, self.e_species = self.__mk_line ( pan, "Species: ", bogus )
            s.Add ( p, 0, wx.EXPAND )
            p, self.e_ass = self.__mk_line ( pan, "Associations: ", bogus )
            s.Add ( p, 0, wx.EXPAND )
            p, self.e_loc = self.__mk_line ( pan, "Location: ", bogus )
            s.Add ( p, 0, wx.EXPAND )

            s.AddSpacer ( 20 )

            #self.l5 = EZtext ( pan, s, bogus )  # origin
            #self.r5 = wx.RadioBox ( p, label = 'Origin', pos = (80,10), choices = lblList , majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
            self.r_origin = wx.RadioBox ( pan, label = 'Origin', choices = self.origin_labels, style = wx.RA_SPECIFY_COLS )
            s.Add ( self.r_origin, 0, wx.EXPAND )

            s.AddSpacer ( 10 )

            p, self.e_source = self.__mk_line ( pan, "Source: ", bogus )
            s.Add ( p, 0, wx.EXPAND )

            #self.l8 = EZtext ( pan, s, bogus )  # status
            self.r_status = wx.RadioBox ( pan, label = 'Status', choices = self.status_labels, style = wx.RA_SPECIFY_COLS )
            s.Add ( self.r_status, 0, wx.EXPAND )

            s.AddSpacer ( 5 )

            self.r_collection = wx.RadioBox ( pan, label = 'Collection', choices = self.collection_labels, style = wx.RA_SPECIFY_COLS )
            s.Add ( self.r_collection, 0, wx.EXPAND )

            s.AddSpacer ( 10 )

            #self.l6 = EZtext ( pan, s, bogus )  # source

            self.l_owner = EZtext ( pan, s, bogus )  # owner

            self.lc = EZtext ( pan, s, bogus )  # created
            self.lu = EZtext ( pan, s, bogus )  # updated

            s.AddSpacer ( 10 )

            # notes
            #self.l9 = EZtext ( pan, s, bogus )
            p, self.e_notes = self.__mk_line ( pan, "Notes: ", bogus )
            s.Add ( p, 0, wx.EXPAND )

            s.AddStretchSpacer()

            #prev = wx.StaticBitmap ( pan, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
            # This ends up 291 by 290 pixels
            prev = wx.StaticBitmap ( pan, -1 )
            s.Add ( prev, 0, wx.EXPAND )
            self.bitmap = prev

            # fill with data
            self.refresh ( index )

        # Make a line that is a panel with a label and text entry
        def __mk_line ( self, ppan, lab, fill ) :

            pan = wx.Panel ( ppan, -1 )
            s = wx.BoxSizer ( wx.HORIZONTAL )
            pan.SetSizer ( s )

            label = EZtext ( pan, s, lab )

            edit = wx.TextCtrl ( pan, size=(800, -1), value="")
            #edit.SetLabel ( fill )
            s.Add ( edit, 1, wx.EXPAND )

            s.AddStretchSpacer()

            return pan, edit

        # returning 0 on miss is bogus, but better (??)
        # than having the program blow up
        def __find_index ( self, vals, what ) :
            for i in range ( len(vals) ) :
                if what == vals[i] :
                    return i
            return 0

        def refresh ( self, index ) :
            self.index = index
            mm = self.data[self.index]
            self.pristine = mm

            #msg = "My ID = " + mm[m_MYID] + "     database ID = " + mm[m_ID]
            msg = f"My ID = {mm[m_MYID]}      database ID = {mm[m_ID]}"
            self.l1.SetLabel ( msg )

            #self.e_species.AppendText ( mm[m_SPECIES] )
            self.e_species.SetValue ( mm[m_SPECIES] )
            self.e_ass.SetValue ( mm[m_ASS] )
            self.e_loc.SetValue ( mm[m_LOC] )

            #msg = f"Origin: {mm[m_ORIGIN]}"
            #self.l5.SetLabel ( msg )
            ix = self.__find_index ( self.origin_vals, mm[m_ORIGIN] )
            self.r_origin.SetSelection ( ix )

            #msg = f"Status: {mm[m_STATUS]}"
            #self.l8.SetLabel ( msg )
            ix = self.__find_index ( self.status_vals, mm[m_STATUS] )
            self.r_status.SetSelection ( ix )

            ix = self.__find_index ( self.collection_vals, mm[m_COLLECTION] )
            self.r_collection.SetSelection ( ix )

            self.e_source.SetValue ( mm[m_SOURCE] )

            #msg = f"Source: {mm[m_SOURCE]}"
            #self.l6.SetLabel ( msg )

            # always TT at this time
            msg = f"Owner: {mm[m_OWNER]}"
            self.l_owner.SetLabel ( msg )

            msg = f"Created: {mm[m_CREATED]}"
            self.lc.SetLabel ( msg )
            msg = f"Updated: {mm[m_UPDATED]}"
            self.lu.SetLabel ( msg )

            # Put notes last so multiple lines have room
            #if mm[m_NOTES] == "" :
            #    msg = f"Notes: -none-"
            #else :
            #    msg = f"Notes: {mm[m_NOTES]}"
            #self.l9.SetLabel ( msg )

            self.e_notes.SetValue ( mm[m_NOTES] )

            self.label_refresh ( mm )

        # Temporary copy, updated just for label
        # The labels only uses 4 fields:
        #  myid, species, ass, and loc
        def __update_m ( self, mm ) :
            ml = list ( mm )
            ml[m_SPECIES] = self.e_species.GetValue ()
            ml[m_ASS] = self.e_ass.GetValue ()
            ml[m_LOC] = self.e_loc.GetValue ()
            return ml

        # Redo the label image
        def label_refresh ( self, mm ) :
            m_label = self.__update_m ( mm )
            p_path = self.labelmaker.preview ( m_label )
            #path = "label_preview.png"
            png = wx.Image ( p_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.bitmap.SetBitmap ( png )

        def __check ( self, entry, field ) :
            new = entry.GetValue ()
            name = self.tags[field]
            #print ( f"check {name}: {new}" )
            if new != self.pristine[field] :
                #print ( f"- changed -- {self.pristine[field]} --> {new}" ) 
                id = self.pristine[m_ID] 
                self.db.update_one ( id, name, new )

        def __check_r ( self, entry, vals, field ) :
            ix = entry.GetSelection ()
            new = vals[ix]
            name = self.tags[field]
            #print ( f"check_r {name}: {new}" )
            if new != self.pristine[field] :
                #print ( f"- changed_R -- {self.pristine[field]} --> {new}" ) 
                id = self.pristine[m_ID] 
                self.db.update_one ( id, name, new )

        # Each check call may do an update
        def __doSave ( self ) :
            self.__check ( self.e_species, m_SPECIES )
            self.__check ( self.e_loc, m_LOC )
            self.__check ( self.e_ass, m_ASS )
            self.__check ( self.e_source, m_SOURCE )
            self.__check ( self.e_notes, m_NOTES )
            self.__check_r ( self.r_origin, self.origin_vals, m_ORIGIN )
            self.__check_r ( self.r_status, self.status_vals, m_STATUS )
            self.__check_r ( self.r_collection, self.collection_vals, m_COLLECTION )
            self.main_display.refresh ( True )

        def __onNav ( self, event ) :
            obj = event.GetEventObject()
            action = obj.GetLabel()
            #print ( "NAV2 button was pushed for: ", action )

            if action == "Next" :
                if self.index + 1 < self.n_data :
                    self.refresh ( self.index + 1)
                return
            if action == "Prev" :
                if self.index > 0 :
                    self.refresh ( self.index - 1)
                return
            if action == "Refresh" :
                self.label_refresh ( self.data[self.index] )
                return
            if action == "Save" :
                self.__doSave ()
                self.Close ()
                return
            if action == "Cancel" :
                self.Close ()
                return

        def __build_nav ( self, pp ) :
            pan = wx.Panel ( pp, -1 )
            sz = wx.BoxSizer ( wx.HORIZONTAL )
            pan.SetSizer ( sz )

            b = wx.Button ( pan, wx.ID_ANY, "Prev")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "Next")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            sz.AddSpacer ( 50 )
            #sz.AddStretchSpacer()

            b = wx.Button ( pan, wx.ID_ANY, "Refresh")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "Save")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            #sz.AddSpacer ( 50 )
            sz.AddStretchSpacer()

            b = wx.Button ( pan, wx.ID_ANY, "Cancel")
            b.Bind ( wx.EVT_BUTTON, self.__onNav )
            sz.Add ( b, 0, wx.EXPAND )

            return pan

# THE END
