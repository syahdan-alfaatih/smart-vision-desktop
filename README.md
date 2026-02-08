# 👁️ Smart Vision Desktop

A robust real-time Face Recognition and Tracking application built with **Python**, **OpenCV**, and **Dlib**. 

Unlike standard tutorials, this system implements a **State Machine Architecture** (IDLE -> SEARCHING -> CONFIRMED -> LOST) to handle occlusion, lighting changes, and detection jitter, ensuring smooth and stable tracking.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Active-green)

## ✨ Key Features

* **🧠 Robust State Machine:** Prevents flickering statuses using `IDLE`, `SEARCHING`, `CONFIRMED`, and `LOST` states.
* **🔒 Identity Lock & Hysteresis:** Uses dual-threshold logic (0.50 / 0.60) to prevent identity switching when confidence drops slightly.
* **⚡ Multi-Face Memory:** Tracks and remembers up to 2 faces simultaneously with independent states.
* **💾 Local Database System:** Manage faces (Add/Delete) via a GUI without restarting the application.
* **🎨 Modern GUI:** Built with `CustomTkinter` for a dark-themed, professional dashboard.
* **🛡️ Anti-Jitter:** Implements Rect Smoothing to keep bounding boxes stable.

## 🛠️ Tech Stack

* **Language:** Python
* **GUI:** CustomTkinter
* **Computer Vision:** OpenCV, Dlib
* **Logic:** Custom State Machine & Euclidean Distance Matching

## 🚀 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/syahdan-alfaatih/smart-vision-desktop.git
    cd smart-vision-desktop
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Download Dlib Models**
    Due to GitHub file size limits, please download these models and place them in the `resources/` folder:
    * [shape_predictor_68_face_landmarks.dat](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)
    * [dlib_face_recognition_resnet_model_v1.dat](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2)
    *(Extract the .bz2 files before using)*

4.  **Run the App**
    ```bash
    python main.py
    ```

## 📂 Project Structure

```text
smart-vision-desktop/
│
├── 📂 assets/                  # Local storage for app data
│   └── 📂 database/
│       ├── 📄 face_cache.pkl   # The AI Brain (Pickle database storing face encodings)
│       └── 📂 raw_images/      # Folder for source images (optional backup)
│
├── 📂 modules/                 # Core application logic
│   ├── 🐍 camera_thread.py     # AI Engine (State Machine, Hysteresis, Anti-Jitter)
│   ├── 🐍 data_manager.py      # Database Handler (Add/Delete/Load logic)
│   └── 🐍 ui_components.py     # GUI Components (Sidebar, Pop-ups, Layouts)
│
├── 📂 resources/               # Dlib AI Models (Download externally if not included)
│   ├── 📦 shape_predictor_68_face_landmarks.dat
│   └── 📦 dlib_face_recognition_resnet_model_v1.dat
│
├── 📄 .gitignore               # Git configuration (Ignored files)
├── 🐍 main.py                  # Entry Point (Run this file to start)
├── 📝 README.md                # Documentation
└── 📄 requirements.txt         # Dependency list
```

## 👨‍💻 Author
**Syahdan Alfaatih**
