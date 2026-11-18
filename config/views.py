from datetime import timedelta

from urllib.parse import urlencode

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError
from django.db.models import Count, Q
from django.http import Http404
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import FORMULARIOS
from clases.models import Clase
from entrenadores.models import Entrenador
from inscripciones.models import Inscripcion
from membresias.models import Membresia
from planes.models import Plan
from socios.models import Socio
from usuarios.models import Usuario

DIAS_AVISO = 15  # una membresía "por vencer" es la que termina en 15 días o menos

CATALOGOS = {
    'socios': {
        'titulo': 'Socios',
        'descripcion': 'Administra la información de los socios del gimnasio.',
        'modelo': Socio,
        'columnas': (
            ('Documento', 'soc_documento'),
            ('Nombre', 'soc_nombre'),
            ('Apellido', 'soc_apellido'),
            ('Teléfono', 'soc_telefono'),
            ('Correo', 'soc_correo'),
        ),
        'busqueda': ('soc_documento', 'soc_nombre', 'soc_apellido', 'soc_correo'),
        'crear_texto': 'Nuevo socio',
    },
    'planes': {
        'titulo': 'Planes',
        'descripcion': 'Consulta los planes y sus condiciones.',
        'modelo': Plan,
        'columnas': (
            ('Nombre', 'pla_nombre'),
            ('Precio', 'pla_precio'),
            ('Duración (días)', 'pla_dias'),
        ),
        'busqueda': ('pla_nombre',),
        'crear_texto': 'Nuevo plan',
    },
    'membresias': {
        'titulo': 'Membresías',
        'descripcion': 'Consulta las membresías asignadas a los socios.',
        'modelo': Membresia,
        'columnas': (
            ('Socio', 'fk_soc'),
            ('Plan', 'fk_pla'),
            ('Registrada por', 'fk_usu'),
            ('Inicio', 'mem_inicio'),
            ('Fin', 'mem_fin'),
        ),
        'busqueda': (
            'fk_soc__soc_nombre',
            'fk_soc__soc_apellido',
            'fk_soc__soc_documento',
            'fk_pla__pla_nombre',
        ),
        'relaciones': ('fk_soc', 'fk_pla', 'fk_usu'),
        'crear_texto': 'Nueva membresía',
    },
    'entrenadores': {
        'titulo': 'Entrenadores',
        'descripcion': 'Consulta el equipo de entrenadores del gimnasio.',
        'modelo': Entrenador,
        'columnas': (
            ('Nombre', 'ent_nombre'),
            ('Apellido', 'ent_apellido'),
            ('Teléfono', 'ent_telefono'),
            ('Especialidad', 'ent_especialidad'),
        ),
        'busqueda': ('ent_nombre', 'ent_apellido', 'ent_especialidad'),
        'crear_texto': 'Nuevo entrenador',
    },
    'clases': {
        'titulo': 'Clases',
        'descripcion': 'Revisa horarios, cupos y entrenadores de cada clase.',
        'modelo': Clase,
        'columnas': (
            ('Clase', 'cla_nombre'),
            ('Entrenador', 'fk_ent'),
            ('Día', 'get_cla_dia_display'),
            ('Hora', 'cla_hora'),
            ('Cupo', 'cla_cupo'),
        ),
        'busqueda': ('cla_nombre', 'fk_ent__ent_nombre', 'fk_ent__ent_apellido'),
        'relaciones': ('fk_ent',),
        'crear_texto': 'Nueva clase',
    },
    'inscripciones': {
        'titulo': 'Inscripciones',
        'descripcion': 'Consulta las inscripciones de socios a las clases.',
        'modelo': Inscripcion,
        'columnas': (
            ('Socio', 'fk_soc'),
            ('Clase', 'fk_cla'),
            ('Gestionada por', 'fk_usu'),
            ('Fecha', 'inc_fecha'),
        ),
        'busqueda': (
            'fk_soc__soc_nombre',
            'fk_soc__soc_apellido',
            'fk_cla__cla_nombre',
            'fk_usu__usu_usuario',
        ),
        'relaciones': ('fk_soc', 'fk_cla', 'fk_usu'),
        'crear_texto': 'Nueva inscripción',
    },
    'usuarios': {
        'titulo': 'Usuarios',
        'descripcion': 'Consulta el personal registrado en el sistema.',
        'modelo': Usuario,
        'columnas': (
            ('Usuario', 'usu_usuario'),
            ('Nombre', 'usu_nombre'),
            ('Apellido', 'usu_apellido'),
            ('Correo', 'usu_correo'),
            ('Rol', 'get_usu_rol_display'),
        ),
        'busqueda': ('usu_usuario', 'usu_nombre', 'usu_apellido', 'usu_correo'),
        'crear_texto': 'Nuevo usuario',
    },
}


