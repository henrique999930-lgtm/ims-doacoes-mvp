from django.contrib import admin

from .models import Delivery, DeliveryItem, Family, Item, StockMovement


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("nome_responsavel", "quantidade_membros", "ativo", "data_cadastro")
    search_fields = ("nome_responsavel", "telefone")
    list_filter = ("ativo",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("nome", "unidade_medida", "estoque_atual", "estoque_minimo", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo", "unidade_medida")


class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 0


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "family", "responsavel", "data_hora", "status")
    list_filter = ("status", "data_hora")
    search_fields = ("family__nome_responsavel", "responsavel__username")
    inlines = [DeliveryItemInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "tipo", "quantidade", "responsavel", "data_hora", "delivery")
    list_filter = ("tipo", "data_hora")
    search_fields = ("item__nome", "responsavel__username")
