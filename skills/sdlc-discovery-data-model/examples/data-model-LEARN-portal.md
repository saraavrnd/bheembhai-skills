<!-- Worked example: data-model for Learn Portal (fastapi pack). Sourced from the real migration + model. -->
```yaml
artifact: data-model
service: learn-portal
generated: 2026-10-01
stack_pack: fastapi
summary: >
  The academic_year table (school_admin module) is defined by migration 0005 and the AcademicYear
  ORM model; the two agree. One unique constraint (school_id, year_label) enforces one label per
  school. Coverage here is the school_admin slice; other modules mapped in their own passes.
entities:
  - name: academic_year
    columns:
      - { name: id, type: str, nullable: false, note: "PK" }
      - { name: school_id, type: str, nullable: false, note: "part of unique(school_id, year_label)" }
      - { name: year_label, type: str, nullable: false, note: "part of unique(school_id, year_label)" }
      - { name: is_current, type: bool, nullable: false, note: "default false; exactly one true per school" }
    confidence: observed
    source: "migrations/versions/0005_academic_year_table.py"
    note: "ORM model app/school_admin/models.py agrees — no drift"
relationships: []
coverage: { entities_found: 1, source_of_truth: "migrations/versions/", partial: true }
```
