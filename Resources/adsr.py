from pyo import *
from mixer import *

#Chaines audio du synthetiseur analogique, avec et sans controleur MIDI:
#   generateurs de son/bruit --> mixeur --> filtre --> enveloppe ADSR
#Enveloppe est donc la classe "finale", dont le output.

#Appels de methodes sur les generateurs de son/bruit:
#   objetEnveloppe.mixer.methode(valeur)

#Appels de methodes sur le filtre:
#   objetEnveloppe.filtre.methode(valeur)


#Mode 1 (Pour usage avec un controleur MIDI)
class KeyboardEnv():
    def __init__(self, mul=0.8):
        self.mul = Sig(value=mul)
        self.midi = Notein(scale=1)
        self.mixer = MixerSection(ref_freq = self.midi['pitch']).stop()
        self.midi_adsr = MidiAdsr(self.midi['velocity'],mul=self.mul)
        self.filtre = Filter(self.mixer.getOut(),amp=self.midi_adsr).stop()
        
    #Methodes directes de l'objet MidiAdsr:
    #   self.midi_adsr.setAttack(x) pour la duree d'attaque
    #   self.midi_adsr.setDecay(x) pour la duree du decay
    #   self.midi_adsr.setRelease(x) pour la duree du release
    def setMasterVolume(self,x):
        self.mul.value = x
        
    def out(self):
        self.mixer.play() 
        self.filtre.out()
        return self
        
    def stop(self):
        self.mixer.stop()
        self.filtre.stop()
        
        
#Mode 2 (Dans le cas ou l'utilisateur n'a pas ou ne veut pas de controleur MIDI):
#   Ne pas oublier d'appeler la methode play() sur l'objet cree pour partir la note, et stop() pour l'arreter!
class AutoEnv():
    def __init__(self, mul=0.8):
        self.mul = Sig(value=mul)
        self.adsr = Adsr(attack=.01, decay=.2, sustain=.5, release=.1, dur=0, mul=.5)
        self.mixer = MixerSection(130.,0.).stop()
        self.filtre = Filter(self.mixer.getOut(),amp=self.adsr).stop()
        
    #Methodes:
    #   adsr.play() pour partir la note
    #   adsr.stop() pour partir le release
    #   adsr.setAttack(x) pour la duree d'attaque
    #   adsr.setDecay(x) pour la duree du decay
    #   adsr.setRelease(x) pour la duree du release
    def setMasterVolume(self,x):
        self.mul.value = x

    def out(self):
        self.mixer.play() 
        self.filtre.out()
        return self

    def stop(self):
        self.mixer.stop()
        self.filtre.stop()


if __name__ == '__main__':
    s = Server(duplex=1).boot() 
    output1 = KeyboardEnv()
    output2 = AutoEnv()
    mode = 1
    if mode == 1:
        output1.out()
    elif mode == 2:
        output2.out()
    s.gui(locals())