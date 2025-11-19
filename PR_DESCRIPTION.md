## Description
This PR enhances the API response format and modularizes the codebase for better maintainability and web visualization support.

## Changes Made
- **Enhanced API Response**: Modified `/simulate` endpoint to return structured JSON optimized for web visualization instead of raw stdout
- **Code Modularization**: Refactored codebase into separate modules:
  - `app.py` - Flask routes and endpoints only
  - `config.py` - Configuration, binary path management, and error handling
  - `utils.py` - Utility functions for command building and file operations
  - `parser.py` - Parsing logic to convert stdout into structured JSON
- **Response Enhancements**: Added visualization-friendly fields:
  - Parsed match ranges with start/end positions
  - Coverage metrics per sequence
  - Summary statistics (total sequences, matches, states visited, average coverage)
  - Structured sequence data with match counts and flags
- **Documentation**: Updated README.md to reflect new project structure and API response format

## Type of Change
- [x] New feature (non-breaking change which adds functionality)
- [x] Code refactoring
- [x] Documentation update

## Testing
- [x] Manual testing completed
- [x] Verified API responses return structured JSON
- [x] Confirmed all modules import correctly
- [x] Tested with sample patterns and sequences

## Checklist
- [x] Code follows the project's style guidelines
- [x] Self-review completed
- [x] Comments added for complex code
- [x] Documentation updated
- [x] No new warnings generated
- [x] Changes tested locally

## API Response Example
The response now includes structured data like:
```json
{
  "pattern": "A(CG|TT)*",
  "automaton_mode": "DFA",
  "sequences": [
    {
      "sequence_number": 1,
      "matches": ["[0,1)", "[0,3)", ...],
      "match_ranges": [
        {"range": "[0,1)", "start": 0, "end": 1, "length": 1},
        ...
      ],
      "coverage": 0.5,
      "match_count": 6,
      ...
    }
  ],
  "total_sequences": 1,
  "average_coverage": 0.5,
  ...
}
```

## Additional Notes
- The parser automatically sorts match ranges by start position for easier visualization
- Coverage metrics are calculated automatically based on match positions
- All existing functionality is preserved, only the response format has changed

