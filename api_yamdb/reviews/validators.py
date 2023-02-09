from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_future_year(value):
    """Валидатор поля проверки даты выхода произведения."""
    if value > timezone.now().year:
        raise ValidationError(
            f'Год произведения не может быть больше {timezone.now().year}'
        )
