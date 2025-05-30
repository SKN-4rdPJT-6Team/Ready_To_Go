from rest_framework import serializers
from .models import Document, Conversation, Message, FAQ

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    references = serializers.JSONField(required=False)
    
    class Meta:
        model = Message
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

# 요청/응답 전용 시리얼라이저
class ConversationCreateSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=100)
    country_id = serializers.CharField(max_length=100)
    topic_id = serializers.CharField(max_length=100)

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    conversation_id = serializers.IntegerField(required=False)
    session_id = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100, required=False)
    topic = serializers.CharField(max_length=100, required=False)
    model_id = serializers.CharField(max_length=100, required=False)
    stream = serializers.BooleanField(default=False)

class ChatResponseSerializer(serializers.Serializer):
    message = MessageSerializer()
    conversation_id = serializers.IntegerField()
