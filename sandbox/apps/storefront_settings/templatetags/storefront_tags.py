from django import template

register = template.Library()


@register.simple_tag
def storefront_dept_card_url(url_list, counter):
    """
    Return the background URL for a department card.
    ``counter`` should be ``forloop.counter`` (1-based), matching department order.
    Extra departments (beyond four) reuse the last configured image.
    """
    if not url_list:
        return ""
    try:
        idx = int(counter) - 1
    except (TypeError, ValueError):
        idx = 0
    if idx < 0:
        idx = 0
    if idx >= len(url_list):
        idx = len(url_list) - 1
    return url_list[idx]
