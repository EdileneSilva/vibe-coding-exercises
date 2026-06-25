#!/usr/bin/env bun

import { $ } from "bun";
import fs from "node:fs";
import process from "node:process";

console.log("Running commit message validation...\n");

const commitMsgFile = process.argv[2] || "COMMIT_EDITMSG";

if (!fs.existsSync(commitMsgFile)) {
  console.error("Commit message file not found:", commitMsgFile);
  process.exit(1);
}

const commitMsg = fs.readFileSync(commitMsgFile, "utf-8").trim();

console.log("Commit message:", JSON.stringify(commitMsg));

// Check for empty message
if (!commitMsg || commitMsg.length === 0) {
  console.error("❌ Commit message is empty");
  process.exit(1);
}

// Check using commitlint
try {
  const result = await $`commitlint --edit ${commitMsgFile}`.quiet();
  if (result.exitCode !== 0) {
    console.error("❌ Invalid commit message format. Use 'bun run commit' for interactive commit or follow conventional commits.");
    process.exit(1);
  }
} catch (error) {
  console.error("❌ Commit message validation failed:", error);
  process.exit(1);
}

console.log("✅ Commit message is valid.");
process.exit(0);
