"""
Core assignment algorithm for the 2-Week Staffing Suggester.

This module implements the main assignment logic that handles:
- One person per project per week constraint
- Role matching (DS→DS, DE→DE)
- Continuity preference (Week 1 assignees preferred for Week 2)
- Alphabetical tie-breaking for deterministic results
"""

from typing import Dict, List, Set, Tuple, Optional
import pandas as pd


def assign_staff_to_projects(
    projects_df: pd.DataFrame,
    resourcing_df: pd.DataFrame
) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
    """
    Main assignment algorithm that assigns staff to projects for both weeks.
    
    Args:
        projects_df: DataFrame containing project information with columns:
                    - Project Name, Week 1 DS Role, Week 1 DE Role,
                      Week 2 DS Role, Week 2 DE Role
        resourcing_df: DataFrame containing staff availability with columns:
                      - Name, Role, Week 1 Available, Week 2 Available
    
    Returns:
        Dictionary with structure:
        {
            project_name: {
                'Week 1': {
                    'DS': ['person1', 'person2', ...],
                    'DE': ['person3', 'person4', ...]
                },
                'Week 2': {
                    'DS': ['person1', 'person5', ...],
                    'DE': ['person3', 'person6', ...]
                }
            }
        }
    """
    # Normalize boolean columns first
    from scripts.io_utils import normalize_boolean_columns
    projects_df = normalize_boolean_columns(projects_df, ['Starts_Week1', 'Starts_Week2'])
    resourcing_df = normalize_boolean_columns(resourcing_df, ['Week1_Occupied', 'Week2_Occupied'])
    
    # Initialize assignments dictionary
    assignments = {}
    
    # Track current availability (will be updated as we make assignments)
    current_availability = track_availability(resourcing_df)
    
    # Process each project
    for _, project in projects_df.iterrows():
        project_name = project['Project']
        assignments[project_name] = {'Week 1': {'DS': [], 'DE': []}, 'Week 2': {'DS': [], 'DE': []}}
        
        # Week 1 assignments
        if project['Starts_Week1']:
            week1_needs = {
                'DS': int(project['Week1_DS_Needed']),
                'DE': int(project['Week1_DE_Needed'])
            }
            
            week1_assignments = {}
            for role in ['DS', 'DE']:
                needed = week1_needs[role]
                available = current_availability['Week 1'][role].copy()
                
                # Assign staff alphabetically
                assigned = resolve_ties_alphabetically(available, needed)
                assignments[project_name]['Week 1'][role] = assigned
                week1_assignments[role] = assigned
                
                # Remove assigned staff from Week 1 availability only
                # Staff can work both weeks if available, constraint is per-project-per-week
                for staff in assigned:
                    if staff in current_availability['Week 1'][role]:
                        current_availability['Week 1'][role].remove(staff)
                    # DO NOT remove from Week 2 - staff can work both weeks for different projects
        
        # Week 2 assignments
        if project['Starts_Week2']:
            week2_needs = {
                'DS': int(project['Week2_DS_Needed']),
                'DE': int(project['Week2_DE_Needed'])
            }
            
            # Apply continuity preference if project started in Week 1
            if project['Starts_Week1']:
                week1_project_assignments = assignments[project_name]['Week 1']
                week2_assignments = apply_continuity_preference(
                    week1_project_assignments,
                    week2_needs,
                    current_availability['Week 2']
                )
            else:
                # No continuity preference, just assign from available pool
                week2_assignments = {'DS': [], 'DE': []}
                for role in ['DS', 'DE']:
                    needed = week2_needs[role]
                    available = current_availability['Week 2'][role].copy()
                    assigned = resolve_ties_alphabetically(available, needed)
                    week2_assignments[role] = assigned
            
            # Update assignments and availability
            for role in ['DS', 'DE']:
                assignments[project_name]['Week 2'][role] = week2_assignments[role]
                # Remove assigned staff from availability
                for staff in week2_assignments[role]:
                    if staff in current_availability['Week 2'][role]:
                        current_availability['Week 2'][role].remove(staff)
    
    return assignments


