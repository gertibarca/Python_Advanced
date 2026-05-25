from Car import Car

kerri1 = Car(name="Toyota", color="Red", year="2026", motor="2.0 Diesel", condition="New")

kerri2 = Car(name="BMW", color="Black", year="2024", motor="3.0 Petrol", condition="Used")

kerri3 = Car(name="Audi", color="White", year="2025", motor="2.5 TDI", condition="New")

kerri4 = Car(name="Mercedes", color="Blue", year="2023", motor="4.0 AMG", condition="Excellent")

kerri1.start()
kerri1.drive()
kerri1.info()

print("---------------")

kerri2.start()
kerri2.horn()
kerri2.brake()
kerri2.info()

print("---------------")

kerri3.start()
kerri3.stop()
kerri3.info()

print("---------------")

kerri4.start()
kerri4.drive()
kerri4.info()