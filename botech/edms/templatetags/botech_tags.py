
from django.template import Library

register = Library()


@register.simple_tag
def botech():
    """Very cool test function"""
    raise Exception()
    return u"This is cool!"

