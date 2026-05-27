from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import datetime
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from .models import Categoria, ContaAgendada, Transacao
from .serializers import CategoriaSerializer, TransacaoSerializer, ContaAgendadaSerializer



class CategoriaListCreateView(ListCreateAPIView): #Criar/listar categorias dos gastos/receita
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class CategoriaDetailView(RetrieveUpdateDestroyAPIView): #Listar/update/delete categorias criadas pelo user
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)







class TransacaoListCreateView(ListCreateAPIView):
    serializer_class = TransacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Transacao.objects.filter(usuario=self.request.user)
        mes = self.request.query_params.get('mes')
        tipo = self.request.query_params.get('tipo')
        if mes:
            qs = qs.filter(data__startswith=mes)
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs.order_by('-data')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class TransacaoDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TransacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transacao.objects.filter(usuario=self.request.user)        





class ContaAgendadaListCreateView(ListCreateAPIView):
    serializer_class = ContaAgendadaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ContaAgendada.objects.filter(
            usuario=self.request.user
        ).order_by('vencimento')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ContaAgendadaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, usuario):
        try:
            return ContaAgendada.objects.get(pk=pk, usuario=usuario)
        except ContaAgendada.DoesNotExist:
            return None

    def get(self, request, pk):
        conta = self.get_object(pk, request.user)
        if not conta:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ContaAgendadaSerializer(conta)
        return Response(serializer.data)

    def patch(self, request, pk):
        conta = self.get_object(pk, request.user)
        if not conta:
            return Response(status=status.HTTP_404_NOT_FOUND)

        ja_estava_paga = conta.paga
        serializer = ContaAgendadaSerializer(conta, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            if not ja_estava_paga and serializer.instance.paga:
                Transacao.objects.create(
                    usuario=request.user,
                    descricao=conta.descricao,
                    valor=conta.valor,
                    tipo=conta.tipo,
                    categoria=conta.categoria,
                    data=conta.vencimento,
                )

                if conta.recorrente:
                    ContaAgendada.objects.create(
                        usuario=request.user,
                        descricao=conta.descricao,
                        valor=conta.valor,
                        tipo=conta.tipo,
                        categoria=conta.categoria,
                        vencimento=conta.vencimento + relativedelta(months=1),
                        recorrente=True,
                        paga=False,
                    )

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        conta = self.get_object(pk, request.user)
        if not conta:
            return Response(status=status.HTTP_404_NOT_FOUND)
        conta.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class ResumoFinanceiroView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mes = request.query_params.get('mes')
        
        if not mes:
            hoje = datetime.date.today()
            mes = hoje.strftime('%Y-%m')

        transacoes = Transacao.objects.filter(
            usuario=request.user,
            data__startswith=mes
        )

        total_receitas = transacoes.filter(
            tipo='receita'
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        total_despesas = transacoes.filter(
            tipo='despesa'
        ).aggregate(total=Sum('valor'))['total'] or 0

        saldo = total_receitas - total_despesas

        # Gastos por categoria
        por_categoria = []
        categorias = transacoes.filter(
            tipo='despesa'
        ).values(
            'categoria__nome'
        ).annotate(
            total=Sum('valor')
        ).order_by('-total')

        for c in categorias:
            por_categoria.append({
                'categoria': c['categoria__nome'] or 'Sem categoria',
                'total': c['total']
            })

        # Contas a vencer nos próximos 7 dias
        hoje = datetime.date.today()
        proximos = ContaAgendada.objects.filter(
            usuario=request.user,
            paga=False,
            vencimento__gte=hoje,
            vencimento__lte=hoje + datetime.timedelta(days=7)
        ).order_by('vencimento')

        contas_proximas = [{
            'descricao': c.descricao,
            'valor': c.valor,
            'vencimento': c.vencimento,
            'tipo': c.tipo
        } for c in proximos]

        return Response({
            'mes': mes,
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo': saldo,
            'por_categoria': por_categoria,
            'contas_proximas': contas_proximas
        })        


# Export pdf

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
import io


class ExportarRelatorioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request): 
        mes = request.query_params.get('mes')
        if not mes:
            mes = datetime.date.today().strftime('%Y-%m')

        transacoes = Transacao.objects.filter(
            usuario=request.user,
            data__startswith=mes
        ).order_by('data')

        total_receitas = transacoes.filter(tipo='receita').aggregate(
            total=Sum('valor'))['total'] or 0
        total_despesas = transacoes.filter(tipo='despesa').aggregate(
            total=Sum('valor'))['total'] or 0
        saldo = total_receitas - total_despesas

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)

        styles = getSampleStyleSheet()
        elements = []

        # Título
        elements.append(Paragraph(f'Relatório Financeiro — {mes}', styles['Title']))
        elements.append(Paragraph(f'Usuário: {request.user.username}', styles['Normal']))
        elements.append(Spacer(1, 20))

        # Resumo
        resumo_data = [
            ['Receitas', 'Despesas', 'Saldo'],
            [f'R$ {total_receitas:,.2f}', f'R$ {total_despesas:,.2f}', f'R$ {saldo:,.2f}'],
        ]
        resumo_table = Table(resumo_data, colWidths=[165, 165, 165])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e1e1e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f5f5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(resumo_table)
        elements.append(Spacer(1, 24))

        # Transações
        elements.append(Paragraph('Transações do mês', styles['Heading2']))
        elements.append(Spacer(1, 8))

        if transacoes.exists():
            rows = [['Data', 'Descrição', 'Categoria', 'Tipo', 'Valor']]
            for t in transacoes:
                rows.append([
                    t.data.strftime('%d/%m/%Y'),
                    t.descricao,
                    t.categoria.nome if t.categoria else '—',
                    t.tipo.capitalize(),
                    f'R$ {t.valor:,.2f}',
                ])

            tabela = Table(rows, colWidths=[80, 160, 110, 70, 95])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e1e1e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ]))
            elements.append(tabela)
        else:
            elements.append(Paragraph('Nenhuma transação registrada neste mês.', styles['Normal']))

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="fintrack-{mes}.pdf"'
        return response