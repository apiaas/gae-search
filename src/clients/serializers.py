from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from util.rest import fields
from .models import User


class UserSerializer(serializers.Serializer):
    id = fields.KeyField(source='key', entity_name=User, read_only=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=500, min_length=2, write_only=True
    )
    is_super_admin = serializers.NullBooleanField()

    def validate_email(self, value):
        user = User.get_by_email(value)
        if user:
            msg = 'User with {} email already exists. (user id={})'
            msg = msg.format(user.email, user.key.id())
            raise serializers.ValidationError(msg)

        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.put()
        return user

    def update(self, instance, validated_data):
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.put_async()
        return instance


class AuthViaEmailSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=500, min_length=3)
    password = serializers.CharField(
        max_length=500, min_length=2, style={'input_type': 'password'}
    )
    user_disabled = _('User account is disabled.')
    invalid_creds = _('Unable to login with provided credentials.')
    missing_creds = _('You must provide "email" and "password"')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError(self.user_disabled)
            else:
                raise serializers.ValidationError(self.invalid_creds)
        else:
            raise serializers.ValidationError(self.missing_creds)

        attrs['user'] = user
        return attrs
