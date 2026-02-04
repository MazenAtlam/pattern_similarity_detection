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

def extract_chains_from_match(file_path):
    """
    Extracts chains of consecutive passes from a match.
    Returns a list of chains, where each chain is a list of consecutive 'PA' events.
    """
    events = load_json(file_path)
    
    # Sort by time just in case
    # events.sort(key=lambda x: x.get('eventTime', 0)) 
    
    chains = []
    current_chain = []
    
    for i, event in enumerate(events):
        pos_evt = event.get('possessionEvents')
        if not pos_evt: continue
        
        # We look for Passes
        if pos_evt.get('possessionEventType') != 'PA':
            # If we hit a non-pass event that changes possession or stops play, break chain?
            # Actually, sometimes minor events happen in between.
            # But "Consecutive Passes" usually implies direct sequence.
            # If team changes, definitely break.
            # If time gap is large, break.
            continue

        # Extract basic info
        team_id = event['gameEvents']['teamId']
        
        # Check if we continue chain
        if not current_chain:
            current_chain.append(event)
        else:
            last_event = current_chain[-1]
            last_team = last_event['gameEvents']['teamId']
            
            # Constraint 1: Same Team
            if team_id != last_team:
                chains.append(current_chain)
                current_chain = [event]
            else:
                # Constraint 2: Consecutive?
                # We assume if they appear in order in JSON and are same team passes, they are consecutive.
                # One check: 'passerPlayerId' of current should match 'targetPlayerId' of previous ideally?
                # Or just generally "Team kept the ball".
                # User said "consecutive passes that are next to each other".
                # Let's verify temporal proximity?
                # For now, let's treat "Sequence of Pasess by Team A" as a chain.
                # If there's an interception or unknown event in between, it often breaks the flow.
                # But filtering only "PA" might skip "Dribble" in between.
                # User asked for "Number of passes". 
                # Strict interpretation: P1 -> P2 -> P3.
                current_chain.append(event)
    
    if current_chain:
        chains.append(current_chain)
        
    return chains

def get_event_fingerprint(event, next_event=None):
    """
    Extracts single-pass features (start, end, players).
    """
    # ... (Logic similar to V2 but returns dict) ...
    stadium_meta = event.get('stadiumMetadata')
    attack_dir_val = stadium_meta.get('teamAttackingDirection') if stadium_meta else 'R'
    norm_factor = 1.0 if attack_dir_val == 'R' else -1.0
    
    ball = event.get('ball')
    if not ball: return None
    
    ball_x = ball[0]['x'] * norm_factor
    ball_y = ball[0]['y'] * norm_factor
    
    pass_end_x = ball_x
    pass_end_y = ball_y
    
    if next_event:
        nb = next_event.get('ball')
        if nb:
            pass_end_x = nb[0]['x'] * norm_factor
            pass_end_y = nb[0]['y'] * norm_factor
            
    # Players
    home_team_id = event['homePlayers'][0]['teamId'] if event.get('homePlayers') else None # Approx
    # Better: get from Metadata passed in? Or infer.
    # Actually 'teamId' in event tells us attacking team.
    attacking_team_id = event['gameEvents']['teamId']
    
    teammates = []
    opponents = []
    
    for p in event.get('homePlayers', []):
        px = p['x'] * norm_factor
        py = p['y'] * norm_factor
        if str(p.get('teamId', '')) == str(attacking_team_id) or not p.get('teamId'): # Fallback
             # Wait, homePlayers usually all belong to home team?
             # Let's assume homePlayers list is Home Team.
             # We need to know who is who.
             pass 
             
    # Simpler: just use the arrays.
    # But we need Attack v Def.
    # event['homePlayers'] are the players of Home Team.
    # event['awayPlayers'] are Away Team.
    
    # We need home/away team IDs from metadata or assume consistent?
    # Let's rely on 'attacking_team_id'.
    # We don't have easy access to HomeTeamID in just the event without context.
    # But usually we can check against 'gameEvents.teamId'.
    
    # Re-using V2 logic for player extraction
    # Need to pass home/away IDs or infer.
    # V2 load_metadata approach was good.
    return {
        'timestamp': event.get('eventTime'),
        'ball_x': ball_x, 'ball_y': ball_y,
        'pass_end_x': pass_end_x, 'pass_end_y': pass_end_y,
        'attacking_team_id': attacking_team_id,
        # Store players raw for now, refine in loop
        'home_players': [{'x': p['x']*norm_factor, 'y': p['y']*norm_factor} for p in event.get('homePlayers',[])],
        'away_players': [{'x': p['x']*norm_factor, 'y': p['y']*norm_factor} for p in event.get('awayPlayers',[])]
    }

