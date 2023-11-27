from robocorp.tasks import task
from robocorp import vault

from llama_index import SimpleDirectoryReader, StorageContext
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.vector_stores import TimescaleVectorStore

import textwrap
import os

@task
def my_timescale_loader():
    """Load all data from work item files as vector embeddings to Timescale Vector.
    Uses Llamaindex Simple Directory Reader, supporting multiple file types."""

    # Set up all the credentials from Robocorp Vault
    openai_credentials = vault.get_secret("OpenAI")
    os.environ["OPENAI_API_KEY"] = openai_credentials["key"]
    timescale_credentials = vault.get_secret("Timescale")
    TIMESCALE_SERVICE_URL = timescale_credentials["service-url"]

    # Get work item files and store to local data folder temporatily.
    # TODO

    # Read documents
    documents = SimpleDirectoryReader("data").load_data()
    print("Document ID:", documents[0].doc_id)

    # Create a TimescaleVectorStore to store the documents
    vector_store = TimescaleVectorStore.from_params(
        service_url=TIMESCALE_SERVICE_URL,
        table_name="timescale_robocorp_example",
    )

    # Create a new VectorStoreIndex using the TimescaleVectorStore
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )

    # Query
    query_engine = index.as_query_engine()
    response = query_engine.query("What did the president say about Ketanji Brown Jackson?")
    print(textwrap.fill(str(response), 100))