from rest_framework import serializers
from rest_framework.validators import ValidationError, UniqueTogetherValidator
from django.utils.translation import gettext_lazy as _

from .models import User, FriendshipRequest


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class FriendshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendshipRequest
        fields = '__all__'
        read_only_fields = ('user_sender', 'accept', 'created_at', 'updated_at')
        extra_kwargs = {
            'user_sender': {'default': serializers.CurrentUserDefault()},
            'accept': {'default': None},
        }

    def validate(self, attrs):
        if self.context['request'].user == attrs['user_reciever']:
            raise ValidationError(_('Impossible to make friendship request to yourself'))
        return attrs
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_sender'] = UserSerializer(instance.user_sender).data
        representation['user_reciever'] = UserSerializer(instance.user_reciever).data

        return representation

