from pyo import *
from random import uniform
from audio import *

#On pourrait passer le signal obtenu de l'objet MixerSection dans un effet externe avant de le passer au filtre.
class MixerSection():
    def __init__(self, ref_freq=130., finetune=0., mul=0.8):
        self.ref_freq = Sig(value=ref_freq)
        self.fine_tune = Sig(value=finetune)
        
        self.wave1 = 0. #Sinusoidale par defaut
        self.freq1 = self.ref_freq*(Pow(base=2.0, exponent=(self.fine_tune/12.0), mul=1.))#controle avec le fine_tune, +ou- 2 demi-tons par rapport a la frequence de reference
        self.octave1 = 1.
        self.amp1 = 0.4
        
        self.wave2 = 0. #Valeurs par defaut a changer par des appels de methode
        self.freq2 = self.freq1
        self.transpo2 = 0.
        self.octave2 = 1.
        self.amp2 = 0.4
        
        self.wave3 = 0. #Valeurs par defaut a changer par des appels de methode
        self.freq3 = self.freq1
        self.transpo3 = 0.
        self.octave3 = 1.
        self.lfo3 = 0.
        self.amp3 = 0.4
        
        self.noise_type = 1 #Seulement pour la valeur par defaut.
        self.noise_amp = 0.3
        
        #Pour le fun, un petit SfPlayer (je pourrais peut-etre faire de la synthese ou de la modulation avec...)
        #(Il fallait que je plogue le rire de Jacques Languirand dans mon travail - c'est mon baseball majeur a moi!)
        #Pour changer la source : appeler objetMixerSection.setSfPlayer_path(path)
        self.sfPlayer_mul = 0.4
        self.sfPlayer = SfPlayer(path="jacquesLanguirand.aiff", speed=1, loop=True, offset=0, interp=2, mul=self.sfPlayer_mul, add=0).stop()
        
        #Source externe: verifier le channel.
        self.external_mul = 0.4
        self.external = Input(mul=self.external_mul).stop()
        
        self.osc1 = Oscillator(wave=self.wave1, freq=self.freq1, transpo=0., octave=self.octave1, lfo=0., amp=self.amp1).stop()
        self.osc2 = Oscillator(wave=self.wave2, freq=self.freq2, transpo=self.transpo2, octave=self.octave2, lfo=0., amp=self.amp2).stop()
        self.osc3 = Oscillator(wave=self.wave3, freq=self.freq3, transpo=self.transpo3, octave=self.octave3, lfo=self.lfo3, amp=self.amp3).stop()
        self.noise = NoiseGenerator(noise=self.noise_type, amp=self.noise_amp).stop()
        
        #Pour la synthese FM
        self.ratio = Sig(value=(self.osc3.freq/self.osc1.freq))
        self.index = Sig(self.osc3.amp*20.)
        self.mod_osc = Osc(table=self.osc3.newTable, freq=self.freq1*self.ratio, mul=0.1).stop()
        self.port_phasor_freq = self.mod_osc*self.freq1*self.ratio*self.index
        self.port_phasor = Phasor(freq=self.port_phasor_freq+self.freq1).stop()
        self.fm = Osc(table=self.osc1.newTable, freq=self.port_phasor_freq, mul=0.1, add=-0.05).stop()
        
        #Pour le Sync 1-2
        self.metro = Metro(time=1/self.freq1).stop()
        self.osc2Aux = OscTrig(table=self.osc2.newTable, trig=self.metro, freq=self.osc2.freq, mul=0.5).stop()
        
        #Signal de sortie
        self.mul = mul
        self.inputs = [self.osc1.getOut(), self.osc2.getOut(), self.osc3.getOut(), self.noise.getOut(), self.sfPlayer, self.external, self.fm, self.osc2Aux] #ajouter external et sfplayer s'il y a lieu
        self.mix = Mix(input=self.inputs, voices=1, mul=self.mul)
    
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
        
    def setMul(self,x):
        self.mix.mul = x;
        
    #Methodes pour les parametres des oscillateurs et du generateur de bruit
    def setRefFreq(self,x):
        self.ref_freq.value = x
        
    def setFineTune(self,x):
        self.fine_tune.value = x
        
    def setWave1(self,x):
        self.osc1.setWave(x)
        
    def setOctave1(self,x):
        self.osc1.setOctave(x)
        
    def setAmp1(self,x):
        self.osc1.setAmp(x)
        
    def setWave2(self,x):
        self.osc2.setWave(x)
        
    def setTranspo2(self,x):
        self.osc2.setTranspo(x)
        
    def setOctave2(self,x):
        self.osc2.setOctave(x)
        
    def setAmp2(self, x):
        self.osc2.setAmp(x)

    def setWave3(self,x):
        self.osc3.setWave(x)

    def setTranspo3(self,x):
        self.osc3.setTranspo(x)

    def setOctave3(self,x):
        self.osc3.setOctave(x)

    def setLFO3Mode(self,x):
        self.osc3.setLFO(x)
        
    def setAmp3(self, x):
        self.osc3.setAmp(x)
        
    def setNoiseType(self,x):
        self.noise.setNoise(x)
        
    def setNoiseAmp(self,x):
        self.noise.setAmp(x)
        
    def setExternal_mul(self,x):
        self.external.mul = x
    
    def setSfPlayer_mul(self,x):
        self.sfPlayer.mul = x
        
    def setSfPlayer_path(self,path):
        self.sfPlayer.path = path
    
    #Methodes on/off pour les oscillateurs et le generateur:    
    
    def externalOn(self):
        self.external.play()
        
    def externalOff(self):
        self.external.stop()
        
    def sfPlayerOn(self):
        self.sfPlayer.play()
        
    def sfPlayerOff(self):
        self.sfPlayer.stop()
    
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
        
    #Glide Rate
    def glideOn(self):
        self.osc1.setGlide(1.) 
        self.osc2.setGlide(1.)
        self.osc3.setGlide(1.)
        
    def glideOff(self):
        self.osc1.freq_interp.risetime = 0.05
        self.osc2.freq_interp.risetime = 0.05
        self.osc3.freq_interp.risetime = 0.05
        
    def setGlideRate(x):
        self.osc1.freq_interp.risetime = x
        self.osc2.freq_interp.risetime = x
        self.osc3.freq_interp.risetime = x
        
    #Synthese FM (3-1 FM)
    def synthFMOn(self):
        self.osc1Off()
        self.osc3Off()
        self.mod_osc.play()
        self.port_phasor.play()
        self.fm.play()
        
    def synthFMOff(self):
        self.fm.stop()
        self.port_phasor.stop()
        self.mod_osc.stop()
        self.osc1On()
        self.osc3On()
        
    #Sync 1-2
    def sync12On(self):
        self.osc2Off()
        self.osc1On()
        self.metro.play()
        self.osc2Aux.play()
        
    def sync12Off(self):
        self.osc2Aux.stop()
        self.metro.stop()
        self.self.osc2On()


if __name__ == '__main__':
    s = Server(duplex=1).boot()
    mix = MixerSection(130.,0.,0.8).out()
    s.gui(locals())
        