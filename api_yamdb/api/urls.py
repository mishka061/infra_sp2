from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UserViewSet, get_jwt_token,
                       register_user, )

router_v1 = DefaultRouter()
router_v1.register(r'categories', CategoryViewSet, basename='сategories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(r'users', UserViewSet, basename='users')
urlpatterns_auth = [
    path('signup/', register_user, name='register_user'),
    path('token/', get_jwt_token, name='token')
]
urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(urlpatterns_auth)),
]
