import os
from timescale_vector import client
from llama_index import SimpleDirectoryReader, StorageContext
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.vector_stores import TimescaleVectorStore
from llama_index.vector_stores.types import VectorStoreQuery, MetadataFilters
import openai
import textwrap

def my_thing():
    os.environ["OPENAI_API_KEY"] = "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"
    openai.api_key = "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"

    TIMESCALE_SERVICE_URL = "postgres://tsdbadmin:23r#IUN#K68nnf@qx08tqdq1w.coxdn34fiq.tsdb.cloud.timescale.com:37304/tsdb?sslmode=require"

    documents = SimpleDirectoryReader("data").load_data()
    print("Document ID:", documents[0].doc_id)

    # Create a TimescaleVectorStore to store the documents
    vector_store = TimescaleVectorStore.from_params(
        service_url=TIMESCALE_SERVICE_URL,
        table_name="state_of_the_union",
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

my_thing()