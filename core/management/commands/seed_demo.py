import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Family, Item


class Command(BaseCommand):
    help = "Cria dados fictícios para demonstração do MVP."

    def handle(self, *args, **options):
        Family.objects.get_or_create(
            nome_responsavel="Maria Exemplo",
            defaults={"quantidade_membros": 4, "ativo": True},
        )
        Item.objects.get_or_create(
            nome="Arroz",
            defaults={"unidade_medida": "UN", "estoque_atual": 20, "estoque_minimo": 5},
        )
        Item.objects.get_or_create(
            nome="Feijão",
            defaults={"unidade_medida": "UN", "estoque_atual": 15, "estoque_minimo": 5},
        )
        Item.objects.get_or_create(
            nome="Macarrão",
            defaults={"unidade_medida": "PCT", "estoque_atual": 12, "estoque_minimo": 4},
        )
        username = os.getenv("DEMO_USERNAME", "").strip()
        password = os.getenv("DEMO_PASSWORD", "").strip()

        if username and password:
            User = get_user_model()
            user, _ = User.objects.get_or_create(username=username)
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"Usuário de demonstração '{username}' preparado.")
            )

        self.stdout.write(self.style.SUCCESS("Dados fictícios criados com sucesso."))
