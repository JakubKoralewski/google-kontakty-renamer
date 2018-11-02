lista = set()
iloscPrzed = 0
with open('lista_zrobionych.txt', 'r', encoding='UTF-8') as plik:
    for nazwisko in plik:
        iloscPrzed += 1
        lista.add(nazwisko.strip())
iloscPo = 0
with open('lista_zrobionych.txt', 'w', encoding='UTF-8') as plik:
    for nazwisko in lista:
        iloscPo += 1
        plik.write(nazwisko+'\n')

print(f'Ilosc przed = {iloscPrzed}, Ilosc po = {iloscPo}, duplikatow = {iloscPrzed-iloscPo}')