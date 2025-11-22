import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';
import fs from 'fs';
import path from 'path';

async function runLighthouse() {
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
  const options = {
    logLevel: 'info',
    output: 'html',
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    port: chrome.port,
  };

  // Use LH_URL if provided (e.g. different port in local dev),
  // otherwise default to Vite preview port (4173) used in CI.
  const url = process.env.LH_URL || 'http://localhost:4173';
  console.log(`Running Lighthouse on ${url}...`);

  const runnerResult = await lighthouse(url, options);

  // Save HTML report
  const reportDir = './lighthouse-report';
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir);
  }

  const reportPath = path.join(reportDir, 'report.html');
  fs.writeFileSync(reportPath, runnerResult.report);

  // Extract scores
  const { lhr } = runnerResult;
  const scores = {
    performance: Math.round(lhr.categories.performance.score * 100),
    accessibility: Math.round(lhr.categories.accessibility.score * 100),
    bestPractices: Math.round(lhr.categories['best-practices'].score * 100),
    seo: Math.round(lhr.categories.seo.score * 100),
  };

  // Generate markdown summary
  const markdown = `# Lighthouse Report

**Date**: ${new Date().toISOString().split('T')[0]}
**URL**: ${url}

## Scores

| Category | Score | Target | Status |
|----------|-------|--------|--------|
| Performance | ${scores.performance} | ≥90 | ${scores.performance >= 90 ? '✅' : '⚠️'} |
| Accessibility | ${scores.accessibility} | ≥85 | ${scores.accessibility >= 85 ? '✅' : '⚠️'} |
| Best Practices | ${scores.bestPractices} | ≥90 | ${scores.bestPractices >= 90 ? '✅' : '⚠️'} |
| SEO | ${scores.seo} | ≥90 | ${scores.seo >= 90 ? '✅' : '⚠️'} |

## Details

Full HTML report: \`${reportPath}\`

### Key Metrics
- **First Contentful Paint**: ${lhr.audits['first-contentful-paint'].displayValue}
- **Largest Contentful Paint**: ${lhr.audits['largest-contentful-paint'].displayValue}
- **Total Blocking Time**: ${lhr.audits['total-blocking-time'].displayValue}
- **Cumulative Layout Shift**: ${lhr.audits['cumulative-layout-shift'].displayValue}
- **Speed Index**: ${lhr.audits['speed-index'].displayValue}
`;

  fs.writeFileSync(path.join(reportDir, 'LIGHTHOUSE.md'), markdown);

  console.log('\n' + markdown);
  console.log(`\nFull report saved to: ${reportPath}`);

  await chrome.kill();

  // Exit with error if targets not met
  const passed =
    scores.performance >= 90 &&
    scores.accessibility >= 85 &&
    scores.bestPractices >= 90 &&
    scores.seo >= 90;

  process.exit(passed ? 0 : 1);
}

runLighthouse().catch((err) => {
  console.error(err);
  process.exit(1);
});
