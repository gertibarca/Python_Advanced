from Kerri import Kerri

class KerriElektrik(Kerri):
    def __init__(self, name, vitiProdhmit, dyert, ngjyra, bateria):
        super().__init__(name, vitiProdhmit, dyert, ngjyra)
        self.bateria=bateria

    def mbusheBaterine(self):
        print("Bateria eshte duke u mbushur")