def track_availability(
    resourcing_df: pd.DataFrame,
    assignments: Dict[str, Dict[str, List[str]]] = None
) -> Dict[str, Dict[str, List[str]]]:
    """
    Track and update staff availability based on current assignments.
    
    Args:
        resourcing_df: Original staff availability DataFrame
        assignments: Current assignment dictionary (optional)
    
    Returns:
        Dictionary with structure {week: {role: [available_names]}}
    """
    # Build initial availability from resourcing data
    availability = {}
    
    for week in ['Week 1', 'Week 2']:
        availability[week] = get_available_staff_by_role(resourcing_df, week)
    
    # If assignments provided, remove assigned staff from availability
    if assignments:
        for project_name, project_assignments in assignments.items():
            for week, week_assignments in project_assignments.items():
                if week in availability:
                    for role, assigned_staff in week_assignments.items():
                        if role in availability[week]:
                            # Remove assigned staff from available pool
                            for staff_name in assigned_staff:
                                if staff_name in availability[week][role]:
                                    availability[week][role].remove(staff_name)
    
    return availability


def validate_constraints(
    assignments: Dict[str, Dict[str, Dict[str, List[str]]]],
    resourcing_df: pd.DataFrame
) -> Tuple[bool, List[str]]:
    """
    Validate that all assignment constraints are met.
    
    Args:
        assignments: Assignment dictionary to validate
        resourcing_df: Staff availability DataFrame
    
    Returns:
        Tuple of (is_valid, list_of_constraint_violations)
    """
    violations = []
    
    # Normalize boolean columns
    from scripts.io_utils import normalize_boolean_columns
    resourcing_df = normalize_boolean_columns(resourcing_df, ['Week1_Occupied', 'Week2_Occupied'])
    
    # Track all assignments by person and week
    person_assignments = {}  # {person: {week: [projects]}}
    
    # Collect all assignments
    for project_name, project_assignments in assignments.items():
        for week, week_assignments in project_assignments.items():
            for role, assigned_staff in week_assignments.items():
                for person in assigned_staff:
                    if person not in person_assignments:
                        person_assignments[person] = {'Week 1': [], 'Week 2': []}
                    person_assignments[person][week].append(project_name)
    
    # Check constraint: one project per person per week
    for person, weeks in person_assignments.items():
        for week, projects in weeks.items():
            if len(projects) > 1:
                violations.append(f"{person} assigned to multiple projects in {week}: {', '.join(projects)}")
    
    # Check constraint: assigned people must be available
    for project_name, project_assignments in assignments.items():
        for week, week_assignments in project_assignments.items():
            week_col = 'Week1_Occupied' if week == 'Week 1' else 'Week2_Occupied'
            
            for role, assigned_staff in week_assignments.items():
                for person in assigned_staff:
                    # Find person in resourcing data
                    person_data = resourcing_df[resourcing_df['ResourceName'] == person]
                    
                    if person_data.empty:
                        violations.append(f"{person} assigned to {project_name} {week} but not found in resourcing data")
                        continue
                    
                    person_row = person_data.iloc[0]
                    
                    # Check if person has correct role
                    if person_row['Role'] != role:
                        violations.append(f"{person} assigned as {role} to {project_name} {week} but has role {person_row['Role']}")
                    
                    # Check if person is available (not occupied)
                    if person_row[week_col] == True:
                        violations.append(f"{person} assigned to {project_name} {week} but is occupied")
    
    return len(violations) == 0, violations


