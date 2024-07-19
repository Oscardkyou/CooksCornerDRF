# Generated by Django 4.2.10 on 2024-07-19 07:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('receipts', '0001_initial'),
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='userprofile.userprofile', verbose_name='author'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='liked_by',
            field=models.ManyToManyField(blank=True, related_name='likes', to='userprofile.userprofile'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='saved_by',
            field=models.ManyToManyField(blank=True, related_name='saves', to='userprofile.userprofile'),
        ),
    ]
