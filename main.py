"""
CLI entrypoint for the Resourcely.

This module provides the command-line interface for the staffing assignment tool,
integrating all backend components and orchestrating the main workflow.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

from scripts.io_utils import (
    load_csv_file,
    validate_projects_csv,
    validate_resourcing_csv,
    normalize_boolean_columns,
    save_csv_file,
    create_output_directory
)
from scripts.assigner import (
    assign_staff_to_projects,
    validate_constraints
)
from scripts.formatting import (
    extend_projects_table,
    format_output_for_display,
    generate_assignment_statistics
)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Resourcely - Assign Data Scientists and Data Engineers to projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python main.py --pros data/Prospective_Projects.csv --res data/Resourcing_View.csv --out output/Prospective_Projects_with_Assignments.csv
        """
    )
    
    parser.add_argument(
        '--pros',
        required=True,
        help='Path to Prospective_Projects.csv file'
    )
    
    parser.add_argument(
        '--res',
        required=True,
        help='Path to Resourcing_View.csv file'
    )
    
    parser.add_argument(
        '--out',
        required=True,
        help='Path to output CSV file'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging level (default: INFO)'
    )
    
    return parser.parse_args()


def validate_input_files(projects_file: str, resourcing_file: str) -> bool:
    """
    Validate that input files exist and are accessible.
    
    Args:
        projects_file: Path to projects CSV file
        resourcing_file: Path to resourcing CSV file
    
    Returns:
        True if both files are valid, False otherwise
    """
    try:
        projects_path = Path(projects_file)
        resourcing_path = Path(resourcing_file)
        
        if not projects_path.exists():
            logging.error(f"Projects file not found: {projects_file}")
            return False
            
        if not projects_path.is_file():
            logging.error(f"Projects path is not a file: {projects_file}")
            return False
            
        if not resourcing_path.exists():
            logging.error(f"Resourcing file not found: {resourcing_file}")
            return False
            
        if not resourcing_path.is_file():
            logging.error(f"Resourcing path is not a file: {resourcing_file}")
            return False
            
        # Check if files are readable
        try:
            with open(projects_path, 'r') as f:
                f.read(1)
        except Exception as e:
            logging.error(f"Cannot read projects file {projects_file}: {e}")
            return False
            
        try:
            with open(resourcing_path, 'r') as f:
                f.read(1)
        except Exception as e:
            logging.error(f"Cannot read resourcing file {resourcing_file}: {e}")
            return False
            
        return True
        
    except Exception as e:
        logging.error(f"Error validating input files: {e}")
        return False


