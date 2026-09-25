from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import DeliveryItem, Family, Item, StockMovement
from .services import apply_stock_movement, register_delivery

User = get_user_model()


class InventoryServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="voluntario", password="SenhaSegura123!")
        self.item = Item.objects.create(nome="Arroz", estoque_atual=Decimal("20.00"))

    def test_entrada_aumenta_estoque(self):
        apply_stock_movement(
            item_id=self.item.pk, tipo="entrada", quantidade="5", user=self.user
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.estoque_atual, Decimal("25.00"))

    def test_saida_nao_permite_saldo_negativo(self):
        with self.assertRaises(ValidationError):
            apply_stock_movement(
                item_id=self.item.pk, tipo="saida", quantidade="25", user=self.user
            )


class DeliveryServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="voluntario", password="SenhaSegura123!")
        self.family = Family.objects.create(nome_responsavel="Família Exemplo", quantidade_membros=4)
        self.arroz = Item.objects.create(nome="Arroz", estoque_atual=Decimal("20.00"))
        self.feijao = Item.objects.create(nome="Feijão", estoque_atual=Decimal("15.00"))

    def test_entrega_reduz_estoque_e_cria_historico(self):
        delivery = register_delivery(
            family=self.family,
            user=self.user,
            lines=[(self.arroz.pk, "2"), (self.feijao.pk, "2")],
        )
        self.arroz.refresh_from_db()
        self.feijao.refresh_from_db()
        self.assertEqual(self.arroz.estoque_atual, Decimal("18.00"))
        self.assertEqual(self.feijao.estoque_atual, Decimal("13.00"))
        self.assertEqual(DeliveryItem.objects.filter(delivery=delivery).count(), 2)
        self.assertEqual(StockMovement.objects.filter(delivery=delivery, tipo="saida").count(), 2)

    def test_entrega_falha_se_estoque_insuficiente(self):
        with self.assertRaises(ValidationError):
            register_delivery(
                family=self.family,
                user=self.user,
                lines=[(self.arroz.pk, "200")],
            )
        self.arroz.refresh_from_db()
        self.assertEqual(self.arroz.estoque_atual, Decimal("20.00"))


class AuthenticationTests(TestCase):
    def test_home_exige_login(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class HomeSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="atendente",
            password="SenhaSegura123!"
        )
        self.ativa = Family.objects.create(
            nome_responsavel="Familia Exemplo Ativa",
            quantidade_membros=4,
            ativo=True,
        )
        self.inativa = Family.objects.create(
            nome_responsavel="Familia Exemplo Inativa",
            quantidade_membros=3,
            ativo=False,
        )

    def test_busca_exibe_apenas_familias_ativas(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"), {"q": "Exemplo"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Familia Exemplo Ativa")
        self.assertNotContains(response, "Familia Exemplo Inativa")
