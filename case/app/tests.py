from django.test import TestCase, RequestFactory
from django.urls import reverse, reverse_lazy

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, FriendshipRelation
from .views import (
    RegistrationView,
    FriendshipRequestView,
    FriendshipAcceptView,
    FriendshipView,
    GetRelationView,
)


class BaseViewTest(TestCase):

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

    view = RegistrationView

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        pass
    
    def test_registration(self):
        """Testing the registration of a new user."""

        user = {
            "username": "user",
            "password": "password",
        }
        request = self.factory.post(
            reverse('registration'),
            user,
        )
        response = self.view.as_view()(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

    def test_bad_registration_with_not_unique_username(self):
        """
        Testing the registration of a new user with username that already exists in database.
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
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)


class FriendshipRequestCreateViewTest(BaseViewTest):
    """
    Testing the functionality of creation friendship requests.
    FriendshipRequestView (POST) method.
    """

    url = reverse('requests-list')
    view = FriendshipRequestView

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user1 = User.objects.create(username='user1')
    
    def test_create_friendship_request(self):
        """Creation friendship request instance."""

        request = self.factory.post(
            self.url,
            {'request_friendship_to_user': self.user1.id},
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FriendshipRelation.objects.count(), 1)
        self.assertEqual(FriendshipRelation.objects.filter(
            user_sender=self.test_user,
            user_recipient=self.user1,
            accept=None,
        ).exists(), True)
    
    def test_mutual_friendship_request(self):
        """
        Mutual outgoing friendship request replaces incoming with accept=True(friendship status).
        """

        FriendshipRelation.objects.create(
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
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FriendshipRelation.objects.count(), 1)
        relation = FriendshipRelation.objects.filter(user_sender=self.test_user).first()
        self.assertTrue(relation.accept)
    
    def test_bad_self_friendship_request(self):
        """Impossible to create a friendship request instance to self user object."""

        request = self.factory.post(
            self.url,
            {'request_friendship_to_user': self.test_user.id},
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FriendshipRelation.objects.count(), 0)
    
    def test_bad_dublicate_friendship_request(self):
        """Impossible to create a dublicate friendship request instance."""

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
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FriendshipRelation.objects.count(), 1)
    
    def test_bad_unauthorized_user_friendship_request(self):
        """Anonymous user can't create friendship request."""

        request = self.factory.post(
            self.url,
            {'request_friendship_to_user': self.user1.id},
            content_type='application/json',
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 401)
    
    def test_bad_request_with_sensitive_data_in_body(self):
        """Incoming extra data in Body doesn't change standart behavior."""

        request = self.factory.post(
            self.url,
            {
                'request_friendship_to_user': self.user1.id,
                'accept': 'true'
            },
            content_type='application/json',
            **self.headers,
        )
        response = self.view.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FriendshipRelation.objects.count(), 1)
        self.assertEqual(FriendshipRelation.objects.filter(
            user_sender=self.test_user,
            user_recipient=self.user1,
            accept=None,
        ).exists(), True)


class FriendshipRequestReadViewTest(BaseViewTest):
    """
    Testing a readable functionalities (list, retrieve) of a friendship request resources.
    FriendshipRequestView (GET) methods.
    """

    view = FriendshipRequestView
    list_url = reverse('requests-list')
    
    @classmethod
    def setUpTestData(cls):
        """
        Create a relations set up.

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
            user_sender = user,
            user_recipient = cls.test_user,
            accept=None
        ) for user in users_objects[:2]]
        FriendshipRelation.objects.bulk_create(incoming)
        outgoing = [FriendshipRelation(
            user_sender = cls.test_user,
            user_recipient = user,
            accept=None
        ) for user in users_objects[2:4]]
        FriendshipRelation.objects.bulk_create(outgoing)
        FriendshipRelation.objects.create(
            user_sender=cls.test_user,
            user_recipient=users_objects[4],
            accept=False,
        )
        FriendshipRelation.objects.create(
            user_sender=cls.test_user,
            user_recipient=users_objects[5],
            accept=True,
        )


    def test_list_friendship_requests(self):
        """Testing the retrieving of user's incoming and outgoing friendship requests."""

        request = self.factory.get(
            self.list_url,
            **self.headers
        )
        response = self.view.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
    
    def test_list_with_query_params(self):
        """Return filtered friendship requests by incoming or outgoing status."""

        request_in = self.factory.get(
            self.list_url + '?incoming',
            **self.headers
        )
        request_out = self.factory.get(
            self.list_url + '?outgoing',
            **self.headers
        )
        response_in = self.view.as_view({'get': 'list'})(request_in)
        response_out = self.view.as_view({'get': 'list'})(request_out)
        self.assertEqual(response_in.status_code, 200)
        self.assertEqual(response_out.status_code, 200)
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

    def test_retrieve_friendship_request(self):
        """Testing the retrieving of a user's friendship request instance."""

        friendship_request = FriendshipRelation.objects.filter(
            user_sender=self.test_user,
            accept=None,
        ).first()
        request = self.factory.get(
            reverse('requests-detail', kwargs={'pk': friendship_request.pk}),
            **self.headers,
        )
        response = self.view.as_view({'get': 'retrieve'})(request, pk=friendship_request.pk)
        self.assertEqual(response.status_code, 200)


