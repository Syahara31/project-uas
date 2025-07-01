import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import pandas as pd
from datetime import datetime
import os

# ===================================================================================
# BAGIAN DATA DAN KONFIGURASI GLOBAL
# ===================================================================================

# (Bagian ini tidak ada perubahan, sama seperti sebelumnya)
dosen_input = [
    'Alun Sujjada, ST., M.Kom', 'Anggun Fergina, M.Kom', 'Gina Purnama Insany, S.Si.T., M.Kom',
    'Ir. Somantri, ST., M.Kom', 'Ivana Lucia Kharisma, M.Kom', 'Ir. Kamdan, M.Kom',
    'Dhita Diana Dewi, M.Stat', 'Lusiana Sani Parwati, M.Mat', 'Drs. Nuzwan Sudariana, MM',
    'Syahid Abdullah, S.Si., M.Kom', 'Hermanto, M.Kom', 'Nugraha, M.Kom', 'Imam Sanjaya, SP., M.Kom',
    'Zaenal Alamsyah, M.Kom', 'M.Ikhsan Thohir, M.Kom', 'Adrian Reza, M.Kom', 'Shinta Ayuningtyas, M.Kom',
    'Moneyta Dholah Rosita, M.Kom', 'Mega Lumbia Octavia Sinaga, M.Kom', 'Indra Yustiana, M.Kom',
    'Harris Al Qodri Maarif, S.T., M.Sc. PhD', 'Dr. Iwan Setiawan, S.T., M.T', 'Dede Sukmawan, M.Kom',
    'Falentino Sembiring, M.Kom', 'Dr. Huang Gan', 'Muchtar Ali Setyo Yudono, S.T., M.T',
    'Dr. Deni Hasman', 'Dr. Nurkhan', 'Dr. Yurman Zaenal', 'Zaenal Alamsyah, M.Kom',
    'Indra Yustiana, M.Kom', 'Ir. Somantri', 'Anggun Fergina, M.Kom', 'Gina Purnama Insany, S.Si.T., M.Kom',
    'Moneyta Dholah Rosita, M.Kom', 'Mega Lumbia Octavia Sinaga, M.Kom', 'Shinta Ayuningtyas, M.Kom'
]
DOSEN_LIST = sorted(list(set(dosen_input)))
MATAKULIAH_LIST = sorted([
    'Algoritma dan Struktur Data', 'Pemrograman Berbasis Platform', 'Kompleksitas Algoritma',
    'Pengolahan Citra Digital', 'Pemrograman Berbasis Web', 'Jaringan Komputer dan Keamanan Informasi',
    'Sistem Paralel dan Terdistribusi', 'Rekayasa Perangkat Lunak', 'Basis Data',
    'Projek Perangkat Lunak', 'Logika Informatika', 'Statistika dan Probabilitas',
    'Metodologi Penelitian', 'Data Science', 'Cyber Security', 'Sistem Informasi Geografis',
    'Big Data Arsitektur dan Infrastruktur', 'Interaksi Manusia dan Komputer', 'Computer Vision',
    'Deep Learning', 'Organisasi dan Arsitektur Komputer', 'Kalkulus', 'Metode Numerik',
    'Pemrograman Berbasis Mobile', 'Pengolahan Perangkat Lunak', 'Etika Profesi', 'Teknologi Blockchain'
])
PRODI_LIST = sorted(['Teknik Informatika', 'Sistem Informasi', 'Manajemen Informatika', 'Komputerisasi Akuntansi', 'Teknik Komputer'])
SEMESTER_LIST = list(range(1, 9))
SKS_LIST = list(range(1, 7))
MODE_LIST = ['OFFLINE', 'ONLINE']

# --- MODIFIKASI STRUKTUR DATA RUANGAN ---
# Definisikan daftar ruangan standar untuk Gedung B lantai 2-7
RUANG_B_STANDARD = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

