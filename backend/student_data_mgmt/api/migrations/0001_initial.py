# Generated by Django 5.1.6 on 2025-02-18 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('roll', models.IntegerField()),
                ('city', models.CharField(max_length=100)),
                ('Class', models.CharField(max_length=100)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='images/')),
            ],
        ),
    ]
