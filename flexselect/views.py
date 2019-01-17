import json
from itertools import chain

from django.http import HttpResponse
from django.utils.html import format_html
from django.forms.widgets import Select
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required

from flexselect import (FlexSelectWidget, choices_from_instance, 
                        details_from_instance, instance_from_request)


class CustomSelectWidget(Select):

    def render_option(self, selected_choices, option_value, option_label):
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html('<option value="{}"{}>{}</option>',
                           option_value,
                           selected_html,
                           force_text(option_label))


    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(format_html('<optgroup label="{}">', force_text(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append('</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))

        return '\n'.join(output)


@login_required
def field_changed(request):
    """
    Ajax callback called when a trigger field or base field has changed. Returns
    html for new options and details for the dependent field as json.
    """
    hashed_name = request.POST.__getitem__('hashed_name')
    widget = FlexSelectWidget.instances[hashed_name]    
    instance = instance_from_request(request, widget)
    
    if bool(int(request.POST.__getitem__('include_options'))):
        choices = choices_from_instance(instance, widget)
        options = CustomSelectWidget(choices=choices).render_options([], [])
    else:
        options = None
    
    return HttpResponse(json.dumps({
        'options' : options,
        'details': details_from_instance(instance, widget),
        }))
