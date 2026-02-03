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

from pattern_matcher import FingerprintDatabase
from visualizer import plot_scene, draw_pitch

class FIFA_App_V2:
    def __init__(self, root):
        self.root = root
        self.root.title("FIFA World Cup 2022 - Similar Plays (V2: Player Positions)")
        self.root.geometry("1400x900")
        
        # State
        self.db = None
        self.match_list = [] # List of dicts {label, id, filename}
        self.current_match_plays = [] # List of fingerprints for selected match
        self.current_play_idx = 0
        self.search_results = []
        
        # Paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # code/
        self.metadata_dir = os.path.join(self.base_dir, 'data', 'Metadata')
        
        # Initialize
        self.load_metadata()
        self.setup_ui()
        self.load_database()
        
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

    def load_database(self):
        """Loads the pre-computed fingerprints."""
        try:
            self.db = FingerprintDatabase() # Auto-loads from data/fingerprints_db.pkl
            self.lbl_status.config(text=f"Database Loaded: {len(self.db.database)} plays indexed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {e}")
            self.lbl_status.config(text="Database Load Failed.")

    def setup_ui(self):
        # 1. Top Controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(control_frame, text="Select Match:").pack(side=tk.LEFT, padx=5)
        
        self.cb_matches = ttk.Combobox(control_frame, width=50, state="readonly")
        self.cb_matches['values'] = [m['label'] for m in self.match_list]
        self.cb_matches.pack(side=tk.LEFT, padx=5)
        self.cb_matches.bind('<<ComboboxSelected>>', self.on_match_selected)
        
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
        
    def on_match_selected(self, event):
        idx = self.cb_matches.current()
        if idx < 0: return
        
        match_id = self.match_list[idx]['id']
        print(f"Selected match {match_id}")
        
        # Filter DB for this match
        if not self.db or not self.db.database:
            return
            
        self.current_match_plays = [
            p for p in self.db.database 
            if str(p['game_id']) == str(match_id)
        ]
        
        # Sort by event_id or timestamp
        self.current_match_plays.sort(key=lambda x: x['timestamp'])
        
        self.current_play_idx = 0
        if self.current_match_plays:
            self.update_ui()
            self.lbl_status.config(text=f"Loaded {len(self.current_match_plays)} pass events for Match {match_id}.")
        else:
            self.lbl_status.config(text=f"No pass events found for Match {match_id} in DB.")
            self.ax.clear()
            self.canvas.draw()
            
    def update_ui(self):
        if not self.current_match_plays: return
        
        play = self.current_match_plays[self.current_play_idx]
        
        self.lbl_play_counter.config(text=f"Play: {self.current_play_idx + 1} / {len(self.current_match_plays)}")
        
        plot_scene(self.ax, play, title=f"Time: {play['timestamp']:.1f}s | Event: {play['event_id']}")
        self.canvas.draw()
        
    def prev_play(self):
        if self.current_play_idx > 0:
            self.current_play_idx -= 1
            self.update_ui()
            
    def next_play(self):
        if self.current_play_idx < len(self.current_match_plays) - 1:
            self.current_play_idx += 1
            self.update_ui()
            
    def find_similar(self):
        if not self.current_match_plays: return
        
        query = self.current_match_plays[self.current_play_idx]
        print(f"Finding similar for Play Event {query['event_id']}...")
        
        results = self.db.find_nearest_neighbors(query, top_k=10)
        
        self.search_results = results
        self.list_results.delete(0, tk.END)
        
        for r in results:
            # We assume find_nearest_neighbors returns dicts with 'distance' and 'data' (the play dict)
            # as per my pattern_matcher implementation
            match_id = r['match']
            time = r['timestamp']
            dist = r['distance']
            text = f"Match {match_id} | T:{time:.1f}s | D:{dist:.2f}"
            self.list_results.insert(tk.END, text)
            
    def on_result_select(self, event):
        sel = self.list_results.curselection()
        if not sel: return
        
        idx = sel[0]
        result = self.search_results[idx]
        play_data = result['data']
        
        # Plot this result
        # Note: This momentarily diverts from the "current match navigation"
        # The visualizer will show the result.
        plot_scene(self.ax, play_data, title=f"MATCH RESULT: {result['match']} @ {result['timestamp']:.1f}s")
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = FIFA_App_V2(root)
    root.mainloop()
