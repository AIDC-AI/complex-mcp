from typing import List, Dict, Any
from abc import ABC, abstractmethod
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from shortuuid import uuid

class RAGEngine(ABC):
    @abstractmethod
    def __init__(self, *_, **__):
        pass
    
    @abstractmethod
    def read(self, query: str, k: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def write(self, doc: str, meta_data: Dict[str, str]):
        pass

class ChromaRAG(RAGEngine):
    def __init__(self, name: str = "vec_db"):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name=name)

    def read(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        n_resp = len(results["ids"][0])

        return [{
            "id": results["ids"][0][i],
            "meta_data": results["metadatas"][0][i]
        } for i in range(n_resp)]

    def write(self, doc: str, meta_data: Dict[str, str]):
        node_id = uuid()
        self.collection.add(
            ids=[node_id],
            metadatas=[meta_data],
            documents=[doc]
        )

if __name__ == "__main__":
    rag = ChromaRAG()

    rag.write(
        doc="(send_message) Send a message",
        meta_data={
            "key_name": "send_message"
        }
    )

    rag.write(
        doc="(open_file) Open a file",
        meta_data={
            "key_name": "open_file"
        }
    )

    results = rag.read(query="send a message to Carl")

    print(results)

