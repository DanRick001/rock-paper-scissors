a = {
    "камень": "ножницы",
    "ножницы": "бумага",
    "бумага": "камень"
}

while True:
    b = input("Игрок 1: ")
    c = input("Игрок 2: ")

    if b == c:
        print("ничья")
        continue
    for i, j in a.items():
        if b == i and c == j:
            print("Победил Игрок 1")
            break
        elif c == i and b == j:
            print("Победил Игрок 2")
            break