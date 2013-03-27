from pyo import *
from audio import *

s = Server().boot()

osc1 = Oscillator(wave=1).out()
#noise1 = NoiseGenerator(type=2).out()

s.gui(locals())