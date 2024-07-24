#!/bin/python3

import os
import re
import Micros

class Labelsheet :
    #def __init__ ( self, micros ) :
    def __init__ ( self ) :
        #self.micros = micros

        self.euro = True

        # I no longer find printing duplicate labels
        # useful -- it used to be insurance against bad
        # printing by my ancient HP laserjet
        self.repeats = 1

        if self.euro :
            self.max_count = 80
            self.species_font_big = 6
            self.species_font_small = 5
            self.loc_font_big = 6
            self.loc_font_small = 5
            # ID font size is 6 in boiler
        else :
            self.max_count = 130
            self.species_font_big = 6
            self.species_font_small = 5
            self.loc_font_big = 5
            self.loc_font_small = 4
            # ID font size is 5 in boiler

        mypath = Micros.Micros.grog_path ()
        print ( "LABELS grog = ", mypath )

        if self.euro :
            self.boiler = mypath + "/" + 'boiler_euro.ps'
        else :
            self.boiler = mypath + "/" + 'boiler.ps'

    def cleanup ( self ) :
        os.system ( "rm -f label_preview.ps" )
        os.system ( "rm -f label_preview.png" )

#    def show_all ( self ) :
#        for m in self.micros :
#            print ( m )
#
#    def show ( self ) :
#        print ( len(self.micros), " generated" )
#        #self.show_all ()

    # This is shared by both the label preview code
    # and the actual label printing code so that we
    # get exactly the same result from both
    def emit_label ( self, f, mm ) :

        # Only 4 things go on label --
        # myid, species, location, associations
        hh = Micros.to_hash ( mm )

        #species1 = hh['species'].sub /^\s*/, ""
        species1 = re.sub ( r'^\s*', '', hh['species'] )
        #species1 = species1.sub /\s+.*/, ""
        species1 = re.sub ( r'\s+.*', '', species1 )

        #ass_a = hh['associations'].split ( /,\s*/ )
        ass_a = re.split ( r',\s*', hh['associations'] )
        if len(ass_a) > 0 :
            species2 = ass_a[0]
        else :
            species2 = ""

        longest_sp = len(species1)
        if len(species2) > longest_sp :
            longest_sp = len(species2)

        # The value of 16 (now 20 for euro boxes) was
        #  determined by trial and error, we can only guess
        #  if we are using a proportional font (unless we
        #  want to go to a LOT of trouble).

        # Decide to use smaller font for species
        # small_sp = longest_sp > 16 (classic)
        small_sp = longest_sp > 20

        #loc_a = hh['location'].split ( /,\s*/ )
        loc_x = re.split ( r',\s*', hh['location'] )

        # XXX
        # It might be neater to just append blank lines to
        # the array if needed, and yank lines out if we have
        # too many.
        # Also, if we decide we want the smaller font, we can
        # allow 5 lines of location, but this interacts with
        # the business of pulling lines out.

        # delete lines that begin with a "-" (ruby filter)
        #loc_x.delete_if { |l| l =~ /^\s*-/ }

        # semicolons act like sticky commas
        # i.e. they slip by the split above, then
        # we change them to commas here
        #loc_a.each { |l|
        #    l.sub! /;/, ","
        #}

        longest_loc = 0
        loc_a = []
        for l in loc_x :
            if re.match ( r'^\s*-', l ) :
                continue
            loc_a.append ( l.replace ( ';', ',' ) )
            ll = len(l)
            if ll > longest_loc :
                longest_loc = ll 

        loc_n = len(loc_a)

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

        if loc_n > 4 :
            loc2 = loc_a[loc_n-4]
            loc3 = loc_a[loc_n-3]
            loc4 = loc_a[loc_n-2]
            loc5 = loc_a[loc_n-1]
        elif loc_n == 4 :
            loc2 = loc_a[1]
            loc3 = loc_a[2]
            loc4 = loc_a[3]
            loc5 = ""
        elif loc_n == 3 :
            loc2 = loc_a[1]
            loc3 = loc_a[2]
            loc4 = ""
            loc5 = ""
        elif loc_n == 2 :
            loc2 = loc_a[1]
            loc3 = ""
            loc4 = ""
            loc5 = ""
        else :
            loc2 = ""
            loc3 = ""
            loc4 = ""
            loc5 = ""

        if small_sp :
            f.write ( f"/Speciesfontsize {self.species_font_small} def\n" )
        else :
            f.write ( f"/Speciesfontsize {self.species_font_big} def\n" )

        if small_loc :
            f.write ( f"/Locfontsize {self.loc_font_small} def\n" )
        else :
            f.write ( f"/Locfontsize {self.loc_font_big} def\n" )

        myid = hh['myid']

        # reverse order
        # Postscript needs to see strings with () around them
        f.write ( f"({myid})" )
        f.write ( f"({loc5})" )
        f.write ( f"({loc4})" )
        f.write ( f"({loc3})" )
        f.write ( f"({loc2})" )
        f.write ( f"({loc1})" )
        f.write ( f"({species2})" )
        f.write ( f"({species1})" )

    def emit_label_DEMO ( self, f, mm ) :

        small_sp = False
        small_loc = False

        if small_sp :
            f.write ( f"/Speciesfontsize {self.species_font_small} def\n" )
        else :
            f.write ( f"/Speciesfontsize {self.species_font_big} def\n" )

        if small_loc :
            f.write ( f"/Locfontsize {self.loc_font_small} def\n" )
        else :
            f.write ( f"/Locfontsize {self.loc_font_big} def\n" )

        # Postscript needs to see strings with () around them
        f.write ( "(myid)\n" )
        f.write ( "(France)\n" )
        f.write ( "(France)\n" )
        f.write ( "(France)\n" )
        f.write ( "(France)\n" )
        f.write ( "(France)\n" )
        f.write ( "(Bobs Mine)\n" )
        f.write ( "(Sulfur)\n" )
        f.write ( "(Galena)\n" )

    # Generate a label preview
    def preview ( self, mm ) :
        basename = "label_preview"
        label_ps = basename + ".ps"
        label_png = basename + ".png"

        self.cleanup ()

        #system "echo #{label_ps}"
        #os.system "cp #{boiler} #{label_ps}"
        #os.system "chmod u+w #{label_ps}"
        os.system ( f"cp {self.boiler} {label_ps}" )
        os.system ( f"chmod u+w {label_ps}" )

        with open ( label_ps, "a" ) as f:
            f.write ( "preview\n" )
            self.emit_label ( f, mm )
            f.write ( "label5 showpage\n" )

        # NOTE: the command pstoimg is in the Fedora package "latex2html"
        # As of 2-16-2018 pstoimg stopped working, giving the error
        # pstoimg: Error: Couldn't find pnm output of label_17-3.ps
        # the actual problem was errors in my postscript boilerplate
        # so if this happens again, the smart thing is to find the ps
        # file and run gv on it to get error messages.
        # Note also that I did not have the "rm" commands above and
        # old stale files were confusing things badly

        pstoimg = "/usr/bin/pstoimg -quiet -type png -crop a -antialias -aaliastext"
        #os.system ( "#{pstoimg} -out #{label_png} #{label_ps}" )
        cmd = f"{pstoimg} -out {label_png} {label_ps}"
        print ( cmd )
        os.system ( cmd )

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

    def sheet ( self, mlist ) :

        max_label_count = self.max_count

        tmp_ps = "label_sheet.ps"

        os.system ( f"cp {self.boiler} {tmp_ps}" )

        print ( f"Make sheet with {len(mlist)} labels" )

        with open ( tmp_ps, "a" ) as f:
            f.write ( "sheet\n" )

            first = True
            label_count = 0

            for mount in mlist :
                #mount = @@mdb.fetch mount_id
                if label_count + self.repeats > max_label_count :
                    break

                for _ in range ( self.repeats ) :
                    if not first :
                        f.write ( "next_label\n" )
                    first = False

                    self.emit_label ( f, mount )
                    f.write ( "label5\n" )

                label_count += self.repeats

            f.write ( "showpage\n" )

# THE END
