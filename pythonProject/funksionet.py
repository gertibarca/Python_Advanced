def sayHello():
    print("Hello")

sayHello()

def greet_person(name):
    print("Pershendetje,", name)

greet_person("Gerti")
greet_person("Geati")

def prezantimi(emri,mbiemri):
    print("Pershendtje, emri im eshte", emri ,"dhe mbiemri im eshte", mbiemri)
prezantimi("Gerti","Novoberdaliu")

def prezantimi2(emri,mbiemri):
    print(f"Pershendtje, emri im eshte {emri} dhe mbiemri im eshte {mbiemri}")
prezantimi2("Gerti","Novoberdaliu")

print("----------------")
def add(number1,number2):
    return number1+number2
print(add(2,2))

def zbritja(x,y):
    rezultati= x-y
    return rezultati
print(zbritja(9,2))
