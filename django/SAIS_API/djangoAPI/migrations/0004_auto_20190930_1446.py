# Generated by Django 2.2.5 on 2019-09-30 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangoAPI', '0003_projectassetrolerecordtbl_project_tbl'),
    ]

    operations = [
        migrations.RenameField(
            model_name='predesignreconciledassetrecordtbl',
            old_name='does_not_exist',
            new_name='entity_exists',
        ),
        migrations.RenameField(
            model_name='predesignreconciledrolerecordtbl',
            old_name='does_not_exist',
            new_name='entity_exists',
        ),
    ]
