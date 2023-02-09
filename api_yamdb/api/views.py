from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (IsAdmin, IsAdminModeratorAuthorOrReadOnly,
                          IsAdminOrReadOnly, )
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, RegisterUserSerializer,
                          ReviewSerializer, TitleCreateSerializer,
                          TitleListSerializer, TokenUserSerializer,
                          UserSerializer, )


class UserViewSet(viewsets.ModelViewSet):
    """
        GET - Получение списка всех пользователей, получение пользователя по
        username & me,
        PATCH - изменение данных о пользователе по username & me,
        DELETE - удаление пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ('role',)
    pagination_class = PageNumberPagination
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = [IsAuthenticated, IsAdmin, ]

    @action(
        methods=('GET', 'PATCH'),
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated, ],
    )
    def profile_user(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(
                get_object_or_404(User, id=request.user.id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(request.user, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """POST - отправляется запрос на регистрацию нового пользователя."""
    serializer = RegisterUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, _ = User.objects.get_or_create(
        username=serializer.validated_data.get('username'),
        email=serializer.validated_data.get('email')
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Регистрация нового пользователя',
        message=f'Твой токен: {confirmation_code}',
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    """С помощью POST-запроса отправляется токен пользователю."""
    serializer = TokenUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=serializer.validated_data.get(
        'username'))
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(ListCreateDestroyViewSet):
    """Класс вьюсета для модели категории."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class GenreViewSet(ListCreateDestroyViewSet):
    """Класс вьюсета для модели жанры."""
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Класс вьюсета для модели произведений."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitleCreateSerializer

    permission_classes = [IsAdminOrReadOnly, ]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter


class CommentViewSet(viewsets.ModelViewSet):
    """
        Комментарии к отзывам.
        Комментарий привязан к определённому отзыву.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        ).comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(Review, id=self.kwargs.get('review_id'))
        )


class ReviewViewSet(viewsets.ModelViewSet):
    """
        Отзывы на произведения.
        Отзыв привязан к определённому произведению.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        ).reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(
                Title,
                id=self.kwargs.get('title_id')
            )
        )
