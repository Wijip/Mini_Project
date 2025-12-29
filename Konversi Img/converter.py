import os
import shutil
import logging
from PIL import Image

# Setup logger
logger = logging.getLogger("ImageConverter")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    log_dir = os.path.abspath(".")
    log_path = os.path.join(log_dir, "app.log")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

class ImageConverter:
    # Default supported extensions (lowercase, with dot)
    DEFAULT_SUPPORTED_EXT = (".png", ".jpg", ".jpeg")

    def __init__(self,
                 base_media_dir="media",
                 img_folder="Img",
                 input_dir_name="input",
                 output_dir_name="output",
                 success_dir_name="success",
                 fail_dir_name="fail"):
        """
        Struktur default:
        media/Img/input
        media/Img/output
        media/Img/success
        media/Img/fail
        """
        self.base_media_dir = base_media_dir
        self.img_folder = img_folder

        base_img_path = os.path.join(self.base_media_dir, self.img_folder)
        self.input_dir = os.path.join(base_img_path, input_dir_name)
        self.output_dir = os.path.join(base_img_path, output_dir_name)
        self.success_dir = os.path.join(base_img_path, success_dir_name)
        self.fail_dir = os.path.join(base_img_path, fail_dir_name)

        self._prepare_folders()
        logger.info("ImageConverter initialized. input=%s output=%s success=%s fail=%s",
                    self.input_dir, self.output_dir, self.success_dir, self.fail_dir)

    def _prepare_folders(self):
        folders = [self.base_media_dir,
                   os.path.join(self.base_media_dir, self.img_folder),
                   self.input_dir, self.output_dir, self.success_dir, self.fail_dir]
        for folder in folders:
            try:
                os.makedirs(folder, exist_ok=True)
                logger.debug("Ensured folder exists: %s", folder)
            except Exception as e:
                logger.exception("Failed to create folder %s: %s", folder, e)

    def _is_supported(self, filename, extensions=None):
        """
        Cek apakah filename berakhiran salah satu ekstensi yang diberikan.
        Jika extensions None, gunakan DEFAULT_SUPPORTED_EXT.
        extensions harus berupa iterable ekstensi dengan dot, mis. ('.png', '.jpg')
        """
        if extensions is None:
            extensions = self.DEFAULT_SUPPORTED_EXT
        lower = filename.lower()
        return any(lower.endswith(ext) for ext in extensions)

    def convert_file(self, input_path, quality=80):
        """
        Mengonversi satu file gambar (png/jpg/jpeg) ke WebP.
        quality: integer 0-100 untuk WebP.
        Mengembalikan (True, output_path) jika sukses,
        atau (False, error_message) jika gagal.
        """
        filename = os.path.basename(input_path)
        name_wo_ext, _ = os.path.splitext(filename)
        output_path = os.path.join(self.output_dir, name_wo_ext + ".webp")
        logger.info("Start convert_file: %s (quality=%s)", input_path, quality)

        try:
            img = Image.open(input_path)
            # Pilih mode yang sesuai: JPG biasanya RGB, PNG bisa RGBA
            if img.mode not in ("RGB", "RGBA"):
                try:
                    img = img.convert("RGBA")
                except Exception:
                    img = img.convert("RGB")

            # Simpan sebagai WebP dengan quality
            img.save(output_path, "WEBP", quality=int(quality))
            # pindahkan file sumber ke folder success
            shutil.move(input_path, os.path.join(self.success_dir, filename))
            logger.info("Convert success: %s -> %s (moved to %s)", input_path, output_path, self.success_dir)
            return True, output_path
        except Exception as e:
            logger.exception("Convert failed for %s: %s", input_path, e)
            try:
                shutil.move(input_path, os.path.join(self.fail_dir, filename))
                logger.info("Moved failed file to %s", self.fail_dir)
            except Exception as mv_e:
                logger.exception("Failed to move failed file %s: %s", input_path, mv_e)
            return False, str(e)

    def convert_all(self, extensions=None, quality=80):
        """
        Mengonversi semua file di folder input yang cocok dengan 'extensions'.
        extensions: iterable ekstensi dengan dot, mis. ('.png', '.jpg').
                    Jika None, gunakan DEFAULT_SUPPORTED_EXT.
        quality: integer 0-100 untuk WebP.
        Mengembalikan list tuple: (filename, success_bool, info)
        """
        if extensions is None:
            extensions = self.DEFAULT_SUPPORTED_EXT
        logger.info("Start convert_all in folder: %s with extensions=%s quality=%s",
                    self.input_dir, extensions, quality)
        results = []
        try:
            filenames = sorted(os.listdir(self.input_dir))
        except FileNotFoundError:
            filenames = []
        for filename in filenames:
            if self._is_supported(filename, extensions):
                input_path = os.path.join(self.input_dir, filename)
                success, info = self.convert_file(input_path, quality=quality)
                results.append((filename, success, info))
        logger.info("convert_all finished. total_processed=%d", len(results))
        return results
