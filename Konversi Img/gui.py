# gui.py
import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from converter import ImageConverter, logger

CONFIG_PATH = "config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        try:
            logger.exception("Failed to save config")
        except Exception:
            pass

class ConverterApp:
    def set_window_center(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter (PNG/JPG/JPEG → WebP)")

        # Force fixed window size and non-resizable
        self.set_window_center(1366, 768)
        self.root.geometry("1366x768")
        self.root.resizable(False, False)

        # load config
        self.config = load_config()
        self.sash_pos = self.config.get("sash_pos", 980)
        self.quality_default = self.config.get("quality", 80)
        exts = self.config.get("exts", [".png", ".jpg", ".jpeg"])

        # converter
        self.converter = ImageConverter()

        # options
        self.ext_png_var = tk.BooleanVar(value=(".png" in exts))
        self.ext_jpg_var = tk.BooleanVar(value=(".jpg" in exts))
        self.ext_jpeg_var = tk.BooleanVar(value=(".jpeg" in exts))
        self.quality_var = tk.IntVar(value=self.quality_default)

        # arrange guards
        self._arrange_after_id = None
        self._arranging = False
        self._last_right_height = 0

        # header
        header = tk.Label(root, text="Image Converter", font=("Arial", 18, "bold"))
        header.pack(pady=8)

        # top: search + options
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=12, pady=6)

        search_frame = tk.Frame(top_frame)
        search_frame.pack(side="left", fill="x", expand=True)

        tk.Label(search_frame, text="🔍 Cari File:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=6)
        tk.Button(search_frame, text="Cari", command=self.search_file).pack(side="left", padx=4)
        tk.Button(search_frame, text="Reset", command=self.refresh_list).pack(side="left", padx=4)

        options_frame = tk.Frame(top_frame)
        options_frame.pack(side="right", fill="y")
        self.btn_options = tk.Button(options_frame, text=self._options_button_text(), command=self.open_options_dialog)
        self.btn_options.pack(anchor="e")

        # paned window: left tree, right actions (preview removed)
        paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=12, pady=6)
        self.paned = paned

        # left: treeview
        left_frame = tk.LabelFrame(paned, text="Daftar File", padx=6, pady=6)
        left_inner = tk.Frame(left_frame)
        left_inner.pack(fill="both", expand=True)
        paned.add(left_frame, minsize=400)

        columns = ("No", "Nama File", "Ukuran", "Path", "Status")
        self.tree = ttk.Treeview(left_inner, columns=columns, show="headings")
        scroll_y = ttk.Scrollbar(left_inner, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(left_inner, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(_col, False))

        self.tree.column("No", width=60, anchor="center", stretch=False)
        self.tree.column("Nama File", width=300, anchor="w", stretch=True)
        self.tree.column("Ukuran", width=140, anchor="center", stretch=False)
        self.tree.column("Path", width=700, anchor="w", stretch=True)
        self.tree.column("Status", width=140, anchor="center", stretch=False)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew", columnspan=2)
        left_inner.rowconfigure(0, weight=1)
        left_inner.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.on_tree_right_click)

        # right: actions only (preview removed)
        right_frame = tk.LabelFrame(paned, text="Preview & Aksi", padx=8, pady=8)
        paned.add(right_frame, minsize=300)
        self.right_frame = right_frame

        # context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Buka File", command=self.context_open_file)
        self.context_menu.add_command(label="Buka Folder", command=self.context_open_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Hapus File", command=self.context_delete_file)

        # buttons container
        self.buttons_frame = tk.Frame(right_frame)
        self.buttons_frame.pack(fill="both", expand=False)

        # action buttons list (btn, label, cmd, key)
        self.action_buttons = []
        def add_action(label, cmd, key):
            btn = tk.Button(self.buttons_frame, text=label, width=28, command=cmd)
            self.action_buttons.append((btn, label, cmd, key))
            return btn

        # MAIN PRIORITY BUTTONS (always prioritized)
        self.btn_refresh = add_action("🔄 Refresh List", self.refresh_list, 0)
        self.btn_convert_selected = add_action("✅ Konversi File Terpilih", self.convert_selected, 1)
        self.btn_batch = add_action("⚙️ Konversi Semua ", self.convert_batch, 2)
        self.btn_show_all = add_action("📂 Kembali ke Tampilan Input", self.refresh_list, 3)
        self.btn_close = add_action("❌ Tutup Program", self.on_close, 4)

        # NON-PRIORITY (moved to More)
        self.btn_show_success = add_action("📂 Lihat List Berhasil", self.show_success, 10)
        self.btn_show_fail = add_action("📂 Lihat List Gagal", self.show_fail, 11)
        self.btn_view_log = add_action("📝 Lihat Log", self.open_log_window, 12)
        self.btn_clear_log = add_action("🧹 Hapus Log", self.clear_log, 13)

        # More menu: always packed once at bottom to avoid blinking
        self.btn_more = tk.Menubutton(self.buttons_frame, text="More ▾", relief="raised", width=28)
        self.btn_more_menu = tk.Menu(self.btn_more, tearoff=0)
        self.btn_more["menu"] = self.btn_more_menu
        self.btn_more.pack(side="bottom", pady=6)
        self.btn_more.config(state="disabled")

        # progress + status
        progress_frame = tk.Frame(root)
        progress_frame.pack(fill="x", padx=12, pady=(6,10))
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=1100, mode="determinate")
        self.progress.pack(side="left", padx=(0,8), fill="x", expand=True)
        self.progress_label = tk.Label(progress_frame, text="0%")
        self.progress_label.pack(side="left")

        self.status_path = tk.Label(root, text=f"Input folder: {self.converter.input_dir}", anchor="w", fg="blue")
        self.status_path.pack(fill="x", padx=12)
        self.status = tk.Label(root, text="Ready", anchor="w")
        self.status.pack(fill="x", padx=12, pady=(0,8))

        self.view_mode = "all"
        self.search_keyword = ""

        # bind configure (debounced)
        self.right_frame.bind("<Configure>", self._on_right_frame_configure)

        # restore sash after start
        self.root.after(100, self._restore_sash)

        # save sash on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # initial populate
        self.refresh_list()

    # sash restore & save
    def _restore_sash(self):
        try:
            self.paned.sash_place(0, self.sash_pos, 0)
        except Exception:
            pass
        self._on_right_frame_configure()

    def _on_close(self):
        try:
            x = self.paned.sash_coord(0)[0]
            self.config["sash_pos"] = int(x)
        except Exception:
            pass
        self.config["quality"] = int(self.quality_var.get())
        exts = []
        if self.ext_png_var.get(): exts.append(".png")
        if self.ext_jpg_var.get(): exts.append(".jpg")
        if self.ext_jpeg_var.get(): exts.append(".jpeg")
        self.config["exts"] = exts
        save_config(self.config)
        try:
            self.root.destroy()
        except Exception:
            pass

    def on_close(self):
        try:
            self._on_close()
        except Exception:
            try:
                self.root.destroy()
            except Exception:
                pass

    # debounce wrapper with height-change guard
    def _on_right_frame_configure(self, event=None):
        try:
            if self._arrange_after_id:
                self.right_frame.after_cancel(self._arrange_after_id)
        except Exception:
            pass

        try:
            cur_h = self.right_frame.winfo_height()
        except Exception:
            cur_h = 0

        if abs(cur_h - self._last_right_height) < 6 and self._last_right_height != 0:
            return

        self._arrange_after_id = self.right_frame.after(250, self.arrange_action_buttons)

    # arrange buttons (no pack/forget of More)
    def arrange_action_buttons(self):
        if self._arranging:
            return
        self._arranging = True
        try:
            # unpack all action buttons (not More)
            for btn, _, _, _ in self.action_buttons:
                try:
                    btn.pack_forget()
                except Exception:
                    pass

            # minimal geometry updates
            try:
                self.buttons_frame.update_idletasks()
                self.right_frame.update_idletasks()
            except Exception:
                pass

            total_h = max(0, self.right_frame.winfo_height())
            # preview removed => preview_h = 0
            preview_h = 0
            padding = 20
            available_h = max(0, total_h - preview_h - padding)

            sample_height = 36
            if self.action_buttons:
                try:
                    req = self.action_buttons[0][0].winfo_reqheight()
                    if req and req > 0:
                        sample_height = req + 8
                except Exception:
                    sample_height = 36

            sorted_buttons = sorted(self.action_buttons, key=lambda t: (t[3] if t[3] is not None else 999,))

            used_h = 0
            overflow = []

            # pack priority 0..5 first
            for btn, label, cmd, key in sorted_buttons:
                if key is not None and key <= 5:
                    if used_h + sample_height <= available_h:
                        try:
                            btn.pack(pady=6)
                        except Exception:
                            pass
                        used_h += sample_height
                    else:
                        overflow.append((label, cmd))

            # pack non-priority if space remains
            for btn, label, cmd, key in sorted_buttons:
                if key is None or key > 5:
                    if used_h + sample_height <= available_h:
                        try:
                            btn.pack(pady=6)
                        except Exception:
                            pass
                        used_h += sample_height
                    else:
                        overflow.append((label, cmd))

            # save last height
            try:
                self._last_right_height = self.right_frame.winfo_height()
            except Exception:
                pass

            # populate More menu (exclude "Tutup Program" from More)
            self._populate_more_menu(overflow)
        finally:
            self._arranging = False

    def _populate_more_menu(self, overflow):
        try:
            self.btn_more_menu.delete(0, "end")
        except Exception:
            pass

        # Add overflow items into More; ensure "Tutup Program" not added
        if overflow:
            for label, cmd in overflow:
                if "Tutup Program" in label:
                    continue
                try:
                    self.btn_more_menu.add_command(label=label, command=(lambda c=cmd: c()))
                except Exception:
                    pass
            try:
                self.btn_more.config(state="normal")
            except Exception:
                pass
        else:
            try:
                self.btn_more.config(state="disabled")
            except Exception:
                pass

    # UI helpers & options dialog
    def _options_button_text(self):
        exts = []
        if getattr(self, "ext_png_var", None) and self.ext_png_var.get():
            exts.append(".png")
        if getattr(self, "ext_jpg_var", None) and self.ext_jpg_var.get():
            exts.append(".jpg")
        if getattr(self, "ext_jpeg_var", None) and self.ext_jpeg_var.get():
            exts.append(".jpeg")
        q = getattr(self, "quality_var", None).get() if getattr(self, "quality_var", None) else 80
        exts_text = ",".join(exts) if exts else "none"
        return f"Pengaturan ({exts_text}) Q={q}"

    def _center_popup(self, win, w, h):
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        if root_w == 1 and root_h == 1:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            x = (screen_w // 2) - (w // 2)
            y = (screen_h // 2) - (h // 2)
        else:
            x = root_x + (root_w // 2) - (w // 2)
            y = root_y + (root_h // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

    def open_options_dialog(self):
        logger.info("Action: open_options_dialog")
        dlg = tk.Toplevel(self.root)
        dlg.title("Pengaturan Konversi")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        self._center_popup(dlg, 420, 260)
        dlg.grab_set()

        frame = tk.Frame(dlg, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Pilih ekstensi yang akan dikonversi:").pack(anchor="w")
        cb_png = tk.Checkbutton(frame, text=".png", variable=self.ext_png_var)
        cb_jpg = tk.Checkbutton(frame, text=".jpg", variable=self.ext_jpg_var)
        cb_jpeg = tk.Checkbutton(frame, text=".jpeg", variable=self.ext_jpeg_var)
        cb_png.pack(anchor="w", pady=2)
        cb_jpg.pack(anchor="w", pady=2)
        cb_jpeg.pack(anchor="w", pady=2)

        tk.Label(frame, text="Kualitas WebP (0-100):").pack(anchor="w", pady=(8,0))
        quality_scale = tk.Scale(frame, from_=0, to=100, orient="horizontal", variable=self.quality_var, length=360)
        quality_scale.pack(anchor="w", pady=4)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=(12,0))
        def on_ok():
            if not (self.ext_png_var.get() or self.ext_jpg_var.get() or self.ext_jpeg_var.get()):
                messagebox.showwarning("Peringatan", "Pilih minimal satu ekstensi untuk dikonversi.", parent=dlg)
                return
            self.btn_options.config(text=self._options_button_text())
            logger.info("Options updated: png=%s jpg=%s jpeg=%s quality=%s",
                        self.ext_png_var.get(), self.ext_jpg_var.get(), self.ext_jpeg_var.get(), self.quality_var.get())
            dlg.destroy()
            self._on_right_frame_configure()

        def on_cancel():
            dlg.destroy()

        ok_btn = tk.Button(btn_frame, text="OK", width=12, command=on_ok)
        ok_btn.pack(side="right", padx=6)
        cancel_btn = tk.Button(btn_frame, text="Batal", width=12, command=on_cancel)
        cancel_btn.pack(side="right")

        dlg.wait_window()

    # file listing & refresh
    def refresh_list(self):
        logger.info("Action: refresh_list")
        self.view_mode = "all"
        self.search_keyword = ""
        self._populate_from_input()
        count = len(self.tree.get_children())
        self.status.config(text=f"{count} file ditemukan di folder input")
        self.status_path.config(text=f"Input folder: {self.converter.input_dir}")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")
        self.btn_options.config(text=self._options_button_text())
        self._on_right_frame_configure()

    def _populate_from_input(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            files = [f for f in os.listdir(self.converter.input_dir) if f.lower().endswith(self.converter.DEFAULT_SUPPORTED_EXT)]
        except FileNotFoundError:
            files = []
        for i, filename in enumerate(sorted(files), start=1):
            file_path = os.path.join(self.converter.input_dir, filename)
            size_kb = max(1, os.path.getsize(file_path) // 1024) if os.path.exists(file_path) else 0
            self.tree.insert("", "end", values=(i, filename, size_kb, file_path, "Belum"))

    # selection (preview removed)
    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            self.status.config(text="Ready")
            return
        item = self.tree.item(sel[0])
        filename = item["values"][1] if len(item["values"]) > 1 else ""
        self.status.config(text=f"File terpilih: {filename}")

    # context menu handlers
    def on_tree_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def _get_selected_path(self):
        sel = self.tree.selection()
        if not sel:
            return None
        item = self.tree.item(sel[0])
        return item["values"][3]

    def context_open_file(self):
        path = self._get_selected_path()
        if not path or not os.path.exists(path):
            messagebox.showinfo("Info", "File tidak ditemukan.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            logger.info("Context: open file %s", path)
        except Exception as e:
            try:
                logger.exception("Failed to open file %s: %s", path, e)
            except Exception:
                pass
            messagebox.showerror("Gagal", f"Gagal membuka file: {e}")

    def context_open_folder(self):
        path = self._get_selected_path()
        if not path:
            messagebox.showinfo("Info", "File tidak ditemukan.")
            return
        folder = os.path.dirname(path)
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
            logger.info("Context: open folder %s", folder)
        except Exception as e:
            try:
                logger.exception("Failed to open folder %s: %s", folder, e)
            except Exception:
                pass
            messagebox.showerror("Gagal", f"Gagal membuka folder: {e}")

    def context_delete_file(self):
        path = self._get_selected_path()
        if not path or not os.path.exists(path):
            messagebox.showinfo("Info", "File tidak ditemukan.")
            return
        if not messagebox.askyesno("Hapus File", f"Yakin ingin menghapus file:\n{os.path.basename(path)}?"):
            return
        try:
            os.remove(path)
            logger.info("Context: deleted file %s", path)
            messagebox.showinfo("Sukses", "File dihapus.")
            if self.view_mode == "all":
                self._populate_from_input()
            elif self.view_mode == "search":
                self.search_file()
            else:
                if self.view_mode == "success":
                    self._filter_by_status_folder(self.converter.success_dir, "Berhasil")
                elif self.view_mode == "fail":
                    self._filter_by_status_folder(self.converter.fail_dir, "Gagal")
            self.status.config(text="Ready")
        except Exception as e:
            try:
                logger.exception("Failed to delete file %s: %s", path, e)
            except Exception:
                pass
            messagebox.showerror("Gagal", f"Gagal menghapus file: {e}")

    # conversion actions
    def _selected_extensions(self):
        exts = []
        if self.ext_png_var.get():
            exts.append(".png")
        if self.ext_jpg_var.get():
            exts.append(".jpg")
        if self.ext_jpeg_var.get():
            exts.append(".jpeg")
        return tuple(exts) if exts else None

    def convert_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih file terlebih dahulu.")
            return
        item = self.tree.item(selected[0])
        filename = item["values"][1]
        input_path = os.path.join(self.converter.input_dir, filename)

        selected_exts = self._selected_extensions()
        if selected_exts is None:
            messagebox.showwarning("Peringatan", "Pilih minimal satu ekstensi untuk dikonversi (Pengaturan).")
            return
        if not self.converter._is_supported(filename, selected_exts):
            messagebox.showinfo("Info", f"File {filename} tidak termasuk ekstensi yang dipilih.")
            return

        quality = int(self.quality_var.get())
        logger.info("Action: convert_selected -> %s (quality=%s)", filename, quality)

        if not os.path.exists(input_path):
            messagebox.showinfo("Info", "File tidak ditemukan di folder input. Mungkin sudah dipindahkan.")
            logger.warning("convert_selected: file not found %s", input_path)
            return

        success, info = self.converter.convert_file(input_path, quality=quality)
        if success:
            messagebox.showinfo("Sukses", f"File berhasil dikonversi ke:\n{info}")
            self.update_status(filename, "Berhasil")
            self.status.config(text=f"{filename} berhasil dikonversi")
        else:
            messagebox.showerror("Gagal", f"Konversi gagal: {info}")
            self.update_status(filename, "Gagal")
            self.status.config(text=f"{filename} gagal dikonversi")

        if self.view_mode == "all":
            self._populate_from_input()
        elif self.view_mode == "search":
            self.search_file()

    def convert_batch(self):
        logger.info("Action: convert_batch started")
        selected_exts = self._selected_extensions()
        if selected_exts is None:
            messagebox.showwarning("Peringatan", "Pilih minimal satu ekstensi untuk dikonversi (Pengaturan).")
            return
        quality = int(self.quality_var.get())

        try:
            files = [f for f in os.listdir(self.converter.input_dir) if f.lower().endswith(selected_exts)]
        except FileNotFoundError:
            files = []
        files = sorted(files)
        total = len(files)
        if total == 0:
            messagebox.showinfo("Info", "Tidak ada file yang cocok dengan ekstensi terpilih di folder input.")
            logger.info("convert_batch: no files found for extensions=%s", selected_exts)
            return

        self.progress["maximum"] = total
        self.progress["value"] = 0
        self.progress_label.config(text="0%")
        sukses, gagal = 0, 0

        if self.view_mode != "all":
            self._populate_from_input()
            self.view_mode = "all"

        for i, filename in enumerate(files, start=1):
            input_path = os.path.join(self.converter.input_dir, filename)
            try:
                success, _ = self.converter.convert_file(input_path, quality=quality)
            except Exception:
                success = False

            if success:
                sukses += 1
                self.update_status(filename, "Berhasil")
            else:
                gagal += 1
                self.update_status(filename, "Gagal")

            self.progress["value"] = i
            percent = int((i / total) * 100)
            self.progress_label.config(text=f"{percent}%")
            self.root.update_idletasks()

        logger.info("Action: convert_batch finished. success=%d fail=%d", sukses, gagal)
        messagebox.showinfo("Hasil Batch", f"Berhasil: {sukses}\nGagal: {gagal}")
        self.status.config(text=f"Batch selesai: {sukses} berhasil, {gagal} gagal")
        self._populate_from_input()

    # filters, search, sort, log
    def show_success(self):
        logger.info("Action: show_success")
        self.view_mode = "success"
        self._filter_by_status_folder(self.converter.success_dir, "Berhasil")

    def show_fail(self):
        logger.info("Action: show_fail")
        self.view_mode = "fail"
        self._filter_by_status_folder(self.converter.fail_dir, "Gagal")

    def _filter_by_status_folder(self, folder, status_label):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        files = [f for f in os.listdir(folder) if f.lower().endswith(self.converter.DEFAULT_SUPPORTED_EXT)]
        for i, filename in enumerate(sorted(files), start=1):
            file_path = os.path.join(folder, filename)
            size_kb = max(1, os.path.getsize(file_path) // 1024)
            self.tree.insert("", "end", values=(i, filename, size_kb, file_path, status_label))
        self.status.config(text=f"Menampilkan {len(files)} file dengan status {status_label}")
        self.status_path.config(text=f"Folder: {folder}")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")

    def search_file(self):
        keyword = self.search_var.get().strip().lower()
        logger.info("Action: search_file keyword=%s", keyword)
        if not keyword:
            messagebox.showinfo("Info", "Masukkan kata kunci pencarian.")
            return
        self.view_mode = "search"
        self.search_keyword = keyword
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            files = [f for f in os.listdir(self.converter.input_dir) if f.lower().endswith(self.converter.DEFAULT_SUPPORTED_EXT)]
        except FileNotFoundError:
            files = []
        matched = [f for f in files if keyword in f.lower()]
        for i, filename in enumerate(sorted(matched), start=1):
            file_path = os.path.join(self.converter.input_dir, filename)
            size_kb = max(1, os.path.getsize(file_path) // 1024)
            self.tree.insert("", "end", values=(i, filename, size_kb, file_path, "Belum"))
        self.status.config(text=f"{len(matched)} hasil pencarian untuk '{self.search_var.get()}'")
        self.status_path.config(text=f"Input folder: {self.converter.input_dir}")
        self.progress["value"] = 0
        self.progress_label.config(text="0%")

    def treeview_sort_column(self, col, reverse):
        logger.debug("Sorting column: %s reverse=%s", col, reverse)
        data_list = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        if col in ("No", "Ukuran"):
            def try_num(x):
                try:
                    return int(x)
                except Exception:
                    try:
                        return float(x)
                    except Exception:
                        return 0
            data_list.sort(key=lambda t: try_num(t[0]), reverse=reverse)
        else:
            data_list.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (val, k) in enumerate(data_list):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

    def open_log_window(self):
        logger.info("Action: open_log_window")
        log_path = os.path.join(os.path.abspath("."), "app.log")
        win = tk.Toplevel(self.root)
        win.title("Log Viewer")
        win.geometry("900x600")
        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, state="normal")
        txt.pack(fill="both", expand=True)
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = "Log file tidak ditemukan."
        txt.insert("1.0", content)
        txt.configure(state="disabled")

    def clear_log(self):
        if not messagebox.askyesno("Hapus Log", "Yakin ingin mengosongkan file log?"):
            return
        log_path = os.path.join(os.path.abspath("."), "app.log")
        try:
            open(log_path, "w", encoding="utf-8").close()
            logger.info("Log file cleared by user")
            messagebox.showinfo("Sukses", "Log berhasil dikosongkan.")
        except Exception as e:
            try:
                logger.exception("Failed to clear log: %s", e)
            except Exception:
                pass
            messagebox.showerror("Gagal", f"Gagal mengosongkan log: {e}")

    # update status cell
    def update_status(self, filename, status_text):
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if len(values) >= 2 and values[1] == filename:
                self.tree.item(item, values=(values[0], values[1], values[2], values[3], status_text))
                break
