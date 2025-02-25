from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, modelform_factory, DecimalField, BaseModelFormSet
from django.forms.widgets import Select
from django.core import validators

from bboard.models import Bb, Rubric


# BbForm = modelform_factory(
#     Bb,
#     fields=('title', 'content', 'price', 'rubric'),
#     labels={'title': 'Название товара'},
#     help_texts={'rubric': 'Не забудьте выбрать рубрику!'},
#     field_classes={'price': DecimalField},
#     widgets={'rubric': Select(attrs={'size': 8})}
# )


# class BbForm(ModelForm):
#     class Meta:
#         model = Bb
#         fields = ('title', 'content', 'price', 'rubric')
#         labels = {'title': 'Название товара'}
#         help_texts = {'rubric': 'Не забудьте выбрать рубрику!'}
#         field_classes = {'price': DecimalField}
#         widgets = {'rubric': Select(attrs={'size': 8})}


class BbForm(ModelForm):
    title = forms.CharField(
        label='Название товара',
        validators=[validators.RegexValidator(regex='^.{4,}$')],
        error_messages={'invalid': 'Слишком короткое название товара'}
    )
    content = forms.CharField(label='Описание',
                              widget=forms.widgets.Textarea())
    price = forms.DecimalField(label='Цена', decimal_places=2)
    rubric = forms.ModelChoiceField(queryset=Rubric.objects.all(),
                                    label='Рубрика',
                                    help_text='Не забудьте выбрать рубрику!',
                                    widget=forms.widgets.Select(attrs={'size': 8}))

    def clean_title(self):
        val = self.cleaned_data['title']
        if val == 'Прошлогодний снег':
            raise ValidationError('К продаже не допускается')
        return val

    def clean(self):
        super().clean()
        errors = {}

        if not self.cleaned_data['content']:
            errors['content'] = ValidationError(
                'Укажите описание продаваемого товара'
            )

        if not self.cleaned_data['price'] < 0:
            errors['price'] = ValidationError(
                'Укажите неотрицательное значение цены'
            )

        if errors:
            raise ValidationError(errors)

    class Meta:
        model = Bb
        fields = ('title', 'content', 'price', 'rubric')


class RegisterUserForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль')
    password2 = forms.CharField(label='Пароль (повторно)')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name')


class RubricBaseFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        names = [form.cleaned_data['name'] for form in self.forms
                 if 'name' in form.cleaned_data]
        if ('Недвижимость' not in names) or ('Транспорт' not in names) \
            or ('Мебель' not in names):
            raise ValidationError(
                'Добавьте рубрики недвижимости, транспорта и мебели'
            )
