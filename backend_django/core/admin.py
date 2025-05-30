from django.contrib import admin
from .models import Document, Conversation, Message, FAQ

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'country', 'topic', 'source', 'created_at']
    list_filter = ['country', 'topic', 'source', 'created_at']
    search_fields = ['title', 'country', 'topic']
    ordering = ['-created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'country', 'topic', 'created_at']
    list_filter = ['country', 'topic', 'created_at']
    search_fields = ['session_id', 'country', 'topic']
    ordering = ['-created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'country', 'topic', 'created_at']
    list_filter = ['country', 'topic', 'created_at']
    search_fields = ['question', 'country', 'topic']
    ordering = ['-created_at']
    
    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question Preview'
