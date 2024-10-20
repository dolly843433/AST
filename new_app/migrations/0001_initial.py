# Generated by Django 5.1.2 on 2024-10-19 21:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('rule_id', models.AutoField(primary_key=True, serialize=False)),
                ('rule_name', models.CharField(blank=True, max_length=255, null=True)),
                ('rule_string', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ASTNode',
            fields=[
                ('node_id', models.AutoField(primary_key=True, serialize=False)),
                ('node_type', models.CharField(max_length=50)),
                ('operator', models.CharField(blank=True, max_length=10, null=True)),
                ('field_name', models.CharField(blank=True, max_length=50, null=True)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('left_child', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='left', to='new_app.astnode')),
                ('parent_node', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='new_app.astnode')),
                ('right_child', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='right', to='new_app.astnode')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ast_nodes', to='new_app.rule')),
            ],
        ),
    ]
