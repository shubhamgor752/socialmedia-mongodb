# Generated by Django 5.0.7 on 2024-07-25 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administartion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
