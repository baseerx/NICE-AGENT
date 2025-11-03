from django.db import models


class MSSQLSequentialUUIDField(models.UUIDField):
    """
    A UUID field that uses SQL Server's NEWSEQUENTIALID() for auto-generation.
    """

    def db_type(self, connection):
        # Ensure the database column is of type uniqueidentifier
        return 'uniqueidentifier'

    def _check_default(self):
        # Prevent Django from complaining about the lack of a Python-side default
        return []

    def deconstruct(self):
        """
        Prevent Django migrations from trying to serialize our SQL default.
        """
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop('default', None)
        return name, path, args, kwargs
