from django.forms import Widget


class MarkdownTextField(Widget):
    template_name = 'pastvina/widgets/markdown_textarea.html'

    def __init__(self, attrs=None):
        default_attrs = {'cols': '70', 'rows': '10'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)