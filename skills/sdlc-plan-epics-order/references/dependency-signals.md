# Cross-epic dependency signals

An edge A → B means **B cannot be built or tested without A**. Use the strongest signal
available, and record it.

| Source | What it looks like | Confidence |
|--------|--------------------|------------|
| `link` | An existing Jira "A blocks B" link between published epics | firm |
| `prd` | A requirement in B names an output a requirement in A creates ("FR-012: the dashboard shows each student's session history" and FR-001 creates the sessions) | firm |
| `epic-body` | B's "Implementation guidance / dependency order" names A or its output | provisional |
| `lifecycle` | B uses an actor, entity or stored state that only A creates (accounts, rosters, uploaded content) | provisional |

## Counts as an edge
- B reads or updates data that A introduces.
- B's users or roles are created or imported by A.
- B calls an interface (API, event, job) that A builds.
- B's acceptance can only be tested end to end once A exists.

## Does not count as an edge
- Shared platform every epic touches lightly (logging, CI) — unless an epic owns that platform
  and others cannot run without it, in which case it is a real wave-1 epic.
- "It would be nicer to do A first" with nothing in B that uses A.
- Cross-cutting NFR epics (security, privacy) that *constrain* others: the constraint is an
  acceptance criterion in each epic, not a build dependency. Add an edge only if B needs a
  mechanism A builds (an audit log, a consent store).

## Cycles
A cycle (A needs B, B needs A) almost always means one capability was split across two epics.
Recommend the re-slice: move the shared piece into one of them, or into a new small epic both
depend on. Never break a cycle by dropping an edge.
