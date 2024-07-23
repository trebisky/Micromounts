#!/bin/python3

class Labelsheet :
    def __init__ ( self, micros ) :
        self.micros = micros

    def show ( self ) :
        print ( len(self.micros), " generated" )
        for m in self.micros :
            print ( m )

# THE END
