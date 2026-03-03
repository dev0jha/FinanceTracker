import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, DirectoryLoader, CSVLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

load_dotenv()

# Constants
CHROMA_PATH = ".chroma"
DATA_PATH = "." 

def get_embeddings():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in a .env file.")
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

def index_docs():
    # Load Python files
    py_loader = DirectoryLoader(DATA_PATH, glob="*.py", loader_cls=TextLoader)
    py_docs = py_loader.load()
    
    # Load CSV data
    csv_file = "finance_data.csv"
    if os.path.exists(csv_file):
        csv_loader = CSVLoader(csv_file)
        csv_docs = csv_loader.load()
    else:
        csv_docs = []
        print(f"Warning: {csv_file} not found. Skipping CSV indexing.")
    
    all_docs = py_docs + csv_docs
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(all_docs)
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=get_embeddings(),
        persist_directory=CHROMA_PATH
    )
    return vectorstore

def query_docs(query):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=get_embeddings()
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
    )
    
    response = qa_chain.invoke(query)
    return response["result"]
