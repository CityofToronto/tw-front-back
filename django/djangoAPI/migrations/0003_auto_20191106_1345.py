# Generated by Django 2.2.5 on 2019-11-06 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangoAPI', '0002_auto_20191105_1622'),
    ]

    operations = [
        migrations.RenameField(
            model_name='constructionphasetbl',
            old_name='designer_organization_name',
            new_name='constructor_organization_name',
        ),
        migrations.AlterField(
            model_name='constructionphasetbl',
            name='contract_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='designprojecttbl',
            name='contract_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='usergroupnametbl',
            name='outside_organization_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]