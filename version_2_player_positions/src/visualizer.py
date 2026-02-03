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

def plot_scene(ax, fingerprint, title="Play"):
    """
    Plots a static scene from the fingerprint data with pass trajectory.
    """
    ax.clear()
    draw_pitch(ax)
    
    ball_x = fingerprint['ball_x']
    ball_y = fingerprint['ball_y']
    
    # Check if we have pass end coordinates (added in update)
    pass_end_x = fingerprint.get('pass_end_x', ball_x)
    pass_end_y = fingerprint.get('pass_end_y', ball_y)
    
    # Plot Trajectory (Arrow)
    # Using small offset so arrow head is visible/doesn't overlap ball exactly?
    ax.annotate('', xy=(pass_end_x, pass_end_y), xytext=(ball_x, ball_y),
                arrowprops=dict(facecolor='black', edgecolor='black', width=2, headwidth=8, alpha=0.7))
    
    # Plot Ball Start
    ax.plot(ball_x, ball_y, 'o', color='black', markersize=8, zorder=10, label='Start')
    
    # Plot Pass End Marker
    if pass_end_x != ball_x or pass_end_y != ball_y:
         ax.plot(pass_end_x, pass_end_y, 'x', color='black', markersize=8, zorder=9, label='End')
    
    # Plot Teammates (Blue)
    tm_x = [p[0] + ball_x for p in fingerprint['teammates_rel']]
    tm_y = [p[1] + ball_y for p in fingerprint['teammates_rel']]
    ax.plot(tm_x, tm_y, 'o', color='blue', markersize=6, label='Atk Team')
    
    # Plot Opponents (Red)
    opp_x = [p[0] + ball_x for p in fingerprint['opponents_rel']]
    opp_y = [p[1] + ball_y for p in fingerprint['opponents_rel']]
    ax.plot(opp_x, opp_y, 'o', color='red', markersize=6, label='Def Team')
    
    ax.set_title(title)
    ax.legend(loc='upper right')
