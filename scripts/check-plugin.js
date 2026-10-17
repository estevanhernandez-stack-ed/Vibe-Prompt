#!/usr/bin/env node
// Static plugin check (Vibe family version). Zero dependencies.
// Ported from vibe-cartographer/scripts/check-plugin.js, 2026-10-16.
//
// Usage: node scripts/check-plugin.js [plugin-root]
//   plugin-root defaults to the single directory under plugins/ or packages/
//   that holds .claude-plugin/plugin.json.
//
// Fails (exit 1) on:
//   1. SKILL.md or command frontmatter that is missing, unterminated, or would
//      fail YAML parsing (unescaped inner double quotes, ": " in a plain
//      scalar, tab indentation). Claude Code loads such a skill with empty
//      metadata.
//   2. Command shadowing: a commands/<x>.md with a same-name skills/<x>/SKILL.md
//      must tell the agent to read ${CLAUDE_PLUGIN_ROOT}/skills/<x>/SKILL.md.
//      The slash command delivers only the command body, so without the
//      pointer the skill never loads.
// Warns (exit 0) on version-pair drift between plugin.json and the plugin's own
// npm package.
'use strict';
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');

function findPluginRoot() {
  if (process.argv[2]) return path.resolve(process.argv[2]);
  const found = [];
  for (const parent of ['plugins', 'packages']) {
    const dir = path.join(repoRoot, parent);
    if (!fs.existsSync(dir)) continue;
    for (const d of fs.readdirSync(dir, { withFileTypes: true })) {
      if (d.isDirectory() && fs.existsSync(path.join(dir, d.name, '.claude-plugin', 'plugin.json'))) found.push(path.join(dir, d.name));
    }
  }
  if (fs.existsSync(path.join(repoRoot, '.claude-plugin', 'plugin.json'))) found.push(repoRoot);
  if (found.length !== 1) {
    console.error(`check-plugin: expected one plugin root, found ${found.length}; pass it as an argument`);
    process.exit(2);
  }
  return found[0];
}

const pluginRoot = findPluginRoot();
const errors = [];
const fail = (file, msg) => errors.push(`${path.relative(repoRoot, file) || file}: ${msg}`);

function parseFrontmatter(file) {
  const lines = fs.readFileSync(file, 'utf8').replace(/^﻿/, '').split(/\r?\n/);
  if (lines[0].trimEnd() !== '---') { fail(file, 'frontmatter missing (file must start with ---)'); return null; }
  let end = -1;
  for (let i = 1; i < lines.length; i++) if (lines[i].trimEnd() === '---') { end = i; break; }
  if (end < 0) { fail(file, 'frontmatter unterminated (no closing ---)'); return null; }
  const fm = {};
  let key = null;
  for (let i = 1; i < end; i++) {
    const line = lines[i];
    if (/^[ ]*\t/.test(line)) fail(file, `line ${i + 1}: tab indentation in frontmatter`);
    if (!line.trim() || /^\s*#/.test(line)) continue;
    const m = /^([A-Za-z0-9_-]+):(?:\s+(.*)|\s*)$/.exec(line);
    if (m && !/^\s/.test(line)) {
      key = m[1];
      fm[key] = (m[2] || '').trim();
      checkScalar(file, i + 1, key, fm[key]);
    } else if (/^\s/.test(line) && key) {
      fm[key] += (fm[key] ? ' ' : '') + line.trim();
    } else {
      fail(file, `line ${i + 1}: not a "key: value" frontmatter line: ${line.slice(0, 60)}`);
    }
  }
  return fm;
}

function checkScalar(file, ln, key, val) {
  if (!val) return;
  const c = val[0];
  if (c === '"') {
    let i = 1;
    for (; i < val.length; i++) {
      if (val[i] === '\\') { i++; continue; }
      if (val[i] === '"') break;
    }
    if (i >= val.length) { fail(file, `line ${ln}: ${key}: unterminated double-quoted string`); return; }
    const rest = val.slice(i + 1).trim();
    if (rest && !rest.startsWith('#')) fail(file, `line ${ln}: ${key}: unescaped inner double quote (escape as \\")`);
  } else if (c === "'") {
    if (!/^'(?:[^']|'')*'\s*(#.*)?$/.test(val)) fail(file, `line ${ln}: ${key}: malformed single-quoted string (double inner ' as '')`);
  } else if (!'>|[{&*!%@`'.includes(c) && val !== '~') {
    if (/:(\s|$)/.test(val)) fail(file, `line ${ln}: ${key}: plain scalar contains ": " (quote the value)`);
  }
}

let skillCount = 0;
const skillsDir = path.join(pluginRoot, 'skills');
if (fs.existsSync(skillsDir)) {
  for (const d of fs.readdirSync(skillsDir, { withFileTypes: true })) {
    if (!d.isDirectory()) continue;
    const file = path.join(skillsDir, d.name, 'SKILL.md');
    if (!fs.existsSync(file)) continue;
    skillCount++;
    const fm = parseFrontmatter(file);
    if (fm && !fm.description) fail(file, 'frontmatter lacks description');
  }
}

let cmdCount = 0;
const cmdDir = path.join(pluginRoot, 'commands');
if (fs.existsSync(cmdDir)) {
  for (const f of fs.readdirSync(cmdDir).filter((n) => n.endsWith('.md'))) {
    cmdCount++;
    const file = path.join(cmdDir, f);
    const fm = parseFrontmatter(file);
    if (fm && !fm.description) fail(file, 'frontmatter lacks description');
    const name = f.slice(0, -3);
    if (fs.existsSync(path.join(skillsDir, name, 'SKILL.md'))) {
      const pointer = '${CLAUDE_PLUGIN_ROOT}/skills/' + name + '/SKILL.md';
      if (!fs.readFileSync(file, 'utf8').includes(pointer)) fail(file, `shadowing: must tell the agent to read ${pointer}`);
    }
  }
}

// Version pair: warn only. Compare plugin.json with the plugin's own npm
// package: skip private workspace roots and packages named for something else.
const plugFile = path.join(pluginRoot, '.claude-plugin', 'plugin.json');
const lv = JSON.parse(fs.readFileSync(plugFile, 'utf8')).version;
const pluginName = path.basename(pluginRoot);
const warnings = [];
for (const pkgFile of [path.join(pluginRoot, 'package.json'), path.join(repoRoot, 'package.json')]) {
  if (!fs.existsSync(pkgFile)) continue;
  const pkg = JSON.parse(fs.readFileSync(pkgFile, 'utf8'));
  if (pkg.private || !String(pkg.name || '').endsWith(pluginName)) continue;
  if (pkg.version !== lv) warnings.push(`${path.relative(repoRoot, pkgFile)} ${pkg.version} vs plugin.json ${lv}`);
  break;
}
for (const w of warnings) console.warn(`WARN version pair drift: ${w}`);

if (errors.length) {
  for (const e of errors) console.error(`FAIL ${e}`);
  process.exit(1);
}
console.log(`OK: ${skillCount} skills, ${cmdCount} commands, version ${lv}.`);
