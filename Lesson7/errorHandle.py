try:
    rezultati = 10/0
except ZeroDivisionError:
    print("Nuk mundesh te pjesetosh me 0")
else:
    print("Pjesetimi eshte realizuar me sukses")

frutat = {
    "molllat": 5,
    "banane": 7,
    "portokalla": 3
}

try:
    print(frutat["dredhezat"])
except KeyError:
    print("The key does not exist in the directory.")

text = "This is not a number"

try:
    text_to_int = int(text)
except Exception as e:
    print("Ka ndodh nje error:", e)
finally:
    print("Hey, ke mberri deri te rreshti i 25")