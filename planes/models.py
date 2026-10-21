from django.db import models


class Plan(models.Model):
    pk_pla_id = models.AutoField(primary_key=True)
    pla_nombre = models.CharField(max_length=50)
    pla_precio = models.DecimalField(max_digits=10, decimal_places=2)
    pla_dias = models.PositiveIntegerField()

    class Meta:
        db_table = 'tbl_plan'

    def __str__(self):
        return f'{self.pla_nombre} ({self.pla_dias} días)'