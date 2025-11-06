# Resourcely

A Python-based tool for optimally assigning Data Scientists (DS) and Data Engineers (DE) to projects across two weeks, ensuring role matching, availability constraints, and continuity preferences.

## Overview

The Resourcely automates the complex task of staff assignment by:

- **Role Matching**: Ensures DS roles are filled by Data Scientists and DE roles by Data Engineers
- **Availability Constraints**: Respects individual staff availability for each week
- **One Person Per Project Per Week**: Prevents overallocation of staff to multiple projects simultaneously
- **Continuity Preference**: Prioritizes Week 1 assignees for Week 2 roles when possible
- **Deterministic Results**: Uses alphabetical tie-breaking for consistent, reproducible assignments

## Project Structure

```
/
├── main.py                    # CLI entrypoint and workflow orchestration
├── requirements.txt           # Python dependencies (pandas only)
├── README.md                 # This file
├── scripts/
│   ├── assigner.py           # Core assignment algorithm
│   ├── io_utils.py           # CSV load/validate/save operations
│   └── formatting.py         # Output formatting and data presentation
└── output/                   # Directory for generated assignment files
    └── .gitkeep             # Maintains directory structure
```

## Input Requirements

### Projects CSV Format
The projects file should contain the following columns:
- `Project Name`: Unique identifier for each project
- `Week 1 DS Role`: Number of DS roles needed in Week 1 (integer)
- `Week 1 DE Role`: Number of DE roles needed in Week 1 (integer)
- `Week 2 DS Role`: Number of DS roles needed in Week 2 (integer)
- `Week 2 DE Role`: Number of DE roles needed in Week 2 (integer)

### Resourcing CSV Format
The resourcing file should contain the following columns:
- `Name`: Staff member's name (unique identifier)
- `Role`: Staff role (must be "DS" or "DE")
- `Week 1 Available`: Availability for Week 1 ("Yes"/"No" or boolean)
- `Week 2 Available`: Availability for Week 2 ("Yes"/"No" or boolean)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python main.py --projects projects.csv --resourcing resourcing.csv --output output/assignments.csv
```

### Command Line Arguments
- `--projects`: Path to the projects CSV file (required)
- `--resourcing`: Path to the resourcing CSV file (required)
- `--output`: Path for the output CSV file (required)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR) - default: INFO

### Example
```bash
python main.py \
  --projects Prospective_Projects.csv \
  --resourcing Resourcing_View.csv \
  --output output/staffing_assignments.csv \
  --log-level INFO
```

## Output Format

The tool generates an extended version of the original projects table with four additional "Proposed" columns:

- `Proposed Week 1 DS`: Assigned Data Scientists for Week 1
- `Proposed Week 1 DE`: Assigned Data Engineers for Week 1
- `Proposed Week 2 DS`: Assigned Data Scientists for Week 2
- `Proposed Week 2 DE`: Assigned Data Engineers for Week 2

Staff assignments are presented as comma-separated lists when multiple people are assigned to the same role.

## Assignment Algorithm

The tool implements a sophisticated assignment algorithm that:

1. **Validates Input**: Ensures all required data is present and properly formatted
2. **Calculates Requirements**: Determines total role needs by week
3. **Filters Availability**: Identifies available staff by role and week
4. **Applies Constraints**: Enforces one-person-per-project-per-week rule
5. **Prioritizes Continuity**: Prefers Week 1 assignees for Week 2 roles
6. **Resolves Ties**: Uses alphabetical ordering for deterministic results
7. **Validates Output**: Confirms all constraints are satisfied

## Key Features

### Constraint Handling
- **Role Matching**: Strict enforcement of DS→DS and DE→DE assignments
- **Availability Respect**: Only assigns available staff members
- **No Double-Booking**: Prevents staff from being assigned to multiple projects in the same week

### Continuity Optimization
- Week 1 assignees are given preference for Week 2 assignments in the same role
- Helps maintain project knowledge and reduces context switching
- Improves project efficiency and staff satisfaction

### Deterministic Results
- Alphabetical tie-breaking ensures consistent results across runs
- Reproducible assignments for audit and planning purposes
- Eliminates randomness in staff selection

## Error Handling

The tool provides comprehensive error handling for:
- Missing or invalid input files
- Incorrect CSV formats or missing columns
- Invalid role values (non-DS/DE entries)
- Insufficient staff availability
- Constraint violations
- File permission issues

## Logging

Detailed logging provides visibility into:
- Input validation results
- Assignment process steps
- Constraint checking outcomes
- Error conditions and resolutions
- Final assignment statistics

## Development Status

This project is currently in the scaffolding phase with function stubs in place. The core architecture is established and ready for implementation of the assignment algorithms and data processing logic.

## Future Enhancements

Potential improvements for future versions:
- Support for additional roles beyond DS/DE
- Weighted preference scoring for assignments
- Integration with external calendar systems
- Web-based user interface
- Advanced reporting and analytics
- Multi-week planning beyond 2 weeks

## Contributing

When implementing the function stubs:
1. Maintain the existing function signatures and docstrings
2. Follow Python best practices and PEP 8 style guidelines
3. Add comprehensive error handling and logging
4. Include unit tests for all functions
5. Update this README with any new features or requirements

## License

This project is intended for internal use in staff assignment and resource planning.