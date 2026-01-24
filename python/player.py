#made by wdibt ^.^
#DO NOT USE THE LATEST PYTHON (3.14+) PLEASE USE 3.13.11 OR OLDER.
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2, serial, time, threading, os, tempfile
import numpy as np
from PIL import Image, ImageTk
import serial.tools.list_ports
import pygame

# --- moviepy check ---
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy import VideoFileClip
    except ImportError:
        VideoFileClip = None

class BadAppleStreamerV312:
    def __init__(self, root):
        self.root = root
        self.root.title("BadAppleDuino v2.0.0")
        self.root.geometry("620x860")
        self.root.configure(bg="#0d0d0d")
        
        # --- params ---
        self.W, self.H = 128, 64
        self.active = False
        self.seeking = False
        self.seek_to_frame = -1
        self.v_ready = False
        self.audio_ready = False
        self.temp_audio_path = os.path.join(tempfile.gettempdir(), "bad_apple_temp.mp3")
        
        self.port = tk.StringVar()
        self.baud = tk.IntVar(value=2000000)
        self.threshold = tk.IntVar(value=127)
        self.realtime_sync = tk.BooleanVar(value=True)
        self.loop = tk.BooleanVar(value=True)
        self.volume = tk.IntVar(value=50)
        
        self.total_f = 0
        self.orig_fps = 30.0
        self.start_time = 0
        
        pygame.mixer.init()
        self.build_ui()
        self.scan_ports()

    def build_ui(self):
        # style cfg (manual colors for tk, style for ttk)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", foreground="#00ff41", background="#0d0d0d")
        style.configure("TLabelframe", foreground="#00ff41", background="#0d0d0d")
        style.configure("TLabelframe.Label", foreground="#00ff41", background="#0d0d0d")

        # [ io cfg ]
        io = ttk.LabelFrame(self.root, text=" [ SERIAL PORT ] ", padding=10)
        io.pack(fill="x", padx=20, pady=10)
        ttk.Label(io, text="PORT:").grid(row=0, column=0)
        self.cb_port = ttk.Combobox(io, textvariable=self.port, width=15)
        self.cb_port.grid(row=0, column=1, padx=10)
        ttk.Button(io, text="SCAN", command=self.scan_ports).grid(row=0, column=2)
        ttk.Label(io, text="BAUD:").grid(row=0, column=3, padx=10)
        ttk.Entry(io, textvariable=self.baud, width=12).grid(row=0, column=4)

        # [ media src ]
        f_p = ttk.LabelFrame(self.root, text=" [ VIDEO SOURCE ] ", padding=10)
        f_p.pack(fill="x", padx=20, pady=5)
        ttk.Button(f_p, text="SELECT VIDEO", command=self.load_v).pack(side="left")
        self.lbl_v_name = ttk.Label(f_p, text="No file...", font=("Consolas", 8))
        self.lbl_v_name.pack(side="left", padx=15)
        self.lbl_audio_stat = ttk.Label(f_p, text="[AUDIO: N/A]", foreground="#ffaa00")
        self.lbl_audio_stat.pack(side="right")

        # [ engine ] - use tk.frame to fix bg bug
        mid = tk.Frame(self.root, bg="#0d0d0d")
        mid.pack(fill="x", padx=20, pady=10)
        
        eng = ttk.LabelFrame(mid, text=" [ PROCESSOR ] ", padding=10)
        eng.pack(side="left", fill="both", expand=True)
        ttk.Label(eng, text="B/W THRESHOLD:").pack()
        tk.Scale(eng, from_=0, to=255, orient="horizontal", variable=self.threshold, 
                 bg="#0d0d0d", fg="#00ff41", highlightthickness=0).pack(fill="x")
        ttk.Checkbutton(eng, text="REALTIME SYNC", variable=self.realtime_sync).pack(anchor="w")
        ttk.Checkbutton(eng, text="LOOP VIDEO", variable=self.loop).pack(anchor="w")

        # [ audio ]
        aud = ttk.LabelFrame(mid, text=" [ AUDIO ] ", padding=10)
        aud.pack(side="right", fill="both", expand=True, padx=(10,0))
        ttk.Label(aud, text="VOLUME:").pack()
        tk.Scale(aud, from_=0, to=100, orient="horizontal", variable=self.volume, 
                 command=self.set_vol, bg="#0d0d0d", fg="#00ff41", highlightthickness=0).pack(fill="x")

        # [ monitor ]
        mon = ttk.LabelFrame(self.root, text=" [ OLED PREVIEW ] ", padding=10)
        mon.pack(fill="both", expand=True, padx=20, pady=5)
        self.cvs = tk.Canvas(mon, width=self.W*2, height=self.H*2, bg="#000", highlightthickness=1, highlightbackground="#00ff41")
        self.cvs.pack(pady=10)
        self.lbl_fps = ttk.Label(mon, text="STREAM FPS: 0.0", font=("Consolas", 11, "bold"))
        self.lbl_fps.pack()

        # [ seek bar ] - fixed via tk.frame
        sk = tk.Frame(self.root, bg="#0d0d0d")
        sk.pack(fill="x", padx=20, pady=15)
        self.sk_var = tk.DoubleVar()
        self.sk_bar = ttk.Scale(sk, from_=0, to=100, variable=self.sk_var, orient="horizontal")
        self.sk_bar.pack(side="left", fill="x", expand=True)
        self.sk_bar.bind("<ButtonPress-1>", lambda e: setattr(self, 'seeking', True))
        self.sk_bar.bind("<ButtonRelease-1>", self.on_seek_end)
        self.lbl_time = ttk.Label(sk, text="00:00 / 00:00")
        self.lbl_time.pack(side="right", padx=10)

        self.btn_run = ttk.Button(self.root, text="START MASTER STREAM", command=self.run_toggle)
        self.btn_run.pack(fill="x", padx=40, pady=20, ipady=12)

    def scan_ports(self):
        self.cb_port['values'] = [p.device for p in serial.tools.list_ports.comports()]
        if self.cb_port['values']: self.cb_port.current(0)

    def set_vol(self, v):
        pygame.mixer.music.set_volume(int(v)/100)

    def load_v(self):
        f = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi *.mkv")])
        if not f: return
        self._v_path = f
        self.lbl_v_name.config(text=os.path.basename(f))
        
        cap = cv2.VideoCapture(f)
        self.total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.sk_bar.config(to=self.total_f)
        cap.release()
        
        self.v_ready = True
        if VideoFileClip:
            self.lbl_audio_stat.config(text="[EXTRACTING AUDIO...]", foreground="#ffaa00")
            threading.Thread(target=self.extract_audio_task, args=(f,), daemon=True).start()
        else:
            self.lbl_audio_stat.config(text="[NO MOVIEPY]", foreground="#ff0000")

    def extract_audio_task(self, path):
        try:
            clip = VideoFileClip(path)
            if clip.audio:
                clip.audio.write_audiofile(self.temp_audio_path, logger=None)
                pygame.mixer.music.load(self.temp_audio_path)
                self.audio_ready = True
                self.root.after(0, lambda: self.lbl_audio_stat.config(text="[AUDIO READY]", foreground="#00ff41"))
            clip.close()
        except:
            self.root.after(0, lambda: self.lbl_audio_stat.config(text="[AUDIO ERROR]", foreground="#ff0000"))

    def on_seek_end(self, e):
        f = int(self.sk_var.get())
        self.seek_to_frame = f
        if self.active and self.audio_ready:
            pygame.mixer.music.play(start=f/self.orig_fps)
        self.seeking = False

    def run_toggle(self):
        if not self.active:
            if not self.v_ready: return
            try:
                self.ser = serial.Serial(self.port.get(), self.baud.get(), timeout=0.1)
                self.active = True
                self.btn_run.config(text="STOP STREAM")
                threading.Thread(target=self.stream_loop, daemon=True).start()
            except Exception as e: messagebox.showerror("Serial", str(e))
        else: self.active = False

    def stream_loop(self):
        cap = cv2.VideoCapture(self._v_path)
        cur_f = self.sk_var.get()
        cap.set(cv2.CAP_PROP_POS_FRAMES, cur_f)
        self.start_time = time.time() - (cur_f / self.orig_fps)
        
        if self.audio_ready:
            pygame.mixer.music.set_volume(self.volume.get()/100)
            pygame.mixer.music.play(start=cur_f/self.orig_fps)

        fps_c, fps_t = 0, time.time()
        try:
            while self.active:
                if self.ser.in_waiting == 0:
                    time.sleep(0.001); continue
                if self.ser.read(1) != b'\xAA': continue

                if self.seek_to_frame != -1:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_to_frame)
                    self.start_time = time.time() - (self.seek_to_frame / self.orig_fps)
                    self.seek_to_frame = -1

                idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                if self.realtime_sync.get():
                    tgt = int((time.time() - self.start_time) * self.orig_fps)
                    if tgt >= self.total_f:
                        if self.loop.get():
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            self.start_time = time.time(); tgt = 0
                            if self.audio_ready: pygame.mixer.music.play(0)
                        else: break
                    if tgt > idx + 1: cap.set(cv2.CAP_PROP_POS_FRAMES, tgt)
                
                ret, frame = cap.read()
                if not ret:
                    if self.loop.get():
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0); self.start_time = time.time()
                        if self.audio_ready: pygame.mixer.music.play(0)
                        continue
                    else: break

                # oled frame proc
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                res = cv2.resize(gray, (self.W, self.H), interpolation=cv2.INTER_AREA)
                _, th = cv2.threshold(res, self.threshold.get(), 255, cv2.THRESH_BINARY)
                
                bits = (th > 128).astype(np.uint8)
                buf = bits.reshape(int(self.H/8), 8, self.W).transpose(0, 2, 1)
                packed = np.packbits(buf, axis=2, bitorder='little').tobytes()
                
                rle = bytearray()
                if packed:
                    c, p = 1, packed[0]
                    for b in packed[1:]:
                        if b == p and c < 255: c += 1
                        else:
                            rle.extend([c, p]); c, p = 1, b
                    rle.extend([c, p])
                self.ser.write(rle)

                fps_c += 1
                if idx % 5 == 0:
                    t_n = idx / self.orig_fps
                    t_t = self.total_f / self.orig_fps
                    t_s = f"{int(t_n//60):02}:{int(t_n%60):02} / {int(t_t//60):02}:{int(t_t%60):02}"
                    self.root.after(0, self.up_ui, th, idx, t_s)

                if time.time() - fps_t >= 1.0:
                    v = fps_c / (time.time() - fps_t)
                    self.root.after(0, lambda v=v: self.lbl_fps.config(text=f"STREAM FPS: {v:.1f}"))
                    fps_c, fps_t = 0, time.time()
        finally:
            cap.release(); self.ser.close(); pygame.mixer.music.stop()
            self.active = False; self.root.after(0, self.reset_gui)

    def up_ui(self, img, f, s):
        p = Image.fromarray(img).resize((self.W*2, self.H*2), Image.NEAREST)
        self.tk_i = ImageTk.PhotoImage(p)
        self.cvs.create_image(self.W, self.H, image=self.tk_i)
        self.lbl_time.config(text=s)
        if not self.seeking: self.sk_var.set(f)

    def reset_gui(self):
        self.btn_run.config(text="START MASTER STREAM")

if __name__ == "__main__":
    root = tk.Tk()
    BadAppleStreamerV312(root)
    root.mainloop()
