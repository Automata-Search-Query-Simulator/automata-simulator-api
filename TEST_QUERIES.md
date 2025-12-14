# Test Queries for Automata Simulator API

This document provides comprehensive test queries for all automaton modes, including edge cases to thoroughly test the logic.

## Base URL

```
http://127.0.0.1:5000/simulate
```

## Input Methods

You can provide sequences in two ways:

1. **Inline sequences** (using `sequences` parameter): Pass sequences directly as query parameters

   ```bash
   curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&sequences=ACGT&sequences=TTTT"
   ```

2. **File input** (using `input_path` parameter): Provide path to a file containing sequences (one per line)
   ```bash
   curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&input_path=datasets/dna/sample.txt"
   ```

**Note**: If both `input_path` and `sequences` are provided, `input_path` takes precedence.

### Input File Format

When using `input_path`, the file should contain sequences separated by newlines:

```
ACGTACGTACGT
TTTTTTTT
ACGTACGTACGTACGT
```

Each line represents one sequence. Empty lines are ignored.

---

## Mode 1: NFA (Non-deterministic Finite Automaton)

NFA mode uses regex patterns to match sequences. It supports alternation (`|`), repetition (`*`, `+`, `?`), and grouping.

### Basic Tests

#### Test 1.1: Simple pattern match

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&sequences=ACGT"
```

**Expected**: Match at `[0,4)` in sequence "ACGT"

#### Test 1.2: Pattern with alternation

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=A(CG|TT)&sequences=ACGT&sequences=ATTT"
```

**Expected**:

- Sequence 1: Match at `[0,3)` for "ACG"
- Sequence 2: Match at `[0,3)` for "ATT"

#### Test 1.3: Pattern with Kleene star

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=A(CG)*&sequences=ACGCGCG"
```

**Expected**: Multiple matches including `[0,1)`, `[0,3)`, `[0,5)`, `[0,7)`

#### Test 1.4: Multiple sequences

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&sequences=ACGT&sequences=TTTT&sequences=ACGTACGT"
```

**Expected**:

- Sequence 1: 1 match at `[0,4)`
- Sequence 2: 0 matches
- Sequence 3: 2 matches at `[0,4)` and `[4,8)`

#### Test 1.4b: Using input_path instead of inline sequences

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&input_path=datasets/dna/sample.txt"
```

**Expected**: Same results as Test 1.4, but sequences are read from file

### Edge Cases

#### Test 1.5: Empty sequence

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&sequences="
```

**Expected**: Sequence with length 0, no matches

#### Test 1.6: Pattern matches entire sequence

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&sequences=ACGT"
```

**Expected**: Single match covering entire sequence `[0,4)`

#### Test 1.7: Pattern never matches

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=XXXX&sequences=ACGTACGT"
```

**Expected**: No matches, `has_matches: false`, `match_count: 0`

#### Test 1.8: Overlapping matches

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=A(CG|TT)*&sequences=ACGTACGTACGT"
```

**Expected**: Multiple overlapping matches at different positions

#### Test 1.9: Pattern with optional character

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=AC?GT&sequences=ACGT&sequences=AGT"
```

**Expected**: Both sequences should match

#### Test 1.10: Very long sequence

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&sequences=ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT"
```

**Expected**: Multiple matches throughout the sequence

---

## Mode 2: DFA (Deterministic Finite Automaton)

DFA mode is similar to NFA but uses deterministic automaton. Should produce same results but potentially different state visit counts.

### Basic Tests

#### Test 2.1: Simple pattern match

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=ACGT&sequences=ACGT"
```

**Expected**: Match at `[0,4)` in sequence "ACGT"

#### Test 2.2: Pattern with alternation

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=A(CG|TT)&sequences=ACGT&sequences=ATTT"
```

**Expected**:

- Sequence 1: Match at `[0,3)` for "ACG"
- Sequence 2: Match at `[0,3)` for "ATT"

#### Test 2.3: Pattern with repetition

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=(ACGT)+&sequences=ACGTACGT"
```

**Expected**: Matches at `[0,4)`, `[4,8)`, and `[0,8)` (the `+` quantifier matches individual occurrences and the combined sequence)

#### Test 2.4: Multiple sequences with different outcomes

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=ACGT&sequences=ACGT&sequences=TTTT&sequences=ACGTACGT"
```

**Expected**:

- Sequence 1: 1 match
- Sequence 2: 0 matches
- Sequence 3: 2 matches

### Edge Cases

#### Test 2.5: Empty pattern (if supported)

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=&sequences=ACGT"
```

