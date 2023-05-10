from enum import Enum


class FriendshipStatus(str, Enum):
    accepted = 'Friendship is accepted.'
    rejected = 'Friendship is rejected.'
    waiting = 'The request is awaiting a response.'
