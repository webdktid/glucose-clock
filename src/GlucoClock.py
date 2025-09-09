import tkinter as tk
import threading
import time
import os
import numpy as np
import wave
import pygame
import math

from io import BytesIO
from datetime import datetime, timedelta
from pydexcom import Dexcom
from settings import settings

# Initialize tkinter root and canvas globally
root = tk.Tk()
root.geometry(settings.WINDOW_SIZE)
root.configure(bg=settings.COLORS['background'])

# Canvas for glucose symbol - global scope
canvas_size = 300
canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg=settings.COLORS['background'], highlightthickness=0)
canvas.place(x=250, y=70)
bloodSugar = 0 
trend = 0  

def get_glucose_color(value):
    if value < settings.LOW_GLUCOSE_THRESHOLD:
        return settings.COLORS['gloucose_low'] 
    elif value < settings.HIGH_GLUCOSE_THRESHOLD:
        return settings.COLORS['gloucose_normal']  
    else:
        return settings.COLORS['gloucose_high']  

def draw_glucose_symbol(glucose_value=None, trend_value=None):
   
    global bloodSugar, trend
    
    # Use global values if not specified
    if glucose_value is None:
        glucose_value = bloodSugar
    if trend_value is None:
        trend_value = trend
    
    canvas.delete("all")
    
    center_x = canvas_size // 2  # 100
    center_y = canvas_size // 2  # 100
    radius = 65  # Reduced slightly to give more space for the triangle
    
    # Get color based on blood sugar value
    fill_color = get_glucose_color(glucose_value)
    
    # Draw gray border (lighter gray)
    canvas.create_oval(
        center_x - radius - 10, center_y - radius - 10,
        center_x + radius + 10, center_y + radius + 10,
        fill="#d0d0d0", outline=""
    )
    
    # Draw colored circle
    canvas.create_oval(
        center_x - radius, center_y - radius,
        center_x + radius, center_y + radius,
        fill=fill_color, outline=""
    )
    
    # Draw blood sugar value
    canvas.create_text(
        center_x, center_y - 5,
        text=f"{glucose_value:.1f}",
        font=("Arial", 36, "bold"),
        fill="black"
    )
    
    # Draw mmol/L text
    canvas.create_text(
        center_x, center_y + 30,
        text="mmol/L",
        font=("Arial", 14),
        fill="black"
    )
    
    # Draw trend triangle - AFTER everything else so it's on top
    # Map trend value to angle
    trend_angles = {
        1: -90,   # ↑↑ Rising rapidly - straight up
        2: -60,   # ↑  Rising - angled up
        3: -30,   # ↗  Rising slowly - slightly angled up
        4: 0,     # →  Stable - straight to the right
        5: 30,    # ↘  Falling slowly - slightly angled down
        6: 60,    # ↓  Falling - angled down
        7: 90     # ↓↓ Falling rapidly - straight down
    }
    
    angle = trend_angles.get(trend_value, 0)
    
    # Convert to radians
    angle_rad = math.radians(angle)
    
    # Place the triangle completely outside the gray border
    triangle_distance = radius + 5  # Closer but still outside gray border
    
    # Calculate triangle's center position
    tri_center_x = center_x + triangle_distance * math.cos(angle_rad)
    tri_center_y = center_y + triangle_distance * math.sin(angle_rad)
    
    # Larger triangle for better visibility
    # Calculate tip point (furthest from the circle)
    tip_distance = 30
    tip_x = tri_center_x + tip_distance * math.cos(angle_rad)
    tip_y = tri_center_y + tip_distance * math.sin(angle_rad)
    
    # Calculate base points (closer to the circle)
    base_width = 20
    base_angle = angle_rad + math.pi / 2  # 90 degrees perpendicular to the direction
    
    base1_x = tri_center_x + base_width * math.cos(base_angle)
    base1_y = tri_center_y + base_width * math.sin(base_angle)
    
    base2_x = tri_center_x - base_width * math.cos(base_angle)
    base2_y = tri_center_y - base_width * math.sin(base_angle)
    
    # Draw triangle with black color and thick white border for maximum visibility
    canvas.create_polygon(
        tip_x, tip_y,
        base1_x, base1_y,
        base2_x, base2_y,
        fill=fill_color, outline="#d0d0d0", width=5
    )


