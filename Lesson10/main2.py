from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def make_sound(self):
        pass


class Dog(Animal):
    def make_sound(self):
        print("Bark Bark!")


class Cat(Animal):
    def make_sound(self):
        print("Meow Meow!")

if __name__ == "__main__":
    qeni = Dog()
    maca = Cat()

    qeni.make_sound()
    maca.make_sound()