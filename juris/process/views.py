#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from django.utils.cache import add_never_cache_headers

from bs4 import BeautifulSoup

import json
import urllib
import hashlib
import base64
import datetime
import re

from process.models import Processo, Assunto, Situacao


def index(request):
	return render(request, 'index.html')

def mock_data(request):
	return render(request, 'juris/tj.html')

def valida_numero_proc(processo):
	tam_str = len(processo)
	validos = [10, 15, 20]
	#@TODO: melhorar essa validacao...
	if(tam_str not in validos):
		#nao ta...
		return False
	return True		

def valida_origem (origem):
	origens_validas = ["RS", "SC", "PR", "TRF"]
	if any(origem in s for s in origens_validas):
		return True
	return False

def busca_proc_web(numero, origem, hash_proc):
	#TODO: Remover esses dados fixos e colocar um tratamento em casa de retorno vazio.
	#"5002375-86.2014.404.7100" 
	#primeiro guess eh que seja RS..
	response_dict = {}

	soup = busca_dados_jfrs(numero, origem)

	strongs = soup.findAll("strong")

	orgao = ""
	#assuntos_list = []
	gratuita = ""
	erros = ""
	#fases_list = []

	# 10 pq qnd tiver 2 ou 3 deu erro... quando da certo nunca eh menor que 10
	if(len(strongs) < 10 ): 
		## @TODO: 
		## Ideia, caso nao ache, podemos tentar buscar nas outras origens automaticamente... (de repente até eliminar o campo)

		response_dict['erro'] = "Não foi possível buscar o processo. Confira se o nro do processo é valido ou origem é valida."
	else:
		novo_proc = Processo()
		novo_proc.numero = numero
		novo_proc.id_md5 = hash_proc
		novo_proc.origem = origem
		novo_proc.status = "novo"

		## @TODO:
		## considerar usar a funcao any do python. nao sei se eh o melhor caso aqui...

		for title in strongs:
			titulo = title.getText()    
			## @TODO: Melhorar isso...  
			subject = "Assuntos"
			organ = "Julgador"
			gratuity = "gratuita"

			if organ in titulo:
				orgao = unicode(title.next_sibling)     
				novo_proc.orgao_julgador = orgao     

			if gratuity in titulo:
				gratuita = unicode(title.next_sibling)
				novo_proc.justica_gratuita = gratuita
				
			novo_proc.save()
			if subject in titulo:           
				for idx, assunto in enumerate(title.findAllNext(text=lambda(x): len(x) > 4)):
					if idx > 0 and "Clique" not in assunto:
						assuntos = Assunto()
						assuntos.proc_id = novo_proc
						assuntos.assunto = assunto
						assuntos.save()

					elif "Clique" in assunto:
						break
			
		#captura todas as fases do processo (inclui a imagem divisoria)
		barra = soup.find("img", {"alt" : "Barra divisora Fases"})

		#Separamos agora data e texto - 
		strong = barra.findAllNext('strong')
					
		for text in strong:
			situacao = Situacao()
			situacao.proc_id = novo_proc			
			#12/03/2014 08:13
			#@TODO: usar datetime retorna um naive date - runtime warning, devo usar o django.utils timezone
			situacao.data = datetime.datetime.strptime(text.getText(), "%d/%m/%Y %H:%M")
			situacao.situacao = unicode(text.next_sibling)
			situacao.save()


		print "Saindo do metodo - busca_proc_web"
	
def busca_dados_jfrs(nro_processo, origem):
	url_jfrs = "http://www.jfrs.jus.br/processos/acompanhamento/resultado_pesquisa.php?selForma=NU&todasfases=S&txtValor="+nro_processo+"&selOrigem="+origem+""
	mocked = "http://127.0.0.1:8000/tj"
	content = urllib.urlopen(url_jfrs)
	soup = BeautifulSoup(content)

	return soup

