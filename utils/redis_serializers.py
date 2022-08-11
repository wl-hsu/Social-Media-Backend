from django.core import serializers
from django_hbase.models import HBaseModel
from utils.json_encoder import JSONEncoder

import json


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        # Django's serializers require a QuerySet or list type of data to serialize by default,
        # so you need to add a [] to instance to become a list
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # You need to add .object to get the original model type object data,
        # otherwise the data obtained is not an ORM object, but a DeserializedObject type
        return list(serializers.deserialize('json', serialized_data))[0].object


class HBaseModelSerializer:

    @classmethod
    def get_model_class(cls, model_class_name):
        for subclass in HBaseModel.__subclasses__():
            if subclass.__name__ == model_class_name:
                return subclass
        raise Exception('HBaseModel {} not found'.format(model_class_name))

    @classmethod
    def serialize(cls, instance):
        json_data = {'model_class_name': instance.__class__.__name__}
        for key in instance.get_field_hash():
            value = getattr(instance, key)
            json_data[key] = value
        return json.dumps(json_data)

    @classmethod
    def deserialize(cls, serialized_data):
        json_data = json.loads(serialized_data)
        model_class = cls.get_model_class(json_data['model_class_name'])
        del json_data['model_class_name']
        return model_class(**json_data)