# Ambiguity Handling

How to handle unclear or incomplete requests before executing design work.

## When to ask a clarifying question

Ask before proceeding if:
- The design type is genuinely unclear from both frame dimensions and user language
- The user's intent is ambiguous (e.g., "make it better" — better how?)
- Multiple valid interpretations exist and they lead to very different outputs
- The user hasn't specified a frame and nothing is selected

## When NOT to ask

Do not ask if:
- The frame and context make the design type obvious
- The request is clear enough to begin (inspect first, then proceed)
- The ambiguity can be resolved by inspecting the frame

Prefer to inspect the frame and infer intent rather than asking. Only ask when inspection is insufficient.

## How to ask

Ask one question only. Make it specific.

Bad: "Can you tell me more about what you're looking for?"
Good: "Is this a social media post or a landing page section? The frame is 1080×1080 but the content looks promotional."

Bad: "What kind of variations do you want?"
Good: "Should I explore layout changes, color changes, or both?"

## Incomplete brief handling

If the user provides a brief but it is missing key information:

| Missing | How to handle |
|---|---|
| Platform/format | Infer from frame dimensions. If unclear, ask. |
| Number of variations | Default to 2 strong variations |
| Placement direction | Default to right of source |
| Color direction | Preserve existing color logic, explore one alternative |
| Specific style request | Use judgment from the source frame's existing tone |

## Conflict resolution

If the user's instruction would produce a worse result (e.g., "add more elements" to an already crowded frame):
- Do not follow the instruction literally
- Adapt it intelligently: "Adding elements would crowd this frame — I'll reorganize the existing ones to create the emphasis you're describing instead."
- State the adaptation clearly before executing

## Flagging issues before execution

If inspection reveals a problem that will affect the quality of variations (e.g., the source frame is already broken — overlapping elements, clipped text), flag it:
- Note what is broken in the source
- Ask whether to fix the source first or proceed with variations based on the broken state
- Default: proceed with variations while cleaning up the source issues in the clones
