from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clases.models import Clase
from entrenadores.models import Entrenador
from inscripciones.models import Inscripcion
from membresias.models import Membresia
from planes.models import Plan
from usuarios.models import Usuario
from .models import Socio


class CatalogoViewTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='personal',
            password='prueba-segura-123',
            is_staff=True,
        )
        self.client.force_login(usuario)

    def test_todas_las_secciones_abren_la_interfaz_grafica(self):
        secciones = (
            ('socios', 'Socios'),
            ('planes', 'Planes'),
            ('membresias', 'Membresías'),
            ('entrenadores', 'Entrenadores'),
            ('clases', 'Clases'),
            ('inscripciones', 'Inscripciones'),
            ('usuarios', 'Usuarios'),
        )

        for modulo, titulo in secciones:
            with self.subTest(modulo=modulo):
                response = self.client.get(reverse('catalogo', args=[modulo]))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'catalogo.html')
                self.assertContains(response, titulo)
                self.assertContains(response, f'/catalogo/{modulo}/')

    def test_catalogo_socios_filtra_por_busqueda(self):
        Socio.objects.create(
            soc_documento='12345',
            soc_nombre='Ana',
            soc_apellido='Prueba',
            soc_telefono='555-0101',
            soc_correo='ana@example.com',
        )
        Socio.objects.create(
            soc_documento='67890',
            soc_nombre='Luis',
            soc_apellido='Ejemplo',
            soc_telefono='555-0102',
            soc_correo='luis@example.com',
        )

        response = self.client.get(
            reverse('catalogo', args=['socios']),
            {'q': 'Ana'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana')
        self.assertNotContains(response, 'Luis')

    def test_catalogo_requiere_personal_autenticado(self):
        self.client.logout()

        response = self.client.get(reverse('catalogo', args=['socios']))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_catalogo_muestra_modal_con_formulario_de_creacion(self):
        response = self.client.get(reverse('catalogo', args=['planes']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<dialog', html=False)
        self.assertContains(response, 'name="pla_nombre"', html=False)
        self.assertContains(response, 'name="pla_precio"', html=False)
        self.assertContains(response, 'name="pla_dias"', html=False)
        self.assertNotContains(response, '/admin/planes/plan/add/')

    def test_catalogo_muestra_accion_de_eliminacion_con_confirmacion(self):
        socio = Socio.objects.create(
            soc_documento='DOC-ELIMINAR-100',
            soc_nombre='Socio',
            soc_apellido='Eliminar',
            soc_telefono='555-0300',
            soc_correo='eliminar@example.com',
        )

        response = self.client.get(reverse('catalogo', args=['socios']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eliminar')
        self.assertContains(
            response,
            reverse('eliminar_registro', args=['socios', socio.pk]),
        )
        self.assertContains(response, 'También se eliminarán sus membresías e inscripciones.')

    def test_eliminar_socio_elimina_sus_registros_dependientes(self):
        socio = Socio.objects.create(
            soc_documento='DOC-CASCADE-100',
            soc_nombre='Socio',
            soc_apellido='Cascade',
            soc_telefono='555-0301',
            soc_correo='cascade@example.com',
        )
        plan = Plan.objects.create(pla_nombre='Plan Cascade', pla_precio=100, pla_dias=30)
        usuario = Usuario.objects.create(
            usu_usuario='usuario_cascade',
            usu_nombre='Usuario',
            usu_apellido='Cascade',
            usu_correo='usuario.cascade@example.com',
            usu_rol=Usuario.ROL_RECEPCIONISTA,
        )
        membresia = Membresia.objects.create(
            fk_soc=socio,
            fk_pla=plan,
            fk_usu=usuario,
            mem_inicio='2026-10-21',
            mem_fin='2026-11-20',
        )
        entrenador = Entrenador.objects.create(
            ent_nombre='Entrenador',
            ent_apellido='Cascade',
            ent_telefono='555-0302',
            ent_especialidad='Fuerza',
        )
        clase = Clase.objects.create(
            fk_ent=entrenador,
            cla_nombre='Clase Cascade',
            cla_dia='lunes',
            cla_hora='10:00',
            cla_cupo=10,
        )
        inscripcion = Inscripcion.objects.create(
            fk_soc=socio,
            fk_cla=clase,
            fk_usu=usuario,
            inc_fecha='2026-10-21',
        )

        response = self.client.post(
            reverse('eliminar_registro', args=['socios', socio.pk]),
            {'q': 'Cascade', 'page': '1'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Socio.objects.filter(pk=socio.pk).exists())
        self.assertFalse(Membresia.objects.filter(pk=membresia.pk).exists())
        self.assertFalse(Inscripcion.objects.filter(pk=inscripcion.pk).exists())
        self.assertContains(response, 'se eliminó correctamente')
        self.assertEqual(response.request['PATH_INFO'], reverse('catalogo', args=['socios']))
        self.assertEqual(response.request['QUERY_STRING'], 'q=Cascade&page=1')

    def test_no_elimina_plan_protegido_por_una_membresia(self):
        socio = Socio.objects.create(
            soc_documento='DOC-PROTECT-100',
            soc_nombre='Socio',
            soc_apellido='Protegido',
            soc_telefono='555-0303',
            soc_correo='protegido@example.com',
        )
        plan = Plan.objects.create(pla_nombre='Plan Protegido', pla_precio=100, pla_dias=30)
        usuario = Usuario.objects.create(
            usu_usuario='usuario_protegido',
            usu_nombre='Usuario',
            usu_apellido='Protegido',
            usu_correo='usuario.protegido@example.com',
            usu_rol=Usuario.ROL_RECEPCIONISTA,
        )
        Membresia.objects.create(
            fk_soc=socio,
            fk_pla=plan,
            fk_usu=usuario,
            mem_inicio='2026-10-21',
            mem_fin='2026-11-20',
        )

        response = self.client.post(
            reverse('eliminar_registro', args=['planes', plan.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Plan.objects.filter(pk=plan.pk).exists())
        self.assertContains(response, 'relacionado con otros registros protegidos')

    def test_inicio_no_muestra_boton_nuevo_socio_y_abre_modales_rapidos(self):
        response = self.client.get(reverse('inicio'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertNotContains(response, '+ Nuevo socio')
        self.assertContains(response, 'data-modal-open="modal-socios"', html=False)
        self.assertContains(response, 'id="modal-membresias"', html=False)
        self.assertContains(response, 'action="/catalogo/socios/crear/"', html=False)

    def test_acceso_rapido_del_inicio_guarda_socio_y_regresa_al_inicio(self):
        response = self.client.post(
            reverse('crear_registro', args=['socios']),
            {
                'origen': 'inicio',
                'soc_documento': 'DOC-INICIO-100',
                'soc_nombre': 'Rocio',
                'soc_apellido': 'Inicio',
                'soc_telefono': '555-0200',
                'soc_correo': 'rocio@example.com',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], reverse('inicio'))
        self.assertTrue(Socio.objects.filter(soc_documento='DOC-INICIO-100').exists())
        self.assertContains(response, 'Registro guardado correctamente.')

    def test_crea_registros_de_todas_las_entidades_desde_sus_formularios(self):
        socio_response = self.client.post(
            reverse('crear_registro', args=['socios']),
            {
                'origen': 'catalogo',
                'soc_documento': 'DOC-TEST-100',
                'soc_nombre': 'Camila',
                'soc_apellido': 'Prueba',
                'soc_telefono': '555-0100',
                'soc_correo': 'camila@example.com',
            },
        )
        plan_response = self.client.post(
            reverse('crear_registro', args=['planes']),
            {'origen': 'catalogo', 'pla_nombre': 'Plan de prueba', 'pla_precio': '29.90', 'pla_dias': '30'},
        )
        entrenador_response = self.client.post(
            reverse('crear_registro', args=['entrenadores']),
            {
                'origen': 'catalogo',
                'ent_nombre': 'Alex',
                'ent_apellido': 'Prueba',
                'ent_telefono': '555-0101',
                'ent_especialidad': 'Fuerza',
            },
        )
        usuario_response = self.client.post(
            reverse('crear_registro', args=['usuarios']),
            {
                'origen': 'catalogo',
                'usu_usuario': 'usuario_prueba',
                'usu_nombre': 'Sam',
                'usu_apellido': 'Prueba',
                'usu_correo': 'sam@example.com',
                'usu_rol': Usuario.ROL_RECEPCIONISTA,
            },
        )

        socio = Socio.objects.get(soc_documento='DOC-TEST-100')
        plan = Plan.objects.get(pla_nombre='Plan de prueba')
        entrenador = Entrenador.objects.get(ent_nombre='Alex')
        usuario = Usuario.objects.get(usu_usuario='usuario_prueba')

        clase_response = self.client.post(
            reverse('crear_registro', args=['clases']),
            {
                'origen': 'catalogo',
                'fk_ent': entrenador.pk,
                'cla_nombre': 'Clase de prueba modal',
                'cla_dia': 'lunes',
                'cla_hora': '09:30',
                'cla_cupo': '12',
            },
        )
        clase = Clase.objects.get(cla_nombre='Clase de prueba modal')
        membresia_response = self.client.post(
            reverse('crear_registro', args=['membresias']),
            {
                'origen': 'catalogo',
                'fk_soc': socio.pk,
                'fk_pla': plan.pk,
                'fk_usu': usuario.pk,
                'mem_inicio': '2026-10-21',
                'mem_fin': '2026-11-20',
            },
        )
        inscripcion_response = self.client.post(
            reverse('crear_registro', args=['inscripciones']),
            {
                'origen': 'catalogo',
                'fk_soc': socio.pk,
                'fk_cla': clase.pk,
                'fk_usu': usuario.pk,
                'inc_fecha': '2026-10-21',
            },
        )

        for response in (
            socio_response,
            plan_response,
            entrenador_response,
            usuario_response,
            clase_response,
            membresia_response,
            inscripcion_response,
        ):
            self.assertEqual(response.status_code, 302)

        self.assertEqual(Membresia.objects.count(), 1)
        self.assertEqual(Inscripcion.objects.count(), 1)

    def test_formulario_invalido_vuelve_a_mostrar_modal_con_errores(self):
        response = self.client.post(
            reverse('crear_registro', args=['planes']),
            {'origen': 'catalogo', 'pla_nombre': '', 'pla_precio': 'no-es-numero', 'pla_dias': '0'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['modal_abierto'], 'modal-planes')
        self.assertTrue(response.context['formulario'].errors)

    def test_formulario_usuario_ofrece_rol_cliente(self):
        response = self.client.get(reverse('catalogo', args=['usuarios']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="cliente">Cliente</option>', html=False)
