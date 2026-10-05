from django.db import models


class SingletonManager(models.Manager):
    def get(self, *args, **kwargs):
        """
        Get will return the singleton instance if it exists and None otherwise.
        """
        return super().first()

    def create(self, **kwargs):
        """
        Creates the singleton if it doesn't already exist.
        Otherwise updates the existing instance.
        """
        singleton = self.get()

        if not singleton:
            return super().create(**kwargs)

        for name, value in kwargs.items():
            setattr(singleton, name, value)

        singleton.save()

        return singleton


class SoftDeletableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(removed_at__isnull=True)
