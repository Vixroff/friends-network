from http import HTTPStatus

from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from .models import FriendshipRelation, User
from .serializers import FriendshipStatus
from .views import (FriendshipRequestViewSet, FriendshipViewSet,
                    GetRelationView, RegistrationView)


class BaseViewTest(TestCase):
    """
    Base test class that contains request factory, registered user and his auth headers.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(username='test_user')

    def setUp(self):
        token = RefreshToken.for_user(self.test_user).access_token
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}


class RegistrationViewTest(BaseViewTest):
    """
    Testing the capability to register a new users.
    """

    view = RegistrationView

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        pass

    def test_registration(self):
        """
        Registration of a new user.
        """

        user = {
            "username": "user",
            "password": "password",
        }
        request = self.factory.post(
            reverse('registration'),
            user,
        )
        response = self.view.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_bad_registration_with_not_unique_username(self):
        """
        Registration of a new user with username that already exists in database.
        """

        User.objects.create(username='user')
        user = {
            "username": "user",
            "password": "password",
        }
        request = self.factory.post(
            reverse('registration'),
            user
        )
        response = self.view.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)


class FriendshipRequestCreateViewSetTest(BaseViewTest):
    """
    Testing the functionality of creation friendship requests.
    FriendshipRequestView (POST) method.
    """

    url = reverse('requests-list')
    view = FriendshipRequestViewSet

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user1 = User.objects.create(username='user1')

    def test_create_friendship_request(self):
        """
        Authenticated user is able to request a user for friendship.
        """

        request = self.factory.post(
            self.url,
            {'request_friendship_to_user': self.user1.id},
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(FriendshipRelation.objects.count(), 1)
        self.assertEqual(FriendshipRelation.objects.filter(
            user_sender=self.test_user,
            user_recipient=self.user1,
            accept_is=None,
        ).exists(), True)

    def test_mutual_friendship_request(self):
        """
        Mutual friendship request automatically accepts first one.
        """

        relation = FriendshipRelation.objects.create(
            user_sender=self.user1,
            user_recipient=self.test_user,
        )
        request = self.factory.post(
            self.url,
            {'request_friendship_to_user': self.user1.id},
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'post': 'create'})(request)
        relation.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(FriendshipRelation.objects.count(), 1)
        self.assertTrue(relation.accept_is)

    def test_bad_self_friendship_request(self):
        """
        Authenticated user is not able to request for self friendship.
        """

        request = self.factory.post(
            self.url,
            {'request_friendship_to_user': self.test_user.id},
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(FriendshipRelation.objects.count(), 0)

    def test_bad_dublicate_friendship_request(self):
        """
        Authenticated user is not able to repeat existing friendship request.
        """

        FriendshipRelation.objects.create(
            user_sender=self.test_user,
            user_recipient=self.user1,
        )
        request = self.factory.post(
            self.url,
            {'request_friendship_to_user': self.user1.id},
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(FriendshipRelation.objects.count(), 1)

    def test_bad_unauthorized_user_friendship_request(self):
        """
        Anonymous user is not able to create friendship request.
        """

        request = self.factory.post(
            self.url,
            {'request_friendship_to_user': self.user1.id},
            content_type='application/json',
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_bad_request_with_sensitive_data_in_body(self):
        """
        Incoming extra data in body doesn't change standart behavior.
        """

        request = self.factory.post(
            self.url,
            {
                'request_friendship_to_user': self.user1.id,
                'accept_is': 'true'
            },
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(FriendshipRelation.objects.count(), 1)
        self.assertEqual(FriendshipRelation.objects.filter(
            user_sender=self.test_user,
            user_recipient=self.user1,
            accept_is=None,
        ).exists(), True)


class FriendshipRequestReadViewSetTest(BaseViewTest):
    """
    Testing the functionality of reading a friendship request resources.
    FriendshipRequestView (GET) method.
    """

    view = FriendshipRequestViewSet
    url = reverse('requests-list')

    @classmethod
    def setUpTestData(cls):
        """
        Create a relations data setup.

        7 users: 1 base, 6 extra.
        2 incoming friendship request: from user1, user2;
        2 outgoing friendship request: to user3, user4;
        1 accepted friendship request: from user5;
        1 rejected friendship request: from user6;
        """

        super().setUpTestData()
        users = []
        for i in range(1, 7):
            users.append(User(username=f'user{i}'))
        users_objects = User.objects.bulk_create(users)
        incoming = [FriendshipRelation(
            user_sender=user,
            user_recipient=cls.test_user,
            accept_is=None,
        ) for user in users_objects[:2]]
        FriendshipRelation.objects.bulk_create(incoming)
        outgoing = [FriendshipRelation(
            user_sender=cls.test_user,
            user_recipient=user,
            accept_is=None,
        ) for user in users_objects[2:4]]
        FriendshipRelation.objects.bulk_create(outgoing)
        FriendshipRelation.objects.create(
            user_sender=cls.test_user,
            user_recipient=users_objects[4],
            accept_is=False,
        )
        FriendshipRelation.objects.create(
            user_sender=cls.test_user,
            user_recipient=users_objects[5],
            accept_is=True,
        )

    def test_list_friendship_requests(self):
        """Testing clean list action."""

        request = self.factory.get(
            self.url,
            **self.headers
        )
        response = self.view.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data), 4)

    def test_list_with_query_params(self):
        """Testing clean list action with query params."""

        request_in = self.factory.get(
            self.url + '?incoming',
            **self.headers
        )
        request_out = self.factory.get(
            self.url + '?outgoing',
            **self.headers
        )
        response_in = self.view.as_view({'get': 'list'})(request_in)
        response_out = self.view.as_view({'get': 'list'})(request_out)
        self.assertEqual(response_in.status_code, HTTPStatus.OK)
        self.assertEqual(response_out.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_in.data), 2)
        self.assertEqual(len(response_out.data), 2)
        self.assertEqual(
            set([pk['friend_recipient']['id'] for pk in response_in.data]),
            set([str(self.test_user.pk)],)
        )
        self.assertEqual(
            set([pk['friend_sender']['id'] for pk in response_out.data]),
            set([str(self.test_user.pk)],)
        )

    def test_bad_unauthorized_user_cant_list_friendship_requests(self):
        """Unauthorized user cant read any friendship requests."""

        request = self.factory.get(
            self.url,
        )
        response = self.view.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


class FriendshipRequestUpdateViewSetTest(BaseViewTest):
    """
    Testing the capability to update a friendship request status (reject/accept).
    """

    view = FriendshipRequestViewSet

    def setUp(self):
        super().setUp()
        self.user1 = User.objects.create(username='user1')
        self.friendship_request = FriendshipRelation.objects.create(
            user_sender=self.user1,
            user_recipient=self.test_user,
        )

    def test_accept_friendship_request(self):
        """
        User recipient has capability to accept/reject a friendship request.
        """

        request = self.factory.put(
            reverse('requests-detail', kwargs={'pk': self.friendship_request.id}),
            {'accept_is': 'true'},
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'put': 'update'})(request, pk=self.friendship_request.id)
        self.friendship_request.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.friendship_request.accept_is)

    def test_bad_sender_updates_friendship_request(self):
        """
        User sender is not allowed to update the friendship request status.
        """

        token = RefreshToken.for_user(self.user1).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        request = self.factory.put(
            reverse('requests-detail', kwargs={'pk': self.friendship_request.id}),
            {'accept_is': 'true'},
            content_type='application/json',
            **headers,
        )
        response = self.view.as_view({'put': 'update'})(request, pk=self.friendship_request.id)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIsNone(self.friendship_request.accept_is)

    def test_bad_anonymous_user_updates_friendship_request(self):
        """
        Anonymous user is not allowed to update a friendship request status.
        """

        request = self.factory.put(
            reverse('requests-detail', kwargs={'pk': self.friendship_request.id}),
            {'accept_is': 'true'},
            content_type='application/json',
        )
        response = self.view.as_view({'put': 'update'})(request, pk=self.friendship_request.id)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertIsNone(self.friendship_request.accept_is)


class FriendshipViewTest(BaseViewTest):
    """
    Testing the capabilities to have list and destroy actions with accepted friendships.
    """

    view = FriendshipViewSet

    def setUp(self):
        """
        Friendships dataset setup.

        self.test_user has 6 accepted friendships.
        """

        super().setUp()
        users = []
        for i in range(1, 7):
            users.append(User(username=f'user{i}'))
        user_objects = User.objects.bulk_create(users)
        self.friendships = [FriendshipRelation.objects.create(
            user_sender=user,
            user_recipient=self.test_user,
            accept_is=True,
        ) for user in user_objects]

    def test_list_friendships(self):
        """
        Authenticated user is able to get all friendships.
        """

        request = self.factory.get(
            reverse('friendships-list'),
            **self.headers,
        )
        response = self.view.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data), 6)

    def test_list_accepted_only_friendships(self):
        """
        Friendships are only accepted friendship requests.
        """

        user = User.objects.create(username='rejected_user')
        FriendshipRelation.objects.create(
            user_sender=self.test_user,
            user_recipient=user,
            accept_is=False,
        )
        request = self.factory.get(
            reverse('friendships-list'),
            **self.headers,
        )
        response = self.view.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data), 6)

    def test_destroy_friendship_instance(self):
        """
        Authenticated user is able to delete a friendship.
        """

        request = self.factory.delete(
            reverse('friendships-detail', kwargs={'pk': self.friendships[0].id}),
            **self.headers,
        )
        response = self.view.as_view({'delete': 'destroy'})(request, pk=self.friendships[0].pk)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(FriendshipRelation.objects.count(), 5)


class GetRelationViewTest(BaseViewTest):
    """
    Testing the capability to get relation with user.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Relations dataset setup.

        5 users: 1 base, 4 extra.
        4 relations:
            Accepted friendship - self.test_user to user1;
            Rejected friendship - self.test_user to user2;
            Requested friendship - self.test_user to user3;
            None - self.test_user and user4;
        """

        super().setUpTestData()
        users = []
        for i in range(1, 5):
            users.append(User(username=f'user{i}'))
        cls.user_objects = User.objects.bulk_create(users)
        FriendshipRelation.objects.create(
            user_sender=cls.test_user,
            user_recipient=cls.user_objects[0],
            accept_is=True,
        )
        FriendshipRelation.objects.create(
            user_sender=cls.test_user,
            user_recipient=cls.user_objects[1],
            accept_is=False,
        )
        FriendshipRelation.objects.create(
            user_sender=cls.test_user,
            user_recipient=cls.user_objects[2],
            accept_is=None,
        )

    def test_get_accepted_relation(self):
        """
        Testing the accepted friendship case.
        """

        request = self.factory.get(
            reverse('relations-detail', kwargs={'username': self.user_objects[0].username}),
            **self.headers,
        )
        response = GetRelationView.as_view()(request, username=self.user_objects[0].username)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['status'], FriendshipStatus.accepted)

    def test_get_rejected_relation_with_user(self):
        """
        Testing the rejected friendship case.
        """

        request = self.factory.get(
            reverse('relations-detail', kwargs={'username': self.user_objects[1].username}),
            **self.headers,
        )
        response = GetRelationView.as_view()(request, username=self.user_objects[1].username)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['status'], FriendshipStatus.rejected)

    def test_get_requested_only_relation_with_user(self):
        """
        Testing the requested friendship case.
        """

        request = self.factory.get(
            reverse('relations-detail', kwargs={'username': self.user_objects[2].username}),
            **self.headers,
        )
        response = GetRelationView.as_view()(request, username=self.user_objects[2].username)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['status'], FriendshipStatus.waiting)

    def test_get_null_relation_with_user(self):
        """
        Testing the unexisted relation case.
        """

        request = self.factory.get(
            reverse('relations-detail', kwargs={'username': self.user_objects[3].username}),
            **self.headers,
        )
        response = GetRelationView.as_view()(request, username=self.user_objects[3].username)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_get_unexisted_user(self):
        """
        Testing the unexisted user case.
        """

        request = self.factory.get(
            reverse('relations-detail', kwargs={'username': 'lol'}),
            **self.headers,
        )
        response = GetRelationView.as_view()(request, username='lol')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
