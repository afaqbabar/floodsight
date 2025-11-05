import { test, expect } from '@playwright/test';

test.describe('FloodSight Landing Page', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/FloodSight/);
    await expect(page.locator('h1')).toContainText('See floods before they happen');
  });

  test('should have working navigation links', async ({ page }) => {
    await page.goto('/');

    // Test anchor navigation
    await page.click('a[href="#features"]');
    await expect(page.locator('#features')).toBeVisible();

    await page.click('a[href="#pricing"]');
    await expect(page.locator('#pricing')).toBeVisible();

    await page.click('a[href="#contact"]');
    await expect(page.locator('#contact')).toBeVisible();
  });

  test('should have accessible skip link', async ({ page }) => {
    await page.goto('/');
    await page.keyboard.press('Tab');
    const skipLink = page.locator('.skip-link');
    await expect(skipLink).toBeFocused();
    await expect(skipLink).toHaveText('Skip to content');
  });

  test('should have working signup form', async ({ page }) => {
    await page.goto('/');
    await page.locator('#signup').scrollIntoViewIfNeeded();

    // Check form exists and has required fields
    const form = page.locator('#signup .form');
    await expect(form).toBeVisible();
    await expect(page.locator('#name')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#org')).toBeVisible();
  });
});

test.describe('Legal Pages', () => {
  test('should load impressum page', async ({ page }) => {
    await page.goto('/impressum');
    await expect(page).toHaveTitle(/Impressum/);
    await expect(page.locator('h1')).toContainText('Impressum');
  });

  test('should load privacy page', async ({ page }) => {
    await page.goto('/privacy');
    await expect(page).toHaveTitle(/Privacy/);
    await expect(page.locator('h1')).toContainText('Privacy');
  });

  test('should load terms page', async ({ page }) => {
    await page.goto('/terms');
    await expect(page).toHaveTitle(/Terms/);
    await expect(page.locator('h1')).toContainText('Terms');
  });

  test('should load security page', async ({ page }) => {
    await page.goto('/security');
    await expect(page).toHaveTitle(/Security/);
    await expect(page.locator('h1')).toContainText('Security');
  });

  test('should navigate from footer to legal pages', async ({ page }) => {
    await page.goto('/');

    // Click impressum link in footer
    await page.click('footer a[href="/impressum"]');
    await expect(page).toHaveURL(/\/impressum/);
    await expect(page.locator('h1')).toContainText('Impressum');

    // Navigate back and try privacy
    await page.goto('/');
    await page.click('footer a[href="/privacy"]');
    await expect(page).toHaveURL(/\/privacy/);
  });
});

test.describe('404 Handling', () => {
  test('should show 404 page for non-existent routes', async ({ page }) => {
    const response = await page.goto('/this-page-does-not-exist');
    expect(response?.status()).toBe(404);
  });
});

test.describe('Mobile Responsive', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('should display mobile navigation correctly', async ({ page }) => {
    await page.goto('/');
    const header = page.locator('.site-header');
    await expect(header).toBeVisible();

    // Mobile nav button should be present
    const navToggle = page.locator('.nav-toggle');
    if (await navToggle.isVisible()) {
      await expect(navToggle).toHaveAttribute('aria-expanded', 'false');
    }
  });

  test('should have readable text on mobile', async ({ page }) => {
    await page.goto('/');
    const hero = page.locator('.hero h1');
    await expect(hero).toBeVisible();
    // Font should be responsive
    const fontSize = await hero.evaluate((el) => window.getComputedStyle(el).fontSize);
    expect(parseInt(fontSize)).toBeGreaterThan(20);
  });
});

test.describe('Accessibility', () => {
  test('should have proper landmarks', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('header[role="banner"]')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('footer[role="contentinfo"]')).toBeVisible();
  });

  test('should have alt text for images', async ({ page }) => {
    await page.goto('/');
    const images = page.locator('img');
    const count = await images.count();
    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      await expect(img).toHaveAttribute('alt');
    }
  });

  test('should have form labels', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('label[for="name"]')).toBeVisible();
    await expect(page.locator('label[for="email"]')).toBeVisible();
    await expect(page.locator('label[for="org"]')).toBeVisible();
  });
});

