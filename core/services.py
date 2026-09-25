from collections import defaultdict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Delivery, DeliveryItem, Item, StockMovement


@transaction.atomic
def apply_stock_movement(*, item_id, tipo, quantidade, user):
    quantidade = Decimal(quantidade)
    if quantidade <= 0:
        raise ValidationError("A quantidade deve ser maior que zero.")

    item = Item.objects.select_for_update().get(pk=item_id)
    if tipo == "saida" and item.estoque_atual < quantidade:
        raise ValidationError(f"Estoque insuficiente para {item.nome}.")
    if tipo not in {"entrada", "saida"}:
        raise ValidationError("Tipo de movimentação inválido.")

    item.estoque_atual = (
        item.estoque_atual + quantidade
        if tipo == "entrada"
        else item.estoque_atual - quantidade
    )
    item.save(update_fields=["estoque_atual"])
    return StockMovement.objects.create(
        item=item,
        tipo=tipo,
        quantidade=quantidade,
        responsavel=user,
    )


def _consolidate_delivery_lines(lines):
    """Valida e consolida quantidades repetidas do mesmo item."""
    consolidated = defaultdict(lambda: Decimal("0"))

    for item_id, quantidade in lines:
        quantidade = Decimal(str(quantidade))

        if quantidade <= 0:
            raise ValidationError("As quantidades devem ser maiores que zero.")

        consolidated[int(item_id)] += quantidade

    if not consolidated:
        raise ValidationError("Informe pelo menos um item para a entrega.")

    return consolidated


@transaction.atomic
def register_delivery(*, family, user, lines, observacao=""):
    """Registra uma entrega e atualiza o estoque de forma atômica.

    lines: iterável de pares (item_id, quantidade).
    """
    consolidated = _consolidate_delivery_lines(lines)

    items = {
        item.pk: item
        for item in Item.objects.select_for_update().filter(
            pk__in=consolidated.keys(), ativo=True
        )
    }
    if len(items) != len(consolidated):
        raise ValidationError("Um ou mais itens não existem ou estão inativos.")

    for item_id, quantidade in consolidated.items():
        item = items[item_id]
        if item.estoque_atual < quantidade:
            raise ValidationError(
                f"Estoque insuficiente para {item.nome}. Disponível: {item.estoque_atual}."
            )

    delivery = Delivery.objects.create(
        family=family,
        responsavel=user,
        observacao=observacao,
    )

    for item_id, quantidade in consolidated.items():
        item = items[item_id]
        DeliveryItem.objects.create(
            delivery=delivery,
            item=item,
            quantidade=quantidade,
        )
        StockMovement.objects.create(
            item=item,
            tipo="saida",
            quantidade=quantidade,
            delivery=delivery,
            responsavel=user,
        )
        item.estoque_atual -= quantidade
        item.save(update_fields=["estoque_atual"])

    return delivery
