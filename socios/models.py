from django.db import models


class Socio(models.Model):
    pk_soc_id = models.AutoField(primary_key=True)
    soc_documento = models.CharField(max_length=20, unique=True)
    soc_nombre = models.CharField(max_length=80)
    soc_apellido = models.CharField(max_length=80)
    soc_telefono = models.CharField(max_length=20)
    soc_correo = models.EmailField(max_length=100)

    class Meta:
        db_table = 'tbl_socio'

    def __str__(self):
        return f'{self.soc_nombre} {self.soc_apellido} - {self.soc_documento}'