import base64
import logging

import six
from django import forms
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile, File
from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers

logger = logging.getLogger(__name__)


class MultiFileInput(forms.FileInput):
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs["multiple"] = "multiple"
        return super().render(name, None, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, "getlist"):
            return files.getlist(name)
        else:
            return [files.get(name)]


class MultiFileField(forms.FileField):
    widget = MultiFileInput
    default_error_messages = {
        "min_num": "Ensure at least %(min_num)s files are uploaded (received %(num_files)s).",
        "max_num": "Ensure at most %(max_num)s files are uploaded (received %(num_files)s).",
        "file_size": "File: %(uploaded_file_name)s, exceeded maximum upload size.",
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop("min_num", 0)
        self.max_num = kwargs.pop("max_num", None)
        self.maximum_file_size = kwargs.pop("maximum_file_size", None)
        super().__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            ret.append(super().to_python(item))
        return ret

    def validate(self, data):
        super().validate(data)
        num_files = len(data)
        if len(data) and not data[0]:
            num_files = 0
        if num_files < self.min_num:
            raise ValidationError(
                self.error_messages["min_num"]
                % {"min_num": self.min_num, "num_files": num_files}
            )
            return
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(
                self.error_messages["max_num"]
                % {"max_num": self.max_num, "num_files": num_files}
            )
        for uploaded_file in data:
            if self.maximum_file_size and uploaded_file.size > self.maximum_file_size:
                raise ValidationError(
                    self.error_messages["file_size"]
                    % {"uploaded_file_name": uploaded_file.name}
                )


def to_file_object(field, instance, file):
    if isinstance(file, str) or file is None:
        return field.attr_class(instance, field, file)
    elif isinstance(file, File) and not isinstance(file, FieldFile):
        file_copy = field.attr_class(instance, field, file.name)
        file_copy.file = file
        file_copy._committed = False
        return file_copy
    elif isinstance(file, FieldFile) and not hasattr(file, "field"):
        file.instance = instance
        file.field = field
        file.storage = field.storage
        return file
    else:
        return file


class ArrayFileDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                f"The '{self.field.name}' attribute can only be accessed from {owner.__name__} instances."
            )
        try:
            return [
                to_file_object(self.field.base_field, instance, file)
                for file in instance.__dict__[self.field.name]
            ]
        except Exception as ex:
            logger.error(ex)
            return []

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value


class ArrayFileField(ArrayField):
    descriptor_class = ArrayFileDescriptor

    def set_attributes_from_name(self, name):
        super(ArrayField, self).set_attributes_from_name(name)
        self.base_field.set_attributes_from_name(f"{name}_array")

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, self.descriptor_class(self))

    def pre_save(self, instance, add):
        """Returns field's value just before saving."""
        files = [
            to_file_object(self.base_field, instance, file)
            for file in super(ArrayField, self).pre_save(instance, add)
        ]

        for file_copy in files:
            if file_copy and not file_copy._committed:
                file_copy.save(file_copy.name, file_copy, save=False)

        return files

    def formfield(self, **kwargs):
        defaults = {"form_class": MultiFileField, "max_num": self.size}
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class AnyBase64FileField(Base64FileField):
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                'Expected a dictionary with "file" and "filename" keys.'
            )

        if "file" not in data or "filename" not in data:
            raise serializers.ValidationError(
                'Both "file" and "filename" keys are required.'
            )

        file_data = data["file"]
        filename = data["filename"]

        if not isinstance(file_data, six.string_types):
            raise serializers.ValidationError(
                "File data must be a base64 encoded string."
            )

        if "data:" in file_data and ";base64," in file_data:
            header, file_data = file_data.split(";base64,")

        try:
            decoded_file = base64.b64decode(file_data, validate=True)
        except (base64.binascii.Error, ValueError):
            raise serializers.ValidationError("Invalid base64 format.")

        complete_file_name = filename
        return ContentFile(decoded_file, name=complete_file_name)
