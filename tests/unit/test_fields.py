# -*- coding: utf-8 -*-

from hamcrest import *
from doublex import Stub
from nose.tools import assert_raises, assert_raises_regexp

from booby import fields, errors, models, validators
import datetime


class TestFieldInit(object):
    def test_when_kwargs_then_field_options_is_a_dict_with_these_args(self):
        kwargs = dict(required=True, primary=True, foo=u'bar')

        field = fields.Field(**kwargs)

        assert_that(field.options, has_entries(kwargs))

    def test_when_no_kwargs_then_field_options_is_an_empty_dict(self):
        field = fields.Field()

        assert_that(field.options, is_({}))


class TestFieldDescriptor(object):
    def test_when_access_obj_field_and_value_is_not_assigned_yet_then_is_default(self):
        user = User()

        assert_that(user.name, is_('nobody'))

    def test_when_access_obj_field_and_value_is_already_assigned_then_is_value(self):
        user = User()
        user.name = 'Jack'

        assert_that(user.name, is_('Jack'))

    def test_when_access_class_field_then_is_field_object(self):
        assert_that(User.name, instance_of(fields.Field))


class TestEmbeddedFieldDescriptor(object):
    def test_when_set_field_value_with_dict_then_value_is_embedded_object_with_dict_values(self):
        self.group.admin = {'name': u'foo', 'email': u'foo@example.com'}

        assert_that(self.group.admin, instance_of(User))
        assert_that(self.group.admin.name, is_(u'foo'))
        assert_that(self.group.admin.email, is_(u'foo@example.com'))

    def test_when_set_field_value_with_dict_with_invalid_field_then_raises_field_error(self):
        with assert_raises_regexp(errors.FieldError, 'foo'):
            self.group.admin = {'name': u'foo', 'foo': u'bar'}

    def test_when_set_field_value_with_not_dict_object_then_value_is_given_object(self):
        user = User(name=u'foo', email=u'foo@example.com')
        self.group.admin = user

        assert_that(self.group.admin, is_(user))

    def test_when_set_field_with_not_model_instance_then_value_is_given_object(self):
        user = object()
        self.group.admin = user

        assert_that(self.group.admin, is_(user))

    def setup(self):
        self.group = Group()


class User(models.Model):
    name = fields.StringField(default='nobody')
    email = fields.StringField()


class Group(models.Model):
    name = fields.StringField()
    admin = fields.EmbeddedField(User)


class TestValidateField(object):
    def test_when_validate_without_validation_errors_then_does_not_raise(self):
        validator1 = Stub()
        validator2 = Stub()

        field = fields.Field(validator1, validator2)

        field.validate('foo')

    def test_when_first_validator_raises_validation_error_then_raises_exception(self):
        with Stub() as validator1:
            validator1.validate('foo').raises(errors.ValidationError)

        validator2 = Stub()

        field = fields.Field(validator1, validator2)

        with assert_raises(errors.ValidationError):
            field.validate('foo')

    def test_when_second_validator_raises_validation_error_then_raises_exception(self):
        validator1 = Stub()

        with Stub() as validator2:
            validator2.validate('foo').raises(errors.ValidationError)

        field = fields.Field(validator1, validator2)

        with assert_raises(errors.ValidationError):
            field.validate('foo')


class TestFieldBuiltinValidations(object):
    def test_when_required_is_true_then_value_shouldnt_be_none(self):
        field = fields.Field(required=True)

        with assert_raises_regexp(errors.ValidationError, 'required'):
            field.validate(None)

    def test_when_required_is_false_then_value_can_be_none(self):
        field = fields.Field(required=False)

        field.validate(None)

    def test_when_not_required_then_value_can_be_none(self):
        field = fields.Field()

        field.validate(None)

    def test_when_choices_then_value_should_be_in_choices(self):
        field = fields.Field(choices=['foo', 'bar'])

        with assert_raises_regexp(errors.ValidationError, ' in '):
            field.validate('baz')

    def test_when_not_choices_then_value_can_be_whatever_value(self):
        field = fields.Field()

        field.validate('foo')


class TestEmbeddedFieldBuildtinValidators(object):
    def test_when_value_is_not_instance_of_model_then_raises_validation_error(self):
        with assert_raises_regexp(errors.ValidationError, 'instance of'):
            self.field.validate(object())

    def test_when_embedded_model_field_has_invalid_value_then_raises_validation_error(self):
        with assert_raises_regexp(errors.ValidationError, 'string'):
            self.field.validate(User(name=1))

    def test_when_embedded_model_validates_then_does_not_raise(self):
        self.field.validate(User())

    def setup(self):
        self.field = fields.EmbeddedField(User)


class TestDateFieldToPlain(object):
    def test_when_format_is_not_set(self):
        value = '2013-01-19 14:30:55'
        date = datetime.datetime.strptime(value,
            '%Y-%m-%d %H:%M:%S')
        assert_that(self.field.to_plain(date), equal_to(value))

    def test_when_format_is_set(self):
        value = '2013-01-19 14:30:55'
        date = datetime.datetime.strptime(value,
            '%Y-%m-%d %H:%M:%S')
        assert_that(self.format_field.to_plain(date), equal_to('2013'))

    def test_when_value_is_None(self):
        assert_that(self.format_field.to_plain(None), equal_to(None))

    def setup(self):
        self.field = fields.DateTimeField()
        self.format_field = fields.DateTimeField(format="%Y")


class TestDictField(object):
    def test_when_no_key_validators(self):
        m = SimpleDictModel(data={})
        m.validate()

    def test_when_dict_of_plain_assigned(self):
        m = DictModel()
        m.data = {1: {'length': 4}}
        assert_that(m.data, instance_of(dict))
        assert_that(m.data[1], instance_of(LengthModel))
        assert_that(m.data[1].length, instance_of(int))
        m.validate()

    def test_when_dict_of_typed_assigned(self):
        m = DictModel()
        m.data = {1: LengthModel(length=4)}
        assert_that(m.data, instance_of(dict))
        assert_that(m.data[1], instance_of(LengthModel))
        assert_that(m.data[1].length, instance_of(int))
        m.validate()


class TestListField(object):

    def test_when_list_of_plain_dicts_assigned(self):
        m = ListModel()
        m.data = [{'length': 4}, {'length': 3}]
        assert_that(m.data, instance_of(list))
        assert_that(m.data[0], instance_of(LengthModel))
        assert_that(m.data[0].length, instance_of(int))
        m.validate()

    def test_when_list_of_typed_assigned(self):
        m = ListModel()
        m.data = [LengthModel(length=4), LengthModel(length=3)]
        assert_that(m.data, instance_of(list))
        assert_that(m.data[0], instance_of(LengthModel))
        assert_that(m.data[0].length, instance_of(int))
        assert_that(m.to_plain(), has_entries(data=has_item({'length': 3})))
        m.validate()


class SimpleDictModel(models.Model):
    data = fields.DictField()


class LengthModel(models.Model):
    length = fields.IntegerField()


class DictModel(models.Model):
    data = fields.DictField(key=validators.Integer, value=validators.Model(LengthModel))


class ListModel(models.Model):
    data = fields.ListField(LengthModel)
