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

# Display one mount in dialog
# XXX reuse the same dialog if up, don't keep spawning new ones.
# Also, refresh information here, and in main display when things
# get updated.
class Uno
    @dialog = nil

    def initialize ( main )
	@parent = main
	@cur = nil
    end

    def mk_line ( label, stuff )
	rv = Gtk::Box.new(:horizontal, 5)
	l = Gtk::Label.new label
	rv.pack_start( l, :expand => false, :fill => false)
	l = Gtk::Label.new stuff
	rv.pack_start( l, :expand => false, :fill => false)
	rv
    end

    # This does make a new mount
    def tester
	x = $mdb.alloc
	show_mount x
	$mdb.insert x
    end

    # This does do the update
    def tester2
	@cur.species = "baloney"
	$mdb.update @cur
    end

    # We can find the last record
    def tester3
	lm = $mdb.fetch_last
	show_mount lm
    end

    def show_mount ( m )

	# XXX
	@cur = m

	@dialog = Gtk::Dialog.new( :title => "Mount", :parent => @parent, :flags => :destroy_with_parent )

	@dialog.child.add mk_line( "Mount: ", m.mk_id(nil) )	# myid
	@dialog.child.add mk_line( "Species: ", m.species )
	@dialog.child.add mk_line( "Associations: ", m.associations )
	@dialog.child.add mk_line( "Location: ", m.location )

	@dialog.child.add mk_line( "Created: ", m.created_at )
	@dialog.child.add mk_line( "Updated: ", m.updated_at )
	@dialog.child.add mk_line( "Internal ID: ", m.id.to_s )

	bx = Gtk::Box.new(:horizontal, 5)

	b = Gtk::Button.new( :label => "Prev" )
	bx.pack_start( b, :expand => false, :fill => false)

	b = Gtk::Button.new( :label => "Next" )
	bx.pack_start( b, :expand => false, :fill => false)

	b = Gtk::Button.new( :label => "Test" )
	b.signal_connect( "clicked" ) {
	    tester
	}
	bx.pack_start( b, :expand => false, :fill => false)

	b = Gtk::Button.new( :label => "Dismiss" )
	b.signal_connect( "clicked" ) {
	    x = @dialog
	    @dialog = nil
	    x.destroy
	}
	bx.pack_start( b, :expand => false, :fill => false)

	@dialog.child.add bx

	@dialog.show_all
    end
end

class Search
    @dialog = nil
    @parent = nil

    def initialize ( main )
	@search = nil
	@parent = main
    end

    def show_dialog
	# gtk3 says: 'Gtk::Dialog#initialize(title, parent, flags, *buttons)' style has been deprecated.
	# Use 'Gtk::Dialog#initialize(:title => nil, :parent => nil, :flags => 0, :buttons => nil)' style.
	@dialog = Gtk::Dialog.new( :title => "Search", :parent => @parent, :flags => :destroy_with_parent )

	# Ensure that the dialog box is destroyed when the user responds.
	#  I am not sure this is really necessary
	# @dialog.signal_connect('response') { @dialog.destroy }

	sp_box = Gtk::Box.new(:horizontal, 5)
	l = Gtk::Label.new "Species: "
	sp_box.pack_start( l, :expand => false, :fill => false)

	@e_species = Gtk::Entry.new
	sp_box.pack_start( @e_species, :expand => false, :fill => true)

	@dialog.child.add sp_box

	@ass = Gtk::CheckButton.new "With associations: "
	@dialog.child.add @ass

	loc_box = Gtk::Box.new(:horizontal, 5)
	l = Gtk::Label.new "Location: "
	loc_box.pack_start( l, :expand => false, :fill => false)

	@e_location = Gtk::Entry.new
	loc_box.pack_start( @e_location, :expand => false, :fill => true)

	@dialog.child.add loc_box

	b = Gtk::Button.new( :label => "Search" )
	b.signal_connect( "clicked" ) { run_search }
	@dialog.child.add b

	b = Gtk::Button.new( :label => "Clear" )
	b.signal_connect( "clicked" ) { clear_search }
	@dialog.child.add b

	b = Gtk::Button.new( :label => "Done" )
	b.signal_connect( "clicked" ) { @dialog.destroy }
	@dialog.child.add b

	@status = Gtk::Label.new("")
	@dialog.child.add @status

	@dialog.show_all
    end

    def clear_search
	@search = nil
	$nav.show_mounts_end
	@status.text = ""
    end

    def run_search
	ass = @ass.active?
	if ( ass )
	    puts "Associations active"
	else
	    puts "Associations NOT active"
	end

	# an empty entry widget yields an empty string
	who = @e_species.text
	who_loc = @e_location.text

	puts "Searching for species: #{who}"
	if ( who_loc != "" )
	    puts "Searching for location: #{who_loc}"
	end

	num = $mdb.fetch_u_count who, who_loc, ass
	#print "#{num} specimens of #{who} in database\n"

	if num < 1
	    @status.text = "Sorry"
	    color_red  = Gdk::RGBA::new 1.0, 0.0, 0.0, 1.0
	    color_yellow = Gdk::RGBA::new 1.0, 1.0, 0.0, 1.0
	    @status.override_background_color :normal, color_yellow
	    @status.override_color :normal, color_red
	    @search = nil
	    $nav.show_mounts_end
	else
	    @status.text = "#{num} found"
	    color_black  = Gdk::RGBA::new 0.0, 0.0, 0.0, 1.0
	    color_white = Gdk::RGBA::new 1.0, 1.0, 1.0, 1.0
	    @status.override_background_color :normal, color_white
	    @status.override_color :normal, color_black
	    @search = $mdb.fetch_u who, who_loc, ass
	    $nav.show_mounts 1
	    #@dialog.destroy
	end
    end
    def get_search
	return @search
    end
