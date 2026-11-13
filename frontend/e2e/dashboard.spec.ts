import { expect, test, type Page } from '@playwright/test';

const testToken = 'e2e_' + 'a'.repeat(40);
async function authenticate(page: Page) {
  await page.getByLabel('Local API access token').fill(testToken);
  await page.getByRole('button', {name: 'Apply token or clear'}).click();
}

test('create records and switch language with RTL and keyboard access', async ({page}) => {
  const rejected = await page.request.post('/api/projects', {
    headers: {'Origin': 'https://evil.example', 'Authorization': `Bearer ${testToken}`}, data: {name: 'Cross-origin test'},
  });
  expect(rejected.status()).toBe(403);
  expect((await page.request.get('/api/tasks')).status()).toBe(401);
  await page.goto('/');
  await expect(page.getByRole('status')).toContainText('Ready');
  await authenticate(page);

  await page.getByLabel('Project name').fill('مشروع AATM');
  await page.getByLabel('Description').fill('Browser test');
  await page.getByRole('button', { name: 'Create project' }).click();
  const projectSection = page.getByRole('region', { name: 'Projects' });
  await expect(projectSection.locator('li')).toContainText('مشروع AATM');

  await page.getByLabel('Agent name').fill('QA Agent');
  await page.getByLabel('Role', { exact: true }).fill('QA');
  const agentSection = page.getByRole('region', { name: 'Agent configurations' });
  await agentSection.getByLabel('Project').selectOption({label: 'مشروع AATM'});
  await page.getByRole('button', { name: 'Create configuration' }).click();
  await expect(agentSection.locator('li')).toContainText('QA Agent');
  await expect(agentSection.locator('li')).toContainText('Agent process lifecycle not implemented');

  const taskSection = page.getByRole('region', { name: 'Planning tasks', exact: true });
  await taskSection.getByLabel('Project').selectOption({label: 'مشروع AATM'});
  await page.getByLabel('Task title').fill('Check UI');
  await page.getByRole('button', { name: 'Create task' }).click();
  await expect(taskSection.locator('li')).toContainText('Check UI');
  await expect(taskSection.locator('li')).toContainText('Pending');
  await expect(page.getByRole('region', {name: 'Ready planning tasks'}).locator('li')).toContainText('Check UI');

  await page.getByLabel('Language').selectOption('ar');
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.getByRole('heading', {name: 'المشاريع'})).toBeVisible();
  await expect(page.getByRole('region', {name: 'المهام التخطيطية'}).locator('li')).toContainText('معلّقة');
  const input = page.getByLabel('اسم المشروع');
  await input.focus();
  await expect(input).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('الوصف')).toBeFocused();
  // The section inherits RTL; user-entered input uses dir=auto.
  await expect(page.getByRole('region', {name: 'المشاريع'})).toHaveCSS('direction', 'rtl');

  await page.getByLabel('اللغة').selectOption('fa');
  await expect(page.locator('html')).toHaveAttribute('lang', 'fa');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.getByRole('heading', {name: 'پروژه‌ها'})).toBeVisible();
  await expect(page.getByRole('region', {name: 'وظایف برنامه‌ریزی'}).locator('li')).toContainText('در انتظار');
  await page.getByLabel('زبان').selectOption('en');
  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  await expect(projectSection.locator('li')).toContainText('مشروع AATM');
  await taskSection.getByRole('button', {name: 'Mark complete manually'}).click();
  await expect(taskSection.locator('li')).toContainText('Completed');
  await expect(page.getByRole('region', {name: 'Ready planning tasks'}).locator('li')).toHaveCount(0);
  await expect(page.getByRole('region', {name: 'Recent task activity'}).locator('li').first()).toContainText('Task completed manually');
});

test('manage task dependencies and inspect readiness', async ({page}) => {
  await page.goto('/');
  await expect(page.getByRole('status')).toContainText('Ready');
  await authenticate(page);
  await page.getByLabel('Project name').fill('Dependencies project');
  await page.getByRole('button', {name: 'Create project'}).click();
  await page.getByLabel('Agent name').fill('Planner');
  await page.getByLabel('Role', {exact: true}).fill('Planner');
  await page.getByRole('region', {name: 'Agent configurations'}).getByLabel('Project').selectOption({label: 'Dependencies project'});
  await page.getByRole('button', {name: 'Create configuration'}).click();
  await expect(page.getByRole('region', {name: 'Agent configurations'}).locator('li').filter({hasText: 'Planner'})).toBeVisible();
  const section = page.getByRole('region', {name: 'Planning tasks', exact: true});
  for (const title of ['Consumer', 'Prerequisite']) {
    await section.getByLabel('Project').selectOption({label: 'Dependencies project'});
    await page.getByLabel('Task title').fill(title);
    await page.getByRole('button', {name: 'Create task'}).click();
    await expect(section.locator('li').filter({hasText: title}).first()).toBeVisible();
  }
  const consumer = await page.getByLabel('Select task').locator('option').filter({hasText: 'Consumer'}).getAttribute('value');
  await page.getByLabel('Select task').selectOption(consumer!);
  await expect(page.getByText('Ready for manual completion', {exact: true})).toBeVisible();
  await expect(page.getByText('No runs loaded.')).toBeVisible();
  const assignment = page.getByRole('combobox', {name: 'Assigned agent configuration'});
  await assignment.selectOption({index: 1});
  await page.getByRole('button', {name: 'Save assignment'}).click();
  await expect(page.getByRole('region', {name: 'Recent task activity'}).locator('li').first()).toContainText('Task assigned for planning');
  await page.reload();
  await expect(page.getByRole('alert')).toContainText('Could not load data');
  await authenticate(page);
  await page.getByLabel('Select task').selectOption(consumer!);
  await expect(assignment.locator('option:checked')).toContainText('Planner');
  await page.getByRole('combobox', {name: 'Prerequisite', exact: true}).selectOption({index: 1});
  await page.getByRole('button', {name: 'Add dependency'}).click();
  await expect(page.getByText('Not ready for manual completion', {exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Ready planning tasks'}).locator('li').filter({hasText: 'Consumer'})).toHaveCount(0);
  await expect(page.getByText(/Incomplete prerequisites:/)).toContainText('Prerequisite');
  await section.locator('li').filter({hasText: 'Consumer'}).first().getByRole('button', {name: 'Mark complete manually'}).click();
  await expect(page.getByRole('alert')).toContainText('Could not complete task');
  await page.getByRole('button', {name: /Remove dependency: Prerequisite/}).click();
  await expect(page.getByText('Ready for manual completion', {exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Ready planning tasks'}).locator('li').filter({hasText: 'Consumer'})).toHaveCount(1);
  await page.getByLabel('Language').selectOption('ar');
  await expect(page.getByText('جاهزة للإكمال اليدوي')).toBeVisible();
  await page.getByLabel('اللغة').selectOption('en');
  await section.locator('li').filter({hasText: 'Consumer'}).first().getByRole('button', {name: 'Mark complete manually'}).click();
  await expect(page.getByRole('button', {name: 'Remove assignment'})).toBeVisible();
  await page.getByRole('button', {name: 'Remove assignment'}).click();
  await expect(page.getByRole('button', {name: 'Remove assignment'})).toHaveCount(0);
  await expect(page.getByRole('region', {name: 'Recent task activity'}).locator('li').first()).toContainText('Task unassigned');
});