**Expected**: Error or empty pattern handling

#### Test 2.6: Pattern matches at start and end

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=ACGT&sequences=ACGTACGTACGT"
```

**Expected**: Matches at `[0,4)`, `[4,8)`, `[8,12)`

#### Test 2.7: Single character pattern

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=A&sequences=AAAA"
```

**Expected**: Multiple matches, one for each 'A'

#### Test 2.8: Pattern with special regex characters

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=A.*GT&sequences=ACGT&sequences=ATTTGT"
```

**Expected**: Both sequences should match if `.*` is supported

#### Test 2.9: Sequence shorter than pattern

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=ACGTACGT&sequences=ACGT"
```

**Expected**: No matches

#### Test 2.10: Pattern equals sequence exactly

```bash
curl "http://127.0.0.1:5000/simulate?mode=dfa&pattern=ACGT&sequences=ACGT"
```

**Expected**: Single match covering entire sequence, `coverage: 1.0`

---

## Mode 3: EFA (Extended Finite Automaton)

EFA mode supports approximate matching with a mismatch budget (k). Use `mismatch_budget` parameter to allow k mismatches.

### Basic Tests

#### Test 3.1: Exact match (k=0)

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=0&sequences=ACGT"
```

**Expected**: Match at `[0,4)` with no mismatches

#### Test 3.2: One mismatch allowed (k=1)

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=1&sequences=ACCT"
```

**Expected**: Match at `[0,4)` with 1 mismatch (C instead of G)

#### Test 3.3: Two mismatches allowed (k=2)

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=2&sequences=ATTT"
```

**Expected**: Match at `[0,4)` with 2 mismatches

#### Test 3.4: Multiple occurrences with mismatches

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=1&sequences=ACCTACGTACCT"
```

**Expected**: Multiple matches where some have mismatches

### Edge Cases

#### Test 3.5: Mismatch budget larger than pattern length

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=10&sequences=TTTT"
```

**Expected**: Should match (allowing all characters to mismatch)

#### Test 3.6: Zero mismatch budget with no exact match

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=0&sequences=ACCT"
```

**Expected**: No matches

#### Test 3.7: Mismatch budget = 1, sequence has 1 mismatch

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=1&sequences=ACCT"
```

**Expected**: Match at `[0,4)`

#### Test 3.8: Mismatch budget = 1, sequence has 2 mismatches

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=1&sequences=ATTT"
```

**Expected**: No match (exceeds budget)

#### Test 3.9: Pattern longer than sequence

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGTACGT&mismatch_budget=2&sequences=ACGT"
```

**Expected**: No matches (pattern too long)

#### Test 3.10: Large mismatch budget with exact matches

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=5&sequences=ACGTACGTACGT"
```

**Expected**: Multiple matches, some exact, some with mismatches

---

## Mode 4: PDA (Pushdown Automaton)

PDA mode is used for structured sequences like RNA secondary structures. Supports two modes:
1. **Standard PDA**: Uses `allow_dot_bracket=true` for dot-bracket notation validation
2. **RNA Mode**: Uses `rna_mode=true` for RNA sequence validation with base pairing checks

### Basic Tests (Standard PDA)

#### Test 4.1: Simple balanced parentheses

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=()"
```

**Expected**: Match for balanced structure

#### Test 4.2: Nested parentheses

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=(())"
```

**Expected**: Match for nested structure

#### Test 4.3: Multiple sequences

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=()&sequences=(())&sequences=((..))"
```

**Expected**: All sequences should match if they're valid structures

#### Test 4.4: Sequence with unpaired bases

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=((..))"
```

**Expected**: Match with unpaired positions represented by dots

### RNA Mode Tests

PDA mode can validate RNA sequences with secondary structure using `rna_mode=true`. This validates Watson-Crick base pairing (A-U, G-C) and wobble pairs (G-U).

