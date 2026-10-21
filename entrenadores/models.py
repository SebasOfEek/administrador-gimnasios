from django.db import models


class Entrenador(models.Model):
    pk_ent_id = models.AutoField(primary_key=True)
    ent_nombre = models.CharField(max_length=80)
    ent_apellido = models.CharField(max_length=80)
    ent_telefono = models.CharField(max_length=20)
    ent_especialidad = models.CharField(max_length=60)

    class Meta:
        db_table = 'tbl_entrenador'

    def __str__(self):
        return f'{self.ent_nombre} {self.ent_apellido} - {self.ent_especialidad}'