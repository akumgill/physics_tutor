# Generated by Django 5.1.2 on 2024-11-07 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storyboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='img_url',
        ),
        migrations.RemoveField(
            model_name='question',
            name='section',
        ),
        migrations.AddField(
            model_name='question',
            name='img_name',
            field=models.TextField(default='', verbose_name='img_name'),
        ),
    ]
