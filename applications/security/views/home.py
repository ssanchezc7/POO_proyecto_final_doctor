

from django.views.generic import TemplateView
from applications.security.components.menu_module import MenuModule
from applications.security.components.mixin_crud import PermissionMixin

class ModuloTemplateView(PermissionMixin,TemplateView):
    template_name = 'home.html'
   
    def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)
        context={}
        context["title"]= "IC - Modulos"
        context["title1"]= "Modulos Disponibles"
        MenuModule(self.request).fill(context)
        
        print("estoy saliendo en el modulo template view")
       
        return context