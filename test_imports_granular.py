print("Importing langchain_community...")
from langchain_community.document_loaders import TextLoader, DirectoryLoader, CSVLoader
print("Importing langchain_google_genai...")
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
print("Importing langchain_text_splitters...")
from langchain_text_splitters import RecursiveCharacterTextSplitter
print("Importing langchain_chroma...")
from langchain_chroma import Chroma
print("Importing langchain.chains...")
from langchain.chains import RetrievalQA
print("All successful!")
