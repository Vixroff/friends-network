from django_filters import rest_framework as filters


class FriendshipRequestFilter(filters.FilterSet):

    is_incoming = filters.BooleanFilter(method='filter_is_incoming')
    is_outgoing = filters.BooleanFilter(method='filter_is_outgoing')

    def filter_is_incoming(self, queryset, name, value):
        if value:
            return queryset.filter(user_recipient=self.request.user)
        return queryset
    
    def filter_is_outgoing(self, queryset, name, value):
        if value:
            return queryset.filter(user_sender=self.request.user)
        return queryset
