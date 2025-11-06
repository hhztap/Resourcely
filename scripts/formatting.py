"""
Output formatting utilities for the Resourcely.

This module handles:
- Extending original table with 4 "Proposed" columns
- Converting assignment lists to comma-separated strings
- Structuring final staffing assignments
- Data presentation formatting
"""

from typing import Dict, List, Optional, Tuple, Any
import pandas as pd


def extend_projects_table(
    projects_df: pd.DataFrame,
    assignments: Dict[str, Dict[str, Dict[str, List[str]]]]
) -> pd.DataFrame:
    """
    Extend the original projects table with 4 "Proposed" assignment columns.
    
    Adds columns:
    - Proposed_DS_Week1
    - Proposed_DS_Week2
    - Proposed_DE_Week1
    - Proposed_DE_Week2
    
    Args:
        projects_df: Original projects DataFrame
        assignments: Assignment dictionary from assigner module
    
    Returns:
        Extended DataFrame with proposed assignment columns
    """
    # Create a copy of the original DataFrame
    extended_df = projects_df.copy()
    
    # Initialize the 4 new columns with empty strings
    extended_df['Proposed_DS_Week1'] = ""
    extended_df['Proposed_DS_Week2'] = ""
    extended_df['Proposed_DE_Week1'] = ""
    extended_df['Proposed_DE_Week2'] = ""
    
    # Convert assignments to strings and map to projects
    string_assignments = convert_assignments_to_strings(assignments)
    project_mappings = map_assignments_to_projects(string_assignments, projects_df)
    
    # Fill in the assignment columns
    for idx, row in extended_df.iterrows():
        project_name = row['Project']
        if project_name in project_mappings:
            mappings = project_mappings[project_name]
            extended_df.at[idx, 'Proposed_DS_Week1'] = mappings.get('Proposed_DS_Week1', "")
            extended_df.at[idx, 'Proposed_DS_Week2'] = mappings.get('Proposed_DS_Week2', "")
            extended_df.at[idx, 'Proposed_DE_Week1'] = mappings.get('Proposed_DE_Week1', "")
            extended_df.at[idx, 'Proposed_DE_Week2'] = mappings.get('Proposed_DE_Week2', "")
    
    return extended_df


