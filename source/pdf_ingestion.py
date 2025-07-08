import getpass
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# file_path = "data/CELEX_32016R0679_EN_TXT.pdf"
# loader = PyPDFLoader(file_path)
# docs = loader.load()
# print(len(docs))

#os.environ["OPENAI_API_KEY"] = getpass.getpass()

llm = ChatOpenAI(model="gpt-4o")

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# splits = text_splitter.split_documents(docs)
#Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(),persist_directory="./chroma_db")
# load from disk
vectorstore = Chroma(persist_directory="./chroma_db",embedding_function=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

variable_name = "mail"

system_prompt = (
"You are an assistant for data control tasks in compliance with the GDPR. "
"Use the following pieces of context to answer the question. answer only if you know the answer"
"Check if the variable variable name contains sensitive data according to GDPR regulations."
"just answer yes or no"
"{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)


question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

results = rag_chain.invoke({"input": "Does {variable_name} contain sensitive data?"})

#print(results)
print(results["context"][0].page_content)
print(results["answer"])
print(results["context"][0].metadata['page'])