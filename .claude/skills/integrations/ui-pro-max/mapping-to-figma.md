# Mapping to Figma

Convert normalized system + HTML structure into Figma-ready output.

## Layout
- use auto layout for all containers
- preserve hierarchy from HTML structure
- avoid absolute positioning unless strictly necessary

## Tokens
- replace raw values with semantic tokens
- connect to design-system variables
- ensure consistent usage across components

## Components
Identify repeated structures and convert them into:
- buttons
- cards
- inputs
- navigation elements

Create:
- reusable components
- variants where applicable

## Spacing
- use consistent spacing scale
- do not introduce arbitrary spacing values
- maintain visual rhythm

## Typography
- map roles (heading, body, label) to consistent styles
- ensure readability and hierarchy

## Validation
Before completion:
- check consistency of tokens
- check spacing alignment
- check hierarchy clarity
- ensure components are reusable

## Rules
- do not duplicate components unnecessarily
- do not mix raw values with tokens
- prioritize system consistency over visual novelty

## Strict token enforcement

- do not allow raw hex values in final output
- all colors must map to semantic tokens
- all spacing must map to spacing tokens
- all radius values must map to radius tokens

If a raw value appears:
→ convert it into a token or reference an existing one
