import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(__file__))

from data_loader import load_chunk
from dsp_utils import apply_dsp_cleaning, create_windows
from pattern_matcher import FingerprintDatabase
from visualizer import draw_pitch, plot_play, plot_signals

class FIFA_DSP_App:
    def __init__(self, root):
        self.root = root
        self.root.title("FIFA World Cup 2022 - DSP Similarity Search")
        self.root.geometry("1400x900")
        
        # State
        self.df_data = None
        self.windows = []
        self.current_window_idx = 0
        self.db = None
        self.search_results = []
        
        # Config
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.default_file = os.path.join(self.base_dir, 'data', 'Tracking Data', '3812.jsonl.bz2')
        if not os.path.exists(self.default_file):
             # Try alternate path if default doesn't exist (e.g. flat structure in some envs)
             self.default_file = os.path.join(self.base_dir, 'data', '3812_tracking_data.jsonl.bz2')

        self.setup_ui()

    def setup_ui(self):
        # 1. Top Controls Frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(control_frame, text="Load Data", command=self.load_data).pack(side=tk.LEFT, padx=5)
        
        self.lbl_status = ttk.Label(control_frame, text="Status: Ready. Please load data.")
        self.lbl_status.pack(side=tk.LEFT, padx=20)
        
        # Navigation
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.RIGHT)
        ttk.Button(nav_frame, text="< Prev", command=self.prev_window).pack(side=tk.LEFT)
        self.lbl_window = ttk.Label(nav_frame, text="Window: 0 / 0")
        self.lbl_window.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="Next >", command=self.next_window).pack(side=tk.LEFT)
        
        # Search Button
        ttk.Button(nav_frame, text="🔍 Find Similar", command=self.find_similar).pack(side=tk.LEFT, padx=10)

        # 2. Main Content Area (Paned Window)
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel: Query Window + Visualization
        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=3)
        
        # Pitch Plot
        self.fig_pitch = Figure(figsize=(6, 6), dpi=100)
        self.ax_pitch = self.fig_pitch.add_subplot(111)
        self.canvas_pitch = FigureCanvasTkAgg(self.fig_pitch, master=left_panel)
        self.canvas_pitch.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Signal Plot
        self.fig_sig = Figure(figsize=(6, 2), dpi=100)
        self.ax_sig = self.fig_sig.add_subplot(111)
        self.canvas_sig = FigureCanvasTkAgg(self.fig_sig, master=left_panel)
        self.canvas_sig.get_tk_widget().pack(fill=tk.X, expand=False, pady=5)
        
        # Search Button (Moved to Top Nav)
        # ttk.Button(left_panel, text="🔍 FIND SIMILAR PLAYS", command=self.find_similar, style="Accent.TButton").pack(fill=tk.X, pady=10)

        # Right Panel: Results
        right_panel = ttk.Labelframe(paned, text="Search Results (Top 5 Matches)")
        paned.add(right_panel, weight=1)
        
        self.results_list = tk.Listbox(right_panel, font=("Consolas", 10))
        self.results_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_list.bind('<<ListboxSelect>>', self.on_result_select)

    def load_data(self):
        filename = filedialog.askopenfilename(initialdir=os.path.dirname(self.default_file), 
                                              filetypes=[("BZ2 files", "*.bz2"), ("All files", "*.*")])
        if not filename:
            # Fallback to default for quick testing if user cancels but default exists
            if os.path.exists(self.default_file):
                 filename = self.default_file
            else:
                 return

        try:
            self.lbl_status.config(text="Loading... (this may take a moment)")
            self.root.update()
            
            # Load ~2 minutes of play for demo
            start_time = 141.0 # Kickoff
            duration = 120    # 2 minutes
            
            df_raw = load_chunk(filename, start_time, duration)
            if df_raw.empty:
                messagebox.showerror("Error", "No data loaded.")
                return
                
            self.df_data = apply_dsp_cleaning(df_raw)
            
            # Create Windows
            self.windows = create_windows(self.df_data, window_size_sec=10, overlap_percent=0.5)
            self.current_window_idx = 0
            
            # Build Database
            self.db = FingerprintDatabase()
            self.db.build_from_dataframe(self.df_data)
            
            self.update_ui()
            self.lbl_status.config(text=f"Loaded {len(self.windows)} windows. DB Built.")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.lbl_status.config(text="Error loading data.")

    def update_ui(self):
        if not self.windows: return
        
        win = self.windows[self.current_window_idx]
        
        # Labels
        self.lbl_window.config(text=f"Window: {self.current_window_idx + 1} / {len(self.windows)}")
        
        # Draw Pitch
        self.ax_pitch.clear()
        draw_pitch(self.ax_pitch)
        plot_play(self.ax_pitch, win, color='blue', label='Query Play')
        self.ax_pitch.set_title(f"Query Play (Window {self.current_window_idx})")
        self.canvas_pitch.draw()
        
        # Draw Signals
        self.ax_sig.clear()
        plot_signals(self.ax_sig, win)
        self.ax_sig.set_title("X/Y Signal Components (Time Domain)")
        self.canvas_sig.draw()

    def prev_window(self):
        if self.current_window_idx > 0:
            self.current_window_idx -= 1
            self.update_ui()

    def next_window(self):
        if self.current_window_idx < len(self.windows) - 1:
            self.current_window_idx += 1
            self.update_ui()

    def find_similar(self):
        if not self.db or not self.windows:
            print("find_similar aborted: No DB or windows.")
            return
        
        try:
            print(f"DEBUG: Finding similar for window {self.current_window_idx}...")
            query_entry = self.db.database[self.current_window_idx]
            
            # Find matches
            matches = self.db.find_nearest_neighbors(query_entry, top_k=6) 
            print(f"DEBUG: Found {len(matches)} matches.")
            
            self.search_results = matches
            self.results_list.delete(0, tk.END)
            
            count_inserted = 0
            for m in matches:
                # Debug print
                print(f"DEBUG: Match Win {m['window_id']} Dist {m['distance']}")
                
                # Skip self match if dist is 0 (or very close)
                if m['window_id'] == self.current_window_idx:
                    continue
                
                text = f"Win {m['window_id']} | Time: {m['start_time']:.1f}s | Dist: {m['distance']:.2f}"
                self.results_list.insert(tk.END, text)
                count_inserted += 1
                
            if count_inserted == 0:
                 self.results_list.insert(tk.END, "No similar plays found.")
                 print("DEBUG: No similar plays found (all filtered or empty).")

        except Exception as e:
            print(f"ERROR in find_similar: {e}")
            messagebox.showerror("Search Error", str(e))
            import traceback
            traceback.print_exc()

    def on_result_select(self, event):
        selection = self.results_list.curselection()
        if not selection: return
        
        index = selection[0]
        # Map back to result list (taking into account we might have skipped self)
        # Actually simplest is to just parse the list text or store a separate list of displayed items.
        # Let's simple-parse:
        list_text = self.results_list.get(index) # "Win 5 | ..."
        win_id = int(list_text.split('|')[0].replace('Win', '').strip())
        
        # Plot Overlay
        match_win = self.windows[win_id]
        
        # We want to overlay this on the pitch view
        # Redraw original first
        self.ax_pitch.clear()
        draw_pitch(self.ax_pitch)
        
        # Plot Query
        query_win = self.windows[self.current_window_idx]
        plot_play(self.ax_pitch, query_win, color='blue', label='Query', alpha=0.6)
        
        # Plot Match
        plot_play(self.ax_pitch, match_win, color='magenta', label=f'Match (Win {win_id})', alpha=0.8)
        
        self.ax_pitch.legend()
        self.ax_pitch.set_title(f"Comparison: Query vs Match {win_id}")
        self.canvas_pitch.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = FIFA_DSP_App(root)
    root.mainloop()
