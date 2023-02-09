from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import (Category, Comment, Genre, Review, Title,
                            User, )


class CategorySerializer(serializers.ModelSerializer):
    """Сеарилизатор категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сеарилизатор жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleListSerializer(serializers.ModelSerializer):
    """Сеарилизатор произведений для чтения."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сеарилизатор произведений для записи."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Комментарии к отзывам."""
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы к произведениям."""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'

    def validate_score(self, value):
        if 1 > value > 10:
            raise serializers.ValidationError('Оценка по шкале от 1 до 10.')
        return value

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(
                author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Можно оставить только один отзыв.'
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]',
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254, required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует!')
        return value


class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=254, required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]',
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['email', 'username']

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Использовать имя \'me\' в качестве username запрещено.'
            )
        return data


class TokenUserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]',
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if not username and not confirmation_code:
            raise serializers.ValidationError(
                f"Пустые поля: {username}, {confirmation_code}"
            )
        return data


class UserProfileSerializer(serializers.Serializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