def _texto_vencimiento(dias):
    if dias == 0:
        return 'Vence hoy'
    if dias <= DIAS_AVISO:
        return f'Vence en {dias} día' + ('' if dias == 1 else 's')
    return 'Vigente'


def _formularios_rapidos(formulario_activo=None):
    modulos = ('socios', 'membresias', 'inscripciones', 'clases')
    formularios = []
    for modulo in modulos:
        configuracion = CATALOGOS[modulo]
        formulario = (
            formulario_activo
            if formulario_activo is not None and modulo == formulario_activo['modulo']
            else FORMULARIOS[modulo]()
        )
        formularios.append({
            'modulo': modulo,
            'titulo': configuracion['crear_texto'],
            'formulario': formulario,
            'modal_id': f'modal-{modulo}',
        })
    return formularios


def _contexto_inicio(formulario_activo=None, modal_abierto=None):
    hoy = timezone.localdate()
    limite = hoy + timedelta(days=DIAS_AVISO)

    vigentes = Membresia.objects.filter(mem_inicio__lte=hoy, mem_fin__gte=hoy)
    meses = []
    for desplazamiento in range(5, -1, -1):
        indice_mes = hoy.year * 12 + hoy.month - 1 - desplazamiento
        anio, mes = divmod(indice_mes, 12)
        meses.append((anio, mes + 1))

    inicio_periodo = hoy.replace(year=meses[0][0], month=meses[0][1], day=1)
    altas_por_mes = {
        (registro['mem_inicio__year'], registro['mem_inicio__month']): registro['total']
        for registro in Membresia.objects.filter(mem_inicio__gte=inicio_periodo, mem_inicio__lte=hoy)
        .values('mem_inicio__year', 'mem_inicio__month')
        .annotate(total=Count('pk'))
    }
    nombres_meses = ('Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic')
    altas_membresias = [
        {
            'mes': nombres_meses[mes - 1],
            'total': altas_por_mes.get((anio, mes), 0),
        }
        for anio, mes in meses
    ]
    max_altas = max((mes['total'] for mes in altas_membresias), default=0)
    for mes in altas_membresias:
        mes['altura'] = round(mes['total'] * 100 / max_altas) if max_altas else 0

    proximas = []
    consulta = (
        Membresia.objects.filter(mem_fin__gte=hoy)
        .select_related('fk_soc', 'fk_pla')
        .order_by('mem_fin')[:5]
    )
    for membresia in consulta:
        dias = (membresia.mem_fin - hoy).days
        proximas.append({
            'socio': f'{membresia.fk_soc.soc_nombre} {membresia.fk_soc.soc_apellido}',
            'plan': membresia.fk_pla.pla_nombre,
            'fin': membresia.mem_fin,
            'estado': 'aviso' if dias <= DIAS_AVISO else 'ok',
            'texto': _texto_vencimiento(dias),
        })

    clases = Clase.objects.select_related('fk_ent').annotate(inscritos=Count('inscripciones'))
    for clase in clases:
        clase.porcentaje = min(100, clase.inscritos * 100 // clase.cla_cupo) if clase.cla_cupo else 0
    ocupacion_clases = sorted(
        clases,
        key=lambda clase: (clase.porcentaje, clase.inscritos),
        reverse=True,
    )[:5]

    return {
        'hoy': hoy,
        'total_socios': Socio.objects.count(),
        'total_vigentes': vigentes.count(),
        'por_vencer': vigentes.filter(mem_fin__lte=limite).count(),
        'total_clases': clases.count(),
        'total_entrenadores': Entrenador.objects.count(),
        'total_inscripciones': Inscripcion.objects.count(),
        'proximas': proximas,
        'clases': clases,
        'ocupacion_clases': ocupacion_clases,
        'altas_membresias': altas_membresias,
        'planes': Plan.objects.all(),
        'formularios_rapidos': _formularios_rapidos(formulario_activo),
        'modal_abierto': modal_abierto,
    }


@staff_member_required
def inicio(request):
    return render(request, 'index.html', _contexto_inicio())


@staff_member_required
def catalogo(
    request,
    modulo,
    formulario=None,
    modal_abierto=None,
    formulario_edicion=None,
    registro_edicion=None,
    parametros_catalogo=None,
):
    configuracion = CATALOGOS.get(modulo)
    if configuracion is None:
        raise Http404('No existe esta sección.')

    if registro_edicion is None and request.GET.get('editar'):
        registro_edicion = get_object_or_404(
            configuracion['modelo'],
            pk=request.GET['editar'],
        )
    if registro_edicion is not None and formulario_edicion is None:
        formulario_edicion = FORMULARIOS[modulo](instance=registro_edicion)
        modal_abierto = 'modal-editar'

    consulta = configuracion['modelo'].objects.order_by('pk')
    relaciones = configuracion.get('relaciones', ())
    if relaciones:
        consulta = consulta.select_related(*relaciones)

    termino = (
        parametros_catalogo.get('q', request.GET.get('q', ''))
        if parametros_catalogo is not None
        else request.GET.get('q', '')
    ).strip()
    if termino:
        filtros = Q()
        for campo in configuracion['busqueda']:
            filtros |= Q(**{f'{campo}__icontains': termino})
        consulta = consulta.filter(filtros)

    paginador = Paginator(consulta, 15)
    numero_pagina = (
        parametros_catalogo.get('page')
        if parametros_catalogo is not None
        else request.GET.get('page')
    )
    pagina = paginador.get_page(numero_pagina)
    filas = []
    for registro in pagina:
        valores = []
        for _, atributo in configuracion['columnas']:
            valor = registro
            for parte in atributo.split('__'):
                valor = getattr(valor, parte)
                if callable(valor):
                    valor = valor()
            valores.append(str(valor) if valor is not None else '—')
        impacto = {
            'socios': ' También se eliminarán sus membresías e inscripciones.',
            'clases': ' También se eliminarán las inscripciones asociadas.',
        }.get(modulo, '')
        filas.append({
            'id': registro.pk,
            'valores': valores,
            'confirmacion': f'¿Eliminar «{registro}»? Esta acción no se puede deshacer.{impacto}',
        })

    contexto = {
        'titulo': configuracion['titulo'],
        'descripcion': configuracion['descripcion'],
        'columnas': [titulo for titulo, _ in configuracion['columnas']],
        'filas': filas,
        'pagina': pagina,
        'total': paginador.count,
        'termino': termino,
        'crear_texto': configuracion['crear_texto'],
        'formulario': formulario if formulario is not None else FORMULARIOS[modulo](),
        'formulario_url': reverse('crear_registro', args=[modulo]),
        'modal_id': f'modal-{modulo}',
        'modal_abierto': modal_abierto,
        'modulo': modulo,
        'formulario_edicion': formulario_edicion,
        'registro_edicion': registro_edicion,
        'url_edicion': (
            reverse('editar_registro', args=[modulo, registro_edicion.pk])
            if registro_edicion is not None else ''
        ),
    }
    return render(request, 'catalogo.html', contexto)


@staff_member_required
@require_POST
def crear_registro(request, modulo):
    if modulo not in CATALOGOS:
        raise Http404('No existe esta sección.')

    formulario = FORMULARIOS[modulo](request.POST)
    origen = request.POST.get('origen')
    if formulario.is_valid():
        formulario.save()
        messages.success(request, 'Registro guardado correctamente.')
        if origen == 'inicio':
            return redirect('inicio')
        return redirect('catalogo', modulo=modulo)

    if origen == 'inicio':
        return render(
            request,
            'index.html',
            _contexto_inicio(
                formulario_activo={'modulo': modulo, 'formulario': formulario},
                modal_abierto=f'modal-{modulo}',
            ),
        )
    return catalogo(request, modulo, formulario=formulario, modal_abierto=f'modal-{modulo}')


@staff_member_required
@require_POST
def editar_registro(request, modulo, registro_id):
    configuracion = CATALOGOS.get(modulo)
    if configuracion is None:
        raise Http404('No existe esta sección.')

    registro = get_object_or_404(configuracion['modelo'], pk=registro_id)
    formulario = FORMULARIOS[modulo](request.POST, instance=registro)
    if formulario.is_valid():
        formulario.save()
        messages.success(request, f'«{registro}» se actualizó correctamente.')
        url = reverse('catalogo', args=[modulo])
        parametros = {
            clave: request.POST[clave]
            for clave in ('q', 'page')
            if request.POST.get(clave)
        }
        if parametros:
            url = f'{url}?{urlencode(parametros)}'
        return redirect(url)

    return catalogo(
        request,
        modulo,
        modal_abierto='modal-editar',
        formulario_edicion=formulario,
        registro_edicion=registro,
        parametros_catalogo=request.POST,
    )


@staff_member_required
@require_POST
def eliminar_registro(request, modulo, registro_id):
    configuracion = CATALOGOS.get(modulo)
    if configuracion is None:
        raise Http404('No existe esta sección.')

    registro = get_object_or_404(configuracion['modelo'], pk=registro_id)
    try:
        registro.delete()
    except ProtectedError:
        messages.error(
            request,
            f'No se pudo eliminar «{registro}» porque está relacionado con otros '
            'registros protegidos. Elimina o reasigna primero esos registros.',
        )
    else:
        messages.success(request, f'«{registro}» se eliminó correctamente.')

    url = reverse('catalogo', args=[modulo])
    parametros = {
        clave: request.POST[clave]
        for clave in ('q', 'page')
        if request.POST.get(clave)
    }
    if parametros:
        url = f'{url}?{urlencode(parametros)}'
    return redirect(url)