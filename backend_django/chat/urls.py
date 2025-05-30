from django.urls import path
from . import views

urlpatterns = [
    path('chat/conversation/', views.create_conversation, name='create_conversation'),
    path('chat/message/', views.process_message, name='process_message'),
    path('chat/history/<int:conversation_id>/', views.get_conversation_history, name='get_conversation_history'),
    path('chat/settings/models/', views.get_available_models, name='get_available_models'),
    path('chat/examples/', views.get_example_questions, name='get_example_questions'),
    path('chat/sources/', views.get_document_sources, name='get_document_sources'),
]
