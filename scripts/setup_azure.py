import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "pdf-documents")


def setup_blob_container():
    if not CONNECTION_STRING:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING manquant dans .env")

    client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = client.get_container_client(CONTAINER_NAME)

    try:
        container_client.create_container()
        print(f"[OK] Container '{CONTAINER_NAME}' créé avec succès.")
    except ResourceExistsError:
        print(f"[OK] Container '{CONTAINER_NAME}' existe déjà.")

    props = container_client.get_container_properties()
    print(f"[INFO] Statut : {props['lease']['status']}, URL : {container_client.url}")


if __name__ == "__main__":
    setup_blob_container()
