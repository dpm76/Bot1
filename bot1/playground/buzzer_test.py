'''
Created on 17 nov. 2018

@author: david
'''
from ui.buzzer import Buzzer


buz = Buzzer(3)
notes = [
    (Buzzer.A2, Buzzer.E-Buzzer.S),
    (Buzzer.M, Buzzer.S),
    (Buzzer.A2, Buzzer.E-Buzzer.S),
    (Buzzer.M, Buzzer.S),
    (Buzzer.A5, Buzzer.Q-Buzzer.S),
    (Buzzer.M, Buzzer.H+Buzzer.S),
    
    (Buzzer.A4, Buzzer.E),
    (Buzzer.A3, Buzzer.E),
    (Buzzer.A2, Buzzer.E+Buzzer.S),
    (Buzzer.M, Buzzer.S),
    
    (Buzzer.A5, Buzzer.E),
    (Buzzer.A3, Buzzer.E),
    (Buzzer.A4, Buzzer.E+Buzzer.S),
    (Buzzer.M, Buzzer.S),
    
    (Buzzer.A5, Buzzer.Q),
    (Buzzer.A4, Buzzer.H+Buzzer.Q)
    ]

try:    
    for note in notes:        
        buz.playNote(note[0], note[1])

finally:
    buz.cleanup()