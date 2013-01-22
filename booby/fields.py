# -*- coding: utf-8 -*-
#
# Copyright 2012 Jaime Gil de Sagredo Luna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The `fields` module contains a list of `Field` classes
for model's definition.

The example below shows the most common fields and builtin validations::

    class Token(Model):
        key = StringField()
        secret = StringField()

    class User(Model):
        login = StringField(required=True)
        name = StringField()
        role = StringField(choices=['admin', 'moderator', 'user'])
        email = EmailField(required=True)
        token = EmbeddedField(Token, required=True)
        is_active = BooleanField(default=False)
"""

from booby import validators as builtin_validators
from booby.base import Field
from booby.models import Model
import datetime


class StringField(Field):
    """:class:`Field` subclass with builtin `string` validation."""

    def __init__(self, *args, **kwargs):
        super(StringField, self).__init__(builtin_validators.String(), *args, **kwargs)


class IntegerField(Field):
    """:class:`Field` subclass with builtin `integer` validation."""

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(builtin_validators.Integer(), *args, **kwargs)


class FloatField(Field):
    """:class:`Field` subclass with builtin `float` validation."""

    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(builtin_validators.Float(), *args, **kwargs)


class BooleanField(Field):
    """:class:`Field` subclass with builtin `bool` validation."""

    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(builtin_validators.Boolean(), *args, **kwargs)


class EmbeddedField(Field):
    """:class:`Field` subclass with builtin embedded :class:`models.Model`
    validation.

    """

    def __init__(self, model, *args, **kwargs):
        super(EmbeddedField, self).__init__(builtin_validators.Model(model),
            *args, **kwargs)

        self.model = model

    def __set__(self, instance, value):
        if isinstance(value, dict):
            value = self.model(**value)

        super(EmbeddedField, self).__set__(instance, value)

    def to_plain(self, value):
        return value and value.to_plain() or None


class ListField(Field):
    """:class:`Field` subclass validates a list of another fields or models.
    """
    def __init__(self, validators, *args, **kwargs):
        if not isinstance(validators, (tuple, list)):
            validators = (validators,)
        validators = map(lambda v: isinstance(v, Model) and \
            builtin_validators.Model(v) or v, validators)
        super(ListField, self).__init__(
            builtin_validators.List(*validators),
            **kwargs)

    def to_plain(self, value):
        return value and map(lambda s: isinstance(s, Model) and s.to_plain(), value) or None


class DateTimeField(Field):
    """:class:`Field` subclass validates a list of another fields or models.
    """
    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(builtin_validators.DateTime(),
            *args, **kwargs)
        self.format = self.options.get('format', '%Y-%m-%d %H:%M:%S')

    def to_plain(self, value):
        return value and value.strftime(self.format) or value

    def to_python(self, value):
        return value and datetime.datetime.strptime(value, self.format)


class DictField(Field):
    """:class:`Field` subclass validates a list of another fields or models.
    """
    def __init__(self, *args, **kwargs):
        super(DictField, self).__init__(builtin_validators.Dict(),
            *args, **kwargs)


class EmailField(Field):
    """:class:`Field` subclass with builtin `email` validation."""

    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(builtin_validators.Email(), *args, **kwargs)
