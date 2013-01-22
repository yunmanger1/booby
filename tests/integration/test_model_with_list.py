# -*- coding: utf-8 -*-

from nose.tools import assert_raises_regexp

from booby import errors
from booby.models import Model
from booby.fields import StringField, IntegerField, DictField, ListField


class TestModelValidation(object):
    def test_when_list_is_not_set(self):
        cell = Cell(direction=0)
        cell.validate()

    def test_when_modifiers_is_a_list_of_modifiers(self):
        modifier = Modifier(name="bomb")
        cell = Cell(direction=0, modifiers=[modifier])
        cell.validate()

    # def test_when_karma_is_not_an_integer_then_raises_validation_error(self):
    #     user = User(login=u'root', karma=u'max')

    #     with assert_raises_regexp(errors.ValidationError, 'should be an integer'):
    #         user.validate()

    # def test_when_token_key_is_not_a_string_then_raises_validation_error(self):
    #     user = User(login=u'root', token=Token(key=1))

    #     with assert_raises_regexp(errors.ValidationError, 'should be a string'):
    #         user.validate()

    # def test_when_email_is_an_invalid_email_then_raises_validation_error(self):
    #     user = User(login=u'root', email='root@localhost')

    #     with assert_raises_regexp(errors.ValidationError, 'should be a valid email'):
    #         user.validate()


class Modifier(Model):
    name = StringField()
    kwargs = DictField()


class Cell(Model):
    direction = IntegerField(choices=range(4))
    modifiers = ListField(Modifier, required=False)