AVAILABLE_ROOMS = {
    'A': {
        # Gedung A memiliki lantai 1-6, semuanya tanpa pilihan ruangan spesifik
        'floors': {
            i: ['-'] for i in range(1, 6)
        }
    },
    'B': {
        # Gedung B memiliki lantai 1-7 dengan aturan berbeda
        'floors': {
            1: ['-'],  # Lantai 1 tidak memiliki ruangan
            # Lantai 2 hingga 7 memiliki ruangan standar
            **{i: RUANG_B_STANDARD for i in range(2, 7)}
        }
    }
}

ALLOWED_DAYS = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT']
MIN_TIME = datetime.strptime("08:00", "%H:%M").time()
MAX_TIME = datetime.strptime("20:00", "%H:%M").time()
BREAKS = [(datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("13:00", "%H:%M").time()), (datetime.strptime("18:00", "%H:%M").time(), datetime.strptime("19:00", "%H:%M").time())]
NAMA_FILE_EXCEL = 'reservasi_ruangan.xlsx'
KOLOM_WAJIB = ['HARI', 'DOSEN', 'MATAKULIAH', 'PRODI', 'SEMESTER', 'SKS', 'KELAS', 'MODE', 'GEDUNG', 'LANTAI', 'RUANGAN', 'MULAI', 'SELESAI', 'TANGGAL_DIBUAT']
KOLOM_FORM = ['HARI', 'DOSEN', 'MATAKULIAH', 'PRODI', 'SEMESTER', 'SKS', 'KELAS', 'MODE', 'GEDUNG', 'LANTAI', 'RUANGAN', 'MULAI', 'SELESAI']


# ===================================================================================
# FUNGSI HELPER
# ===================================================================================
# (Bagian ini tidak ada perubahan, sama seperti sebelumnya)
def is_time_slot_valid(start_str, end_str):
    try:
        start_t, end_t = datetime.strptime(start_str, "%H:%M").time(), datetime.strptime(end_str, "%H:%M").time()
    except (ValueError, TypeError):
        return False, "Format waktu salah. Gunakan HH:MM."
    if not (MIN_TIME <= start_t < MAX_TIME and MIN_TIME < end_t <= MAX_TIME and start_t < end_t):
        return False, f"Waktu reservasi harus antara {MIN_TIME:%H:%M} dan {MAX_TIME:%H:%M}."
    for s, e in BREAKS:
        if s <= start_t < e or s < end_t <= e:
            return False, f"Waktu reservasi tumpang tindih dengan jam istirahat ({s:%H:%M}-{e:%H:%M})."
    return True, ""

def is_room_available(df, day, start_str, end_str, gedung, lantai, ruangan, ignore_index=None):
    temp_df = df.copy()
    if ignore_index is not None:
        temp_df = temp_df.drop(index=ignore_index)
    start_t, end_t = datetime.strptime(start_str, "%H:%M").time(), datetime.strptime(end_str, "%H:%M").time()
    bookings = temp_df[(temp_df['HARI'] == day) & (temp_df['GEDUNG'] == gedung) & (pd.to_numeric(temp_df['LANTAI'], errors='coerce') == lantai) & (temp_df['RUANGAN'] == ruangan)]
    for _, row in bookings.iterrows():
        booked_start, booked_end = datetime.strptime(row['MULAI'], "%H:%M").time(), datetime.strptime(row['SELESAI'], "%H:%M").time()
        if max(start_t, booked_start) < min(end_t, booked_end):
            return False, f"Lokasi ini sudah dipesan dari jam {row['MULAI']}-{row['SELESAI']}."
    return True, ""

# ===================================================================================
# KELAS APLIKASI GUI
# ===================================================================================

class ReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Reservasi Ruangan")
        self.root.geometry("1366x768")
        self.df = self.load_data()

        style = ttk.Style(self.root)
        try:
            theme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azure.tcl")
            self.root.tk.call("source", theme_path)
            style.theme_use("azure-light")
        except tk.TclError:
            print("Peringatan: Tema 'azure' tidak ditemukan. Menggunakan tema default.")

        style.configure("Treeview", rowheight=25, font=('Segoe UI', 9))
        style.map('Treeview', background=[('selected', "#0078D7")])
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), padding=(5,5))

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(tree_frame, columns=KOLOM_WAJIB, show='headings', yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        self.tree.tag_configure('oddrow', background='#F0F0F0')
        self.tree.tag_configure('evenrow', background='white')
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        for col in KOLOM_WAJIB:
            self.tree.heading(col, text=col, anchor='w')
            self.tree.column(col, width=120, anchor='w')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)

        # ### --- FRAME FORM DIBUAT SCROLLABLE SECARA HORIZONTAL --- ###
        form_container = ttk.LabelFrame(main_frame, text="Detail Reservasi", padding=(10, 5))
        form_container.pack(fill=tk.X)

        canvas = tk.Canvas(form_container, borderwidth=0, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

        x_scrollbar_visible = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
        x_scrollbar_visible.pack(fill=tk.X, padx=10, pady=(0,5))
        
        canvas.configure(xscrollcommand=x_scrollbar_visible.set)
        
        scrollable_form_frame = ttk.Frame(canvas, padding=(0, 5))
        canvas.create_window((0, 0), window=scrollable_form_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.config(height=scrollable_form_frame.winfo_height())

        scrollable_form_frame.bind("<Configure>", on_frame_configure)
        
        self.entries = {}
        # Menghapus 'KELAS' dari widget_configs karena 'PRODI' sudah ada
        widget_configs = {
            'HARI': {'widget': ttk.Combobox, 'options': {'values': ALLOWED_DAYS, 'width': 15}},
            'DOSEN': {'widget': ttk.Combobox, 'options': {'values': DOSEN_LIST, 'width': 30}},
            'MATAKULIAH': {'widget': ttk.Combobox, 'options': {'values': MATAKULIAH_LIST, 'width': 30}},
            'PRODI': {'widget': ttk.Combobox, 'options': {'values': PRODI_LIST, 'width': 20}},
            'SEMESTER': {'widget': ttk.Combobox, 'options': {'values': SEMESTER_LIST, 'width': 10}},
            'SKS': {'widget': ttk.Combobox, 'options': {'values': SKS_LIST, 'width': 10}},
            'KELAS': {'widget': ttk.Combobox, 'options': {'values': RUANG_B_STANDARD, 'width': 10}}, # KELAS diubah jadi Entry biasa
            'MODE': {'widget': ttk.Combobox, 'options': {'values': MODE_LIST, 'width': 15}},
            'GEDUNG': {'widget': ttk.Combobox, 'options': {'values': list(AVAILABLE_ROOMS.keys()), 'width': 10}},
            'LANTAI': {'widget': ttk.Combobox, 'options': {'width': 10}},
            'RUANGAN': {'widget': ttk.Combobox, 'options': {'width': 10}},
            'MULAI': {'widget': ttk.Entry, 'options': {'width': 10}},
            'SELESAI': {'widget': ttk.Entry, 'options': {'width': 10}}
        }

        for i, label in enumerate(KOLOM_FORM):
            if label not in widget_configs: continue
            config = widget_configs[label]
            
            field_frame = ttk.Frame(scrollable_form_frame)
            field_frame.grid(row=0, column=i, padx=5, pady=0, sticky='ns')
            
            lbl = ttk.Label(field_frame, text=label)
            lbl.pack(pady=(0,2), anchor='w')
            
            widget = config['widget'](field_frame, **config.get('options', {}))
            if isinstance(widget, ttk.Combobox):
                widget.config(state='readonly')
            
            widget.pack(anchor='w')
            self.entries[label] = widget
        
        # --- MODIFIKASI EVENT BINDING ---
        self.entries['MODE'].bind('<<ComboboxSelected>>', self.on_mode_select)
        self.entries['GEDUNG'].bind('<<ComboboxSelected>>', self.update_floor_options)
        self.entries['LANTAI'].bind('<<ComboboxSelected>>', self.update_room_options)
        # --- AKHIR MODIFIKASI EVENT BINDING ---

        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Tambah", command=self.add_reservation).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(button_frame, text="Update", command=self.update_reservation).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(button_frame, text="Hapus", command=self.delete_reservation).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(button_frame, text="Ekspor", command=self.export_to_excel).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.populate_treeview()
        self.on_mode_select()

    def adjust_column_widths(self):
        cols_to_adjust = ['DOSEN', 'MATAKULIAH']
        try:
            font_config = self.tree.heading(cols_to_adjust[0])
            heading_font = tkfont.Font(font=font_config["font"])
        except (tk.TclError, IndexError, KeyError):
            heading_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        for col in cols_to_adjust:
            max_len = heading_font.measure(col.title())
            if not self.df.empty and col in self.df:
                try:
                    longest_item_index = self.df[col].astype(str).map(len).idxmax()
                    longest_item_value = self.df.loc[longest_item_index, col]
                    if pd.notna(longest_item_value):
                        measured_len = heading_font.measure(str(longest_item_value))
                        max_len = max(max_len, measured_len)
                except ValueError:
                    pass
            self.tree.column(col, width=max_len + 20)

    def populate_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i, row in self.df.iterrows():
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=list(row.astype(str)), tags=(tag,))
        self.adjust_column_widths()

    def on_item_select(self, event):
        if not self.tree.selection(): return
        selected_item = self.tree.selection()[0]
        item_values = self.tree.item(selected_item, 'values')
        values_dict = dict(zip(KOLOM_WAJIB, item_values))
        self.clear_form(clear_selection=False)
        for key in KOLOM_FORM:
            if key in self.entries and key in values_dict:
                value = values_dict[key]
                if value == 'nan': value = ''
                if isinstance(self.entries[key], ttk.Combobox):
                    self.entries[key].set(value)
                else:
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, value)
        self.on_mode_select()
        if self.entries['MODE'].get() == 'OFFLINE': 
            self.update_floor_options()
            self.update_room_options()
    
    def _get_and_validate_form_data(self):
        data = {key: widget.get().strip() for key, widget in self.entries.items()}
        required_fields = [f for f in KOLOM_FORM if f not in ['GEDUNG', 'LANTAI', 'RUANGAN', 'PRODI']] # Prodi tidak wajib
        for field in required_fields:
            if not data.get(field):
                messagebox.showerror("Input Tidak Lengkap", f"Kolom '{field}' harus diisi.")
                return None
        mode = data.get('MODE')
        if mode == 'OFFLINE':
            for field in ['GEDUNG', 'LANTAI', 'RUANGAN']:
                if not data.get(field) or data.get(field) == '-':
                    messagebox.showerror("Input Tidak Lengkap", f"Untuk mode OFFLINE, kolom '{field}' harus diisi.")
                    return None
        try:
            data['LANTAI_INT'] = int(float(data.get('LANTAI', 0))) if mode == 'OFFLINE' else 0
            data['SEMESTER_INT'] = int(float(data['SEMESTER']))
            data['SKS_INT'] = int(float(data['SKS']))
        except (ValueError, TypeError):
            messagebox.showerror("Input Salah", "Kolom numerik (Lantai, Semester, SKS) harus berupa angka.")
            return None
        valid, msg = is_time_slot_valid(data['MULAI'], data['SELESAI'])
        if not valid:
            messagebox.showerror("Error Waktu", msg)
            return None
        return data

    def add_reservation(self):
        data = self._get_and_validate_form_data()
        if data is None: return
        if data.get('MODE') == 'OFFLINE':
            valid, msg = is_room_available(self.df, data['HARI'].upper(), data['MULAI'], data['SELESAI'], data['GEDUNG'], data['LANTAI_INT'], data['RUANGAN'])
            if not valid:
                messagebox.showerror("Jadwal Bentrok", msg)
                return
        new_data = {
            'HARI': data['HARI'].upper(), 'DOSEN': data['DOSEN'], 'MATAKULIAH': data['MATAKULIAH'],
            'PRODI': data['PRODI'], 'SEMESTER': str(data['SEMESTER_INT']), 'SKS': str(data['SKS_INT']),
            'KELAS': data['KELAS'].upper(), 'MODE': data['MODE'],
            'GEDUNG': data['GEDUNG'] if data['MODE'] == 'OFFLINE' else '-',
            'LANTAI': str(data['LANTAI_INT']) if data['MODE'] == 'OFFLINE' else '-',
            'RUANGAN': data['RUANGAN'] if data['MODE'] == 'OFFLINE' else '-',
            'MULAI': data['MULAI'], 'SELESAI': data['SELESAI'], 
            'TANGGAL_DIBUAT': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        new_df = pd.DataFrame([new_data])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        messagebox.showinfo("Sukses", "Reservasi berhasil ditambahkan.")
        self.save_data_auto()
        self.populate_treeview()
        self.clear_form()

    def update_reservation(self):
        if not self.tree.selection():
            messagebox.showwarning("Peringatan", "Pilih data yang ingin diupdate.")
            return
        selected_iid = self.tree.selection()[0]
        df_index_to_update = self.tree.index(selected_iid)
        data = self._get_and_validate_form_data()
        if data is None: return
        if data.get('MODE') == 'OFFLINE':
            valid, msg = is_room_available(self.df, data['HARI'].upper(), data['MULAI'], data['SELESAI'], data['GEDUNG'], data['LANTAI_INT'], data['RUANGAN'], ignore_index=df_index_to_update)
            if not valid:
                messagebox.showerror("Jadwal Bentrok", msg)
                return
        updated_row_data = {
            'HARI': data['HARI'].upper(), 'DOSEN': data['DOSEN'], 'MATAKULIAH': data['MATAKULIAH'],
            'PRODI': data['PRODI'], 'SEMESTER': str(data['SEMESTER_INT']), 'SKS': str(data['SKS_INT']),
            'KELAS': data['KELAS'].upper(), 'MODE': data['MODE'],
            'GEDUNG': data['GEDUNG'] if data['MODE'] == 'OFFLINE' else '-',
            'LANTAI': str(data['LANTAI_INT']) if data['MODE'] == 'OFFLINE' else '-',
            'RUANGAN': data['RUANGAN'] if data['MODE'] == 'OFFLINE' else '-',
            'MULAI': data['MULAI'], 'SELESAI': data['SELESAI']
        }
        for col, value in updated_row_data.items():
            self.df.loc[df_index_to_update, col] = value
        messagebox.showinfo("Sukses", "Reservasi berhasil diperbarui.")
        self.save_data_auto()
        self.populate_treeview()
        self.clear_form()

    def delete_reservation(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Peringatan", "Pilih data yang ingin dihapus.")
            return
        if messagebox.askyesno("Konfirmasi Hapus", "Yakin ingin menghapus data yang dipilih?"):
            indices_to_drop = [self.tree.index(item) for item in selected_items]
            self.df = self.df.drop(indices_to_drop).reset_index(drop=True)
            self.save_data_auto()
            self.populate_treeview()
            self.clear_form()
            messagebox.showinfo("Sukses", "Reservasi berhasil dihapus.")

    def load_data(self):
        try:
            df = pd.read_excel(NAMA_FILE_EXCEL)
            for col in KOLOM_WAJIB:
                if col not in df.columns: df[col] = ''
            return df[KOLOM_WAJIB].astype(str)
        except FileNotFoundError:
            return pd.DataFrame(columns=KOLOM_WAJIB)
        except Exception as e:
            messagebox.showerror("Error Memuat Data", f"Gagal memuat file Excel:\n{e}")
            return pd.DataFrame(columns=KOLOM_WAJIB)

    def save_data_auto(self):
        try:
            self.df.to_excel(NAMA_FILE_EXCEL, index=False)
        except Exception as e:
            messagebox.showerror("Error Penyimpanan Otomatis", f"Gagal menyimpan ke {NAMA_FILE_EXCEL}:\n{e}")

    def export_to_excel(self):
        if self.df.empty:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diekspor.")
            return
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")], title="Simpan Data Reservasi")
            if file_path:
                self.df.to_excel(file_path, index=False)
                messagebox.showinfo("Sukses", f"Data berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error Ekspor", f"Gagal mengekspor file:\n{e}")

    def on_mode_select(self, event=None):
        mode = self.entries['MODE'].get()
        location_widgets = [self.entries['GEDUNG'], self.entries['LANTAI'], self.entries['RUANGAN']]
        if mode == 'ONLINE':
            for widget in location_widgets:
                widget.set('-')
                widget.config(state='disabled')
        else:
            for widget in location_widgets:
                widget.config(state='readonly')
            if self.entries['GEDUNG'].get() in ('', '-'):
                self.entries['GEDUNG'].set('')
                self.update_floor_options()
    
    # --- FUNGSI LAMA 'update_location_options' DIHAPUS DAN DIGANTI DENGAN 2 FUNGSI DI BAWAH INI ---

    def update_floor_options(self, event=None):
        """Dipanggil saat Gedung dipilih. Mengisi pilihan Lantai."""
        selected_gedung = self.entries['GEDUNG'].get()
        # Kosongkan pilihan lantai dan ruangan berikutnya
        self.entries['LANTAI'].set('')
        self.entries['RUANGAN'].set('')
        self.entries['LANTAI']['values'] = []
        self.entries['RUANGAN']['values'] = []

        if selected_gedung and selected_gedung in AVAILABLE_ROOMS:
            # Ambil nomor lantai dari keys dictionary 'floors'
            floor_numbers = list(AVAILABLE_ROOMS[selected_gedung]['floors'].keys())
            self.entries['LANTAI']['values'] = floor_numbers

    def update_room_options(self, event=None):
        """Dipanggil saat Lantai dipilih. Mengisi pilihan Ruangan."""
        selected_gedung = self.entries['GEDUNG'].get()
        selected_lantai_str = self.entries['LANTAI'].get()

        # Kosongkan pilihan ruangan
        self.entries['RUANGAN'].set('')
        self.entries['RUANGAN']['values'] = []
        self.entries['RUANGAN'].config(state='readonly') # Aktifkan kembali secara default

        if selected_gedung in AVAILABLE_ROOMS and selected_lantai_str:
            try:
                # Konversi lantai ke integer untuk lookup di dictionary
                selected_lantai = int(selected_lantai_str)
                if selected_lantai in AVAILABLE_ROOMS[selected_gedung]['floors']:
                    # Ambil daftar ruangan berdasarkan gedung dan lantai yang dipilih
                    room_options = AVAILABLE_ROOMS[selected_gedung]['floors'][selected_lantai]
                    self.entries['RUANGAN']['values'] = room_options

                    # Jika satu-satunya pilihan adalah '-', otomatis pilih dan nonaktifkan
                    if len(room_options) == 1 and room_options[0] == '-':
                        self.entries['RUANGAN'].set(room_options[0])
                        self.entries['RUANGAN'].config(state='disabled')
                    else:
                        # Jika ada pilihan lain, pastikan combobox bisa dipilih
                        self.entries['RUANGAN'].config(state='readonly')
            except (ValueError, KeyError):
                # Abaikan jika terjadi error (misal, input lantai belum valid)
                pass

    def clear_form(self, clear_selection=True):
        if clear_selection and self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        for widget in self.entries.values():
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            else:
                widget.delete(0, tk.END)
        self.on_mode_select()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservationApp(root)
    root.mainloop()