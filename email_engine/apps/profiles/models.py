from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import UserManager
from django.db import models

from apps.core.exceptions import ResourceNotFound
from apps.core.models import BaseModel


# Create your models here.


class People(BaseModel):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    dob = models.DateField()
    gender = models.CharField(max_length=6)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    sms_pref = models.BooleanField()
    email_pref = models.BooleanField()
    account_status = models.CharField(max_length=10)
    last_login = models.DateTimeField(blank=False, null=True)
    active = models.BooleanField(default=True)

    def delete_person(self):
        self.delete()

    @staticmethod
    def get_person(uuid):
        try:
            person = People.objects.get(pk=uuid)
        except People.DoesNotExist:
            raise ResourceNotFound('People', uuid)
        return person

