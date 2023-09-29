from django.db import models
from .azure_storage import AzureMediaStorage

# Create your models here.

class Message(models.Model):
    prompt = models.TextField()
    response = models.TextField(default='')
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message(prompt={self.prompt}, response={self.response})'
    
class UploadedPDF(models.Model):
    pdf_file = models.FileField(storage=AzureMediaStorage())
    description = models.TextField(default='')
    upload_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.pdf_file.name

class PineconeSettings(models.Model):
    api_key = models.CharField(max_length=100)
    environment = models.CharField(max_length= 100)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"API Key: {self.api_key}, Environment: {self.environment}"
  
class PineconeIndex(models.Model):
    index_name = models.TextField()
    metric = models.TextField()
    dimension = models.IntegerField()

    def __str__(self):
        return f"Index Name: {self.index_name}, Metric: {self.metric}, Dimension: {self.dimension}"

class OpenAIModel(models.Model):
    openai_api_key = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model_name

class ChunkSettings(models.Model):
    chunk_size = models.PositiveIntegerField(default=600)
    chunk_overlap = models.PositiveIntegerField(default=50)

    def __str__(self):
        return f"Chunk Settings - Chunk Size: {self.chunk_size}, Chunk Overlap: {self.chunk_overlap}"