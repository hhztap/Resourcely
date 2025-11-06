"""
CSV input/output utilities for the 2-Week Staffing Suggester.

This module handles:
- Loading and validating CSV files
- Data normalization (Yes/No to boolean conversion)
- Input validation (mandatory fields, data types)
- Duplicate detection and error handling
- CSV export functionality
"""

from typing import List, Dict, Tuple, Optional, Any
import pandas as pd
from pathlib import Path


def load_csv_file(file_path: str) -> pd.DataFrame:
    """
    Load a CSV file and return as DataFrame.
    
    Args:
        file_path: Path to the CSV file
    
    Returns:
        DataFrame containing the CSV data
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.EmptyDataError: If the file is empty
        pd.errors.ParserError: If the file format is invalid
    """
    try:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        df = pd.read_csv(file_path)
        
        if df.empty:
            raise pd.errors.EmptyDataError(f"File is empty: {file_path}")
        
        return df
    
    except pd.errors.EmptyDataError:
        raise
    except pd.errors.ParserError as e:
        raise pd.errors.ParserError(f"Invalid CSV format in {file_path}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error loading CSV file {file_path}: {str(e)}")


def validate_projects_csv(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate the projects CSV structure and content.
    
    Expected columns:
    - Project, UseCase, Starts_Week1, Starts_Week2
    - Week1_DS_Needed, Week1_DE_Needed, Week2_DS_Needed, Week2_DE_Needed (optional)
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Tuple of (is_valid, list_of_validation_errors)
    """
    errors = []
    
    # Required columns
    required_columns = ['Project', 'UseCase', 'Starts_Week1', 'Starts_Week2']
    optional_columns = ['Week1_DS_Needed', 'Week1_DE_Needed', 'Week2_DS_Needed', 'Week2_DE_Needed']
    
    # Check mandatory fields
    is_mandatory_valid, mandatory_errors = check_mandatory_fields(df, required_columns)
    errors.extend(mandatory_errors)
    
    # Add missing optional columns with default value 0
    df_copy = df.copy()
    for col in optional_columns:
        if col not in df_copy.columns:
            df_copy[col] = 0
    
    # Validate boolean columns (Starts_Week1, Starts_Week2)
    boolean_columns = ['Starts_Week1', 'Starts_Week2']
    for col in boolean_columns:
        if col in df_copy.columns:
            is_valid, col_errors = validate_availability_values(df_copy, [col])
            if not is_valid:
                errors.extend(col_errors)
    
    # Validate numeric columns (resource needed columns)
    numeric_columns = ['Week1_DS_Needed', 'Week1_DE_Needed', 'Week2_DS_Needed', 'Week2_DE_Needed']
    for col in numeric_columns:
        if col in df_copy.columns:
            try:
                pd.to_numeric(df_copy[col], errors='raise')
            except (ValueError, TypeError):
                errors.append(f"Column '{col}' must contain numeric values")
    
    # Check for duplicate projects
    has_duplicates, duplicate_errors = detect_duplicates(df_copy, ['Project'])
    if has_duplicates:
        errors.extend(duplicate_errors)
    
    return len(errors) == 0, errors


def validate_resourcing_csv(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate the resourcing CSV structure and content.
    
    Expected columns:
    - Project, ResourceName, Role, Week1_Occupied, Week2_Occupied
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Tuple of (is_valid, list_of_validation_errors)
    """
    errors = []
    
    # Required columns
    required_columns = ['Project', 'ResourceName', 'Role', 'Week1_Occupied', 'Week2_Occupied']
    
    # Check mandatory fields
    is_mandatory_valid, mandatory_errors = check_mandatory_fields(df, required_columns)
    errors.extend(mandatory_errors)
    
    # Validate role values
    if 'Role' in df.columns:
        is_role_valid, role_errors = validate_role_values(df, 'Role')
        if not is_role_valid:
            errors.extend(role_errors)
    
    # Validate availability values
    availability_columns = ['Week1_Occupied', 'Week2_Occupied']
    is_availability_valid, availability_errors = validate_availability_values(df, availability_columns)
    if not is_availability_valid:
        errors.extend(availability_errors)
    
    # Check for duplicate resource assignments (same project + resource)
    has_duplicates, duplicate_errors = detect_duplicates(df, ['Project', 'ResourceName'])
    if has_duplicates:
        errors.extend(duplicate_errors)
    
    return len(errors) == 0, errors


def normalize_boolean_columns(
    df: pd.DataFrame,
    boolean_columns: List[str]
) -> pd.DataFrame:
    """
    Convert Yes/No string values to boolean values.
    
    Args:
        df: DataFrame to normalize
        boolean_columns: List of column names to convert
    
    Returns:
        DataFrame with normalized boolean columns
    """
    df_copy = df.copy()
    
    for col in boolean_columns:
        if col in df_copy.columns:
            # Convert to string first to handle mixed types
            df_copy[col] = df_copy[col].astype(str).str.strip()
            
            # Case-insensitive conversion
            df_copy[col] = df_copy[col].str.lower().map({
                'yes': True,
                'no': False,
                'true': True,
                'false': False,
                '1': True,
                '0': False
            })
            
            # Fill any unmapped values with False (or could raise error)
            df_copy[col] = df_copy[col].fillna(False)
    
    return df_copy


def check_mandatory_fields(
    df: pd.DataFrame,
    required_columns: List[str]
) -> Tuple[bool, List[str]]:
    """
    Check that all mandatory fields are present and non-empty.
    
    Args:
        df: DataFrame to check
        required_columns: List of required column names
    
    Returns:
        Tuple of (all_present, list_of_missing_or_empty_fields)
    """
    errors = []
    
    # Check for missing columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    for col in missing_columns:
        errors.append(f"Required column '{col}' is missing")
    
    # Check for empty/null values in existing required columns
    for col in required_columns:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            empty_count = (df[col].astype(str).str.strip() == '').sum()
            
            if null_count > 0:
                errors.append(f"Column '{col}' has {null_count} null values")
            if empty_count > 0:
                errors.append(f"Column '{col}' has {empty_count} empty values")
    
    return len(errors) == 0, errors


def validate_data_types(
    df: pd.DataFrame,
    column_types: Dict[str, type]
) -> Tuple[bool, List[str]]:
    """
    Validate that columns have the expected data types.
    
    Args:
        df: DataFrame to validate
        column_types: Dictionary mapping column names to expected types
    
    Returns:
        Tuple of (types_valid, list_of_type_errors)
    """
    errors = []
    
    for col, expected_type in column_types.items():
        if col not in df.columns:
            errors.append(f"Column '{col}' not found for type validation")
            continue
        
        try:
            if expected_type == bool:
                # For boolean, check if values can be converted to bool
                test_series = df[col].astype(str).str.lower()
                valid_bool_values = {'yes', 'no', 'true', 'false', '1', '0'}
                invalid_values = test_series[~test_series.isin(valid_bool_values)]
                if not invalid_values.empty:
                    errors.append(f"Column '{col}' contains invalid boolean values: {invalid_values.unique().tolist()}")
            
            elif expected_type in [int, float]:
                # For numeric types, try to convert
                pd.to_numeric(df[col], errors='raise')
            
            elif expected_type == str:
                # String type is generally always valid
                pass
            
        except (ValueError, TypeError) as e:
            errors.append(f"Column '{col}' cannot be converted to {expected_type.__name__}: {str(e)}")
    
    return len(errors) == 0, errors


def detect_duplicates(
    df: pd.DataFrame,
    key_columns: List[str]
) -> Tuple[bool, List[str]]:
    """
    Detect duplicate entries based on key columns.
    
    Args:
        df: DataFrame to check for duplicates
        key_columns: List of columns that should be unique together
    
    Returns:
        Tuple of (has_duplicates, list_of_duplicate_descriptions)
    """
    errors = []
    
    # Check if all key columns exist
    missing_cols = [col for col in key_columns if col not in df.columns]
    if missing_cols:
        errors.append(f"Cannot check duplicates: missing columns {missing_cols}")
        return True, errors
    
    # Find duplicates
    duplicates = df[df.duplicated(subset=key_columns, keep=False)]
    
    if not duplicates.empty:
        # Group duplicates and report them
        for key_values, group in duplicates.groupby(key_columns):
            if len(group) > 1:
                if len(key_columns) == 1:
                    errors.append(f"Duplicate found for {key_columns[0]}: '{key_values}' ({len(group)} occurrences)")
                else:
                    key_str = ', '.join([f"{col}='{val}'" for col, val in zip(key_columns, key_values)])
                    errors.append(f"Duplicate found for combination [{key_str}] ({len(group)} occurrences)")
    
    return len(errors) > 0, errors


def validate_role_values(df: pd.DataFrame, role_column: str) -> Tuple[bool, List[str]]:
    """
    Validate that role values are within expected set (DS, DE).
    
    Args:
        df: DataFrame to validate
        role_column: Name of the role column
    
    Returns:
        Tuple of (roles_valid, list_of_invalid_roles)
    """
    errors = []
    valid_roles = {'DS', 'DE'}
    
    if role_column not in df.columns:
        errors.append(f"Role column '{role_column}' not found")
        return False, errors
    
    # Get unique role values and check against valid set
    unique_roles = set(df[role_column].dropna().astype(str).str.strip().str.upper())
    invalid_roles = unique_roles - valid_roles
    
    if invalid_roles:
        errors.append(f"Invalid role values found: {list(invalid_roles)}. Valid roles are: {list(valid_roles)}")
    
    return len(errors) == 0, errors


def validate_availability_values(
    df: pd.DataFrame,
    availability_columns: List[str]
) -> Tuple[bool, List[str]]:
    """
    Validate that availability values are Yes/No or boolean.
    
    Args:
        df: DataFrame to validate
        availability_columns: List of availability column names
    
    Returns:
        Tuple of (availability_valid, list_of_invalid_values)
    """
    errors = []
    valid_values = {'yes', 'no', 'true', 'false', '1', '0'}
    
    for col in availability_columns:
        if col not in df.columns:
            errors.append(f"Availability column '{col}' not found")
            continue
        
        # Convert to string and normalize case
        col_values = df[col].dropna().astype(str).str.strip().str.lower()
        invalid_values = col_values[~col_values.isin(valid_values)]
        
        if not invalid_values.empty:
            unique_invalid = invalid_values.unique().tolist()
            errors.append(f"Column '{col}' contains invalid availability values: {unique_invalid}. Valid values are: Yes/No, True/False, 1/0")
    
    return len(errors) == 0, errors


def save_csv_file(
    df: pd.DataFrame,
    file_path: str,
    index: bool = False
) -> bool:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        file_path: Output file path
        index: Whether to include row indices
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        PermissionError: If unable to write to the file
        OSError: If there's a filesystem error
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(file_path).parent
        create_output_directory(str(output_dir))
        
        # Save the CSV file
        df.to_csv(file_path, index=index)
        return True
        
    except PermissionError as e:
        raise PermissionError(f"Permission denied writing to {file_path}: {str(e)}")
    except OSError as e:
        raise OSError(f"Filesystem error writing to {file_path}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error saving CSV file {file_path}: {str(e)}")


def create_output_directory(output_path: str) -> bool:
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_path: Path to the output directory
    
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(output_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {output_path}: {str(e)}")
        return False


def validate_file_permissions(file_path: str, mode: str = 'r') -> Tuple[bool, str]:
    """
    Validate file permissions for read/write operations.
    
    Args:
        file_path: Path to the file
        mode: File access mode ('r' for read, 'w' for write)
    
    Returns:
        Tuple of (has_permission, error_message)
    """
    try:
        path = Path(file_path)
        
        if mode == 'r':
            if not path.exists():
                return False, f"File does not exist: {file_path}"
            if not path.is_file():
                return False, f"Path is not a file: {file_path}"
            if not path.stat().st_mode & 0o444:  # Check read permission
                return False, f"No read permission for file: {file_path}"
        
        elif mode == 'w':
            if path.exists():
                if not path.is_file():
                    return False, f"Path exists but is not a file: {file_path}"
                if not path.stat().st_mode & 0o200:  # Check write permission
                    return False, f"No write permission for file: {file_path}"
            else:
                # Check if parent directory is writable
                parent = path.parent
                if not parent.exists():
                    try:
                        parent.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        return False, f"Cannot create parent directory: {str(e)}"
                if not parent.stat().st_mode & 0o200:
                    return False, f"No write permission for directory: {parent}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Error checking file permissions: {str(e)}"