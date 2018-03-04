This is a database to keep track of my micromount mineral collection.
It allows me to perform various searches, but is also extremely useful
in allowing me to generate labels that go on the mineral boxes.

This began as a ruby on rails project, but rails sucks so bad and is
such a train wreck that I got fed up and changed it into a ruby based
program that I can run on my linux desktop.  This gives up the
questionable convenience of web access, but is a gigantic win in
every other way.

The database is in sqlite3, which is accessed via the sqlite3 gem.
No activerecord nonsense!  The GUI is done using gtk2.
The labels themselves are done using postscript.
