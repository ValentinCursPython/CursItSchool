#Problema1

parola = input("Introduceti parola: ")

if len(parola) < 10:
    print("Parola trebuie sa aiba cel putin 10 caractere.")
elif " " in parola:
    print("Parola nu trebuie sa conțina spatii.")
else:
    print("OK")


#Problema 2

cuvant = "programare"
litera = "r"
numar_aparitii = cuvant.count(litera)
print(f"Litera '{litera}' apare de {numar_aparitii} ori in cuvantul '{cuvant}'.")

#Problema 3

putere = 0
while True:
    valoare = 3 ** putere
    if valoare > 300:
        break
    if valoare >= 200:
        print(valoare)
    putere += 1

#Problema 4

n = int(input("Introduceti un numar: "))

# Variante FOR
suma = 0
for i in range(1, n + 1):
    suma += i
print(f"Suma (cu for) este: {suma}")

# Varianta WHILE
i = 1
suma = 0
while i <= n:
    suma += i
    i += 1
print(f"Suma (cu while) este: {suma}")


#Problema 5

n = int(input("Introduceți un număr: "))

# Varianta FOR
for i in range(n, -1, -1):
    print(i)

# Varianta WHILE
i = n
while i >= 0:
    print(i)
    i -= 1
