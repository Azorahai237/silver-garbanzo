# Generated by Django 5.1.6 on 2025-03-02 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0003_alter_rating_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='professor',
            name='average_rating',
            field=models.FloatField(default=0.0),
        ),
    ]
