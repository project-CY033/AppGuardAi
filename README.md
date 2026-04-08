# AppGuardAi
AppGuardAi uses Artificial Intelligence (AI) and Machine Learning (ML) to automatically scan and compare different applications.

---

# AppGuardAi 

<p align="center">
  <img src="assets/logos/logo.png" width="150" alt="AppGuardAi Logo">
</p>

<p align="center">
  <h2>Ai-Powered Advanced System for Detecting and Mitigating 
Clone and Fake Applications</h2>
</p>

AppGuardAi is a production-level, AI-powered cybersecurity and device optimization application designed to protect mobile ecosystems from evolving threats. By leveraging advanced machine learning algorithms, it provides automated detection of fake apps, cloned applications, and malicious software while optimizing device performance through deep cleaning and speed boosting mechanisms.

---

## 📱 Screenshots

<p align="center">
  <img src="assets/screenshots/dashboard1.jpeg" width="250" alt="Dashboard">
  <img src="assets/screenshots/dashboard2.jpeg" width="250" alt="Dashboard">
</p>

---

## 📑 Table of Contents
- [Introduction](#introduction)
- [Proposed Solution](#proposed-solution)
- [How It Solves the Problem](#how-it-solves-the-problem)
- [Key Features](#key-features)
- [Key Innovations](#key-innovations)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Workflow](#workflow)
- [Installation Guide](#installation-guide)
- [Usage Guide](#usage-guide)
- [About the Developer](#about-the-developer)

---

## 📝 Introduction
In an era of increasing mobile threats, **AppGuardAi** stands as a comprehensive shield for your digital life. It is not just a security scanner; it is a premium device management suite that combines real-time threat intelligence with high-end system optimization tools. Built with a focus on user experience and robust security, it emulates the clean, structured interfaces of modern Android system tools (like MIUI) while providing enterprise-grade analysis.

---

## 💡 Proposed Solution
AppGuardAi uses **Artificial Intelligence (AI)** and **Machine Learning (ML)** to automatically scan and compare different applications. It studies how an app is built, how it behaves, and how its code is written. By doing this, it can easily detect fake, cloned, or harmful apps that try to steal user data or cause damage. The system uses both **Static Analysis** (checking the app without running it) and **Dynamic Analysis** (observing the app while it runs) to find threats in real time.

---

## 🛡️ How It Solves the Problem
- **Automated Detection**: AI algorithms identify clones and modified versions by analyzing APK signatures, API usage, and code flow.
- **Behavioral Analysis**: Monitors runtime behaviors to detect hidden malicious actions or suspicious permission requests.
- **Centralized Threat Database**: Stores detected clone patterns and malware indicators for continuous model improvement and faster future lookups.
- **Cross-Platform Support**: Engineered to work across Android, iOS, Windows, macOS, and Linux applications.

---

## 🚀 Key Features
- **Full System Scan**: Scans all installed applications for malware and security vulnerabilities.
- **Manage Apps**: A native-style app manager to view storage usage, data consumption, and manage app permissions.
- **Deep Clean**: Identifies and removes junk files, cache, and residual data to reclaim storage space.
- **Boost Speed**: Optimizes RAM usage and background processes to enhance device responsiveness.
- **PDF Scan**: Deeply inspects PDF documents for malicious macros, phishing links, and obfuscated scripts.
- **Real-time Alerts**: Pushes immediate notifications when a threat is detected or a system optimization is required.
- **Security Reports**: Maintains a historical audit log of all scans and detected threats.

---

## ✨ Key Innovations
- **Hybrid AI Model**: Combines deep learning for pattern recognition with supervised classification for known threat vectors.
- **Adaptive Threat Intelligence**: An engine that learns from new attack vectors globally and updates local definitions dynamically.
- **Multi-layered Verification**: Uses a combination of code fingerprinting and behavioral similarity to ensure 99.9% detection accuracy.
- **Developer Integration**: Can be integrated with developer dashboards for continuous monitoring of app integrity.

---

## 🛠️ Technology Stack
### Frontend
- **Flutter & Dart**: Cross-platform UI development with a focus on high-performance animations and responsiveness.
- **Provider**: State management for clean separation of business logic and UI.
- **Material 3**: Modern design system for a premium look and feel.

### Backend
- **Python FastAPI**: High-performance asynchronous API framework.
- **Aiosqlite**: Asynchronous persistent storage for threat intelligence.
- **Androguard**: Powerful tool for reverse engineering and decompiling Android binaries.
- **Pydantic**: Robust data validation and settings management.

### Infrastructure
- **Supabase**: Backend-as-a-Service (BaaS) providing PostgreSQL, Authentication, and Real-time data sync.
- **Docker**: Containerization for seamless deployment across environments.

---

## 🏗️ System Architecture
The application follows a **Modular Clean Architecture**:
1.  **Presentation Layer (Flutter)**: Handles UI rendering, user input validation, and local state management.
2.  **Service Layer (API Config)**: Manages communication between the mobile client and the analytical backend.
3.  **Analysis Engine (FastAPI)**: Performs heavy computational tasks like APK decompilation and AI heuristics.
4.  **Data Persistence (Supabase & SQLite)**: Manages user data, historical reports, and global threat definitions.

---

## 📂 Project Structure

### Frontend (lib/)
```text
lib/
├── app/               # App entry and global routing (routes.dart)
├── components/        # Reusable UI widgets (buttons, inputs, scaffolds)
├── core/
│   ├── api/           # Centralized API configuration (api_config.dart)
│   ├── theme/         # Global styles and color constants (app_theme.dart)
│   └── utils/         # Helpers (responsive_helper.dart)
├── features/          # Domain-driven features
│   ├── app_scan/      # Malware scanning logic and UI
│   ├── auth/          # Login, Signup, and Password management
│   ├── boost/         # Speed optimization and rocket animations
│   ├── dashboard/     # Main mission control UI
│   ├── deep_clean/    # Storage optimization logic
│   ├── manage_apps/   # MIUI-inspired app management & info
│   ├── notifications/ # Real-time alert system
│   ├── onboarding/    # User welcome sequence
│   ├── pdf_scan/      # Document analysis feature
│   ├── reports/       # Scan history and audit logs
│   ├── settings/      # User preferences
│   └── splash/        # Boot-time initialization
└── services/          # API service clients (scan_service.dart, etc.)
```

### Backend (backend/)
```text
backend/
├── api/routes/        # FastAPI endpoints (scan, clean, boost)
├── app/               # Advanced configuration and system core
├── core/              # Basic settings and environment mapping
├── models/            # Pydantic schemas for typed payloads
├── services/          # Analysis engines (static, behavioral, scoring)
├── uploads/           # Temporary storage for binary analysis
└── main.py            # Backend entry point
```

---

## 🔄 Workflow
1.  **Initiation**: User triggers a scan or optimization task from the Dashboard.
2.  **Data Collection**: The Flutter app gathers metadata (package names, hashes) or uploads files (APKs/PDFs).
3.  **Analysis**: The FastAPI backend receives the request and executes parallel analysis tasks (Static + Dynamic + AI).
4.  **Reporting**: Results are returned to the client and synchronized with Supabase for long-term tracking.
5.  **Action**: The user takes action (Uninstall, Clean, or Whitelist) based on the generated security report.

---

## 🚀 Installation Guide

Setting up AppGuardAi requires configuring both the Python FastAPI backend and the Flutter mobile frontend. Follow this detailed guide to ensure a smooth installation and connection.

### 🛠️ Prerequisites
Before starting, ensure you have the following installed on your system:
- **Flutter SDK (v3.10+)**: [Download Flutter](https://docs.flutter.dev/get-started/install)
- **Python (v3.10+)**: [Download Python](https://www.python.org/downloads/)
- **Android Studio / VS Code**: With Flutter and Dart plugins installed.
- **Java Development Kit (JDK)**: Required for Android builds.
- **ADB (Android Debug Bridge)**: Essential for physical device debugging and port forwarding.
- **Git**: To clone and manage the repository.

---

### 📥 1. Clone the Repository
Open your terminal or command prompt and run:
```bash
git clone https://github.com/RajatBanshiwal/AppGuardAi.git
cd AppGuardAi
```

---

### 🐍 2. Backend Setup (FastAPI)
The backend handles AI heuristics and heavy security analysis.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Virtual Environment:**
   It is highly recommended to use a virtual environment to avoid dependency conflicts.
   ```bash
   # Create environment
   python -m venv venv

   # Activate environment
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables (.env):**
   Create a `.env` file in the `backend/` root and add your Supabase credentials:
   ```ini
   SUPABASE_URL=https://your-project-url.supabase.co
   SUPABASE_KEY=your-anon-key
   DEBUG=True
   ```

5. **Run the Backend Server:**
   ```bash
   # Start server on local port 8000
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   > **Note:** Running on `0.0.0.0` allows the server to be accessible from other devices on the same Wi-Fi network.

---

### 📱 3. Frontend Setup (Flutter)
The frontend is the mobile client that interacts with the backend.

1. **Return to the project root:**
   ```bash
   cd ..
   ```

2. **Install Flutter Dependencies:**
   ```bash
   flutter pub get
   ```

3. **Configure API Endpoints:**
   Open `lib/core/api/api_config.dart` and ensure the `_hostIp` is set correctly:
   - For **Android Emulator**: Use `10.0.2.2`.
   - For **Physical Device (via USB)**: Use `127.0.0.1` (after running `adb reverse`).
   - For **Physical Device (via Wi-Fi)**: Use your computer's local IPv4 address (e.g., `192.168.1.5`).

---

### 🔌 4. Connecting a Physical Device (Detailed)
Testing on a physical Android device provides the best experience for security features.

#### Step A: Enable Developer Options
1. Open **Settings** on your Android phone.
2. Go to **About Phone** > **Software Information**.
3. Tap **Build Number** 7 times until you see "You are now a developer!".
4. Go back to **Settings** > **System** > **Developer Options**.
5. Enable **USB Debugging**.
6. (Optional but recommended) Enable **Install via USB** and **USB Debugging (Security Settings)**.

#### Step B: Connect via USB (Recommended)
1. Connect your phone to your computer via a high-quality USB cable.
2. Accept the "Allow USB Debugging?" prompt on your phone.
3. **Crucial Step: Port Forwarding**
   Run the following command to allow your phone to "see" the backend running on your computer:
   ```bash
   adb reverse tcp:8000 tcp:8000
   ```
   *This maps the phone's port 8000 directly to your computer's port 8000.*

#### Step C: Connect via same Wi-Fi (Alternative)
If you cannot use USB, ensure both your computer and phone are on the **Same Wi-Fi Network**.
1. Find your computer's local IP (Run `ipconfig` on Windows or `ifconfig` on Mac).
2. Update `lib/core/api/api_config.dart` with this IP.
3. Ensure your computer's Firewall is not blocking port 8000.

---

### ⚠️ Important Notes & Warnings
- **Firewall Alert:** If you get a "Connection Refused" error, check if your Windows Defender or Third-party Firewall is blocking Python/Uvicorn.
- **VPN Issues:** Disable any active VPN on either your computer or phone, as they can interfere with local network routing.
- **Sync Issues:** Always ensure the backend is running **before** initiating a scan in the mobile app.
- **ADB Status:** If the app cannot connect, try restarting the ADB server:
  ```bash
  adb kill-server
  adb start-server
  adb reverse tcp:8000 tcp:8000
  ```

---

### 🏃 5. Launch the Application
With the backend running and the device connected:
```bash
flutter run
```

---

## 📖 Detailed Usage Guide

AppGuardAi is designed for maximum security and ease of use. Follow these detailed instructions to get the most out of each feature.

### 🛡️ 1. Security Scanning (Malware Detection)
The primary function of AppGuardAi is to identify malicious clones and fake applications.
- **Start a Scan**: From the Dashboard, tap the **"Start Full Scan"** button in the Security Tools section.
- **Process**: The app will retrieve a list of all installed packages and send their metadata to the AI-powered backend.
- **Results**: Once the scan is complete (usually within 30-60 seconds depending on the number of apps), a detailed report will appear.
- **Actions**: For each flagged app, you can view the risk score (0-100), read why it was flagged (e.g., "Suspicious API usage"), and choose to **Uninstall** or **Whitelist** it.

### 📱 2. Advanced App Management
Manage your applications like a system administrator with the MIUI-inspired interface.
- **Access**: Tap the **"Manage Apps"** card on the Dashboard.
- **Search**: Use the top search bar to filter apps by name in real-time.
- **App Details**: Tap any app to open the **App Info** screen.
- **System Actions**: From the App Info screen, use the bottom actions:
    - **Force Stop**: Redirects to system settings to halt the app process.
    - **Uninstall**: Triggers the native Android uninstallation prompt.
    - **Clear Data**: Quickly navigate to the storage settings to wipe app data/cache.

### ⚡ 3. Device Optimization (Boost & Clean)
Keep your device running at peak performance.
- **Boost Speed**: 
    - Tap **"Boost Speed"** to optimize RAM. 
    - The app identifies background processes that are consuming excessive memory and provides a one-tap solution to free up resources with a smooth rocket animation.
- **Deep Clean**: 
    - Tap **"Deep Clean"** to analyze your storage. 
    - It identifies redundant cache files, old downloads, and large files that are no longer needed. Confirm the cleanup to reclaim gigabytes of storage space.

### 📄 4. Document Shield (PDF Analysis)
Protect yourself from "weaponized" documents.
- **Usage**: Tap **"PDF Scan"** on the Dashboard.
- **Selection**: Choose any PDF file from your device's internal storage.
- **Deep Analysis**: The backend decompiles the PDF and checks for:
    - Hidden JavaScript/Macros.
    - Phishing links embedded in the text.
    - Malicious metadata or structural anomalies.
- **Verdict**: View the safety score before opening the document in your preferred reader.

### 🔔 5. Notifications & Reports
- **Alerts**: Receive real-time push notifications when a new high-risk app is installed on your device.
- **History**: Access the **"Reports"** section from the Dashboard to view a historical log of all previous scans, identified threats, and optimization results.

---

## 👨‍💻 About the Developer



---

