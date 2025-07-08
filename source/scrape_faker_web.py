import requests
from bs4 import BeautifulSoup
import csv

def get_faker_functions():
    url = "https://faker.readthedocs.io/en/master/locales/it_IT.html#faker.providers.address.it_IT.Provider.street_address"
    # Effettua una richiesta GET per ottenere il contenuto della pagina
    response = requests.get(url)

    # Controlla se la richiesta è stata effettuata con successo
    if response.status_code == 200:
        # Crea un oggetto BeautifulSoup con il contenuto della pagina
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trova tutti gli elementi <span> con la classe "sig-name descname"
        parent_elements = soup.find_all('span', class_='sig-name descname')
        
        # Insieme per memorizzare gli elementi unici <span class="pre">
        extracted_elements = set()
        
        # Per ogni elemento padre trovato
        for parent in parent_elements:
            # Trova tutti gli elementi <span> con la classe "pre" sotto l'elemento padre
            child_elements = parent.find_all_next('span', class_='pre')
            
            # Aggiungi il testo di ciascun elemento trovato all'insieme
            for element in child_elements:
                text = element.get_text()
                # Filtra solo gli elementi che terminano con ()
                if text.endswith("()"):
                    # Sostituisci "Provider." con "fake."
                    text = text.replace("Provider.", "fake.")
                    extracted_elements.add(text)
        
        # Restituisci la lista degli elementi filtrati (ora unici)
        return list(extracted_elements)
    else:
        print(f"Errore nella richiesta: {response.status_code}")
        return []

# Esempio di utilizzo
faker_functions = get_faker_functions()

# Salva gli elementi estratti in un file CSV
csv_file = "faker_functions.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Faker Functions"])  # Header
    for func in faker_functions:
        writer.writerow([func])
