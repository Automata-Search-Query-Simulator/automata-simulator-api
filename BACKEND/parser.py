"""Parser module for automata simulator stdout output."""
import re


def parse_match_range(match_str: str) -> dict:
    """Parse a match range string like '[0,1)' into structured data."""
    # Match pattern: [start,end) or [start,end]
    range_match = re.match(r"\[(\d+),(\d+)\)", match_str)
    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        return {
            "range": match_str,
            "start": start,
            "end": end,
            "length": end - start,
        }
    return {"range": match_str, "start": 0, "end": 0, "length": 0}

#comment for testing
def parse_stdout(stdout: str) -> dict:
    """Parse the stdout from automata_sim into structured JSON."""
    result = {
        "pattern": "",
        "datasets": "",
        "dataset_count": 0,
        "automaton_mode": "",
        "sequences": [],
        "runs": 0,
        "matches": 0,
        "all_accepted": False,
    }

    lines = stdout.strip().split("\n")

    # Parse header information
    for line in lines:
        if line.startswith("Pattern:"):
            result["pattern"] = line.split("Pattern:", 1)[1].strip()
        elif line.startswith("Datasets:"):
            datasets_str = line.split("Datasets:", 1)[1].strip()
            result["datasets"] = datasets_str
            # Extract number from "1 sequence(s)" or similar
            count_match = re.search(r"(\d+)", datasets_str)
            if count_match:
                result["dataset_count"] = int(count_match.group(1))
        elif line.startswith("Automaton Mode:"):
            result["automaton_mode"] = line.split("Automaton Mode:", 1)[1].strip()

    # Parse sequences
    sequence_pattern = re.compile(r"Sequence #(\d+) \(len=(\d+)\)")
    matches_pattern = re.compile(r"\s*Matches: (.+)")
    states_visited_pattern = re.compile(r"\s*States visited: (\d+)(?:\s*\|\s*Max stack depth: (\d+))?")
    rna_result_pattern = re.compile(r"\s*-> Result: (Valid|Invalid)")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        seq_match = sequence_pattern.match(line)
        if seq_match:
            seq_num = int(seq_match.group(1))
            seq_len = int(seq_match.group(2))

            sequence_data = {
                "sequence_number": seq_num,
                "length": seq_len,
                "matches": [],
                "match_ranges": [],
                "sequence_text": "",
                "states_visited": 0,
                "max_stack_depth": None,  # Only for PDA mode
                # RNA/PDA-specific fields
                "rna_sequence": None,
                "dot_bracket": None,
                "rna_valid_bases": None,
                "rna_checks": [],
                "rna_result": None,
                "pda_messages": [],
                "is_rna_mode": False,
            }

            # Look ahead for RNA-specific format
            # RNA format: Sequence: CGUAGCUCUG
            #             Dot-bracket: (..((..)))
            #             [OK] Valid RNA Bases
            #             Check: ...
            i += 1
            is_rna_mode = False
            
            # Check if next line starts with "Sequence:" (RNA mode)
            # Look for "Sequence:" in the current or next few lines
            if i < len(lines) and "Sequence:" in lines[i]:
                is_rna_mode = True
                sequence_data["is_rna_mode"] = True
                # Extract RNA sequence
                seq_line = lines[i].strip()
                if "Sequence:" in seq_line:
                    sequence_data["rna_sequence"] = seq_line.split("Sequence:", 1)[1].strip()
                    i += 1
                
                # Extract dot-bracket notation
                if i < len(lines) and "Dot-bracket:" in lines[i]:
                    dot_bracket_line = lines[i].strip()
                    sequence_data["dot_bracket"] = dot_bracket_line.split("Dot-bracket:", 1)[1].strip()
                    i += 1
                
                # Skip empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1

                # Gather RNA/PDA validation block lines until we hit the next sequence,
                # summary line, or automaton stats.
                validation_lines = []
                rewind_for_next_sequence = False
                while i < len(lines):
                    candidate_raw = lines[i]
                    candidate = candidate_raw.strip()
                    if not candidate:
                        i += 1
                        continue
                    if candidate.startswith("Sequence #"):
                        rewind_for_next_sequence = True
                        break
                    if candidate.startswith("Runs:"):
                        break
                    if matches_pattern.match(candidate_raw) or candidate.startswith("Matches:") or candidate.startswith("No matches found.") or candidate.startswith("States visited:"):
                        break
                    validation_lines.append(candidate)
                    i += 1

                j = 0
                while j < len(validation_lines):
                    line = validation_lines[j]
                    if "Valid RNA Bases" in line:
                        sequence_data["rna_valid_bases"] = "[OK]" in line or "OK" in line
                        j += 1
                        continue
                    if line.startswith("Check:"):
                        j += 1
                        while j < len(validation_lines) and validation_lines[j].startswith("- "):
                            sequence_data["rna_checks"].append(validation_lines[j][2:])
                            j += 1
                        continue
                    if line.startswith("-> Result:"):
                        result_match = rna_result_pattern.match(line)
                        if result_match:
                            sequence_data["rna_result"] = result_match.group(1)
                        j += 1
                        continue
                    # Capture additional PDA-specific validation messages (length mismatch, etc.)
                    sequence_data["pda_messages"].append(line)
                    j += 1

                if rewind_for_next_sequence:
                    i -= 1

            # If not RNA mode, use old parsing logic
            if not is_rna_mode:
                # Get matches from current line (may be indented)
                if i < len(lines):
                    matches_line = lines[i]
                    matches_match = matches_pattern.match(matches_line)
                    if matches_match:
                        matches_str = matches_match.group(1).strip()
                        # Extract all match ranges like [0,1) [0,3) etc.
                        # Use a more precise pattern to ensure we get individual ranges
                        match_ranges_raw = re.findall(r"\[\d+,\d+\)", matches_str)
                        sequence_data["matches"] = match_ranges_raw
                        # Parse into structured format
                        match_ranges_parsed = [
                            parse_match_range(m) for m in match_ranges_raw
                        ]
                        # Sort by start position for easier visualization
                        match_ranges_parsed.sort(key=lambda x: x["start"])
                        sequence_data["match_ranges"] = match_ranges_parsed

                # Get sequence text from next line (may be indented, no label)
                i += 1
                if i < len(lines):
                    seq_text = lines[i].strip()
                    # Sequence text is the line that's not "Matches:" or "States visited:"
                    if seq_text and not seq_text.startswith("Matches:") and not seq_text.startswith("States visited:"):
                        sequence_data["sequence_text"] = seq_text

                # Get states visited (may be indented)
                # For PDA mode, this may also include "Max stack depth"
                i += 1
                if i < len(lines):
                    states_line = lines[i]
                    states_match = states_visited_pattern.match(states_line)
                    if states_match:
                        sequence_data["states_visited"] = int(states_match.group(1))
                        # PDA mode includes max stack depth
                        if states_match.group(2):
                            sequence_data["max_stack_depth"] = int(states_match.group(2))

            # Normalize sequence text when running RNA validation so UI consumers
            # don't need to read two different fields.
            if is_rna_mode and sequence_data["rna_sequence"]:
                sequence_data["sequence_text"] = sequence_data["rna_sequence"]

            if is_rna_mode:
                # Treat a valid RNA pairing as a successful match for stats/coverage.
                sequence_data["match_count"] = 1 if sequence_data["rna_result"] == "Valid" else 0
                sequence_data["has_matches"] = sequence_data["match_count"] > 0
                if sequence_data["has_matches"] and seq_len > 0:
                    sequence_data["coverage"] = 1.0
                else:
                    sequence_data["coverage"] = 0.0

                sequence_data["pda_validation"] = {
                    "sequence": sequence_data.get("rna_sequence"),
                    "structure": sequence_data.get("dot_bracket"),
                    "valid_rna_bases": sequence_data.get("rna_valid_bases"),
                    "checks": sequence_data.get("rna_checks", []),
                    "result": sequence_data.get("rna_result"),
                    "messages": sequence_data.get("pda_messages", []),
                }
            else:
                # Add match count for regex/NFA/DFA/EFA/PDA (dot-bracket) modes
                sequence_data["match_count"] = len(sequence_data["matches"])
                sequence_data["has_matches"] = len(sequence_data["matches"]) > 0
                
                # Calculate match coverage (percentage of sequence covered by matches)
                if sequence_data["match_ranges"] and seq_len > 0:
                    covered_positions = set()
                    for match_range in sequence_data["match_ranges"]:
                        covered_positions.update(range(match_range["start"], match_range["end"]))
                    sequence_data["coverage"] = len(covered_positions) / seq_len
                else:
                    sequence_data["coverage"] = 0.0

            result["sequences"].append(sequence_data)
        i += 1

    # Parse summary line: "Runs: 1, Matches: 6, All accepted: no"
    summary_pattern = re.compile(
        r"Runs: (\d+), Matches: (\d+), All accepted: (yes|no)"
    )
    for line in lines:
        summary_match = summary_pattern.search(line)
        if summary_match:
            result["runs"] = int(summary_match.group(1))
            result["matches"] = int(summary_match.group(2))
            result["all_accepted"] = summary_match.group(3).lower() == "yes"
            break

    # Add summary statistics for visualization
    result["total_sequences"] = len(result["sequences"])
    result["sequences_with_matches"] = sum(
        1 for seq in result["sequences"] if seq.get("has_matches", False)
    )
    result["total_states_visited"] = sum(
        seq.get("states_visited", 0) for seq in result["sequences"]
    )
    result["average_coverage"] = (
        sum(seq.get("coverage", 0.0) for seq in result["sequences"])
        / result["total_sequences"]
        if result["total_sequences"] > 0
        else 0.0
    )

    if result["automaton_mode"].lower() == "pda":
        pda_sequences = []
        for seq in result["sequences"]:
            pda_sequences.append(
                {
                    "sequence_number": seq.get("sequence_number"),
                    "length": seq.get("length"),
                    "sequence": seq.get("sequence_text"),
                    "dot_bracket": seq.get("dot_bracket"),
                    "result": seq.get("rna_result"),
                    "valid_rna_bases": seq.get("rna_valid_bases"),
                    "checks": seq.get("rna_checks", []),
                    "messages": seq.get("pda_messages", []),
                    "has_matches": seq.get("has_matches", False),
                    "match_count": seq.get("match_count", 0),
                    "coverage": seq.get("coverage", 0.0),
                }
            )
        result["pda_sequences"] = pda_sequences

    return result
