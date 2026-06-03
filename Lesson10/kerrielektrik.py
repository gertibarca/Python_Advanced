from abc import ABC, abstractmethod

class Makina(ABC):
    def __init__(self, name, ngjyra, viti):
        self.name = name
        self.ngjyra = ngjyra
        self.viti = viti
        self.shpejtesia = 0

    @abstractmethod
    def rriteGazin(self, vlera):
        pass

    @abstractmethod
    def uleGazin(self, vlera):
        pass


class KerrElektrik(Makina):
    def __init__(self, name, ngjyra, viti, bateria):
        super().__init__(name, ngjyra, viti)
        self.bateria = bateria

    # Implementimi i detyrueshëm i metodës rriteGazin
    def rriteGazin(self, vlera):
        self.shpejtesia += vlera
        print(f"Shpejtësia u rrit në {self.shpejtesia} km/h.")

    # Implementimi i detyrueshëm i metodës uleGazin
    def uleGazin(self, vlera):
        self.shpejtesia -= vlera
        if self.shpejtesia < 0:
            self.shpejtesia = 0
        print(f"Shpejtësia u ul në {self.shpejtesia} km/h.")

    # Getters dhe Setters
    def get_name(self):
        return self.name

    def setName(self, name):
        self.name = name

    def get_ngjyra(self):
        return self.ngjyra

    def setNgjyra(self, ngjyra):
        self.ngjyra = ngjyra

    def get_viti(self):
        return self.viti

    def setViti(self, viti):
        self.viti = viti