from django import template
from subprocess import Popen, PIPE
import re
from itertools import chain, zip_longest

from django.utils import timezone


register = template.Library()


@register.filter
def index(indexable, i):
    """
    Returns ith element of a container.

    :param indexable: an indexable container
    :param i: the index
    :return: ith element
    """
    return indexable[i]


@register.filter
def key(obj, k):
    """
    Returns and element of a container by key.

    :param onj: a dictionary
    :param k: key
    :return: element indexed by the provided key
    """
    return obj[k]


@register.filter
def latex_to_html(text):
    """
    Transforms the input latex text into html.

    :param text: latex text
    :return: respective html code
    """

    macros = "\\newcommand{\\uv}[1]{``#1''}\n"
    proc = Popen(["pandoc", "-f", "latex", "-t", "html", "--html-q-tags", "--mathjax"],
                            stdin=PIPE, stdout=PIPE, encoding='utf8')
    return proc.communicate(macros + text)[0]


def time_from_now(time):
    """

    :param time: A point in time
    :return: (timedelta) Remaining time to the specified point in time
    """

    now = timezone.now()
    return time - now


@register.filter
def timedelta_to_days_str(interval):
    days = interval.days

    if days < 1:
        word = "dne"
    if days >= 1:
        word = "den"
    if days >= 1.1:
        word = "dne"
    if days >= 2:
        word = "dny"
    if days >= 5:
        word = "dnů"
    return "{0} {1}".format(interval.days, word)


@register.filter
def add_red(hex_code):
    int_code = int(hex_code[1:7], 16)
    r = (int_code >> 16)
    g = (int_code >> 8) % 256
    b = int_code % 256
    r = min(255, r + 30)
    g = max(0, int(g - 30))
    b = max(0, int(b - 30))
    return f"#{hex((r << 16) + (g << 8) + b)[2:]}"