#### Test 4.12: RNA sequence with inline dot-bracket

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&rna_mode=true&sequences=CGUAGCUCUG&secondary_structures=(..((..)))"
```

**Expected**: Validates RNA sequence against secondary structure

**Response includes**:
```json
{
  "pda_sequences": [
    {
      "sequence": "CGUAGCUCUG",
      "dot_bracket": "(..((..)))",
      "result": "Valid",
      "checks": [
        "5th nucleotide G <-> 8th nucleotide C -> valid? [OK]",
        "4th nucleotide A <-> 9th nucleotide U -> valid? [OK]",
        "1th nucleotide C <-> 10th nucleotide G -> valid? [OK]",
        "Parentheses balanced? [OK]"
      ],
      "messages": []
    }
  ],
  "sequences": [{
    "rna_sequence": "CGUAGCUCUG",
    "dot_bracket": "(..((..)))",
    "rna_valid_bases": true,
    "rna_checks": [
      "5th nucleotide G <-> 8th nucleotide C -> valid? [OK]",
      "4th nucleotide A <-> 9th nucleotide U -> valid? [OK]",
      "1th nucleotide C <-> 10th nucleotide G -> valid? [OK]",
      "Parentheses balanced? [OK]"
    ],
    "rna_result": "Valid"
  }]
}
```

#### Test 4.13: Multiple RNA sequences with structures

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&rna_mode=true&sequences=CGUAGCUCUG&sequences=AAAUUUGGG&secondary_structures=(..((..)))&secondary_structures=(((...)))"
```

**Expected**: Validates each RNA sequence against its corresponding dot-bracket structure

#### Test 4.14: RNA with file input

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&rna_mode=true&input_path=datasets/rna/sequence.txt&secondary_structure_path=datasets/rna/sample.txt"
```

**Expected**: Reads sequences and structures from files, validates base pairing

#### Test 4.15: Invalid RNA bases

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&rna_mode=true&sequences=CGXAGCUCUG&secondary_structures=(..((..)))"
```

**Expected**: Returns validation error for invalid RNA bases (only A, U, C, G allowed)

#### Test 4.16: Invalid base pairing

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&rna_mode=true&sequences=CGUAGCUCUA&secondary_structures=(..((..)))"
```

**Expected**: Returns `rna_result: "Invalid"` if base pairs don't follow Watson-Crick or wobble pairing rules

### Edge Cases

#### Test 4.5: Unbalanced parentheses (too many opens)

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=((()"
```

**Expected**: No match or error (unbalanced structure)

#### Test 4.6: Unbalanced parentheses (too many closes)

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=()))"
```

**Expected**: No match or error (unbalanced structure)

#### Test 4.7: Empty sequence

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences="
```

**Expected**: Empty sequence handling

#### Test 4.8: Only dots (no pairs)

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=...."
```

**Expected**: Match (all unpaired)

#### Test 4.9: Only opening parentheses

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=(((("
```

**Expected**: No match (unbalanced)

#### Test 4.10: Complex nested structure

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=((()()))"
```

**Expected**: Match for valid nested structure

#### Test 4.11: Missing allow_dot_bracket flag

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&sequences=()"
```

**Expected**: May fail or handle differently without the flag

#### Test 4.17: RNA with unbalanced structure

```bash
curl "http://127.0.0.1:5000/simulate?mode=pda&rna_mode=true&sequences=CGUAGCUCUG&secondary_structures=(..((..)"
```

**Expected**: Returns validation error for unbalanced parentheses

---

## Mode 5: AUTO (Automatic Mode Selection)

AUTO mode lets the system choose the appropriate automaton type automatically.

### Basic Tests

#### Test 5.1: Simple pattern (should choose DFA/NFA)

```bash
curl "http://127.0.0.1:5000/simulate?mode=auto&pattern=ACGT&sequences=ACGT"
```

**Expected**: Automatically selects appropriate mode, returns matches

#### Test 5.2: Pattern with mismatch budget (should choose EFA)

```bash
curl "http://127.0.0.1:5000/simulate?mode=auto&pattern=ACGT&mismatch_budget=1&sequences=ACCT"
```

**Expected**: Automatically selects EFA mode

#### Test 5.3: Dot-bracket sequence (should choose PDA)

```bash
curl "http://127.0.0.1:5000/simulate?mode=auto&allow_dot_bracket=true&sequences=()"
```

**Expected**: Automatically selects PDA mode

### Edge Cases

#### Test 5.4: Conflicting parameters

```bash
curl "http://127.0.0.1:5000/simulate?mode=auto&pattern=ACGT&mismatch_budget=1&allow_dot_bracket=true&sequences=()"
```

**Expected**: System should prioritize based on parameters

---

## Cross-Mode Edge Cases

### Test X.1: Missing required parameters

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&sequences=ACGT"
```

**Expected**: Error (pattern required for regex modes)

### Test X.2: Invalid mode

```bash
curl "http://127.0.0.1:5000/simulate?mode=invalid&pattern=ACGT&sequences=ACGT"
```

**Expected**: Error 400 with message about unsupported mode

### Test X.3: No sequences and no input_path

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT"
```

**Expected**: Error (no input provided)

