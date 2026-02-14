<!--
#
# typescript.md - TypeScript-specific coding rules for AI agents
#
# This file contains TypeScript/Node.js-specific best practices and requirements.
# It is used in combination with base.md for TypeScript projects.
#
-->

# TypeScript

- All code must use TypeScript with strict type checking enabled.
- Use TypeScript types and interfaces consistently throughout the codebase.
- Prefer interfaces over type aliases for object shapes.
- Use `unknown` instead of `any` when the type is not known.

## Testing

- Use a consistent testing framework (Jest, Mocha, or Vitest) for JavaScript/TypeScript projects.
- Ensure all tests are properly typed.

## Code Quality

- Use ESLint for linting TypeScript code.
- Use Prettier for code formatting.
- Configure TypeScript with `strict: true` in `tsconfig.json`.

## Module System

- Use ES modules (`import`/`export`) over CommonJS (`require`/`module.exports`).
- Organize imports: external dependencies first, then internal modules.
