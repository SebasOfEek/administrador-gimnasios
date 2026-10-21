from django.db import models


class Usuario(models.Model):
    ROL_ADMINISTRADOR = 'administrador'
    ROL_RECEPCIONISTA = 'recepcionista'
    ROL_CLIENTE = 'cliente'
    ROLES = [
        (ROL_ADMINISTRADOR, 'Administrador'),
        (ROL_RECEPCIONISTA, 'Recepcionista'),
        (ROL_CLIENTE, 'Cliente'),
    ]

    pk_usu_id = models.AutoField(primary_key=True)
    usu_usuario = models.CharField(max_length=30, unique=True)
    usu_nombre = models.CharField(max_length=80)
    usu_apellido = models.CharField(max_length=80)
    usu_correo = models.EmailField(max_length=100)
    usu_rol = models.CharField(max_length=15, choices=ROLES)

    class Meta:
        db_table = 'tbl_usuario'

    def __str__(self):
        return f'{self.usu_nombre} {self.usu_apellido} ({self.get_usu_rol_display()})'