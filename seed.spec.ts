import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('logs in as a patient', async ({ page }) => {
    // Open the landing page and start the sign-in flow.
    await page.goto('/');
    await expect(page.getByText('Smarter Health Management Starts Here.')).toBeVisible();
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Fill in the patient credentials and submit the sign-in form.
    await expect(page.getByText('Sign In to Your Account')).toBeVisible();
    await page.getByRole('textbox', { name: 'Email' }).fill('trevorhuff96@gmail.com');
    await page.getByRole('textbox', { name: 'Password' }).fill('test123456');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Confirm the patient dashboard loads for the authenticated user.
    await expect(page.getByText('Welcome back, Trevor Huffstetler!')).toBeVisible();
    await expect(page.getByText('Account: trevorhuff96@gmail.com')).toBeVisible();
    await expect(page.getByText('Role: Patient')).toBeVisible();
  });
});
