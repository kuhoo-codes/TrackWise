import js from "@eslint/js";
import globals from "globals";
import reactRecommended from "eslint-plugin-react/configs/recommended.js";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";
import eslintPluginImport from "eslint-plugin-import";

/** @type {import("eslint").FlatConfig[]} */
export default [
  {
    ignores: [
      "**/dist/**",
      "**/node_modules/**",
      "**/build/**",
      "vite.config.ts",
      "src/components",
    ],
  },
  {
    settings: {
      react: {
        version: "detect",
      },
      "import/resolver": {
        typescript: {},
        node: true,
      },
    },
  },
  js.configs.recommended,
  reactRecommended,
  ...tseslint.configs.recommended,
  ...tseslint.configs.stylistic,
  prettier,
  {
    files: ["**/*.ts", "**/*.tsx"],
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      import: eslintPluginImport,
    },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parser: tseslint.parser,
      parserOptions: {
        project: "./tsconfig.json",
        tsconfigRootDir: import.meta.dirname,
        ecmaFeatures: {
          jsx: true,
        },
      },
    },

    rules: {
      // React rules
      "react/no-unescaped-entities": "off",
      "react/prop-types": "off",
      "react/jsx-uses-react": "error",
      "react/jsx-uses-vars": "error",
      "react/react-in-jsx-scope": "off",
      "react/jsx-filename-extension": ["error", { extensions: [".tsx"] }],
      "react/jsx-curly-brace-presence": [
        "error",
        { props: "never", children: "never" },
      ],
      "react/self-closing-comp": ["error", { component: true, html: true }],
      "react/jsx-boolean-value": ["error", "never"],

      // React Hooks rules
      ...reactHooks.configs.recommended.rules,
      "react-hooks/exhaustive-deps": "warn",

      // React Refresh rules
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],

      // Import rules
      "import/no-default-export": "error",
      "import/order": [
        "error",
        {
          groups: [
            "builtin",
            "external",
            "internal",
            "parent",
            "sibling",
            "index",
          ],
          alphabetize: { order: "asc", caseInsensitive: true },
        },
      ],

      // TypeScript rules
      "@typescript-eslint/explicit-function-return-type": [
        "error",
        {
          allowExpressions: true,
          allowHigherOrderFunctions: true,
          allowConciseArrowFunctionExpressionsStartingWithVoid: true,
          allowFunctionsWithoutTypeParameters: true,
        },
      ],
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/ban-ts-comment": [
        "error",
        { "ts-expect-error": "allow-with-description" },
      ],
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { prefer: "type-imports", fixStyle: "inline-type-imports" },
      ],
      "@typescript-eslint/consistent-type-definitions": ["error", "interface"],
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/await-thenable": "error",
      "@typescript-eslint/no-misused-promises": "error",
      "@typescript-eslint/promise-function-async": "error",

      // Naming conventions
      "@typescript-eslint/naming-convention": [
        "error",
        {
          selector: "default",
          format: ["camelCase"],
          leadingUnderscore: "allow",
          filter: {
            regex: "^(--.*|Content-Type|Accept|Authorization|X-.*)$",
            match: false,
          },
        },
        {
          selector: ["objectLiteralProperty", "typeProperty"],
          format: ["camelCase", "UPPER_CASE"],
          leadingUnderscore: "allow",
          filter: {
            regex: "^(--.*|Content-Type|Accept|Authorization|X-.*)$",
            match: false,
          },
        },
        {
          selector: "function",
          format: ["camelCase", "PascalCase"],
        },
        {
          selector: "import",
          format: ["PascalCase"],
        },
        {
          selector: "variable",
          format: ["camelCase", "UPPER_CASE", "PascalCase"],
          leadingUnderscore: "allow",
        },
        {
          selector: "typeLike",
          format: ["PascalCase"],
        },
        {
          selector: "enumMember",
          format: ["UPPER_CASE"],
        },
      ],

      // General JavaScript rules
      "no-console": ["error", { allow: ["warn", "error"] }],
      "no-debugger": "error",
      eqeqeq: ["error", "always"],
      curly: ["error", "multi-line", "consistent"],
      "arrow-body-style": ["error", "as-needed"],
      "prefer-const": "error",
      "no-var": "error",
      "object-shorthand": ["error", "always"],
      "quote-props": ["error", "consistent-as-needed"],
    },
  },
  {
    files: ["**/*.tsx", "**/*.ts"],
    rules: {
      "import/no-default-export": "off",
      "react/jsx-filename-extension": [
        "error",
        { extensions: [".tsx", ".ts"] },
      ],
    },
  },
  {
    files: [
      "src/services/apiTypes.ts",
      "src/services/adapters.ts",
      "src/features/timeline/components/types.ts",
    ],
    rules: {
      "@typescript-eslint/naming-convention": [
        "error",
        {
          selector: "default",
          format: ["camelCase"],
        },
        {
          selector: ["objectLiteralProperty", "typeProperty"],
          format: ["camelCase", "snake_case"],
        },
        {
          selector: "typeLike",
          format: ["PascalCase"],
        },
      ],
    },
  },
];
