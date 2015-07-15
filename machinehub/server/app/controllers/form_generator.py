from wtforms import Form, TextField, validators, IntegerField, DecimalField
from wtforms.fields.html5 import core, widgets
from wtforms.fields.core import SelectField
from wtforms.widgets.core import HTMLString, html_params


range_input_type = {'float': 'any',
                    'int': '1'}

single_input_type = {'str': TextField,
                     'int': IntegerField,
                     'float': DecimalField}

types = {'str': str,
         'int': int,
         'float': float}

range_script = '''
        <script type="text/javascript">
          function show%s(num){
                   var result = document.getElementById('result%s');
                   result.innerHTML = num;
          }
          </script>
'''


class Range(widgets.Input):
    """
    Renders an input with type "range".
    """
    input_type = 'range'

    def __init__(self, step=None, min_value=None, max_value=None, default=None):
        self.step = step
        self.min = min_value
        self.max = max_value
        self.default = str(default) or '0'

    def __call__(self, field, **kwargs):
        if self.step is not None:
            kwargs.setdefault('step', self.step)
        if self.min is not None:
            kwargs.setdefault('min', self.min)
        if self.max is not None:
            kwargs.setdefault('max', self.max)
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        html_text = (range_script % (field.name, field.name),
                     '<input %s onChange="show%s(%s.value);"/>' % (html_params(name=field.name,
                                                                               **kwargs),
                                                                   field.name,
                                                                   field.name),
                     '<div class="range_result" id="result%s">%s</div>' % (field.name,
                                                                           self.default))
        return HTMLString('\n'.join(html_text))


def rangeField(step, min_value, max_value, default):
    class cls(core.DecimalField):
        """
        Represents an ``<input type="range">``.
        """
        widget = Range(step=step,
                       min_value=min_value,
                       max_value=max_value,
                       default=default)
    cls.__name__ = 'DecimalRangeField_%s' % step
    return cls


def metaform(name, inputs):
    class MetaForm(Form):
        pass
    MetaForm.__name__ = name
    default = []
    for name, _type, default, _range, allowed_values in inputs:
        if _range:
            _min, _max = _range[0], _range[2]
            step = range_input_type[_type]
            if len(_range) == 3:
                step = _range[1]
            RangeField = rangeField(step, _min, _max, default)
            setattr(MetaForm, name, RangeField(name,
                                               validators=[validators.input_required()],
                                               default=types[_type](default)))
        elif allowed_values:
            choices = []
            default_index = 0
            for value in allowed_values:
                choices.append((value, value))
                if default == value:
                    default_index = value
            setattr(MetaForm, name, SelectField(name,
                                                choices=choices,
                                                validators=[validators.input_required()],
                                                default=default_index))
        elif _type in single_input_type.keys():
            _SingleField = single_input_type[_type]
            setattr(MetaForm, name, _SingleField(name,
                                                 validators=[validators.input_required()],
                                                 default=default))

    return MetaForm
