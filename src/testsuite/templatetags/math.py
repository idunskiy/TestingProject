from django import template

register = template.Library()


def mult(value, arg):
    return value * arg


@register.filter(name='div')
def div(value, arg):
    return value / arg

# Simple tag can take unlimited arguments
@register.simple_tag(name='expr')
def expr(value, *args):
    # "(%1 + %2) * %3"
    for idx, arg in enumerate(args, 1):
        value = value.replace(f'%{idx}', str(arg))
    return eval(value)

register.filter('mult', mult)
