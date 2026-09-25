from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Family(models.Model):
    nome_responsavel = models.CharField(max_length=160)
    telefone = models.CharField(max_length=30, blank=True)
    quantidade_membros = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["nome_responsavel"]
        verbose_name = "família"
        verbose_name_plural = "famílias"

    def __str__(self):
        return self.nome_responsavel


class Item(models.Model):
    UNIDADES = [
        ("UN", "Unidade"),
        ("KG", "Quilograma"),
        ("PCT", "Pacote"),
        ("CST", "Cesta"),
    ]

    nome = models.CharField(max_length=120, unique=True)
    unidade_medida = models.CharField(max_length=3, choices=UNIDADES, default="UN")
    estoque_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    @property
    def estoque_baixo(self):
        return self.estoque_atual <= self.estoque_minimo

    def __str__(self):
        return self.nome


class Delivery(models.Model):
    STATUS = [("registrada", "Registrada"), ("cancelada", "Cancelada")]

    family = models.ForeignKey(Family, on_delete=models.PROTECT, related_name="entregas")
    data_hora = models.DateTimeField(auto_now_add=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="entregas_registradas",
    )
    observacao = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="registrada")

    class Meta:
        ordering = ["-data_hora"]
        verbose_name = "entrega"
        verbose_name_plural = "entregas"

    def __str__(self):
        return f"Entrega #{self.pk} - {self.family}"


class DeliveryItem(models.Model):
    delivery = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, related_name="itens_entregues"
    )
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="itens_entregues")
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["delivery", "item"], name="unique_item_por_entrega"
            )
        ]

    def __str__(self):
        return f"{self.item}: {self.quantidade}"


class StockMovement(models.Model):
    TIPOS = [("entrada", "Entrada"), ("saida", "Saída")]

    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="movimentacoes")
    tipo = models.CharField(max_length=7, choices=TIPOS)
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    data_hora = models.DateTimeField(auto_now_add=True)
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.PROTECT,
        related_name="movimentacoes_estoque",
        null=True,
        blank=True,
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentacoes_registradas",
    )

    class Meta:
        ordering = ["-data_hora"]
        verbose_name = "movimentação de estoque"
        verbose_name_plural = "movimentações de estoque"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.item} - {self.quantidade}"
