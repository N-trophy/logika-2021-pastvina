from django import template
from subprocess import Popen, PIPE
import re
from itertools import chain, zip_longest

from django.utils import timezone

from pastvina.models import MediaFile


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
def gen_file_refs(text):
    """
    Parses the input text and replaces all occurences of file tags by their respective real urls.
    A tag [[<name>]] is replaced by the url of the file with name <name>.
    Unmatched file tags are ignored (i.e. replaced by an empty string).

    :param  text: input text
    :return: input text with urls replaced
    """
    regexp = r"\[\[[^\[\]]*\]\]"
    matches = [ match[2:-2] for match in re.findall(regexp, text) ]
    context = re.split(regexp, text)

    urls = { f.name: f.content.url for f in MediaFile.objects.filter(name__in=matches)}
    result = [ urls[m] if m in urls else '' for m in matches ]

    return ''.join(list(chain.from_iterable(zip_longest(context, result)))[:-1])


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


@register.filter
def markdown_to_html(text):
    """
    Transforms the input markdown text into html.
    
    :param text: markdown text
    :return: respective html code
    """

    macros = "\\newcommand{\\uv}[1]{``#1''}\n"
    proc = Popen(["pandoc", "-f", "markdown", "-t", "html", "--html-q-tags", "--mathjax"],
                            stdin=PIPE, stdout=PIPE, encoding='utf8')
    return proc.communicate(macros + text)[0]


@register.filter
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
