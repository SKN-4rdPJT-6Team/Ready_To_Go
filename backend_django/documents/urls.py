from django.urls import path
from . import views

urlpatterns = [
    path('documents/', views.list_documents, name='list_documents'),
    path('documents/<int:document_id>/', views.get_document, name='get_document'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
]
