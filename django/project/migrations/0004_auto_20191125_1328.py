# Generated by Django 2.2.5 on 2019-11-25 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_auto_20191125_1038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectdetails',
            old_name='key_bus_unit_contact',
            new_name='key_business_unit_contact',
        ),
        migrations.RenameField(
            model_name='projectdetails',
            old_name='key_bus_unit_contact_email',
            new_name='key_business_unit_contact_email',
        ),
    ]
