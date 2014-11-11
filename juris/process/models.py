from django.db import models

class Processo(models.Model):
    """
        Armazena o Nro do Processo e sua origem
    """

    id_md5 = models.CharField(max_length=32)
    #dispositivo = models.ForeignKey(Dispositivo)

    numero = models.CharField(max_length=50)
    status = models.CharField(max_length=10)

    origem = models.CharField(max_length=3)
    orgao_julgador = models.CharField(max_length=100)
    justica_gratuita = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%s - %s' % (self.numero, self.status)


class Assunto(models.Model):
    proc_id = models.ForeignKey(Processo)
    assunto = models.CharField(max_length=800) #esse limite ta mto chutao, ajustar 
    
    def __unicode__(self):
        return u'%s - %s' % (self.proc_id.numero, self.assunto)


class Situacao(models.Model):
    proc_id = models.ForeignKey(Processo)
    situacao = models.CharField(max_length=800) #esse limite ta mto chutao, ajustar 
    data = models.DateTimeField()

    class Meta:
        get_latest_by = 'data'

    def __unicode__(self):
        return u'%s - %s - %s' % (self.proc_id.numero, self.data, self.situacao)

# class Dispositivo(models.Model):
#     id_md5 = models.CharField(max_length=32)
#     id_dispositivo = models.CharField(max_length=40)
#     nome_dispositivo = models.CharField(max_length=80)
#     ativo = models.NullBooleanField(blank=True, null=True)

#     def __unicode__(self):
#         return u'%s - %s - %s' % (self.id_md5, self.dono, self.ativo)


