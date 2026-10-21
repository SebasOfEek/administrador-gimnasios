from django.db import models


class Clase(models.Model):
    DIAS = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    pk_cla_id = models.AutoField(primary_key=True)
    fk_ent = models.ForeignKey(
        'entrenadores.Entrenador',
        on_delete=models.PROTECT,
        related_name='clases',
    )
    cla_nombre = models.CharField(max_length=60)
    cla_dia = models.CharField(max_length=10, choices=DIAS)
    cla_hora = models.TimeField()
    cla_cupo = models.PositiveIntegerField()

    # Relación N:M con Socio, resuelta por la tabla intermedia Inscripcion
    socios = models.ManyToManyField(
        'socios.Socio',
        through='inscripciones.Inscripcion',
        related_name='clases',
    )

    class Meta:
        db_table = 'tbl_clase'

    def __str__(self):
        return f'{self.cla_nombre} - {self.get_cla_dia_display()} {self.cla_hora:%H:%M}'