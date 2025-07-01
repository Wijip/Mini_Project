from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # Maksimal 100 MB untuk video

# Pastikan folder uploads ada
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Simpan metadata video
videos = []

# Beranda
@app.route("/")
def index():
    return render_template("index.html", videos=videos)

# Halaman unggah video
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # Ambil file dari form
        if "file" not in request.files:
            return "❌ Tidak ada file!"
        file = request.files["file"]
        if file.filename == "":
            return "❌ Nama file kosong!"

        # Simpan file ke folder uploads
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        videos.append({"title": request.form["title"], "filename": file.filename})

        return redirect(url_for("index"))
    return render_template("upload.html")

# Halaman tonton video
@app.route("/watch/<filename>")
def watch(filename):
    video = next((v for v in videos if v["filename"] == filename), None)
    if video:
        return render_template("watch.html", video=video)
    return "❌ Video tidak ditemukan!"

# Route untuk mengakses file video
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True)
