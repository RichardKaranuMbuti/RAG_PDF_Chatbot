from django.shortcuts import render
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
from .models import UploadedPDF, PineconeSettings, PineconeIndex, OpenAIModel, ChunkSettings
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from pinecone.core.client.configuration import Configuration as OpenApiConfiguration


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

    # Retrieve the values from the database
    saved_chunk_settings = ChunkSettings.objects.first()

    if saved_chunk_settings:
        saved_chunk_size = saved_chunk_settings.chunk_size
        saved_chunk_overlap = saved_chunk_settings.chunk_overlap
    else:
        saved_chunk_size = 600  # Default value
        saved_chunk_overlap = 50  # Default value

    chunk_size = saved_chunk_size
    chunk_overlap = saved_chunk_overlap

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
        #openapi_config = OpenApiConfiguration.get_default_copy()
        #openapi_config.proxy = "http://proxy.server:3128"
        if pinecone_settings:
            pinecone.init(api_key=pinecone_settings.api_key, environment=pinecone_settings.environment)#,openapi_config=openapi_config)
            index_name = 'unitech'
            print("Pinecone initialized successfully")
        else:
            return JsonResponse({"error": "Pinecone settings not found in the database"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Failed to initialize Pinecone: {str(e)}"}, status=500)

#Initialilize pinecone
#pinecone_setup()

@csrf_exempt
def get_pinecone_index():
        # Get the first PineconeIndex object
    first_pinecone_index = PineconeIndex.objects.first()

    # Check if an object was found before trying to access its attributes
    if first_pinecone_index:
        index_name = first_pinecone_index.index_name
        return index_name
    else:
        print("Error, no index instance found")
        

# Define index name
#index_name = get_pinecone_index()

@csrf_exempt
def pinecone_index_setup(request):
    index_name = get_pinecone_index()
    print("Index name: ", index_name)
    index_name = index_name
    try:
        pinecone_setup()
        # Delete the index if it exists
        pinecone.delete_index(index_name)
        indexes_list = pinecone.list_indexes()
        print("List 1: ", indexes_list)

        # Initialize Pinecone for a new connection
        pinecone_setup()

        # Get the first PineconeIndex object
        first_pinecone_index = PineconeIndex.objects.first()
        print("first: ", first_pinecone_index)

        # Check if an object was found before trying to access its attributes
        if first_pinecone_index:
            metric = first_pinecone_index.metric
            dimension = first_pinecone_index.dimension
        print("dimension:", dimension)
        print("metric: ", metric)

        metric = metric
        dimension = dimension

        print("metric", metric, "dimension: ", dimension)



        pinecone.create_index(
                name=index_name,
                metric=metric,
                dimension=dimension  # Adjust as needed
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
    

    index_name = get_pinecone_index()

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


#Display pdf files
def get_recent_pdfs(request):
    if request.method == "GET":
        # Retrieve all items from the UploadedPDF model, ordered by upload_date in descending order
        recent_pdfs = UploadedPDF.objects.order_by('-upload_date')

        # Create a list of dictionaries with file names, descriptions, and primary keys
        pdf_list = []
        for pdf in recent_pdfs:
            pdf_dict = {
                'pdf_name': pdf.pdf_file.name.split('/')[-1],
                'description': pdf.description,
                'pk': pdf.pk,  # Add the primary key
            }
            pdf_list.append(pdf_dict)

        # Create a JSON response with the list of dictionaries
        response_data = {
            'pdfs': pdf_list
        }

        return JsonResponse(response_data, safe=False)
    return JsonResponse({"message": "Not allowed"}, status=405)


from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import os

#Deleting doccuments
@csrf_exempt
def delete_document(request, pk):
    # Initialize the response data
    response_data = {}

    try:
        # Try to get the document based on its primary key
        document = UploadedPDF.objects.get(pk=pk)
        print("document: ", document)

        # Extract the actual file name
        file_name = os.path.basename(document.pdf_file.name)

        # Delete the document from the database
        document.delete()

        # Delete the document file from the media folder
        document_path = os.path.join(settings.MEDIA_ROOT, document.pdf_file.name)
        if os.path.exists(document_path):
            os.remove(document_path)

        response_data['success'] = True
        response_data['message'] = f'Document "{file_name}" has been deleted.'
    except ObjectDoesNotExist:
        response_data['success'] = False
        response_data['message'] = f'Document not found in the database.'
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = f'An error occurred: {str(e)}'

    return JsonResponse(response_data)


#Update Vectorstore settings
def pinecone_settings_view(request):
    try:
        # Get the existing Pinecone settings object (assuming only one exists)
        settings = PineconeSettings.objects.first()

        if request.method == 'POST':
            # Handle form submission and update the settings
            api_key = request.POST.get('api_key')
            environment = request.POST.get('environment')
            # Retrieve other fields as needed

            # Update the settings
            settings.api_key = api_key
            settings.environment = environment
            # Update other fields as needed
            settings.save()

            return JsonResponse({'success': True, 'message': 'Settings updated successfully'})

        return render(request, 'settings.html', {'settings': settings})

    except PineconeSettings.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Settings not found'})



def upload_docs_view(request):
    return render(request, 'upload.html')

def send_message_get_response(request):
    return render(request, 'chat.html')

def view_docs(request):
    return render(request, 'view_docs.html')

def process_documents_template(request):
    return render(request, 'process.html')

