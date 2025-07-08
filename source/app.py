# Do not change the import order, first utils then pd then st and last string.
from utils import check_sensitive_data
from utils import convert_to_arrow_compatible
from utils import read_csv_with_encoding
from utils import detect_separator
from utils import generate_synthetic_data
import pandas as pd
import streamlit as st
import string
import os

data = {
    'Nome': ['Alice Johnson', 'Bob Smith', 'Charlie Davis', 'Diana Ross', 'Ethan Hunt', 'Fiona Apple', 'George Clooney', 'Hannah Montana', 'Ian McKellen', 'Julia Roberts', 'Kevin Bacon', 'Laura Pausini', 'Michael Jordan', 'Naomi Campbell', 'Orlando Bloom', 'Penelope Cruz', 'Quentin Tarantino', 'Rachel Green', 'Steve Jobs', 'Taylor Swift', 'Uma Thurman', 'Victoria Beckham', 'Will Smith', 'Xena Warrior', 'Yoko Ono', 'Zac Efron', 'Adam Sandler', 'Britney Spears', 'Celine Dion', 'David Bowie', 'Emma Watson', 'Frank Sinatra', 'Gwen Stefani', 'Hugh Jackman', 'Iggy Pop', 'Jennifer Aniston', 'Kanye West', 'Liam Neeson', 'Meryl Streep', 'Natalie Portman', 'Oprah Winfrey', 'Paul McCartney', 'Queen Latifah', 'Robert De Niro', 'Scarlett Johansson', 'Tom Hanks', 'Usain Bolt', 'Vin Diesel', 'Whoopi Goldberg', 'Xavier Dolan', 'Yannick Noah', 'Zoe Saldana', 'Al Pacino', 'Brad Pitt', 'Charlize Theron'],
    'Email': ['alice.johnson@example.com', 'bob.smith@example.com', 'charlie.davis@example.com', 'diana.ross@example.com', 'ethan.hunt@example.com', 'fiona.apple@example.com', 'george.clooney@example.com', 'hannah.montana@example.com', 'ian.mckellen@example.com', 'julia.roberts@example.com', 'kevin.bacon@example.com', 'laura.pausini@example.com', 'michael.jordan@example.com', 'naomi.campbell@example.com', 'orlando.bloom@example.com', 'penelope.cruz@example.com', 'quentin.tarantino@example.com', 'rachel.green@example.com', 'steve.jobs@example.com', 'taylor.swift@example.com', 'uma.thurman@example.com', 'victoria.beckham@example.com', 'will.smith@example.com', 'xena.warrior@example.com', 'yoko.ono@example.com', 'zac.efron@example.com', 'adam.sandler@example.com', 'britney.spears@example.com', 'celine.dion@example.com', 'david.bowie@example.com', 'emma.watson@example.com', 'frank.sinatra@example.com', 'gwen.stefani@example.com', 'hugh.jackman@example.com', 'iggy.pop@example.com', 'jennifer.aniston@example.com', 'kanye.west@example.com', 'liam.neeson@example.com', 'meryl.streep@example.com', 'natalie.portman@example.com', 'oprah.winfrey@example.com', 'paul.mccartney@example.com', 'queen.latifah@example.com', 'robert.deniro@example.com', 'scarlett.johansson@example.com', 'tom.hanks@example.com', 'usain.bolt@example.com', 'vin.diesel@example.com', 'whoopi.goldberg@example.com', 'xavier.dolan@example.com', 'yannick.noah@example.com', 'zoe.saldana@example.com', 'al.pacino@example.com', 'brad.pitt@example.com', 'charlize.theron@example.com'],
    'Codice_sanitario': ['123-45-6789', '987-65-4321', '111-22-3333', '444-55-6666', '777-88-9999', '123-98-7654', '321-54-9876', '159-75-3153', '753-15-9513', '951-35-7531', '147-25-8369', '258-36-9147', '369-14-7258', '741-25-8963', '852-36-9741', '963-14-7852', '159-26-3748', '267-34-8159', '374-85-1926', '485-92-6137', '596-13-7248', '617-24-8359', '728-35-9461', '839-46-1572', '941-57-2683', '152-68-3794', '263-79-4815', '374-81-5926', '485-92-6137', '596-13-7248', '617-24-8359', '728-35-9461', '839-46-1572', '941-57-2683', '152-68-3794', '263-79-4815', '374-81-5926', '485-92-6137', '596-13-7248', '617-24-8359', '728-35-9461', '839-46-1572', '941-57-2683', '152-68-3794', '263-79-4815', '374-81-5926', '485-92-6137', '596-13-7248', '617-24-8359', '728-35-9461', '839-46-1572', '941-57-2683', '152-68-3794', '263-79-4815', '374-81-5926'],
    'Telefono': ['555-1234', '555-5678', '555-8765', '555-4321', '555-8765', '555-2468', '555-1357', '555-9876', '555-3698', '555-7412', '555-2589', '555-3698', '555-1478', '555-9632', '555-7896', '555-3214', '555-6547', '555-9874', '555-3216', '555-7894', '555-2587', '555-3698', '555-1478', '555-9632', '555-7896', '555-3214', '555-6547', '555-9874', '555-3216', '555-7894', '555-2587', '555-3698', '555-1478', '555-9632', '555-7896', '555-3214', '555-6547', '555-9874', '555-3216', '555-7894', '555-2587', '555-3698', '555-1478', '555-9632', '555-7896', '555-3214', '555-6547', '555-9874', '555-3216', '555-7894', '555-2587', '555-3698', '555-1478', '555-9632', '555-7896'],
    'Data_di_nascita': ['1980-05-15', '1975-11-30', '1990-03-22', '1965-07-01', '1985-09-18', '1977-09-23', '1961-05-06', '1992-11-23', '1939-05-25', '1967-10-28', '1958-07-08', '1974-05-18', '1963-02-17', '1970-05-22', '1977-01-13', '1974-04-28', '1963-03-27', '1969-05-15', '1955-02-24', '1989-12-13', '1970-04-29', '1974-04-17', '1968-09-25', '1969-07-19', '1933-02-18', '1987-10-18', '1966-09-09', '1981-12-02', '1968-03-30', '1947-01-08', '1990-04-15', '1915-12-12', '1969-10-03', '1968-10-12', '1947-04-21', '1969-02-11', '1977-06-08', '1952-06-07', '1949-06-22', '1981-06-09', '1954-01-29', '1942-06-18', '1970-03-18', '1943-08-17', '1984-11-22', '1956-07-09', '1986-08-21', '1967-07-18', '1955-11-13', '1989-03-20', '1960-05-12', '1978-06-19', '1940-04-25', '1963-12-18', '1975-08-07'],
    'Citta': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'San Francisco', 'Charlotte', 'Indianapolis', 'Seattle', 'Denver', 'Washington', 'Boston', 'El Paso', 'Detroit', 'Nashville', 'Portland', 'Memphis', 'Oklahoma City', 'Las Vegas', 'Louisville', 'Baltimore', 'Milwaukee', 'Albuquerque', 'Tucson', 'Fresno', 'Sacramento', 'Mesa', 'Kansas City', 'Atlanta', 'Long Beach', 'Colorado Springs', 'Raleigh', 'Miami', 'Virginia Beach', 'Omaha', 'Oakland', 'Minneapolis', 'Tulsa', 'Arlington', 'New Orleans', 'Wichita', 'Cleveland', 'Tampa', 'Bakersfield', 'Aurora', 'Anaheim'],
    'Professione': ['Attore', 'Cantante', 'Atleta', 'Regista', 'Modello', 'Musicista', 'Imprenditore', 'Politico', 'Scrittore', 'Comico', 'Chef', 'Giornalista', 'Scienziato', 'Artista', 'Avvocato', 'Medico', 'Insegnante', 'Ingegnere', 'Fotografo', 'Architetto', 'Stilista', 'Ballerino', 'Produttore', 'Presentatore TV', 'Pittore', 'Scultore', 'Pilota', 'Astronauta', 'Archeologo', 'Biologo', 'Psicologo', 'Economista', 'Fisico', 'Chimico', 'Matematico', 'Filosofo', 'Sociologo', 'Antropologo', 'Geologo', 'Zoologo', 'Botanico', 'Veterinario', 'Farmacista', 'Infermiere', 'Dentista', 'Fisioterapista', 'Nutrizionista', 'Personal Trainer', 'Programmatore', 'Web Designer', 'Grafico', 'Traduttore', 'Interprete', 'Archeologo', 'Storico'],
    'Stipendio': [100000, 85000, 120000, 95000, 110000, 75000, 150000, 80000, 90000, 105000, 70000, 88000, 130000, 92000, 115000, 78000, 98000, 140000, 82000, 125000, 72000, 108000, 135000, 94000, 102000, 76000, 112000, 145000, 86000, 118000, 74000, 96000, 128000, 84000, 122000, 79000, 106000, 138000, 89000, 116000, 73000, 99000, 132000, 87000, 124000, 77000, 104000, 142000, 91000, 120000, 75000, 110000, 136000, 93000, 126000],
    'Anni_di_esperienza': [15, 20, 10, 25, 12, 18, 30, 8, 35, 22, 28, 14, 32, 16, 19, 23, 11, 27, 33, 9, 21, 17, 29, 13, 36, 7, 24, 31, 6, 26, 34, 5, 20, 28, 15, 30, 8, 22, 35, 11, 25, 38, 4, 19, 32, 9, 23, 36, 7, 21, 33, 10, 27, 39, 3],
    'Hobby': ['Lettura', 'Giardinaggio', 'Fotografia', 'Cucina', 'Viaggi', 'Sport', 'Pittura', 'Musica', 'Danza', 'Escursionismo', 'Yoga', 'Meditazione', 'Cinema', 'Teatro', 'Scrittura', 'Bricolage', 'Collezionismo', 'Videogiochi', 'Scacchi', 'Pesca', 'Caccia', 'Nuoto', 'Ciclismo', 'Corsa', 'Arrampicata', 'Surf', 'Sci', 'Golf', 'Tennis', 'Basket', 'Calcio', 'Pallavolo', 'Rugby', 'Hockey', 'Boxe', 'Arti marziali', 'Equitazione', 'Vela', 'Canottaggio', 'Paracadutismo', 'Bungee jumping', 'Skydiving', 'Pilates', 'Crossfit', 'Ballo', 'Canto', 'Recitazione', 'Magia', 'Origami', 'Ceramica', 'Scultura', 'Ricamo', 'Maglia', 'Astronomia', 'Birdwatching']
}

