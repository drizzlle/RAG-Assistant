from django.db import models
from pgvector.django import VectorField

# Create your models here.

class Document(models.Model):
    title = models.TextField()
    source_url = models.URLField()
    def __str__(self):
        return f"Document {self.title}"
    
class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    embedding_vector = VectorField(dimensions=1536)  # Assuming 1536 dimensions for the embedding
    def __str__(self):
        return f"Chunk of {self.document.title}"