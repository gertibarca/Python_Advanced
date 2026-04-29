persona = {
    "Gerti": {
        "phone": "044123456",
        "email": "gerti@gmail.com"
    },
    "Joni": {
        "phone": "049987654",
        "email": "joni@gmail.com"
    }
}


print("Fillimi:")
print(persona)


persona["Gerti"]["email"] = "gerti_new@gmail.com"


persona["Geati"] = {
    "phone": "045111222",
    "email": "geati@gmail.com"
}


persona["Joni"]["phone"] = "049000000"

print("\nPas ndryshimeve:")
print(persona)


del persona["Joni"]["email"]


del persona["Geati"]

print("\nPas fshirjeve:")
print(persona)