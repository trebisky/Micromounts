#!/usr/bin/ruby

# micros.rb
#
# This is the application to handle
#  my mineral application database.
#
# It is written in ruby, and is my first
#  ruby project using the gtk3 toolkit.
# The database itself is done via the
#  sqlite3 gem (see Mounts.rb)
#
# I began developing this as browse.rb,
# thinking that would just be a "test flight"
# of a read only database browser.
# But I kept adding features, including the
# ability to edit entries, and make new entries.
# When I got ready to add the label making code,
# I decided it was time to change to the official
# final name for the project (micros.rb)
#
# Tom Trebisky 3-4-2018 -- began browse.rb
# Tom Trebisky 3-10-2018 -- transition to micros.rb

require 'gtk3'

$:.unshift "."
require 'Mounts'
require 'Labels'

$db = "minerals.sqlite3"
$nrows = 25
$but_size = 11
$lab_size = 100

# -----------------------------------------

# Display one mount in a dialog for editing
# (began as a clone of Uno)
class Edit

    # for radiobuttons.
    # vals are what goes into database
    # labels are what we show on GUI
    @@status_vals = %w(ok lost gift trade)
    @@status_labels = %w(OK Lost Given\ away Traded)

    @@origin_vals = %w(collected bought gift trade)
    @@origin_labels = %w(Collected Purchased Gift Trade)

    def initialize ( main )
	@parent = main
	@cur = nil
	@dialog = nil
	@visible = false

    end

    # Two labels in a box, for items we are not allowed to edit.
    def mk_line ( main, label )
	rv = Gtk::Box.new(:horizontal, 5)
	l = Gtk::Label.new label
	rv.pack_start( l, :expand => false, :fill => false)
	l = Gtk::Label.new ""
	rv.pack_start( l, :expand => false, :fill => false)
	main.child.add rv
	l
    end

    def mk_entry ( main, label )
	rv = Gtk::Box.new(:horizontal, 5)
	l = Gtk::Label.new label
	rv.pack_start( l, :expand => false, :fill => false)

	e = Gtk::Entry.new
	e.width_chars = 80

	rv.pack_start( e, :expand => false, :fill => true)
	main.child.add rv
	e
    end

    def mk_radio ( main, label, choices )
	rv = Gtk::Box.new(:horizontal, 5)
	l = Gtk::Label.new label
	rv.pack_start( l, :expand => false, :fill => false)

	buts = Array.new
	c_main = choices.shift
	r_main = Gtk::RadioButton.new( :label => c_main )
	buts << r_main
	rv.pack_start( r_main, :expand => false, :fill => true)
	choices.each { |c|
	    r = Gtk::RadioButton.new( :member => r_main, :label => c )
	    buts << r
	    rv.pack_start( r, :expand => false, :fill => true)
	}
	main.child.add rv
	buts
    end

    def radio_extract ( rb )
	rv = nil
	i = 0
	rb.each { |b|
	    rv = i if b.active?
	    i += 1
	}
	rv
    end

    # call this to extract everything from the form and load it
    # back into our object, then save the modified record
    # only entry and radio gadgets could have been modified.
    def save

	puts @e_species.text
	puts @e_ass.text
	puts @e_loc.text

	puts @e_source.text

	s_index = radio_extract @r_status
	o_index = radio_extract @r_origin

	puts @@status_vals[s_index]
	puts @@origin_vals[o_index]

	# update object values
	@cur.species = @e_species.text
	@cur.associations = @e_ass.text
	@cur.location = @e_loc.text
	@cur.source = @e_source.text

	@cur.status = @@status_vals[s_index]
	@cur.origin = @@origin_vals[o_index]

	$mdb.update @cur
	refresh
	$nav.refresh

    end

    # clone a record and then switch to it.
    def clone
	$mdb.clone @cur
	mm = $mdb.fetch_last
	@cur = mm
	reload
	$nav.refresh
    end

    def setup_dialog ( png_file )
	@dialog = Gtk::Dialog.new( :title => "Mount", :parent => @parent, :flags => :destroy_with_parent )

	@l_myid = mk_line( @dialog, "Mount: " )

	@e_species = mk_entry( @dialog, "Species: " )
	@e_ass = mk_entry( @dialog, "Associations: " )
	@e_loc = mk_entry( @dialog, "Location: " )

	@r_status = mk_radio( @dialog, "Status", @@status_labels )
	@r_origin = mk_radio( @dialog, "Origin", @@origin_labels )

	@e_source = mk_entry( @dialog, "Source: " )

	@l_created = mk_line( @dialog, "Created: " )
	@l_updated = mk_line( @dialog, "Updated: " )

	@l_id = mk_line( @dialog, "Internal ID: " )

	# Make navigation row at bottom
	bx = Gtk::Box.new(:horizontal, 5)

	b = Gtk::Button.new( :label => "Prev" )
	bx.pack_start( b, :expand => false, :fill => false)
	b.signal_connect( "clicked" ) {
	    load_prev
	}

	b = Gtk::Button.new( :label => "Next" )
	bx.pack_start( b, :expand => false, :fill => false)
	b.signal_connect( "clicked" ) {
	    load_next
	}

	b = Gtk::Button.new( :label => " Save " )
	b.signal_connect( "clicked" ) {
	    save
	}
	bx.pack_start( b, :expand => false, :fill => false)

	b = Gtk::Button.new( :label => " Clone " )
	b.signal_connect( "clicked" ) {
	    clone
	}
	bx.pack_start( b, :expand => false, :fill => false)

	b = Gtk::Button.new( :label => "Dismiss" )
	b.signal_connect( "clicked" ) {
	    x = @dialog
	    @dialog = nil
	    @visible = nil
	    x.destroy
	}
	bx.pack_start( b, :expand => false, :fill => false)

	# img = Gtk::Image.new png_file (deprecated)
	img = Gtk::Image.new( :file => png_file )
	@image = img

	vb = Gtk::Box.new(:vertical, 5)

	vb.pack_start( bx, :expand => false, :fill => false)
	vb.pack_start( img, :expand => false, :fill => false)

	#@dialog.child.add bx
	@dialog.child.add vb

	@dialog.show_all

	@visible = true
    end

    def reload

	# labels
	@l_myid.text = @cur.mk_id(nil)
	@l_created.text = @cur.created_at + " UTC"
	@l_updated.text = @cur.updated_at + " UTC"
	@l_id.text = @cur.id.to_s

	# entries
	@e_species.text = @cur.species
	@e_ass.text = @cur.associations
	@e_loc.text = @cur.location

	@e_source.text = @cur.source

	# radios
	i_status = @@status_vals.index @cur.status
	i_origin = @@origin_vals.index @cur.origin

	@r_status[i_status].set_active true
	@r_origin[i_origin].set_active true

	# label preview
	# This image seems to be 521 by 521 pixels, although
	# I have never needed to take that into account.
	png_path = Label.get_label @cur
	# png_pixbuf = Gdk::Pixbuf.new( png_path ) -- deprecated
	png_pixbuf = GdkPixbuf::Pixbuf.new( :file => png_path )
	@image.set_from_pixbuf png_pixbuf

    end

    def load_prev
	mm = $mdb.fetch_prev ( @cur.id )
	return if mm == nil
	@cur = mm
	reload
	$nav.refresh
    end

    def load_next
	mm = $mdb.fetch_next ( @cur.id )
	return if mm == nil
	@cur = mm
	reload
	$nav.refresh
    end

    # Called after we have written a modified
    # (or brand new) record to the database.
    # This ensures that autogenerated fields
    # such at the updated time stamp get displayed
    def refresh
	mm = $mdb.fetch ( @cur.id )
	@cur = mm
	reload
    end

    # This does the initial display of a mount
    # when a mount button is clicked
    def show_mount ( m )

	png_path = Label.get_label m
	#puts png

	unless @visible
	    setup_dialog png_path
	end

	@cur = m
	reload
    end
