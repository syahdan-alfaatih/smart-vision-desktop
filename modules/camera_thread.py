import cv2
import threading
import time
import dlib
import os
import numpy as np
from PIL import Image

class CameraThread:
    def __init__(self, video_source=0):
        self.video_source = video_source
        self.is_running = False
        self.thread = None
        self.latest_frame = None

        print(">> [AI-ENGINE] Memuat Model Dlib...")
        self.detector = dlib.get_frontal_face_detector()

        path_landmarks = "resources/shape_predictor_68_face_landmarks.dat"
        path_resnet = "resources/dlib_face_recognition_resnet_model_v1.dat"

        self.predictor = None
        self.face_rec_model = None

        if os.path.exists(path_landmarks) and os.path.exists(path_resnet):
            self.predictor = dlib.shape_predictor(path_landmarks)
            self.face_rec_model = dlib.face_recognition_model_v1(path_resnet)
            print(">> [AI-ENGINE] Model AI SIAP!")

        self.face_database = [] 
        
        # Multi-face slots initialization
        self.face_slots = [
            {
                "id": 0, "active": False, "rect": None, "landmarks": None,
                "state": "IDLE", "confidence": 0.0, "name": "UNKNOWN",
                "color": (255, 0, 0), "lost_counter": 0, "miss_counter": 0
            },
            {
                "id": 1, "active": False, "rect": None, "landmarks": None,
                "state": "IDLE", "confidence": 0.0, "name": "UNKNOWN",
                "color": (0, 255, 255), "lost_counter": 0, "miss_counter": 0
            }
        ]
        
        # Configuration
        self.MAX_LOST_FRAMES = 5
        self.CONFIDENCE_THRESHOLD = 3.0
        self.RECOG_ACCEPT = 0.50 
        self.RECOG_GRAY = 0.60    
        self.frame_count = 0

    def update_database(self, new_database):
        self.face_database = new_database
        print(f">> [CAMERA] Database diperbarui! Total wajah: {len(self.face_database)}")

    def start_camera(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()

    def stop_camera(self):
        self.is_running = False

    def calculate_center(self, rect):
        return (rect.left() + rect.right()) // 2, (rect.top() + rect.bottom()) // 2

    def calculate_distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def smooth_rect(self, old_rect, new_rect, alpha=0.6):
        # Anti-jitter: Blend old position (60%) with new position (40%)
        if old_rect is None: return new_rect
        
        l = int(alpha * old_rect.left() + (1 - alpha) * new_rect.left())
        t = int(alpha * old_rect.top() + (1 - alpha) * new_rect.top())
        r = int(alpha * old_rect.right() + (1 - alpha) * new_rect.right())
        b = int(alpha * old_rect.bottom() + (1 - alpha) * new_rect.bottom())
        
        return dlib.rectangle(l, t, r, b)

    def _update_slot_state(self, slot, matched_this_frame):
        if matched_this_frame:
            # Reset failure counters
            slot["lost_counter"] = 0
            slot["miss_counter"] = 0 
            slot["active"] = True
            
            # State Transitions
            if slot["state"] == "IDLE":
                slot["state"] = "SEARCHING"
                
            elif slot["state"] == "LOST":
                if slot["confidence"] >= self.CONFIDENCE_THRESHOLD:
                    slot["state"] = "CONFIRMED"
                else:
                    slot["state"] = "SEARCHING"
                    
            elif slot["state"] == "SEARCHING":
                if slot["confidence"] >= self.CONFIDENCE_THRESHOLD:
                    slot["state"] = "CONFIRMED"
            
            # Downgrade check
            if slot["state"] == "CONFIRMED" and slot["confidence"] < 1.0:
                 slot["state"] = "SEARCHING"
                 slot["name"] = "UNKNOWN"

        else:
            # Miss tolerance logic
            slot["miss_counter"] += 1

            if slot["state"] == "CONFIRMED":
                # Grace period: Require 2 consecutive misses to consider LOST
                if slot["miss_counter"] >= 2:
                    slot["state"] = "LOST"
                    slot["lost_counter"] = 0
            
            elif slot["state"] == "SEARCHING":
                slot["state"] = "IDLE"
                slot["active"] = False
                slot["confidence"] = 0.0
                slot["name"] = "UNKNOWN"
                slot["rect"] = None
            
            elif slot["state"] == "LOST":
                slot["lost_counter"] += 1
                if slot["lost_counter"] > self.MAX_LOST_FRAMES:
                    slot["state"] = "IDLE"
                    slot["active"] = False
                    slot["confidence"] = 0.0
                    slot["name"] = "UNKNOWN"
                    slot["rect"] = None

    def _capture_loop(self):
        cap = cv2.VideoCapture(self.video_source, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print(">> [INFO] SmartVision Pro Logic Running")

        TARGET_FPS = 25
        FRAME_TIME = 1 / TARGET_FPS
        DETECT_INTERVAL = 4 

        while self.is_running:
            start_time = time.time()
            ret, frame = cap.read()
            if not ret: continue

            h, w, _ = frame.shape
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            rgb_small = np.ascontiguousarray(rgb_small, dtype=np.uint8)

            detected_faces = []
            detection_ran = False 

            # --- Detection Phase ---
            if self.frame_count % DETECT_INTERVAL == 0:
                detection_ran = True 
                raw_faces = self.detector(rgb_small, 0)
                sorted_faces = sorted(raw_faces, key=lambda f: f.area(), reverse=True)
                detected_faces = sorted_faces[:2]

            # --- Slot Assignment Logic ---
            if detection_ran:
                slot_matches = [False, False] 

                if len(detected_faces) > 0:
                    for face in detected_faces:
                        cx, cy = self.calculate_center(face)
                        best_slot_idx = -1
                        min_dist = 10000

                        # Find closest active slot
                        for i, slot in enumerate(self.face_slots):
                            if slot["active"] and slot["rect"]:
                                scx, scy = self.calculate_center(slot["rect"])
                                dist = self.calculate_distance((cx, cy), (scx, scy))
                                
                                threshold = 150 
                                if slot["state"] == "LOST": threshold = 80 

                                if dist < threshold and dist < min_dist:
                                    min_dist = dist
                                    best_slot_idx = i

                        # If no match, find empty slot
                        if best_slot_idx == -1:
                            for i, slot in enumerate(self.face_slots):
                                if not slot["active"] and slot["state"] == "IDLE":
                                    best_slot_idx = i
                                    break
                        
                        # Assign and Smooth
                        if best_slot_idx != -1 and not slot_matches[best_slot_idx]:
                            old_rect = self.face_slots[best_slot_idx]["rect"]
                            self.face_slots[best_slot_idx]["rect"] = self.smooth_rect(old_rect, face)
                            slot_matches[best_slot_idx] = True

                for i, slot in enumerate(self.face_slots):
                    matched = slot_matches[i]
                    self._update_slot_state(slot, matched)

            else:
                # Keep alive during non-detection frames
                for slot in self.face_slots:
                    if slot["active"] and slot["state"] != "LOST":
                        slot["lost_counter"] = 0
            
            # --- Recognition Phase ---
            for slot in self.face_slots:
                if slot["active"] and slot["rect"] and slot["state"] != "LOST":
                    
                    slot["landmarks"] = self.predictor(rgb_small, slot["rect"])
                    rec_check_interval = 6 if slot["state"] == "SEARCHING" else 15
                    did_recognition = False 

                    if (self.face_rec_model and len(self.face_database) > 0 and 
                        slot["landmarks"] and self.frame_count % rec_check_interval == 0):
                        
                        did_recognition = True
                        current_desc = np.array(self.face_rec_model.compute_face_descriptor(rgb_small, slot["landmarks"]))
                        
                        best_match_dist = 1.0 
                        best_match_name = "UNKNOWN"
                        
                        for data in self.face_database:
                            dist = np.linalg.norm(data["encoding"] - current_desc)
                            if dist < best_match_dist:
                                best_match_dist = dist
                                best_match_name = data["name"]
                        
                        # Hysteresis Logic
                        if best_match_dist < self.RECOG_ACCEPT:
                            if slot["state"] == "CONFIRMED" and slot["name"] == best_match_name:
                                slot["confidence"] = min(slot["confidence"] + 1.0, 5.0)
                            else:
                                slot["name"] = best_match_name
                                slot["confidence"] = min(slot["confidence"] + 1.5, 5.0)

                        elif best_match_dist < self.RECOG_GRAY:
                            slot["confidence"] -= 0.1

                        else:
                            if slot["state"] == "CONFIRMED":
                                slot["confidence"] -= 0.5 
                                if slot["confidence"] <= 0: slot["name"] = "UNKNOWN"
                            else:
                                slot["confidence"] = max(slot["confidence"] - 2.0, 0.0)
                                slot["name"] = "UNKNOWN"

                    # Confidence Decay
                    elif not did_recognition and slot["confidence"] > 0:
                        if slot["state"] == "CONFIRMED":
                            slot["confidence"] -= 0.01 
                        else:
                            slot["confidence"] -= 0.2 

            # --- Visualization ---
            for slot in self.face_slots:
                if slot["active"] and slot["rect"]:
                    rect = slot["rect"]
                    x1, y1 = int(rect.left() * 2), int(rect.top() * 2)
                    x2, y2 = int(rect.right() * 2), int(rect.bottom() * 2)

                    color = slot["color"]
                    display_name = slot['name']
                    
                    if slot["state"] == "LOST":
                         display_name = "LOST..."
                         color = (0, 0, 150)
                         cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1) 
                    else:
                         if slot["state"] == "CONFIRMED": color = (0, 255, 0) 
                         elif slot["state"] == "SEARCHING": color = (0, 255, 255) 
                         cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    status_text = f"S{slot['id']} {display_name} {slot['confidence']:.1f}"
                    cv2.putText(frame, status_text, (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            self.frame_count += 1
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.latest_frame = Image.fromarray(frame_rgb)

            elapsed = time.time() - start_time
            if elapsed < FRAME_TIME:
                time.sleep(FRAME_TIME - elapsed)