def load_and_validate_data(
    projects_file: str,
    resourcing_file: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and validate input CSV files.
    
    Args:
        projects_file: Path to projects CSV file
        resourcing_file: Path to resourcing CSV file
    
    Returns:
        Tuple of (projects_df, resourcing_df)
    
    Raises:
        ValueError: If data validation fails
        FileNotFoundError: If input files don't exist
    """
    logging.info("Loading input CSV files...")
    
    # Load CSV files
    try:
        projects_df = load_csv_file(projects_file)
        logging.info(f"Loaded projects CSV: {projects_df.shape[0]} rows, {projects_df.shape[1]} columns")
    except Exception as e:
        raise FileNotFoundError(f"Failed to load projects file {projects_file}: {e}")
    
    try:
        resourcing_df = load_csv_file(resourcing_file)
        logging.info(f"Loaded resourcing CSV: {resourcing_df.shape[0]} rows, {resourcing_df.shape[1]} columns")
    except Exception as e:
        raise FileNotFoundError(f"Failed to load resourcing file {resourcing_file}: {e}")
    
    # Validate schemas
    logging.info("Validating data schemas...")
    
    is_valid, errors = validate_projects_csv(projects_df)
    if not is_valid:
        error_msg = "Projects CSV validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    is_valid, errors = validate_resourcing_csv(resourcing_df)
    if not is_valid:
        error_msg = "Resourcing CSV validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    # Normalize boolean columns
    logging.info("Normalizing boolean columns...")
    projects_df = normalize_boolean_columns(projects_df, ['Starts_Week1', 'Starts_Week2'])
    resourcing_df = normalize_boolean_columns(resourcing_df, ['Week1_Occupied', 'Week2_Occupied'])
    
    logging.info("Data loading and validation completed successfully")
    return projects_df, resourcing_df


def process_assignments(
    projects_df: pd.DataFrame,
    resourcing_df: pd.DataFrame
) -> tuple[pd.DataFrame, dict, dict]:
    """
    Process staff assignments and generate output.
    
    Args:
        projects_df: Projects DataFrame
        resourcing_df: Resourcing DataFrame
    
    Returns:
        Tuple of (extended_df, assignments, statistics)
    """
    logging.info("Running assignment algorithm...")
    
    # Run assignment algorithm
    assignments = assign_staff_to_projects(projects_df, resourcing_df)
    logging.info("Assignment algorithm completed")
    
    # Validate constraints
    logging.info("Validating assignment constraints...")
    is_valid, violations = validate_constraints(assignments, resourcing_df)
    if violations:
        logging.warning(f"Found {len(violations)} constraint violations:")
        for violation in violations:
            logging.warning(f"  - {violation}")
    else:
        logging.info("No constraint violations found")
    
    # Format output
    logging.info("Formatting output table...")
    extended_df = extend_projects_table(projects_df, assignments)
    
    # Generate statistics
    logging.info("Generating assignment statistics...")
    statistics = generate_assignment_statistics(assignments, projects_df)
    
    logging.info("Assignment processing completed successfully")
    return extended_df, assignments, statistics


def save_output(
    output_df: pd.DataFrame,
    output_file: str,
    create_dir: bool = True
) -> bool:
    """
    Save the final output to CSV file.
    
    Args:
        output_df: DataFrame to save
        output_file: Output file path
        create_dir: Whether to create output directory if it doesn't exist
    
    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(output_file)
        
        # Create output directory if needed
        if create_dir and output_path.parent != Path('.'):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created output directory: {output_path.parent}")
        
        # Save the CSV file
        success = save_csv_file(output_df, output_file)
        if success:
            logging.info(f"Successfully saved output to: {output_file}")
            logging.info(f"Output contains {output_df.shape[0]} rows and {output_df.shape[1]} columns")
        else:
            logging.error(f"Failed to save output to: {output_file}")
        
        return success
        
    except Exception as e:
        logging.error(f"Error saving output file {output_file}: {e}")
        return False


def print_summary(
    assignments: dict,
    statistics: dict,
    output_file: str
) -> None:
    """
    Print assignment summary to console.
    
    Args:
        assignments: Assignment dictionary
        statistics: Assignment statistics dictionary
        output_file: Path to output file
    """
    print("\n" + "="*60)
    print("           2-WEEK STAFFING ASSIGNMENT SUMMARY")
    print("="*60)
    
    # Count assignments
    total_assignments = 0
    projects_with_assignments = 0
    people_assigned = set()
    
    for project, weeks in assignments.items():
        project_has_assignments = False
        for week, roles in weeks.items():
            for role, staff_list in roles.items():
                if staff_list:
                    total_assignments += len(staff_list)
                    people_assigned.update(staff_list)
                    project_has_assignments = True
        if project_has_assignments:
            projects_with_assignments += 1
    
    print(f"\nASSIGNMENT OVERVIEW:")
    print(f"  • Projects with assignments: {projects_with_assignments}")
    print(f"  • Total assignments made: {total_assignments}")
    print(f"  • Unique people assigned: {len(people_assigned)}")
    
    # Show statistics
    print(f"\nRESOURCE STATISTICS:")
    print(f"  • Total DS needed: {statistics.get('total_ds_needed', 0)}")
    print(f"  • Total DE needed: {statistics.get('total_de_needed', 0)}")
    print(f"  • DS assignments made: {statistics.get('ds_assignments', 0)}")
    print(f"  • DE assignments made: {statistics.get('de_assignments', 0)}")
    print(f"  • Total shortage: {statistics.get('total_shortage', 0)}")
    
    # Show detailed assignments
    print(f"\nDETAILED ASSIGNMENTS:")
    for project, weeks in assignments.items():
        project_assignments = []
        for week, roles in weeks.items():
            for role, staff_list in roles.items():
                if staff_list:
                    staff_str = ", ".join(staff_list)
                    project_assignments.append(f"{week} {role}: {staff_str}")
        
        if project_assignments:
            print(f"  • {project}:")
            for assignment in project_assignments:
                print(f"    - {assignment}")
        else:
            print(f"  • {project}: No assignments made")
    
    print(f"\nOUTPUT:")
    print(f"  • Extended CSV saved to: {output_file}")
    print(f"  • Assignment log saved to: output/assignment_log.md")
    
    print("\n" + "="*60)


def generate_assignment_log(
    assignments: dict,
    statistics: dict,
    projects_df: pd.DataFrame
) -> None:
    """
    Generate assignment log markdown file.
    
    Args:
        assignments: Assignment dictionary
        statistics: Assignment statistics dictionary
        projects_df: Original projects DataFrame
    """
    try:
        log_path = Path("output/assignment_log.md")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'w') as f:
            f.write("# 2-Week Staffing Assignment Log\n\n")
            f.write(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary statistics
            f.write("## Assignment Summary\n\n")
            f.write(f"- **Total DS needed**: {statistics.get('total_ds_needed', 0)}\n")
            f.write(f"- **Total DE needed**: {statistics.get('total_de_needed', 0)}\n")
            f.write(f"- **DS assignments made**: {statistics.get('ds_assignments', 0)}\n")
            f.write(f"- **DE assignments made**: {statistics.get('de_assignments', 0)}\n")
            f.write(f"- **Total shortage**: {statistics.get('total_shortage', 0)}\n\n")
            
            # Detailed assignments
            f.write("## Project Assignments\n\n")
            for project, weeks in assignments.items():
                f.write(f"### {project}\n\n")
                
                # Get project requirements
                project_row = projects_df[projects_df['Project'] == project].iloc[0]
                
                for week_num in [1, 2]:
                    week_key = f"Week {week_num}"
                    ds_needed = project_row[f'Week{week_num}_DS_Needed']
                    de_needed = project_row[f'Week{week_num}_DE_Needed']
                    
                    if ds_needed > 0 or de_needed > 0:
                        f.write(f"**{week_key}**:\n")
                        f.write(f"- Required: {ds_needed} DS, {de_needed} DE\n")
                        
                        # Show assignments
                        ds_assigned = weeks.get(week_key, {}).get('DS', [])
                        de_assigned = weeks.get(week_key, {}).get('DE', [])
                        
                        if ds_assigned:
                            f.write(f"- DS assigned: {', '.join(ds_assigned)}\n")
                        else:
                            f.write(f"- DS assigned: None\n")
                            
                        if de_assigned:
                            f.write(f"- DE assigned: {', '.join(de_assigned)}\n")
                        else:
                            f.write(f"- DE assigned: None\n")
                        
                        # Show shortages
                        ds_shortage = max(0, ds_needed - len(ds_assigned))
                        de_shortage = max(0, de_needed - len(de_assigned))
                        
                        if ds_shortage > 0 or de_shortage > 0:
                            shortages = []
                            if ds_shortage > 0:
                                shortages.append(f"missing {ds_shortage} DS")
                            if de_shortage > 0:
                                shortages.append(f"missing {de_shortage} DE")
                            f.write(f"- **Shortage**: {', '.join(shortages)}\n")
                        
                        f.write("\n")
                
                f.write("\n")
            
            # Resource utilization
            f.write("## Resource Utilization\n\n")
            people_assigned = set()
            for weeks in assignments.values():
                for roles in weeks.values():
                    for staff_list in roles.values():
                        people_assigned.update(staff_list)
            
            if people_assigned:
                f.write("**People assigned to projects**:\n")
                for person in sorted(people_assigned):
                    f.write(f"- {person}\n")
            else:
                f.write("No staff assignments were made.\n")
        
        logging.info(f"Assignment log generated: {log_path}")
        
    except Exception as e:
        logging.error(f"Failed to generate assignment log: {e}")


def handle_errors(error: Exception, context: str) -> None:
    """
    Handle and log errors with appropriate context.
    
    Args:
        error: The exception that occurred
        context: Context description of where the error occurred
    """
    error_msg = f"Error in {context}: {str(error)}"
    logging.error(error_msg)
    
    # Print to console as well for immediate visibility
    print(f"\n❌ {error_msg}")
    
    # Log additional details for debugging
    import traceback
    logging.debug(f"Full traceback for {context}:\n{traceback.format_exc()}")


def main() -> int:
    """
    Main entry point for the CLI application.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Set up logging
        setup_logging(getattr(args, 'log_level', 'INFO'))
        
        logging.info("Starting Resourcely")
        
        # Validate input files
        if not validate_input_files(args.pros, args.res):
            logging.error("Input file validation failed")
            return 1
        
        # Load and validate data
        projects_df, resourcing_df = load_and_validate_data(
            args.pros,
            args.res
        )
        
        # Process assignments
        extended_df, assignments, statistics = process_assignments(projects_df, resourcing_df)
        
        # Save output
        if not save_output(extended_df, args.out):
            logging.error("Failed to save output file")
            return 1
        
        # Generate assignment log
        generate_assignment_log(assignments, statistics, projects_df)
        
        # Print summary
        print_summary(assignments, statistics, args.out)
        
        logging.info("Staffing assignment completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
        return 130
    except Exception as e:
        handle_errors(e, "main execution")
        return 1


if __name__ == "__main__":
    sys.exit(main())