from rest_framework import serializers
from .models import Categoria, Transacao, ContaAgendada

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'tipo']



class TransacaoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = Transacao
        fields = ['id', 'descricao', 'valor', 'tipo', 'data', 'categoria', 'categoria_nome', 'criado_em']
        read_only_fields = ['criado_em']




class ContaAgendadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaAgendada
        fields = ['id', 'descricao', 'valor', 'tipo', 'vencimento', 'paga', 'categoria']        