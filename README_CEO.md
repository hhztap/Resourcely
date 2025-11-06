# 👥 Resourcely Staffing Suggester - Quick Start for CEO

## 🚀 One-Click Setup

This application helps you assign staff to projects across two weeks. It's packaged as a self-contained solution that requires no Python knowledge.

### For Windows Users
1. **Install Docker Desktop**: Download from https://www.docker.com/products/docker-desktop
2. **Double-click `run-resourcely.bat`**
3. **Wait 2-3 minutes** for first-time setup
4. **Application opens automatically** in your browser at http://localhost:8501

### For Mac Users  
1. **Install Docker Desktop**: Download from https://www.docker.com/products/docker-desktop
2. **Open Terminal** and navigate to this folder
3. **Run**: `./run-resourcely.sh`
4. **Open browser** to http://localhost:8501

## 📊 Using the Application

### Step 1: Load Data
- Click **"Use Existing Files"** in the sidebar to try with sample data
- Or click **"Upload Files"** to use your own CSV files

### Step 2: Run Assignment
- Click the **"🚀 Run Staff Assignment Algorithm"** button
- Wait for processing to complete

### Step 3: View Results
- Explore the **4 result tabs**:
  - **Extended Projects Table**: Your projects with staff assignments
  - **Assignment Statistics**: Success rates and metrics  
  - **Staffing Summary**: Individual staff tracking
  - **Download Results**: Export your results as CSV files

### Step 4: Download Results
- Click **"📥 Download Extended Projects CSV"** to get your main results
- Results are also saved in the `output/` folder

## 🛑 Stopping the Application

### Windows
- Double-click `stop-resourcely.bat`

### Mac
- Run `./stop-resourcely.sh` in Terminal

## 📋 Data Format Requirements

### Projects CSV
```csv
Project,UseCase,Starts_Week1,Starts_Week2,Week1_DS_Needed,Week1_DE_Needed,Week2_DS_Needed,Week2_DE_Needed
Loblaw,Shelf Optimization,Yes,Yes,1,0,2,0
```

### Resourcing CSV  
```csv
Project,ResourceName,Role,Week1_Occupied,Week2_Occupied
London Drugs,Hasti,DS,No,No
London Drugs,Hinna,DS,Yes,No
```

## 🆘 Need Help?

1. **Check that Docker is running** (look for Docker icon in system tray)
2. **Try the sample data first** to verify everything works
3. **Restart the application** if you encounter issues
4. **See `DEPLOYMENT_GUIDE.md`** for detailed troubleshooting

---

**The application is completely self-contained and runs locally on your machine. No data is sent to external servers.**