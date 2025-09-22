from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Engagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('retainer', 'Retainer'), ('special', 'Special')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('summary', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('suspended', 'Suspended'), ('ended', 'Ended')], default='active', max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('recurrence', models.CharField(default='monthly', max_length=20)),
                ('base_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('default_description', models.TextField(blank=True)),
                ('billing_day', models.PositiveSmallIntegerField(default=1, help_text='Day of month to issue retainer draft')),
                ('tags', models.JSONField(blank=True, default=list)),
                ('last_generated_period', models.CharField(blank=True, help_text='YYYY-MM of latest retainer draft', max_length=7)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engagements', to='clients.client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='engagements_engagement_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='engagements_engagement_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('client__name', 'title'),
                'unique_together': {('client', 'title', 'type')},
            },
        ),
    ]
