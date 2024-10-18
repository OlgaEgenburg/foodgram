import datetime

from django.core.exceptions import ValidationError


def validate_name(value):
    year_today = datetime.datetime.now().year
    if value > year_today:
        raise ValidationError(
            f'Год выпуска не может быть позднее {year_today}.'
        )
