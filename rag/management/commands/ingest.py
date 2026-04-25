import os
from django.core.management.base import BaseCommand
import pdfplumber
import requests
from rag.models import Document, Chunk
import hashlib
    

class Command(BaseCommand):
    help = "Ingest all PDF files from the files/ folder."
    def handle(self, *args, **options):
            pdf_folder = "files"

            for filename in os.listdir(pdf_folder):
                if not filename.endswith(".pdf"):
                    continue

                filepath = os.path.join(pdf_folder, filename)

                with pdfplumber.open(filepath) as pdf:
                    all_text = ""
                    for page in pdf.pages:
                        all_text += page.extract_text()
                chunks = self.chunk_text(all_text)

                file_hash = hashlib.sha256(all_text.encode()).hexdigest()

                if Document.objects.filter(file_hash=file_hash).exists():
                        print(f"'{filename}' already ingested, skipping.")
                        continue

                title = os.path.splitext(filename)[0]
                document = Document.objects.create(title=title, file_hash=file_hash)                
                for chunk in chunks:
                        embedding = self.embed_text(chunk)
                        Chunk.objects.create(
                            document=document,
                            content=chunk,
                            embedding_vector=embedding
                        )

                print(f"'{filename}' — saved {len(chunks)} chunks")
                    

    def chunk_text(self, text, chunk_size=1000, overlap=150):
        """Chunk the text into smaller pieces."""
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]
    
    def embed_text(self, text):
        response = requests.post("http://localhost:11434/api/embeddings", json={ "model": "nomic-embed-text", "prompt": text })
        return response.json()["embedding"]