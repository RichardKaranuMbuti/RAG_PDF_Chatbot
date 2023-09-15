from django.contrib import admin
from django.urls import path,re_path
from . import views




urlpatterns = [
    #path('pinecone-setup/', views.pinecone_setup, name='pinecone_setup'),
    path('upload-pdf/', views.upload_pdf_view, name='upload_pdf'),
    #path('get-pdfs/', views22.get_uploaded_pdf_paths, name='get_pdf_paths'),
    #path('chat/', views22.run_prompt_get_response, name='chatbot_response'),
    path('process-docs/', views.process_documents, name='create_embeddings'),
    path('chat/', views.document_search_view, name='chat'),
    path('upload-docs/', views.upload_docs_view, name='upload_docs'), #Load upload pdf template
    path('chat-page/', views.send_message_get_response, name='send_message'),
]