from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def to_list(*args):
    return args


@register.simple_tag
def color_tag_links(tags):
    color_range = ['Coral', 'MediumVioletRed', 'LightSlateGray', 'DarkSalmon', 'DarkSlateBlue',
                   'DarkTurquoise', 'Maroon', 'RoyalBlue', 'Sienna', 'Teal']
    result = list()
    itr = 0
    for tag in tags:
        color = color_range[itr]
        itr = (itr + 1) % len(color_range)
        ref = reverse('tagged', args=[tag])
        result.append(format_html('<a style="color: {};" href="{}">{}</a>',
                                  color, ref, tag))
    return result
