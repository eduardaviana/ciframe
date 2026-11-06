angular.module('deciframeApp').controller('SequenciaController', function($http, $window, $uibModal, ngProgressFactory, $anchorScroll, $location, GENEROS, $timeout) {
  var acordesCadastro = [
    [
      { 'acorde': 'C',  'cor': '#e6b300' },
      { 'acorde': 'C#', 'cor': '#e6b300' },
      { 'acorde': 'Cm', 'cor': '#efcc59' },
      { 'acorde': 'C#m','cor': '#efcc59' },
      { 'acorde': 'C7', 'cor': '#d6a602' },
      { 'acorde': 'C#7','cor': '#d6a602' }],
    [
      { 'acorde': 'D',  'cor': '#cb6018' },
      { 'acorde': 'D#', 'cor': '#cb6018' },
      { 'acorde': 'Dm', 'cor': '#cf6f3e' },
      { 'acorde': 'D#m','cor': '#cf6f3e' },
      { 'acorde': 'D7', 'cor': '#bc5a1d' },
      { 'acorde': 'D#7','cor': '#bc5a1d' }],
    [
      { 'acorde': 'E',  'cor': '#b72c52' },
      { 'acorde': 'Em', 'cor': '#c5516e' },
      { 'acorde': 'E7', 'cor': '#a92f4d' }],
    [
      { 'acorde': 'F',  'cor': '#ba007c' },
      { 'acorde': 'F#', 'cor': '#ba007c' },
      { 'acorde': 'Fm', 'cor': '#c02a88' },
      { 'acorde': 'F#m','cor': '#c02a88' },
      { 'acorde': 'F7', 'cor': '#ad0076' },
      { 'acorde': 'F#7','cor': '#ad0076' }],
    [
      { 'acorde': 'G',  'cor': '#7b057e' },
      { 'acorde': 'G#', 'cor': '#7b057e' },
      { 'acorde': 'Gm', 'cor': '#882888' },
      { 'acorde': 'G#m','cor': '#882888' },
      { 'acorde': 'G7', 'cor': '#710c77' },
      { 'acorde': 'G#7','cor': '#710c77' }],
    [
      { 'acorde': 'A',  'cor': '#76aadb' },
      { 'acorde': 'A#', 'cor': '#76aadb' },
      { 'acorde': 'Am', 'cor': '#89c0e9' },
      { 'acorde': 'A#m','cor': '#89c0e9' },
      { 'acorde': 'A7', 'cor': '#6c9ecc' },
      { 'acorde': 'A#7','cor': '#6c9ecc' }],
    [
      { 'acorde': 'B',  'cor': '#a3bd31' },
      { 'acorde': 'Bm', 'cor': '#cdd54f' },
      { 'acorde': 'B7', 'cor': '#96b02f' }]
  ];

  var vm = this;
  vm.sequenciasFamosas = [];
  vm.acordesCadastro = acordesCadastro;
  vm.minhaSequencia = {};
  vm.isSearching = false;
  vm.showSearchResultsCount = false;
  vm.esfigeSpeech =  "";
  vm.musics = [];
  vm.generos = GENEROS;
  vm.meuGenero = "";
  vm.progressbar = ngProgressFactory.createInstance();
  vm.erroCatalogo = "";
  vm.mensagemSucesso = "";
  var mensagemSucessoTimeout = null;

  vm.carregarCatalogo = function() {
    vm.erroCatalogo = "";
    return $http.get("sequencias").then(function(response) {
      vm.sequenciasFamosas = response.data.map(function(item) {
        return {
          'id': item.id,
          'sequencia': item.sequencia,
          'acordes': item.acordes.split(';').map(function(acorde) {
            return { 'acorde': acorde, 'cor': '#2E1C74' };
          })
        };
      });
    }, function() {
      vm.sequenciasFamosas = [];
      vm.erroCatalogo = "Não foi possível carregar o catálogo.";
    });
  };

  vm.temAcorde = function(acorde) {
    if (vm.minhaSequencia.acordes) {
      return (vm.minhaSequencia.acordes.indexOf(acorde) > -1);
    } else {
      return false;
    }
  }

  var createChordsString = function(chords) {
    var str = "";
    for (var i = 0; i < chords.length; i++) {
      str = str.concat(chords[i].acorde, ',');
    }
    return str.substring(0, str.length-1);
  }

  vm.pesquisarPorSequencia = function(sequencia) {
    if (sequencia) {
      vm.minhaSequencia = sequencia;
      vm.mensagemSucesso = "";
    }
    vm.progressbar.start();
    vm.esfigeSpeech = "Procurando músicas com base na sequencia...";
    vm.isSearching = true;
    vm.musics = [];

    var apiUrl = "";
    var searchString = "similares?sequencia=".concat(createChordsString(vm.minhaSequencia.acordes));
    if (vm.meuGenero !== "" && vm.meuGenero !== null) {
      searchString += "&generos="+vm.meuGenero;
    }
    $http.get(apiUrl.concat(searchString))
      .success(function(data) {
        vm.progressbar.complete();
        vm.esfigeSpeech = "Encontrei essas músicas";
        vm.isSearching = false;
        vm.showSearchResultsCount = true;
        vm.musics = data;
      })
      .error(function(data) {
        vm.esfigeSpeech = "Ops! Algo errado.";
        vm.isSearching = false;
        vm.showSearchResultsCount = false;
      });
  }

  vm.abrirCadastro = function() {
    vm.mensagemSucesso = "";
    if (mensagemSucessoTimeout) {
      $timeout.cancel(mensagemSucessoTimeout);
      mensagemSucessoTimeout = null;
    }
    var modalInstance = $uibModal.open({
      templateUrl: "sequenciaCadastroModal.html",
      controller: "SequenciaCadastroModalController",
      controllerAs: "Cadastro",
      windowClass: "sequencia-cadastro-modal",
      resolve: {
        acordes: function() {
          return vm.acordesCadastro;
        }
      }
    });

    modalInstance.result.then(function() {
      vm.mensagemSucesso = "Sequência cadastrada com sucesso.";
      vm.carregarCatalogo();
      if (mensagemSucessoTimeout) {
        $timeout.cancel(mensagemSucessoTimeout);
      }
      mensagemSucessoTimeout = $timeout(function() {
        vm.mensagemSucesso = "";
        mensagemSucessoTimeout = null;
      }, 2500);
    }, function() {
      // modal cancelado
    });
  };

  vm.limparPesquisa = function() {
    vm.minhaSequencia = {};
    vm.musics = [];
  }

  vm.goToLirics = function(music) {
    $window.open(music.url);
  };

  vm.goToResults = function() {
    vm.showSearchResultsCount = false;
    $("body").animate({scrollTop: $("#results").offset().top}, "slow");
  };

  vm.carregarCatalogo();
});

