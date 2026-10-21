from django import forms

from clases.models import Clase
from entrenadores.models import Entrenador
from inscripciones.models import Inscripcion
from membresias.models import Membresia
from planes.models import Plan
from socios.models import Socio
from usuarios.models import Usuario


class FormularioModelo(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'campo-modal'
            if isinstance(field.widget, forms.DateInput):
                field.widget.attrs['type'] = 'date'
                field.widget.format = '%Y-%m-%d'
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs['type'] = 'time'
                field.widget.format = '%H:%M'
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.setdefault('step', 'any')


class SocioForm(FormularioModelo):
    class Meta:
        model = Socio
        fields = ('soc_documento', 'soc_nombre', 'soc_apellido', 'soc_telefono', 'soc_correo')
        labels = {
            'soc_documento': 'Documento',
            'soc_nombre': 'Nombre',
            'soc_apellido': 'Apellido',
            'soc_telefono': 'Teléfono',
            'soc_correo': 'Correo electrónico',
        }


class PlanForm(FormularioModelo):
    class Meta:
        model = Plan
        fields = ('pla_nombre', 'pla_precio', 'pla_dias')
        labels = {
            'pla_nombre': 'Nombre del plan',
            'pla_precio': 'Precio',
            'pla_dias': 'Duración (días)',
        }


class MembresiaForm(FormularioModelo):
    class Meta:
        model = Membresia
        fields = ('fk_soc', 'fk_pla', 'fk_usu', 'mem_inicio', 'mem_fin')
        labels = {
            'fk_soc': 'Socio',
            'fk_pla': 'Plan',
            'fk_usu': 'Registrada por',
            'mem_inicio': 'Fecha de inicio',
            'mem_fin': 'Fecha de fin',
        }


class EntrenadorForm(FormularioModelo):
    class Meta:
        model = Entrenador
        fields = ('ent_nombre', 'ent_apellido', 'ent_telefono', 'ent_especialidad')
        labels = {
            'ent_nombre': 'Nombre',
            'ent_apellido': 'Apellido',
            'ent_telefono': 'Teléfono',
            'ent_especialidad': 'Especialidad',
        }


class ClaseForm(FormularioModelo):
    class Meta:
        model = Clase
        fields = ('fk_ent', 'cla_nombre', 'cla_dia', 'cla_hora', 'cla_cupo')
        labels = {
            'fk_ent': 'Entrenador',
            'cla_nombre': 'Nombre de la clase',
            'cla_dia': 'Día',
            'cla_hora': 'Hora',
            'cla_cupo': 'Cupo',
        }


class InscripcionForm(FormularioModelo):
    class Meta:
        model = Inscripcion
        fields = ('fk_soc', 'fk_cla', 'fk_usu', 'inc_fecha')
        labels = {
            'fk_soc': 'Socio',
            'fk_cla': 'Clase',
            'fk_usu': 'Gestionada por',
            'inc_fecha': 'Fecha de inscripción',
        }


class UsuarioForm(FormularioModelo):
    class Meta:
        model = Usuario
        fields = ('usu_usuario', 'usu_nombre', 'usu_apellido', 'usu_correo', 'usu_rol')
        labels = {
            'usu_usuario': 'Nombre de usuario',
            'usu_nombre': 'Nombre',
            'usu_apellido': 'Apellido',
            'usu_correo': 'Correo electrónico',
            'usu_rol': 'Rol',
        }


FORMULARIOS = {
    'socios': SocioForm,
    'planes': PlanForm,
    'membresias': MembresiaForm,
    'entrenadores': EntrenadorForm,
    'clases': ClaseForm,
    'inscripciones': InscripcionForm,
    'usuarios': UsuarioForm,
}
