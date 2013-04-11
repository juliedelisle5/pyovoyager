from pyo import *
from random import uniform
from math import pow

### Tres bien! En priorite selon moi:
### 1 - Faire les connections entre les oscillateurs
### 2 - Le controle des notes en midi
### 
### Le tout peut etre controle en argument et en appels de methode
### Ce qui rend l'interface graphique secondaire (du moins pour le 
### projet dans le cadre du cours!)
### 19/20


s = Server().boot()

"""
A faire prochainement:

-Classe pour le mixeur qui recevra les differentes combinaisons d'oscillateurs et de generateurs de bruit.
-Osc 1-2 sync : avec un objet OscTrig et un objet Metro qui est regle a la vitesse de l'oscillateur 1.
-Osc 3-1 FM : calculer le rapport modulante/porteuse et faire la transition osc3.amp-->frequence en Hertz
-Commande Glide Rate qui permet de faire un portamento entre les frequences.
-Prevoir l'option SfPlayer/External Input pour une source sonore supplementaire.

-Prevoir plusieurs options de pan pour les filtres: un filtre de chaque cote, ou les 2 filtres repartis entre les 2 cotes.
-Creer une classe ADSR
-Faire en sorte que l'amplitude de sortie et la frequence de coupure des filtres puisse etre controlee
 par une enveloppe ADSR ; declenchement des sons par un trig. *Tenir compte du parametre "amount to filter".
 
-Generer des formes d'onde intermediaires a partir des formes d'onde de base. Modifier le dictionnaire en consequence.

-Modifier les methodes setParametre et utiliser l'autre facon de faire avec des @

-Eventuellement, faire heriter ces objets de la classe parente PyoObject (assez complique et pas prioritaire)
"""
#On pourra aussi brancher un SfPlayer ou un Input pour respectivement utiliser
#un fichier son ou une source externe. Lors de la creation de l'interface graphique,
#on pourra prevoir un bouton pour les controler.

class Oscillator(): #Utiliser la methode getFreq pour la synthese FM
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
    
    def __init__(self, wave=1, freq=130., transpo=0., octave=1., lfo=0., amp=0.3):
        #PyoObject.__init__(self) (si on rajoute la classe parente. La donner en argument a la classe egalement)
        self.transpo = Sig(value=(Pow(base=2.0, exponent=(transpo/12.0), mul=1.)), mul=[1.,1.]) 
        self.octave = Sig(octave, mul=[1.,1.]) #En realite, la valeur de self.octave sera comprise entre 1 et 6 (valeurs discretes en float).
        self.lfo = Sig(value=(Pow(base=2.0, exponent=(lfo*4.), mul=1.)), mul=[1.,1.]) #LFO: 0 pour mode normal, 1 pour mode LFO.
        self.amp = Sig(amp, mul=[1.,1.])
        self.freq = Sig(freq*self.octave*self.transpo/self.lfo, mul=[1.,1.])
        
        ### Tous les oscillateurs devraient etre a .stop() dans l'__init__, sauf la wave choisie.
        ### Dans la methode setWave, tu pourrais allumer celle choisie et eteindre l'ancienne.
        ### Economie de CPU (surtout qu'il y a plusieurs oscillateurs) (voir setWave)
        ### Garde la wave courante en memoire
        self.last_wave = wave

        #1-Onde sinusoidale enrichie par un petit chorus
        sinus_freq = []
        for i in range(6):
            sinus_freq.append(self.freq*random.uniform(1.00001,1.00003))
        self.sinus = Sine(freq = sinus_freq, mul=0.07)
        
        #2-Onde triangulaire
        triangle_wave = LinTable(list=[(0,0.),(512,1.),(1024,0.),(1536,-1.),(2047,0)], size=2048)
        self.triangle = Osc(table=triangle_wave, freq=[self.freq,self.freq], mul=0.15)
        
        #3-Onde en dents de scie
        saw_wave = SawTable(order=30)
        self.sawtooth = Osc(table=saw_wave, freq=[self.freq,self.freq], mul=0.1)
        
        #4-onde carree standard
        square_wave = SquareTable(order=30)
        self.square = Osc(table=square_wave, freq=[self.freq,self.freq], mul=0.15)
        
        #5-Onde rectangulaire
        rect_wave = LinTable(list=[(0,0.),(1,1),(127,1),(128,0),(1023,0),(1024,1),(1151,1),(1152,0),(2048,0)], size=2048)
        self.rectangle = Osc(table=rect_wave, freq=[self.freq,self.freq], mul=0.15)
        
        wave_dict = {1:self.sinus, 2:self.triangle, 3:self.sawtooth, 4:self.square, 5:self.rectangle}
        self.wave = Sig(wave_dict[wave], mul=[1,1]) #Sig(wave, mul=[1,1])
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
        wave_dict = {1:self.sinus, 2:self.triangle, 3:self.sawtooth, 4:self.square, 5:self.rectangle}
        ### stop l'ancienne
        wave_dict[self.last_wave].stop()
        ### demarre la nouvelle
        wave_dict[x].play()
        
        self.wave.value = wave_dict[x]
        
        ### remplace la reference a la wave courante
        self.last_wave = x

        
    def setFreq(self,x): #frequence de l'oscillateur principal, 130 Hz par defaut
        self.freq.value = x   
       
    def setTranspo(self,x): # a changer pour faire le calcul direct
        self.transpo.value = Pow(base=2.0,exponent=(x/12.0), mul=1.)
        
    def setOctave(self,x): #octave, 32 par defaut (note la plus grave)
        self.octave.value = x
        
    def setLFO(self,x):
        self.lfo.value = Pow(base=2.0, exponent=(x*4.), mul=1.)
        
    def setAmp(self,x):
        self.amp.value = x
        
        