#@TODO: Double check nisso aqui...
@csrf_exempt
def adiciona_processo(request):
	response_dict = {}
	erro_validacao = False
	ja_cadastrado = False
	processo_json = ""
	hash_proc = None

	if request.method == 'POST':
		nro_proc = request.POST.get('processo', '')
		origem = request.POST.get('origem', 'RS')
		
		#limpa char especiais caso tenham sido passados.
		nro_proc = re.sub("[^0-9]", "", nro_proc)

		#print "Novo processo: " + nro_proc + " origem:" + origem

		if not valida_numero_proc(nro_proc):
			response_dict['erro'] = "nro de processo invalido"
			erro_validacao = True			

		if not valida_origem(origem):			
			response_dict['erro'] = "origem invalida - " + origem
			erro_validacao = True
		
		# proc ja existe ?  
		if not erro_validacao:
			hash_proc = hashlib.md5( u"%s%s" % (nro_proc, origem)).hexdigest()
		
			processo = Processo.objects.filter(id_md5__exact=hash_proc)
			if len(processo) > 0:
				#print "Processo " + processo[0].numero + " ja existe."
				ja_cadastrado = True				
				response_dict['erro'] = "proc ja existe"

			if not ja_cadastrado:
				#xprint "Criando novo processo"
				#busca dados da web e salva dados no banco.
				busca_proc_web(nro_proc, origem, hash_proc)
				response_dict['ok'] = "Sucesso!"
	status = 200
	if (erro_validacao) or (request.method != 'POST'):
		status = 400
	if ja_cadastrado:
		status = 409

	resp = HttpResponse(json.dumps(response_dict), content_type="application/json", status = status)
	add_never_cache_headers(resp)
	return resp

def busca_processo(request, processo):
	processo_json = []
	assuntos_list = []
	situacoes_list = []
	
	try:
		if request.method == 'GET':
			hash_proc = processo			
			processo = get_object_or_404(Processo, numero__exact=hash_proc)
			assuntos = Assunto.objects.filter(proc_id = processo)
			situacoes = Situacao.objects.filter(proc_id = processo)
	
			for assunto in assuntos:
				assuntos_list.append(assunto.assunto)
			for situacao in situacoes:
				situacoes_list.append([str(situacao.data), situacao.situacao])

			processo_json = dict(({'processo': processo.numero, 'id_md5': processo.id_md5, 'orgao_julgador': processo.orgao_julgador,
										 'justica_gratuita': processo.justica_gratuita, 'status': processo.status, 'assuntos': assuntos_list, 'situacoes': situacoes_list}))
	except ObjectDoesNotExist:
		processo = None

	resp = HttpResponse(json.dumps(processo_json), content_type="application/json")
	add_never_cache_headers(resp)
	return resp

def busca_processos(request, proc_list):
	processos_json = []

	try:
	   processos = Processo.objects.filter(numero__in = proc_list)
	   processos_json = dict((e.id_md5, {'nome_empresarial': e.nome_empresarial, 'debitoFGTS': e.debitos_fgts,
										 'debitoRFB': e.debitos_rfbccd, 'debitoSeFaz': e.debitos_sefaz_rs}) for e in empresas)
	except ObjectDoesNotExist:
	   processos = None

	resp = HttpResponse(json.dumps(processo_json), content_type="application/json")
	add_never_cache_headers(resp)
	return resp

#@TODO: Double check nisso aqui...
@csrf_exempt
def deleta_processo(request, processo):
	return_json = []
	status = 200

	try:
		if request.method == 'DELETE':
			hash_proc = processo			
			processo = get_object_or_404(Processo, numero__exact=hash_proc)
			processo.delete()
	except ObjectDoesNotExist:
		status = 404

	resp = HttpResponse(json.dumps(return_json), content_type="application/json", status=status)
	add_never_cache_headers(resp)
	return resp

#poderia usarmos um decorator para verificar o device,
# def registra_dispositivo(request, dispositivo, nome):
# 	try:
# 		novo_dispositivo = get_object_or_404(Dispositivo, id_dispositivo__exact=dispositivo)
# 		status = 409
# 	except ObjectDoesNotExist:
# 		novo_dispositivo = Dispositivo()
# 		novo_dispositivo.id_md5 = hashlib.md5( u"%s%s" % (dispositivo, nome)).hexdigest()
# 		novo_dispositivo.id_dispositivo = dispositivo
# 		novo_dispositivo.nome_dispositivo = nome
# 		novo_dispositivo.ativo = True
# 		novo_dispositivo.save()
# 		status = 200

# 	resp = HttpResponse(json.dumps(processo_json), content_type="application/json", status = status)
# 	add_never_cache_headers(resp)
# 	return resp




























