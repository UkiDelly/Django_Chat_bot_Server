from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(
            self, nickname, email, social_type="email", sns_id=None, password=None
    ):
        if not email:
            raise ValueError("이메일을 입력해주세요")

        user = self.model(
            sns_id=sns_id,
            social_type=social_type,
            email=self.normalize_email(email),
            nickname=nickname,
            created_at=datetime.now(),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname, email, password):
        user = self.create_user(
            nickname=nickname,
            social_type="email",
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    class SocialType(models.TextChoices):
        EMAIL = "email"
        GOOGLE = "google"

    nickname = models.CharField(max_length=100)
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    sns_id = models.CharField(max_length=100, default=None, blank=True, null=True)
    social_type = models.CharField(
        max_length=10,
        choices=SocialType.choices,
        default=SocialType.EMAIL,
    )
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    chat_count = models.PositiveIntegerField(default=0, max_length=5)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = [
        "nickname",
    ]

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def to_json(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "email": self.email,
            "sns_id": self.sns_id,
            "social_type": self.social_type,
            "chat_count": self.chat_count
        }


class MyTokenModel:
    def __init__(self, access_token, refresh_token):
        self.access_token = str(access_token)
        self.refresh_token = str(refresh_token)

    def to_json(self):
        return {"access_token": self.access_token, "refresh_token": self.refresh_token}
