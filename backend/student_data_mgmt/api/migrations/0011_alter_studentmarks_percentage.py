# Generated by Django 5.1.6 on 2025-02-23 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_studentmarks_java_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentmarks',
            name='percentage',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=5),
        ),
    ]
