"""
Comprehensive Streamlit App for 2-Week Staffing Suggester

This app provides a web interface for the staffing assignment system that:
- Allows file upload or selection of existing CSV files
- Validates input data with real-time feedback
- Runs the assignment algorithm
- Displays results with interactive tables
- Provides download functionality for results
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import io

# Add the project root to Python path for imports
sys.path.append('.')

# Import existing functions from scripts
from scripts.io_utils import (
    load_csv_file, validate_projects_csv, validate_resourcing_csv,
    save_csv_file, normalize_boolean_columns
)
from scripts.assigner import assign_staff_to_projects, validate_constraints
from scripts.formatting import (
    extend_projects_table, generate_assignment_statistics, create_staffing_summary
)

# Page configuration
st.set_page_config(
    page_title="2-Week Staffing Suggester",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    st.title("👥 2-Week Staffing Suggester")
    st.markdown("---")
    
    # Initialize session state
    if 'projects_df' not in st.session_state:
        st.session_state.projects_df = None
    if 'resourcing_df' not in st.session_state:
        st.session_state.resourcing_df = None
    if 'assignments' not in st.session_state:
        st.session_state.assignments = None
    if 'extended_df' not in st.session_state:
        st.session_state.extended_df = None
    
    # Sidebar for file input
    with st.sidebar:
        st.header("📁 Data Input")
        file_input_section()
    
    # Main content area
    if st.session_state.projects_df is not None and st.session_state.resourcing_df is not None:
        # Data validation section
        validation_section()
        
        # Assignment processing section
        if st.button("🚀 Run Staff Assignment Algorithm", type="primary", use_container_width=True):
            with st.spinner("Running assignment algorithm..."):
                run_assignment_algorithm()
        
        # Results section
        if st.session_state.assignments is not None:
            results_section()
    else:
        # Welcome section when no data is loaded
        welcome_section()

def file_input_section():
    """Handle file input options in sidebar"""
    st.subheader("Choose Input Method")
    
    input_method = st.radio(
        "Select how to provide CSV files:",
        ["Upload Files", "Use Existing Files"],
        help="Upload new CSV files or use the existing sample files in the project"
    )
    
    if input_method == "Upload Files":
        handle_file_upload()
    else:
        handle_existing_files()

def handle_file_upload():
    """Handle CSV file uploads"""
    st.markdown("### Upload CSV Files")
    
    # Projects file upload
    projects_file = st.file_uploader(
        "Upload Projects CSV",
        type=['csv'],
        help="CSV file containing project information with columns: Project, UseCase, Starts_Week1, Starts_Week2, etc.",
        key="projects_upload"
    )
    
    # Resourcing file upload
    resourcing_file = st.file_uploader(
        "Upload Resourcing CSV",
        type=['csv'],
        help="CSV file containing staff availability with columns: Project, ResourceName, Role, Week1_Occupied, Week2_Occupied",
        key="resourcing_upload"
    )
    
    if projects_file is not None and resourcing_file is not None:
        try:
            # Load uploaded files
            st.session_state.projects_df = pd.read_csv(projects_file)
            st.session_state.resourcing_df = pd.read_csv(resourcing_file)
            
            st.success("✅ Files uploaded successfully!")
            
            # Display basic info about uploaded files
            st.info(f"📊 Projects: {st.session_state.projects_df.shape[0]} rows, {st.session_state.projects_df.shape[1]} columns")
            st.info(f"👥 Resourcing: {st.session_state.resourcing_df.shape[0]} rows, {st.session_state.resourcing_df.shape[1]} columns")
            
        except Exception as e:
            st.error(f"❌ Error loading uploaded files: {str(e)}")
            st.session_state.projects_df = None
            st.session_state.resourcing_df = None

def handle_existing_files():
    """Handle selection of existing CSV files"""
    st.markdown("### Use Existing Files")
    
    # Check if existing files are available
    projects_file_path = "Prospective_Projects.csv"
    resourcing_file_path = "Resourcing_View.csv"
    
    projects_exists = Path(projects_file_path).exists()
    resourcing_exists = Path(resourcing_file_path).exists()
    
    if projects_exists and resourcing_exists:
        if st.button("📂 Load Existing Sample Files", use_container_width=True):
            try:
                st.session_state.projects_df = load_csv_file(projects_file_path)
                st.session_state.resourcing_df = load_csv_file(resourcing_file_path)
                
                st.success("✅ Sample files loaded successfully!")
                st.info(f"📊 Projects: {st.session_state.projects_df.shape[0]} rows, {st.session_state.projects_df.shape[1]} columns")
                st.info(f"👥 Resourcing: {st.session_state.resourcing_df.shape[0]} rows, {st.session_state.resourcing_df.shape[1]} columns")
                
            except Exception as e:
                st.error(f"❌ Error loading existing files: {str(e)}")
                st.session_state.projects_df = None
                st.session_state.resourcing_df = None
    else:
        st.warning("⚠️ Sample files not found in project directory")
        missing_files = []
        if not projects_exists:
            missing_files.append(projects_file_path)
        if not resourcing_exists:
            missing_files.append(resourcing_file_path)
        st.write("Missing files:", missing_files)

def welcome_section():
    """Display welcome information when no data is loaded"""
    st.markdown("""
    ## Welcome to the 2-Week Staffing Suggester! 👋
    
    This application helps you assign staff to projects across two weeks while respecting constraints and preferences.
    
    ### 🎯 Key Features:
    - **Smart Assignment Algorithm**: Automatically assigns staff based on availability and role requirements
    - **Constraint Validation**: Ensures no person is assigned to multiple projects in the same week
    - **Continuity Preference**: Prioritizes keeping the same staff on projects across weeks
    - **Interactive Results**: View assignments, statistics, and staffing summaries
    - **Export Functionality**: Download results as CSV files
    
    ### 📋 Required Data Format:
    
    **Projects CSV should contain:**
    - `Project`: Project name
    - `UseCase`: Project description
    - `Starts_Week1`, `Starts_Week2`: Yes/No for each week
    - `Week1_DS_Needed`, `Week1_DE_Needed`: Number of Data Scientists/Engineers needed for Week 1
    - `Week2_DS_Needed`, `Week2_DE_Needed`: Number of Data Scientists/Engineers needed for Week 2
    
    **Resourcing CSV should contain:**
    - `Project`: Project name (for reference)
    - `ResourceName`: Staff member name
    - `Role`: DS (Data Scientist) or DE (Data Engineer)
    - `Week1_Occupied`, `Week2_Occupied`: Yes/No for availability
    
    ### 🚀 Getting Started:
    1. Use the sidebar to upload your CSV files or load the sample data
    2. Review the data validation results
    3. Run the assignment algorithm
    4. Explore the results and download the output
    """)

def validation_section():
    """Display data validation results with editable tables"""
    st.header("🔍 Data Validation & Editing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Projects Data")
        
        # Editable projects data
        with st.expander("Edit Projects Data", expanded=True):
            # Configure column types for better editing experience
            column_config = {
                "Project": st.column_config.TextColumn("Project", required=True),
                "UseCase": st.column_config.TextColumn("Use Case", required=True),
                "Starts_Week1": st.column_config.SelectboxColumn(
                    "Starts Week 1",
                    options=["Yes", "No"],
                    required=True
                ),
                "Starts_Week2": st.column_config.SelectboxColumn(
                    "Starts Week 2",
                    options=["Yes", "No"],
                    required=True
                ),
                "Week1_DS_Needed": st.column_config.NumberColumn(
                    "Week 1 DS Needed",
                    min_value=0,
                    max_value=10,
                    step=1,
                    required=True
                ),
                "Week1_DE_Needed": st.column_config.NumberColumn(
                    "Week 1 DE Needed",
                    min_value=0,
                    max_value=10,
                    step=1,
                    required=True
                ),
                "Week2_DS_Needed": st.column_config.NumberColumn(
                    "Week 2 DS Needed",
                    min_value=0,
                    max_value=10,
                    step=1,
                    required=True
                ),
                "Week2_DE_Needed": st.column_config.NumberColumn(
                    "Week 2 DE Needed",
                    min_value=0,
                    max_value=10,
                    step=1,
                    required=True
                )
            }
            
            edited_projects = st.data_editor(
                st.session_state.projects_df,
                column_config=column_config,
                use_container_width=True,
                num_rows="dynamic",
                key="projects_editor"
            )
            
            # Save button for projects
            if st.button("💾 Save Projects Changes", key="save_projects"):
                if save_projects_data(edited_projects):
                    st.session_state.projects_df = edited_projects
                    st.success("✅ Projects data saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save projects data")
        
        # Validate projects data
        try:
            is_valid, errors = validate_projects_csv(edited_projects)
            if is_valid:
                st.success("✅ Projects data is valid!")
            else:
                st.error("❌ Projects data validation failed:")
                for error in errors:
                    st.write(f"• {error}")
        except Exception as e:
            st.error(f"❌ Error validating projects data: {str(e)}")
    
    with col2:
        st.subheader("👥 Resourcing Data")
        
        # Editable resourcing data
        with st.expander("Edit Resourcing Data", expanded=True):
            # Configure column types for better editing experience
            column_config = {
                "Project": st.column_config.TextColumn("Project", required=True),
                "ResourceName": st.column_config.TextColumn("Resource Name", required=True),
                "Role": st.column_config.SelectboxColumn(
                    "Role",
                    options=["DS", "DE"],
                    required=True
                ),
                "Week1_Occupied": st.column_config.SelectboxColumn(
                    "Week 1 Occupied",
                    options=["Yes", "No"],
                    required=True
                ),
                "Week2_Occupied": st.column_config.SelectboxColumn(
                    "Week 2 Occupied",
                    options=["Yes", "No"],
                    required=True
                )
            }
            
            edited_resourcing = st.data_editor(
                st.session_state.resourcing_df,
                column_config=column_config,
                use_container_width=True,
                num_rows="dynamic",
                key="resourcing_editor"
            )
            
            # Save button for resourcing
            if st.button("💾 Save Resourcing Changes", key="save_resourcing"):
                if save_resourcing_data(edited_resourcing):
                    st.session_state.resourcing_df = edited_resourcing
                    st.success("✅ Resourcing data saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save resourcing data")
        
        # Validate resourcing data
        try:
            is_valid, errors = validate_resourcing_csv(edited_resourcing)
            if is_valid:
                st.success("✅ Resourcing data is valid!")
            else:
                st.error("❌ Resourcing data validation failed:")
                for error in errors:
                    st.write(f"• {error}")
        except Exception as e:
            st.error(f"❌ Error validating resourcing data: {str(e)}")

def save_projects_data(df):
    """Save edited projects data to CSV file"""
    try:
        # Validate the data before saving
        is_valid, errors = validate_projects_csv(df)
        if not is_valid:
            st.error("Cannot save invalid data:")
            for error in errors:
                st.write(f"• {error}")
            return False
        
        # Save to CSV file
        success = save_csv_file(df, 'Prospective_Projects.csv')
        return success
    except Exception as e:
        st.error(f"Error saving projects data: {str(e)}")
        return False

def save_resourcing_data(df):
    """Save edited resourcing data to CSV file"""
    try:
        # Validate the data before saving
        is_valid, errors = validate_resourcing_csv(df)
        if not is_valid:
            st.error("Cannot save invalid data:")
            for error in errors:
                st.write(f"• {error}")
            return False
        
        # Save to CSV file
        success = save_csv_file(df, 'Resourcing_View.csv')
        return success
    except Exception as e:
        st.error(f"Error saving resourcing data: {str(e)}")
        return False

def run_assignment_algorithm():
    """Execute the staff assignment algorithm"""
    try:
        # Run the assignment algorithm
        st.session_state.assignments = assign_staff_to_projects(
            st.session_state.projects_df, 
            st.session_state.resourcing_df
        )
        
        # Validate constraints
        is_valid, violations = validate_constraints(
            st.session_state.assignments, 
            st.session_state.resourcing_df
        )
        
        # Generate extended table with results
        st.session_state.extended_df = extend_projects_table(
            st.session_state.projects_df, 
            st.session_state.assignments
        )
        
        # Display success message
        if is_valid:
            st.success("✅ Assignment completed successfully! All constraints satisfied.")
        else:
            st.warning("⚠️ Assignment completed with constraint violations:")
            for violation in violations:
                st.write(f"• {violation}")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error running assignment algorithm: {str(e)}")
        st.session_state.assignments = None
        st.session_state.extended_df = None

def results_section():
    """Display assignment results"""
    st.header("📈 Assignment Results")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Extended Projects Table", "📊 Assignment Statistics", "👥 Staffing Summary", "💾 Download Results"])
    
    with tab1:
        display_extended_table()
    
    with tab2:
        display_assignment_statistics()
    
    with tab3:
        display_staffing_summary()
    
    with tab4:
        display_download_section()

def display_extended_table():
    """Display the extended projects table with assignments - now editable"""
    st.subheader("📋 Projects with Proposed Assignments")
    
    if st.session_state.extended_df is not None:
        # Editable extended table
        st.markdown("### ✏️ Edit Extended Projects Table")
        
        # Configure column types for better editing experience
        column_config = {}
        
        # Configure original project columns
        for col in st.session_state.extended_df.columns:
            if col == "Project":
                column_config[col] = st.column_config.TextColumn("Project", disabled=True)
            elif col == "UseCase":
                column_config[col] = st.column_config.TextColumn("Use Case", disabled=True)
            elif col in ["Starts_Week1", "Starts_Week2"]:
                column_config[col] = st.column_config.SelectboxColumn(
                    col.replace("_", " "),
                    options=["Yes", "No"],
                    disabled=True
                )
            elif "Needed" in col:
                column_config[col] = st.column_config.NumberColumn(
                    col.replace("_", " "),
                    min_value=0,
                    max_value=10,
                    step=1,
                    disabled=True
                )
            elif col.startswith("Proposed_"):
                # Make assignment columns editable
                column_config[col] = st.column_config.TextColumn(
                    col.replace("_", " ").replace("Proposed ", ""),
                    help="Enter staff names separated by commas (e.g., 'John,Jane')"
                )
        
        edited_extended = st.data_editor(
            st.session_state.extended_df,
            column_config=column_config,
            use_container_width=True,
            key="extended_editor"
        )
        
        # Save button for extended table
        if st.button("💾 Save Extended Table Changes", key="save_extended"):
            if save_extended_data(edited_extended):
                st.session_state.extended_df = edited_extended
                st.success("✅ Extended table data saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save extended table data")
        
    else:
        st.error("❌ No extended table available. Please run the assignment algorithm first.")

def display_assignment_statistics():
    """Display assignment statistics and metrics"""
    st.subheader("📊 Assignment Statistics")
    
    if st.session_state.assignments is not None:
        try:
            # Generate statistics
            stats = generate_assignment_statistics(
                st.session_state.assignments, 
                st.session_state.projects_df
            )
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Shortage", 
                    stats['total_shortage'],
                    help="Total number of unassigned roles across all projects and weeks"
                )
            
            with col2:
                total_needed = sum(stats['total_needs'].values())
                total_assigned = sum(stats['total_assigned'].values())
                overall_rate = (total_assigned / total_needed * 100) if total_needed > 0 else 100
                st.metric(
                    "Overall Fill Rate", 
                    f"{overall_rate:.1f}%",
                    help="Percentage of required roles that were successfully assigned"
                )
            
            with col3:
                st.metric(
                    "Projects Processed", 
                    len(st.session_state.assignments),
                    help="Number of projects processed by the algorithm"
                )
            
            with col4:
                total_people_assigned = len(set(
                    person for project in st.session_state.assignments.values()
                    for week in project.values()
                    for role in week.values()
                    for person in role
                ))
                st.metric(
                    "People Assigned", 
                    total_people_assigned,
                    help="Number of unique people assigned to projects"
                )
            
            # Detailed breakdown
            st.markdown("### 📋 Detailed Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Requirements vs Assignments:**")
                breakdown_data = []
                for key in stats['total_needs'].keys():
                    week, role = key.split('_', 1)
                    breakdown_data.append({
                        'Week': week.replace('Week', 'Week '),
                        'Role': role,
                        'Needed': stats['total_needs'][key],
                        'Assigned': stats['total_assigned'][key],
                        'Shortage': stats['shortages_by_role_week'][key],
                        'Fill Rate': f"{stats['assignment_rate'][key]:.1f}%"
                    })
                
                breakdown_df = pd.DataFrame(breakdown_data)
                st.dataframe(breakdown_df, use_container_width=True)
            
            with col2:
                st.markdown("**Assignment Rate by Role & Week:**")
                
                # Create a visual representation
                for key, rate in stats['assignment_rate'].items():
                    week, role = key.split('_', 1)
                    label = f"{week.replace('Week', 'Week ')} {role}"
                    
                    # Color based on fill rate
                    if rate >= 100:
                        color = "🟢"
                    elif rate >= 75:
                        color = "🟡"
                    else:
                        color = "🔴"
                    
                    st.write(f"{color} {label}: {rate:.1f}%")
        
        except Exception as e:
            st.error(f"❌ Error generating statistics: {str(e)}")
    else:
        st.error("❌ No assignment data available. Please run the assignment algorithm first.")

def display_staffing_summary():
    """Display staffing summary by person"""
    st.subheader("👥 Staffing Summary")
    
    if st.session_state.assignments is not None:
        try:
            # Generate staffing summary
            staffing_summary = create_staffing_summary(
                st.session_state.assignments, 
                st.session_state.resourcing_df
            )
            
            # Display summary table
            st.dataframe(staffing_summary, use_container_width=True)
            
            # Additional insights
            st.markdown("### 📈 Staffing Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # People with assignments
                assigned_people = staffing_summary[
                    (staffing_summary['Week1_Assignment'] != '') | 
                    (staffing_summary['Week2_Assignment'] != '')
                ]
                
                st.metric(
                    "People with Assignments", 
                    len(assigned_people),
                    help="Number of people assigned to at least one project"
                )
                
                # People working both weeks
                both_weeks = staffing_summary[
                    (staffing_summary['Week1_Assignment'] != '') & 
                    (staffing_summary['Week2_Assignment'] != '')
                ]
                
                st.metric(
                    "Working Both Weeks", 
                    len(both_weeks),
                    help="Number of people assigned to projects in both weeks"
                )
            
            with col2:
                # Utilization by role
                st.markdown("**Utilization by Role:**")
                
                for role in ['DS', 'DE']:
                    role_people = staffing_summary[staffing_summary['Role'] == role]
                    role_assigned = role_people[
                        (role_people['Week1_Assignment'] != '') | 
                        (role_people['Week2_Assignment'] != '')
                    ]
                    
                    if len(role_people) > 0:
                        utilization = len(role_assigned) / len(role_people) * 100
                        st.write(f"• {role}: {utilization:.1f}% ({len(role_assigned)}/{len(role_people)})")
                    else:
                        st.write(f"• {role}: No staff available")
        
        except Exception as e:
            st.error(f"❌ Error generating staffing summary: {str(e)}")
    else:
        st.error("❌ No assignment data available. Please run the assignment algorithm first.")

def display_download_section():
    """Display download options for results"""
    st.subheader("💾 Download Results")
    
    if st.session_state.extended_df is not None:
        # Main results download
        st.markdown("### 📋 Extended Projects Table")
        
        # Convert DataFrame to CSV
        csv_buffer = io.StringIO()
        st.session_state.extended_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Extended Projects CSV",
            data=csv_data,
            file_name="Prospective_Projects_with_Assignments.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Additional downloads
        if st.session_state.assignments is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                # Staffing summary download
                try:
                    staffing_summary = create_staffing_summary(
                        st.session_state.assignments, 
                        st.session_state.resourcing_df
                    )
                    
                    staffing_csv = io.StringIO()
                    staffing_summary.to_csv(staffing_csv, index=False)
                    staffing_data = staffing_csv.getvalue()
                    
                    st.download_button(
                        label="👥 Download Staffing Summary",
                        data=staffing_data,
                        file_name="Staffing_Summary.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error preparing staffing summary: {str(e)}")
            
            with col2:
                # Statistics download
                try:
                    stats = generate_assignment_statistics(
                        st.session_state.assignments, 
                        st.session_state.projects_df
                    )
                    
                    # Convert stats to DataFrame for download
                    stats_data = []
                    for key, value in stats['total_needs'].items():
                        week, role = key.split('_', 1)
                        stats_data.append({
                            'Week': week.replace('Week', 'Week '),
                            'Role': role,
                            'Needed': stats['total_needs'][key],
                            'Assigned': stats['total_assigned'][key],
                            'Shortage': stats['shortages_by_role_week'][key],
                            'Fill_Rate_Percent': stats['assignment_rate'][key]
                        })
                    
                    stats_df = pd.DataFrame(stats_data)
                    stats_csv = io.StringIO()
                    stats_df.to_csv(stats_csv, index=False)
                    stats_csv_data = stats_csv.getvalue()
                    
                    st.download_button(
                        label="📊 Download Statistics",
                        data=stats_csv_data,
                        file_name="Assignment_Statistics.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error preparing statistics: {str(e)}")
        
        # Save to output directory option
        st.markdown("### 💾 Save to Output Directory")
        
        if st.button("💾 Save Results to Output Folder", use_container_width=True):
            try:
                success = save_csv_file(
                    st.session_state.extended_df, 
                    'output/Prospective_Projects_with_Assignments.csv'
                )
                
                if success:
                    st.success("✅ Results saved to output/Prospective_Projects_with_Assignments.csv")
                else:
                    st.error("❌ Failed to save results to output directory")
            except Exception as e:
                st.error(f"❌ Error saving to output directory: {str(e)}")
    
    else:
        st.error("❌ No results available for download. Please run the assignment algorithm first.")

if __name__ == "__main__":
    main()