angular.module('deciframeApp').controller('SequenciaCadastroModalController', function($http, $uibModalInstance, acordes) {
  var vm = this;
  vm.acordes = acordes;
  vm.minhaSequencia = [];
  vm.erro = "";

  vm.adicionarAcorde = function(acorde) {
    vm.minhaSequencia.push(acorde);
    vm.erro = "";
  };

  vm.removerAcorde = function(index) {
    vm.minhaSequencia.splice(index, 1);
    vm.erro = "";
  };

  vm.temAcorde = function(acorde) {
    return (vm.minhaSequencia.indexOf(acorde) > -1);
  };

  vm.cadastrar = function() {
    if (vm.minhaSequencia.length < 2) {
      vm.erro = "Escolha pelo menos 2 acordes.";
      return;
    }

    var sequencia = vm.minhaSequencia.map(function(acorde) {
      return acorde.acorde;
    });

    $http.post("sequencias", { 'sequencia': sequencia })
      .then(function() {
        $uibModalInstance.close();
      }, function(response) {
        if ((response.status === 400 || response.status === 409) && response.data && response.data.erro) {
          vm.erro = response.data.erro;
        } else {
          vm.erro = "Não foi possível cadastrar a sequência. Tente novamente.";
        }
      });
  };

  vm.cancelar = function() {
    $uibModalInstance.dismiss('cancel');
  };
});
