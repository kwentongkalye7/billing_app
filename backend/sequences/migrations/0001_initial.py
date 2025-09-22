from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('prefix', models.CharField(default='SOA-', max_length=20)),
                ('padding', models.PositiveSmallIntegerField(default=4)),
                ('current_value', models.PositiveIntegerField(default=0)),
                ('reset_rule', models.CharField(choices=[('none', 'No Reset'), ('annual', 'Annual')], default='annual', max_length=10)),
                ('last_reset_at', models.DateField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='sequences_sequence_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='sequences_sequence_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('code',),
            },
        ),
    ]
