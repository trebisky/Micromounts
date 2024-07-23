This is a database to keep track of my micromount mineral collection.

This directory holds the old ruby GUI.  It worked fine until the
Ruby gem system got hopelessy tangled up on my Fedora 40 system.

This led me to recoding everything in Python in July of 2024.

I don't like the Python language as well as Ruby, but I do like
stable software.  There were always endless problems with the
Ruby gem system.  Some people use Ruby version managers, but the
very need to do such a thing flags a severe issue in itself.

This code only uses two gems: sqlite3 and gtk3.

This actually began as a ruby on rails project, but rails sucks
so bad and is such a train wreck that I got fed up and changed it
into this ruby based program that I can run on my linux desktop.
This gave up the questionable convenience of web access,
but is a gigantic win in every other way.

The database is in sqlite3, which is accessed via the sqlite3 gem.
No activerecord nonsense!  The GUI is done using gtk3.
The labels themselves are done using postscript.
