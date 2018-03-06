#!/usr/bin/ruby

# browse - 
# A first step towards a real application.
# The idea here is to be able to page through
# the 1000 plus entries in my database, with
# a screen that holds 25 lines.
# This will be the first program that combines
# the use of both sqlite3 and gtk3.
#
# Tom Trebisky 3-4-2018

require 'gtk3'

$:.unshift "."
require 'Mounts'

$db = "minerals.sqlite3"
$nrows = 25
$but_size = 11
$lab_size = 100

# -----------------------------------------

$mdb = Mounts.new
$mdb.set_limit $nrows

Gtk::init()

# Look! in gtk3 you can set the title in the new statement
win = Gtk::Window.new( "Micromount browser" )

##  def add_mount_hbox ( vbox, m )
##      hbox = Gtk::Box.new(:horizontal, 5)
##      id = m.mk_id
##      msg = "ID = " + m.id.to_s
##      but = mk_button( id, msg )
##      desc = Gtk::Label.new m.mk_desc
##  #    desc.justify = :left
##      hbox.pack_start( but, :expand => false, :fill => false)
##      hbox.pack_start( desc, :expand => false, :fill => true)
##      vbox.add(hbox)
##  end
##  
##  def add_mounts ( win, ms )
##      vbox = Gtk::Box.new(:vertical, 5)
##      ms.each { |m|
##  	add_mount_hbox vbox, m
##      }
##  
##      win.add(vbox)
##  end

class Display

    def mk_button ( label, index )
	rv = Gtk::Button.new( :label => label )
	rv.signal_connect "clicked" do |_widget|
	    puts "ID = " + @ids[index]
	end
	rv
    end

    def setup_mount_hbox ( vbox, row )
	hbox = Gtk::Box.new(:horizontal, 5)
	msg = "Row = " + row.to_s
	but = mk_button( @init_but, msg )
	desc = Gtk::Label.new @init_lab
	hbox.pack_start( but, :expand => false, :fill => false)
	hbox.pack_start( desc, :expand => false, :fill => true)
	vbox.add(hbox)
	@buts << but
	@labs << desc
	@ids << 99
    end

    def initialize ( win )
	@init_but = "x" * $but_size
	@init_lab = "x" * $lab_size

	@buts = Array.new
	@labs = Array.new
	@ids = Array.new

	vbox = Gtk::Box.new(:vertical, 5)
	$nrows.times { |row|
	    setup_mount_hbox vbox, row
	}

	win.add(vbox)
    end

    def new_mounts ( ms )
	row = 0
	ms.each { |m|
	    @buts[row].label = m.mk_id
	    @labs[row].text = m.mk_desc
	    @ids[row] = m.id
	    row += 1
	}
    end
end

# def add_mount_grid ( grid, row, m )
#     id = m.mk_id
#     but = mk_button( id, id )
#     grid.attach but, 0, row, 1, 1
#     desc = Gtk::Label.new m.mk_desc 100
#     desc.justify = :left
#     grid.attach desc, 1, row, 1, 1
# end
# 
# def add_mounts_g ( win, ms )
#     grid = Gtk::Grid.new
# #    grid.set_property "row-homogeneous", true
# #    grid.set_property "column-homogeneous", true
# 
#     row = 0
#     ms.each { |m|
# 	add_mount_grid grid, row, m
# 	row += 1
#     }
# 
#     win.add grid
# end

def show_mounts ( w, start )
    start = start - start % $nrows + 1
    total = $mdb.fetch_total_count
    ms = $mdb.fetch_all start
    # print "Got #{ms.size} records\n"
    last = start + ms.size - 1
    msg = "Showing #{start} to #{last} of #{total} mounts"
    puts msg

#    add_mounts( w, ms )
    $disp.new_mounts ms
end

$disp = Display.new win

show_mounts win, 123
#show_mounts win, 1007

#win.signal_connect( 'delete_event' ) { false }
win.signal_connect( "delete-event" ) { |_widget| Gtk.main_quit }
win.signal_connect( 'destroy' ) { Gtk.main_quit }

win.show_all

Gtk.main

puts ""
puts " -- All done"
# THE END
