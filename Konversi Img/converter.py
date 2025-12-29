import os
import shutil
from PIL import Image

class ImageConverter:
    def __init__(self, input_dir="input", output_dir="output", success_dir="success", fail_dir="fail"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.success_dir = success_dir
        self.fail_dir = fail_dir
        self._prepare_folders()

    def _prepare_folders(self):
        for folder in [self.input_dir, self.output_dir, self.success_dir, self.fail_dir]:
            os.makedirs(folder, exist_ok=True)

    def convert_file(self, input_path):
        filename = os.path.basename(input_path)
        output_path = os.path.join(self.output_dir, os.path.splitext(filename)[0] + ".webp")
        try:
            img = Image.open(input_path)
            img.save(output_path, "WEBP")
            shutil.move(input_path, os.path.join(self.success_dir, filename))
            return True, output_path
        except Exception as e:
            shutil.move(input_path, os.path.join(self.fail_dir, filename))
            return False, str(e)

    def convert_all(self):
        results = []
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(".png"):
                input_path = os.path.join(self.input_dir, filename)
                success, info = self.convert_file(input_path)
                results.append((filename, success, info))
        return results
