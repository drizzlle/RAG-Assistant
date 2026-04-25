import os
from django.core.management.base import BaseCommand
import pdfplumber
import requests
from rag.models import Document, Chunk
import hashlib
    

class Command(BaseCommand):
    help = "Ingest all PDF files from the files/ folder."
   
    def handle(self, *args, **options):
        with pdfplumber.open("files/EN-50600.pdf") as pdf:
            all_text = ""
            for page in pdf.pages:
                all_text += page.extract_text()
            chunks = self.chunk_text(all_text)

            file_hash = hashlib.sha256(all_text.encode()).hexdigest()

            if Document.objects.filter(file_hash=file_hash).exists():
                print("Document already ingested, skipping.")
                return

            document = Document.objects.create(title="EN-50600", file_hash=file_hash, source_url="https://www.enisa.europa.eu/publications/en-50600")

            for chunk in chunks:
                embedding = self.embed_text(chunk)
                Chunk.objects.create(
                    document=document,
                    content=chunk,
                    embedding_vector=embedding
                )

            print(f"Saved {len(chunks)} chunks")
            

    def chunk_text(self, text, chunk_size=1000, overlap=150):
        """Chunk the text into smaller pieces."""
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]
    
    def embed_text(self, text):
        response = requests.post("http://localhost:11434/api/embeddings", json={ "model": "nomic-embed-text", "prompt": text })
        return response.json()["embedding"]