# Flask Backend

Simple Flask API that shells out to `automata_sim.exe`, collects the CLI output, and returns the constructed automaton JSON (`--dump-automaton`) plus stdout/stderr. Use it to bridge the C++ simulator with a web frontend.

## Prerequisites

- Python 3.11+ (same version used by your frontend tooling).
- pip / venv.
- `automata_sim.exe` built from the project root (copy it into this `BACKEND/` folder or set `AUTOMATA_SIM_PATH`).

## Installation

```powershell
cd BACKEND
python -m venv .venv
.venv\Scripts\activate           # PowerShell
pip install -r requirements.txt
```

## Running the server

```powershell
cd BACKEND
.venv\Scripts\activate
set FLASK_APP=app.py             # PowerShell; use export on bash
flask run --port 5000
```

Optional: override the simulator path

```powershell
set AUTOMATA_SIM_PATH=C:\path\to\build\bin\automata_sim.exe
```

## API

### `POST /simulate`

Request body (all optional except `pattern` for regex modes):

```jsonc
{
  "pattern": "A(CG|TT)*",
  "mode": "dfa",                // auto, nfa, dfa, efa, pda
  "mismatch_budget": 2,
  "allow_dot_bracket": false,
  "trace": false,
  "input_path": "datasets/dna/sample.txt",
  "sequences": ["ACGTACGT", "..."] // used when input_path omitted
}
```

Response:

```jsonc
{
  "command": ["BACKEND/automata_sim.exe", "--mode", "dfa", "..."],
  "return_code": 0,
  "stdout": "╔════ ...",
  "stderr": "",
  "automaton": { "kind": "DFA", "states": [...] }
}
```

Status `200` indicates success; `500` means the simulator failed; `400` covers validation errors.

### `GET /healthz`

Quick check to confirm the binary is reachable.

## Testing with curl or HTTPie

```powershell
curl -X POST http://127.0.0.1:5000/simulate ^
  -H "Content-Type: application/json" ^
  -d "{\"pattern\":\"A(CG|TT)*\",\"mode\":\"nfa\",\"input_path\":\"datasets/dna/sample.txt\"}"
```

Or from PowerShell with `Invoke-RestMethod`:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/simulate `
  -Body (@{ pattern = "A(CG|TT)*"; mode = "dfa"; input_path = "datasets/dna/sample.txt" } | ConvertTo-Json) `
  -ContentType "application/json"
```

Your frontend can hit `/simulate` with user-selected parameters to get both the textual summary (`stdout`) and structured automaton graph for visualization.

