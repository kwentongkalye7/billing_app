from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.contrib.postgres.fields import ArrayField


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('normalized_name', models.CharField(editable=False, max_length=255)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('billing_address', models.TextField(blank=True)),
                ('tin', models.CharField(blank=True, max_length=20)),
                ('tags', ArrayField(base_field=models.CharField(max_length=50), blank=True, default=list, size=None)),
                ('aliases', ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None)),
                ('group', models.CharField(blank=True, max_length=255)),
                ('branding_logo', models.ImageField(blank=True, null=True, upload_to='client_logos/')),
                ('branding_header_note', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_client_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_client_updated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('role', models.CharField(choices=[('billing', 'Billing'), ('ap', 'Accounts Payable'), ('approver', 'Approver'), ('other', 'Other')], default='other', max_length=20)),
                ('is_billing_recipient', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='clients.client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_contact_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_contact_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('client', 'email', 'phone')},
            },
        ),
    ]
