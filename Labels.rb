# This was pulled from my old rails code and cleaned
#  up (a rail-ectomy) to just be nice clean ruby code.
class Label

    # delete any derelict preview files
    def Label.cleanup
	system "rm -f label_preview.ps"
	system "rm -f label_preview.png"
    end

    # This is shared by both the label preview code
    # and the actual label printing code so that we
    # get exactly the same result from both
    def Label.emit_label ( f, mount )

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

	# Decide to use smaller font for location
	# This would also allow for 5 lines!
	# small_loc = longest_loc > 19 (classic boxes)
	small_loc = longest_loc > 24

	# display up to 4 lines of location
	# if more than 4, skip 2 ...
	loc1 = loc_a[0]
	if loc_n > 3
	    loc2 = loc_a[loc_n-3]
	    loc3 = loc_a[loc_n-2]
	    loc4 = loc_a[loc_n-1]
	elsif loc_n == 3
	    loc2 = loc_a[1]
	    loc3 = loc_a[2]
	    loc4 = ""
	elsif loc_n == 2
	    loc2 = loc_a[1]
	    loc3 = ""
	    loc4 = ""
	else
	    loc2 = ""
	    loc3 = ""
	    loc4 = ""
	end

	if small_sp
	    f.puts "/Speciesfontsize 5 def"
	else
	    f.puts "/Speciesfontsize 6 def"
	end

	if small_loc
	    f.puts "/Locfontsize 4 def"
	else
	    f.puts "/Locfontsize 5 def"
	end

	# reverse order
	f.puts "(#{mount.myid})"
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
    # 2) to avoid collisions with just one name per label, I generate
    #    a unique name for each label preview file, this will build
    #    up and hog disk space (not a major concern).
    def Label.get_label ( mm )
	#basename = "label_" + mm.myid
	basename = "label_preview"
	label_ps = basename + ".ps"
	label_png = basename + ".png"

	system "rm -f #{label_ps}"
	system "rm -f #{label_png}"

	#boiler = 'label_boiler_euro.ps'
	boiler = 'boiler_euro.ps'
	#system "echo #{label_ps}"
	system "cp #{boiler} #{label_ps}"

	f = File.new label_ps, "a"

	f.puts "preview"
	Label.emit_label f, mm
	f.puts "label3 showpage"

	f.close

	# NOTE: the command pstoimg is in the Fedora package "latex2html"
	# As of 2-16-2018 pstoimg stopped working, giving the error
	# pstoimg: Error: Couldn't find pnm output of label_17-3.ps
	# the actual problem was errors in my postscript boilerplate
	# so if this happens again, the smart thing is to find the ps
	# file and run gv on it to get error messages.
	# Note also that I did not have the "rm" commands above and
	# old stale files were confusing things badly

	pstoimg = "/usr/bin/pstoimg -type png -crop a -antialias -aaliastext"
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
# For the euro boxes the label page is 8 wise and 10 tall
#
# For a while, I was printing 4 labels in a row that could hold 10
# With 4 labels in a row, this gave me 4*13 = 52 labels per sheet
#
# The label boilerplate is in /u1/rails/micromounts/minerals/label_boiler.ps
#    (Now actually /u1/rails/micromounts/minerals/label_boiler_euro.ps)
#
#   The placement of labels on the sheet is handled there.
#

# A new way to account for my faulty printer
# Make several copies of each label to
# allow for faulty printing or damage while cutting and mounting

    def Label.print

	# labels per sheet
	# max_label_count = 130 (classic boxes)
	max_label_count = 80

	# duplicate copies of each label
	repeats = 4

	#tmp_ps = Rails.root.join( 'app', 'assets', 'images', target_file )
	#boiler = Rails.root.join( 'minerals', 'label_boiler.ps' )
	tmp_ps = target_file = "label_sheet.ps"
	boiler = 'boiler.ps'
	system "cp #{boiler} #{tmp_ps}"

	f = File.new tmp_ps, "a"

	f.puts "sheet"
	first = true

#	count = Label.count
##	sheet_count = 0
#	reps.times {
#	loop {
#	    Label.find_each { |l|
#		f.puts "next_label" unless first
#		first = false
#
#		mount = Mount.find l.mount_id
#		Label.emit_label f, mount
#		f.puts "label3"
#		sheet_count += 1
#		break if sheet_count >= max_label_count
#	    }
#	    break if sheet_count >= max_label_count
#	}

	label_count = 0

	Label.find_each { |l|
	    mount = Mount.find l.mount_id
	    break if label_count + repeats >= max_label_count
	    repeats.times {
		f.puts "next_label" unless first
		first = false

		Label.emit_label f, mount
		f.puts "label3"
	    }
	    label_count += repeats
	}

	f.puts "showpage"
	f.close
    end

end
