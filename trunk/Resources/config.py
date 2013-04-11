from pyo import *
from audio import *

### Ce fichier devrait plutot s'appeler test.py! 

s = Server().boot()

osc1 = Oscillator(wave=1).out()
#noise1 = NoiseGenerator(type=2).out()

s.gui(locals())