from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

import pandas as pd
import numpy as np
import streamlit as st
from faker import Faker
from openai import OpenAI
import csv
import os
#import string
import re

# Function to select the correct faker function in order to create synthetic data
@st.cache_data
def faker_func_over_openai(var_name):
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API key not found. Please provide it in the sidebar.")
        return "Errore: API key mancante"
    
    # Nome del file CSV da cui importare
    csv_file = "faker_functions.csv"
    # Insieme per memorizzare le funzioni faker (elimina duplicati)
    faker_functions = set()
    # Apri il file CSV e leggi le funzioni
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Salta l'intestazione
            for row in reader:
                faker_functions.add(row[0].strip())  # Aggiungi l'elemento al set (elimina duplicati automaticamente)
    except FileNotFoundError:
        print(f"File {csv_file} non trovato.")
        return None

    base_prompt = (
        f"Which Faker function is best suited to generate the variable '{var_name}'? Here are the options: {', '.join(faker_functions)}. "
        "Select only one of the functions provided, the best option. "
        "Never return a function that is not in the options list. "
        "Just answer with the correct function name, nice formatted."
        "the correct format is like: fake.iban()"
        "always starts with fake. and always ends with ()"
    )

    client = OpenAI()
    max_retries = 10
    previous_function = None

    for attempt in range(max_retries):
        prompt = base_prompt
        if previous_function:
            prompt += f"{previous_function} is the wrong answer. Never answer with {previous_function}."

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise assistant that finds the correct faker function"},
                {"role": "user", "content": prompt}
            ]
        )
        result = completion.choices[0].message.content
        match = re.search('fake.', result)
        result1 = result[match.start():] if match else result
        # remove spaces and punctuation
        selected_function = result1.strip().strip("'")

        if selected_function in faker_functions:
            return selected_function
        else:
            print(f"Attempt {attempt + 1}: '{selected_function}' is not in the list of valid Faker functions.")
            print(result)
            previous_function = selected_function

    return "Errore: Nessuna funzione valida trovata dopo 10 tentativi."


# # Funzione per determinare il separatore del CSV
@st.cache_data
def detect_separator(file):
    sample = file.read(1024)  # Leggi i primi 1024 byte
    file.seek(0)  # Riporta il puntatore del file all'inizio
    if sample.count(b';') > sample.count(b','):
        return ';'
    else:
        return ','

@st.cache_data
def read_csv_with_encoding(file, sep):
    encodings = ['utf-8', 'ISO-8859-1', 'latin1']
    for encoding in encodings:
        try:
            file.seek(0)  # Riporta il puntatore del file all'inizio
            return pd.read_csv(file, sep=sep, encoding=encoding)
        except UnicodeDecodeError:
            continue
    st.error("Non è stato possibile leggere il file con gli encoding disponibili.")
    return None


def save_exec_results(distinct_values, faker_funct):
    fake = Faker('it_IT')
    column_records = []
    for _ in range(distinct_values):
        result = eval(faker_funct)
        # Se il risultato è una lista o un altro tipo iterabile (ma non una stringa),
        # lo estendiamo alla lista principale
        if isinstance(result, (list, tuple, np.ndarray)) and not isinstance(result, str):
            column_records.extend(result)
        else:
            column_records.append(result)
    # Assicuriamoci che tutti gli elementi siano di tipo base (non liste nidificate)
    column_records = [item for item in column_records if not isinstance(item, (list, tuple, np.ndarray))]
    return column_records


# Funzione per generare variabili sintetiche
@st.cache_data
def generate_synthetic_data(df, analysis_results):
    synthetic_df = pd.DataFrame()
    num_var = len(df)
    for result in analysis_results:
        column = result['variable_name']
        distribution = result['distribution']
        distinct_values = result['distinct_values']
        if result['synthesised'].lower() != "no":
            gen_update = f"Genero {num_var} record per la variabile {column}, contenente {distinct_values} valori distinti, con specifica distribuzione."
            print(gen_update)
            st.info(gen_update, icon="ℹ️")
            # Genera dati sintetici mantenendo la distribuzione
            faker_funct = faker_func_over_openai(column)
            print(f"Uso: {faker_funct}")
            st.info(f"Uso: {faker_funct}")
            synthetic_distinct_values = save_exec_results(distinct_values, faker_funct)
            probabilities = list(distribution.values())
            # print(f"data:{len(synthetic_distinct_values)}")
            # print(f"prob:{len(probabilities)}")
            # print(sum(probabilities))
            # Controlla le lunghezze
            if len(synthetic_distinct_values) != len(probabilities):
                original_len = len(probabilities)
                target_len = len(synthetic_distinct_values)
                if original_len == 0:
                    # Handle the case where there are no original probabilities
                    probabilities = [1 / target_len] * target_len
                else:
                    # Ridistribuisci le probabilità per adattarle alla lunghezza dei valori distinti
                    factor = target_len / original_len
                    new_probabilities = []
                    for i in range(target_len):
                        original_index = int(i / factor)
                        new_probabilities.append(probabilities[original_index])
                    # Normalizza le nuove probabilità
                    prob_sum = sum(new_probabilities)
                    probabilities = [p / prob_sum for p in new_probabilities]
            synthetic_values = np.random.choice(synthetic_distinct_values, size=num_var, p=probabilities)
            synthetic_df[column] = synthetic_values
        else:
            synthetic_df[column] = df[column]
    return synthetic_df


def convert_to_arrow_compatible(df):
    for column in df.columns:
        if df[column].dtype == 'object':
            df[column] = df[column].astype(str)
    return df

@st.cache_data
def check_sensitive_data(variable_name):
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API key not found. Please provide it in the sidebar.")
        return {"answer": "error", "context": []}
    
    system_prompt = (
    "You are an assistant for data control tasks in compliance with the GDPR. "
    "Use the following pieces of context to answer the question. answer only if you know the answer"
    "Check if the variable provided contains sensitive data according to GDPR regulations."
    "Consider that GDPR applies to any information relating to an identified or identifiable natural person, either directly or indirectly."
    "just answer yes or no"
    "{context}"
    )
    llm = ChatOpenAI(model="gpt-4o")
    vectorstore = Chroma(persist_directory="./chroma_db",embedding_function=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    results = rag_chain.invoke({"input": "According to the GDPR (General Data Protection Regulation), a data to be protected can be defined as: Any information relating to an identified or identifiable natural person ('data subject')."
                                "An identifiable person is any natural person who can be identified, directly or indirectly, by reference in particular to an identifier such as a name, an identification number, location data, an online identifier or to one or more features of his or her physical, physiological, genetic, mental, economic, cultural or social identity."
                                "It is important to note that the GDPR aims to protect not only data that directly identifies a person, but also data that could be used to indirectly identify that person."
                                f"Uses the text provided to check whether '{variable_name.upper()}' is a type of variable that is subject to GDPR"
                                })
    # results = rag_chain.invoke({"input": "Does {variable_name} contain sensitive data?"
    #                             })
    return results