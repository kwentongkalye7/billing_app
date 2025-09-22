from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('engagements', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('number', models.CharField(blank=True, max_length=50, unique=True)),
                ('period', models.CharField(help_text='YYYY-MM', max_length=7)),
                ('issue_date', models.DateField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('currency', models.CharField(default='PHP', max_length=3)),
                ('notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('pending_review', 'Pending Review'), ('issued', 'Issued'), ('void', 'Void'), ('settled', 'Settled')], default='draft', max_length=20)),
                ('pdf_path', models.CharField(blank=True, max_length=255)),
                ('sub_total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('paid_to_date', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('idempotency_hash', models.CharField(blank=True, max_length=255)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='billing_statements', to='clients.client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statements_billingstatement_created', to=settings.AUTH_USER_MODEL)),
                ('engagement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='billing_statements', to='engagements.engagement')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statements_billingstatement_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-issue_date', '-created_at'),
                'unique_together': {('client', 'engagement', 'period')},
            },
        ),
        migrations.CreateModel(
            name='BillingItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('qty', models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=10)),
                ('unit', models.CharField(blank=True, max_length=50)),
                ('unit_price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('line_total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('billing_statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='statements.billingstatement')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statements_billingitem_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statements_billingitem_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
    ]
