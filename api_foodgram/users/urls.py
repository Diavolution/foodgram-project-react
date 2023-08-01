from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import ProfileViewSet, SubscriptionListViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', ProfileViewSet, basename='users')

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionListViewSet.as_view(),
        name='subscriptions'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
