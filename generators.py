from pyo import *
from random import uniform

s = Server().boot()

generator = 3

main_freq = 442
sinus_freq = []
square_freq = []
square_amps = []

#onde sinusoidale enrichie par un petit chorus
for i in range(6):
    sinus_freq.append(main_freq*random.uniform(0.9999,1.00001))

sinus = Sine(freq = sinus_freq, mul=0.07)

#onde carree standard (l'aigu est un peu agressant pour le moment)
for i in range(1,21):
    square_freq.append(main_freq*(2*i-1))
    square_amps.append(0.1/(2.0*i-1.0))
    
square = Sine(freq=square_freq, mul=square_amps)

#bruit blanc (non!)
white_noise = Noise(mul=[0.2,0.2])

#bruit rose (non, pas vrai!)
pink_noise = PinkNoise(mul=[0.2,0.2])

#Condition determinant la sorte de generateur
if generator == 0:
    white_noise.out()

if generator == 1:
    pink_noise.out()

if generator == 2:
    sinus.out()
    
if generator == 3:
    square.out()
s.gui(locals())