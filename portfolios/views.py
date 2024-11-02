# portfolios/views.py
from django.views.generic import DetailView
from .models import Portfolio

class PortfolioDetailView(DetailView):
    model = Portfolio
    template_name = 'portfolios/portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les images triées par ordre
        context['images'] = self.object.images.all().order_by('order')
        return context