def convert_assignments_to_strings(
    assignments: Dict[str, Dict[str, Dict[str, List[str]]]]
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Convert assignment lists to comma-separated strings for each project.
    
    Args:
        assignments: Raw assignment dictionary {project: {week: {role: [names]}}}
    
    Returns:
        Dictionary with assignments formatted as comma-separated strings
    """
    string_assignments = {}
    
    for project, weeks in assignments.items():
        string_assignments[project] = {}
        for week, roles in weeks.items():
            string_assignments[project][week] = {}
            for role, staff_list in roles.items():
                # Convert list to comma-separated string (no spaces after commas)
                if staff_list:
                    string_assignments[project][week][role] = ",".join(staff_list)
                else:
                    string_assignments[project][week][role] = ""
    
    return string_assignments


def format_assignment_columns(
    extended_df: pd.DataFrame,
    assignment_columns: List[str]
) -> pd.DataFrame:
    """
    Format the assignment columns for better presentation.
    
    Args:
        extended_df: DataFrame with assignment columns
        assignment_columns: List of column names to format
    
    Returns:
        DataFrame with formatted assignment columns
    """
    pass


def create_staffing_summary(
    assignments: Dict[str, Dict[str, List[str]]],
    resourcing_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a summary table showing staff assignments by person.
    
    Args:
        assignments: Assignment dictionary
        resourcing_df: Original resourcing DataFrame
    
    Returns:
        DataFrame showing each person's assignments across weeks
    """
    pass


def map_assignments_to_projects(
    assignments: Dict[str, Dict[str, Dict[str, str]]],
    projects_df: pd.DataFrame
) -> Dict[str, Dict[str, str]]:
    """
    Map role-based assignments to specific projects.
    
    Args:
        assignments: Role-based assignment dictionary (string format)
        projects_df: Projects DataFrame with role requirements
    
    Returns:
        Dictionary mapping projects to assigned staff by role and week
    """
    project_mappings = {}
    
    for project_name in projects_df['Project']:
        project_mappings[project_name] = {
            'Proposed_DS_Week1': "",
            'Proposed_DS_Week2': "",
            'Proposed_DE_Week1': "",
            'Proposed_DE_Week2': ""
        }
        
        if project_name in assignments:
            project_assignments = assignments[project_name]
            
            # Map Week 1 assignments
            if 'Week 1' in project_assignments:
                week1 = project_assignments['Week 1']
                project_mappings[project_name]['Proposed_DS_Week1'] = week1.get('DS', "")
                project_mappings[project_name]['Proposed_DE_Week1'] = week1.get('DE', "")
            
            # Map Week 2 assignments
            if 'Week 2' in project_assignments:
                week2 = project_assignments['Week 2']
                project_mappings[project_name]['Proposed_DS_Week2'] = week2.get('DS', "")
                project_mappings[project_name]['Proposed_DE_Week2'] = week2.get('DE', "")
    
    return project_mappings


def create_staffing_summary(
    assignments: Dict[str, Dict[str, Dict[str, List[str]]]],
    resourcing_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a summary table showing staff assignments by person.
    
    Args:
        assignments: Assignment dictionary
        resourcing_df: Original resourcing DataFrame
    
    Returns:
        DataFrame showing each person's assignments across weeks
    """
    # Create a dictionary to track each person's assignments
    person_assignments = {}
    
    # Initialize all people from resourcing data
    for _, person in resourcing_df.iterrows():
        name = person['ResourceName']
        role = person['Role']
        person_assignments[name] = {
            'ResourceName': name,
            'Role': role,
            'Week1_Assignment': "",
            'Week2_Assignment': ""
        }
    
    # Fill in assignments
    for project_name, weeks in assignments.items():
        for week, roles in weeks.items():
            week_key = 'Week1_Assignment' if week == 'Week 1' else 'Week2_Assignment'
            
            for role, staff_list in roles.items():
                for staff_name in staff_list:
                    if staff_name in person_assignments:
                        person_assignments[staff_name][week_key] = project_name
    
    # Convert to DataFrame
    summary_df = pd.DataFrame(list(person_assignments.values()))
    
    # Sort by ResourceName for consistent output
    summary_df = summary_df.sort_values('ResourceName').reset_index(drop=True)
    
    return summary_df


def generate_assignment_statistics(
    assignments: Dict[str, Dict[str, Dict[str, List[str]]]],
    projects_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Generate statistics about the assignments.
    
    Args:
        assignments: Assignment dictionary
        projects_df: Projects DataFrame
    
    Returns:
        Dictionary containing assignment statistics
    """
    # Calculate total needs
    total_needs = {
        'Week1_DS': 0,
        'Week1_DE': 0,
        'Week2_DS': 0,
        'Week2_DE': 0
    }
    
    # Calculate total assigned
    total_assigned = {
        'Week1_DS': 0,
        'Week1_DE': 0,
        'Week2_DS': 0,
        'Week2_DE': 0
    }
    
    # Count needs from projects
    for _, project in projects_df.iterrows():
        if project.get('Starts_Week1', False):
            total_needs['Week1_DS'] += int(project.get('Week1_DS_Needed', 0))
            total_needs['Week1_DE'] += int(project.get('Week1_DE_Needed', 0))
        
        if project.get('Starts_Week2', False):
            total_needs['Week2_DS'] += int(project.get('Week2_DS_Needed', 0))
            total_needs['Week2_DE'] += int(project.get('Week2_DE_Needed', 0))
    
    # Count assignments
    for project_name, weeks in assignments.items():
        for week, roles in weeks.items():
            week_prefix = 'Week1' if week == 'Week 1' else 'Week2'
            
            for role, staff_list in roles.items():
                key = f'{week_prefix}_{role}'
                if key in total_assigned:
                    total_assigned[key] += len(staff_list)
    
    # Calculate shortages
    shortages_by_role_week = {}
    for key in total_needs.keys():
        shortage = max(0, total_needs[key] - total_assigned[key])
        shortages_by_role_week[key] = shortage
    
    return {
        'total_needs': total_needs,
        'total_assigned': total_assigned,
        'shortages_by_role_week': shortages_by_role_week,
        'total_shortage': sum(shortages_by_role_week.values()),
        'assignment_rate': {
            key: (total_assigned[key] / total_needs[key] * 100) if total_needs[key] > 0 else 100.0
            for key in total_needs.keys()
        }
    }


def format_proposed_assignments(
    project_assignments: Dict[str, Dict[str, str]]
) -> Dict[str, List[str]]:
    """
    Format project assignments into the 4 proposed columns format.
    
    Args:
        project_assignments: Project-specific assignments
    
    Returns:
        Dictionary with formatted assignments for each proposed column
    """
    # This function is used internally by extend_projects_table
    # Implementation is already handled in the main flow
    pass


def validate_assignment_completeness(
    extended_df: pd.DataFrame,
    projects_df: pd.DataFrame
) -> Tuple[bool, List[str]]:
    """
    Validate that all required roles have been assigned.
    
    Args:
        extended_df: Extended DataFrame with proposed assignments
        projects_df: Original projects DataFrame
    
    Returns:
        Tuple of (all_assigned, list_of_unassigned_roles)
    """
    unassigned = []
    
    for idx, row in extended_df.iterrows():
        project_name = row['Project']
        
        # Check Week 1 assignments
        if row.get('Starts_Week1', False):
            week1_ds_needed = int(row.get('Week1_DS_Needed', 0))
            week1_de_needed = int(row.get('Week1_DE_Needed', 0))
            
            week1_ds_assigned = len(row['Proposed_DS_Week1'].split(',')) if row['Proposed_DS_Week1'] else 0
            week1_de_assigned = len(row['Proposed_DE_Week1'].split(',')) if row['Proposed_DE_Week1'] else 0
            
            if week1_ds_assigned < week1_ds_needed:
                unassigned.append(f"{project_name} Week 1 DS: needed {week1_ds_needed}, assigned {week1_ds_assigned}")
            
            if week1_de_assigned < week1_de_needed:
                unassigned.append(f"{project_name} Week 1 DE: needed {week1_de_needed}, assigned {week1_de_assigned}")
        
        # Check Week 2 assignments
        if row.get('Starts_Week2', False):
            week2_ds_needed = int(row.get('Week2_DS_Needed', 0))
            week2_de_needed = int(row.get('Week2_DE_Needed', 0))
            
            week2_ds_assigned = len(row['Proposed_DS_Week2'].split(',')) if row['Proposed_DS_Week2'] else 0
            week2_de_assigned = len(row['Proposed_DE_Week2'].split(',')) if row['Proposed_DE_Week2'] else 0
            
            if week2_ds_assigned < week2_ds_needed:
                unassigned.append(f"{project_name} Week 2 DS: needed {week2_ds_needed}, assigned {week2_ds_assigned}")
            
            if week2_de_assigned < week2_de_needed:
                unassigned.append(f"{project_name} Week 2 DE: needed {week2_de_needed}, assigned {week2_de_assigned}")
    
    return len(unassigned) == 0, unassigned


def create_unassigned_roles_report(
    projects_df: pd.DataFrame,
    extended_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a report of any unassigned roles.
    
    Args:
        projects_df: Original projects DataFrame
        extended_df: Extended DataFrame with assignments
    
    Returns:
        DataFrame listing unassigned roles by project and week
    """
    is_complete, unassigned_list = validate_assignment_completeness(extended_df, projects_df)
    
    if is_complete:
        # Return empty DataFrame if all roles are assigned
        return pd.DataFrame(columns=['Project', 'Week', 'Role', 'Needed', 'Assigned', 'Shortage'])
    
    # Parse unassigned list into structured data
    unassigned_data = []
    for item in unassigned_list:
        # Parse format: "ProjectName Week X Role: needed Y, assigned Z"
        parts = item.split(': needed ')
        if len(parts) == 2:
            project_week_role = parts[0]
            needed_assigned = parts[1]
            
            # Extract project, week, role
            project_parts = project_week_role.split(' Week ')
            if len(project_parts) == 2:
                project = project_parts[0]
                week_role = project_parts[1].split(' ')
                if len(week_role) == 2:
                    week = f"Week {week_role[0]}"
                    role = week_role[1]
                    
                    # Extract needed and assigned counts
                    needed_assigned_parts = needed_assigned.split(', assigned ')
                    if len(needed_assigned_parts) == 2:
                        needed = int(needed_assigned_parts[0])
                        assigned = int(needed_assigned_parts[1])
                        shortage = needed - assigned
                        
                        unassigned_data.append({
                            'Project': project,
                            'Week': week,
                            'Role': role,
                            'Needed': needed,
                            'Assigned': assigned,
                            'Shortage': shortage
                        })
    
    return pd.DataFrame(unassigned_data)


def format_output_for_display(
    extended_df: pd.DataFrame,
    display_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Format the final output for display or export.
    
    Args:
        extended_df: Extended DataFrame with all data
        display_columns: Optional list of columns to include in output
    
    Returns:
        Formatted DataFrame ready for display/export
    """
    if display_columns:
        return extended_df[display_columns].copy()
    else:
        return extended_df.copy()


def create_continuity_report(
    assignments: Dict[str, Dict[str, Dict[str, List[str]]]]
) -> pd.DataFrame:
    """
    Create a report showing continuity between Week 1 and Week 2.
    
    Args:
        assignments: Assignment dictionary
    
    Returns:
        DataFrame showing which staff continue from Week 1 to Week 2
    """
    continuity_data = []
    
    for project_name, weeks in assignments.items():
        week1_assignments = weeks.get('Week 1', {})
        week2_assignments = weeks.get('Week 2', {})
        
        for role in ['DS', 'DE']:
            week1_staff = set(week1_assignments.get(role, []))
            week2_staff = set(week2_assignments.get(role, []))
            
            continuing_staff = week1_staff.intersection(week2_staff)
            new_staff = week2_staff - week1_staff
            dropped_staff = week1_staff - week2_staff
            
            if week1_staff or week2_staff:  # Only include if there are assignments
                continuity_data.append({
                    'Project': project_name,
                    'Role': role,
                    'Week1_Staff': ','.join(sorted(week1_staff)) if week1_staff else '',
                    'Week2_Staff': ','.join(sorted(week2_staff)) if week2_staff else '',
                    'Continuing_Staff': ','.join(sorted(continuing_staff)) if continuing_staff else '',
                    'New_Staff': ','.join(sorted(new_staff)) if new_staff else '',
                    'Dropped_Staff': ','.join(sorted(dropped_staff)) if dropped_staff else ''
                })
    
    return pd.DataFrame(continuity_data)


def format_column_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure consistent column header formatting.
    
    Args:
        df: DataFrame to format
    
    Returns:
        DataFrame with standardized column headers
    """
    formatted_df = df.copy()
    
    # Standardize column names if needed
    column_mapping = {
        'Proposed Week 1 DS': 'Proposed_DS_Week1',
        'Proposed Week 1 DE': 'Proposed_DE_Week1',
        'Proposed Week 2 DS': 'Proposed_DS_Week2',
        'Proposed Week 2 DE': 'Proposed_DE_Week2'
    }
    
    formatted_df = formatted_df.rename(columns=column_mapping)
    
    return formatted_df