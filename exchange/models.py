from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(
        self, email, first_name, last_name, 
        password=None):
        """
        Creates and saves a User with the given arguments.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        """
        Creates and saves a superuser with the given arguments.
        """
        user = self.create_user(
            email,
            first_name,
            last_name,
            password=password,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)


    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user id identified by their email address
        return self.email

    def __str__(self):
        return self.email

    
    def has_perm(self, perm, obj=None):
        print("#########################################################################")
        print(f"MyUser has_perm invoked with args: 1# {self}, 2# {perm}, 3# {obj}")
        print(f"obj.user: {obj.user.pk} and user_obj: {self.pk} and has_perm should return {obj.user.pk==self.pk}")
        return obj.user.pk==self.pk

    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin and self.is_superuser