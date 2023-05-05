from rest_framework import serializers
from rest_framework.validators import ValidationError

from .models import User, FriendshipRelation


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


class FriendshipRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendshipRelation
        fields = ('id', 'user_sender', 'user_reciever', 'created_at', 'accept')
        read_only_fields = ('user_sender', 'created_at', 'accept')
        extra_kwargs = {
            'user_sender': {'default': serializers.CurrentUserDefault()},
            'accept': {'default': None},
        }

    def validate(self, attrs):
        if self.context['request'].user == attrs['user_reciever']:
            raise ValidationError('Impossible to make friendship request to yourself!')
        return attrs
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_sender'] = UserSerializer(instance.user_sender).data
        representation['user_reciever'] = UserSerializer(instance.user_reciever).data
        return representation


class FriendshipAcceptSerializer(serializers.ModelSerializer):

    accept = serializers.BooleanField(
        required=True,
    )

    class Meta:
        model = FriendshipRelation
        fields = ('accept',)

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'friend': UserSerializer(instance.user_sender),
            'friendship': 'Accepted' if instance.accept is True else 'Rejected',
        }
        return representation

