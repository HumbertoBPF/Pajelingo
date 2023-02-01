from django.core.exceptions import ValidationError

from pajelingo.validators.validators import ERROR_REQUIRED_FIELD

ERROR_LETTER_PASSWORD = "The password must have at least one letter."
ERROR_DIGIT_PASSWORD = "The password must have at least one digit."
ERROR_SPECIAL_CHARACTER_PASSWORD = "The password must have at least one special character."
ERROR_LENGTH_PASSWORD = "The password must have a length between 8 and 30."
ALL_PASSWORD_ERRORS = "{}\n{}\n{}\n{}\n{}".format(ERROR_REQUIRED_FIELD, ERROR_LENGTH_PASSWORD, ERROR_DIGIT_PASSWORD, ERROR_LETTER_PASSWORD, ERROR_SPECIAL_CHARACTER_PASSWORD)

class PasswordLengthValidator(object):
    def __init__(self, min_length=8, max_length=30):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password, user=None):
        if (password is not None) and (self.min_length <= len(password) <= self.max_length):
            return
        raise ValidationError(ERROR_LENGTH_PASSWORD, code='password_length_invalid')

    def get_help_text(self):
        return ERROR_LENGTH_PASSWORD

class PasswordHasLetterValidator(object):
    def validate(self, password, user=None):
        if password is not None:
            for char in password:
                if char.isalpha():
                    return
        raise ValidationError(ERROR_LETTER_PASSWORD, code='password_no_letter')

    def get_help_text(self):
        return ERROR_LETTER_PASSWORD

class PasswordHasDigitValidator(object):
    def validate(self, password, user=None):
        if password is not None:
            for char in password:
                if char.isdigit():
                    return
        raise ValidationError(ERROR_DIGIT_PASSWORD, code='password_no_digit')

    def get_help_text(self):
        return ERROR_DIGIT_PASSWORD

class PasswordHasSpecialCharValidator(object):
    def validate(self, password, user=None):
        if password is not None:
            for char in password:
                if not(char.isalpha() or char.isdigit()):
                    return
        raise ValidationError(ERROR_SPECIAL_CHARACTER_PASSWORD, code='password_no_special_char')

    def get_help_text(self):
        return ERROR_SPECIAL_CHARACTER_PASSWORD