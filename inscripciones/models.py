from django.db import models
from django.utils import timezone


class Inscripcion(models.Model):
    pk_inc_id = models.AutoField(primary_key=True)
    fk_soc = models.ForeignKey(
        'socios.Socio',
        on_delete=models.CASCADE,
        related_name='inscripciones',
    )
    fk_cla = models.ForeignKey(
        'clases.Clase',
        on_delete=models.CASCADE,
        related_name='inscripciones',
    )
    fk_usu = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='inscripciones_gestionadas',
    )
    inc_fecha = models.DateField(default=timezone.localdate)

    class Meta:
        db_table = 'tbl_inscripcion'
        constraints = [
            models.UniqueConstraint(
                fields=['fk_soc', 'fk_cla'],
                name='uq_inscripcion_socio_clase',
            )
        ]

    def __str__(self):
        return f'{self.fk_soc.soc_nombre} en {self.fk_cla.cla_nombre}'