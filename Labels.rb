# Tom Trebisky 2-23-2019
#
# This file contains two classes.
# Labelstore holds the list of what mounts
#  we want to make labels from.
# Labelsheet deals with making postscript labels,
#  both single images for preview, and
#  entire sheets of labels to be printed.
#  (I no longer call it Label to be distinct from Gtk::Label)

# Labelstore --------------
# The old rails code used a "labels" table in the database.
# This allows the selections to be persistent.
# The schema has an id field (never used) along
# with created_at and updated_at fields (never used).
# All we really want and need is "mount_id".
# The rest are artifacts of the rails days
# 
# A simple and lazy (but non-persistent) approach
# is to just use a ruby array of mount_id
# The old rails code had Label inherit from ActiveRecord,
# which yielded the method "find_each"

class Labelstore
    def initialize ( mdb )
        @store = Array.new
	@mdb = mdb
    end

    def clear
        @store.clear
    end

    def count
	return @store.size
    end

    def debug
	@store.each { |m|
	    mm = @mdb.fetch m
	    print "Label for: " + m.to_s + " " + mm.myid + "\n"
	}
    end

    def add_mount ( m_id )
        @store << m_id
	#debug
    end

    def remove_mount ( m_id )
        @store.delete m_id
	#debug
    end

    def each
        @store.each { |m|
            yield m
        }
    end
end

# This was pulled from my old rails code and cleaned
#  up (a rail-ectomy) to just be nice clean ruby code.
# This only has class methods

class Labelsheet

    def initialize ( store, mdb )
	@@store = store
	@@mdb = mdb

	# duplicate copies of each label
        @@repeats = 4

        # We have this switch, but a lot of the Euro specific
        # code is wired in, so this is only a suggestion,
        # and I don't ever expect it to be anything but true.
	@@euro = true

        if @@euro
          @@species_font_big = 6
          @@species_font_small = 5
          @@loc_font_big = 6
          @@loc_font_small = 5
          # ID font size is 6 in boiler
        else
          @@species_font_big = 6
          @@species_font_small = 5
          @@loc_font_big = 5
          @@loc_font_small = 4
          # ID font size is 5 in boiler
        end
    end

    def repeats ( val )
        @@repeats = val
    end

    # delete any derelict preview files
    def Labelsheet.cleanup
	system "rm -f label_preview.ps"
	system "rm -f label_preview.png"
    end

    # This is shared by both the label preview code
    # and the actual label printing code so that we
    # get exactly the same result from both
    def Labelsheet.emit_label ( f, mount )

	species1 = mount.species.sub /^\s*/, ""
	species1 = species1.sub /\s+.*/, ""

	ass_a = mount.associations.split /,\s*/
	if ass_a.size > 0
	    species2 = ass_a[0]
	else
	    species2 = ""
	end

	longest_sp = species1.size
	longest_sp = species2.size if species2.size > longest_sp

        # The value of 16 (now 20 for euro boxes) was
        #  determined by trial and error, we can only guess
        #  if we are using a proportional font (unless we
        #  want to go to a LOT of trouble).

	# Decide to use smaller font for species
	# small_sp = longest_sp > 16 (classic)
	small_sp = longest_sp > 20

	loc_a = mount.location.split /,\s*/

	# XXX
	# It might be neater to just append blank lines to
	# the array if needed, and yank lines out if we have
	# too many.
	# Also, if we decide we want the smaller font, we can
	# allow 5 lines of location, but this interacts with
	# the business of pulling lines out.

	# delete lines that begin with a "-"
	loc_a.delete_if { |l| l =~ /^\s*-/ }

	# semicolons act like sticky commas
	longest_loc = 0
	loc_a.each { |l|
	    l.sub! /;/, ","
	    ll = l.size
	    longest_loc = ll if ll > longest_loc
	}
	loc_n = loc_a.size

        # The value of 19 was right with a smaller loc font
        #  and the classic boxes.  But for euro boxes, we use the
        #  same font for loc as for species, so 20 will be right here.

	# Decide to use smaller font for location
	# This would also allow for 5 lines!
	# small_loc = longest_loc > 19 (classic boxes)
	# small_loc = longest_loc > 24 (euro with smaller font)
	small_loc = longest_loc > 20

        # We can handle 5 location lines with euro box labels!
        # (classic labels could only have 4)
	# display up to 4 lines of location
	# if more than 4, skip 2 ...
	loc1 = loc_a[0]
	if loc_n > 4
	    loc2 = loc_a[loc_n-4]
	    loc3 = loc_a[loc_n-3]
	    loc4 = loc_a[loc_n-2]
	    loc5 = loc_a[loc_n-1]
	elsif loc_n == 4
	    loc2 = loc_a[1]
	    loc3 = loc_a[2]
	    loc4 = loc_a[3]
	    loc5 = ""
	elsif loc_n == 3
	    loc2 = loc_a[1]
	    loc3 = loc_a[2]
	    loc4 = ""
	    loc5 = ""
	elsif loc_n == 2
	    loc2 = loc_a[1]
	    loc3 = ""
	    loc4 = ""
	    loc5 = ""
	else
	    loc2 = ""
	    loc3 = ""
	    loc4 = ""
	    loc5 = ""
	end

	if small_sp
	    f.puts "/Speciesfontsize #{@@species_font_small} def"
	else
	    f.puts "/Speciesfontsize #{@@species_font_big} def"
	end

	if small_loc
	    f.puts "/Locfontsize #{@@loc_font_small} def"
	else
	    f.puts "/Locfontsize #{@@loc_font_big} def"
	end

	# reverse order
	f.puts "(#{mount.myid})"
	f.puts "(#{loc5})"
	f.puts "(#{loc4})"
	f.puts "(#{loc3})"
	f.puts "(#{loc2})"
	f.puts "(#{loc1})"
	f.puts "(#{species2})"
	f.puts "(#{species1})"
    end

    # Generate a label preview
    # There are some problems with this:
    # 1) the assets/images directory must be writeable by apache
    # 2) to avoid collisions with just one name per label,
    #    in the rails version I generated
    #    a unique name for each label preview file,
    #    this would build up and hog disk space.
    #     (not a major concern).
    #    The new rails free version uses a single filename.
    def Labelsheet.get_label ( mm )
	#basename = "label_" + mm.myid
	basename = "label_preview"
	label_ps = basename + ".ps"
	label_png = basename + ".png"

	system "rm -f #{label_ps}"
	system "rm -f #{label_png}"

	if @@euro
	    boiler = 'boiler_euro.ps'
	else
	    boiler = 'boiler.ps'
	end
	#system "echo #{label_ps}"
	system "cp #{boiler} #{label_ps}"
	system "chmod u+w #{label_ps}"

	f = File.new label_ps, "a"

	f.puts "preview"
	Labelsheet.emit_label f, mm
	f.puts "label5 showpage"

	f.close

	# NOTE: the command pstoimg is in the Fedora package "latex2html"
	# As of 2-16-2018 pstoimg stopped working, giving the error
	# pstoimg: Error: Couldn't find pnm output of label_17-3.ps
	# the actual problem was errors in my postscript boilerplate
	# so if this happens again, the smart thing is to find the ps
	# file and run gv on it to get error messages.
	# Note also that I did not have the "rm" commands above and
	# old stale files were confusing things badly

	pstoimg = "/usr/bin/pstoimg -quiet -type png -crop a -antialias -aaliastext"
	system "#{pstoimg} -out #{label_png} #{label_ps}"

	# This is unfinished and undebugged
	# 2-16-2018, play fast and loose using one file.
	#target_pnm = "label_pnm"
	#pnm = target_pnm
	#
	#pstopnm = "/usr/bin/pstopnm"
	#pnmtopng = "/usr/bin/pnmtopng"
	#system "#{pstopnm} #{label_ps} #{pnm}"
	#system "#{pnmtopng} #{pnm} #{dst}"

	return label_png
    end

