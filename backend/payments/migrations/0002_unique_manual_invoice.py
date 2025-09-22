from django.db import migrations, models


def dedupe_manual_invoice_numbers(apps, schema_editor):
    Payment = apps.get_model('payments', 'Payment')
    seen = set()
    duplicates = []
    for payment in Payment.objects.order_by('id'):
        key = (payment.client_id, payment.manual_invoice_no)
        if key in seen:
            duplicates.append(payment.id)
        else:
            seen.add(key)
    if duplicates:
        Payment.objects.filter(id__in=duplicates).delete()


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(dedupe_manual_invoice_numbers, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.UniqueConstraint(fields=('client', 'manual_invoice_no'), name='unique_manual_invoice_per_client'),
        ),
    ]
