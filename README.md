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

### Requisitos previos

Antes de comenzar, instala:

1. **Python 3.13.x** desde [python.org](https://www.python.org/downloads/).
   Durante la instalación, activa **Add python.exe to PATH**.
2. **Git for Windows** desde [git-scm.com](https://git-scm.com/download/win).
3. **PowerShell**, incluido en Windows.

Abre una nueva ventana de PowerShell y comprueba que Python y Git estén
disponibles:

```powershell
py -3.13 --version
git --version
```

Python debe mostrar una versión `3.13.x`. Si `py` no se reconoce o no encuentra
Python 3.13, vuelve a instalar Python marcando la opción para agregarlo al PATH
y reinicia PowerShell.

### Descargar e instalar el proyecto

Copia y ejecuta estos comandos **uno por uno** en PowerShell:

```powershell
git clone https://github.com/SebasOfEek/administrador-gimnasios.git
Set-Location administrador-gimnasios
py -3.13 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
```

Estos pasos crean un entorno virtual propio e instalan las versiones indicadas
en `requirements.txt`. Se invoca Python directamente desde `venv`, por lo que
no hace falta activar el entorno ni cambiar la política de ejecución de
PowerShell.

La base de datos `db.sqlite3` con los datos de prueba está incluida en el
repositorio. Ejecutar `migrate` aplica las migraciones pendientes sin borrar
esos registros. No elimines ni reemplaces `db.sqlite3` si necesitas conservar
la base de demostración.

### Iniciar el servidor

Desde la carpeta `administrador-gimnasios`, ejecuta:

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

Mientras esa ventana siga abierta, visita:

- Panel gráfico: <http://127.0.0.1:8000/>
- Administración de Django: <http://127.0.0.1:8000/admin/>

Para detener el servidor, vuelve a PowerShell y presiona `Ctrl+C`. Para
iniciarlo en otra ocasión, abre PowerShell, entra a la carpeta del proyecto y
ejecuta nuevamente el comando `runserver`.

La base incluida tiene el usuario administrativo `Administrador`. La contraseña
de demostración se comparte por separado; no se publica en este README. Si
creaste una base nueva o necesitas otra cuenta administradora, ejecuta:

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

### Solución de problemas comunes

- **`py` no se reconoce:** instala Python 3.13 y marca **Add python.exe to
  PATH**; después cierra y vuelve a abrir PowerShell.
- **`git` no se reconoce:** instala Git for Windows y vuelve a abrir
  PowerShell.
- **No encuentra `manage.py` o `requirements.txt`:** comprueba que estés en la
  carpeta del proyecto con `Get-Location`. Si acabas de clonar el repositorio,
  entra con `Set-Location administrador-gimnasios`.
- **No encuentra `venv\Scripts\python.exe`:** desde la carpeta del proyecto,
  crea el entorno con `py -3.13 -m venv venv` y vuelve a instalar
  `requirements.txt`.
- **Error al instalar dependencias:** confirma que tienes conexión a Internet
  y ejecuta otra vez el comando `pip install -r requirements.txt`.
- **El puerto 8000 ya está ocupado:** inicia Django en otro puerto, por
  ejemplo `.\venv\Scripts\python.exe manage.py runserver 8001`, y abre
  <http://127.0.0.1:8001/>.

El entorno virtual no se incluye en Git; cada integrante debe crearlo e
instalar las dependencias siguiendo estos pasos.

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
