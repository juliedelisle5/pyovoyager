from pyo import *
from random import uniform
from audio import *
#On pourra aussi brancher un SfPlayer ou un Input pour respectivement utiliser
#un fichier son ou une source externe. Lors de la creation de l'interface graphique,
#on pourra prevoir un bouton pour les controler.

#Utiliser la methode getFreq pour la synthese FM
s = Server().boot()

class MixerSection():
    def __init__(self, ref_freq, finetune):
        self.ref_freq = Sig(value=ref_freq)
        self.fine_tune = Sig(value=ref_freq)
        
        self.wave1 = 1 #Sinusoidale par defaut
        self.freq1 = Sig(value=ref_freq*(Pow(base=2.0, exponent=(finetune/12.0), mul=1.))) #controle avec le finetune, +ou- 2 demi-tons par rapport a la frequence de reference
        self.octave1 = 1. #Verifier s'il ya un conflit avec freq1 et la frequence de l'objet oscillator.
        self.amp1 = 0.7
        
        self.wave2 = 1 #Valeurs par defaut, a changer par des appels de methode
        self.freq2 = self.freq1
        self.transpo2 = 0.
        self.octave2 = 1.
        self.amp2 = 0.7
        
        self.wave3 = 1 #Valeurs par defaut, a changer par des appels de methode
        self.freq3 = self.freq1
        self.transpo3 = 0.
        self.octave3 = 1.
        self.lfo3 = 0.
        self.amp3 = 0.7
        
        self.noise_type = 1.
        self.noise_amp = 0.6
        
        #self.external = a rajouter eventuellement avec ses attributs.
        
        self.osc1 = Oscillator(wave=self.wave1, freq=self.freq1, transpo=0., octave=self.octave1, lfo=0., amp=self.amp1).stop()
        self.osc2 = Oscillator(wave=self.wave2, freq=self.freq2, transpo=self.transpo2, octave=self.octave2, lfo=0., amp=self.amp2).stop()
        self.osc3 = Oscillator(wave=self.wave3, freq=self.freq3, transpo=self.transpo3, octave=self.octave3, lfo=self.lfo3, amp=self.amp3).stop()
        self.noise = NoiseGenerator(noise=self.noise_type, amp=self.amp).stop()
        
        self.inputs = [self.osc1.getOut(), self.osc2.getOut(), self.osc3.getOut(), self.noise.getOut()] #ajouter external et sfplayer s'il y a lieu
        self.mix = Mix(input=self.inputs, voices=1, mul=.8)
    
    #Methodes generales (out, getOut, stop, play)
    def out(self):
        self.mix.out()
        return self
        
    def getOut(self):
        return self.mix
        
    def play(self):
        self.mix.play()
        return self
        
    def stop(self):
        self.mix.stop()
        return self
        
    #Methodes pour les parametres des oscillateurs et du generateur de bruit
    def setRefFreq(self,x):
        self.ref_freq.value = x
        
    def setFineTune(self,x):
        self.fine_tune.value = x
        
    def setWave1(self,x):
        self.wave1 = x
        
    def setOctave1(self,x):
        self.octave1 = x
        
    def setAmp1(self,x):
        self.amp1 = x
        
    def setWave2(self,x):
        self.wave2 = x
        
    def setTranspo2(self,x):
        self.transpo2 = x
        
    def setOctave2(self,x):
        self.octave2 = x
        
    def setAmp2(self, x):
        self.amp2 = x

    def setWave3(self,x):
        self.wave3 = x

    def setTranspo3(self,x):
        self.transpo3 = x

    def setOctave3(self,x):
        self.octave3 = x

    def setLFO3Mode(self,x):
        self.lfo3 = x
        
    def setAmp3(self, x):
        self.amp3 = x
        
    def setNoiseType(self,x):
        self.noise_type = x
        
    def setNoiseAmp(self,x):
        self.noise_amp = x
        
    #Methodes on/off pour les oscillateurs et le generateur
    #A ajouter au moment de l'ajout de l'option source externe.  A copier si on ajoute aussi un SfPlayer
    #def externalOn(self):
        #self.external.play()
        
    #def externalOff(self):
        #self.external.stop()
        
    def osc1On(self):
        self.osc1.play()
        
    def osc1Off(self):
        self.osc1.stop()
        
    def osc2On(self):
        self.osc2.play()
        
    def osc2Off(self):
        self.osc2.stop()
        
    def osc3On(self):
        self.osc3.play()
        
    def osc3Off(self):
        self.osc3.stop()
        
    def noiseOn(self):
        self.noise.play()
        
    def noiseOff(self):
        self.noise.stop()
        
    def glideOn(self, x): #On doit absolument fournir un temps de glide en argument!
        self.osc1.setGlide(x) 
        self.osc2.setGlide(x)
        self.osc3.setGlide(x)
        
    def glideOff(self): #Devrait marcher, car ne fait que parler au risetime pour l'interpolation de frequences
        self.osc1.freq_interp.risetime = 0.05 #(n'influence pas les frequences directement)
        self.osc2.freq_interp.risetime = 0.05
        self.osc3.freq_interp.risetime = 0.05
        
        
mix = MixerSection(130.,0.).out()
s.gui(locals())
        