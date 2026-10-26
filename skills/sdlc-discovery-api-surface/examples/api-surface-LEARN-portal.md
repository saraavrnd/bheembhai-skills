<!-- Worked example: api-surface for the Learn Portal backend (fastapi pack).
     Written to docs/discovery/learn-portal/api-surface.md. Sources are the real router lines. -->
```yaml
artifact: api-surface
service: learn-portal
generated: 2026-10-01
stack_pack: fastapi

summary: >
  Six endpoints in the school_admin module: three JSON API routes under /api/v1 and three
  cookie-auth web routes under /admin. JSON mutations are admin-only; the GET list is read-broader
  (admin+teacher). Web routes use cookie-based role auth. Coverage is complete for the
  school_admin router; other routers (auth) extracted separately.

endpoints:
  - method: GET
    path: "/api/v1/academic-years"
    handler: "list_academic_years"
    auth: "require_role(admin, teacher)"
    confidence: observed
    source: "app/school_admin/router.py:45"
    response_shape: "list[{id, year_label, is_current}]"
  - method: POST
    path: "/api/v1/academic-years"
    handler: "create_academic_year"
    auth: "require_role(admin)"
    confidence: observed
    source: "app/school_admin/router.py:52"
    response_shape: "201 / 409 on duplicate"
  - method: PUT
    path: "/api/v1/academic-years/{academic_year_id}/mark-current"
    handler: "mark_current"
    auth: "require_role(admin)"
    confidence: observed
    source: "app/school_admin/router.py:64"
    response_shape: "200 / 404"
  - method: GET
    path: "/admin/academic-years"
    handler: "admin_academic_years_page"
    auth: "require_role_cookie(admin)"
    confidence: observed
    source: "app/school_admin/router.py:106"
    response_shape: "HTML (Jinja2 template)"
  - method: POST
    path: "/admin/academic-years"
    handler: "admin_create_academic_year"
    auth: "require_role_cookie(admin), CSRF-checked"
    confidence: observed
    source: "app/school_admin/router.py:124"
    response_shape: "HTML inline re-render"
  - method: POST
    path: "/admin/academic-years/{academic_year_id}/mark-current"
    handler: "admin_mark_current"
    auth: "require_role_cookie(admin), CSRF-checked"
    confidence: observed
    source: "app/school_admin/router.py:150"
    response_shape: "HTML inline re-render"

coverage:
  routes_found: 6
  locations_searched: ["app/**/router.py"]
  partial: false
  note: "school_admin router fully mapped; app/auth/router.py mapped in its own pass"
```
