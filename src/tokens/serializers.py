from rest_framework import serializers

from util.rest import fields

from .models import Token
from .permissions import roles


class TokenSerializer(serializers.Serializer):
    token = fields.KeyField(
        source='key', entity_name='Token', read_only=True
    )
    created = serializers.DateTimeField(read_only=True)
    endpoint_path = serializers.CharField(max_length=500)
    permissions = serializers.MultipleChoiceField(
        choices=roles
    )
    note = serializers.CharField(
        max_length=500, required=False
    )

    def get_client_key(self):
        return self.context['view'].client.key

    def create(self, validated_data):

        note = validated_data.pop('note', '')
        token = Token(
            key=Token.generate_key(),
            user=self.get_client_key(),
            note=note,
            **validated_data
        )
        token.put_async()
        return token

    def update(self, instance, validated_data):
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.put_async()
        return instance
