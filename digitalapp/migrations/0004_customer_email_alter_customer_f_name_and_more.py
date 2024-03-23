# Generated by Django 5.0.2 on 2024-03-22 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalapp', '0003_remove_registration_request_status_seller_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.CharField(default='00', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='f_name',
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='l_name',
            field=models.CharField(max_length=254, null=True),
        ),
    ]