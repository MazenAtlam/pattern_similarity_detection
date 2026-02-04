import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import glob
import json
import sys

# Add current dir to path
sys.path.append(os.path.dirname(__file__))

from pattern_matcher_v3 import FingerprintDatabaseV3
from visualizer import plot_scene, draw_pitch

class FIFA_App_V3:
    def __init__(self, root):
        self.root = root
        self.root.title("FIFA World Cup 2022 - Similar Plays (V3: Strict Vector Similarity)")
        self.root.geometry("1400x900")
        
        # State
        self.db = None
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # code/
        self.data_dir = os.path.join(self.base_dir, 'version_3_more_than_one_pass', 'data')
        self.metadata_dir = os.path.join(self.base_dir, 'data', 'Metadata')
        
        self.match_list = []
        self.current_match_plays = []
        self.current_play_idx = 0
        self.search_results = []
        self.selected_result_idx = None
        
        # UI init
        self.setup_ui()
        self.load_metadata()
        
        if not os.path.dirname(self.data_dir):
            # Fallback if I got the relative path wrong
             self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
             
        self.db = FingerprintDatabaseV3(base_data_dir=self.data_dir)
        self.lbl_status.config(text=f"Database Loaded (L=1).")
        
    def load_metadata(self):
        """Scans Metadata folder to populate match list."""
        self.match_list = []
        files = glob.glob(os.path.join(self.metadata_dir, "*.json"))
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)[0]
                    home = data['homeTeam']['name']
                    away = data['awayTeam']['name']
                    game_id = data['id']
                    label = f"{home} vs {away} ({game_id})"
                    self.match_list.append({'label': label, 'id': game_id, 'file': f})
            except Exception as e:
                print(f"Error loading meta {f}: {e}")
        self.match_list.sort(key=lambda x: x['label'])
        self.cb_matches['values'] = [m['label'] for m in self.match_list]

    def setup_ui(self):
        # 1. Top Controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Match Selector
        ttk.Label(control_frame, text="Select Match:").pack(side=tk.LEFT, padx=5)
        self.cb_matches = ttk.Combobox(control_frame, width=40, state="readonly")
        self.cb_matches.pack(side=tk.LEFT, padx=5)
        self.cb_matches.bind('<<ComboboxSelected>>', self.on_match_selected)
        
        # Sequence Length Selector
        ttk.Label(control_frame, text="Seq Length:").pack(side=tk.LEFT, padx=15)
        self.spin_len = ttk.Spinbox(control_frame, from_=1, to=10, width=3, command=self.on_length_changed)
        self.spin_len.set(1)
        self.spin_len.pack(side=tk.LEFT, padx=5)
        self.spin_len.bind('<Return>', self.on_length_changed) # Also on Enter
        
        self.lbl_status = ttk.Label(control_frame, text="Loading...")
        self.lbl_status.pack(side=tk.LEFT, padx=20)
        
        # Navigation
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.RIGHT)
        ttk.Button(nav_frame, text="< Prev", command=self.prev_play).pack(side=tk.LEFT)
        self.lbl_play_counter = ttk.Label(nav_frame, text="Play: 0 / 0")
        self.lbl_play_counter.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="Next >", command=self.next_play).pack(side=tk.LEFT)
        
        ttk.Button(nav_frame, text="🔍 Find Similar Play", command=self.find_similar).pack(side=tk.LEFT, padx=20)

        # 2. Main Content
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel: Visualizer
        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=3)
        
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=left_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Right Panel: Results
        right_panel = ttk.Labelframe(paned, text="Search Results (Similar Plays)")
        paned.add(right_panel, weight=1)
        
        self.list_results = tk.Listbox(right_panel, font=("Consolas", 10))
        self.list_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.list_results.bind('<<ListboxSelect>>', self.on_result_select)

    def on_length_changed(self):
        try:
            val = int(self.spin_len.get())
        except:
            return
            
        if self.db.current_length != val:
            print(f"Switching to Length {val}...")
            self.db.load_level(val)
            self.lbl_status.config(text=f"Database Loaded (L={val}). Reload match to refresh plays.")
            # We should try to re-filter the *current* match if selected
            self.on_match_selected(None)

    def on_match_selected(self, event):
        if self.cb_matches.current() < 0: return
        idx = self.cb_matches.current()
        match_id = self.match_list[idx]['id']
        
        # Need to query the current DB for plays from this match
        if not self.db.database: return
        
        self.current_match_plays = [
            p for p in self.db.database
            if str(p['game_id']) == str(match_id)
        ]
        self.current_match_plays.sort(key=lambda x: x['timestamp'])
        
        self.current_play_idx = 0
        if self.current_match_plays:
            self.lbl_status.config(text=f"Loaded {len(self.current_match_plays)} sequences (L={self.db.current_length}) for {match_id}.")
            self.update_ui()
        else:
            self.lbl_status.config(text=f"No sequences found for {match_id} (L={self.db.current_length}).")
            self.ax.clear()
            self.canvas.draw()
            
    def update_ui(self):
        if not self.current_match_plays: return
        play = self.current_match_plays[self.current_play_idx]
        
        self.lbl_play_counter.config(text=f"Play: {self.current_play_idx + 1} / {len(self.current_match_plays)}")
        
        # Clear selected result if we move
        self.selected_result_idx = None
        self.list_results.selection_clear(0, tk.END)
        self.search_results = []
        self.list_results.delete(0, tk.END)
        
        plot_scene(self.ax, play, title=f"Time: {play['timestamp']:.1f}s | Length: {play['length']}")
        self.canvas.draw()
        
    def find_similar(self):
        if not self.current_match_plays: return
        
        query = self.current_match_plays[self.current_play_idx]
        print(f"Searching similar for {query['event_id']} (L={query['length']})...")
        
        results = self.db.find_nearest_neighbors(query, top_k=10)
        self.search_results = results
        self.list_results.delete(0, tk.END)
        
        for r in results:
            text = f"M:{r['match']} | T:{r['timestamp']:.1f}s | D:{r['distance']:.2f}"
            self.list_results.insert(tk.END, text)
            
    def on_result_select(self, event):
        sel = self.list_results.curselection()
        if not sel: return
        
        idx = sel[0]
        result_play = self.search_results[idx]['data']
        current_play = self.current_match_plays[self.current_play_idx]
        
        # Overlay!
        plot_scene(self.ax, current_play, overlay_fingerprint=result_play, 
                   title=f"Comparison: Original vs Match {result_play['game_id']}")
        self.canvas.draw()
        
    def prev_play(self):
        if self.current_play_idx > 0:
            self.current_play_idx -= 1
            self.update_ui()

    def next_play(self):
        if self.current_play_idx < len(self.current_match_plays) - 1:
            self.current_play_idx += 1
            self.update_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = FIFA_App_V3(root)
    root.mainloop()
