# Generated by Django 4.2.13 on 2024-05-30 01:07

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=264, verbose_name="氏名")),
                (
                    "furigana",
                    models.CharField(
                        max_length=264,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="フリガナはカタカナで入力してください。", regex="^[ァ-ンヴー]*$"
                            )
                        ],
                        verbose_name="フリガナ",
                    ),
                ),
                (
                    "mail_address",
                    models.EmailField(
                        max_length=264, unique=True, verbose_name="メールアドレス"
                    ),
                ),
                ("member_pass", models.CharField(max_length=128, verbose_name="パスワード")),
                (
                    "postal_code",
                    models.CharField(
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="郵便番号は半角数字7桁で入力してください。", regex="^\\d{7}$"
                            )
                        ],
                        verbose_name="郵便番号",
                    ),
                ),
                ("address", models.CharField(max_length=264, verbose_name="住所")),
                ("phone_number", models.CharField(max_length=15, verbose_name="電話番号")),
                (
                    "member_type",
                    models.CharField(
                        choices=[("FR", "Free"), ("PR", "Premium")],
                        max_length=2,
                        verbose_name="会員種別",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="登録日"
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新日")),
            ],
        ),
    ]