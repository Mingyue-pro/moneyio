// @ts-check
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended';
import pluginVue from 'eslint-plugin-vue';
import vueParser from 'vue-eslint-parser';

/**
 * ESLint configuration for TypeScript + Vue projects
 */
export default tseslint.config(
  {
    ignores: ['src/api/auth.js'],
  },

  // Extend recommended configs
  eslint.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  ...pluginVue.configs['flat/recommended'],
  eslintPluginPrettierRecommended,

  {
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
        extraFileExtensions: ['.vue'],
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        self: 'readonly',
        global: 'readonly',
        localStorage: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
      },
    },

    rules: {
      // ==========================================
      // TYPE SAFETY RULES [MUST]
      // ==========================================

      // Disallow 'any' - use 'unknown' instead
      '@typescript-eslint/no-explicit-any': 'error',

      // Disallow non-null assertions (!)
      '@typescript-eslint/no-non-null-assertion': 'error',

      // Disallow triple-slash references
      '@typescript-eslint/triple-slash-reference': 'error',

      // No floating promises - always await
      '@typescript-eslint/no-floating-promises': 'error',

      // No misused promises in conditionals
      '@typescript-eslint/no-misused-promises': 'error',

      // ==========================================
      // NAMING CONVENTIONS [MUST]
      // ==========================================

      '@typescript-eslint/naming-convention': [
        'error',
        // Classes, interfaces, types, enums: PascalCase
        {
          selector: ['class', 'interface', 'typeAlias', 'enum'],
          format: ['PascalCase'],
        },
        // Variables, functions, parameters, properties: camelCase
        {
          selector: ['variable', 'function', 'parameter'],
          format: ['camelCase'],
          leadingUnderscore: 'allow',
        },
        // Allow object/type property names that are not camelCase
        {
          selector: ['property', 'objectLiteralProperty', 'typeProperty'],
          format: null,
        },
        // Global constants: UPPER_CASE
        {
          selector: 'variable',
          modifiers: ['const', 'global'],
          format: ['UPPER_CASE', 'camelCase'], // Allow both for flexibility
        },
        // Enum members: UPPER_CASE
        {
          selector: 'enumMember',
          format: ['UPPER_CASE'],
        },
      ],

      // ==========================================
      // CODE PATTERNS [SHOULD]
      // ==========================================

      // Prefer interface over type for object definitions
      '@typescript-eslint/consistent-type-definitions': ['warn', 'interface'],

      // Avoid empty interfaces
      '@typescript-eslint/no-empty-interface': 'warn',

      // Require explicit return types on exported functions
      '@typescript-eslint/explicit-module-boundary-types': [
        'warn',
        {
          allowArgumentsExplicitlyTypedAsAny: false,
        },
      ],

      // Avoid redundant type annotations
      '@typescript-eslint/no-inferrable-types': 'warn',

      // ==========================================
      // IMPORT MANAGEMENT [MUST/SHOULD]
      // ==========================================

      // No unused variables or imports
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],

      // ==========================================
      // ASYNC/AWAIT PATTERNS [MUST]
      // ==========================================

      // Require await in async functions
      '@typescript-eslint/require-await': 'warn',

      // Prefer async/await over promise chains
      '@typescript-eslint/promise-function-async': 'warn',

      // ==========================================
      // GENERAL CODE QUALITY
      // ==========================================

      // Consistent type imports
      '@typescript-eslint/consistent-type-imports': [
        'warn',
        {
          prefer: 'type-imports',
          fixStyle: 'separate-type-imports',
        },
      ],

      // Array type syntax consistency
      '@typescript-eslint/array-type': [
        'warn',
        {
          default: 'array-simple',
        },
      ],
    },
  },

  {
    // Disable type-checked rules for JS files
    files: ['**/*.js'],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    ...tseslint.configs.disableTypeChecked,
    rules: {
      '@typescript-eslint/explicit-module-boundary-types': 'off',
    },
  },

  {
    // The type-checked unsafe-* rules produce false positives in Vue SFC files
    // because ESLint's projectService cannot always fully resolve Pinia store
    // return types across the <script setup> boundary. TypeScript's own compiler
    // already enforces these constraints, so disabling here avoids noise.
    files: ['**/*.vue'],
    rules: {
      '@typescript-eslint/no-unsafe-assignment': 'off',
      '@typescript-eslint/no-unsafe-call': 'off',
      '@typescript-eslint/no-unsafe-member-access': 'off',
      '@typescript-eslint/no-unsafe-return': 'off',
      '@typescript-eslint/no-unsafe-argument': 'off',
      // In Vue <script setup>, variables and functions defined in script are used
      // in the template, but ESLint cannot detect this usage. Disable this rule
      // for Vue files and rely on TypeScript compiler checking.
      '@typescript-eslint/no-unused-vars': 'off',
    },
  },

  {
    // Configuration files can be more lenient
    files: ['*.config.{js,ts,mjs,cjs}'],
    rules: {
      '@typescript-eslint/no-unused-vars': 'off',
    },
  },
);