demo_df = pd.DataFrame(data)

# Streamlit application
def main():
    print("#################START#################")
    st.set_page_config(page_title="AI Data analysis and generator", page_icon=":brain:", layout="wide")
    
    # Sidebar for API key input
    with st.sidebar:
        st.header("🔑 API Configuration")
        
        # Check if API key exists in environment
        existing_api_key = os.getenv("OPENAI_API_KEY")
        
        if existing_api_key:
            st.success("✅ API Key found in environment")
            api_key_input = None
        else:
            st.warning("⚠️ No API Key found in environment")
            api_key_input = st.text_input(
                "Enter your OpenAI API Key:",
                type="password",
                placeholder="sk-...",
                help="Your OpenAI API key is required to use this application. It will not be stored."
            )
            
            if api_key_input:
                # Set the API key in the environment for this session
                os.environ["OPENAI_API_KEY"] = api_key_input
                st.success("✅ API Key configured for this session")
    
    st.title("🔍GDPR Compliance Analysis and Dataset Generator🛡️")

    # Check if API key is available before proceeding
    if not os.getenv("OPENAI_API_KEY"):
        st.error("🚫 Please provide your OpenAI API key in the sidebar to continue.")
        st.stop()

    # Caricamento del file CSV
    demo_toggle = st.toggle("Demo mode ON",value=True)
    uploaded_file = st.file_uploader("Carica il file CSV", type="csv")
    
    if uploaded_file is not None:
        if demo_toggle:
            df = demo_df
        else:
            # infer separator
            separator = detect_separator(uploaded_file)
            # Carica il file CSV con il separatore determinato
            #loaded_df = pd.read_csv(uploaded_file, sep=separator)
            loaded_df = read_csv_with_encoding(uploaded_file, separator)

            df = loaded_df
        st.write("Dataset originale:")
        st.dataframe(df,hide_index=True)
        #with st.spinner("Checking..."):
        try:
            with st.status("Checking..."):
                analysis_results = []
                for column in df.columns:
                    column_data = df[column]
                    distinct_values = column_data.unique()
                    distribution = column_data.value_counts(normalize=True).to_dict()
                    print(f"Analyzing: {column.lower()}")
                    st.info(f"Analyzing: {column.lower()}",icon="ℹ️")
                    results = check_sensitive_data(column.lower())
                    # print("********INPUT******")
                    # print(results["input"])
                    # print("********context******")
                    # print(results["context"])
                    print("********answer******")
                    print(results["answer"])
                    #print(results)
                    print("*******************************")
                    #make the response lowercase and without punctuation
                    results["answer"] = results["answer"].lower().translate(str.maketrans("", "", string.punctuation))
                    if {results["answer"]} != "no":
                        st.info(f"{column.lower()} is sensitive? {results["answer"]}",icon="🚨")
                    else:
                        st.info(f"{column.lower()} is sensitive? {results["answer"]}",icon="⭐")

                    analysis_results.append({
                        'variable_name': column,
                        'distinct_values': len(distinct_values),
                        'distinct_names': distinct_values,
                        'distribution': distribution,
                        'synthesised': results["answer"],
                        'GDPR_reference': results["context"][0].page_content,
                        'GDPR_Page':results["context"][0].metadata['page']
                    })
                analysis_results_df = pd.DataFrame(analysis_results)
                contatore_synthesised_yes = sum(1 for result in analysis_results if result['synthesised'].lower() != "no") 
            st.success(f"Found {contatore_synthesised_yes} sensible variables, on {len(df.columns)} total variables:")
            st.write(result['variable_name'] + ", " for result in analysis_results if result['synthesised'].lower() != "no")
        except Exception as e:
            st.error(f"An error occurred: {e}")

        with st.expander("Analysis results"):
            st.write("Risultati dell'analisi:")
            st.dataframe(analysis_results_df[["variable_name","distinct_values","synthesised","GDPR_reference","GDPR_Page"]],use_container_width=True,hide_index=True )
            # st.data_editor(analysis_results_df[["variable_name","distinct_values","synthesised","GDPR_reference","GDPR_Page"]],
            #                disabled=["variable_name","distinct_values","GDPR_reference","GDPR_Page"],
            #                column_config={
            #                     "synthesised": st.column_config.CheckboxColumn(
            #                         "Da sintetizzare?",
            #                         help="Seleziona le variabili che vuoi sintetizzare",
            #                         default=False,
            #                     )
            #                 },
            #                 use_container_width=True,
            #                 hide_index=True 
            #                )

        with st.status("Create syntethic data"):
            # Generazione del dataset sintetico
            synthetic_df = generate_synthetic_data(df, analysis_results)
            # Ensure all columns are Arrow-compatible
            synthetic_df = convert_to_arrow_compatible(synthetic_df)
            print("synthetic dataframe created")
        st.write("Dataset sintetico:")
        st.dataframe(synthetic_df,hide_index=True)
    print("#################END#################")
if __name__ == "__main__":
    main()