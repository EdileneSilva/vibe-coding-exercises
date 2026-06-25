module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:security/recommended",
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: "module",
  },
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  rules: {
    // Security rules
    "security/detect-object-injection": "error",
    "security/detect-child-process": "warn",
    "security/detect-disable-mustache-escape": "error",
    "security/detect-eval-with-expression": "error",
    "security/detect-new-buffer": "error",
    "security/detect-non-literal-fs-filename": "error",
    "security/detect-non-literal-require": "error",
    "security/detect-non-literal-regexp": "error",
    "security/detect-pseudoRandomBytes": "error",
    "security/detect-unsafe-regex": "error",
    
    // Disable rules that conflict with Svelte
    "security/detect-html-in-js": "off",
    "security/detect-tempfile": "off",
  },
  ignorePatterns: [
    "node_modules/",
    "build/",
    "dist/",
    "*.d.ts",
    "vite.config.ts",
    "svelte.config.js",
  ],
};
