
# ============================
# CONSTANTS AND CONFIGURATION
# ============================



class settings:
 
    # Glucose thresholds (mmol/L)
    LOW_GLUCOSE_THRESHOLD = 3.5
    HIGH_GLUCOSE_THRESHOLD = 10.0

    # Audio configuration
    LOW_TONE_FREQ = 200    # Hz for deep tone (low glucose)
    HIGH_TONE_FREQ = 850  # Hz for high tone (high glucose)
    TONE_DURATION = 3    # seconds

    # Alarm time window (22:30 - 07:00)
    ALARM_START_TIME = 22 * 60 + 30  # 22:30 in minutes
    ALARM_END_TIME = 7 * 60          # 07:00 in minutes
    
    # Brightness settings
    BRIGHTNESS_DAY = 1.0        # 100% brightness during day
    BRIGHTNESS_NIGHT = 0.1      # 10% brightness at night
    DIM_START_TIME = 22 * 60 + 30  # Start dimming at 22:30
    DIM_END_TIME = 7 * 60          # End dimming at 07:00

    # Visual settings
    WINDOW_SIZE = "800x480"         # Example window size
    BORDER_RADIUS = 15              # Example border radius for UI elements
    SHADOW_OFFSET = 2          # Example shadow offset
    
    # Timing constants
    UPDATE_INTERVAL = 300  # 5 minutes between glucose updates
    ALARM_INTERVAL = 120   # 2 minutes between alarms
    MUTE_DURATION = 3600   # 1 hour mute duration in seconds


    # UI color scheme
    COLORS = {
        'button': "#505050",
        'button_hover': '#3D3D3D',    
        'button_muted': '#606000',
        
        'text_primary': "white",
        'text_secondary': "#808080",  # Gray for secondary text        
        'background': "#000000",
        'clock': "#F0F0D0",

        'gloucose_low': "#ff4444",   # Red for low glucose'
        'gloucose_normal': "green",   # Green for normal glucose
        'gloucose_high': "#ff8800",  # Orange for high glucose
    }

    # Dexcom configuration settings (placeholder values)
    DEXCOM_CONFIG = {
    'username': "<insert>",
    'password': "<insert>",
    'region': "ous"
    }


  


