#!/usr/bin/env bun

import { $ } from "bun";
import process from "node:process";

console.log("Running pre-push hooks...\n");

const hooks = [
  {
    name: "Markdown lint",
    command: "bun run lint:md",
  },
  {
    name: "YAML lint",
    command: "bun run lint:yaml",
  },
  {
    name: "Commit message lint",
    command: "bun run lint:commit",
  },
  {
    name: "Secrets detection",
    command: "bun run secrets:scan",
  },
];

let failed = false;

for (const hook of hooks) {
  console.log(`Running: ${hook.name}...`);
  try {
    const result = await $`${hook.command}`.quiet();
    if (result.exitCode !== 0) {
      console.error(`✗ ${hook.name} failed`);
      failed = true;
    } else {
      console.log(`✓ ${hook.name} passed`);
    }
  } catch (error) {
    console.error(`✗ ${hook.name} failed with error:`, error);
    failed = true;
  }
}

if (failed) {
  console.error("\n❌ Pre-push hooks failed. Push aborted.");
  process.exit(1);
}

console.log("\n✅ All pre-push hooks passed.");
process.exit(0);
