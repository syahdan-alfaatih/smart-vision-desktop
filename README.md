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
smart-vision-desktop/ ├── modules/ │ ├── camera_thread.py # The AI Brain (State Machine & Logic) │ ├── data_manager.py # Database Handler (Pickle) │ └── ui_components.py # Sidebar & Windows ├── resources/ # Dlib Models (Not included in repo) ├── assets/ # Database storage ├── main.py # Entry Point └── requirements.txt # Dependencies

## 👨‍💻 Author
**Syahdan Alfaatih**
