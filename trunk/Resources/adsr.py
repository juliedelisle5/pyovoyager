from pyo import *
from mixer import *

#Chaines audio du synthetiseur analogique, avec et sans controleur MIDI:
#   generateurs de son/bruit --> mixeur --> filtre --> enveloppe ADSR de volume
#Enveloppe est donc la classe "finale", dont le output.

#Appels de methodes sur les generateurs de son/bruit:
#   enveloppe.mixer.methode(valeur)

#Appels de methodes sur le filtre:
#   enveloppe.filtre.methode(valeur)


#Mode 1 (Pour usage avec un controleur MIDI)
class VolumeEnv():
    def __init__(self, mul=0.8):
        self.mul = Sig(value=mul)
        self.midi = Notein(scale=1)
        self.mixer = MixerSection(ref_freq = self.midi['pitch']).stop() #Controle clavier de la frequence desactive par defaut
        self.adsr = Adsr(attack=.01, decay=.2, sustain=.5, release=.1, dur=0, mul=.5)
        self.midi_adsr = MidiAdsr(self.midi['velocity'],mul=self.mul)
        self.filtre = Filter(self.mixer.getOut(),amp=self.midi_adsr).stop() #Controle clavier de l'amplitude desactive par defaut
        self.mix = Mix(input=[self.mixer.osc3.getOut()], voices=2, mul=self.mul).stop()
        
    #Volume master
    def setMasterVolume(self,x):
        self.mul.value = x
        
    def out(self):
        self.mixer.play() 
        self.filtre.out()
        return self
        
    def stop(self):
        self.mixer.stop()
        self.filtre.stop()
        
    #Play et stop note quand le controle clavier est desactive
    def playNote(self):
        self.adsr.play()
        
    def stopNote(self):
        self.adsr.stop()
        
    #Activer ou desactiver le controle de l'enveloppe d'amplitude par les touches du controleur MIDI
    #Actif par defaut
    def kbAmpCtlOn(self):
        self.filtre.amp = self.midi_adsr
            
    def kbAmpCtlOff(self):
        self.filtre.amp = self.adsr
        
    #Activer ou desactiver le controle de la frequence de la note jouee par les touches du controleur MIDI
    #Actif par defaut
    def kbFreqCtlOn(self):
        self.mixer.ref_freq = self.midi['pitch']
        
    def kbFreqCtlOff(self):
        self.mixer.ref_freq = 442.
        
    #Permet d'activer ou de desactiver le controle clavier du 3e oscillateur, pour en faire un drone ou une pedale.
    def kb3ControlOn(self):
        self.mix.stop()
        self.mixer.osc3.ref_freq = self.midi['pitch']

    def kb3ControOff(self):
        self.mixer.osc3.ref_freq = 111.
        self.mix.out()
    
    #Parametres de l'enveloppe ADSR de volume
    def setAttack(self,x):
        self.midi_adsr.setAttack(x)
        self.adsr.setAttack(x)
        
    def setDecay(self,x):
        self.midi_adsr.setDecay(x)
        self.adsr.setDecay(x)
        
    def setSustain(self,x):
        self.adsr.setSustain(x)
        
    def setRelease(self,x):
        self.midi_adsr.setRelease(x)
        self.adsr.setRelease(x)


if __name__ == '__main__':
    s = Server(duplex=1).boot() 
    enveloppe = VolumeEnv().out()
    s.gui(locals())