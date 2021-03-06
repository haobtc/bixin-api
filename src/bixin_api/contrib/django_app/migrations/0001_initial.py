# Generated by Django 2.0.5 on 2018-06-27 10:43

import bixin_api.contrib.django_app.fields
import bixin_api.contrib.django_app.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BixinUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('username', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('target_id', models.CharField(max_length=32, null=True, unique=True)),
                ('openid', models.CharField(db_index=True, max_length=32, null=True, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('order_id', models.CharField(db_index=True, default=bixin_api.contrib.django_app.models.hex_uuid, max_length=64)),
                ('symbol', models.CharField(max_length=32)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESS', 'SUCCESS'), ('FAILED', 'FAILED')], default='PENDING', max_length=32)),
                ('amount', bixin_api.contrib.django_app.fields.BixinDecimalField(decimal_places=30, default=0, max_digits=65)),
                ('address', models.CharField(max_length=128)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deposit', to='django_app.BixinUser')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('RECEIVED', 'RECEIVED'), ('PROCESSED', 'PROCESSED')], default='RECEIVED', max_length=32)),
                ('event_id', models.IntegerField(db_index=True)),
                ('vendor_name', models.CharField(max_length=50)),
                ('subject', models.CharField(db_index=True, max_length=32)),
                ('payload', bixin_api.contrib.django_app.fields.JsonField(blank=True, default='{}', max_length=5000, null=True)),
                ('uuid', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('order_id', models.CharField(db_index=True, default=bixin_api.contrib.django_app.models.hex_uuid, max_length=64)),
                ('address', models.CharField(blank=True, max_length=128, null=True)),
                ('symbol', models.CharField(max_length=32)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESS', 'SUCCESS'), ('FAILED', 'FAILED')], default='PENDING', max_length=32)),
                ('amount', bixin_api.contrib.django_app.fields.BixinDecimalField(decimal_places=30, default=0, max_digits=65)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdraw', to='django_app.BixinUser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
