import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc

def draw_pitch(ax, pitch_length=105, pitch_width=68, line_color='black'):
    """
    Draws a standard football pitch on the given Matplotlib axis.
    Dimensions are in meters (standard: 105x68).
    """
    # Pitch Outline
    ax.add_patch(Rectangle((-pitch_length/2, -pitch_width/2), pitch_length, pitch_width, 
                           linestyle='-', color=line_color, fill=False))
    
    # Halfway line
    ax.plot([0, 0], [-pitch_width/2, pitch_width/2], color=line_color)
    
    # Center Circle
    ax.add_patch(Circle((0, 0), 9.15, linestyle='-', color=line_color, fill=False))
    ax.add_patch(Circle((0, 0), 0.2, color=line_color, fill=True)) # Center spot
    
    # Penalty Areas
    penalty_length = 16.5
    penalty_width = 40.3
    
    # Left Penalty Area
    ax.add_patch(Rectangle((-pitch_length/2, -penalty_width/2), penalty_length, penalty_width, 
                           color=line_color, fill=False))
    # Right Penalty Area
    ax.add_patch(Rectangle((pitch_length/2 - penalty_length, -penalty_width/2), penalty_length, penalty_width, 
                           color=line_color, fill=False))

    # Goal Areas
    goal_area_length = 5.5
    goal_area_width = 18.32
    
    # Left Goal Area
    ax.add_patch(Rectangle((-pitch_length/2, -goal_area_width/2), goal_area_length, goal_area_width, 
                           color=line_color, fill=False))
    # Right Goal Area
    ax.add_patch(Rectangle((pitch_length/2 - goal_area_length, -goal_area_width/2), goal_area_length, goal_area_width, 
                           color=line_color, fill=False))
    
    # Goals (Roughly)
    ax.plot([-pitch_length/2, -pitch_length/2], [-7.32/2, 7.32/2], color=line_color, linewidth=3)
    ax.plot([pitch_length/2, pitch_length/2], [-7.32/2, 7.32/2], color=line_color, linewidth=3)

    ax.set_aspect('equal')
    ax.set_xlim(-pitch_length/2 - 5, pitch_length/2 + 5)
    ax.set_ylim(-pitch_width/2 - 5, pitch_width/2 + 5)
    ax.axis('off')

def plot_play(ax, df_window, color='blue', label=None, alpha=1.0):
    """
    Plots the trajectory on the pitch. (Legacy)
    """
    if df_window.empty: return
    
    # Ensure columns exist (handle raw x/y or smoothed)
    x_col = 'x_smooth' if 'x_smooth' in df_window.columns else 'x'
    y_col = 'y_smooth' if 'y_smooth' in df_window.columns else 'y'
    
    ax.plot(df_window[x_col], df_window[y_col], '-', color=color, linewidth=2, label=label, alpha=alpha)
    
    # Mark start and end
    ax.plot(df_window[x_col].iloc[0], df_window[y_col].iloc[0], 'o', color='green', markersize=4) # Start
    ax.plot(df_window[x_col].iloc[-1], df_window[y_col].iloc[-1], 'x', color='red', markersize=4)   # End

def plot_signals(ax, df_window):
    """
    Plots the X and Y signals over time.
    """
    if df_window.empty: return

    t = df_window['time']
    x = df_window['x_smooth'] if 'x_smooth' in df_window.columns else df_window['x']
    y = df_window['y_smooth'] if 'y_smooth' in df_window.columns else df_window['y']
    
    ax.plot(t, x, label='X (Length)', color='blue')
    ax.plot(t, y, label='Y (Width)', color='orange')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Position (m)')
    ax.legend()
    ax.grid(True)

def plot_scene(ax, fingerprint, overlay_fingerprint=None, title="Play"):
    """
    Plots a static scene from the fingerprint data with pass trajectory.
    Can optionally overlay a second fingerprint (ghosted) for comparison.
    """
    ax.clear()
    draw_pitch(ax)
    
    # helper to draw one play
    def draw_play(fp, alpha=1.0, is_overlay=False, color_team='blue', color_opp='red'):
        ball_x = fp['start_x'] # V3 uses start/end fields
        ball_y = fp['start_y']
        
        # Vectors? V3 has list of vectors.
        # We should plot the full chain.
        vectors = fp.get('vectors', [])
        
        # Plot Trajectory Chain
        curr_x, curr_y = ball_x, ball_y
        
        # Style for overlay
        line_style = '--' if is_overlay else '-'
        marker_style = 'x' if is_overlay else 'o'
        arrow_alpha = 0.4 if is_overlay else 0.8
        
        for vec in vectors:
            next_x = curr_x + vec[0]
            next_y = curr_y + vec[1]
            
            ax.annotate('', xy=(next_x, next_y), xytext=(curr_x, curr_y),
                        arrowprops=dict(facecolor='black', edgecolor='black', 
                                        width=2 if is_overlay else 3, 
                                        headwidth=6 if is_overlay else 8, 
                                        alpha=arrow_alpha, linestyle=line_style))
            curr_x, curr_y = next_x, next_y

        # Plot Start
        ax.plot(ball_x, ball_y, marker_style, color='black', markersize=8 if not is_overlay else 6, zorder=10, label='Start' if not is_overlay else None)
        
        # Plot Players (Snapshot at start)
        tm = fp.get('teammates', [])
        op = fp.get('opponents', [])
        
        # Convert relative to absolute
        tm_x = [p[0] + ball_x for p in tm]
        tm_y = [p[1] + ball_y for p in tm]
        op_x = [p[0] + ball_x for p in op]
        op_y = [p[1] + ball_y for p in op]
        
        # Colors
        c_tm = color_team if not is_overlay else 'lightblue'
        c_op = color_opp if not is_overlay else 'lightcoral'
        p_alpha = alpha if not is_overlay else 0.5
        
        ax.plot(tm_x, tm_y, 'o', color=c_tm, markersize=6 if not is_overlay else 4, alpha=p_alpha, label='Atk Team' if not is_overlay else None)
        ax.plot(op_x, op_y, 'o', color=c_op, markersize=6 if not is_overlay else 4, alpha=p_alpha, label='Def Team' if not is_overlay else None)

    # Draw Overlay first (so it's behind?) or second (on top)?
    # On top with transparency is usually better for comparison.
    if overlay_fingerprint:
        # Align overlay start to original start for better shape comparison?
        # User complained about "relative shape".
        # Yes, visually we should align them to see if SHAPE matches.
        # Copy and shift overlay
        ov = overlay_fingerprint.copy()
        
        # Shift Logic:
        # ov_start_x -> fp_start_x
        dx = fingerprint['start_x'] - ov['start_x']
        dy = fingerprint['start_y'] - ov['start_y']
        
        ov['start_x'] += dx
        ov['start_y'] += dy
        
        # Note: vectors are relative (dx, dy) so they don't change!
        # Players are relative to start, so we just shift their drawing origin (handled by reusing the logic).
        # We need to ensure draw_play uses the shifted start_x/y.
        draw_play(ov, alpha=0.5, is_overlay=True)

    # Draw Main Play
    draw_play(fingerprint, alpha=1.0, is_overlay=False)
    
    ax.set_title(title)
    if not overlay_fingerprint:
        ax.legend(loc='upper right')
