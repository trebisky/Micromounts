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

class Display ( wx.Panel ) :

        def __init__ ( self, parent, db, n_lines ):
            wx.Panel.__init__ ( self, parent )

            self.db = db
            self.n_lines = n_lines
            self.data = self.db.all ()

            s = wx.BoxSizer ( wx.VERTICAL )
            self.SetSizer ( s )

            n = self.__build_nav ()
            s.Add ( n, 0, wx.EXPAND )
            d = self.__setup_display ()
            s.Add ( d, 0, wx.EXPAND )

            #self.__load_display ( 0 )
            self.__load_display ( 1270 )

        def onNav ( self, event ) :
            obj = event.GetEventObject()
            print ( "NAV button was pushed for: ", obj.GetLabel() )

        # Build an H-panel full of navigation controls
        def __build_nav ( self ) :
            pan = wx.Panel ( self, -1 )
            #ms.Add ( pan, 1, wx.EXPAND )
            sz = wx.BoxSizer ( wx.HORIZONTAL )
            pan.SetSizer ( sz )

            b = wx.Button ( pan, wx.ID_ANY, "Go")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            b = wx.Button ( pan, wx.ID_ANY, "Stop")
            b.Bind ( wx.EVT_BUTTON, self.onNav )
            sz.Add ( b, 0, wx.EXPAND )

            return pan

        def __load_display ( self, start ) :
            for ll in self.labels :
                ll.SetLabel ( "" )
            # This works fine at the end of data when the
            # slice has less than n_lines
            #slice = self.data[start:end]
            #print ( "Slice: ", len(slice) )
            ii = 0
            end = start + self.n_lines
            for m in self.data[start:end] :
                label = self.mk_desc ( m )
                self.labels[ii].SetLabel ( label )
                self.buttons[ii].SetLabel ( m[m_MYID] )
                ii += 1

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

# THE END
