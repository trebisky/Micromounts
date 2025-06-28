This is a database to keep track of my micromount mineral collection.
It allows me to perform various searches, but is also extremely useful
in allowing me to generate labels that go on the mineral boxes.

It requires the pstoimg package, which has many dependencies
(most of TeX) on Fedora

Up until July, 2024 this was a ruby based project.
Then ruby gems got into some nasty tangle that I could never fix.
I only used two gems (sqlite3 and gtk3), but I gave up and in July
2024 got busy rewriting this in Python.

Hence, there are now both ruby and python directories, with all new
development being done in the python directory.

The database itself is in sqlite3.
The python (or ruby) code are a GUI that allows searches,
additions, and changes to be made to the database.
The labels themselves are done using postscript.
