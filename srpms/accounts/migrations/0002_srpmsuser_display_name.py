# Generated by Django 2.2.6 on 2019-10-14 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='srpmsuser',
            name='display_name',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]
