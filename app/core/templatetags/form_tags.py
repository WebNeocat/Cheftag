from django import template
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

@register.filter
def first_n_words(value, n=10):
    """
    Devuelve las primeras n palabras de un texto
    """
    if value:
        words = value.split()
        if len(words) > n:
            return ' '.join(words[:n]) + '...'
        return value
    return value

@register.filter
def kcal_to_kj(value):
    try:
        kj = float(value) * 4.184
        return int(round(kj))  # redondea al entero más cercano
    except (ValueError, TypeError):
        return ''
