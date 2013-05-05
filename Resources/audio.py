from pyo import *
from random import uniform
from math import pow

#Mettre l'attribut wave a une valeur entre 0 et 1 (float) par defaut et essayer ensuite avec les tables.

#Premiere evaluation:
### Tres bien! En priorite selon moi:
### 1 - Faire les connections entre les oscillateurs
### 2 - Le controle des notes en midi
### 
### Le tout peut etre controle en argument et en appels de methode
### Ce qui rend l'interface graphique secondaire (du moins pour le 
### projet dans le cadre du cours!)
### 19/20



"""
A faire prochainement:

-Classe pour le mixeur qui recevra les differentes combinaisons d'oscillateurs et de generateurs de bruit.
-Osc 1-2 sync : avec un objet OscTrig et un objet Metro qui est regle a la vitesse de l'oscillateur 1.
-Osc 3-1 FM : calculer le rapport modulante/porteuse et faire la transition osc3.amp-->frequence en Hertz
-Commande Glide Rate qui permet de faire un portamento entre les frequences.
-Prevoir l'option SfPlayer/External Input pour une source sonore supplementaire.

-Creer une classe ADSR
-Faire en sorte que l'amplitude de sortie et la frequence de coupure des filtres puisse etre controlee
 par une enveloppe ADSR ; declenchement des sons par un trig. *Tenir compte du parametre "amount to filter".
 
-Generer des formes d'onde intermediaires a partir des formes d'onde de base. Modifier le dictionnaire en consequence.

-Modifier les methodes setParametre et utiliser l'autre facon de faire avec des @

-Rediger des docstrings decents.
"""

class Oscillator(): 
    """Oscillator class. The oscillator is the first sound generator of the synthesizer. 
       
        Parameters:
        -wave: Type of oscillator (1-sine, 2-triangle, 3-sawtooth, 4-square or 5-rectangular)
        -freq: Main frequency of the oscillator (in Hertz - float).
        -transpo: Transposition, in semi-tones (fine tune for the principal oscillator and 
                  frequency for the auxiliary oscillators (float).
        -octave: Octave transposition (32,16,8,4,2,1). Default is 32.
        -lfo: 0.=normal mode, 1.=LFO mode (float)
        -amp: Output amplitude, between 0 and 1. Default is 0.3.
        
        Methods:
        -out(): Envoie le son aux haut-parleurs et retourne l'objet lui-meme
        -getOut(): Retourne l'objet generant du son afin de l'inclure dans une chaine de traitement
        -setWave(): sets the wave parameter (wave)
        -setFreq(): sets the frequency parameter (freq)
        -setTranspo(): sets the transposition parameter (transpo)
        -setOctave(): sets the octave parameter (octave)
        -setLFO(): sets the LFO mode : 0.=normal, 1.=LFO (4 octaves below the principal frequency)
        -setAmp(): sets the amplitude parameter (amp) """
    
    def __init__(self, wave=0., freq=130., transpo=0., octave=1., lfo=0., glide=0.005, amp=0.2):
        self.transpo = Sig(value=(Pow(base=2.0, exponent=(transpo/12.0), mul=1.))) 
        self.octave = Sig(octave) #En realite, la valeur de self.octave sera comprise entre 1 et 6 (valeurs discretes en float).
        self.lfo = Sig(value=(Pow(base=2.0, exponent=(lfo*4.), mul=1.))) #LFO: 0 pour mode normal, 1 pour mode LFO.
        self.amp = Sig(amp)
        self.freq = Sig(value=freq*(Pow(base=2.0, exponent=self.octave-2.))*self.transpo/self.lfo)
        self.glide = glide
        self.freq_interp = Port(input=self.freq, risetime = self.glide)
        
        #1-Onde sinusoidale creee a l'aide d'une HannTable
        self.sine_wave = HarmTable(size=2048)
        
        #2-Onde triangulaire
        self.triangle_wave = LinTable(list=[(0,0.),(512,1.),(1024,0.),(1536,-1.),(2047,0)], size=2048)
        
        #3-Onde en dents de scie
        self.saw_wave = SawTable(order=30)
        
        #4-onde carree standard
        self.square_wave = SquareTable(order=30)
        
        #5-Onde rectangulaire
        self.rect_wave = LinTable(list=[(0,0.),(1,1),(127,1),(128,0),(1023,0),(1152,0),(2048,0)], size=2048) #(1024,1),(1151,1),-->donne l'octave
        
        self.wave = Sig(value=wave) #Sine(.1, mul=.5, add=.5) #Attribut de l'objet, valeur en float entre 0. et 1.
        self.newTable = NewTable(length=2048./44100., chnls=1)
        self.table = TableMorph(input=self.wave, table=self.newTable, sources=[self.sine_wave, self.triangle_wave, self.saw_wave, self.square_wave, self.rect_wave]) #
        #self.newTable.view()
        self.osc = Osc(table=self.newTable, freq=self.freq_interp, mul=0.2).play()
        
        self.mix = Mix(self.osc, voices=2, mul=self.amp)
        
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
        
    def setWave(self,x): #A ajuster
        self.wave.value = x
        
    def setFreq(self,x): #frequence de l'oscillateur principal, 130 Hz par defaut
        self.freq.value = x   
       
    def setTranspo(self,x):
        self.transpo.value = Pow(base=2.0,exponent=(x/12.0), mul=1.)
        
    def setOctave(self,x): #octave, 32 par defaut (note la plus grave, comme les tuyaux d'orgue)
        self.octave.value = x
        
    def setLFO(self,x):
        self.lfo.value = Pow(base=2.0, exponent=(x*4.), mul=1.)
        
    def setAmp(self,x):
        self.amp.value = x
        
    def setGlide(self,x):  #---> Pour le Glide rate: ajoute le temps de portamento.
        self.freq_interp.risetime=x;
        
        
