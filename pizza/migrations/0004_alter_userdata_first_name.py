# Generated by Django 3.2.4 on 2021-06-15 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pizza', '0003_alter_userdata_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='first_name',
            field=models.CharField(max_length=150, verbose_name='first name'),
        ),
    ]
