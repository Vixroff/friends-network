import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):

    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        db_index=True,
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )


class FriendshipRelation(BaseModel):
    user_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_out')
    user_reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_in')
    accept = models.BooleanField(null=True, blank=True)

    class Meta:
        unique_together = ('user_sender', 'user_reciever')
