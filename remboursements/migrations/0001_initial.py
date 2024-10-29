# Generated by Django 5.1.2 on 2024-10-29 00:01

import django.db.models.deletion
import remboursements.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RefundRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(help_text='Veuillez expliquer la raison de votre demande de remboursement', verbose_name='Motif du remboursement')),
                ('wave_number', models.CharField(help_text='Votre numéro Wave Mobile', max_length=20, validators=[remboursements.models.validate_wave_number], verbose_name='Numéro Wave')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('refund_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('processed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_refunds', to=settings.AUTH_USER_MODEL)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refund_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Demande de remboursement',
                'verbose_name_plural': 'Demandes de remboursement',
                'ordering': ['-created_at'],
            },
        ),
    ]