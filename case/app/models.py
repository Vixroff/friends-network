from typing import Iterable, Optional
import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        db_index=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )


class FriendshipRequest(BaseModel):
    user_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_out')
    user_reseiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_in')
    accept = models.BooleanField(null=True, blank=True)

    class Meta:
        unique_together = ('user_sender', 'user_reseiver')
