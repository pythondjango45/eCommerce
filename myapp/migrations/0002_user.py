# Generated by Django 2.2 on 2020-09-07 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=100)),
                ('lname', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('mobile', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('cpassword', models.CharField(max_length=100)),
            ],
        ),
    ]
