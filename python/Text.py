#!/bin/python3

# Text.py
#
# Tom Trebisky  7-25-2024
# 
# my customized Static Text widget

import wx

# wxPython has some severe brain damage as far as greying out text when you move
# the mouse out of the window.  They don't understand the concept that this is
# an information display, not some active control with interaction.
#
# https://stackoverflow.com/questions/17764457/make-disabled-text-render-black
#
# I also want to center text inside an area of fixed size, so I may as well
# dive in.  I am taking the code posted by Hesky Fisher in the above post.
#
#    Thanks Hesky !!

class MyStaticText ( wx.Control ):
    def __init__(self, parent, id=wx.ID_ANY, label="", 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=0, validator=wx.DefaultValidator, 
                 name="MyStaticText"):
        wx.Control.__init__(self, parent, id, pos, size, style|wx.NO_BORDER, validator, name)

        wx.Control.SetLabel(self, label)
        self.InheritAttributes()
        self.SetInitialSize(size)

        self.bg_color = parent.GetBackgroundColour ()
        self.fg_color = wx.BLACK

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    def Draw(self, dc):
        width, height = self.GetClientSize()

        if not width or not height:
            return

        # TJT - We should get the background of the parent instead
        # backBrush = wx.Brush(wx.WHITE, wx.SOLID)
        backBrush = wx.Brush ( self.bg_color, wx.SOLID)
        dc.SetBackground(backBrush)
        dc.Clear()

        #dc.SetTextForeground(wx.BLACK)
        dc.SetTextForeground ( self.fg_color )
        dc.SetFont(self.GetFont())
        label = self.GetLabel()
        dc.DrawText(label, 0, 0)

    def SetFGColour(self, colour):
        self.fg_color = colour
        self.Refresh()

    def SetBGColour(self, colour):
        self.bg_color = colour
        self.Refresh()

    def OnEraseBackground(self, event):
        pass

    def SetLabel(self, label):
        wx.Control.SetLabel(self, label)
        self.InvalidateBestSize()
        self.SetSize(self.GetBestSize())
        self.Refresh()

    def SetFont(self, font):
        wx.Control.SetFont(self, font)
        self.InvalidateBestSize()
        self.SetSize(self.GetBestSize())
        self.Refresh()

    def DoGetBestSize(self):
        label = self.GetLabel()
        font = self.GetFont()

        if not font:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        dc = wx.ClientDC(self)
        dc.SetFont(font)

        textWidth, textHeight = dc.GetTextExtent(label)
        best = wx.Size(textWidth, textHeight)
        self.CacheBestSize(best)
        return best

    def AcceptsFocus(self):
        return False

# Does not work.
#    def SetForegroundColour(self, colour):
#        wx.Control.SetForegroundColour(self, colour)
#        self.Refresh()
#
#    def SetBackgroundColour(self, colour):
#        wx.Control.SetBackgroundColour(self, colour)
#        self.Refresh()

    def GetDefaultAttributes(self):
        return wx.StaticText.GetClassDefaultAttributes()

    def ShouldInheritColours(self):
        return True

# This is my wrapper on the above
# I had trouble getting this right.
# The trick is that the __init__ method does a special thing.
# it effectively returns "self" in a magic way.
# (and "self" is the value returned by the superclass.)
class EZtext ( MyStaticText ) :
        def __init__ ( self, parent, sizer, message ) :
            #rv = MyStaticText.__init__ ( self, parent, wx.ID_ANY, message )
            #sizer.Add ( rv, 1, wx.EXPAND )
            #print ( rv )
            #print ( type(rv) )

            #size = wx.DefaultSize
            #print ( "Text size = ", size )
            # Shows (-1, -1)

            # prefix some space here
            padded = "    " + message
            MyStaticText.__init__ ( self, parent, wx.ID_ANY, padded )
            #sizer.Add ( self, 1, wx.EXPAND )
            sizer.Add ( self, 0, wx.EXPAND )

        def SetLabel ( self, msg ) :
            padded = "    " + msg
            super().SetLabel ( padded )

# THE END