def apply_continuity_preference(
    week1_assignments: Dict[str, List[str]],
    week2_requirements: Dict[str, int],
    available_staff: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    Apply continuity preference for Week 2 assignments.
    
    Prioritizes Week 1 assignees for Week 2 roles when possible.
    
    Args:
        week1_assignments: Week 1 role assignments
        week2_requirements: Week 2 role requirements count
        available_staff: Available staff by role for Week 2
    
    Returns:
        Week 2 assignments with continuity preference applied
    """
    week2_assignments = {'DS': [], 'DE': []}
    
    for role in ['DS', 'DE']:
        needed = week2_requirements.get(role, 0)
        if needed <= 0:
            continue
            
        available_for_role = available_staff.get(role, []).copy()
        week1_assigned = week1_assignments.get(role, [])
        
        # First priority: Week 1 assignees who are still available
        continuing_staff = []
        for staff in week1_assigned:
            if staff in available_for_role:
                continuing_staff.append(staff)
                available_for_role.remove(staff)
        
        # Sort continuing staff alphabetically and take what we need
        continuing_staff = resolve_ties_alphabetically(continuing_staff, needed)
        week2_assignments[role].extend(continuing_staff)
        
        # If we still need more staff, fill from remaining available
        remaining_needed = needed - len(continuing_staff)
        if remaining_needed > 0:
            additional_staff = resolve_ties_alphabetically(available_for_role, remaining_needed)
            week2_assignments[role].extend(additional_staff)
    
    return week2_assignments


def resolve_ties_alphabetically(
    candidates: List[str],
    required_count: int
) -> List[str]:
    """
    Resolve assignment ties using alphabetical ordering.
    
    Args:
        candidates: List of candidate staff names
        required_count: Number of staff needed
    
    Returns:
        Alphabetically sorted list of selected staff
    """
    if not candidates:
        return []
    
    # Sort alphabetically and take the required count
    sorted_candidates = sorted(candidates)
    return sorted_candidates[:required_count]


def get_available_staff_by_role(
    resourcing_df: pd.DataFrame,
    week: str
) -> Dict[str, List[str]]:
    """
    Get available staff grouped by role for a specific week.
    
    Args:
        resourcing_df: Staff availability DataFrame
        week: 'Week 1' or 'Week 2'
    
    Returns:
        Dictionary mapping role to list of available staff names
    """
    # Map week names to column names
    week_col_map = {
        'Week 1': 'Week1_Occupied',
        'Week 2': 'Week2_Occupied'
    }
    
    if week not in week_col_map:
        return {'DS': [], 'DE': []}
    
    occupied_col = week_col_map[week]
    
    # Filter for available staff (not occupied)
    available_staff = resourcing_df[resourcing_df[occupied_col] == False]
    
    # Group by role and get names
    result = {'DS': [], 'DE': []}
    
    for role in ['DS', 'DE']:
        role_staff = available_staff[available_staff['Role'] == role]
        result[role] = sorted(role_staff['ResourceName'].tolist())
    
    return result


def calculate_role_requirements(
    projects_df: pd.DataFrame,
    week: str
) -> Dict[str, int]:
    """
    Calculate total role requirements for a specific week.
    
    Args:
        projects_df: Project requirements DataFrame
        week: 'Week 1' or 'Week 2'
    
    Returns:
        Dictionary mapping role to required count
    """
    # Map week names to column prefixes
    week_col_map = {
        'Week 1': 'Week1',
        'Week 2': 'Week2'
    }
    
    if week not in week_col_map:
        return {'DS': 0, 'DE': 0}
    
    week_prefix = week_col_map[week]
    starts_col = f'Starts_{week_prefix}'
    ds_col = f'{week_prefix}_DS_Needed'
    de_col = f'{week_prefix}_DE_Needed'
    
    # Filter projects that start in this week
    active_projects = projects_df[projects_df[starts_col] == True]
    
    # Sum requirements
    total_ds = active_projects[ds_col].sum() if not active_projects.empty else 0
    total_de = active_projects[de_col].sum() if not active_projects.empty else 0
    
    return {'DS': int(total_ds), 'DE': int(total_de)}