class DigitalClock:


    def __init__(self, root):
        """Initialize the digital clock application."""
        self.root = root
        self._setup_window()

        self._setup_fonts()
        # self._update_theme()
        self._initialize_variables()
        self._setup_audio()
        self._setup_brightness()

        # Use global canvas instead of creating new one
        global canvas, canvas_size
        self.canvas = canvas
        self.canvas_size = canvas_size

        self._create_ui()
        
        # Draw initial glucose symbol with default values
        draw_glucose_symbol(5.5, 4)
        
        self._start_updates()

    def _setup_fonts(self):
        import tkinter.font as tkFont
        available_fonts = tkFont.families()
        
        def get_font_family(preferred_fonts):
            for font in preferred_fonts:
                if font in available_fonts:
                    return font
            return preferred_fonts[-1]  # Return last as fallback
        
        # # Set up font families
        # glucose_family = get_font_family(['SF Pro Display', 'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'])
        clock_family = get_font_family(['SF Mono', 'Monaco', 'Consolas', 'Courier New', 'monospace'])
        ui_family = get_font_family(['SF Pro Text', 'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'])
        
        # # Create font tuples - adjusted for 800x480 display
        # self.glucose_font = (glucose_family, 90, 'normal')  # Smaller for compact display
        self.clock_font = (clock_family, 64, 'normal')     # Proportionally smaller
        # self.trend_font = (glucose_family, 36, 'normal')   # Reduced
        # self.info_font = (ui_family, 14, 'normal')         # Smaller
        # self.countdown_font = (ui_family, 12, 'normal')    # Smaller
        self.button_font = (ui_family, 16, 'bold')       # Smaller buttons

    def _create_ui(self):
        self._create_control_buttons()
        self._create_glucose_info_label()
        self._create_clock_display()
        
        # Initialize Dexcom connection
        self._init_dexcom()
        self._update_glucose_async()

    def _create_glucose_info_label(self):
        """Create label for glucose info, countdown and connection status."""
        self.glucose_info_label = tk.Label(
            self.root,
            text="Waiting for data...",
            font=('Arial', 14, 'normal'),
            bg=settings.COLORS['background'],
            fg=settings.COLORS['text_secondary']
        )
        self.glucose_info_label.place(x=350, y=320)
        
        # Countdown label
        self.countdown_label = tk.Label(
            self.root,
            text="",
            font=('Arial', 12, 'normal'),
            bg=settings.COLORS['background'],
            fg=settings.COLORS['text_secondary']
        )
        self.countdown_label.place(x=50, y=200)

    def _test_low_sound(self):
        if self.low_sound:
            self.low_sound.play()
    
    def _test_high_sound(self):
        if self.high_sound:
                self.high_sound.play()
    
    def _toggle_mute(self):
        if self.muted_until and datetime.now() < self.muted_until:
            self.muted_until = None
            self.mute_button.config(text="🔇 Mute", bg=settings.COLORS['button'])
        else:
            self.muted_until = datetime.now() + timedelta(seconds=settings.MUTE_DURATION)
            self.mute_button.config(bg=settings.COLORS['button_muted'])

    def _init_dexcom(self):
        """Initialize Dexcom connection."""
        try:
            self.dexcom = Dexcom(
                username=settings.DEXCOM_CONFIG['username'],
                password=settings.DEXCOM_CONFIG['password'],
                region=settings.DEXCOM_CONFIG['region']
            )
            print("Dexcom connection established")
        except Exception as e:
            print(f"Error during Dexcom initialization: {e}")
            self.glucose_info_label.config(text=f"Dexcom error {e}")

    def _generate_tone(self, frequency, duration):

        sample_rate = 22050
        samples = int(sample_rate * duration)
        waves = np.sin(2 * np.pi * frequency * np.arange(samples) / sample_rate)
        
        # Convert to 16-bit
        waves = (waves * 32767).astype(np.int16)
        
        # Create stereo signal
        stereo_waves = np.array([waves, waves]).T
        
        # Create WAV file in memory
        wav_file = BytesIO()
        with wave.open(wav_file, 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(stereo_waves.tobytes())
        
        wav_file.seek(0)
        return pygame.mixer.Sound(wav_file)

    def _create_clock_display(self):
        """Create the elegant digital clock display."""
        self.clock_frame = tk.Frame(self.root, bg=settings.COLORS['background'])
        self.clock_frame.pack(side=tk.BOTTOM, pady=30)
        
        # Single monospace time display for perfect alignment
        self.time_label = tk.Label(
            self.clock_frame,
            text='00:00:00',
            font=self.clock_font,
            bg=settings.COLORS['background'],
            fg=settings.COLORS['clock'],
            justify=tk.CENTER
        )
        self.time_label.pack()
        
        # Keep individual labels for easier updates (hidden)
        self.hour_label = tk.Label(self.clock_frame, text='00', font=self.clock_font)
        self.minute_label = tk.Label(self.clock_frame, text='00', font=self.clock_font)
        self.second_label = tk.Label(self.clock_frame, text='00', font=self.clock_font)
        self.colon1 = tk.Label(self.clock_frame, text=':')
        self.colon2 = tk.Label(self.clock_frame, text=':')

    def _setup_window(self):
        """Configure the main window."""
        self.root.title("GlucoClock")
        # Geometry and background already set globally
        self.root.resizable(False, False)
        
        # Enable fullscreen mode
        self.root.attributes('-fullscreen', True)
        
        # Remove window decorations
        self.root.overrideredirect(False)  # Keep False for fullscreen
        
        # Escape key to exit fullscreen (for debugging)
        self.root.bind('<Escape>', self._toggle_fullscreen)
        self.root.bind('<F11>', self._toggle_fullscreen)
        
        # Focus window
        self.root.focus_set()

    def _setup_brightness(self):
        """Setup brightness control for Raspberry Pi."""
        self.current_brightness = 1.0
        self.brightness_path = "/sys/class/backlight/rpi_backlight/brightness"
        self.max_brightness_path = "/sys/class/backlight/rpi_backlight/max_brightness"
        
        # Try to read max brightness
        try:
            with open(self.max_brightness_path, 'r') as f:
                self.max_brightness = int(f.read().strip())
                print(f"Max brightness: {self.max_brightness}")
        except:
            # Default for official 7" touchscreen
            self.max_brightness = 255
            print(f"Using default max brightness: {self.max_brightness}")
        
        self._update_brightness()

    def _is_night_time(self):
        """Check if current time is within night period for dimming."""
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        
        # Check if we're in the night period (after 22:30 or before 07:00)
        return current_time >= settings.DIM_START_TIME or current_time < settings.DIM_END_TIME

    def _set_backlight_brightness(self, brightness_percent):
        """Set the backlight brightness on Raspberry Pi."""
        try:
            # Calculate actual brightness value
            brightness_value = int(self.max_brightness * brightness_percent)
            brightness_value = max(1, brightness_value)  # Ensure minimum brightness of 1
            
            # Write to backlight control
            with open(self.brightness_path, 'w') as f:
                f.write(str(brightness_value))
            return True
        except PermissionError:
            print("Permission denied: Run with sudo or add user to video group")
            print("Run: sudo usermod -a -G video $USER")
            return False
        except FileNotFoundError:
            print(f"Backlight control not found at {self.brightness_path}")
            return False
        except Exception as e:
            print(f"Error setting brightness: {e}")
            return False

    def _update_brightness(self):
        """Update screen brightness based on time of day."""
        target_brightness = settings.BRIGHTNESS_NIGHT if self._is_night_time() else settings.BRIGHTNESS_DAY
        
        if self.current_brightness != target_brightness:
            self.current_brightness = target_brightness
            
            # Set backlight brightness on Pi
            if self._set_backlight_brightness(self.current_brightness):
                print(f"Brightness adjusted to {int(self.current_brightness * 100)}%")
        
        # Check brightness every minute
        self.root.after(60000, self._update_brightness)

    def _setup_audio(self):

        # Initialize pygame mixer with different settings for Raspberry Pi
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
            
        # Check if audio system is working
        print(f"Audio driver: {pygame.mixer.get_init()}")
        print(f"Mixer initialized: {pygame.mixer.get_init() is not None}")
            
        # Test audio device
        import os
        print(f"ALSA PCM: {os.environ.get('ALSA_PCM_CARD', 'Not set')}")
        print(f"ALSA CTL: {os.environ.get('ALSA_CTL_CARD', 'Not set')}")
            
        self.low_sound = self._generate_tone(settings.LOW_TONE_FREQ, settings.TONE_DURATION)
        self.high_sound = self._generate_tone(settings.HIGH_TONE_FREQ, settings.TONE_DURATION)
            
        if self.low_sound and self.high_sound:
           print("Audio tones generated successfully")
        else:
           print("Warning: Audio tones could not be generated")

    def _update_countdown(self):
        """Update countdown display showing seconds until next glucose update."""
        self.reading_seconds_old += 1
        if self.countdown_seconds > 0:
            self.countdown_label.config(text=f"last measure:{self.reading_seconds_old}\rNext update:{self.countdown_seconds}")
            self.countdown_seconds -= 1
        elif self.countdown_seconds == 0:
            self.countdown_label.config(text="Updating...")
            
        # Update every second
        self.root.after(1000, self._update_countdown)

    def _create_control_buttons(self):
        """Create the top control bar with elegant, minimalist buttons."""
        self.top_frame = tk.Frame(self.root, bg=settings.COLORS['background'], height=50)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        self.top_frame.pack_propagate(False)
        
        # Left side - Test buttons with icons
        left_frame = tk.Frame(self.top_frame, bg=settings.COLORS['background'])
        left_frame.pack(side=tk.LEFT)
        
        self.test_low_button = self._create_modern_button(
            left_frame, "▼ Test", self._test_low_sound, 
            settings.COLORS['button'], 8
        )
        self.test_low_button.pack(side=tk.LEFT, padx=(0, 10))

        self.test_high_button = self._create_modern_button(
            left_frame, "▲ Test", self._test_high_sound, 
            settings.COLORS['button'], 8
        )
        self.test_high_button.pack(side=tk.LEFT, padx=(0, 10))

        self.update_now_button = self._create_modern_button(
            left_frame, "Update now", self._update_glucose, 
            settings.COLORS['button'], 8
        )
        self.update_now_button.pack(side=tk.LEFT)


        # Right side - Mute and Exit buttons
        right_frame = tk.Frame(self.top_frame, bg=settings.COLORS['background'])
        right_frame.pack(side=tk.RIGHT)
        
        self.mute_button = self._create_modern_button(
            right_frame, "🔇 Mute", self._toggle_mute, 
             settings.COLORS['button'], 10
        )
        self.mute_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Exit button
        self.exit_button = self._create_modern_button(
            right_frame, "✕ Exit", self._exit_app, 
             settings.COLORS['button'], 10
        )
        self.exit_button.pack(side=tk.LEFT)
 
    def _exit_app(self):
        """Exit the application."""
        try:
            # Stop any playing sounds
            if hasattr(self, 'low_sound') and self.low_sound:
                self.low_sound.stop()
            if hasattr(self, 'high_sound') and self.high_sound:
                self.high_sound.stop()
            # Quit pygame mixer
            pygame.mixer.quit()
        except:
            pass
        finally:
            self.root.quit()
            self.root.destroy()
 
    def _toggle_fullscreen(self, event=None):
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)

    def _initialize_variables(self):

        # Dexcom variables
        self.dexcom = None
        self.last_glucose = None
        self.last_trend = None
        self.last_update_time = None
        self.countdown_seconds = settings.UPDATE_INTERVAL
        self.reading_seconds_old = 0

        # Alarm variables
        self.muted_until = None
        self.last_alarm_time = None
        self.alarm_active = False

    def _create_modern_button(self, parent, text, command, bg_color, padx=10):
        """Create modern, flat buttons with subtle styling."""
        button = tk.Button(
            parent,
            text=text,
            font=self.button_font,
            bg=bg_color,
            fg=settings.COLORS['text_primary'],
            activebackground=settings.COLORS['button_hover'],
            activeforeground=settings.COLORS['text_primary'],
            command=command,
            relief=tk.FLAT,
            bd=1,
            padx=padx,
            pady=8,
            cursor='hand2'
        )
        # Add subtle hover effect
        def on_enter(e):
            button.configure(bg=settings.COLORS['button_hover'])
        def on_leave(e):
            if text == "🔇 Mute" and self.muted_until and datetime.now() < self.muted_until:
                button.configure(bg=settings.COLORS['button_muted'])
            else:
                button.configure(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button

    def _update_glucose(self):
        """Fetch and update glucose data."""
        
        if not self.dexcom:
            return
            
        try:
            # Get latest glucose reading
            bg = self.dexcom.get_current_glucose_reading()
            
            if bg:
                # Store values
                global bloodSugar, trend
                self.last_glucose = bg.mmol_l
                self.last_trend = bg.trend
                self.last_update_time = datetime.now(bg.datetime.tzinfo)
                bloodSugar = bg.mmol_l
                trend = bg.trend
                
                # Update display
                draw_glucose_symbol(bg.mmol_l, bg.trend)
                
                # Subtract using tz-aware datetime
                when = (datetime.now(bg.datetime.tzinfo) - bg.datetime).total_seconds() 

                self.glucose_info_label.config(text="")
                self.reading_seconds_old = round(when)

                # Reset countdown
                self.countdown_seconds = settings.UPDATE_INTERVAL
                
                    
        except Exception as e:
            print(f"Error fetching blood sugar: {e}")
            self.glucose_info_label.config(text="Connection error")
            # Retry sooner on error
            self.countdown_seconds = 30
    
    def _update_glucose_async(self):
        """Update glucose data asynchronously."""
        def update_thread():
            self._update_glucose()
            # Schedule next update
            self.root.after(settings.UPDATE_INTERVAL * 1000, self._update_glucose_async)
        
        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()

    def _is_alarm_time(self):
        """Check if current time is within alarm period (nighttime)."""
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        
        return current_time >= settings.ALARM_START_TIME or current_time < settings.ALARM_END_TIME

    def _should_play_alarm(self):
        """Determine if alarm should be played."""
        if not self._is_alarm_time():
            return False
            
        if self.muted_until and datetime.now() < self.muted_until:
            return False
            
        if self.last_glucose is None:
            return False
            
        # Check if glucose is out of range
        out_of_range = (self.last_glucose <= settings.LOW_GLUCOSE_THRESHOLD or 
                       self.last_glucose >= settings.HIGH_GLUCOSE_THRESHOLD)
        
        if not out_of_range:
            return False
            
        # Check if enough time has passed since last alarm
        if (self.last_alarm_time is None or 
            (datetime.now() - self.last_alarm_time).total_seconds() >= settings.ALARM_INTERVAL):
            return True
                
        return False

    def _play_alarm(self):
        """Play appropriate alarm sound based on glucose level."""
        if self.last_glucose is None:
            return
            
        if self.last_glucose <= settings.LOW_GLUCOSE_THRESHOLD:
            if self.low_sound:
                self.low_sound.play()
                print(f"Low glucose alarm: {self.last_glucose:.1f} mmol/L")
        elif self.last_glucose >= settings.HIGH_GLUCOSE_THRESHOLD:
            if self.high_sound:
                self.high_sound.play()
                print(f"High glucose alarm: {self.last_glucose:.1f} mmol/L")
                
        self.last_alarm_time = datetime.now()

    def _check_alarms(self):
        """Check and play alarms if necessary."""
        if self._should_play_alarm():
            # Run in separate thread to avoid blocking UI
            thread = threading.Thread(target=self._play_alarm, daemon=True)
            thread.start()
            
        # Check again in 10 seconds
        self.root.after(10000, self._check_alarms)

    def _start_updates(self):
        """Start all periodic update functions."""
        self._update_clock()
        self._update_countdown()
        self._update_mute_button()
        self._check_alarms()
        self._update_brightness()

    def _update_clock(self):
        """Update elegant digital clock display."""
        now = datetime.now()
        
        # Update main time display
        time_str = now.strftime('%H:%M:%S')
        self.time_label.config(text=time_str)
        
        # Update individual components (for internal use)
        self.hour_label.config(text=now.strftime('%H'))
        self.minute_label.config(text=now.strftime('%M'))
        self.second_label.config(text=now.strftime('%S'))
        
        # Update every second
        self.root.after(1000, self._update_clock)

    def _update_mute_button(self):
        """Update mute button with remaining time."""
        if self.muted_until and datetime.now() < self.muted_until:
            remaining = self.muted_until - datetime.now()
            minutes = int(remaining.total_seconds() // 60)
            seconds = int(remaining.total_seconds() % 60)
            self.mute_button.config(
                text=f"🔇 {minutes:02d}:{seconds:02d}",
                bg=settings.COLORS['button_muted']
            )
        else:
            if self.muted_until:  # Was muted but expired
                self.muted_until = None
                self.mute_button.config(
                    text="🔇 Mute", 
                    bg=settings.COLORS['button']
                )
                
        # Update every second
        self.root.after(1000, self._update_mute_button)



def main():
    """Main application entry point."""
    global root
    app = DigitalClock(root)
    root.mainloop()

if __name__ == "__main__":
    main()




