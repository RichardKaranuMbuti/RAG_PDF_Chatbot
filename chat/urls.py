from django.contrib import admin
from django.urls import path,re_path
from . import views




urlpatterns = [
    path('pinecone-setup/', views.pinecone_setup, name='pinecone_setup'),
    path('reset/', views.pinecone_index_setup, name='pinecone_index_setup'),
    path('upload-pdf/', views.upload_pdf_view, name='upload_pdf'),
    path('process-docs/', views.process_documents, name='create_embeddings'),
    path('chat/', views.document_search_view, name='chat'),
    path('upload-docs/', views.upload_docs_view, name='upload_docs'), #Load upload pdf template
    path('chat-page/', views.send_message_get_response, name='send_message'),
    path('get_recent_pdfs/', views.get_recent_pdfs, name='get_recent_pdfs'),
    path('view-documents/', views.view_docs, name='view-documents-template'),
    path('delete_document/<int:pk>/', views.delete_document, name='delete_document'),
    path('pinecone-settings/', views.pinecone_settings_view, name='pinecone_settings'),
    path('process-docs-page/', views.process_documents_template, name='process_docs'),

]