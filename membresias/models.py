from django.db import models


class Membresia(models.Model):
    pk_mem_id = models.AutoField(primary_key=True)
    fk_soc = models.ForeignKey(
        'socios.Socio',
        on_delete=models.CASCADE,   # sin socio no existe la membresía
        related_name='membresias',
    )
    fk_pla = models.ForeignKey(
        'planes.Plan',
        on_delete=models.PROTECT,
        related_name='membresias',
    )
    fk_usu = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='membresias_registradas',
    )
    mem_inicio = models.DateField()
    mem_fin = models.DateField()

    class Meta:
        db_table = 'tbl_membresia'

    def __str__(self):
        return f'{self.fk_pla.pla_nombre}: {self.mem_inicio} a {self.mem_fin}'