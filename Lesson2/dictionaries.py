informacionet = {
    "Gerti": 1500,
    "Geati": 2100,
    "Joni": 850
}

print(informacionet)

rroga = informacionet["Gerti"]
print(rroga)

print(informacionet.keys())
print(informacionet.values())

informacionet["Geati"]=2500
print(informacionet)

informacionet["Gerti"]=3155
print(informacionet)

del informacionet["Joni"]
print(informacionet)