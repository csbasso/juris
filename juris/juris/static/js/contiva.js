
function deleta_empresa(id_empresa, nome_empresa, meu_callback) {

  alertify.confirm("Tem certeza que deseja remover a empresa " + nome_empresa + " ?", 
    function (e) {
      if (e) {
        $.ajax({
            type: 'GET',
            url: '/empresa_deleta/' + id_empresa,
            success: function(data, textStatus, jqXHR){
              if (data.mensagem) {
                alertify.success(data.mensagem);
                meu_callback();
              } else {
                alertify.error(data.erro);
              }
            },
            error: function (jqXHR, textStatus, errorThrown){
                alertify.error("Ocorreu um erro inesperado ao processarmos sua solicitação.");
            }
        });
      }
  });
}

function detect_situation(debito){
  if(!debito){
    return "situacao_OK glyphicon glyphicon-check";
  }
  else{
    return "situacao_bad glyphicon glyphicon-warning-sign";
  }
}