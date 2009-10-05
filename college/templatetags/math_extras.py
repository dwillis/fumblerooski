from django import template

register = template.Library()

@register.filter
def percent(value, arg):
    "Returns one value divided by another, multiplied by 100"
    return (float(value) / float(arg)) *100
percent.is_safe = False