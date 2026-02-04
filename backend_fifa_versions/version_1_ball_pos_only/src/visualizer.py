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
    Plots the trajectory on the pitch.
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
