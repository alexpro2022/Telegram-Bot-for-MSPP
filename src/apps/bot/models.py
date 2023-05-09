from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField


class BaseModel(models.Model):
    """
    An abstract base class model.
    It provides self-updating ``created_at`` and ``updated_at`` fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CoverageArea(MPTTModel, BaseModel):
    name = models.CharField(
        verbose_name="название",
        max_length=100,
        unique=True,
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="родительская зона охвата",
    )

    class MPTTMeta:
        order_insertion_by = ("name",)

    class Meta:
        verbose_name = "зона охвата"
        verbose_name_plural = "зоны охвата"

    def __str__(self):
        return self.name


class Fund(BaseModel):
    """Fund class model."""

    name = models.CharField(max_length=256, verbose_name="Название", unique=True)
    coverage_area = TreeManyToManyField(CoverageArea, related_name="funds", verbose_name="Зоны охвата")
    age_limit = models.PositiveSmallIntegerField(verbose_name="Минимальный возраст")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        ordering = ("name",)
        verbose_name = "фонд"
        verbose_name_plural = "фонды"

    def __str__(self):
        return self.name
