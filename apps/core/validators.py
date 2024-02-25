from django.core.validators import URLValidator


class OptionalSchemeURLValidator(URLValidator):
    def __call__(self, value):
        if "://" not in value:
            # Validate as if it were http://
            value = "http://" + value
        super(OptionalSchemeURLValidator, self).__call__(value)
