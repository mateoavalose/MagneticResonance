import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import time

# Simulation parameters
M0 = 1.0        # Initial magnetization (equilibrium state)
T1 = 1.0        # Longitudinal relaxation time (T1)
T2 = 0.2        # Transverse relaxation time (T2)
max_time = 3.0  # Total simulation time (in seconds)
time_steps = 500  # Number of time steps for the simulation
t = np.linspace(0, max_time, time_steps)  # Array representing time points
n_particles = 10  # Number of particles representing spins

# Magnetization relaxation for longitudinal (Mz) and transverse (Mxy) components
Mz = M0 * (1 - np.exp(-t / T1))  # Longitudinal magnetization over time
Mxy = M0 * np.exp(-t / T2)       # Transverse magnetization over time

# Initialize spin orientations: half pointing up (alpha), half down (beta)
spins = np.zeros((n_particles, 2))
spins[:round(n_particles/2), 1] = 1  # Alpha particles (pointing in +y direction)
spins[round(n_particles/2):, 1] = -1  # Beta particles (pointing in -y direction)

# Generate random final spin directions for post-relaxation state in 2D
final_directions = np.random.randn(n_particles, 2)
final_directions = final_directions / np.linalg.norm(final_directions, axis=1)[:, np.newaxis]  # Normalize directions

# Create figure and subplots for magnetization curves and spin vectors
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Plot for magnetization relaxation (Mz and Mxy curves)
line_Mz, = ax1.plot([], [], label=r'Longitudinal Magnetization $M_z(t)$', color='b')
line_Mxy, = ax1.plot([], [], label=r'Transverse Magnetization $M_{xy}(t)$', color='r')
ax1.set_xlim(0, max_time)
ax1.set_ylim(0, 1.1)
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Magnetization')
ax1.legend()
ax1.grid(True)

# Plot for spin vectors (alpha and beta particles)
ax2.set_xlim([-1, 1])
ax2.set_ylim([-1, 1])
ax2.set_xlabel('X')
ax2.set_ylabel('Y')

# Initialize quivers to visualize spin directions
quivers = [ax2.quiver(0, 0, *spins[i], scale=5, color=('b' if i < round(n_particles/2) else 'y'), 
                      label=('Alpha' if i == 0 else 'Beta' if i == round(n_particles/2) else '_nolegend_')) 
           for i in range(n_particles)]

# Add legend for spin types (alpha and beta)
ax2.legend(loc='upper right')

# Control flags for animation state
animation_running = False  # Whether the animation is currently running
current_frame = 0  # Track the current frame
start_time = None  # Time when animation started
paused_time = None  # Time when animation was paused

# Initialize plot data for the animation
def init():
    line_Mz.set_data([], [])
    line_Mxy.set_data([], [])
    return line_Mz, line_Mxy, quivers

# Update function for each animation frame
def update(frame):
    global current_frame
    current_frame = frame

    time_point = t[current_frame]

    # Update magnetization curves
    line_Mz.set_data(t[:current_frame], Mz[:current_frame])
    line_Mxy.set_data(t[:current_frame], Mxy[:current_frame])
    
    # Interpolate spin direction based on current Mz
    for i in range(n_particles):
        interp_factor = Mz[current_frame]  # Interpolation factor based on longitudinal magnetization
        direction = (1 - interp_factor) * spins[i] + interp_factor * final_directions[i]
        direction = direction / np.linalg.norm(direction)  # Re-normalize to ensure unit vector
        quivers[i].remove()  # Remove old quiver to update
        quivers[i] = ax2.quiver(0, 0, *direction, scale=5, color=('b' if i < round(n_particles/2) else 'y'))
    
    return line_Mz, line_Mxy, *quivers

# Function to manually advance animation frame
def advance_frame(val):
    global current_frame, animation_running, start_time

    if animation_running:
        elapsed_time = time.time() - start_time
        current_frame = int((elapsed_time / max_time) * time_steps) % time_steps
        update(current_frame)
        fig.canvas.draw_idle()

    # Reset animation if it reaches the end
    if current_frame >= time_steps - 1:
        reset_animation()

# Reset animation state
def reset_animation():
    global current_frame, start_time, paused_time, animation_running
    current_frame = 0
    start_time = time.time()  # Reset start time
    paused_time = None
    animation_running = False  # Stop animation
    ani.event_source.stop()  # Ensure the animation stops
    update(current_frame)

# Start animation
def start_animation(event):
    global animation_running, start_time, paused_time

    if not animation_running:
        animation_running = True
        if paused_time is not None:
            start_time += time.time() - paused_time  # Adjust start time for paused state
        else:
            start_time = time.time()  # Initialize start time
        ani.event_source.start()  # Resume animation

# Pause animation
def stop_animation(event):
    global animation_running, paused_time
    if animation_running:
        animation_running = False
        paused_time = time.time()  # Store pause time
        ani.event_source.stop()  # Stop the animation

# Create buttons for controlling the animation
start_ax = plt.axes([0.72, 0.02, 0.08, 0.04])  # Smaller button for 'Start'
stop_ax = plt.axes([0.81, 0.02, 0.08, 0.04])   # Smaller button for 'Pause'
start_button = Button(start_ax, 'Start')
stop_button = Button(stop_ax, 'Pause')
start_button.on_clicked(start_animation)
stop_button.on_clicked(stop_animation)

# Create animation using FuncAnimation
ani = FuncAnimation(fig, advance_frame, frames=time_steps, init_func=init, blit=False, interval=30, repeat=False)

# Stop animation at the beginning
animation_running = False

# Display the animation
plt.show()
