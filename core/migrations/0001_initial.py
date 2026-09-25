import decimal
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Family",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome_responsavel", models.CharField(max_length=160)),
                ("telefone", models.CharField(blank=True, max_length=30)),
                ("quantidade_membros", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                ("ativo", models.BooleanField(default=True)),
                ("observacoes", models.TextField(blank=True)),
            ],
            options={"verbose_name": "família", "verbose_name_plural": "famílias", "ordering": ["nome_responsavel"]},
        ),
        migrations.CreateModel(
            name="Item",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120, unique=True)),
                ("unidade_medida", models.CharField(choices=[("UN", "Unidade"), ("KG", "Quilograma"), ("PCT", "Pacote"), ("CST", "Cesta")], default="UN", max_length=3)),
                ("estoque_atual", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=10, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.00"))])),
                ("estoque_minimo", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=10, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.00"))])),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={"ordering": ["nome"]},
        ),
        migrations.CreateModel(
            name="Delivery",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data_hora", models.DateTimeField(auto_now_add=True)),
                ("observacao", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("registrada", "Registrada"), ("cancelada", "Cancelada")], default="registrada", max_length=12)),
                ("family", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="entregas", to="core.family")),
                ("responsavel", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="entregas_registradas", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "entrega", "verbose_name_plural": "entregas", "ordering": ["-data_hora"]},
        ),
        migrations.CreateModel(
            name="DeliveryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.01"))])),
                ("delivery", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="itens_entregues", to="core.delivery")),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="itens_entregues", to="core.item")),
            ],
        ),
        migrations.CreateModel(
            name="StockMovement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("entrada", "Entrada"), ("saida", "Saída")], max_length=7)),
                ("quantidade", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.01"))])),
                ("data_hora", models.DateTimeField(auto_now_add=True)),
                ("delivery", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes_estoque", to="core.delivery")),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes", to="core.item")),
                ("responsavel", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes_registradas", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "movimentação de estoque", "verbose_name_plural": "movimentações de estoque", "ordering": ["-data_hora"]},
        ),
        migrations.AddConstraint(
            model_name="deliveryitem",
            constraint=models.UniqueConstraint(fields=("delivery", "item"), name="unique_item_por_entrega"),
        ),
    ]
