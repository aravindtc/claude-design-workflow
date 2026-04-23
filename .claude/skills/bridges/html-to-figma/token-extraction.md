# Token extraction

When system mode is enabled:

- extract repeated values
- convert to tokens

Example:
- multiple bg-gray-900 → color.background.primary
- repeated p-4 → spacing.md
- repeated rounded-xl → radius.l

Avoid:
- creating tokens for one-off values