end

Gtk::init()

# Look! in gtk3 you can set the title in the new statement
$main_win = Gtk::Window.new( "Micromount browser" )

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

    def handle_button ( row )
	#puts "Button row: " + row.to_s
	if @ids[row] < 0
	    # This happens when we have filler buttons
	    #  at the end of the display
	    # (should not happen now, they are greyed out)
	    puts "Bogus button *********** !"
	else
	    puts "Button id: " + @ids[row].to_s
	    m = $mdb.fetch( @ids[row] )
	    m.show
	    $uno.show_mount m
	end
    end

    def mk_button ( label, row )
	rv = Gtk::Button.new( :label => label )
	rv.signal_connect( "clicked" ) { |_widget|
	    handle_button row
	}
	rv
    end

    def nice_font ( label )
	font = "monospace 12"
	desc = Pango::FontDescription.new font
	#label.text = "Font: %s" % [desc]
	label.override_font desc
    end

    def setup_mount_hbox ( vbox, row )
	hbox = Gtk::Box.new(:horizontal, 5)
	but = mk_button( @init_but, row )
	ckb = Gtk::CheckButton.new ""
	# test via active?
	lab = Gtk::Label.new @init_lab
	nice_font lab
	hbox.pack_start( but, :expand => false, :fill => false)
	hbox.pack_start( ckb, :expand => false, :fill => false)
	hbox.pack_start( lab, :expand => false, :fill => true)
	vbox.add(hbox)
	@buts << but
	@cks << ckb
	@labs << lab
	@ids << 99
    end

    def initialize ( vbox )
	@init_but = "x" * $but_size
	@init_lab = "x" * $lab_size

	@buts = Array.new
	@cks = Array.new
	@labs = Array.new
	@ids = Array.new $nrows, 13

	$nrows.times { |row|
	    setup_mount_hbox vbox, row
	}
    end

    def new_mounts ( ms )
	row = 0
	ms.each { |m|
	    @buts[row].label = m.mk_id
	    @buts[row].sensitive = true
	    @cks[row].set_active false
	    @cks[row].sensitive = true
	    @labs[row].text = m.mk_desc
	    @ids[row] = m.id
	    row += 1
	}
	while row < $nrows
	    @buts[row].label = " "
	    @buts[row].sensitive = false  # grey out
	    @cks[row].set_active false  # turn off check mark
	    @cks[row].sensitive = false
	    @labs[row].text = " "
	    @ids[row] = -1
	    row += 1
	end
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

class Nav

    def nav_button ( box, label )
	b = Gtk::Button.new( :label => label )
	box.pack_start( b, :expand => false, :fill => false)
	b
    end

    def initialize

	@cur = nil

	# This holds navigation and info
	@box = Gtk::Box.new(:horizontal, 5)

	b = nav_button @box, "Search   "
	b.signal_connect( "clicked" ) { $search.show_dialog }

	b = nav_button @box, "First"
	#b.signal_connect( "clicked" ) { |_widget|
	b.signal_connect( "clicked" ) { show_mounts 1 }

	b = nav_button @box, "Previous"
	b.signal_connect( "clicked" ) { show_mounts @cur - 1 }

	b = nav_button @box, "Next"
	b.signal_connect( "clicked" ) { show_mounts @cur + 25 }

	b = nav_button @box, "Last"
	b.signal_connect( "clicked" ) { show_mounts_end }


	$info = Gtk::Label.new "Insert Coin"
	@box.pack_start( $info, :expand => false, :fill => true)
    end

    def box
	return @box
    end

    # This includes logic as to whether we are displaying
    # a full view of the database or the results of a search.
    # XXX - it might be cleaner to move this into the
    # Search object
    def show_mounts ( start )

	db_total = $mdb.fetch_total_count
	ms_search = $search.get_search
	if ms_search
	    total = ms_search.size
	else
	    total = db_total
	end

	start = (start-1) - (start -1) % $nrows + 1
	return if ( start < 1 )
	return if ( start > total )
	@cur = start

	if ms_search
	    ms = ms_search[start-1,$nrows]
	else
	    ms = $mdb.fetch_all start
	end
	# print "Got #{ms.size} records\n"

	last = start + ms.size - 1
	if ms_search
	    msg = "    Showing #{start} to #{last} of #{total} selected from #{db_total} mounts"
	else
	    msg = "    Showing #{start} to #{last} of #{total} mounts"
	end
	$info.text = msg

	$disp.new_mounts ms
    end
    def show_mounts_end
	ms_search = $search.get_search
	if ms_search
	    total = ms_search.size
	else
	    total = $mdb.fetch_total_count
	end
	show_mounts total
    end
end

$search = Search.new $main_win
$uno = Uno.new $main_win

# This holds everything
vbox = Gtk::Box.new(:vertical, 5)

# We get the box from the Nav object
$nav = Nav.new
vbox.add $nav.box

# But we let the display object add itself
$disp = Display.new vbox

$main_win.add(vbox)

# Always start at end of database
$nav.show_mounts_end

#$main_win.signal_connect( 'delete_event' ) { false }
$main_win.signal_connect( "delete-event" ) { |_widget| Gtk.main_quit }
$main_win.signal_connect( 'destroy' ) { Gtk.main_quit }

$main_win.show_all

Gtk.main

puts ""
puts " -- All done"
# THE END
