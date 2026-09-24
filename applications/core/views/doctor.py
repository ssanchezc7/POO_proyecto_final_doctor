from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from applications.security.components.mixin_crud import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from applications.core.forms.doctor import DoctorForm
from applications.core.models import Doctor


class DoctorListView(PermissionMixin, ListViewMixin, ListView):
    template_name = 'core/doctor/list.html'
    model = Doctor
    context_object_name = 'doctores'
    permission_required = 'view_doctor'
    paginate_by = 10

    def get_queryset(self):
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombres__icontains=q1), Q.OR)
            self.query.add(Q(apellidos__icontains=q1), Q.OR)
            self.query.add(Q(ruc__icontains=q1), Q.OR)
            self.query.add(Q(codigo_unico_doctor__icontains=q1), Q.OR)
            self.query.add(Q(email__icontains=q1), Q.OR)
            self.query.add(Q(especialidad__nombre__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).prefetch_related('especialidad').order_by('apellidos', 'nombres')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('core:doctor_create')
        
        # Asegurar que las variables de paginación estén disponibles
        if self.paginate_by and hasattr(context, 'page_obj'):
            context['is_paginated'] = True
            context['paginator'] = context.get('paginator')
            context['page_obj'] = context.get('page_obj')
            
        return context


class DoctorCreateView(PermissionMixin, CreateViewMixin, CreateView):
    model = Doctor
    template_name = 'core/doctor/form.html'
    form_class = DoctorForm
    success_url = reverse_lazy('core:doctor_list')
    permission_required = 'add_doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Doctor'
        # Manejar redirección personalizada
        next_url = self.request.GET.get('next')
        if next_url:
            context['back_url'] = next_url
        else:
            context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        doctor = self.object
        
        # Mensaje de éxito
        success_message = f"Éxito al crear el doctor {doctor.nombre_completo}."
        
        # Si se creó cuenta de usuario, agregar información adicional
        if doctor.email:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if User.objects.filter(email=doctor.email).exists():
                    success_message += " Se han enviado las credenciales de acceso al correo electrónico."
            except:
                pass
        
        messages.success(self.request, success_message)
        
        # Manejar redirección después de crear
        next_url = self.request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)
        
        return response

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()


class DoctorUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
    model = Doctor
    template_name = 'core/doctor/form.html'
    form_class = DoctorForm
    success_url = reverse_lazy('core:doctor_list')
    permission_required = 'change_doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Doctor'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        doctor = self.object
        messages.success(self.request, f"Éxito al actualizar el doctor {doctor.nombre_completo}.")
        return response


class DoctorDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
    model = Doctor
    template_name = 'components/delete.html'
    success_url = reverse_lazy('core:doctor_list')
    permission_required = 'delete_doctor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Doctor'
        context['description'] = f"¿Desea eliminar el doctor: {self.object.nombre_completo}?"
        context['back_url'] = self.success_url
        
        # Verificar si tiene relaciones que impiden la eliminación
        context['has_dependencies'] = False
        context['dependency_message'] = ""
        
        # Verificar si tiene citas médicas asociadas
        try:
            from applications.doctor.models import CitaMedica, Atencion
            if CitaMedica.objects.filter(doctor=self.object).exists():
                context['has_dependencies'] = True
                context['dependency_message'] = "El doctor tiene citas médicas asociadas."
            elif Atencion.objects.filter(doctor=self.object).exists():
                context['has_dependencies'] = True
                context['dependency_message'] = "El doctor tiene atenciones médicas registradas."
        except:
            pass
            
        return context

    def delete(self, request, *args, **kwargs):
        try:
            # Intentar la eliminación normal
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            doctor = self.get_object()
            
            messages.error(
                request, 
                f"No se puede eliminar el doctor '{doctor.nombre_completo}' porque tiene información crítica asociada. "
                f"Considere desactivar el doctor en lugar de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        # Guardar info antes de intentar eliminar
        doctor_nombre = self.object.nombre_completo
        
        try:
            # Intentar la eliminación
            response = super().form_valid(form)
            # Si llegamos aquí, la eliminación fue exitosa
            messages.success(self.request, f"Éxito al eliminar el doctor {doctor_nombre}.")
            return response
        except ProtectedError as e:
            # Si hay error de protección, manejarlo
            messages.error(
                self.request, 
                f"No se puede eliminar el doctor '{doctor_nombre}' porque tiene información crítica asociada. "
                f"Considere desactivar el doctor en lugar de eliminarlo."
            )
            return HttpResponseRedirect(self.success_url)
