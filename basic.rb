#!/usr/bin/ruby

require 'gtk3'

Gtk::init()

# Look! in gtk3 you can set the title in the new statement
win = Gtk::Window.new( "fish" )
#win.set_title ( "basic" )

def mk_button ( label, msg )
    rv = Gtk::Button.new( :label => label )
    rv.signal_connect "clicked" do |_widget|
      puts msg
    end
    rv
end

butt1a = mk_button( "Say hello", "Hello World" )
butt1b = mk_button( "Cry hello", "hello" )
butt2a = mk_button( "Say bye", "Bye World" )
butt2b = mk_button( "Cry bye", "bye bye" )

# We can add to a container or pack in a box.
hbox1 = Gtk::Box.new(:horizontal, 5)
#hbox1.add(butt1a)
#hbox1.add(butt1b)
hbox1.pack_start(butt1a, :expand => true, :fill => true)
hbox1.pack_start(butt1b, :expand => true, :fill => true)

hbox2 = Gtk::Box.new(:horizontal, 5)
hbox2.pack_start(butt2a, :expand => true, :fill => true)
hbox2.pack_start(butt2b, :expand => true, :fill => true)

vbox = Gtk::Box.new(:vertical, 5)
vbox.add(hbox1)
vbox.add(hbox2)

win.add(vbox)

win.signal_connect( 'delete_event' ) { false }
#win.signal_connect( "delete-event" ) { |_widget| Gtk.main_quit }
win.signal_connect( 'destroy' ) { Gtk.main_quit }

win.show_all

Gtk.main
# THE END
