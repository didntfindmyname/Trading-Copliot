import js from "@eslint/js";
import tsParser from "@typescript-eslint/parser";
import tsPlugin from "@typescript-eslint/eslint-plugin";

const browserGlobals = {
  console: "readonly",
  document: "readonly",
  fetch: "readonly",
  File: "readonly",
  FormData: "readonly",
  importMeta: "readonly",
  localStorage: "readonly",
  RequestInit: "readonly",
  window: "readonly"
};

export default [
  {
    ignores: ["dist/**", "node_modules/**"]
  },
  js.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
        ecmaVersion: "latest",
        sourceType: "module"
      },
      globals: browserGlobals
    },
    plugins: {
      "@typescript-eslint": tsPlugin
    },
    rules: {
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }]
    }
  }
];
