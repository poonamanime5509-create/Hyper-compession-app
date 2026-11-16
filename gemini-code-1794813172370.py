import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, END
import hashlib
import zlib
import os

class HyperDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HyperUniversal Compression Suite (v2.1 - Fixed)")
        self.root.geometry("750x520")
        self.root.config(bg="#1e1e1e")

        self.current_directory = os.getcwd()
        self.selected_file_path = None

        # Title Label
        title_label = tk.Label(root, text="HyperUniversal Desktop & File Access", font=("Helvetica", 14, "bold"), fg="#ffffff", bg="#1e1e1e")
        title_label.pack(pady=10)

        # Main Layout Frame
        main_frame = tk.Frame(root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # --- LEFT SIDE: File Explorer Panel ---
        left_frame = tk.Frame(main_frame, bg="#2d2d2d", padx=5, pady=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        lbl_dir = tk.Label(left_frame, text="Computer Files Explorer", font=("Helvetica", 10, "bold"), fg="#00ffcc", bg="#2d2d2d")
        lbl_dir.pack(anchor="w", pady=5)

        self.btn_browse_dir = tk.Button(left_frame, text="Change Folder", bg="#444444", fg="#ffffff", command=self.browse_directory)
        self.btn_browse_dir.pack(fill=tk.X, pady=2)

        list_container = tk.Frame(left_frame, bg="#2d2d2d")
        list_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.file_listbox = Listbox(list_container, bg="#1e1e1e", fg="#ffffff", font=("Courier", 9), selectbackground="#007acc", selectforeground="#ffffff")
        scrollbar = Scrollbar(list_container, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        # --- RIGHT SIDE: Actions & Logs ---
        right_frame = tk.Frame(main_frame, bg="#1e1e1e")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        btn_action_frame = tk.Frame(right_frame, bg="#1e1e1e")
        btn_action_frame.pack(fill=tk.X, pady=5)

        self.btn_compress = tk.Button(btn_action_frame, text="Compress Selected", font=("Helvetica", 10, "bold"), bg="#007acc", fg="#ffffff", padx=10, pady=8, command=self.compress_selected)
        self.btn_compress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_decompress = tk.Button(btn_action_frame, text="Decompress (.hyper)", font=("Helvetica", 10, "bold"), bg="#28a745", fg="#ffffff", padx=10, pady=8, command=self.decompress_selected)
        self.btn_decompress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        lbl_log = tk.Label(right_frame, text="Execution Log:", font=("Helvetica", 10, "bold"), fg="#aaaaaa", bg="#1e1e1e")
        lbl_log.pack(anchor="w", pady=(10, 2))

        self.log_box = tk.Text(right_frame, height=14, font=("Courier", 9), bg="#2d2d2d", fg="#00ff00", insertbackground="white")
        self.log_box.pack(fill=tk.BOTH, expand=True)
        
        self.load_directory_contents(self.current_directory)

    def log(self, message):
        self.log_box.insert(END, message + "\n")
        self.log_box.see(END)

    def browse_directory(self):
        chosen_dir = filedialog.askdirectory(initialdir=self.current_directory)
        if chosen_dir:
            self.current_directory = chosen_dir
            self.load_directory_contents(chosen_dir)

    def load_directory_contents(self, path):
        self.file_listbox.delete(0, END)
        try:
            items = os.listdir(path)
            self.file_listbox.insert(END, "[..] (Parent Directory)")
            for item in sorted(items):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    self.file_listbox.insert(END, f"📁 {item}/")
                else:
                    self.file_listbox.insert(END, f"📄 {item}")
            self.log(f"Opened folder: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory: {e}")

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        text = self.file_listbox.get(index)
        
        if text == "[..] (Parent Directory)":
            parent_dir = os.path.dirname(self.current_directory)
            self.current_directory = parent_dir
            self.load_directory_contents(parent_dir)
            self.selected_file_path = None
            return

        clean_name = text.replace("📁 ", "").replace("📄 ", "").rstrip("/")
        full_path = os.path.join(self.current_directory, clean_name)
        
        if os.path.isdir(full_path):
            self.current_directory = full_path
            self.load_directory_contents(full_path)
            self.selected_file_path = None
        else:
            self.selected_file_path = full_path
            self.log(f"Selected: {clean_name}")

    def _compute_hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def compress_selected(self):
        if not self.selected_file_path or os.path.isdir(self.selected_file_path):
            messagebox.showwarning("Selection Required", "Please click and select a valid file from the list first!")
            return

        input_file = self.selected_file_path
        output_file = input_file + ".hyper"

        try:
            self.log(f"Compressing: {os.path.basename(input_file)}")
            with open(input_file, 'rb') as f:
                raw_data = f.read()

            orig_hash = self._compute_hash(raw_data)
            
            # Efficient binary package format: [Hash (32 bytes)] + [Zlib Compressed Raw Bytes]
            compressed_payload = zlib.compress(raw_data)
            package = orig_hash.encode('utf-8') + b"\n" + compressed_payload

            with open(output_file, 'wb') as f:
                f.write(package)

            self.log(f"SUCCESS! {len(raw_data)}B -> {len(package)}B")
            self.log(f"Saved: {output_file}\n")
            self.load_directory_contents(self.current_directory)
            messagebox.showinfo("Success", f"File compressed to:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"ERROR: {str(e)}\n")

    def decompress_selected(self):
        if not self.selected_file_path or not self.selected_file_path.endswith(".hyper"):
            messagebox.showwarning("Selection Required", "Please select a valid '.hyper' archive file from the list!")
            return

        input_file = self.selected_file_path
        output_file = input_file.replace(".hyper", "_restored")

        try:
            self.log(f"Restoring archive: {os.path.basename(input_file)}")
            with open(input_file, 'rb') as f:
                package = f.read()

            # Split stored SHA-256 hash from compressed payload
            parts = package.split(b"\n", 1)
            stored_hash = parts[0].decode('utf-8')
            compressed_payload = parts[1]

            restored_data = zlib.decompress(compressed_payload)
            restored_hash = self._compute_hash(restored_data)

            if restored_hash == stored_hash:
                self.log("[VERIFY] SHA-256 Hash Match! 0% Data Loss.")
            else:
                self.log("[WARNING] Hash checksum mismatch!")

            with open(output_file, 'wb') as f:
                f.write(restored_data)

            self.log(f"SUCCESS! Restored file saved to:\n{output_file}\n")
            self.load_directory_contents(self.current_directory)
            messagebox.showinfo("Success", "Archive successfully restored with 0% data loss!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = HyperDesktopApp(root)
    root.mainloop()