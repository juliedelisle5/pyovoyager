from pyo import *
from mixer import *

#Chaines audio du synthetiseur analogique, avec et sans controleur MIDI:
#   generateurs de son/bruit --> mixeur --> filtre --> enveloppe ADSR de volume
#Enveloppe est donc la classe "finale" dont le signal est achemine a la sortie audio.

#Appels de methodes sur les generateurs de son/bruit:
#   enveloppe.mixer.methode(valeur)

#Appels de methodes sur le filtre:
#   enveloppe.filtre.methode(valeur)


#Mode 1 (Pour usage avec un controleur MIDI)
class ADSR():
    def __init__(self, amount=0., mul=0.8):
        #controles generaux
        self.mul = Sig(value=mul)
        self.midi = Notein(scale=1)
        self.mixer = MixerSection(ref_freq = self.midi['pitch']).stop()
        #Enveloppe ADSR de volume
        self.adsr = Adsr(attack=.01, decay=.2, sustain=.5, release=.1, dur=0, mul=.5)
        self.midi_adsr = MidiAdsr(self.midi['velocity'],mul=self.mul)
        #Enveloppe ADSR du filtre
        self.amount = amount #Potentiometre "Amount to filter"; valeur par defaut
        self.adsr2 = Adsr(attack=.01, decay=.2, sustain=.5, release=.1, dur=0, mul=self.amount)
        self.midi_adsr2 = MidiAdsr(self.midi['velocity'],mul=self.amount)
        #Le mixer est passe dans le filtre avant d'etre achemine vers la sortie audio
        self.filtre = Filter(self.mixer.getOut(),amp=self.midi_adsr).stop()
        #Controles separes (lorsque c'est le cas, ils ne sont pas passes dans le filtre)
        self.mix1 = Mix(input=[self.mixer.osc3.getOut()], voices=2, mul=self.mul).stop()
        self.mix2 = Mix(input=[self.mixer.noise.getOut()], voices=2, mul=self.mul).stop()
        self.mix3 = Mix(input=[self.mixer.external], voices=2, mul=self.mul).stop()
        self.mix4 = Mix(input=[self.mixer.sfPlayer], voices=2, mul=self.mul).stop()
        
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
        self.filtre.setAmp(self.midi_adsr)
            
    def kbAmpCtlOff(self): 
        self.filtre.setAmp(self.adsr)
        
    #Activer ou desactiver le controle de l'enveloppe du filtre par les touches du controleur MIDI
    #Actif par defaut
    def kbFilterCtlOn(self):
        self.filtre.setVariation(self.midi_adsr2)

    def kbFilterCtlOff(self): #Ne fonctionne pas comme prevu...
        self.filtre.setVariation(self.adsr2)
        
    #Activer ou desactiver le controle de la frequence de la note jouee par les touches du controleur MIDI
    #Actif par defaut
    def kbFreqCtlOn(self):
        self.mixer.setRefFreq(self.midi['pitch'])
        
    def kbFreqCtlOff(self):
        self.mixer.setRefFreq(442.)
        
    #Permet d'activer ou de desactiver le controle clavier du 3e oscillateur, pour en faire un drone ou une pedale.
    def kb3ControlOn(self):
        self.mix1.stop()
        self.mixer.osc3.setAmp(self.midi_adsr)
        self.mixer.osc3.setFreq(self.mixer.freq1) #self.mixer.osc3.self.midi['pitch']

    def kb3ControlOff(self):
        self.mixer.osc3.setFreq(442.)
        self.mixer.osc3.setAmp(self.adsr)
        self.mix1.out()
        
    #Permet d'activer ou de desactiver le controle clavier du generateur de bruit, pour en faire un drone.
    def kbNoiseControlOn(self):
        self.mix2.stop()
        self.mixer.noise.setAmp(self.midi_adsr)

    def kbNoiseControlOff(self):
        self.mixer.noise.setAmp(self.adsr)
        self.mix2.out()

    #Permet d'activer ou de desactiver le controle clavier de l'amplitude de la source externe.
    def kbExtControlOn(self):
        self.mix3.stop()
        self.mixer.external.mul = self.midi_adsr

    def kbExtControlOff(self):
        self.mixer.external.mul = 0.4
        self.mix3.out()
        
    #Permet d'activer ou de desactiver le controle clavier du sfPlayer, pour l'avoir en continu.
    def kbSFPControlOn(self):
        self.mix4.stop()
        self.mixer.sfPlayer.mul = self.midi_adsr

    def kbSFPControlOff(self):
        self.mixer.sfPlayer.mul = 0.4
        self.mix4.out()
    
    #Parametres de l'enveloppe ADSR de volume
    def setAttack(self,x):
        self.midi_adsr.setAttack(x)
        self.adsr.setAttack(x)
        
    def setDecay(self,x):
        self.midi_adsr.setDecay(x)
        self.adsr.setDecay(x)
        
    def setSustain(self,x):
        self.midi_adsr.setSustain(x)
        self.adsr.setSustain(x)
        
    def setRelease(self,x):
        self.midi_adsr.setRelease(x)
        self.adsr.setRelease(x)
        
    #Parametres de l'enveloppe ADSR du filtre
    def setAttack2(self,x):
        self.midi_adsr2.setAttack(x)
        self.adsr2.setAttack(x)

    def setDecay2(self,x):
        self.midi_adsr2.setDecay(x)
        self.adsr2.setDecay(x)

    def setSustain2(self,x):
        self.midi_adsr2.setSustain(x)
        self.adsr2.setSustain(x)

    def setRelease2(self,x):
        self.midi_adsr2.setRelease(x)
        self.adsr2.setRelease(x)
        
    def setAmount(self,x):
        self.midi_adsr2.mul = x
        self.adsr2.mul = x
        self.filtre.setVariation(self.midi_adsr2)



if __name__ == '__main__':
    s = Server(duplex=1).boot() 
    enveloppe = ADSR().out()
    s.gui(locals())