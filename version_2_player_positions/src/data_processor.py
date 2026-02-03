import json
import os
import glob
import pickle
import numpy as np
from tqdm import tqdm
import argparse

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
EVENT_DATA_DIR = os.path.join(DATA_DIR, 'Event Data')
METADATA_DIR = os.path.join(DATA_DIR, 'Metadata')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_coordinates(x, y, attack_dir='R'):
    """
    Normalizes coordinates to always be Left-to-Right attacking.
    Standard PFF coordinates: X [-52.5, 52.5], Y [-34, 34] (approx)
    If attack_dir is 'L', we flip both X and Y.
    """
    if attack_dir == 'L':
        return -x, -y
    return x, y

def process_match(file_path, fingerprints, test_mode=False):
    filename = os.path.basename(file_path)
    game_id = filename.split('.')[0]
    
    # Load Metadata to get team info (Home vs Away)
    meta_path = os.path.join(METADATA_DIR, f"{game_id}.json")
    if not os.path.exists(meta_path):
        print(f"Skipping {game_id}: Metadata not found.")
        return

    try:
        meta = load_json(meta_path)[0] # It's a list with 1 dict
        home_team_id = meta['homeTeam']['id']
        away_team_id = meta['awayTeam']['id']
        # Note: metadata might specify 'teamAttackingDirection' but it changes per half.
        # We usually rely on the event data 'stadiumMetadata' if available or infer it.
    except Exception as e:
        print(f"Error reading metadata for {game_id}: {e}")
        return

    print(f"Processing {filename}...")
    events = load_json(file_path)
    
    for i, event in enumerate(events):
        # We only care about Passes
        pos_evt = event.get('possessionEvents')
        if not pos_evt: continue
        
        if pos_evt.get('possessionEventType') != 'PA':
            continue
            
        # Basic Info
        event_id = event.get('gameEventId')
        timestamp = event.get('eventTime')
        # period = event['gameEvents']['period'] # Unused variable
        
        # Team Info
        attacking_team_id = event['gameEvents']['teamId']
        
        # 1. Determine Attacking Direction
        stadium_meta = event.get('stadiumMetadata')
        attack_dir_val = stadium_meta.get('teamAttackingDirection') if stadium_meta else 'R'
        
        norm_factor = 1.0
        if attack_dir_val == 'L':
            norm_factor = -1.0
            
        # 2. Extract Ball Start
        ball = event.get('ball')
        if not ball or not ball[0].get('visibility'):
            continue # Skip if no ball data
        
        ball_x = ball[0]['x'] * norm_factor
        ball_y = ball[0]['y'] * norm_factor
        
        # 2b. Extract Ball End (Look ahead)
        pass_end_x = ball_x # Default to start if no next event
        pass_end_y = ball_y
        
        if i + 1 < len(events):
            next_event = events[i+1]
            next_ball = next_event.get('ball')
            if next_ball and next_ball[0].get('visibility'):
                 pass_end_x = next_ball[0]['x'] * norm_factor
                 pass_end_y = next_ball[0]['y'] * norm_factor

        # 3. Extract Players
        teammates = []
        opponents = []
        
        # Home Players
        for p in event.get('homePlayers', []):
            px = p['x'] * norm_factor
            py = p['y'] * norm_factor
            
            # Categories
            if str(attacking_team_id) == str(home_team_id):
                teammates.append({'x': px, 'y': py, 'id': p['playerId']})
            else:
                opponents.append({'x': px, 'y': py, 'id': p['playerId']})
                
        # Away Players
        for p in event.get('awayPlayers', []):
            px = p['x'] * norm_factor
            py = p['y'] * norm_factor
            
            # Categories
            if str(attacking_team_id) == str(away_team_id):
                teammates.append({'x': px, 'y': py, 'id': p['playerId']})
            else:
                opponents.append({'x': px, 'y': py, 'id': p['playerId']})

        # 4. Create Feature Vector
        feats_teammates = []
        for p in teammates:
            feats_teammates.append([p['x'] - ball_x, p['y'] - ball_y])
            
        feats_opponents = []
        for p in opponents:
            feats_opponents.append([p['x'] - ball_x, p['y'] - ball_y])
        
        fingerprint = {
            'game_id': game_id,
            'event_id': event_id,
            'timestamp': timestamp,
            'ball_x': ball_x, 
            'ball_y': ball_y,
            'pass_end_x': pass_end_x,
            'pass_end_y': pass_end_y,
            'teammates_rel': feats_teammates,
            'opponents_rel': feats_opponents,
            'attacking_team_id': attacking_team_id
        }
        
        fingerprints.append(fingerprint)
        
    print(f"  Extracted {len(fingerprints)} passes from {filename}.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run on single file only')
    args = parser.parse_args()
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    fingerprints = []
    
    files = glob.glob(os.path.join(EVENT_DATA_DIR, '*.json'))
    if args.test:
        # Pick 3812.json specifically
        files = [f for f in files if '3812.json' in f]
        print("TEST MODE: Processing only 3812.json")
    
    for f in tqdm(files):
        process_match(f, fingerprints)
        
    # Save
    out_file = os.path.join(OUTPUT_DIR, 'fingerprints_db.pkl')
    with open(out_file, 'wb') as f:
        pickle.dump(fingerprints, f)
        
    print(f"Done. Saved {len(fingerprints)} fingerprints to {out_file}")

if __name__ == '__main__':
    main()
