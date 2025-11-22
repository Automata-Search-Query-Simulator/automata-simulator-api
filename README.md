# Flask Backend

Simple Flask API that shells out to `automata_sim` (or `automata_sim.exe` on Windows), parses the CLI output, and returns structured JSON optimized for web visualization. Use it to bridge the C++ simulator with a web frontend.

## Project Structure

The backend is modularized for maintainability:

- **`app.py`** - Flask routes and endpoints only
- **`config.py`** - Configuration, binary path management, and error handling
- **`utils.py`** - Utility functions for command building and file operations
- **`parser.py`** - Parsing logic to convert stdout into structured JSON

## Prerequisites

- Python 3.11+ (same version used by your frontend tooling).
- pip / venv.
- Platform-specific binary built from the project root:
  - **Windows**: `automata_sim.exe`
  - **macOS/Linux**: `automata_sim`
  
  Copy the appropriate binary into this `BACKEND/` folder or set `AUTOMATA_SIM_PATH` environment variable.

## Installation

### Windows (PowerShell)

```powershell
cd BACKEND
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS/Linux (bash/zsh)

```bash
cd BACKEND
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the server

### Windows (PowerShell)

```powershell
cd BACKEND
.venv\Scripts\activate
$env:FLASK_APP="app.py"
flask run --port 5000
```

### macOS/Linux (bash/zsh)

```bash
cd BACKEND
source .venv/bin/activate
export FLASK_APP=app.py
flask run --port 5000
```

### Optional: Override the simulator path

**Windows (PowerShell):**
```powershell
$env:AUTOMATA_SIM_PATH="C:\path\to\build\bin\automata_sim.exe"
```

**macOS/Linux (bash/zsh):**
```bash
export AUTOMATA_SIM_PATH=/path/to/build/bin/automata_sim
```

**Note for macOS/Linux:** Ensure the binary has execute permissions:
```bash
chmod +x BACKEND/automata_sim
```

## API

### `GET /simulate`

Query parameters (all optional except `pattern` for regex modes):

- `pattern`: The regex pattern to match (e.g., `A(CG|TT)*`)
- `mode`: Automaton mode - `auto`, `nfa`, `dfa`, `efa`, or `pda` (default: `auto`)
- `mismatch_budget`: Integer value for mismatch budget
- `allow_dot_bracket`: Boolean (`true`/`false`/`1`/`0`/`yes`/`no`)
- `input_path`: Path to input file (e.g., `datasets/dna/sample.txt`)
- `sequences`: Multiple sequences can be passed as repeated query parameters (used when `input_path` is omitted)

Response (structured JSON optimized for visualization):

```jsonc
{
  "pattern": "A(CG|TT)*",
  "datasets": "1 sequence(s)",
  "dataset_count": 1,
  "automaton_mode": "DFA",
  "sequences": [
    {
      "sequence_number": 1,
      "length": 12,
      "matches": ["[0,1)", "[0,3)", "[4,5)", "[4,7)", "[8,9)", "[8,11)"],
      "match_ranges": [
        {
          "range": "[0,1)",
          "start": 0,
          "end": 1,
          "length": 1
        },
        // ... more match ranges
      ],
      "sequence_text": "ACGTACGTACGT",
      "states_visited": 23,
      "match_count": 6,
      "has_matches": true,
      "coverage": 0.5
    }
  ],
  "runs": 1,
  "matches": 6,
  "all_accepted": false,
  "total_sequences": 1,
  "sequences_with_matches": 1,
  "total_states_visited": 23,
  "average_coverage": 0.5
}
```

Status `200` indicates success; `500` means the simulator failed; `400` covers validation errors.

**Note:** The response is parsed from stdout and structured for easy visualization. Match ranges are sorted by start position, and coverage metrics are calculated automatically.

### Inline sequence examples

You can skip `input_path` and send raw sequences directly as query parameters. Add the same key multiple times to submit several sequences.

#### DFA example (regex)

```
GET http://127.0.0.1:5000/simulate?mode=dfa&pattern=A(CG|TT)*&sequences=ACGTACGTACGT
```

#### EFA example (with mismatch budget)

```
GET http://127.0.0.1:5000/simulate?mode=efa&pattern=ACGT&mismatch_budget=2&sequences=ACGTACGTACGT
```

#### PDA example (dot-bracket sequences)

```
GET http://127.0.0.1:5000/simulate?mode=pda&allow_dot_bracket=true&sequences=(()())&sequences=((..))
```

Each inline request returns the parsed results plus the automaton structure (states + transitions) for `nfa`, `dfa`, `efa`, and `pda` modes. Sample response:

```jsonc
{
  "pattern": "ACGT",
  "automaton_mode": "EFA",
  "sequences": [
    {
      "sequence_number": 1,
      "length": 12,
      "matches": ["[0,4)", "[4,8)", "[8,12)"],
      "sequence_text": "ACGTACGTACGT",
      "states_visited": 36
    }
  ],
  "runs": 1,
  "matches": 3,
  "automaton": {
    "kind": "EFA",
    "pattern": "ACGT",
    "start": 0,
    "states": [
      {
        "id": 0,
        "accept": false,
        "transitions": [
          {"symbol": "A", "to": 3, "type": "match"},
          {"symbol": "C", "to": 4, "type": "mismatch"}
          // ...
        ]
      }
      // ...
    ]
  }
}
```

### `GET /healthz`

Quick check to confirm the binary is reachable.

## Testing with curl or HTTPie

### Windows (PowerShell)

```powershell
curl "http://127.0.0.1:5000/simulate?pattern=A(CG|TT)*&mode=nfa&input_path=datasets/dna/sample.txt"
```

Or with `Invoke-RestMethod`:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:5000/simulate?pattern=A(CG|TT)*&mode=dfa&input_path=datasets/dna/sample.txt"
```

### macOS/Linux (bash/zsh)

```bash
curl "http://127.0.0.1:5000/simulate?pattern=A(CG|TT)*&mode=nfa&input_path=datasets/dna/sample.txt"
```

**Note:** For multiple sequences, use repeated query parameters:
```bash
curl "http://127.0.0.1:5000/simulate?pattern=A(CG|TT)*&sequences=ACGTACGT&sequences=TTTTTT"
```

Your frontend can hit `/simulate` with user-selected parameters to get structured JSON data optimized for visualization, including parsed match positions, coverage metrics, and sequence information.

