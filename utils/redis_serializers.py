from django.core import serializers
from utils.json_encoder import JSONEncoder


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