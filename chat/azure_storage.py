
from storages.backends.azure_storage import AzureStorage
from Unitech.deployment import AZURE_PDF_CONTAINER

class AzureMediaStorage(AzureStorage):
    container_name = AZURE_PDF_CONTAINER
