from django import template

register = template.Library()

@register.filter(name='get_estado_badge')
def get_estado_badge(estado):
    badge_classes = {
        'pendiente': 'info',
        'encamino': 'warning',
        'parcial': 'primary',
        'recibido': 'success',
        'cancelado': 'danger'
    }
    return badge_classes.get(estado, 'secondary')

@register.filter(name='sub')
def sub(value, arg):
    """Filtro para restar valores en templates"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0