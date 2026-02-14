# BigBang Templates

This directory contains parameterized templates for bootstrapping new projects.

## Structure

```
templates/
├── copilot-instructions/    # Coding rules and best practices
│   ├── base.md             # Universal, domain-agnostic rules
│   ├── python.md           # Python-specific overlay
│   └── typescript.md       # TypeScript-specific overlay
└── prompts/                 # Agent workflow templates
    ├── _implement.prompt.md    # Implementation workflow
    ├── _commit.prompt.md       # Commit & PR workflow
    ├── _coverage.prompt.md     # Test coverage workflow
    ├── _maintenance.prompt.md  # Maintenance workflow
    ├── _system.prompt.md       # Utility/prompt commits
    └── _update.prompt.md       # Dependency updates
```

## Template Placeholders

All templates use `{{project_name}}` placeholders that will be replaced during project seeding (Phase 03):

```yaml
# Template form (in BigBang repository)
name: {{project_name}}_implement

# Rendered form (in target project)
name: pulsar_implement
```

## Usage

These templates are **not** meant to be used directly. They will be processed by the `bigbang-seed` CLI tool (to be implemented in Phase 03) which will:

1. Read the target project's configuration
2. Replace `{{project_name}}` with the actual project name
3. Write the rendered files to the target project's `.github/` directory

## Domain Overlays

For copilot-instructions, projects select a base + optional domain overlay:

- **All projects:** Include `base.md`
- **Python projects:** Include `base.md` + `python.md`
- **TypeScript projects:** Include `base.md` + `typescript.md`
- **Multi-language projects:** Include `base.md` + all relevant overlays

The seeding tool will concatenate the base with selected overlays during project initialization.

## Validation Errors

If you see compilation errors like "The 'name' attribute must be a string" on these template files, this is **expected**. The templates contain placeholders that are not valid YAML/Markdown until rendered. These errors will disappear once the templates are processed by the seeding CLI.

## Next Steps

See [doc/planning/03-project-initialization.md](../doc/planning/03-project-initialization.md) for the seeding CLI implementation plan.
