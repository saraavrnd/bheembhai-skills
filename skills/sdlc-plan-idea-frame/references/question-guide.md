# Question guide — what makes a question Blocking

A question is **Blocking** when two reasonable answers would give two differently shaped PRDs.
The shape of a PRD is its users, its feature areas, its MVP boundary, its hard NFRs and the
lifecycle of its core entities. Everything else is **Non-blocking**: the PRD can carry it as an
assumption or an open question and still decompose cleanly.

## Blocking — ask these

| Category | Example | Why it changes the shape |
|----------|---------|--------------------------|
| Who the users are | "Is this for teachers, students, or both?" | Each user type brings its own feature area and permissions |
| MVP boundary | "Must the first release include payments, or is it free-only?" | Moves a whole feature area between MVP and Later |
| Hard constraint | "Will it handle data about children under 13?" | Adds compliance NFRs (COPPA) and consent flows |
| Platform | "Web, mobile, or both at launch?" | Doubles or halves the client-side requirements |
| Core lifecycle | "Do users sign up themselves, or does an admin provision them?" | Decides which requirement creates the main actor |
| Build vs integrate | "Do we own identity, or use the customer's SSO?" | Swaps a feature area for an integration |

## Non-blocking — default them

| Example | Typical default |
|---------|-----------------|
| "What should the success metric target be?" | A conservative, measurable target marked as an assumption |
| "Which file types should upload accept?" | The common set for the domain, listed in the PRD |
| "Should there be dark mode?" | Later |
| "How many users at launch?" | An order-of-magnitude estimate, revisited in arch-design |

## Writing the proposed default

- Pick the answer that keeps the MVP smallest while still testing the value hypothesis.
- Say it as a decision, not a range: "Students and teachers; district admins are Later."
- If no default is defensible (the input describes two incompatible products), that is not a
  question: the idea needs framing, and the step escalates.
