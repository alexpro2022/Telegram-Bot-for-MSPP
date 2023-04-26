# Generated by Django 4.1.5 on 2023-02-05 13:32

import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CoverageArea",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="название")),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
            ],
            options={
                "verbose_name": "зона охвата",
                "verbose_name_plural": "зоны охвата",
            },
        ),
        migrations.AddField(
            model_name="coveragearea",
            name="parent",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="children",
                to="bot.coveragearea",
                verbose_name="родительская зона охвата",
            ),
        ),
        migrations.AlterModelOptions(
            name="fund",
            options={"ordering": ("name",), "verbose_name": "фонд", "verbose_name_plural": "фонды"},
        ),
        migrations.RemoveField(
            model_name="fund",
            name="city",
        ),
        migrations.RenameField(
            model_name="fund",
            old_name="limitation",
            new_name="age_limit",
        ),
        migrations.RenameModel(
            old_name="limitation",
            new_name="AgeLimit",
        ),
        migrations.AlterField(
            model_name="fund",
            name="age_limit",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="bot.agelimit",
                verbose_name="возрастные ограничения",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="fund",
            name="name",
            field=models.CharField(max_length=256, verbose_name="название"),
        ),
        migrations.AddField(
            model_name="fund",
            name="coverage_area",
            field=mptt.fields.TreeManyToManyField(
                related_name="funds", to="bot.coveragearea", verbose_name="зоны охвата"
            ),
        ),
        migrations.AddField(
            model_name="fund",
            name="description",
            field=models.TextField(default="Описание", verbose_name="описание"),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name="agelimit",
            options={
                "ordering": ("from_age", "to_age"),
                "verbose_name": "возрастное ограничение",
                "verbose_name_plural": "возрастные ограничения",
            },
        ),
        migrations.AlterField(
            model_name="agelimit",
            name="from_age",
            field=models.PositiveSmallIntegerField(verbose_name="нижняя граница"),
        ),
        migrations.AlterField(
            model_name="agelimit",
            name="to_age",
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="верхняя граница"),
        ),
        migrations.AddConstraint(
            model_name="agelimit",
            constraint=models.UniqueConstraint(
                fields=("from_age", "to_age"), name="возрастное ограничение должно быть уникальным"
            ),
        ),
        migrations.AddConstraint(
            model_name="agelimit",
            constraint=models.UniqueConstraint(
                condition=models.Q(("to_age__isnull", True)),
                fields=("from_age",),
                name="значение нижней границы, при не указанной верхней, должно быть уникальным",
            ),
        ),
        migrations.AddConstraint(
            model_name="agelimit",
            constraint=models.CheckConstraint(
                check=models.Q(("from_age__lte", models.F("to_age"))),
                name="нижняя граница не может быть больше верхней",
            ),
        ),
        migrations.DeleteModel(
            name="City",
        ),
    ]
