from app.models import FriendshipRelation, User
from rest_framework import serializers
from rest_framework.validators import ValidationError

from .enums import FriendshipStatus


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


class FriendshipRelationSerializer(serializers.ModelSerializer):

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
            'is_accepted',
            'request_friendship_to_user',
        )
        read_only_fields = (
            'user_sender',
            'user_recipient',
            'created_at',
            'is_accepted',
        )
        extra_kwargs = {
            'user_sender': {'default': serializers.CurrentUserDefault()},
            'is_accepted': {'default': None},
        }

    def validate(self, attrs):
        if self.context['request'].user == attrs['user_recipient']:
            raise ValidationError('Impossible to make friendship request to yourself!')
        return attrs

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'friend_sender': UserSerializer(instance.user_sender).data,
            'friend_recipient': UserSerializer(instance.user_recipient).data,
            'status': (
                FriendshipStatus.accepted if instance.is_accepted is True else
                FriendshipStatus.waiting if instance.is_accepted is None else
                FriendshipStatus.rejected
            ),
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
        }
        return representation


class FriendshipAcceptSerializer(serializers.ModelSerializer):

    is_accepted = serializers.BooleanField(
        required=True,
        label='Friendship request processing',
        help_text='Accept: true | Reject: false',
    )

    class Meta:
        model = FriendshipRelation
        fields = ('user_recipient', 'is_accepted')
        read_only_fields = ('user_recipient',)

    def validate(self, attrs):
        if self.context['request'].user != self.instance.user_recipient:
            raise ValidationError('Only recipient can accept or reject friendship!')
        return attrs

    def to_representation(self, instance):
        representation = {
            'id': instance.id,
            'friend_sender': UserSerializer(instance.user_sender).data,
            'friend_recipient': UserSerializer(instance.user_recipient).data,
            'friendship': (
                FriendshipStatus.accepted if instance.is_accepted is True else
                FriendshipStatus.rejected,
            ),
            'updated_at': instance.updated_at,
        }
        return representation
