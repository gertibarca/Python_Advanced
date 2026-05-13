def shuma_cift(lista):
    shuma = 0

    for nr in lista:
        if nr % 2 == 0:
            shuma = shuma + nr

    return shuma


numrat = [1, 2, 3, 4, 5, 6, 7, 8]

print(shuma_cift(numrat))