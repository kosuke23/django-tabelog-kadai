from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User


class UserManager(BaseUserManager):
    def create_user(self, mail_address, password=None, **extra_fields):
        if not mail_address:
            raise ValueError('メールアドレスを入力してください。')
        email = self.normalize_email(mail_address)
        user = self.model(mail_address=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mail_address, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(mail_address, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    MEMBER_TYPE_CHOICES = [
        ('1', '無料'),
        ('2', '有料'),
    ]

    name = models.CharField("氏名", max_length=264)
    furigana = models.CharField(
        "フリガナ", 
        max_length=264, 
        validators=[RegexValidator(
            regex=r'^[ァ-ンヴー]*$', 
            message='フリガナはカタカナで入力してください。'
        )]
    )
    mail_address = models.EmailField("メールアドレス", max_length=264, unique=True)
    EMAIL_FIELD = 'mail_address'
    
    # password = models.CharField("パスワード", max_length=128)  # フィールド名を 'password' に変更
    
    postal_code = models.CharField(
        "郵便番号", 
        max_length=7, 
        validators=[RegexValidator(
            regex=r'^\d{7}$', 
            message='郵便番号は半角数字7桁で入力してください。'
        )]
    )
    address = models.CharField("住所", max_length=264)
    phone_number = models.CharField("電話番号", max_length=15)
    member_type = models.CharField("会員種別", max_length=2, choices=MEMBER_TYPE_CHOICES,  default='1')
    created_at = models.DateTimeField("登録日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'mail_address'
    REQUIRED_FIELDS = ['name']

    
    #def clean(self):
    #    super().clean()
    #    if len(self.password) < 8 or not any(char.isdigit() for char in self.password) or not any(char.isalpha() for char in self.password):
    #        raise ValidationError('パスワードは半角英数字8文字以上で入力してください。')
    

    # def save(self, *args, **kwargs):
    #    if not self.pk or 'password' in kwargs:  # フィールド名を 'password' に変更
    #        self.password = make_password(self.password)
    #    super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField("カテゴリ名", max_length=55)
    created_at = models.DateTimeField("登録日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.name

class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField("店舗名", max_length=264)
    image = models.ImageField("画像", upload_to='store_images/', blank=True, null=True)
    description = models.TextField("説明")
    lowest_price = models.IntegerField("価格帯(下限)")
    highest_price = models.IntegerField("価格帯(上限)")
    opening_time = models.TimeField("営業時間(開店)")
    closing_time = models.TimeField("営業時間(閉店)")
    postal_code = models.CharField("郵便番号", max_length=11)
    address = models.CharField("住所", max_length=264)
    phone_number = models.CharField("電話番号", max_length=55)
    seating_capacity = models.IntegerField("座席数")
    regular_holiday = models.CharField("定休日", max_length=55)
    created_at = models.DateTimeField("登録日", default=timezone.now)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.name
    

class Reservation(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reserved_date = models.DateTimeField()
    reserved_time = models.TimeField()
    number_of_people = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.store.name} - {self.reserved_date} {self.reserved_time} - {self.user.mail_address}'
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    score = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.store.name} - {self.user.name}'
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'store')

    def __str__(self):
        return f'{self.user.name} - {self.store.name}'
    


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.stripe_subscription_id}"