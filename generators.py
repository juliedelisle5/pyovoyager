from pyo import *
from random import uniform

s = Server().boot()

generator = 3 #determine le type de generateur

main_freq = 130

#onde sinusoidale enrichie par un petit chorus
sinus_freq = []

for i in range(6):
    sinus_freq.append(main_freq*random.uniform(0.9999,1.00001))

sinus = Sine(freq = sinus_freq, mul=0.07)

#onde carree standard
square_wave = SquareTable(order=30)
square = Osc(table=square_wave, freq=[main_freq,main_freq], mul=0.15)

#onde triangulaire
triangle_wave = LinTable(list=[(0,0.),(512,1.),(1024,0.),(1536,-1.),(2047,0)], size=2048)
triangle = Osc(table=triangle_wave, freq=[main_freq,main_freq], mul=0.15)

#onde en dents de scie
saw_wave = SawTable(order=30)
sawtooth = Osc(table=saw_wave, freq=[main_freq,main_freq], mul=0.1)

#bruit blanc (non!)
white_noise = Noise(mul=[0.15,0.15])

#bruit rose (non, pas vrai!)
pink_noise = PinkNoise(mul=[0.18,0.18])

#Condition determinant la sorte de generateur
if generator == 0: #white noise
    white_noise.out()
    pink_noise.stop()
    sinus.stop()
    square.stop()
    triangle.stop()
    sawtooth.stop()
if generator == 1: #pink noise
    white_noise.stop()
    pink_noise.out()
    sinus.stop()
    square.stop()
    triangle.stop()
    sawtooth.stop()
if generator == 2: #onde triangulaire
    white_noise.stop()
    pink_noise.stop()
    sinus.stop()
    square.stop()
    triangle.out()
    sawtooth.stop()
if generator == 3: #onde en dents de scie
    white_noise.stop()
    pink_noise.stop()
    sinus.stop()
    square.stop()
    triangle.stop()
    sawtooth.out()
if generator == 4: #onde sinusoidale
    white_noise.stop()
    pink_noise.stop()
    sinus.out()
    square.stop()
    triangle.stop()
    sawtooth.stop()
if generator == 5: #onde carree
    white_noise.stop()
    pink_noise.stop()
    sinus.stop()
    square.out()
    triangle.stop()
    sawtooth.stop()    
    
s.gui(locals())