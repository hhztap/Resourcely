# 2-Week Staffing Suggester - Streamlit Web App

This is a comprehensive web application built with Streamlit that provides an intuitive interface for the 2-Week Staffing Suggester system.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Required packages (install via pip):
  ```bash
  pip install pandas streamlit
  ```

### Running the App
1. Navigate to the project directory:
   ```bash
   cd /workspaces/Resourcely
   ```

2. Launch the Streamlit app:
   ```bash
   streamlit run app.py
   ```

3. Open your browser and go to the displayed URL (typically `http://localhost:8501`)

## 📋 Features

### 🎯 Core Functionality
- **Smart File Input**: Upload your own CSV files or use existing sample data
- **Real-time Validation**: Instant feedback on data quality and format
- **Intelligent Assignment**: Automated staff assignment with constraint validation
- **Interactive Results**: Explore assignments through multiple views and tables
- **Export Capabilities**: Download results in CSV format

### 📊 User Interface Sections

#### 1. **Data Input (Sidebar)**
- Choose between uploading new files or using existing sample data
- Support for drag-and-drop CSV file uploads
- Automatic file validation and preview

#### 2. **Data Validation**
- Real-time validation of both Projects and Resourcing data
- Clear error messages and validation status
- Interactive data preview tables

#### 3. **Assignment Processing**
- One-click assignment algorithm execution
- Progress indicators and status updates
- Constraint validation with detailed feedback

#### 4. **Results Dashboard**
Four comprehensive tabs for exploring results:

**📋 Extended Projects Table**
- Original project data with 4 new "Proposed" assignment columns
- Color-coded assignments for easy identification
- Full project details with staff assignments

**📊 Assignment Statistics**
- Key metrics: Total shortage, fill rates, people assigned
- Detailed breakdown by role and week
- Visual indicators for assignment success rates

**👥 Staffing Summary**
- Individual staff member assignment tracking
- Utilization rates by role
- Cross-week assignment analysis

**💾 Download Results**
- Download extended projects table as CSV
- Export staffing summary and statistics
- Save results to output directory

## 📁 Required Data Format

### Projects CSV
Must contain these columns:
- `Project`: Project name (unique identifier)
- `UseCase`: Project description
- `Starts_Week1`: Yes/No - whether project starts in Week 1
- `Starts_Week2`: Yes/No - whether project starts in Week 2
- `Week1_DS_Needed`: Number of Data Scientists needed for Week 1
- `Week1_DE_Needed`: Number of Data Engineers needed for Week 1
- `Week2_DS_Needed`: Number of Data Scientists needed for Week 2
- `Week2_DE_Needed`: Number of Data Engineers needed for Week 2

### Resourcing CSV
Must contain these columns:
- `Project`: Project name (for reference)
- `ResourceName`: Staff member name
- `Role`: DS (Data Scientist) or DE (Data Engineer)
- `Week1_Occupied`: Yes/No - whether person is occupied in Week 1
- `Week2_Occupied`: Yes/No - whether person is occupied in Week 2

## 🔧 Algorithm Features

### Smart Assignment Logic
- **Constraint Enforcement**: One person per project per week
- **Role Matching**: DS staff assigned to DS roles, DE staff to DE roles
- **Continuity Preference**: Week 1 assignees preferred for Week 2 on same project
- **Alphabetical Tie-Breaking**: Deterministic results when multiple options exist

### Validation & Quality Assurance
- **Input Validation**: Comprehensive data format and content checking
- **Constraint Validation**: Post-assignment verification of all rules
- **Error Reporting**: Clear, actionable error messages
- **Data Integrity**: Automatic boolean normalization and type checking

## 📈 Sample Data

The app includes sample data files:
- `Prospective_Projects.csv`: Example project requirements
- `Resourcing_View.csv`: Example staff availability

These demonstrate the expected format and can be used to test the application.

## 🛠️ Technical Architecture

### Backend Integration
The Streamlit app integrates seamlessly with existing modules:
- **`scripts/io_utils.py`**: File I/O and validation functions
- **`scripts/assigner.py`**: Core assignment algorithm
- **`scripts/formatting.py`**: Output formatting and statistics

### Session Management
- Persistent data storage across user interactions
- Efficient caching of computation results
- Automatic state management for multi-step workflows

## 🎨 User Experience

### Professional Interface
- Clean, modern design with intuitive navigation
- Responsive layout that works on different screen sizes
- Color-coded status indicators and progress feedback
- Interactive data tables with sorting and filtering

### Error Handling
- Graceful handling of invalid file uploads
- Clear error messages with suggested solutions
- Validation feedback before processing
- Recovery options for failed operations

## 📝 Usage Tips

1. **Start with Sample Data**: Use the existing files to understand the format
2. **Validate Early**: Check data validation before running assignments
3. **Explore Results**: Use all four result tabs to understand the assignments
4. **Download Results**: Save your work using the download options
5. **Iterative Refinement**: Upload new data and re-run as needed

## 🔍 Troubleshooting

### Common Issues
- **File Upload Errors**: Ensure CSV files have the correct column names
- **Validation Failures**: Check for missing data or incorrect formats
- **Assignment Issues**: Verify staff availability matches project needs
- **Download Problems**: Ensure browser allows file downloads

### Getting Help
- Check the validation messages for specific error details
- Use the sample data to verify the expected format
- Review the console output for technical error information

## 🚀 Advanced Features

### Batch Processing
- Process multiple scenarios by uploading different data sets
- Compare results across different staffing configurations
- Export multiple result sets for analysis

### Integration Ready
- Results can be imported into other systems
- CSV format compatible with Excel and other tools
- API-ready architecture for future enhancements

---

**Built with ❤️ using Streamlit and the existing 2-Week Staffing Suggester codebase**