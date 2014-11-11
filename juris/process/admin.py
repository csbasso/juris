from django.contrib import admin
from process.models import Processo, Assunto, Situacao #, Dispositivo

# Register your models here.
#admin.site.register(Dispositivo)
admin.site.register(Processo)
admin.site.register(Assunto)
admin.site.register(Situacao)



