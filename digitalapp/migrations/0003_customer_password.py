# Generated by Django 5.0.2 on 2024-03-20 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalapp', '0002_remove_customer_user_customer_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='password',
            field=models.CharField(default='0', max_length=254),
            preserve_default=False,
        ),
    ]