class NoiseGenerator():
    
    def __init__(self, noise=1, amp=0.3):
        
        self.amp = Sig(amp, mul=[1.,1.])
        
        ### Meme chose que pour les waves (stop pour tous sauf le bruit qui joue).
        #bruit blanc
        self.white = Noise(mul=[0.15,0.15])
        #bruit rose
        self.pink = PinkNoise(mul=[0.18,0.18])
        #bruit brun
        self.brown = BrownNoise(mul=[0.2,0.2])
            
        noise_dict = {1:self.white, 2:self.pink, 3:self.brown}
        self.noise = Sig(noise_dict[noise], mul=[1,1])
            
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
        self.noise.value = noise_dict[x]
        
        
class Filter():
    
    def __init__(self, input, filter_mode=1, cutoff=500., spacing=0., resonance=1., pan_mode=1, amp=0.8):
        self.filter_mode = Sig(value=filter_mode, mul=[1.,1.])
        self.input = Sig(value=input, mul=[1.,1.])  #L'input sera eventuellement le Mixer qui rassemblera toutes les voix des oscillateurs.
        #Probleme : l'input doit etre un PyoObject. Faudra que l'objet de la classe du mixeur en soit un.
        self.cutoff = Sig(value=cutoff, mul=[1.,1.])
        self.spacing = Sig(value=spacing, mul=[1.,1.]) #Entre -2 et 2 (float). Indique le nombre d'octaves entre les deux frequences de coupure.
        
        self.freq1 = Sig(value=(self.cutoff - (self.cutoff*Pow(base=2.,exponent=self.spacing, mul=1.))), mul=[1.,1.])
        self.freq2 = Sig(value=(self.cutoff + (self.cutoff*Pow(2.,exponent=self.spacing, mul=1.))), mul=[1.,1.])
        self.resonance = Sig(value=resonance, mul=[1.,1.])
        self.q = Sig(value=(self.resonance*49.9 + 1.), mul=[1.,1.]) #Resonance se situant entre 0 et 10, on vise un facteur Q entre 1 et 500.

        if filter_mode == 1: # dual lowpass
            self.filter1 = Biquadx(self.input, freq=self.freq1, q=self.q, type=0, stages=2, mul=0.6, add=0)
            self.filter2 = Biquadx(self.input, freq=self.freq2, q=self.q, type=0, stages=2, mul=0.6, add=0)
        elif filter_mode == 2: #lowpass/highpass
            self.filter1 = Biquadx(self.input, freq=self.freq1, q=self.q, type=0, stages=2, mul=0.6, add=0)
            self.filter2 = Biquadx(self.input, freq=self.freq2, q=self.q, type=0, stages=2, mul=0.6, add=0)
        
        pan_dict1 = {1:0.5, 2:0., 3:1., 4:0.} #1=50% de chaque cote; 2=filtre 1 a gauche, filtre 2 a droite
        pan_dict2 = {1:0.5, 2:1., 3:0., 4:0.} #3=filtre 1 a droite, filtre 2 a gauche, 4=mono (gauche)
        self.pan1 = Sig(value=pan_dict1[pan_mode], mul=[1,1])
        self.pan2 = Sig(value=pan_dict2[pan_mode], mul=[1,1])
        ### Un petit portamento sur les pans serait surement profitable. (soit en utilisant des SigTo ou en passant 
        ### par un objet Port).
        self.amp = Sig(value=amp, mul=[1,1])
        self.filter1_pan = Pan(input=self.filter1, outs=2, pan=self.pan1, spread=1., mul=self.amp)
        self.filter2_pan = Pan(input=self.filter2, outs=2, pan=self.pan2, spread=1., mul=self.amp)
        
        ### L'InputFader devrait etre au debut de la classe et recevoir directement l'arguement "input".
        ### Il pourrait remplacer l'objet Sig en self.input...
        self.in_fader = InputFader(self.input)
        
    def setInput(self, x, fadetime=0.05):
        self.input.value = x
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
        #self.filter1_pan.pan.value = pan_dict1[x]
        #self.filter2_pan.pan.value = pan_dict2[x]
    
    def setAmp(self,x):
        self.amp.value = x
        

src1 = Oscillator(wave=2,octave=1., lfo=0.)
src2 = Oscillator(wave=4,octave=2, lfo=0.)
bruit = NoiseGenerator()
filtre = Filter(src1.getOut()).out()

#test2 = NoiseGenerator(noise=2)
noise = Noise()
s.gui(locals())