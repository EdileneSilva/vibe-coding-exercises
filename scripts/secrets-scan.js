#!/usr/bin/env bun

import { $ } from "bun";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

console.log("Scanning for secrets...\n");

const repoRoot = process.cwd();
const gitignorePath = path.join(repoRoot, ".gitignore");
const patterns = [
  // Database URLs
  /(?:mysql|postgres|postgresql|mongodb|redis|sqlite):\/\/[^\s"']+/i,
  // AWS
  /(?:AKIA|ASIA)[A-Z0-9]{16,}/i,
  /aws[_-]?access[_-]?key[_-]?id['"\s]*[:=]['"\s]*[A-Z0-9]{20,}/i,
  /aws[_-]?secret[_-]?access[_-]?key['"\s]*[:=]['"\s]*[A-Za-z0-9/+=]{40,}/i,
  // GitHub
  /(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9_]{36,}/i,
  // GitLab
  /glpat-[a-zA-Z0-9_-]{20,}/i,
  // Slack
  /xox[baprs]-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9-]*/i,
  // Generic
  /(?:password|passwd|pwd|secret|token|api[_-]?key)['"\s]*[:=]['"\s]*[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:'",.<>/?`~]{16,}/i,
  // Private keys
  /-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----/i,
  // JWT tokens
  /eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+/i,
];

const excludeDirs = [
  "node_modules",
  ".git",
  "dist",
  "build",
  "coverage",
  ".vibe",
  "__pycache__",
  ".pytest_cache",
  "*.lock",
  ".env.example",
  "test",
  "tests",
  "fixtures",
  "examples",
  "samples",
];

const allowlist = [
  "password: test",
  "password: example",
  "secret: placeholder",
  "token: dummy",
  "api_key: REPLACE_ME",
  "DATABASE_URL=sqlite:///",
  "DATABASE_URL=postgresql://",
];

function shouldExclude(filepath) {
  for (const exclude of excludeDirs) {
    if (filepath.includes(`/${exclude}/`) || filepath.endsWith(exclude)) {
      return true;
    }
  }
  return false;
}

function isAllowed(content, filepath) {
  // Allow .env.example and similar files
  if (filepath.includes(".env.example") || filepath.includes("AGENTS.md") || filepath.includes("README")) {
    return true;
  }
  
  for (const allowed of allowlist) {
    if (content.includes(allowed)) {
      return true;
    }
  }
  return false;
}

async function scanFile(filepath) {
  try {
    const content = fs.readFileSync(filepath, "utf-8");
    
    for (const pattern of patterns) {
      const matches = content.match(pattern);
      if (matches && !isAllowed(content, filepath)) {
        return {
          filepath,
          matches,
        };
      }
    }
  } catch (error) {
    // Ignore files we can't read
  }
  return null;
}

async function walkDir(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const filepath = path.join(dir, file);
    const stat = fs.statSync(filepath);
    
    if (stat.isDirectory()) {
      if (!shouldExclude(filepath)) {
        await walkDir(filepath, fileList);
      }
    } else if (!shouldExclude(filepath)) {
      fileList.push(filepath);
    }
  }
  
  return fileList;
}

async function main() {
  let foundSecrets = false;
  const issues = [];
  
  const files = await walkDir(repoRoot);
  
  console.log(`Scanning ${files.length} files...`);
  
  for (const filepath of files) {
    const result = await scanFile(filepath);
    if (result) {
      foundSecrets = true;
      issues.push({
        file: filepath.replace(repoRoot + "/", ""),
        matches: result.matches,
      });
    }
  }
  
  if (foundSecrets) {
    console.error("\n❌ Potential secrets detected:");
    for (const issue of issues) {
      console.error(`  📄 ${issue.file}`);
      console.error(`     Matches: ${JSON.stringify(issue.matches)}`);
    }
    console.error("\n⚠️  Please review these potential secrets. If they are false positives, add them to the allowlist.");
    console.error("💡 Use .env files for secrets and add .env to .gitignore");
    process.exit(1);
  } else {
    console.log("✅ No secrets detected.");
  }
  
  process.exit(foundSecrets ? 1 : 0);
}

main().catch((error) => {
  console.error("Error during secrets scan:", error);
  process.exit(1);
});