### Test X.4: Special characters in pattern (URL encoding)

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=A(CG|TT)*&sequences=ACGT"
```

**Expected**: Pattern should be properly parsed

### Test X.5: Very long pattern

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGTACGTACGTACGTACGTACGTACGTACGT&sequences=ACGTACGTACGTACGTACGTACGTACGTACGT"
```

**Expected**: Should handle long patterns

### Test X.6: Negative mismatch budget

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=-1&sequences=ACGT"
```

**Expected**: Error or treat as 0

### Test X.7: Non-integer mismatch budget

```bash
curl "http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=abc&sequences=ACGT"
```

**Expected**: Error (invalid type)

### Test X.8: Multiple sequences with mixed lengths

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&sequences=A&sequences=ACGT&sequences=ACGTACGTACGTACGT"
```

**Expected**: Handle sequences of varying lengths

### Test X.9: Case sensitivity

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=acgt&sequences=ACGT"
```

**Expected**: Check if matching is case-sensitive

### Test X.10: Whitespace in sequences

```bash
curl "http://127.0.0.1:5000/simulate?mode=nfa&pattern=ACGT&sequences=ACGT ACGT"
```

**Expected**: Handle whitespace appropriately

---

## Expected Response Structure

All successful responses should include:

```json
{
  "pattern": "...",
  "datasets": "N sequence(s)",
  "dataset_count": N,
  "automaton_mode": "NFA|DFA|EFA|PDA",
  "sequences": [
    {
      "sequence_number": 1,
      "length": N,
      "matches": ["[start,end)", ...],
      "match_ranges": [
        {
          "range": "[start,end)",
          "start": N,
          "end": N,
          "length": N
        }
      ],
      "sequence_text": "...",
      "states_visited": N,
      "max_stack_depth": N,  // Only for PDA mode
      "match_count": N,
      "has_matches": true/false,
      "coverage": 0.0-1.0,
      // RNA-specific fields (only when rna_mode=true)
      "rna_sequence": "CGUAGCUCUG",
      "dot_bracket": "(..((..)))",
      "rna_valid_bases": true,
      "rna_checks": [
        "5th nucleotide G <-> 8th nucleotide C -> valid? [OK]",
        "4th nucleotide A <-> 9th nucleotide U -> valid? [OK]",
        "Parentheses balanced? [OK]"
      ],
      "rna_result": "Valid"
    }
  ],
  "runs": 1,
  "matches": N,
  "all_accepted": true/false,
  "total_sequences": N,
  "sequences_with_matches": N,
  "total_states_visited": N,
  "average_coverage": 0.0-1.0,
  "automaton": {
    "kind": "PDA",
    "start": 0,
    "states": [
      {
        "id": 0,
        "accept": true,
        "stackDepth": 0,  // PDA-specific field
        "transitions": [
          {
            "code": 40,
            "symbol": "(",
            "to": 1,
            "operation": "push"  // PDA-specific: push, pop, or ignore
          }
        ]
      }
    ],
    "rules": [  // PDA-specific field
      {"expected": "("},
      {"expected": ")"}
    ]
  }
}
```

---

## Notes

1. **URL Encoding**: Special characters in patterns (like `|`, `*`, `+`, `?`, `(`, `)`) may need URL encoding in curl commands. Use `%7C` for `|`, `%28` for `(`, `%29` for `)`.

2. **Multiple Sequences**: Use repeated `sequences=` parameters or provide `input_path` pointing to a file.

3. **Automaton Structure**: Modes `nfa`, `dfa`, `efa`, and `pda` return automaton structure in the response if the binary supports `--dump-automaton`.
   - For PDA mode, the automaton includes `stackDepth` for each state and `operation` (push/pop/ignore) for transitions.

4. **Coverage**: Coverage is calculated as the percentage of sequence positions covered by at least one match.

5. **States Visited**: Different modes may visit different numbers of states even for the same pattern/sequence combination.

6. **RNA Mode Parameters**:
   - `rna_mode=true`: Enables RNA validation mode for PDA
   - `sequences`: RNA sequences (e.g., "CGUAGCUCUG")
   - `secondary_structures`: Inline dot-bracket notation (e.g., "(..((..)))")
   - `secondary_structure_path`: File path to dot-bracket notation file
   - Validates Watson-Crick pairs (A-U, G-C) and wobble pairs (G-U)

7. **PDA Modes**:
   - **Standard PDA**: Use `allow_dot_bracket=true` for simple parentheses validation
   - **RNA PDA**: Use `rna_mode=true` for RNA secondary structure validation with base pairing checks
