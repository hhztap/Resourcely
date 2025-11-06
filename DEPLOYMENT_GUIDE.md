# 🚀 Resourcely Staffing Suggester - Deployment Guide

This guide provides complete instructions for deploying the Resourcely Staffing Suggester as a standalone application that can run without requiring access to the source code or Python development environment.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Running the Application](#running-the-application)
- [Using the Application](#using-the-application)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
- [Updating the Application](#updating-the-application)

## 🚀 Quick Start

### For Windows Users
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Download the deployment package
3. Double-click `run-resourcely.bat`
4. Open your browser to http://localhost:8501

### For Mac/Linux Users
1. Install [Docker](https://www.docker.com/get-started)
2. Download the deployment package
3. Run `./run-resourcely.sh` in terminal
4. Open your browser to http://localhost:8501

## 💻 System Requirements

### Minimum Requirements
- **RAM**: 2GB available memory
- **Storage**: 1GB free disk space
- **Network**: Internet connection for initial setup
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

### Supported Operating Systems
- **Windows**: Windows 10/11 (64-bit)
- **macOS**: macOS 10.14 or later
- **Linux**: Ubuntu 18.04+, CentOS 7+, or equivalent

### Required Software
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (usually included with Docker Desktop)

## 📦 Installation Methods

### Method 1: Docker Containerization (Recommended)

This is the easiest and most reliable deployment method.

#### Step 1: Install Docker

**Windows:**
1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Verify installation by opening Command Prompt and running: `docker --version`

**macOS:**
1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. Drag Docker to Applications folder
3. Launch Docker from Applications
4. Verify installation by opening Terminal and running: `docker --version`

**Linux (Ubuntu/Debian):**
```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install docker.io docker-compose

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
```

#### Step 2: Download Deployment Package

Extract the deployment package to a folder on your computer. The package contains:

```
Resourcely-Deployment/
├── run-resourcely.bat          # Windows run script
├── run-resourcely.sh           # Mac/Linux run script
├── stop-resourcely.bat         # Windows stop script
├── stop-resourcely.sh          # Mac/Linux stop script
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Container definition
├── app.py                      # Streamlit application
├── requirements.txt            # Python dependencies
├── scripts/                    # Application modules
├── Prospective_Projects.csv    # Sample projects data
├── Resourcing_View.csv         # Sample resourcing data
├── output/                     # Results directory
└── DEPLOYMENT_GUIDE.md         # This guide
```

## 🏃‍♂️ Running the Application

### Windows

1. **Navigate to the deployment folder**
2. **Double-click `run-resourcely.bat`**
3. **Wait for the application to start** (first run may take 2-3 minutes)
4. **Open your browser** to http://localhost:8501

The script will:
- Check if Docker is installed
- Build the application container (first run only)
- Start the application
- Automatically open your browser

### Mac/Linux

1. **Open Terminal**
2. **Navigate to the deployment folder:**
   ```bash
   cd /path/to/Resourcely-Deployment
   ```
3. **Make scripts executable (first time only):**
   ```bash
   chmod +x run-resourcely.sh stop-resourcely.sh
   ```
4. **Run the application:**
   ```bash
   ./run-resourcely.sh
   ```
5. **Open your browser** to http://localhost:8501

### Manual Docker Commands

If you prefer to use Docker commands directly:

```bash
# Build and start the application
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## 📊 Using the Application

### 1. Data Input

The application supports two input methods:

**Option A: Use Sample Data**
- Click "Use Existing Files" in the sidebar
- Click "Load Existing Sample Files"
- This loads the included sample data for demonstration

**Option B: Upload Your Own Data**
- Click "Upload Files" in the sidebar
- Upload your Projects CSV and Resourcing CSV files
- Ensure your files match the required format (see below)

### 2. Required Data Format

**Projects CSV Format:**
```csv
Project,UseCase,Starts_Week1,Starts_Week2,Week1_DS_Needed,Week1_DE_Needed,Week2_DS_Needed,Week2_DE_Needed
Loblaw,Shelf Optimization,Yes,Yes,1,0,2,0
Human,Innovation,No,No,0,0,0,0
```

**Resourcing CSV Format:**
```csv
Project,ResourceName,Role,Week1_Occupied,Week2_Occupied
London Drugs,Hasti,DS,No,No
London Drugs,Hinna,DS,Yes,No
Continuum,Tyler,DS,Yes,Yes
```

### 3. Running Assignments

1. **Validate your data** - Check for any validation errors
2. **Click "Run Staff Assignment Algorithm"**
3. **Review results** in the four tabs:
   - **Extended Projects Table**: Original data with proposed assignments
   - **Assignment Statistics**: Metrics and fill rates
   - **Staffing Summary**: Individual staff assignments
   - **Download Results**: Export options

### 4. Downloading Results

- **Extended Projects CSV**: Main results with assignments
- **Staffing Summary**: Individual staff tracking
- **Assignment Statistics**: Metrics and analysis
- **Save to Output Folder**: Saves results locally

## 🔧 Troubleshooting

### Common Issues

#### "Docker is not installed" Error
**Solution:** Install Docker Desktop from https://www.docker.com/products/docker-desktop

#### "Port 8501 is already in use"
**Solution:** 
1. Stop any existing instances: `docker-compose down`
2. Or change the port in `docker-compose.yml`

#### Application won't start
**Solutions:**
1. **Check Docker is running**: Look for Docker icon in system tray
2. **Restart Docker Desktop**
3. **Clear Docker cache**:
   ```bash
   docker system prune -a
   ```
4. **Check available disk space** (need at least 1GB)

#### Browser shows "This site can't be reached"
**Solutions:**
1. **Wait longer** - First startup can take 2-3 minutes
2. **Check the application is running**:
   ```bash
   docker-compose ps
   ```
3. **Try a different browser**
4. **Check firewall settings**

#### File upload errors
**Solutions:**
1. **Check file format** - Must be CSV with correct columns
2. **Check file size** - Keep under 10MB
3. **Remove special characters** from file names
4. **Ensure files are not open** in Excel or other programs

### Getting Help

#### Check Application Logs
```bash
# View current logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f
```

#### Restart the Application
```bash
# Stop the application
docker-compose down

# Start fresh
docker-compose up --build -d
```

#### Reset Everything
```bash
# Stop and remove everything
docker-compose down
docker system prune -a

# Start fresh
docker-compose up --build -d
```

## ⚙️ Advanced Configuration

### Changing the Port

Edit `docker-compose.yml`:
```yaml
services:
  resourcely-app:
    ports:
      - "8502:8501"  # Change 8502 to your desired port
```

### Persistent Data Storage

The `output/` folder is automatically mounted to preserve your results between runs.

### Memory Configuration

For large datasets, increase Docker memory:
1. Open Docker Desktop
2. Go to Settings → Resources
3. Increase Memory to 4GB or more

### Custom Data Location

To use data from a different folder, edit `docker-compose.yml`:
```yaml
volumes:
  - ./output:/app/output
  - /path/to/your/data:/app/data  # Add this line
```

## 🔄 Updating the Application

### Method 1: Replace Files
1. Stop the current application
2. Replace the deployment files with new versions
3. Restart the application

### Method 2: Rebuild Container
```bash
# Stop current version
docker-compose down

# Remove old images
docker rmi resourcely-resourcely-app

# Rebuild and start
docker-compose up --build -d
```

## 🛡️ Security Considerations

### Network Security
- The application runs on localhost by default
- To access from other machines, modify the `docker-compose.yml`
- Consider using a reverse proxy for production deployments

### Data Security
- All data processing happens locally
- No data is sent to external servers
- Results are saved in the local `output/` folder

### File Permissions
- Ensure the `output/` folder is writable
- On Linux/Mac, you may need to adjust permissions:
  ```bash
  chmod 755 output/
  ```

## 📞 Support

### Self-Help Resources
1. **Check this guide** for common solutions
2. **Review application logs** for error details
3. **Verify Docker installation** and status
4. **Test with sample data** to isolate issues

### System Information
When reporting issues, include:
- Operating system and version
- Docker version (`docker --version`)
- Error messages from logs
- Steps to reproduce the problem

---

## 🎯 Summary

The Resourcely Staffing Suggester is now packaged as a self-contained Docker application that:

✅ **Requires no Python knowledge**  
✅ **Includes all dependencies**  
✅ **Works on Windows, Mac, and Linux**  
✅ **Provides sample data for testing**  
✅ **Offers intuitive web interface**  
✅ **Generates downloadable results**  

Simply install Docker, run the provided script, and start using the application in your browser!