# SelectLineFromDropdown Node

A ComfyUI node for selecting and processing lines from text files.

## Features

- Select lines from text files in various modes:
  - **manual**: Select a specific line by index
  - **random**: Select a random line based on a seed
  - **increment**: Start from a line and increment with each batch
  - **decrement**: Start from a line and decrement with each batch
  - **custom_seq**: Iterate through a custom sequence of line indices
  - **custom_random**: Randomly select from a custom set of line indices

## Custom Indices Format

The `custom_indices` parameter accepts a string of comma-separated indices and/or ranges:

- Individual indices: `"1,5,9,15"`
- Ranges: `"5-10"` (includes 5 through 10)
- Mixed: `"1,3,5-8,10,15-20"`

Examples:

1. To use specific lines from a text file: `"12,18,78,91"`
2. To use a range of lines: `"5-10,15-20"`
3. To combine individual lines and ranges: `"1,3,5-10,15,20-25"`

## Usage Examples

### Custom Sequence Mode

Set `mode` to "custom_seq" and provide a comma-separated list of indices in the `custom_indices` field:

```
12,18,78,91
```

This will iterate through these line indices in order with each batch.

### Custom Random Mode

Set `mode` to "custom_random" and provide a comma-separated list of indices in the `custom_indices` field:

```
12,18,78,91
```

This will randomly select one of these line indices for each batch, using the seed value for consistent randomization.

### Using Ranges

You can also specify ranges for more convenient selection of larger sets of lines:

```
12-20,30-40,50,52,54
```

This will include all lines from 12-20, 30-40, plus lines 50, 52, and 54.
