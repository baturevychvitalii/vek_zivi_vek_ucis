# Layer Responsibilities

The system has distinct layers. Each layer has a single responsibility and a direction
of dependency — upper layers know about lower layers, never the reverse.

- **Domain packages (groves)** — carry their own rules and behavior; the system reads
  from them. Trajectory: groves graduate toward independently-versioned, distributable
  knowledge packages; they rely on infrastructure without referencing it (see
  `product-vision.md`)
- **Stdlib (skills)** — generic operations, parameterized by node context files
- **Enforcement layer (hooks)** — enforce contracts at write time; independent of content
- **Constitution (meta/)** — design record and governance; referenced, never modified lightly

Two structures sit alongside the stack rather than inside it:
- **Shared primitives (`.claude/utils/`)** — consumed across hooks, scripts; no directional dependency
- **Integration boundary (`plugins/anki-mcp/`)** — exposes external systems as native tools; maintained as an independently-versioned submodule packaged as a plugin

Collapsing layers for convenience is always a short-term gain and a long-term cost.
