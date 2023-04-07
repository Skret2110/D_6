from django import template

register = template.Library()


@register.filter(name='censor')
def censor(value):
    stop_words = ('Война', "сука", 'нападающим')

    for sw in value.split():
        if sw.lower() in stop_words:
            value = value.replace(sw, f"{sw[0]}{'*' * (len(sw) - 1)}")
    return value

