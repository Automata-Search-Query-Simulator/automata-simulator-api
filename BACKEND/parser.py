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
    states_visited_pattern = re.compile(r"\s*States visited: (\d+)")

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
            }

            # Get matches from next line (may be indented)
            i += 1
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
            i += 1
            if i < len(lines):
                states_line = lines[i]
                states_match = states_visited_pattern.match(states_line)
                if states_match:
                    sequence_data["states_visited"] = int(states_match.group(1))

            # Add match count for this sequence
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

    return result

