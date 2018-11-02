from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import time
import atexit
from config import HASLO, EMAIL

plikLista = 'lista_zrobionych.txt'
listaZrobionych = set()

with open(plikLista, 'r', encoding='UTF-8') as plik:
    for nazwisko in plik:
        nazwisko = nazwisko.strip()
        if len(nazwisko)>1:
            listaZrobionych.add(nazwisko)

print(f'listaZrobionych = {listaZrobionych}')


# https://contacts.google.com/?hl=pl&tab=mC
# wszystkie: jsname="rymPhb"
# elementSelector: str, timeout=5
def waitForElement(*args):
    timeout = args[1] or 5
    if type(args[0]) is str:
        elementSelector = args[0]
        try:
            element_present = EC.element_to_be_clickable((By.CSS_SELECTOR, elementSelector))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print(f"Timed out waiting for {elementSelector} to load!")
    elif type(args[0]) is webdriver.remote.webelement.WebElement:
        element = args[0]
        try:
            element_present = EC.element_to_be_clickable((element))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print(f"Timed out waiting for {element} to load!")

def saveOnExit():
    with open(plikLista, 'a', encoding='UTF-8') as plik:
        for nazwisko in listaZrobionych:
            plik.write(nazwisko + '\n')
    

atexit.register(saveOnExit)

driver = webdriver.Chrome()

driver.get("https://contacts.google.com/?hl=pl&tab=mC")
emailInput = driver.find_element_by_css_selector('input')
emailInput.send_keys(EMAIL, Keys.ENTER)
waitForElement('input[type="password"]', 5)
passwordInput = driver.find_element_by_css_selector('input[type="password"]')
passwordInput.send_keys(HASLO, Keys.ENTER)

# ZALOGOWANO


waitForElement('div[jsname="rymPhb"]', 10)

def zdobadzEmail(selector):
    opis = driver.find_element_by_css_selector(selector)
    opis = opis.text
    print(f'opis: {opis}')
    emailPattern = re.compile(r'Podstawowy e-mail: (\S*)')
    match = re.search(emailPattern, opis)
    if match:
        email = match.group(1)
        return email
    else:
        return None

def zamknij():
    zamknijSelector = 'div .RANAid.jaWtS.Mmnd7d'
    waitForElement(zamknijSelector, 5)
    zamknij = driver.find_element_by_css_selector(zamknijSelector)
    zamknij.click()

textAreaSelector = 'textarea[jsname="YPqjbf"]'
osobaSelector = '.XXcuqd'
edytujSelector = '[aria-label="Edytuj kontakt"]'
anulujSelector = 'button[jsname="gQ2Xie"]'


nieWszystkiePominiete = True
i = 0
maxPowtorzen = 100
while nieWszystkiePominiete or i < maxPowtorzen:
    # Zaloz ze nie wszystkie zostaly wykonane
    nieWszystkiePominiete = False
    # Bo jesli wszystkie pominieto to nie ma sensu jeszcze raz

    for osoba in driver.find_elements_by_css_selector(osobaSelector):
        try:
            nazwisko = osoba.find_element_by_css_selector('.PDfZbf').text
        except StaleElementReferenceException:
            print('Stale Element Skipped.')
            continue
        edytuj = osoba.find_element_by_css_selector(edytujSelector)

        # Zjedź niżej
        driver.execute_script("arguments[0].scrollIntoView(true);", edytuj)
        print(f'nazwisko: {nazwisko}')

        # Jesli juz wykonane, przejdz do next
        if nazwisko in listaZrobionych and nazwisko not in ["", " "]:
            continue
        
        nieWszystkiePominiete = True

        # Kliknij uzywajac JS, bo przycisk jest zaslaniany
        driver.execute_script("arguments[0].click();", edytuj)

        waitForElement(textAreaSelector, 2)
        email = zdobadzEmail(textAreaSelector)

        # Jesli nie znaleziono, idz do nastepnego
        if not email:
            waitForElement(anulujSelector, 5)
            driver.find_element_by_css_selector(anulujSelector).click()
            zamknij()
            continue

        print(f'email: {email}')
        poleEmail = driver.find_element_by_css_selector('input[aria-label="E-mail"]')
        # ERRORS:

        # Sprawdz czy wpisano to co powinno
        wpisanoNiepoprawne = True
        maxProb = 5
        proby = 0
        while wpisanoNiepoprawne and proby < maxProb:
            poleEmail.send_keys(Keys.CONTROL + 'a')
            poleEmail.send_keys(email)
            if poleEmail.get_attribute("value") == email:
                wpisanoNiepoprawne = False
            proby += 1

        # Zapisz
        zapisz = driver.find_element_by_css_selector('button[jsname="x8hlje"]')
        zapisz.click()

        # Zamknij
        zamknij()
        
        # Dodaj ten przycisk jako wykonany
        listaZrobionych.add(nazwisko)
    i += 1