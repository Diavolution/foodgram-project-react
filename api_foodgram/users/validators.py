from django.core.exceptions import ValidationError


def unavailable_usernames_validator(value):
    if value.lower() == 'me':
        raise ValidationError('Имя пользователя "me" недоступно')