class NoiseGenerator():
    
    def __init__(self, noise=1, amp=0.3):
        
        self.amp = Sig(amp)
        self.last_noise = noise
        
        #bruit blanc
        self.white = Noise(mul=[0.15,0.15]).stop()
        #bruit rose
        self.pink = PinkNoise(mul=[0.18,0.18]).stop()
        #bruit brun
        self.brown = BrownNoise(mul=[0.2,0.2]).stop()
            
        noise_dict = {1:self.white, 2:self.pink, 3:self.brown}
        noise_dict[noise].play() #Appel du generateur de bruit choisi
        self.noise = Sig(noise_dict[noise])
            
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
        self.amp.value = x

    def setNoise(self,x):
        noise_dict = {1:self.white, 2:self.pink, 3:self.brown}
        noise_dict[self.last_noise].stop()
        noise_dict[x].play()
        self.noise.value = noise_dict[x]
        self.last_noise = x

        
class Filter(): #Le changement d'input fait planter le programme. (Il ne devrait pas y en avoir de toute facon, mais on ne sait jamais.)
    
    def __init__(self, input, filter_mode=1, cutoff=500., spacing=0, resonance=1., pan_mode=1, amp=0.8):
        self.filter_mode = Sig(value=filter_mode)
        #self.input = Sig(value=input, mul=[1.,1.]) -->vieille version
        self.input = input
        self.in_fader = InputFader(self.input)
        self.cutoff = Sig(value=cutoff)
        self.spacing = Sig(value=spacing) #Entre -3 et 3 (float). Indique le nombre d'octaves entre les deux frequences de coupure.
        
        self.freq1 = Sig(value=(self.cutoff*Pow(base=2.,exponent=-1.*self.spacing))) #a repenser
        self.freq2 = Sig(value=(self.cutoff*Pow(base=2.,exponent=self.spacing)))
        self.resonance = Sig(value=resonance)
        self.q = Sig(value=(self.resonance*4.99 + 1.)) #Resonance se situant entre 0 et 10, on vise un facteur Q entre 1 et 500.

        if filter_mode == 1: # dual lowpass
            self.filter1 = Biquadx(self.in_fader, freq=self.freq1, q=self.q, type=0, stages=2, mul=0.6, add=0) #self.in_fader
            self.filter2 = Biquadx(self.in_fader, freq=self.freq2, q=self.q, type=0, stages=2, mul=0.6, add=0) #self.in_fader
        elif filter_mode == 2: #lowpass/highpass
            self.filter1 = Biquadx(self.in_fader, freq=self.freq1, q=self.q, type=0, stages=2, mul=0.6, add=0) #self.in_fader
            self.filter2 = Biquadx(self.in_fader, freq=self.freq2, q=self.q, type=1, stages=2, mul=0.6, add=0) #self.in_fader
        
        pan_dict1 = {1:0.5, 2:0., 3:1., 4:0.} #1=50% de chaque cote; 2=filtre 1 a gauche, filtre 2 a droite
        pan_dict2 = {1:0.5, 2:1., 3:0., 4:0.} #3=filtre 1 a droite, filtre 2 a gauche, 4=mono (gauche)
        self.pan1 = SigTo(value=pan_dict1[pan_mode])
        self.pan2 = SigTo(value=pan_dict2[pan_mode])
        self.amp = Sig(value=amp)
        self.filter1_pan = SPan(input=self.filter1.mix(1), outs=2, pan=self.pan1, mul=self.amp)
        self.filter2_pan = SPan(input=self.filter2.mix(1), outs=2, pan=self.pan2, mul=self.amp)
        
        ### L'InputFader devrait etre au debut de la classe et recevoir directement l'arguement "input".
        ### Il pourrait remplacer l'objet Sig en self.input... ---> Cause un bogue. A regler!
        
        
    def setInput(self, x, fadetime=0.05):
        self.input = x
        self.in_fader.setInput(x, fadetime)
    
    def out(self): #Envoie le son aux haut-parleurs et retourne l'objet lui-meme
        self.filter1_pan.out()
        self.filter2_pan.out()
        return self   

    def stop(self):
        self.filter1_pan.stop()
        self.filter2_pan.stop()
        return self

    def play(self):
        self.filter1_pan.play()
        self.filter2_pan.play()
        return self
        
    def setFilter_mode(self,x):
        self.filter_mode.value = x
        
    def setCutoff(self,x):
        self.cutoff.value = x
        
    def setSpacing(self,x):
        self.spacing.value = x
            
    def setResonance(self,x):
        self.resonance.value = x
    
    def setPan_mode(self,x):
        pan_dict1 = {1:0.5, 2:0., 3:1., 4:0.} #1=50% de chaque cote; 2=filtre 1 a gauche, filtre 2 a droite
        pan_dict2 = {1:0.5, 2:1., 3:0., 4:0.} #3=filtre 1 a droite, filtre 2 a gauche, 4=mono (gauche)
        self.pan1.value = pan_dict1[x]
        self.pan2.value = pan_dict2[x]
    
    def setAmp(self,x):
        self.amp.value = x
#Fin de la classe filtre

if __name__ == '__main__':
    s = Server().boot()
    
    src1 = Oscillator(wave=1.,octave=1., lfo=0.).play()
    src2 = Oscillator(wave=1.,octave=2., lfo=0.).stop()
    bruit = NoiseGenerator().stop()
    filtre = Filter(src1.getOut(), amp=0.1).out()

    s.gui(locals())