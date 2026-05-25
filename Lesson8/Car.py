class Car:

    def __init__(self, name, color, year, motor, condition):
        self.name = name
        self.color = color
        self.year = year
        self.motor = motor
        self.condition = condition

    def start(self):
        print(f"{self.name} u ndez!")

    def drive(self):
        print(f"{self.name} eshte duke vozitur.")

    def brake(self):
        print(f"{self.name} ndaloi me frena.")

    def horn(self):
        print(f"{self.name} beri BEEP BEEP!")

    def stop(self):
        print(f"{self.name} u fik.")

    def info(self):
        print("----- INFO -----")
        print(f"Name: {self.name}")
        print(f"Color: {self.color}")
        print(f"Year: {self.year}")
        print(f"Motor: {self.motor}")
        print(f"Condition: {self.condition}")