const fs = require('fs');
const path = require('path');

class DetailedStatusReporter {
  constructor(options = {}) {
    this.outputDir = options.outputDir || 'playwright-report-data';
    this.markdownFile = options.markdownFile || 'detailed-report.md';
    this.jsonFile = options.jsonFile || 'detailed-report.json';
    this.startedAt = null;
    this.testEntries = [];
    this.totalTests = 0;
  }

  onBegin(config, suite) {
    this.startedAt = new Date();
    this.totalTests = suite.allTests().length;
  }

  onTestEnd(test, result) {
    const outcome = this._classify(result);
    const titlePath = test.titlePath().filter(Boolean);
    const location = `${test.location.file}:${test.location.line}:${test.location.column}`;

    this.testEntries.push({
      id: titlePath.join(' > '),
      file: test.location.file,
      location,
      titlePath,
      title: test.title,
      outcome,
      status: result.status,
      expectedStatus: test.expectedStatus,
      durationMs: result.duration,
      retry: result.retry,
      error: result.error ? this._formatError(result.error) : '',
    });
  }

  async onEnd(result) {
    const endedAt = new Date();
    const grouped = {
      passed: [],
      failed: [],
      untested: [],
    };

    for (const entry of this.testEntries) {
      grouped[entry.outcome].push(entry);
    }

    const summary = {
      generatedAt: endedAt.toISOString(),
      startedAt: this.startedAt ? this.startedAt.toISOString() : null,
      durationMs: this.startedAt ? endedAt.getTime() - this.startedAt.getTime() : null,
      overallStatus: result.status,
      total: this.totalTests,
      passed: grouped.passed.length,
      failed: grouped.failed.length,
      untested: grouped.untested.length,
      tests: this.testEntries,
    };

    fs.mkdirSync(this.outputDir, { recursive: true });
    fs.writeFileSync(
      path.join(this.outputDir, this.jsonFile),
      JSON.stringify(summary, null, 2),
      'utf8',
    );
    fs.writeFileSync(
      path.join(this.outputDir, this.markdownFile),
      this._buildMarkdown(summary, grouped),
      'utf8',
    );
  }

  _classify(result) {
    if (result.status === 'passed') {
      return 'passed';
    }

    if (result.status === 'failed' || result.status === 'timedOut' || result.status === 'interrupted') {
      return 'failed';
    }

    return 'untested';
  }

  _formatError(error) {
    if (!error) {
      return '';
    }

    if (typeof error === 'string') {
      return error;
    }

    return [error.message, error.snippet, error.stack]
      .filter(Boolean)
      .join('\n')
      .trim();
  }

  _buildMarkdown(summary, grouped) {
    const lines = [];
    lines.push('# Playwright Detailed Report');
    lines.push('');
    lines.push(`Generated: ${summary.generatedAt}`);
    lines.push(`Overall status: ${summary.overallStatus}`);
    lines.push(`Total tests: ${summary.total}`);
    lines.push(`Passed: ${summary.passed}`);
    lines.push(`Failed: ${summary.failed}`);
    lines.push(`Untested: ${summary.untested}`);
    lines.push('');

    lines.push('## Summary');
    lines.push('');
    lines.push('| Status | Count |');
    lines.push('| --- | ---: |');
    lines.push(`| Passed | ${summary.passed} |`);
    lines.push(`| Failed | ${summary.failed} |`);
    lines.push(`| Untested | ${summary.untested} |`);
    lines.push('');

    this._appendSection(lines, 'Passed', grouped.passed);
    this._appendSection(lines, 'Failed', grouped.failed, true);
    this._appendSection(lines, 'Untested', grouped.untested);

    return `${lines.join('\n')}\n`;
  }

  _appendSection(lines, title, tests, includeErrors = false) {
    lines.push(`## ${title}`);
    lines.push('');

    if (!tests.length) {
      lines.push(`No ${title.toLowerCase()} tests.`);
      lines.push('');
      return;
    }

    for (const test of tests) {
      lines.push(`### ${test.titlePath.join(' > ')}`);
      lines.push('');
      lines.push(`- File: ${test.file}`);
      lines.push(`- Location: ${test.location}`);
      lines.push(`- Playwright status: ${test.status}`);
      lines.push(`- Expected status: ${test.expectedStatus}`);
      lines.push(`- Duration: ${test.durationMs} ms`);
      if (typeof test.retry === 'number' && test.retry > 0) {
        lines.push(`- Retry: ${test.retry}`);
      }
      if (includeErrors && test.error) {
        lines.push('- Error:');
        lines.push('```text');
        lines.push(test.error);
        lines.push('```');
      }
      lines.push('');
    }
  }
}

module.exports = DetailedStatusReporter;
