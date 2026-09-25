from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DeliveryLineFormSet, FamilyForm, StockMovementForm
from .models import Delivery, Family, Item
from .services import apply_stock_movement, register_delivery


@login_required
def home(request):
    query = request.GET.get("q", "").strip()
    families = Family.objects.none()
    if query:
        families = Family.objects.filter(
            Q(nome_responsavel__icontains=query) | Q(pk__icontains=query),
            ativo=True,
        )[:20]
    return render(request, "core/home.html", {"families": families, "query": query})


@login_required
def family_create(request):
    if request.method == "POST":
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save()
            messages.success(request, "Família cadastrada com sucesso.")
            return redirect("delivery_create", family_id=family.pk)
    else:
        form = FamilyForm()
    return render(request, "core/family_form.html", {"form": form})


@login_required
def stock(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)
        if form.is_valid():
            try:
                movement = apply_stock_movement(
                    item_id=form.cleaned_data["item"].pk,
                    tipo=form.cleaned_data["tipo"],
                    quantidade=form.cleaned_data["quantidade"],
                    user=request.user,
                )
            except ValidationError as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(
                    request,
                    f"Movimentação registrada: {movement.get_tipo_display()} de {movement.quantidade} {movement.item.get_unidade_medida_display()}.",
                )
                return redirect("stock")
    else:
        form = StockMovementForm()

    items = Item.objects.filter(ativo=True).order_by("nome")
    return render(request, "core/stock.html", {"form": form, "items": items})


@login_required
def delivery_create(request, family_id):
    family = get_object_or_404(Family, pk=family_id, ativo=True)

    if request.method == "POST":
        formset = DeliveryLineFormSet(request.POST, prefix="itens")
        observacao = request.POST.get("observacao", "").strip()
        if formset.is_valid():
            lines = []
            for form in formset:
                if not form.cleaned_data:
                    continue
                item = form.cleaned_data.get("item")
                quantidade = form.cleaned_data.get("quantidade")
                if item and quantidade:
                    lines.append((item.pk, quantidade))
            try:
                delivery = register_delivery(
                    family=family,
                    user=request.user,
                    lines=lines,
                    observacao=observacao,
                )
            except ValidationError as exc:
                formset._non_form_errors = formset.error_class([exc.message])
            else:
                return redirect("delivery_success", delivery_id=delivery.pk)
    else:
        formset = DeliveryLineFormSet(prefix="itens")

    items = Item.objects.filter(ativo=True).order_by("nome")
    return render(
        request,
        "core/delivery_form.html",
        {"family": family, "formset": formset, "items": items},
    )


@login_required
def delivery_success(request, delivery_id):
    delivery = get_object_or_404(
        Delivery.objects.select_related("family", "responsavel").prefetch_related(
            "itens_entregues__item"
        ),
        pk=delivery_id,
    )
    return render(request, "core/delivery_success.html", {"delivery": delivery})
