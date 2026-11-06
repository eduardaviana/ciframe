const { defineConfig } = require('@playwright/test');
const os = require('os');
const path = require('path');

const dbPath = path.join(
  os.tmpdir(),
  'deciframe-e2e-' + process.pid + '-' + Date.now() + '.db'
);
const channel = process.env.PW_CHANNEL;
const python = process.env.PYTHON || (process.platform === 'win32' ? 'py' : 'python3');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 60000,
  expect: {
    timeout: 10000,
  },
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:5077',
    headless: true,
    ...(channel === 'none' ? {} : { channel: channel || 'msedge' }),
    viewport: { width: 1280, height: 800 },
  },
  webServer: {
    command: python + ' -c "import main; main.app.run(host=\'127.0.0.1\', port=5077, debug=False)"',
    cwd: __dirname,
    url: 'http://127.0.0.1:5077/generos',
    reuseExistingServer: false,
    timeout: 120000,
    env: {
      ...process.env,
      PYTHONUTF8: '1',
      SEQUENCIAS_DB_PATH: dbPath,
    },
  },
});
