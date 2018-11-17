'''
Created on 17 nov. 2018

@author: david
'''
from ui.buzzer import Buzzer


buz = Buzzer(3)
notes = [
    (110.0, Buzzer.E-Buzzer.S),
    (Buzzer.M, Buzzer.S)
    (110.0, Buzzer.E-Buzzer.S),
    (Buzzer.M, Buzzer.S)
    (880.0, Buzzer.Q-Buzzer.S),
    (Buzzer.M, Buzzer.H+Buzzer.S),
    
    (440.0, Buzzer.E),
    (220.0, Buzzer.E),
    (110.0, Buzzer.E+Buzzer.S),
    (Buzzer.M, Buzzer.S),
    
    (880.0, Buzzer.E),
    (220.0, Buzzer.E),
    (440.0, Buzzer.E+Buzzer.S),
    (Buzzer.M, Buzzer.S),
    (880.0, Buzzer.Q),
    (440.0, Buzzer.H+Buzzer.Q),
    ]

try:    
    for note in notes:        
        buz.playNote(note[0], note[1])

finally:
    buz.cleanup()