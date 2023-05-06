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

    request_friendship_to_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='user_recipient',
        label='Friendship request to user',
        help_text='Pass here id of user to be requested.'
    )

    class Meta:
        model = FriendshipRelation
        fields = (
            'id',
            'user_sender',
            'user_recipient',
            'created_at',
            'accept',
            'request_friendship_to_user',
        )
        read_only_fields = (
            'user_sender',
            'user_recipient',
            'created_at',
            'accept',
        )
        extra_kwargs = {
            'user_sender': {'default': serializers.CurrentUserDefault()},
            'accept': {'default': None},
        }

    def validate(self, attrs):
        if self.context['request'].user == attrs['user_recipient']:
            raise ValidationError('Impossible to make friendship request to yourself!')
        return attrs
    
    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'friend_sender': UserSerializer(instance.user_sender).data,
            'friend_recipier': UserSerializer(instance.user_recipient).data,
            'status': 'Friends' if instance.accept is True else \
                'Waiting response' if instance.accept is None else \
                'Rejected',
            'updated_at': instance.updated_at,
            'created_at': instance.created_at,     
        }
        return representation 


class FriendshipAcceptSerializer(serializers.ModelSerializer):

    accept = serializers.BooleanField(
        required=True,
        label='Friendship accepting',
        help_text='Accept: true | Reject: false',
    )

    class Meta:
        model = FriendshipRelation
        fields = ('accept',)

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'friend': UserSerializer(instance.user_sender).data,
            'friendship': 'Accepted' if instance.accept is True else 'Rejected',
        }
        return representation

