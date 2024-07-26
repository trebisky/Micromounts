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

class Display ( wx.Panel ) :

        def __init__ ( self, parent, db, n_lines ):
            wx.Panel.__init__ ( self, parent )

            self.db = db
            self.n_lines = n_lines

            self.preview = None
            self.labelmaker = Labelsheet ()

            self.data = self.db.all ()
            self.n_data = len ( self.data )
            self.cur = None

            s = wx.BoxSizer ( wx.VERTICAL )
            self.SetSizer ( s )

            n = self.__build_nav ()
            s.Add ( n, 0, wx.EXPAND )
            d = self.__setup_display ()
            s.Add ( d, 0, wx.EXPAND )

            #self.__load_display ( 0 )
            #self.__load_display ( 1270 )
            self.__load_display ( self.n_data - self.n_lines )

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
            print ( "NAV button was pushed for: ", action )

            if action == "Next" :
                start = self.cur + self.n_lines
                if start < self.n_data :
                    self.__load_display ( start )
                return
            if action == "Prev" :
                start = self.cur - self.n_lines
                if start >= 0 :
                    self.__load_display ( start )
                return
            if action == "Start" :
                self.__load_display ( 0 )
                return
            if action == "End" :
                self.__load_display ( self.n_data - self.n_lines )
                return
            if action == "Find" :
                xx = self.find.GetValue()
                print ( "Look for: ", xx )
                ii = self.__lookup_I ( xx )
                if ii == None :
                    print ( xx, " not found" )
                    return
                self.__load_display ( ii )
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

            # Size is in pixels, not characters
            self.find = wx.TextCtrl ( pan, size=(100, -1))
            sz.Add ( self.find, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "Find")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            return pan

        def __load_display ( self, start ) :
            self.cur = start
            for ll in self.labels :
                ll.SetLabel ( "" )
            for bb in self.buttons :
                bb.SetLabel ( "--" )
            # This works fine at the end of data when the
            # slice has less than n_lines
            ii = 0
            end = start + self.n_lines
            slice = self.data[start:end]
            #print ( "Slice: ", len(slice) )
            for m in slice :
                label = self.mk_desc ( m )
                self.labels[ii].SetLabel ( label )
                self.buttons[ii].SetLabel ( m[m_MYID] )
                ii += 1

        def Pop_micro ( self, my_id ) :
            m = self.__lookup_id ( my_id )
            if m == None :
                return
            # or, we could keep the existing frame and just
            # change the contents
            if self.preview :
                self.preview.destroy ()
            self.preview = Preview_Frame ( self, m, self.labelmaker )
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
            print ( "button was pushed for: ", obj.GetLabel() )
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
        def mk_desc ( self, m ) :
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
            return rv

class Preview_Frame ( wx.Frame ) :

        def __init__ ( self, parent, mm, ll ):
            title = "One mount"
            psize = ( 600, 600 )
            wx.Frame.__init__(self, None, wx.ID_ANY, title, size=psize )
            #top = wx.Frame.__init__(self, None, wx.ID_ANY, title, pos=(a,b), size=wsize )

            pan = wx.Panel ( self, -1 )
            s = wx.BoxSizer ( wx.VERTICAL )
            pan.SetSizer ( s )

            t = EZtext ( pan, s, mm[m_MYID] )
            #t.SetFont ( xxx_font )

            p_path = ll.preview ( mm )
            #path = "label_preview.png"
            png = wx.Image ( p_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            prev = wx.StaticBitmap ( pan, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
            s.Add ( prev, 0, wx.EXPAND )

            # Display is a panel that fills this frame
            #self.dd = Display ( self, db, max_lines )

# THE END
