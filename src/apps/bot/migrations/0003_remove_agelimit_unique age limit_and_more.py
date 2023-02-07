# Generated by Django 4.1.5 on 2023-02-07 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0002_coveragearea_alter_fund_options_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="agelimit",
            name="Unique age limit",
        ),
        migrations.RemoveConstraint(
            model_name="agelimit",
            name="Нужно указать хотя бы одно значение",
        ),
        migrations.AddConstraint(
            model_name="agelimit",
            constraint=models.UniqueConstraint(
                fields=("from_age", "to_age"), name="диапазон возрастов должен быть уникальным"
            ),
        ),
        migrations.AddConstraint(
            model_name="agelimit",
            constraint=models.UniqueConstraint(
                condition=models.Q(("to_age__isnull", True)),
                fields=("from_age",),
                name="значение нижней границы, при не указанном верхнем, должно быть уникальным",
            ),
        ),
        migrations.AddConstraint(
            model_name="agelimit",
            constraint=models.UniqueConstraint(
                condition=models.Q(("from_age__isnull", True)),
                fields=("to_age",),
                name="значение верхней границы, при не указанном нижнем, должно быть уникальным",
            ),
        ),
        migrations.AddConstraint(
            model_name="agelimit",
            constraint=models.CheckConstraint(
                check=models.Q(("from_age", None), ("to_age", None), _negated=True),
                name="нужно указать хотя бы одно значение",
            ),
        ),
        migrations.AddConstraint(
            model_name="agelimit",
            constraint=models.CheckConstraint(
                check=models.Q(("from_age__lte", models.F("to_age"))),
                name="нижняя граница не может быть больше верхней",
            ),
        ),
    ]
