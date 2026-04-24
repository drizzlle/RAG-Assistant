from django.contrib import admin
from .models import Document, Chunk

# Register your models here.
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'source_url')
    search_fields = ('title',)

@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'content')
    search_fields = ('content',)