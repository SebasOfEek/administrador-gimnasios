# Sistema de Administración de Gimnasio

Aplicación web desarrollada con Django para administrar socios, planes,
membresías, entrenadores, clases e inscripciones. Incluye un panel gráfico
propio para consultar, buscar, registrar y eliminar datos, además del panel
administrativo de Django.

## Tecnologías y versiones

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.13">
  <img src="https://img.shields.io/badge/Django-6.1.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django 6.1.2">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
</p>

- **Python:** 3.13.x
- **Django:** 6.1.2
- **Base de datos:** SQLite
- **Interfaz:** Django Templates, HTML, CSS y JavaScript

La configuración está pensada para desarrollo y demostración académica local;
no despliegues esta configuración tal cual en un servidor público. La clave
incluida en `settings.py` es solo para desarrollo local.

Las dependencias fijadas del entorno están en [`requirements.txt`](./requirements.txt).
Si se actualizan, se pueden regenerar desde el entorno virtual activo con:

```powershell
python -m pip freeze > requirements.txt
```

## Funcionalidades

- Consultar, buscar y paginar los registros de cada entidad.
- Crear registros mediante formularios modales con validación.
- Eliminar registros desde los catálogos con confirmación.
- Proteger las relaciones que no se deben borrar mientras estén en uso.
- Eliminar en cascada las inscripciones de una clase y las membresías e
  inscripciones de un socio, según las relaciones del modelo.
- Consultar en el inicio indicadores, membresías próximas a vencer y cupos de
  clases.
- Administrar los registros desde Django Admin, con búsquedas, filtros e
  interfaces inline para membresías e inscripciones.

## Aplicaciones y modelo de datos

Cada entidad tiene su propia aplicación Django y está registrada en
`INSTALLED_APPS`.

| Aplicación | Tabla | Función y relaciones |
|---|---|---|
| `usuarios` | `tbl_usuario` | Personal que registra membresías e inscripciones. |
| `socios` | `tbl_socio` | Socios con membresías e inscripciones. |
| `planes` | `tbl_plan` | Planes disponibles para las membresías. |
| `membresias` | `tbl_membresia` | Relaciona socio, plan y usuario que la registra. |
| `entrenadores` | `tbl_entrenador` | Entrenadores que dictan clases. |
| `clases` | `tbl_clase` | Clases dictadas por un entrenador; relación N:M con socios mediante Inscripción. |
| `inscripciones` | `tbl_inscripcion` | Tabla intermedia entre socios y clases; registra también quién la gestiona. |

Cada modelo define su representación `__str__`. En el admin, todos los modelos
tienen `list_display`, `search_fields` y `list_filter`. Las membresías se
gestionan inline en el formulario de Socio; las inscripciones, en el de Clase.
La relación N:M Socio-Clase usa `ManyToManyField` con `Inscripcion` como
`through`.

## Operaciones de datos

Los catálogos gráficos permiten **crear, consultar y eliminar** registros. La
edición y administración detallada también están disponibles en Django Admin.
Las relaciones protegidas —por ejemplo, un plan usado por una membresía— no se
eliminan accidentalmente: el sistema informa que primero se deben quitar o
reasignar las dependencias.

El modelo `Usuario` descrito por el ER es una entidad de negocio. No es la
cuenta de autenticación de Django que se utiliza para iniciar sesión.

## Estructura del proyecto

```text
gimnasio/
├── clases/
├── config/                 # Configuración, rutas y vistas del panel gráfico
├── docs/                   # Diagramas y documentos de la entrega
├── entrenadores/
├── inscripciones/
├── membresias/
├── planes/
├── socios/
├── usuarios/
├── static/css/             # Estilos de la interfaz
├── templates/              # index, catálogos y formularios modales
├── db.sqlite3              # Base incluida con datos de prueba
├── manage.py
├── requirements.txt
└── README.md
```

Las aplicaciones tienen sus carpetas `migrations/` versionadas, que permiten
recrear la estructura de la base de datos.

## Datos de prueba

La base [`db.sqlite3`](./db.sqlite3) incluida contiene registros para todas las
entidades. Conteos verificados:

| Entidad | Registros |
|---|---:|
| Usuario | 10 |
| Socio | 9 |
| Plan | 10 |
| Membresía | 9 |
| Entrenador | 10 |
| Clase | 10 |
| Inscripción | 9 |

La base también contiene cuentas de acceso a Django Admin. El usuario de
demostración es `Administrador`. Por seguridad, comparte la contraseña por un
medio privado y no la publiques en este README ni en el repositorio.

## Instalación y ejecución en Windows

Requiere Python 3.13 y Git. Desde PowerShell:

```powershell
git clone https://github.com/SebasOfEek/administrador-gimnasios.git
Set-Location administrador-gimnasios
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abre <http://127.0.0.1:8000/> para el panel gráfico y
<http://127.0.0.1:8000/admin/> para Django Admin. Inicia sesión con una cuenta
de personal. Si se necesita crear otra cuenta administradora en esta base:

```powershell
python manage.py createsuperuser
```

El entorno virtual no se incluye en Git; cada integrante debe crearlo e
instalar las dependencias con `requirements.txt`.

## Diagramas y documentos

- [Diagrama de actores](./docs/diagrama_actores.pdf)
- [Diagrama entidad-relación](./docs/diagrama_er.pdf)

## Verificaciones realizadas

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test socios.tests --verbosity 1
```

Las pruebas cubren navegación, creación, búsqueda y eliminación desde la
interfaz gráfica. Las migraciones se encuentran aplicadas en la base incluida.
