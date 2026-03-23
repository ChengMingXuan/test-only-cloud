import { test, expect, request as playwrightRequest, type APIRequestContext, type Page } from '@playwright/test';

const FRONTEND_BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:8000';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://localhost:5000';
const TENANT_ID = '00000000-0000-0000-0000-000000000001';
const ADMIN_USERNAME = process.env.E2E_ADMIN_USERNAME;
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD;

type LoginResponse = {
  data: {
    token: {
      accessToken: string;
      refreshToken: string;
    };
  };
};

type SensitiveWordItem = {
  id: string;
  word: string;
  category: string;
  replacement?: string;
};

type SensitiveCategoryItem = {
  id: string;
  name: string;
  sortOrder?: number;
};

const runId = Date.now().toString();
const createdWord = `e2e-${runId}-add`;
const editedWord = `e2e-${runId}-edit`;
const importWordOne = `e2e-${runId}-import-1`;
const importWordTwo = `e2e-${runId}-import-2`;
const categoryName = `E2E分类-${runId}`;

let apiContext: APIRequestContext;
let accessToken = '';
let refreshToken = '';

function requireCredentials() {
  if (!ADMIN_USERNAME || !ADMIN_PASSWORD) {
    throw new Error('缺少 E2E_ADMIN_USERNAME 或 E2E_ADMIN_PASSWORD 环境变量');
  }
}

function getAuthHeaders() {
  return {
    Authorization: `Bearer ${accessToken}`,
    'X-Tenant-Id': TENANT_ID,
  };
}

async function login() {
  requireCredentials();

  const response = await apiContext.post(`${API_BASE_URL}/api/auth/login`, {
    data: {
      username: ADMIN_USERNAME,
      password: ADMIN_PASSWORD,
    },
  });

  expect(response.ok()).toBeTruthy();
  const body = (await response.json()) as LoginResponse;
  accessToken = body.data.token.accessToken;
  refreshToken = body.data.token.refreshToken;
}

async function fetchWord(word: string) {
  const response = await apiContext.get(`${API_BASE_URL}/api/security/sensitive-word`, {
    headers: getAuthHeaders(),
    params: {
      pageIndex: '1',
      pageSize: '20',
      keyword: word,
    },
  });

  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  const items = (body?.data?.items || []) as SensitiveWordItem[];
  return items.find((item) => item.word === word);
}

async function fetchCategory(name: string) {
  const response = await apiContext.get(`${API_BASE_URL}/api/security/sensitive-word/categories`, {
    headers: getAuthHeaders(),
  });

  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  const categories = (Array.isArray(body?.data) ? body.data : body?.data?.categories || []) as SensitiveCategoryItem[];
  return categories.find((item) => item.name === name);
}

async function deleteWordIfExists(word: string) {
  const target = await fetchWord(word);
  if (!target) {
    return;
  }

  const response = await apiContext.delete(`${API_BASE_URL}/api/security/sensitive-word/${target.id}`, {
    headers: getAuthHeaders(),
  });
  expect(response.ok()).toBeTruthy();
}

async function deleteCategoryIfExists(name: string) {
  const target = await fetchCategory(name);
  if (!target) {
    return;
  }

  const response = await apiContext.delete(`${API_BASE_URL}/api/security/sensitive-word/categories/${target.id}`, {
    headers: getAuthHeaders(),
  });
  expect(response.ok()).toBeTruthy();
}

async function injectLogin(page: Page) {
  await page.addInitScript(
    ({ token, refresh, tenantId }) => {
      localStorage.setItem('jgsy_access_token', token);
      localStorage.setItem('jgsy_refresh_token', refresh);
      localStorage.setItem('tenantId', tenantId);
      localStorage.setItem('tenantName', 'JGSY总部');
    },
    { token: accessToken, refresh: refreshToken, tenantId: TENANT_ID },
  );
}

async function openSensitiveWordPage(page: Page) {
  await injectLogin(page);
  await page.goto(FRONTEND_BASE_URL, { waitUntil: 'networkidle' });
  await page.getByText('安全中心', { exact: true }).last().click();
  await page.getByText('敏感词过滤', { exact: true }).last().click();
  await page.waitForURL('**/security/sensitive-word');
  await expect(page.getByText('敏感词管理', { exact: true })).toBeVisible();
}

async function submitPrimaryModal(page: Page) {
  const submitButton = page.locator('button').filter({ hasText: /确\s*定|提\s*交|保\s*存/ }).last();
  await expect(submitButton).toBeVisible();
  await submitButton.click();
}