def process_all_files():
    # Load all metadata first to map GameID -> Home/Away IDs
    game_meta = {}
    meta_files = glob.glob(os.path.join(METADATA_DIR, '*.json'))
    for mf in meta_files:
        try:
            m = load_json(mf)[0]
            game_meta[str(m['id'])] = {
                'home': str(m['homeTeam']['id']), 
                'away': str(m['awayTeam']['id'])
            }
        except: pass
        
    # Databases by length: 1 to 10
    dbs = {i: [] for i in range(1, 11)}
    
    files = glob.glob(os.path.join(EVENT_DATA_DIR, '*.json'))
    
    for f in tqdm(files):
        filename = os.path.basename(f)
        game_id = filename.split('.')[0]
        if game_id not in game_meta: continue
        
        meta = game_meta[game_id]
        
        chains = extract_chains_from_match(f)
        
        for chain in chains:
            # We have a chain of N passes.
            # We can extract sub-sequences of lengths 1..N (up to 10)
            
            # Start of chain is index 0.
            # We only generate sequences starting from the *beginning* of the chain?
            # Or sliding window?
            # User said "different number of passes". 
            # Usually meant "Find me a 3-pass play".
            # Could be passes 3,4,5 of a long chain.
            # Let's do sliding window over the chain.
            
            L = len(chain)
            
            for length in range(1, 11):
                if length > L: break
                
                # Sliding window
                for start_idx in range(L - length + 1):
                    # Sequence of 'length' passes
                    sub_seq = chain[start_idx : start_idx + length]
                    
                    # Compute Fingerprint for this sequence
                    # Feature 1: Vectors
                    vectors = []
                    start_evt = sub_seq[0]
                    # Get End coords for each pass
                    # Note: pass_end of sub_seq[i] is ball_start of sub_seq[i+1] usually.
                    # For total last pass, we look ahead in 'chain' if possible, or use end of that event (derived from next event in full list).
                    # 'extract_chains' logic kept simple events. we might need to look at 'next event in raw file'.
                    
                    # Let's assume extract_chains returns enough info.
                    # Actually, we need to re-parse.
                    
                    # Refined approach:
                    # process_match computes fingerprints for ALL passes first (V2 style),
                    # then links them into chains.
                    pass
        
    # Start Over with clearer flow
    pass

