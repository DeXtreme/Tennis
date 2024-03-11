# Generated by Django 5.0.3 on 2024-03-11 15:26

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courts', '0002_delete_booking'),
    ]

    operations = [
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('worker_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField()),
                ('email', models.EmailField(max_length=254)),
                ('court', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workers', to='courts.court')),
            ],
        ),
    ]
