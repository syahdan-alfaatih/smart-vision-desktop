import os
import pickle
import dlib
import cv2
import numpy as np

class DataManager:
    def __init__(self):
        self.db_folder = "assets/database"
        self.db_file = os.path.join(self.db_folder, "face_cache.pkl")
        
        self.model_shape = "resources/shape_predictor_68_face_landmarks.dat"
        self.model_resnet = "resources/dlib_face_recognition_resnet_model_v1.dat"

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

        if not os.path.exists(image_path):
            return False, "File gambar tidak ditemukan!"

        if not (os.path.exists(self.model_shape) and os.path.exists(self.model_resnet)):
            return False, "Model AI (Dlib) tidak ditemukan di folder resources!"

        try:
            print(">> [AI] Memuat model Dlib sementara...")
            detector = dlib.get_frontal_face_detector()
            predictor = dlib.shape_predictor(self.model_shape)
            facerec = dlib.face_recognition_model_v1(self.model_resnet)
        except Exception as e:
            return False, f"Gagal memuat model AI: {e}"

        try:
            img_bgr = cv2.imread(image_path)
            if img_bgr is None:
                return False, "Format gambar tidak didukung atau rusak."
            
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            faces = detector(img_rgb, 1)
            
            if len(faces) == 0:
                return False, "Tidak ditemukan wajah! Gunakan foto yang jelas."
            elif len(faces) > 1:
                return False, f"Terdeteksi {len(faces)} wajah! Gunakan foto SATU orang saja."
            
            print(">> [AI] Wajah valid. Memulai enkripsi biometrik...")
            shape = predictor(img_rgb, faces[0])
            encoding = np.array(facerec.compute_face_descriptor(img_rgb, shape))

            current_db = self.load_database()
            
            for user in current_db:
                if user['name'].upper() == name.upper():
                    return False, f"Nama '{name}' sudah ada di database!"

            new_data = {
                "name": name.upper(),
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
        return sorted([u['name'] for u in db])
