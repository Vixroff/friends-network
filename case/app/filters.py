from rest_framework.filters import BaseFilterBackend


class FriendshipRequestInOutFilter(BaseFilterBackend):
    """
    Filtering friendship requests to incoming or outgoing.
    """

    def filter_queryset(self, request, queryset, view):
        if 'incoming' in request.query_params and 'outgoing' not in request.query_params:
            return queryset.filter(user_recipient=request.user)
        elif 'outgoing' in request.query_params and 'incoming' not in request.query_params:
            return queryset.filter(user_sender=request.user)
        return queryset
