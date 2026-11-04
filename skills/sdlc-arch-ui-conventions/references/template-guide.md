# Template guide — sdlc-arch-ui-conventions

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/ui-conventions.md.tmpl`

### Framework & component structure

The frontend stack (e.g. React + Vite + Alpine) and how components are organized. Mirror the
source-tree convention: components grouped by module/feature.

### Design tokens (minimal starter)

Start small; expand as needed. The point is that stories use THESE, not one-off values.

### Spacing scale

e.g. 4 / 8 / 12 / 16 / 24 / 32 px

### Typography

font family, base size, heading scale

### State & data-loading pattern

Where state lives (component-local vs a shared store) and how API data is fetched/loaded.
One approach for the whole app so every UI story follows it.

### Responsive

Breakpoints to support and the layout approach (mobile-first, grid, etc.).

### Patterns (grows over time)

sdlc-deliver-docs-sync promotes reusable patterns here as UI stories establish them: common components
(cards, modals, forms), form-validation display, toast/notification, table conventions, etc.
Starts mostly empty; fills in as the product is built.
