# Generated manually to overcome environment restrictions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telemedicine', '0003_prescriptionrequest_lab_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescriptionrequest',
            name='consultation_summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]
