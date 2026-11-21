# Epic plan review checklist

Each category says what a real finding looks like, and what is not one. `verify.yaml` on
`sdlc-plan-epics-create` and `sdlc-plan-epics-order` already checks that every requirement lands
in exactly one epic, that the map, the fan-out block and the order agree, that each epic has its
sections, and that the order is acyclic with consistent waves; do not repeat those.

## 1. Boundaries and size (target: epics)
- **Finding:** an epic bundles two themes a team would plan separately; an epic holds so many
  requirements that one per-epic run would produce an unreviewable story set (about 15+); two
  tiny epics that cannot be planned or built apart.
- **Not a finding:** an epic that is large but one coherent theme.

## 2. Self-containment (target: epics)
- **Finding:** a person given only this epic's section (as in its own planning run) could not
  tell who the users are, what is in and out of scope, or what "done" means.
- **Proposed change:** the missing sentences, not a rewrite.

## 3. Lifecycle across epics (target: epics or order)
- **Finding:** an epic uses an actor, entity or state (accounts, a roster, an uploaded file)
  that no epic creates and the PRD does not mark external. Target `epics` if the creating scope
  is missing; `order` if it exists but the order does not reflect it.
- **Severity:** Blocking: the per-epic runs would each assume someone else builds it.

## 4. Requirement placement (target: epics)
- **Finding:** a requirement sits in an epic whose theme it does not belong to, so that epic's
  stories would cover it awkwardly and the right epic's stories would miss it.

## 5. Edges and waves (target: order)
- **Finding:** a missing edge (B clearly uses what A creates), an edge with no real dependency
  behind it, or a firm edge whose source does not say what it claims.
- **Not a finding:** a provisional edge that is plausible; it is labelled provisional for a reason.

## 6. MVP path (target: order or epics)
- **Finding:** an MVP epic that depends on a Later epic; an MVP path that leaves out an epic an
  MVP epic needs.
- **Question:** usually a person's call (pull the Later scope into MVP, or drop the MVP need),
  with a proposed default.

## 7. Ready for a per-epic run (target: epics)
- **Finding:** an epic whose stories could not be written without decisions only the PRD's author
  can make (an unresolved choice between two flows). Raise it now, as a question, so it is not
  asked again in every epic's run.
