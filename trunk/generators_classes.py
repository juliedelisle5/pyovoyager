from pyo import *
from random import uniform

s = Server().boot()

class PrincipalOsc(): #Mettre PyoObject comme classe parente?
    """Principal oscillator class. The oscillator is the first sound generator of the synthesizer.
    Methods:
    A completer... """
    
    def __init__(self, wave=1, main_freq=130, finetune=0., octave=1, mul=0.5):
        #PyoObject.__init__(self)
        self.wave = wave
        self.main_freq = main_freq
        self.finetune = finetune
        self.octave = octave
        self.mul = mul
        
        #Definition des formes d'ondes
        #1-Onde sinusoidale enrichie par un petit chorus
        sinus_freq = []
        for i in range(6):
            sinus_freq.append(self.main_freq*random.uniform(1.00001,1.00003))
        print sinus_freq
        sinus = Sine(freq = sinus_freq, mul=0.07)
        #2-Onde triangulaire
        triangle_wave = LinTable(list=[(0,0.),(512,1.),(1024,0.),(1536,-1.),(2047,0)], size=2048)
        triangle = Osc(table=triangle_wave, freq=[main_freq,main_freq], mul=0.15)
        #3-Onde en dents de scie
        saw_wave = SawTable(order=30)
        sawtooth = Osc(table=saw_wave, freq=[main_freq,main_freq], mul=0.1)
        #4-onde carree standard
        square_wave = SquareTable(order=30)
        square = Osc(table=square_wave, freq=[main_freq,main_freq], mul=0.15)
        #5-Onde rectangulaire (a completer)
        #Attribut self.sound
        if wave == 1:
            self.sound = sinus
        elif wave == 2:
            self.sound = triangle
        elif wave == 3:
            self.sound = sawtooth
        elif wave == 4:
            self.sound = square
        #elif wave == 5:
            #self.sound = rectangle
        self.mix = Mix(self.sound, voices=2, mul=self.mul)
        
    def out(self): #Envoie le son aux haut-parleurs et retourne l'objet lui-meme
        self.mix.out()
        return self
        
    def getOut(self): #retourne l'objet generant du son afin de l'inclure dans une chaine de traitement
        return self.mix
        
    def setWave(self,x):
        self.wave = x
        wave_dict = {1:'sine', 2:'triangle', 3:'sawtooth', 4:'square', 5:'rectangular'} #a titre indicatif
        return self.wave
        
    def setMainFreq(self,x): #frequence de l'oscillateur principal, 130 Hz par defaut
        self.main_freq = x    
       
    def setFinetune(self,x): #ajustement fin de la frequence principale
        self.finetune = x
        
    def setOctave(self,x): #octave, 32 par defaut
        self.octave = x
        
class SecondaryOsc(): #Mettre PyoObject comme classe parente?
    """Secondary oscillator class. Depends on the principal oscillator of the synthesizer.
    Methods:
    A completer... """
    
    def __init__(self, wave=1, main_freq=130, transpo=0., octave=1, mul=0.5):
        #PyoObject.__init__(self)
        self.wave = wave
        self.main_freq = main_freq
        self.transpo = transpo
        self.octave = octave
        self.mul = mul
        
        #Definition des formes d'ondes
        #1-Onde sinusoidale enrichie par un petit chorus
        sinus_freq = []
        for i in range(6):
            sinus_freq.append(self.main_freq*random.uniform(1.00001,1.00003))
        print sinus_freq
        sinus = Sine(freq = sinus_freq, mul=0.07)
        #2-Onde triangulaire
        triangle_wave = LinTable(list=[(0,0.),(512,1.),(1024,0.),(1536,-1.),(2047,0)], size=2048)
        triangle = Osc(table=triangle_wave, freq=[main_freq,main_freq], mul=0.15)
        #3-Onde en dents de scie
        saw_wave = SawTable(order=30)
        sawtooth = Osc(table=saw_wave, freq=[main_freq,main_freq], mul=0.1)
        #4-onde carree standard
        square_wave = SquareTable(order=30)
        square = Osc(table=square_wave, freq=[main_freq,main_freq], mul=0.15)
        #5-Onde rectangulaire (a completer)
        #Attribut self.sound
        if wave == 1:
            self.sound = sinus
        elif wave == 2:
            self.sound = triangle
        elif wave == 3:
            self.sound = sawtooth
        elif wave == 4:
            self.sound = square
        #elif wave == 5:
            #self.sound = rectangle
        self.mix = Mix(self.sound, voices=2, mul=self.mul)
        
    def out(self): #Envoie le son aux haut-parleurs et retourne l'objet lui-meme
        self.mix.out()
        return self
        
    def getOut(self): #retourne l'objet generant du son afin de l'inclure dans une chaine de traitement
        return self.mix
        
    def setWave(self,x):
        self.wave = x
        wave_dict = {1:'sine', 2:'triangle', 3:'sawtooth', 4:'square', 5:'rectangular'} #a titre indicatif
        return self.wave
        
    def setMainFreq(self,x): #frequence de l'oscillateur principal, 130 Hz par defaut
        self.main_freq = x    
       
    def setTranspo(self,x): #facteur de transposition pour oscillateurs secondaires
        self.transpo = x
        
    def setOctave(self,x): #octave, 32 par defaut
        self.octave = x
        

test = PrincipalOsc().out()


#bruit blanc (non!)
white_noise = Noise(mul=[0.15,0.15]).stop()

#bruit rose (non, pas vrai!)
pink_noise = PinkNoise(mul=[0.18,0.18]).stop()

    
s.gui(locals())