end

# Display one mount in dialog
# This turned into Edit (above) and is no longer used.
# XXX XXX
# We might want this to have a readonly mode for the application.
# If so, a fair amount of stuff from the above would need to
# get retrofited to his.  In particular the business of not
# continually spawning an endless number of new dialogs, but
# updating values in an existing one.
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
    def tester1
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

    # Test clone, -- it works !!
    def tester
	$mdb.clone @cur
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

# This is not quite right since show_mounts is
# really dealing with record numbers, not id numbers
    def fetch_tt ( myid )
	mm = $mdb.fetch_myid ( myid )
	if mm != nil
	    $nav.show_mounts mm.id
	end
    end

    def show_dialog
	# gtk3 says: 'Gtk::Dialog#initialize(title, parent, flags, *buttons)' style has been deprecated.
	# Use 'Gtk::Dialog#initialize(:title => nil, :parent => nil, :flags => 0, :buttons => nil)' style.
	@dialog = Gtk::Dialog.new( :title => "Search", :parent => @parent, :flags => :destroy_with_parent )

	# Ensure that the dialog box is destroyed when the user responds.
	#  I am not sure this is really necessary
	# @dialog.signal_connect('response') { @dialog.destroy }

	# As for mount by TT number
	tt_box = Gtk::Box.new(:horizontal, 5)
	l = Gtk::Label.new "TT-"
	tt_box.pack_start( l, :expand => false, :fill => false)

	@e_myid = Gtk::Entry.new
	tt_box.pack_start( @e_myid, :expand => false, :fill => true)

	b = Gtk::Button.new( :label => "Fetch TT number" )
	b.signal_connect( "clicked" ) { fetch_tt( @e_myid.text ) }
	tt_box.pack_start( b, :expand => false, :fill => true)

	@dialog.child.add tt_box

	# Start standard species, location search
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

