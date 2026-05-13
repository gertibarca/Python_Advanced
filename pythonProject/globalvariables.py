greetings = "Hello"

def greet(name):
    global message

    message = f"{greetings}, {name}"

    print(message)

greet("Bob")
print(message)