class FriendshipAcceptViewTest(BaseViewTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
    
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='user1')
        cls.user2 = User.objects.create(username='user2')
    
    def setUp(self):
        token = RefreshToken.for_user(self.user1).access_token
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        self.friendship_request = FriendshipRelation.objects.create(
            user_sender=self.user2,
            user_recipient=self.user1,
        )
    
    def test_process_friendship_request(self):
        """Testing sender user is not allowed to process friendship request."""

        request = self.factory.put(
            reverse('friendships-accept', kwargs={'pk': self.friendship_request.id}),
            {'accept': 'true'},
            content_type='application/json',
            **self.headers,
        )
        response = FriendshipAcceptView.as_view()(request, pk=self.friendship_request.id)
        self.friendship_request.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.friendship_request.accept)

    def test_bad_sender_processes_friendship_request(self):
        """Only recipient is allowed to process friendship request."""

        token = RefreshToken.for_user(self.user2).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

        request = self.factory.put(
            reverse('friendships-accept', kwargs={'pk': self.friendship_request.id}),
            {'accept': 'true'},
            content_type='application/json',
            **headers,
        )
        response = FriendshipAcceptView.as_view()(request, pk=self.friendship_request.id)
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(self.friendship_request.accept)
    
    def test_bad_anonymous_user_processes_friendship_request(self):
        """Testing anonymous user is not allowed to process friendship request."""

        request = self.factory.put(
            reverse('friendships-accept', kwargs={'pk': self.friendship_request.id}),
            {'accept': 'true'},
            content_type='application/json',
        )
        response = FriendshipAcceptView.as_view()(request, pk=self.friendship_request.id)
        self.assertEqual(response.status_code, 401)
        self.assertIsNone(self.friendship_request.accept)


class FriendshipViewTest(BaseViewTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
    
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='user1')
        cls.user2 = User.objects.create(username='user2')
        cls.user3 = User.objects.create(username='user3')
    
    def setUp(self):
        token = RefreshToken.for_user(self.user1).access_token
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        self.friendship = FriendshipRelation.objects.create(
            user_sender=self.user1,
            user_recipient=self.user2,
            accept=True,
        )
    
    def test_list_friendships_of_authenticated_user(self):
        """Testing the retrieving of user's friendships."""

        FriendshipRelation.objects.create(
            user_sender=self.user1,
            user_recipient=self.user3,
            accept=True,
        )
        request = self.factory.get(
            reverse('friendships-list'),
            **self.headers,
        )
        response = FriendshipView.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_friendship_instance(self):
        """Testing the retrieving of a friendship instance."""

        request = self.factory.get(
            reverse('friendships-detail', kwargs={'pk': self.friendship.id}),
            **self.headers,
        )
        response = FriendshipView.as_view({'get': 'retrieve'})(request, pk=self.friendship.pk)
        self.assertEqual(response.status_code, 200)
    
    def test_sender_destroy_friendship_instance(self):
        """Testing the destroying of a friendship instance."""

        request = self.factory.delete(
            reverse('friendships-detail', kwargs={'pk': self.friendship.id}),
            **self.headers,
        )
        response = FriendshipView.as_view({'delete': 'destroy'})(request, pk=self.friendship.pk)
        self.assertEqual(response.status_code, 204)


class GetRelationViewTest(BaseViewTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
    
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='user1')
        cls.user2 = User.objects.create(username='user2')
        cls.user3 = User.objects.create(username='user3')
    
    def setUp(self):
        token = RefreshToken.for_user(self.user1).access_token
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    def get_friendship_relation_with_user(self):
        """Testing the searching relation with user (friendship case)."""

        FriendshipRelation.objects.create(
            user_sender=self.user1,
            user_recipient=self.user2,
            accept=True,
        )

        request = self.factory.get(
            reverse('relations', kwargs={'username': self.user2.username}),
            **self.headers,
        )
        response = GetRelationView.as_view({'get': 'retrieve'})(request, username=self.user2.username)
        self.assertEqual(response.status_code, 200)
    
    def get_request_relation_with_user(self):
        """Testing the searching relation with user (requested case)."""

        FriendshipRelation.objects.create(
            user_sender=self.user1,
            user_recipient=self.user2,
            accept=None,
        )

        request = self.factory.get(
            reverse('relations', kwargs={'username': self.user2.username}),
            **self.headers,
        )
        response = GetRelationView.as_view({'get': 'retrieve'})(request, username=self.user2.username)
        self.assertEqual(response.status_code, 200)
    
    def get_null_relation_with_user(self):
        """Testing the searching relation with user (null case)."""

        request = self.factory.get(
            reverse('relations', kwargs={'username': self.user2.username}),
            **self.headers,
        )
        response = GetRelationView.as_view({'get': 'retrieve'})(request, username=self.user2.username)
        self.assertEqual(response.status_code, 404)
