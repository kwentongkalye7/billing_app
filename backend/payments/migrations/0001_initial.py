from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('statements', '0001_initial'),
        ('clients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment_date', models.DateField()),
                ('amount_received', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='PHP', max_length=3)),
                ('method', models.CharField(choices=[('cash', 'Cash'), ('check', 'Check'), ('bpi_transfer', 'BPI Bank Transfer'), ('bdo_transfer', 'BDO Bank Transfer'), ('lbp_transfer', 'LBP Bank Transfer'), ('gcash', 'GCash')], max_length=20)),
                ('manual_invoice_no', models.CharField(max_length=50)),
                ('reference_no', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('posted', 'Posted'), ('verified', 'Verified'), ('void', 'Void')], default='draft', max_length=20)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='clients.client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_payment_created', to=settings.AUTH_USER_MODEL)),
                ('recorded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments_recorded', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_payment_updated', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payments_verified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-payment_date', '-created_at'),
            },
        ),
        migrations.CreateModel(
            name='UnappliedCredit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('reason', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(choices=[('open', 'Open'), ('applied', 'Applied'), ('refunded', 'Refunded')], default='open', max_length=20)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unapplied_credits', to='clients.client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_unappliedcredit_created', to=settings.AUTH_USER_MODEL)),
                ('source_payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unapplied_credits', to='payments.payment')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_unappliedcredit_updated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount_applied', models.DecimalField(decimal_places=2, max_digits=12)),
                ('billing_statement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='allocations', to='statements.billingstatement')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_paymentallocation_created', to=settings.AUTH_USER_MODEL)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocations', to='payments.payment')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_paymentallocation_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('payment', 'billing_statement')},
            },
        ),
    ]
