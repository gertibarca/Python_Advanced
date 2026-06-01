class Kafsha:
    def __init__(self, tingulli):
        self.tingulli = tingulli

    def tingulliKafshes(self):
        pass


class Maca(Kafsha):
    def tingulliKafshes(self):
        print(f"Maca thotë: {self.tingulli}wwwwww")


class Qeni(Kafsha):
    def tingulliKafshes(self):
        print(f"Qeni thotë: {self.tingulli}mmm {self.tingulli}mmm")


def bëjTingullin(objekti_kafshë):
    objekti_kafshë.tingulliKafshes()


kafsha1 = Qeni("hamm")
kafsha2 = Maca("maww")

bëjTingullin(kafsha1)
bëjTingullin(kafsha2)