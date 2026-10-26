# Severity rubric

Severity is **impact × reach**. Priority (when to fix) is a product call and may differ; this
skill records severity only.

| Severity | Impact | Reach | Examples |
|----------|--------|-------|----------|
| **S1 Critical** | Data loss or corruption, security exposure, or the product is unusable | Any | Uploaded materials of one course visible to another tenant; login fails for everyone; a migration drops a column |
| **S2 Major** | A core flow is broken with no reasonable workaround | Many users or a whole role | Instructors cannot upload any PDF; quiz submissions are lost on timeout |
| **S3 Minor** | A flow is broken but a workaround exists, or a secondary flow is broken | Some users or specific input | Files with an uppercase extension are rejected (rename works); sorting ignores accents |
| **S4 Trivial** | Cosmetic, wording, or layout only; no behaviour wrong | Any | Misaligned button; typo in an error message that is not asserted anywhere |

## Rules
- **Security or data integrity is S1** regardless of reach. If you are unsure whether data is
  exposed, assume it is and say so in the justification.
- **A workaround lowers severity by one level at most**, and only if a typical user would find it.
- **Reach is the affected population, not the number of reports.** One report of a bug every
  instructor hits is still S2.
- **Do not inflate for tone.** "URGENT!!!" in the report is not evidence.
- Write the justification as `<impact>; <reach>; <workaround or none>`.
