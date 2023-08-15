from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from flask import Flask,request,jsonify
import os

def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader=PdfReader(pdf)
        for page in pdf_reader.pages:
            text+=page.extract_text()
    return text


def get_text_chunks(raw_text):
    text_splitter=CharacterTextSplitter(separator='\n',chunk_size=1000,chunk_overlap=200,length_function=len)
    chunks=text_splitter.split_text(raw_text)
    return chunks


def getVectorStores(text_chunks):
    embeddings=OpenAIEmbeddings()
    vector_store=FAISS.from_texts(texts=text_chunks,embedding=embeddings)
    return vector_store

def getConversationalChain(vector_store):
    llm=ChatOpenAI()
    memory=ConversationBufferMemory(memory_key='chat_history',return_messages=True)
    conversation_chain=ConversationalRetrievalChain.from_llm(llm=llm,retriever=vector_store.as_retriever(),memory=memory)
    return conversation_chain

def handleUserQue(conversation,question):
    response=conversation({'question':question})
    chat_history=response['chat_history']

    return response['answer']


raw_text=""
load_dotenv()
pdf_docs=[os.path.join('ChatPDF_Test.pdf')]


# Get the PDFs
raw_text=get_pdf_text(pdf_docs)

# Get the text chunks
text_chunks=get_text_chunks(raw_text)


# Create Vector Stores (Embeddings)
vector_store=getVectorStores(text_chunks)

# Create Conversation
conversation=getConversationalChain(vector_store)


app=Flask(__name__)


@app.route('/')
def index():
    return """<h1><b>PDFxChat </b>: Question Answer Chatting App with PDF</h1>
    <h2> Steps to use this API :</h2>
    <h3>
    1. Request on this url's '/ans' route with argument as 'que' and pass your question inside 'que' argument.<br>
    Example request, 'url/que=who is rohan?'
    It will return response as answer for following question
    </h3>
    """

@app.route('/ans')
def generateAnswer():
    quetion=request.args.get('que','')
    if quetion.strip()=='':
        return "Provide Valid Question"
    return jsonify({"question" : quetion,
            "answer" : handleUserQue(conversation,quetion)
           })


# if __name__=="__main__":
#     app.run(debug=True)