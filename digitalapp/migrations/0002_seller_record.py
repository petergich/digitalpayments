# Generated by Django 5.0.2 on 2024-03-20 20:01

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='seller_record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField(default=django.utils.timezone.now)),
                ('amount', models.IntegerField()),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='digitalapp.seller')),
            ],
        ),
    ]
