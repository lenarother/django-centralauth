# Generated by Django 2.1.3 on 2018-11-14 12:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0002_auto_20181107_0932'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'verbose_name': 'Application', 'verbose_name_plural': 'Applications'},
        ),
        migrations.AlterModelOptions(
            name='applicationpermission',
            options={'ordering': ('application', 'repr'), 'verbose_name': 'Application permission', 'verbose_name_plural': 'Application permissions'},
        ),
        migrations.AlterModelOptions(
            name='applicationpermissiongroup',
            options={'ordering': ('application', 'name'), 'verbose_name': 'Application permission group', 'verbose_name_plural': 'Application permission groups'},
        ),
        migrations.AlterField(
            model_name='applicationpermission',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL, verbose_name='Application'),
        ),
        migrations.AlterField(
            model_name='applicationpermission',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date (created)'),
        ),
        migrations.AlterField(
            model_name='applicationpermissiongroup',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL, verbose_name='Application'),
        ),
        migrations.AlterField(
            model_name='applicationpermissiongroup',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='provider.ApplicationPermission', verbose_name='Permissions'),
        ),
        migrations.AlterField(
            model_name='applicationuser',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL, verbose_name='Application'),
        ),
        migrations.AlterField(
            model_name='applicationuser',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date (created)'),
        ),
        migrations.AlterField(
            model_name='applicationuser',
            name='groups',
            field=models.ManyToManyField(blank=True, to='provider.ApplicationPermissionGroup', verbose_name='Groups'),
        ),
        migrations.AlterField(
            model_name='applicationuser',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='provider.ApplicationPermission', verbose_name='Permissions'),
        ),
        migrations.AlterField(
            model_name='applicationuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]