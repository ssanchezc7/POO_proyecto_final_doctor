from django.contrib.auth.models import Group

class UserGroupSession: 
    def __init__(self, request):
        self.request = request

    def get_group_session(self):
        try:
            return Group.objects.get(pk=self.request.session['group_id'])
        except (Group.DoesNotExist, KeyError):
            # Si no existe el grupo en la sesión o el grupo no existe, establecer uno válido
            self.set_group_session()
            if 'group_id' in self.request.session:
                return Group.objects.get(pk=self.request.session['group_id'])
            return None

    def set_group_session(self):
        if 'group_id' not in self.request.session or not self._is_valid_user_group():
            groups = self.request.user.groups.all().order_by('id')
            if groups.exists():
                self.request.session['group_id'] = groups.first().id
            else:
                # Si el usuario no tiene grupos, remover group_id de la sesión
                self.request.session.pop('group_id', None)

    def _is_valid_user_group(self):
        """Verifica que el grupo en la sesión pertenezca al usuario actual"""
        try:
            group_id = self.request.session.get('group_id')
            if group_id:
                return self.request.user.groups.filter(id=group_id).exists()
        except:
            pass
        return False
             
