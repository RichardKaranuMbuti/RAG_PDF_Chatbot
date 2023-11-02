from django.contrib import admin
from .models import Message, UploadedPDF, PineconeSettings, PineconeIndex, OpenAIModel, ChunkSettings

# Register your models here.

class MessageAdmin(admin.ModelAdmin):
    list_display = ('prompt', 'response', 'created_on')
admin.site.register(Message)
admin.site.register(UploadedPDF)
admin.site.register(PineconeSettings)
admin.site.register(PineconeIndex)
admin.site.register(OpenAIModel)
admin.site.register(ChunkSettings)