def process_match_refined(file_path, game_meta_entry, dbs):
    game_id = str(game_meta_entry['id']) # wait, ID is key
    home_id = game_meta_entry['home']
    away_id = game_meta_entry['away']
    
    events = load_json(file_path)
    
    # 1. Parse all valid Passes into a structured list
    pass_list = []
    
    for i, event in enumerate(events):
        pos_evt = event.get('possessionEvents')
        if not pos_evt or pos_evt.get('possessionEventType') != 'PA':
            continue
            
        # Get coordinates
        stadium_meta = event.get('stadiumMetadata')
        attack_dir_val = stadium_meta.get('teamAttackingDirection') if stadium_meta else 'R'
        norm_factor = 1.0 if attack_dir_val == 'R' else -1.0
        
        ball = event.get('ball')
        if not ball: continue
        
        bx = ball[0]['x'] * norm_factor
        by = ball[0]['y'] * norm_factor
        
        # End coordinates (look ahead in raw events)
        ex, ey = bx, by
        if i + 1 < len(events):
            next_ball = events[i+1].get('ball')
            if next_ball:
                ex = next_ball[0]['x'] * norm_factor
                ey = next_ball[0]['y'] * norm_factor
                
        # Players (Relative to Ball Start)
        teammates = []
        opponents = []
        attack_team = event['gameEvents']['teamId']
        
        # Quick extract
        for p in event.get('homePlayers', []):
            px, py = p['x'] * norm_factor, p['y'] * norm_factor
            if str(home_id) == str(attack_team): teammates.append((px - bx, py - by))
            else: opponents.append((px - bx, py - by))
            
        for p in event.get('awayPlayers', []):
            px, py = p['x'] * norm_factor, p['y'] * norm_factor
            if str(away_id) == str(attack_team): teammates.append((px - bx, py - by))
            else: opponents.append((px - bx, py - by))
            
        pass_entry = {
            'game_id': str(game_id), # Ensure string
            'event_id': event['gameEventId'],
            'timestamp': event['eventTime'],
            'team_id': attack_team,
            'start_x': bx, 'start_y': by,
            'end_x': ex, 'end_y': ey,
            'vector': (ex - bx, ey - by),
            'teammates': teammates,
            'opponents': opponents
        }
        pass_list.append(pass_entry)
        
    # 2. Build Chains
    # A chain is consecutive passes by same team
    # We iterate pass_list. If team changes, break chain.
    # Note: pass_list only has 'PA' events. So this skips intercepted passes automatically?
    # Cons: If Team A passes, then Team A Dribbles, then Team A passes... is it a chain? 
    # User said "consecutive passes". P1->P2.
    # We will assume contiguous in pass_list + Same Team = Chain.
    
    current_chain = []
    
    for p in pass_list:
        if not current_chain:
            current_chain.append(p)
            continue
            
        last = current_chain[-1]
        
        # Check Team
        if p['team_id'] == last['team_id']:
            # Check Time Gap? (e.g. < 5 seconds between end of last and start of current?)
            # Let's be lenient.
            current_chain.append(p)
        else:
            # Process Chain
            save_chain_to_dbs(current_chain, dbs)
            current_chain = [p]
            
    if current_chain:
        save_chain_to_dbs(current_chain, dbs)

def save_chain_to_dbs(chain, dbs):
    # Retrieve chains of length 1 to 10
    L = len(chain)
    
    for length in range(1, 11):
        if length > L: break
        
        # Sliding window
        for i in range(L - length + 1):
            seq = chain[i : i+length]
            
            # Create Entry
            # Features: 
            # - Start X,Y (of first pass)
            # - List of Vectors
            # - Players (of first pass only, or all? Usually first pass sets the scene)
            
            first = seq[0]
            vectors = [s['vector'] for s in seq]
            
            entry = {
                'game_id': first['game_id'],
                'event_id': first['event_id'], # ID of first pass
                'timestamp': first['timestamp'],
                'length': length,
                'start_x': first['start_x'],
                'start_y': first['start_y'],
                'vectors': vectors, # List of (dx, dy)
                'teammates': first['teammates'], # Snapshot at start
                'opponents': first['opponents']
            }
            dbs[length].append(entry)

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    # Load Meta
    game_meta = {}
    for mf in glob.glob(os.path.join(METADATA_DIR, '*.json')):
        try:
            m = load_json(mf)[0]
            game_meta[str(m['id'])] = {'id': m['id'], 'home': m['homeTeam']['id'], 'away': m['awayTeam']['id']}
        except: pass
        
    # DBs
    dbs = {i: [] for i in range(1, 11)}
    
    files = glob.glob(os.path.join(EVENT_DATA_DIR, '*.json'))
    
    print("Processing matches...")
    for f in tqdm(files):
        try:
            filename = os.path.basename(f)
            gid = filename.split('.')[0]
            if gid in game_meta:
                process_match_refined(f, game_meta[gid], dbs)
        except Exception as e:
            print(f"Error {f}: {e}")
            
    # Save
    print("Saving databases...")
    for i in range(1, 11):
        path = os.path.join(OUTPUT_DIR, f'fingerprints_{i}pass.pkl')
        with open(path, 'wb') as f:
            pickle.dump(dbs[i], f)
        print(f"Saved L={i}: {len(dbs[i])} entries.")

if __name__ == '__main__':
    main()
