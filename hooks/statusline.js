#!/usr/bin/env node
const fs = require('fs');

let input = '';
const stdinTimeout = setTimeout(() => process.exit(0), 3000);

process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  clearTimeout(stdinTimeout);
  try {
    const data = JSON.parse(input);
    const model = data.model?.display_name || 'Gemini 3.5 Flash';
    const effort = data.model?.effort || data.effort || 'medium';
    const remaining = data.context_window?.remaining_percentage;
    const tokensUsed = data.context_window?.tokens_used;
    const tokensTotal = data.context_window?.tokens_total;

    let ctxStr = '';
    if (remaining != null) {
      const usedPct = Math.max(0, Math.min(100, Math.round(100 - remaining)));
      
      // Select bar colors: green (<50), yellow (<75), red (>=75)
      let color = '\x1b[32m'; // Green
      if (usedPct >= 75) {
        color = '\x1b[31m'; // Red
      } else if (usedPct >= 50) {
        color = '\x1b[33m'; // Yellow
      }

      ctxStr = ` │ Context: ${color}${usedPct}%\x1b[0m`;
      if (tokensUsed != null && tokensTotal != null) {
        // Format as k tokens (e.g. 120k / 1000k)
        const usedK = (tokensUsed / 1000).toFixed(1);
        const totalK = (tokensTotal / 1000).toFixed(0);
        ctxStr += ` (${usedK}k/${totalK}k)`;
      }
    }

    // Output formatted status line: Model · Effort | Context
    process.stdout.write(`${model} · ${effort}${ctxStr}`);
  } catch (e) {
    // Fallback if parsing fails
    process.stdout.write('Gemini 3.5 Flash · medium');
  }
});
