# Learnings

- Planning documents should follow a consistent numbered convention (00-overview, 01-phase1, etc.) with standard sections: Objective, Implementation Details, Tests Required, Acceptance Criteria, Dependencies, Risk Assessment.
- Each planning document should include a model recommendation (Haiku/Sonnet/Opus) and extended thinking flag to guide the implementing agent.
- The Pulsar project's `doc/planning/` structure serves as the reference format for BigBang planning documents.
- Automated audit scripts: Shell scripts with clear output formatting (Unicode box-drawing characters) provide better UX than plain text listings.
- Subagent delegation for classification tasks: Large-scale content classification (660+ learning entries) is more efficient when delegated to a subagent with clear output format requirements.
- Template parameterization validation: Template files with `{{placeholder}}` syntax will trigger validation errors in IDEs; document this in README.md to clarify they're intentional.
- Conservative deduplication: For learning consolidation, prefer false negatives (missing a duplicate) over false positives (rejecting unique insights).
- Domain-specific overlays pattern: Separating base rules from domain-specific rules (Python, TypeScript) creates cleaner templates and easier maintenance.
- Audit-first consolidation: Running an automated audit before consolidation provides clear metrics and helps prioritize which artifacts to merge first.
