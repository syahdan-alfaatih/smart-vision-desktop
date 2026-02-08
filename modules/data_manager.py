import os
import pickle
import dlib
import cv2
import numpy as np

class DataManager:
    def __init__(self):
        # ===== KONFIGURASI PATH =====
        # Kita pakai path relatif dari root project
        self.db_folder = "assets/database"
        self.db_file = os.path.join(self.db_folder, "face_cache.pkl")
        
        self.model_shape = "resources/shape_predictor_68_face_landmarks.dat"
        self.model_resnet = "resources/dlib_face_recognition_resnet_model_v1.dat"

        # Pastikan folder database ada
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
            print(f">> [DATA] Folder dibuat: {self.db_folder}")

    def load_database(self):
        """
        Memuat database wajah dari file .pkl
        Return: List of dict [{'name': '...', 'encoding': ...}]
        """
        if not os.path.exists(self.db_file):
            print(">> [DATA] Database kosong / file belum ada.")
            return []

        try:
            with open(self.db_file, "rb") as f:
                data = pickle.load(f)
                print(f">> [DATA] Berhasil memuat {len(data)} wajah dari cache.")
                return data
        except Exception as e:
            print(f">> [ERROR] Gagal memuat database: {e}")
            return []

    def save_database(self, data):
        """
        Menyimpan list wajah ke file .pkl
        """
        try:
            with open(self.db_file, "wb") as f:
                pickle.dump(data, f)
            print(">> [DATA] Database berhasil disimpan!")
            return True
        except Exception as e:
            print(f">> [ERROR] Gagal menyimpan database: {e}")
            return False

    def add_face(self, name, image_path):
        """
        Core Logic:
        1. Load Model (Independent)
        2. Validasi Strict (Harus 1 Wajah)
        3. Encode
        4. Simpan
        
        Return: (Success: bool, Message: str)
        """
        print(f">> [PROCESS] Memulai proses Add Face: {name}")

        # 1. VALIDASI FILE
        if not os.path.exists(image_path):
            return False, "File gambar tidak ditemukan!"

        # 2. LOAD MODEL (HANYA SAAT DIBUTUHKAN)
        # Ini strategi 'Separation of Concerns' biar CameraThread aman
        if not (os.path.exists(self.model_shape) and os.path.exists(self.model_resnet)):
            return False, "Model AI (Dlib) tidak ditemukan di folder resources!"

        try:
            print(">> [AI] Memuat model Dlib sementara...")
            detector = dlib.get_frontal_face_detector()
            predictor = dlib.shape_predictor(self.model_shape)
            facerec = dlib.face_recognition_model_v1(self.model_resnet)
        except Exception as e:
            return False, f"Gagal memuat model AI: {e}"

        # 3. PROSES GAMBAR
        try:
            # Load pakai OpenCV lalu convert ke RGB (Dlib butuh RGB)
            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                return False, "Format gambar tidak didukung atau rusak."
            
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            # Detect Wajah
            faces = detector(img_rgb, 1)
            
            # 4. STRICT MODE VALIDATION 👮
            if len(faces) == 0:
                return False, "Tidak ditemukan wajah! Gunakan foto yang jelas."
            elif len(faces) > 1:
                return False, f"Terdeteksi {len(faces)} wajah! Gunakan foto SATU orang saja."
            
            # Kalau lolos (len == 1)
            print(">> [AI] Wajah valid. Memulai enkripsi biometrik...")
            shape = predictor(img_rgb, faces[0])
            encoding = np.array(facerec.compute_face_descriptor(img_rgb, shape))

            # 5. SIMPAN KE DATABASE
            current_db = self.load_database()
            
            # Cek duplikat nama (Opsional, tapi bagus buat UX)
            for user in current_db:
                if user['name'].upper() == name.upper():
                    return False, f"Nama '{name}' sudah ada di database!"

            new_data = {
                "name": name.upper(), # Kita standar-kan jadi Huruf Besar
                "encoding": encoding
            }
            
            current_db.append(new_data)
            
            if self.save_database(current_db):
                return True, f"Berhasil mendaftarkan: {name}"
            else:
                return False, "Gagal menulis ke file database."

        except Exception as e:
            print(f">> [ERROR] {e}")
            return False, f"Terjadi kesalahan sistem: {e}"

    def delete_face(self, name):
        """
        Menghapus wajah berdasarkan nama
        """
        current_db = self.load_database()
        filtered_db = [u for u in current_db if u['name'] != name]

        if len(current_db) == len(filtered_db):
            return False, "Nama tidak ditemukan di database."
        
        if self.save_database(filtered_db):
            return True, f"Wajah '{name}' berhasil dihapus."
        else:
            return False, "Gagal update file database."

    def get_face_list(self):
        """
        Helper untuk UI: Mengambil list nama saja
        """
        db = self.load_database()
        # Return list nama (sorted A-Z biar rapi)
        return sorted([u['name'] for u in db])