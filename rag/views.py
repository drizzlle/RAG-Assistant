from django.shortcuts import render
import requests
from pgvector.django import CosineDistance
from rag.models import Chunk
from django.http import JsonResponse

def search_documents(request):
    query = request.GET.get('q', '')
    answer = ''
    top_chunks = []

    if query:
        response = requests.post("http://localhost:11434/api/embeddings", json={"model": "nomic-embed-text", "prompt": query})
        query_embedding = response.json()["embedding"]

        top_chunks = Chunk.objects.annotate(
            distance=CosineDistance('embedding_vector', query_embedding)
        ).order_by('distance')[:5]

        context = "\n\n".join([chunk.content for chunk in top_chunks])

        llm_response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": (
                "You are a helpful RAG assistant for data center planning. "
                "Answer using only the context below. If the context is insufficient, say so clearly.\n\n"
                f"Question:\n{query}\n\n"
                f"Context:\n{context}\n\n"
                "Answer:"
    ),
            "stream": False
        })

        answer = llm_response.json()["response"]
        source = top_chunks[0].document.title if top_chunks else ""

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'answer': answer, 'source': source})

    return render(request, 'search_results.html', {'query': query})
