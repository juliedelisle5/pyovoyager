from pyo import *
from random import uniform
from math import pow

s = Server(duplex=1).boot()

#On pourra aussi brancher un SfPlayer ou un Input pour respectivement utiliser
#un fichier son ou une source externe. Lors de la creation de l'interface graphique,
#on pourra prevoir un bouton pour les controler.

#Prevoir une commande Glide Rate qui permet de faire un portamento entre les frequences (a l'etape du controle MIDI?).

class Oscillator():
    """Oscillator class. The oscillator is the first sound generator of the synthesizer. 
       
        Parameters:
        -wave: Type of oscillator (1-sine, 2-triangle, 3-sawtooth, 4-square or 5-rectangular)
        -freq: Main frequency of the oscillator (in Hertz)
        -transpo: Transposition, in semi-tones (fine tune for the principal oscillator and 
                  frequency for the auxiliary oscillators.
        -octave: Octave transposition (32,16,8,4,2,1). Default is 32.
        -amp: Output amplitude, between 0 and 1. Default is 0.3.
        
        Methods:
        -out(): Envoie le son aux haut-parleurs et retourne l'objet lui-meme
        -getOut(): Retourne l'objet generant du son afin de l'inclure dans une chaine de traitement
        -setWave(): sets the wave parameter (wave)
        -setFreq(): sets the frequency parameter (freq)
        -setTranspo(): sets the transposition parameter (transpo)
        -setOctave(): sets the octave parameter (octave)
        -setAmp(): sets the amplitude parameter (amp) """
    
    def __init__(self, wave=1, freq=130, transpo=0., octave=1, amp=0.3):
        #Definition des formes d'ondes: self.sound
        
        #1-Onde sinusoidale enrichie par un petit chorus
        sinus_freq = []
        for i in range(6):
            sinus_freq.append(freq*random.uniform(1.00001,1.00003))
        sinus = Sine(freq = sinus_freq, mul=0.07)
        
        #2-Onde triangulaire
        triangle_wave = LinTable(list=[(0,0.),(512,1.),(1024,0.),(1536,-1.),(2047,0)], size=2048)
        triangle = Osc(table=triangle_wave, freq=[freq,freq], mul=0.15)
        
        #3-Onde en dents de scie
        saw_wave = SawTable(order=30)
        sawtooth = Osc(table=saw_wave, freq=[freq,freq], mul=0.1)
        
        #4-onde carree standard
        square_wave = SquareTable(order=30)
        square = Osc(table=square_wave, freq=[freq,freq], mul=0.15)
        
        #5-Onde rectangulaire
        rect_wave = LinTable(list=[(0,0.),(1,1),(127,1),(128,0),(1023,0),(1024,1),(1151,1),(1152,0),(2048,0)], size=2048)
        rectangle = Osc(table=rect_wave, freq=[freq,freq], mul=0.15)

        #Attribut self.wave
        self.wave = wave
        if wave == 1:
            self.wave = sinus
        elif wave == 2:
            self.wave = triangle
        elif wave == 3:
            self.wave = sawtooth
        elif wave == 4:
            self.wave = square
        elif wave == 5:
            self.wave = rectangle
        
        self.freq = freq
        
        self.transpo = transpo
        if transpo != 0:
            freq = freq*(pow(2.0,(transpo/12.0)))
        
        self.octave = octave
        if octave != 1:
            freq = freq*octave
        
        self.amp = amp
        
        self.mix = Mix(self.wave, voices=2, mul=self.amp)
        
    def out(self): 
        self.mix.out()
        return self
    
    def stop(self):
        self.mix.stop()
        return self
        
    def play(self):
        self.mix.play()
        return self
              
    def getOut(self):
        return self.mix
        
    def setWave(self,x):
        self.wave = x
        wave_dict = {1:'sine', 2:'triangle', 3:'sawtooth', 4:'square', 5:'rectangular'} #a titre indicatif
        return self.wave
        
    def setFreq(self,x): #frequence de l'oscillateur principal, 130 Hz par defaut
        self.freq = x
        return self.freq    
       
    def setTranspo(self,x):
        self.transpo = x
        return self.transpo
        
    def setOctave(self,x): #octave, 32 par defaut
        self.octave = x
        return self.octave
        
    def setAmp(self,x):
        self.amp = x
        return self.amp
        
        
