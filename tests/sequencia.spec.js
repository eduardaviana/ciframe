const { test, expect } = require('@playwright/test');

const catalogo = (page) => page.locator('.viewWindow-panel-C .acordes-container');
const modal = (page) => page.locator('.modal');

async function abrirCadastro(page) {
  await page.getByRole('button', { name: 'Cadastrar sequência', exact: true }).click();
  await expect(modal(page)).toBeVisible();
}

async function escolherAcorde(page, acorde) {
  const regex = new RegExp('^\\s*' + acorde.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*$');
  await modal(page)
    .locator('.sequencia-cadastro-grade df-hex .acorde-wrapper')
    .filter({ hasText: regex })
    .first()
    .click();
}

async function cadastrarCEm(page) {
  await abrirCadastro(page);
  await escolherAcorde(page, 'C');
  await escolherAcorde(page, 'Em');
  await expect(modal(page).locator('.sequencia-selecionada df-hex')).toHaveCount(2);
  await modal(page).getByRole('button', { name: 'Cadastrar', exact: true }).click();
}

test.describe('sequências customizadas', () => {
  test('catálogo, cadastro, toast, busca e duplicata', async ({ page }) => {
    await page.goto('/#/porsequencia');

    await expect(catalogo(page)).toHaveCount(6);

    await cadastrarCEm(page);

    const toast = page.locator('.sequencia-toast');
    await expect(toast).toContainText('Sequência cadastrada com sucesso.');
    await expect(catalogo(page)).toHaveCount(7);

    const requestPromise = page.waitForRequest((request) =>
      decodeURIComponent(request.url()).includes('sequencia=C,Em')
    );
    await catalogo(page).nth(6).locator('.acorde-wrapper').first().click();
    const request = await requestPromise;
    expect(decodeURIComponent(request.url())).toContain('sequencia=C,Em');

    await expect(toast).toBeHidden({ timeout: 5000 });

    await cadastrarCEm(page);
    await expect(modal(page).locator('.alert-danger')).toContainText(
      'sequência já cadastrada'
    );
    await expect(modal(page)).toBeVisible();
  });

  test('mostra erro de rede ao cadastrar', async ({ page }) => {
    await page.route('**/sequencias', async (route) => {
      if (route.request().method() === 'POST') {
        await route.abort('failed');
      } else {
        await route.continue();
      }
    });

    await page.goto('/#/porsequencia');
    await expect(catalogo(page)).not.toHaveCount(0);

    await cadastrarCEm(page);

    await expect(modal(page).locator('.alert-danger')).toContainText(
      'Não foi possível cadastrar a sequência. Tente novamente.'
    );
    await expect(modal(page)).toBeVisible();
  });

  test('mostra erro quando o catálogo não carrega', async ({ page }) => {
    await page.route('**/sequencias', async (route) => {
      if (route.request().method() === 'GET') {
        await route.abort('failed');
      } else {
        await route.continue();
      }
    });

    await page.goto('/#/porsequencia');

    await expect(page.locator('.viewWindow-panel-C .alert-danger')).toContainText(
      'Não foi possível carregar o catálogo.'
    );
    await expect(catalogo(page)).toHaveCount(0);
  });

  test('modal não cria rolagem horizontal em 375px', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 800 });
    await page.goto('/#/porsequencia');
    await expect(catalogo(page)).not.toHaveCount(0);

    await abrirCadastro(page);

    const semRolagemHorizontal = await page.evaluate(() =>
      document.documentElement.scrollWidth <= window.innerWidth + 1
    );
    expect(semRolagemHorizontal).toBe(true);
  });
});
