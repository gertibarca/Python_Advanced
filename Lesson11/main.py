file_path = "example.txt"
file = open(file_path, "r")
content = file.read()
print(content)
file.close()