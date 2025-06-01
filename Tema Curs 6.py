
#exercitiu telefon

numere=["-+40720033157","-0731301886","-0040750037872"]
numere_noi=[]

for i in range (0,len(numere)):
    numere_noi.append(numere[i][-10:])
    if numere_noi[i][2] == '2' or numere_noi[i][2] == '3':
        print(f'Numarul {numere[i]} este Vodafone')
    elif numere_noi[i][2] == '4' or numere_noi[i][2] == '5':
        print(f'Numarul {numere[i]} este Orange')
    elif numere_noi[i][2] == '6' or numere_noi[i][2] == '8':
        print(f'Numarul {numere[i]} este Telekom')
    else:
        print(f'Numarul {numere[i]} este Digi')


print(numere_noi)



#exercitiu catalog

catalog = [
    ['Florin', [5, 7, 9]],
    ['Cosmin', [9, 2, 4]],
    ['Ioana', [10, 9, 6, 8, 2]]
]

# meniu
def meniu_catalog():
    print('\n=== Meniu Catalog ===')
    print('1. Afiseaza promovati')
    print('2. Introdu un nou elev')
    print('3. Modifica o nota')
    print('4. Sterge elev')
    print('5. Iesire program')

# functie afiseaza promovati
def afiseaza_promovati(catalog):
    print("\nElevii promovati sunt:")
    for elev in catalog:
        nume = elev[0]
        note = elev[1]
        media = sum(note) / len(note)
        if media >= 5:
            print(f'{nume} este promovat cu media {media:.2f}')

# functie introducere elev
def introdu_elev():
    nume = input("Introdu numele elev nou: ")
    nr1 = int(input("Nota 1: "))
    nr2 = int(input("Nota 2: "))
    nr3 = int(input("Nota 3: "))
    catalog.append([nume, [nr1, nr2, nr3]])
    print("Elev adaugat!")

# functie modificare nota
def modifica_nota():
    nume = input("Introdu nume elev nou: ")
    gasit = False
    for elev in catalog:
        if elev[0] == nume:
            gasit = True
            note = elev[1]
            print("Notele curente:", note)
            poz = int(input("A cata nota vrei sa o modifici?: "))
            if poz >= 1 and poz <= len(note):
                noua_nota = int(input("Introdu noua nota: "))
                note[poz - 1] = noua_nota
                print("Nota a fost modificata")
            else:
                print("Invalid.")
    if gasit == False:
        print("Elevul nu a fost gasit")

# functie stergere elev
def sterge_elev():
    nume = input("Introdu numele elevului de sters: ")
    gasit = False
    for elev in catalog:
        if elev[0] == nume:
            catalog.remove(elev)
            print("Elev sters.")
            gasit = True
            break
    if gasit == False:
        print("Elevul nu a fost gasit")

# functie program
def program_catalog():
    while True:
        meniu_catalog()
        optiune = input('Alege o optiune (1-5): ')
        if optiune == '1':
            afiseaza_promovati(catalog)
        elif optiune == '2':
            introdu_elev()
        elif optiune == '3':
            modifica_nota()
        elif optiune == '4':
            sterge_elev()
        elif optiune == '5':
            print('Adios amigo!')
            break
        else:
            print('Optiune invalida. Incearca din nou')

program_catalog()
