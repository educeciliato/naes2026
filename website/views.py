from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "website/modelo.html"
    
class ContatoView(TemplateView):
    tamplate_name = "website.modelo.html"

# Create your views here.
