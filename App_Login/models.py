from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

# to automically create Profile or one to one object
from django.db.models.signals import post_save
from django.dispatch import receiver


class MyUserManager(BaseUserManager):
    """ A custom manager to deal with emails with unique identifier """

    def _create_user(self, email, password, **extra_fields):
        # create and save email password
        if not email:
            raise ValueError("Please provide an email")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Create super user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have staff access")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have Superuser access")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True, null=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log in this site')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('When the user is active')
    )

    # Specify unique related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_permissions'
    )

    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(

        User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=264, blank=True)
    full_name = models.CharField(max_length=264, blank=True)
    address_1 = models.TextField(max_length=512, blank=True)
    city = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username + " 's Profile"

    def is_fully_filled(self):
        fields_name = [f.name for f in self._meta.get_fields()]

        for field_name in fields_name:
            value = getattr(self, field_name)
            if value is None or value == '':
                return False

            return True


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
