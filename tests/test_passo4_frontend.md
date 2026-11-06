# Checklist manual — Passo 4 (frontend de sequências)

> O fluxo principal já tem cobertura automatizada em `tests/sequencia.spec.js`
> (Playwright). Use este checklist para os detalhes visuais, de responsividade
> e de interação que não valem um teste E2E.

Use este checklist para validar a interface de `#/porsequencia` antes de
considerar o Passo 4 concluído.

## Pré-requisitos

```powershell
py main.py
```

Abra `http://localhost:5000/#/porsequencia`.

Para observar as requisições, abra o DevTools na aba **Network**.

## Catálogo

- [ ] O catálogo mostra as 6 sequências originais vindas de `GET /sequencias`.
- [ ] As sequências aparecem apenas como hexágonos, sem nome ou rótulo.
- [ ] O botão **Cadastrar sequência** fica acima do catálogo.
- [ ] Se `GET /sequencias` falhar, aparece “Não foi possível carregar o catálogo.” no painel esquerdo.

## Modal de cadastro

- [ ] O botão **Cadastrar sequência** abre o modal.
- [ ] O modal tem fundo branco ou quase branco.
- [ ] O modal tem um “X” no cabeçalho.
- [ ] O botão **Cancelar** fecha o modal.
- [ ] O “X” fecha o modal.
- [ ] A grade de acordes é a mesma usada em `#/poracordes`.

## Montagem da sequência

- [ ] Clicar em um acorde acrescenta o acorde ao fim da faixa “Sequência montada”.
- [ ] Clicar no mesmo acorde novamente acrescenta outra ocorrência.
- [ ] Clicar em um acorde da faixa remove somente aquela ocorrência.
- [ ] Não existe limite máximo de acordes.
- [ ] Não há drag-and-drop nem setas de reordenação.
- [ ] A quantidade selecionada é exibida corretamente.
- [ ] Com 0 ou 1 acorde, o botão **Cadastrar** fica desabilitado e aparece “Escolha pelo menos 2 acordes.”.
- [ ] Com 2 ou mais acordes, o botão **Cadastrar** fica habilitado.

## Cadastro

- [ ] Cadastrar uma sequência nova (por exemplo, `C` → `Em`) fecha o modal.
- [ ] O catálogo é recarregado e a nova sequência aparece ao final.
- [ ] A mensagem “Sequência cadastrada com sucesso.” aparece em um aviso flutuante sobre o painel esquerdo.
- [ ] O aviso desaparece automaticamente após aproximadamente 2,5 segundos.
- [ ] Tentar cadastrar a mesma sequência novamente mantém o modal aberto e mostra “sequência já cadastrada” inline.
- [ ] Com o DevTools em modo **Offline**, cadastrar mostra “Não foi possível cadastrar a sequência. Tente novamente.” inline.

## Busca

- [ ] Clicar em uma sequência original dispara `GET /similares?sequencia=...`.
- [ ] Clicar na sequência recém-cadastrada também dispara a busca.
- [ ] Os resultados aparecem ordenados por popularidade.
- [ ] O filtro de gênero refaz a busca com o parâmetro `generos`.
- [ ] A lista de resultados continua funcionando como antes.

## Responsividade

- [ ] Em 375px de largura, o modal ocupa a tela sem rolagem horizontal.
- [ ] Em 375px, os botões do rodapé ficam empilhados.
- [ ] Em 768px, o layout intermediário funciona.
- [ ] Em 1280px, catálogo e resultados ficam lado a lado.
- [ ] Ao adicionar muitos acordes, o corpo do modal ganha barra de rolagem.
- [ ] Cabeçalho, “X” e botões do rodapé permanecem visíveis durante a rolagem do corpo.
- [ ] O aviso de sucesso não invade a área de resultados.

## Limpeza

A remoção de sequências está fora do escopo. Para apagar uma sequência criada
durante o teste:

```powershell
py -c "import sqlite3; c=sqlite3.connect('data/db/sequencias.db'); c.execute('DELETE FROM sequencias WHERE sequencia = ?', ('CEm',)); c.commit(); c.close()"
```

Não remova as sequências originais: `BmGDA`, `CGAmF`, `EmG`, `CA7DmG7`,
`GmF`, `CC7FFm`.
