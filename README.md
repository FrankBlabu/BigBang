# BigBang

Meta repository as a starter for agent based coding projects

## Overview

BigBang is a template management system that helps maintain consistency across multiple coding projects by providing:

- Canonical templates for prompts, copilot instructions, and learnings
- Tools to seed new projects with best practices
- Tools to propagate updates from BigBang to existing projects
- Domain-specific overlays (Python, TypeScript, C++, DevOps)

## Setup

### Prerequisites

- Python 3.12 or higher
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/FrankBlabu/Pulsar.git BigBang
   cd BigBang
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Tools

### Push Tool

Forward-propagate BigBang improvements to previously seeded projects.

#### Usage

```bash
.venv/bin/python scripts/push.py [OPTIONS] TARGET_PATH
```

#### Options

- `--dry-run` - Preview what would be updated without writing files
- `--force` - Overwrite locally modified files without confirmation
- `--skip-modified` - Skip files that have local modifications
- `--learnings-only` - Only push new learnings, skip other artifacts

#### Examples

Preview updates:
```bash
.venv/bin/python scripts/push.py --dry-run /path/to/project
```

Push updates (interactive):
```bash
.venv/bin/python scripts/push.py /path/to/project
```

Force update all files:
```bash
.venv/bin/python scripts/push.py --force /path/to/project
```

## Testing

Run the test suite:

```bash
.venv/bin/python -m pytest tests/ -v
```

## Project Structure

```
BigBang/
├── .github/              # GitHub configuration
│   └── prompts/          # Prompt templates for BigBang itself
├── doc/                  # Documentation
│   └── planning/         # Planning documents
├── learnings/            # Domain-specific learnings
│   ├── LEARNINGS.python.md
│   ├── LEARNINGS.typescript.md
│   └── ...
├── schemas/              # JSON schemas
├── scripts/              # Tools and utilities
│   ├── push.py          # Forward-propagation tool
│   └── audit.sh         # Audit script
├── templates/            # Canonical templates
│   ├── copilot-instructions/
│   │   ├── base.md
│   │   ├── python.md
│   │   └── ...
│   └── prompts/
│       ├── _implement.prompt.md
│       ├── _commit.prompt.md
│       └── ...
├── tests/                # Test suite
├── LEARNINGS.md          # General learnings
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## Contributing

See the planning documents in [doc/planning/](doc/planning/) for implementation details and roadmap.

## License

See [LICENSE](LICENSE) file for details.