class Display

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

    def handle_button ( row )
	#puts "Button row: " + row.to_s
	if @ids[row] < 0
	    # This happens when we have filler buttons
	    #  at the end of the display
	    # (should not happen now, they are greyed out)
	    puts "Bogus button *********** !"
	else
	    ##puts "Button id: " + @ids[row].to_s
	    m = $mdb.fetch( @ids[row] )
	    # m.show
	    # $uno.show_mount m
	    $edit.show_mount m
	end
    end

    def mk_button ( label, row )
	rv = Gtk::Button.new( :label => label )
	rv.signal_connect( "clicked" ) { |_widget|
	    handle_button row
	}
	rv
    end

    # This handles the label checkbutton on the index.
    def label_callback ( b, m )
	#print "Button: " + m.id.to_s + " " + m.mk_desc + " "
	if b.active?
	    #puts "Active"
	    $ls.add_mount m.id
	else
	    #puts "Not active"
	    $ls.remove_mount m.id
       end
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
	# This is actually a flavor of ToggleButton
	ckb = Gtk::CheckButton.new ""
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

    def new_mounts ( ms )
	row = 0
	# These are actually real things being displayed
	ms.each { |m|
	    @buts[row].label = m.mk_id
	    @buts[row].sensitive = true
	    @labs[row].text = m.mk_desc
	    @ids[row] = m.id

	    checker = @cks[row]
	    # ?? use either of these, but apparently we
	    # don't need to.  They come up unchecked.
	    #checker.set_active false
	    #checker.active = false

	    ##if $rand.rand(100) < 50
	    ##	@cks[row].active = true
	    ##end
	    checker.sensitive = true
	    checker.signal_connect('toggled') {
		label_callback checker, m
	    }

	    row += 1
	}
	# These are empty rows on the display
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

# We have a problem in that this set of routines paginates by
# record number, whereas "id" may or may not correspond to the
# record number.  In fact we have a 7 entry gap after id 849.
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

    # Called after the user modifies the database in any way
    # (adding a new mount or editing an existing one)
    # so that the main display stays up to date
    def refresh
	show_mounts @cur
    end
end

##$rand = Random.new

$mdb = Mounts.new
$mdb.set_limit $nrows

$ls = Labelstore.new $mdb
Label.new $ls, $mdb

Gtk::init()

# Look! in gtk3 you can set the title in the new statement
#$main_win = Gtk::Window.new( Gtk::Window::TOPLEVEL )
#$main_win.activate_focus

$main_win = Gtk::Window.new( "Micromount browser" )

# Experimenting trying to set a color so things
# don't change when the mouse moves out of the window.
# No luck yet.
###color_black  = Gdk::RGBA::new 0.0, 0.0, 0.0, 1.0
##color_black  = Gdk::RGBA::new 1.0, 0.0, 0.0, 1.0
##$main_win.override_color :normal, color_black
##$main_win.override_color :prelight, color_black
##$main_win.override_color :active, color_black
##$main_win.override_color :selected, color_black
##$main_win.override_color :insensitive, color_black

# These are dialogs that can pop up eventually
$search = Search.new $main_win
##$uno = Uno.new $main_win
$edit = Edit.new $main_win
Label.cleanup

# This holds everything
vbox = Gtk::Box.new(:vertical, 5)

# We get the box from the Nav object, then add it.
$nav = Nav.new
vbox.add $nav.box

# But we pass the box to the display object and let it add itself
$disp = Display.new vbox

$main_win.add vbox

# Load the display for the first view.
# We always start at end of the database,
#  so we start off looking at the latest additions.
$nav.show_mounts_end

#$main_win.signal_connect( 'delete_event' ) { false }
$main_win.signal_connect( "delete-event" ) { |_widget| Gtk.main_quit }
$main_win.signal_connect( 'destroy' ) { Gtk.main_quit }

$main_win.show_all

Gtk.main

puts ""
puts " -- All done"

# THE END