# For classic boxes the label page is 10 wide and 13 tall
#   ( One sheet can hold 130 labels )
# For the euro boxes the label page is 8 wide and 10 tall
#   ( One sheet can hold 80 labels )
#
# For a while, I was printing 4 labels in a row that could hold 10
# With 4 labels in a row, this gave me 4*13 = 52 labels per sheet
#
# The label boilerplate is in /u1/rails/micromounts/minerals/label_boiler.ps
#    (Now actually /u1/rails/micromounts/minerals/label_boiler_euro.ps)
#
#   The placement of labels on the sheet is handled there.

# A new way to account for my faulty printer
# Make several copies of each label to
# allow for faulty printing or damage while cutting and mounting

    def Labelsheet.print

	# labels per sheet
	# max_label_count = 130 (classic boxes)
	max_label_count = 80

	tmp_ps = target_file = "label_sheet.ps"
	if @@euro
	    boiler = 'boiler_euro.ps'
	else
	    boiler = 'boiler.ps'
	end
	system "cp #{boiler} #{tmp_ps}"

	f = File.new tmp_ps, "a"

	f.puts "sheet"
	first = true

#	count = Labelsheet.count
##	sheet_count = 0
#	reps.times {
#	loop {
#	    Labelsheet.find_each { |l|
#		f.puts "next_label" unless first
#		first = false
#
#		mount = Mount.find l.mount_id
#		Labelsheet.emit_label f, mount
#		f.puts "label4"
#		sheet_count += 1
#		break if sheet_count >= max_label_count
#	    }
#	    break if sheet_count >= max_label_count
#	}

	label_count = 0

	@@store.each { |mount_id|
	    mount = @@mdb.fetch mount_id
	    break if label_count + @@repeats >= max_label_count
	    @@repeats.times {
		f.puts "next_label" unless first
		first = false

		Labelsheet.emit_label f, mount
		f.puts "label5"
	    }
	    label_count += @@repeats
	}

	f.puts "showpage"
	f.close
    end

end
