# Leximi i vetëm një rreshti
with open("example.txt", "r") as file:
    file1 = file.readline()
    print(file1)

# Leximi i të gjithë rreshtave si një listë
with open("example.txt", "r") as file:
    lines = file.readlines()
    print(lines)