test.describe.serial('敏感词过滤真实 UI 定向复核', () => {
  test.beforeAll(async () => {
    apiContext = await playwrightRequest.newContext({ ignoreHTTPSErrors: true });
    await login();
    await deleteWordIfExists(createdWord);
    await deleteWordIfExists(editedWord);
    await deleteWordIfExists(importWordOne);
    await deleteWordIfExists(importWordTwo);
    await deleteCategoryIfExists(categoryName);
  });

  test.afterAll(async () => {
    await deleteWordIfExists(createdWord);
    await deleteWordIfExists(editedWord);
    await deleteWordIfExists(importWordOne);
    await deleteWordIfExists(importWordTwo);
    await deleteCategoryIfExists(categoryName);
    await apiContext.dispose();
  });

  test('新增敏感词链路可用', async ({ page }) => {
    await openSensitiveWordPage(page);

    await page.getByRole('button', { name: '添加敏感词' }).click();
    const dialog = page.locator('.ant-modal:visible').last();
    await dialog.getByPlaceholder('请输入单个敏感词；批量新增请使用“批量导入”').fill(createdWord);
    await dialog.getByPlaceholder('处理方式为替换时生效').fill('已脱敏');
    await submitPrimaryModal(page);

    await expect.poll(async () => {
      const item = await fetchWord(createdWord);
      return item?.replacement || null;
    }).toBe('已脱敏');

    await expect(page.locator('tr').filter({ hasText: createdWord }).first()).toBeVisible();
  });

  test('编辑敏感词链路可用', async ({ page }) => {
    await openSensitiveWordPage(page);

    const row = page.locator('tr').filter({ hasText: createdWord }).first();
    await expect(row).toBeVisible();
    await row.getByRole('button', { name: '编辑' }).click();

    const dialog = page.locator('.ant-modal:visible').last();
    await dialog.getByPlaceholder('请输入单个敏感词；批量新增请使用“批量导入”').fill(editedWord);
    await dialog.getByPlaceholder('处理方式为替换时生效').fill('编辑后替换词');
    await submitPrimaryModal(page);

    await expect.poll(async () => {
      const item = await fetchWord(editedWord);
      return item?.replacement || null;
    }).toBe('编辑后替换词');

    await expect.poll(async () => {
      const item = await fetchWord(createdWord);
      return item ? 'exists' : 'missing';
    }).toBe('missing');
  });

  test('分类排序链路可用', async ({ page }) => {
    await openSensitiveWordPage(page);
    await page.getByRole('tab', { name: '分类管理' }).click();
    await page.getByRole('button', { name: '添加分类' }).click();

    const createDialog = page.locator('.ant-modal:visible').last();
    await createDialog.getByLabel('分类名称').fill(categoryName);
    await createDialog.getByLabel('描述').fill('E2E 分类排序验证');
    await createDialog.getByLabel('排序').fill('999');
    await submitPrimaryModal(page);

    await expect.poll(async () => {
      const item = await fetchCategory(categoryName);
      return item?.sortOrder ?? null;
    }).toBe(999);

    const row = page.locator('tr').filter({ hasText: categoryName }).first();
    await expect(row).toBeVisible();
    await row.getByRole('button', { name: '编辑' }).click();

    const editDialog = page.locator('.ant-modal:visible').last();
    await editDialog.getByLabel('排序').fill('0');
    await submitPrimaryModal(page);

    await expect.poll(async () => {
      const item = await fetchCategory(categoryName);
      return item?.sortOrder ?? null;
    }).toBe(0);

    await expect(page.locator('tbody tr').first()).toContainText(categoryName);
  });

  test('批量导入链路可用', async ({ page }) => {
    await openSensitiveWordPage(page);

    await page.getByRole('button', { name: '批量导入' }).click();
    const dialog = page.locator('.ant-modal').last();
    await dialog.locator('select').nth(0).selectOption(categoryName);
    await dialog.locator('select').nth(1).selectOption('low');
    await dialog.locator('textarea').fill(`${importWordOne}\n${importWordTwo}`);
    await dialog.getByRole('button', { name: '导入' }).click();

    await expect.poll(async () => {
      const first = await fetchWord(importWordOne);
      const second = await fetchWord(importWordTwo);
      return [first?.category, second?.category].join(',');
    }).toBe(`${categoryName},${categoryName}`);
  });

  test('在线检测链路可用', async ({ page }) => {
    await openSensitiveWordPage(page);

    await page.getByRole('button', { name: '在线检测' }).click();
    const drawer = page.locator('.ant-drawer').last();
    await drawer.locator('textarea').fill(`这段文本包含 ${editedWord} 和 ${importWordOne}，需要被检测。`);
    await drawer.getByRole('button', { name: '开始检测' }).click();

    await expect(drawer.getByText(editedWord, { exact: false })).toBeVisible();
    await expect(drawer.getByText(importWordOne, { exact: false })).toBeVisible();
  });
});