class NoiseGenerator():
    
    def __init__(self, type=1, amp=0.3):
        self.type = type
        self.amp = amp
        
        #bruit blanc (non!)
        white_noise = Noise(mul=[0.15,0.15])
        #bruit rose (non, pas vrai!)
        pink_noise = PinkNoise(mul=[0.18,0.18])
        if type == 1:
            self.noise = white_noise
        if type == 2:
            self.noise = pink_noise
            
        self.mix = Mix(self.noise, voices=2, mul=self.amp)
        
    def out(self): #Envoie le son aux haut-parleurs et retourne l'objet lui-meme
        self.mix.out()
        return self
            
    def stop(self):
        self.mix.stop()
        return self
        
    def play(self):
        self.mix.play()
        return self
        
    def getOut(self): #retourne l'objet generant du son afin de l'inclure dans une chaine de traitement
        return self.mix
        
    def setAmp(self,x):
        self.amp = x
        return self.amp

    def setType(self,x):
        self.type = x
        return self.type
        
class Filter(): #Voir si un panning individuel pour chaque filtre est possible (surement!).
#Voir pourquoi on me dit que l'objet Filter n'a pas d'attribut out.
#Ajouter les attributs et methodes pour pouvoir lire l'enveloppe ADSR modulant la frequence de coupure (Amount to Filter).
    
    def __init__(self, input, mode=1, cutoff=5000, spacing=0, resonance=5):
        self.mode = mode
        self.input = input
        self.cutoff = cutoff
        self.spacing = spacing #Entre -2 et 2. Indique le nombre d'octaves entre les deux frequences de coupure.
        
        self.freq1 = cutoff - (cutoff*pow(2,spacing))
        self.freq2 = cutoff + (cutoff*pow(2,spacing))
        self.resonance = resonance
        self.q = resonance*50 + 1 #Resonance se situant entre 0 et 10, on vise un facteur Q entre 1 et 500.
        
        if mode == 1: # dual lowpass
            self.filter1 = Biquadx(self.input, freq=self.freq1, q=self.q, type=0, stages=4, mul=0.6, add=0)
            self.filter2 = Biquadx(self.input, freq=self.freq2, q=self.q, type=0, stages=4, mul=0.6, add=0)
        elif mode == 2: #lowpass/highpass
            self.filter1 = Biquadx(self.input, freq=self.freq1, q=self.q, type=0, stages=4, mul=0.6, add=0)
            self.filter2 = Biquadx(self.input, freq=self.freq2, q=self.q, type=0, stages=4, mul=0.6, add=0)
        
        self.mix = Mixer(mul=0.8)
        self.mix.addInput(1,self.filter1)
        self.mix.addInput(2,self.filter2)
        
        def out(self): #Envoie le son aux haut-parleurs et retourne l'objet lui-meme
            self.mix.out()
            return self

        def stop(self):
            self.mix.stop()
            return self

        def play(self):
            self.mix.play()
            return self

        def getOut(self): #retourne l'objet generant du son afin de l'inclure dans une chaine de traitement
            return self.mix
            
        def setMode(self,x):
            self.mode = x
            return self.mode
            
        def sefInput(self,input):
            self.input = input
            return self.input
            
        def setCutoff(self,x):
            self.cutoff = x
            return self.cutoff
        
        def setSpacing(self,x):
            self.spacing = x
            return self.spacing
            
        def setResonance(self,x):
            self.resonance = x
            return self.resonance 
            

class ADSR():
    
    def __init__(self, ):
        

#sinus = Sine(freq=442, mul=0.8)
#src = Oscillator(wave=1)
#filtre = Filter(sinus).out()
#test2 = NoiseGenerator(type=2).out()
s.gui(locals())