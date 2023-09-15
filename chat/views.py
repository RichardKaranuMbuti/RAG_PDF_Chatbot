from django.shortcuts import render

import streamlit as st
from dotenv import load_dotenv #enable app to use variables inside .env
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter #Create smaller text chunks from large one
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS # A vector store that runs locally
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import UploadedPDF, PineconeSettings, PineconeIndex, OpenAIModel
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain


#Document loader
def get_pdf_text(pdf_docs):
    text= ""
    for pdf in pdf_docs: # loop through all out pdfs
        pdf_reader=PdfReader(pdf) # Initialize a pdfReader object which allows us to access the pages
        for page in pdf_reader.pages: # Loop through all the pages
            text += page.extract_text() # Extract the page contents and store in the variable
    return text

#text = get_pdf_text(pdf_docs)

# Transformers
import nltk
nltk.download('punkt')

def get_text_chunks(text):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    chunk_size = 600
    chunk_overlap = 50
    length_function =len
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

#chunks = get_text_chunks(text)


def pinecone_setup():
    try:
        # Initialize Pinecone from the database
        pinecone_settings = PineconeSettings.objects.first()
        if pinecone_settings:
            pinecone.init(api_key=pinecone_settings.api_key, environment=pinecone_settings.environment)
            index_name = 'unitech'
            print("Pinecone initialized successfully")
        else:
            return JsonResponse({"error": "Pinecone settings not found in the database"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Failed to initialize Pinecone: {str(e)}"}, status=500)

pinecone_setup()


# Define index name
index_name = 'unitech'

def pinecone_index_setup():
    index_name = 'unitech'
    try:
        # Delete the index if it exists
        pinecone.delete_index(index_name)
        
        # Initialize Pinecone for a new connection
        #pinecone_setup()
        
        
        pinecone.create_index(
                name=index_name,
                metric='cosine',
                dimension=1536  # Adjust as needed
            )
        
        # Initialize Pinecone to use the created index
        index = pinecone.Index(index_name)
        
        # Check if the index name is in the list of indexes
        indexes_list = pinecone.list_indexes()
        if index_name in indexes_list:
            return JsonResponse({"success": True})
            print("Index created successfully")
        else:
            return JsonResponse({"success": False, "message": "Index creation failed"})
    
    except Exception as e:
        return JsonResponse({"error": f"Error in Pinecone index setup: {str(e)}"}, status=500)
    

# Create Embeddings
@csrf_exempt
def process_documents(request):

    index_name = 'unitech'

    try:
        

        pinecone_setup()

        pdf_docs = get_uploaded_pdf_paths()
        text = get_pdf_text(pdf_docs)
        chunks = get_text_chunks(text)


        openai_model = OpenAIModel.objects.latest('created_on')
        openai_api_key = openai_model.openai_api_key
        model_name = openai_model.model_name

        embeddings = OpenAIEmbeddings(model=model_name,
                                    openai_api_key=openai_api_key)
        
        vectorstore = Pinecone.from_texts([t for t in chunks], embeddings, index_name=index_name)

        return JsonResponse({"success": True, "message": "Embeddings created successfully"})
    except Exception as e:
        print("Error : ", e)
        return JsonResponse({"error": f"Error in creating embeddings: {str(e)}"}, status=500)
        



# Create a chatbot
@csrf_exempt
def document_search_view(request):

    pinecone_setup()

    index_name = 'unitech'

    print("index_name: ", index_name)

    query = request.POST.get('query', '')
    print("question: ", query)

    openai_model = OpenAIModel.objects.latest('created_on')
    openai_api_key = openai_model.openai_api_key
    model_name = openai_model.model_name


    embeddings = OpenAIEmbeddings(model=model_name,
                                    openai_api_key=openai_api_key)
    try:
        docsearch = Pinecone.from_texts('texts',embeddings,
                                        index_name=index_name)
        
        llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
        chain = load_qa_chain(llm, chain_type="stuff")
        docs = docsearch.similarity_search(query)
        answer = chain.run(input_documents=docs, question=query)
        return JsonResponse({"success": True, "answer": answer})
    except Exception as e:
        print("Error : ", e)
        return JsonResponse({"error": f"Error in chatbot creation: {str(e)}"}, status=500)
        


from .models import UploadedPDF
from .serializers import UploadedPDFSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_pdf_view(request):
    if request.method == 'POST':
        
        description = request.POST.get('description', '')
        files = request.FILES.getlist('pdf_files[]')
        print ("files: ", files)
        # Check if files were uploaded
        if 'pdf_files[]' in request.FILES:
            pdf_files = request.FILES.getlist('pdf_files[]')
            print ("pdf files found : ", pdf_files)

            # Loop through the uploaded PDF files
            for pdf_file in pdf_files:
                # Create a new UploadedPDF instance and save the PDF
                uploaded_pdf = UploadedPDF(pdf_file=pdf_file, description=description)
                uploaded_pdf.save()

            # Retrieve all PDFs saved in the model
            pdf_docs = UploadedPDF.objects.all()

            # Serialize the PDFs using the UploadedPDFSerializer
            serializer = UploadedPDFSerializer(pdf_docs, many=True)

            return JsonResponse({"message": "PDFs uploaded successfully", "status": 200})
        else:
            return JsonResponse({"error": "No PDF files were uploaded"}, status=400)
    else:
        return JsonResponse({"error": "Unsupported request method"}, status=405)


import os
from django.conf import settings

@csrf_exempt
def get_uploaded_pdf_paths():
    pdf_docs = []

    # Loop through all the UploadedPDF objects in the database
    for uploaded_pdf in UploadedPDF.objects.all():
        # Get the PDF file's relative path (without media root)
        pdf_relative_path = str(uploaded_pdf.pdf_file)

        # Create the full path to the PDF file by joining with the media root
        pdf_full_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, pdf_relative_path))

        # Append the PDF file's full path to the list
        pdf_docs.append(pdf_full_path)
    print("pdf_docs inside function: ", pdf_docs)

    # You should return a response, for example, a JSON response with the data
    return pdf_docs


def upload_docs_view(request):
    return render(request, 'upload.html')

def send_message_get_response(request):
    return render(request, 'chat.html')