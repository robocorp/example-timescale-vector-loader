from robocorp.tasks import task
from robocorp import vault, workitems

from llama_index import SimpleDirectoryReader, StorageContext
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.vector_stores import TimescaleVectorStore

import textwrap
import os

@task
def my_timescale_loader():
    """Load all data from work item files as vector embeddings to Timescale Vector.
    Uses Llamaindex Simple Directory Reader, supporting multiple file types."""

    # Initialize all things
    TIMESCALE_SERVICE_URL = setup()

    # Work Items are task inputs provided by Robocorp Control Room.
    # They can contain JSON payloads, and file attachments. In case of email trigger,
    # Control Room automatically maps the email contents to a Work Item. In this case,
    # we are only interested in the files. This loops through all input Work Items and
    # stores all theavailable files to a local "data" folder in the execution environment.
    for input in workitems.inputs:
        input.get_files("*", "data")

    # Read documents
    documents = SimpleDirectoryReader("data").load_data()

    # Create a TimescaleVectorStore object
    vector_store = TimescaleVectorStore.from_params(
        service_url=TIMESCALE_SERVICE_URL,
        table_name="timescale_robocorp_example2",
    )

    # Create a new VectorStoreIndex using the TimescaleVectorStore
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )


@task
def query_from_vectordb():
    """Does a query to an existing Timescale Vector embeddings db using Llamaindex."""

    TIMESCALE_SERVICE_URL = setup()

    vector_store = TimescaleVectorStore.from_params(
        service_url=TIMESCALE_SERVICE_URL,
        table_name="timescale_robocorp_example2",
    )

    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Query
    query_engine = index.as_query_engine()
    # response = query_engine.query("What did the president say about Ketanji Brown Jackson?")
    # response = query_engine.query("Which entities were added to the list?")
    response = query_engine.query("what is the cost of green hydrogen from solar PV today in different geographic locations?")
    print(textwrap.fill(str(response), 100))


def setup():
    # Set up all the credentials from Robocorp Vault
    openai_credentials = vault.get_secret("OpenAI")
    os.environ["OPENAI_API_KEY"] = openai_credentials["key"]
    timescale_credentials = vault.get_secret("Timescale")
    return timescale_credentials["service-url"]