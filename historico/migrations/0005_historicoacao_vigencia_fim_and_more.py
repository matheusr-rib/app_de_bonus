# Generated by Django 4.2.23 on 2025-07-09 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('historico', '0004_historicoacao_campanha_nome'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicoacao',
            name='vigencia_fim',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicoacao',
            name='vigencia_inicio',
            field=models.DateField(blank=True, null=True),
        ),
    ]
