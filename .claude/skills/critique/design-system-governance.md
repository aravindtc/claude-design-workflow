# Design System Governance Agent

Keep the design system coherent as new sections, screens, components, and visual treatments are produced. The system is allowed to **evolve**, but never **drift randomly**.

This skill behaves like an agentic governance process: scan → detect → decide → propose → ask → only then update.

---

## WHEN TO RUN

Run this scan after any of the following:

- a new major **section** is created
- a new **screen** is created
- a new **component family** is introduced
- a **style change** is introduced from inspiration
- any **new visual treatment** is added
- **before final Figma completion**
- **before code generation**

Do not skip. The router enforces this.

---

## WHAT TO CHECK

Compare the new design work against the **current design system** (tokens, styles, components, layout rules, responsive rules).

### 1. Token drift
- new colors introduced outside the palette
- inconsistent spacing values (one-off pixel/rem values)
- new radius values
- unapproved shadows/effects
- raw values used instead of variables

### 2. Typography drift
- inconsistent heading sizes
- unclear text hierarchy
- one-off font treatments
- typography not mapped to defined text styles

### 3. Component drift
- repeated elements not using components
- similar components with different styling
- duplicate button/card/input patterns
- variants created as separate components instead of properties

### 4. Layout drift
- inconsistent grid usage
- inconsistent section spacing
- broken rhythm between sections
- auto layout not used where appropriate

### 5. Style drift
- section feels visually disconnected from the rest of the page
- inspiration influence is too strong in one area
- visual language changes without reason
- overly generic pattern introduced into a distinctive direction

### 6. Responsive drift
- section works on desktop but does not adapt cleanly
- mobile/tablet behavior is unclear
- hierarchy collapses at smaller sizes

---

## DECISION LOGIC

For every detected issue, classify it into exactly one of:

**A. Reuse existing design system**
- the new element is unnecessary variation
- an existing token/component/style already fits
- the difference creates inconsistency without adding meaning

**B. Update existing component**
- the new use case is valid
- it should become a component variant
- an existing component needs a more flexible state or property

**C. Add new design system token/component**
- the new element is genuinely useful
- it supports the approved creative direction
- it is likely to be reused
- it fills a real system gap

**D. Reject / simplify**
- the element only exists because of inspiration drift
- it weakens hierarchy
- it creates visual noise
- it is too one-off to systematize

**E. Defer decision**
- more sections are needed before deciding
- the pattern may or may not repeat
- user input is needed later

---

## USER APPROVAL RULE

**Do NOT update the design system automatically.**

For each suggested change, present:
- issue detected
- affected section/component
- recommendation
- reason
- impact if accepted
- risk if rejected
- suggested action

Then ask the user to choose one of:

1. Apply existing system
2. Update component
3. Add new token/component
4. Reject/simplify
5. Decide later

Only **after explicit user approval**:
- update Figma variables/styles/components
- update design system documentation/state
- update affected design sections

If the user has not chosen, **do not write to Figma** and **do not modify the design system state**.

---

## OUTPUT FORMAT

Always emit results in this exact structure:

```
# Design System Governance Scan

## Summary
- Issues found:
- Severity: low / medium / high
- Overall coherence status:

## Findings

### Finding 1
- Type: token / typography / component / layout / style / responsive
- Location:
- Problem:
- Recommendation:
- Reason:
- Impact if accepted:
- Risk if rejected:
- Suggested action:

(repeat per finding)

## Recommended Updates
- token updates:
- component updates:
- typography/style updates:
- layout rules:
- responsive rules:

## User Approval Required
Ask the user which recommendations to apply (per finding, by number).
```

---

## IMPORTANT BEHAVIOR

The governance agent must **not over-normalize**.

It must preserve:
- approved creative direction
- visual character
- deliberate expressive choices
- section-level contrast and rhythm

It should prevent:
- accidental inconsistency
- duplicate components
- token drift
- spacing drift
- random style changes
- Figma files becoming messy

**Rule:** Consistency should support clarity, not kill character.

When in doubt between coherence and character, flag it as a finding and let the user decide — do not silently normalize away an expressive choice.

---

## EXECUTION GUARD

- This skill is a **checkpoint**, not a rewrite pass.
- It must run before final Figma completion and before code generation.
- No design system mutation may occur without an explicit user approval message naming the finding number(s) to apply.
