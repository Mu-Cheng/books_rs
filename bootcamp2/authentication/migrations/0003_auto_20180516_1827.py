# Generated by Django 2.0.1 on 2018-05-16 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20180514_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='student_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
