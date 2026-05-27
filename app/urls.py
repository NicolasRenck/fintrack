from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    # Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # Categorias
    path('categorias/', views.CategoriaListCreateView.as_view(), name='categoria-list'),
    path('categorias/<int:pk>/', views.CategoriaDetailView.as_view(), name='categoria-detail'),

    # Transacoes
    path('transacoes/', views.TransacaoListCreateView.as_view(), name='transacao-list'),
    path('transacoes/<int:pk>/', views.TransacaoDetailView.as_view(), name='transacao-detail'),

    # Contas Agendadas
    path('contas/', views.ContaAgendadaListCreateView.as_view(), name='conta-list'),
    path('contas/<int:pk>/', views.ContaAgendadaDetailView.as_view(), name='conta-detail'),
    path('relatorio/exportar/', views.ExportarRelatorioView.as_view(), name='relatorio-exportar'),

    # Docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('resumo/', views.ResumoFinanceiroView.as_view(), name='resumo'),
]