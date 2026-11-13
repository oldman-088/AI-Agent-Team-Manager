import { expect, test } from '@playwright/test';

test('create records and switch language with RTL and keyboard access', async ({page}) => {
  await page.goto('/');
  await expect(page.getByRole('status')).toContainText('Ready');

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
  await expect(agentSection.locator('li')).toContainText('Execution not implemented');

  const taskSection = page.getByRole('region', { name: 'Planning tasks' });
  await taskSection.getByLabel('Project').selectOption({label: 'مشروع AATM'});
  await page.getByLabel('Task title').fill('Check UI');
  await page.getByRole('button', { name: 'Create task' }).click();
  await expect(taskSection.locator('li')).toContainText('Check UI');
  await expect(taskSection.locator('li')).toContainText('Pending');

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
  const direction = await input.evaluate(element => getComputedStyle(element).direction);
  // dir=auto on an empty input may be LTR; check inherited section direction instead.
  expect(['ltr', 'rtl']).toContain(direction);
  await expect(page.getByRole('region', {name: 'المشاريع'})).toHaveCSS('direction', 'rtl');

  await page.getByLabel('اللغة').selectOption('fa');
  await expect(page.locator('html')).toHaveAttribute('lang', 'fa');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.getByRole('heading', {name: 'پروژه‌ها'})).toBeVisible();
  await expect(page.getByRole('region', {name: 'وظایف برنامه‌ریزی'}).locator('li')).toContainText('در انتظار');
  await page.getByLabel('زبان').selectOption('en');
  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  await expect(projectSection.locator('li')).toContainText('مشروع AATM');
});
