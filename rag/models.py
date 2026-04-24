from django.db import models
from pgvector.django import VectorField

# Create your models here.

class Document(models.Model):
    title = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64, unique=True)
    source_url = models.URLField(blank=True, null=True)
    def __str__(self):
        return f"Document {self.title}"
    
class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    embedding_vector = VectorField(dimensions=768)  # Assuming 768 dimensions for the embedding
    def __str__(self):
        return f"Chunk of {self.document.title}"