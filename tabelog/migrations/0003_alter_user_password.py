# Generated by Django 4.2.13 on 2024-06-03 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tabelog", "0002_rename_member_pass_user_password_user_groups_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(max_length=128, verbose_name="password"),
        ),
    ]
