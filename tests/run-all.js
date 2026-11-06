const { spawnSync } = require('child_process');
const path = require('path');

const root = path.resolve(__dirname, '..');
const python = process.env.PYTHON || (process.platform === 'win32' ? 'py' : 'python3');

const testesPython = [
  'tests/test_passo1_exec_main.py',
  'tests/test_passo1_docker_persistence.py',
  'tests/test_passo2_matcher.py',
  'tests/test_passo3_routes.py',
  'tests/test_passo5_integration.py',
];

function executar(nome, comando, argumentos, opcoes = {}) {
  console.log(`\n===== ${nome} =====`);
  const resultado = spawnSync(comando, argumentos, {
    cwd: root,
    stdio: 'inherit',
    ...opcoes,
  });

  if (resultado.error) {
    console.error(`Falha ao executar ${nome}: ${resultado.error.message}`);
    return false;
  }

  if (resultado.status !== 0) {
    console.error(`${nome} falhou com código ${resultado.status}.`);
    return false;
  }

  return true;
}

let falhas = 0;

for (const teste of testesPython) {
  if (!executar(`Backend: ${teste}`, python, [teste])) {
    falhas += 1;
  }
}

if (process.platform === 'win32') {
  if (!executar('Frontend: Playwright', process.env.ComSpec || 'cmd.exe', [
    '/d', '/s', '/c', 'npm run test:frontend',
  ])) {
    falhas += 1;
  }
} else if (!executar('Frontend: Playwright', 'npm', ['run', 'test:frontend'])) {
  falhas += 1;
}

console.log('\n' + '='.repeat(60));
if (falhas > 0) {
  console.error(`${falhas} comando(s) de teste falharam.`);
  process.exit(1);
}

console.log('TODOS OS TESTES PASSARAM!');
