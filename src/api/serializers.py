from rest_framework import serializers
from util.rest import fields
from .models import Endpoint

class EndpointSerializer(serializers.Serializer):
    path = fields.PathField(
        source='key', entity_name=Endpoint,
        entity_parent='get_parent()'
    )

    def get_parent(self):
        return self.context['view'].client.key

    def create(self, validated_data):
        endpoint = Endpoint(**validated_data)
        endpoint.put()
        return endpoint
