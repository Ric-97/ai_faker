from utils import faker_func_over_openai, save_exec_results
import numpy as np
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="AI Data Generator", page_icon=":bowling:", layout="wide")

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

st.title("Data faker with AI :bowling:")

# Check if API key is available before proceeding
if not os.getenv("OPENAI_API_KEY"):
    st.error("🚫 Please provide your OpenAI API key in the sidebar to continue.")
    st.stop()

class VariableInfo(BaseModel):
    """Informazioni su una variabile."""
    name: str = Field(description="Nome della variabile")
    distinct_values: Optional[int] = Field(description="Numero di valori distinti", default=None)

class DatasetInfo(BaseModel):
    """Informazioni sul dataset."""
    num_records: int = Field(description="Numero di record")
    variables: List[VariableInfo] = Field(description="Lista delle variabili")

# Configurazione del modello ChatOpenAI (only after API key is confirmed)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([DatasetInfo])

# Creazione del prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Sei un assistente che estrae informazioni strutturate sulle variabili dal testo fornito."),
    ("user", "Estrai le seguenti informazioni dal testo: numero di record (obbligatorio) e le informazioni sulle variabili (nome obbligatorio, numero di valori distinti se presente). Testo: {input}")
])

# Configurazione del parser
parser = JsonOutputToolsParser()

# Creazione della catena
chain = prompt | model | parser

# Funzione per processare l'input
def process_input(input_text):
    result = chain.invoke({"input": input_text})
    if result and 'args' in result[0]:
        return DatasetInfo(**result[0]['args'])
    return None

# Input testuale
input_text = st.text_area("Inserisci le informazioni sul dataset:", 
                          "Numero di record: 1000\n\n"
                          "Nome variabile: Età\n"
                          "Numero di valori distinti: 5\n\n"
                          "Nome variabile: Altezza\n"
                          "Numero di valori distinti: 4")

if st.button("Analizza"):
    try:
        dataset_info = process_input(input_text)

        if dataset_info:
            synthetic_df = pd.DataFrame()
            
            variable_list = []
            for variable_info in dataset_info.variables:
                variable_list.append(variable_info.name)
            st.write(f"Creo un dataset di **{dataset_info.num_records}** records","con le variabili: ",", ".join(variable_list))

            for variable_info in dataset_info.variables:
                #st.write("Nome variabile:", variable_info.name)
                faker_funct = faker_func_over_openai(variable_info.name)
                st.write(f"Per **{variable_info.name}** creo **{variable_info.distinct_values}** valori distinti, usando **{faker_funct}**")
                #st.write("Numero di valori distinti:", variable_info.distinct_values)
                synthetic_distinct_values = save_exec_results(variable_info.distinct_values, faker_funct)
                synthetic_values = np.random.choice(synthetic_distinct_values, size=dataset_info.num_records)#, p=probabilities)
                synthetic_df[variable_info.name] = synthetic_values
        else:
            st.error("Non è stato possibile estrarre le informazioni dal testo fornito.")

        if not synthetic_df.empty:
            st.dataframe(synthetic_df, hide_index=True)
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error("Please make sure your OpenAI API key is valid and you have sufficient credits.")