# Te dhenat fillestare
name = "Gerti"
age = 16
score = 69
number = 13453
numbers_list = [1, 2, 3, 4, 5]

# Printim i te dhenave
print("Emri:", name)
print("Mosha:", age)
print("Score:", score)
print("Numri:", number)
print("Lista:", numbers_list)

# Kontroll per moshen
if age > 10:
    print("Personi eshte me i madh se 10 vjeq")
else:
    print("Personi eshte me i vogel ose baraz me 10 vjeq")

# Kontroll tjeter
if age > 200:
    print("Kjo moshe nuk eshte reale")
else:
    print("Mosha duket normale")

# Loop ne liste
print("\nNumrat ne liste:")
for n in numbers_list:
    print(n)

# Llogaritje me score
if score >= 50:
    print("\nKalove testin!")
else:
    print("\nNuk kalove testin.")

# Funksion
def pershendetje(emri):
    print("\nPershendetje,", emri)

pershendetje(name)

# Llogarit shumen e listes
shuma = sum(numbers_list)
print("\nShuma e numrave:", shuma)

# Gjetja e numrit me te madh
max_num = max(numbers_list)
print("Numri me i madh ne liste:", max_num)

# Shtim i nje numri ne liste
numbers_list.append(6)
print("Lista pas shtimit:", numbers_list)