# GlucoClock - Digital Ur med Blodsukker Overvågning

Et Python-baseret digitalt ur med real-time blodsukker overvågning fra Dexcom CGM enheder og alarm-funktionalitet.

## Features

- **Digital ur**: Viser tid i 24-timers format
- **Blodsukker visning**: Henter og viser blodsukker værdier fra Dexcom Share
- **Trend pile**: Viser retning og hastighed af blodsukker ændringer
- **Farve-kodning**: 
  - Rød: < 4.0 mmol/L
  - Grøn: 4.0-7.0 mmol/L  
  - Gul: 7.0-10.0 mmol/L
  - Orange: ≥ 10.0 mmol/L
- **Alarm-system** (22:30-07:00):
  - Dyb tone (300Hz) hver 2. minut ved lavt blodsukker (≤ 3.5 mmol/L)
  - Høj tone (1000Hz) hver 2. minut ved højt blodsukker (≥ 10.0 mmol/L)
- **Mute funktion**: Knap til at slå alarmer fra i 1 time med nedtælling

## Installation

### Windows
```bash
c:/Python/Python39/python.exe -m pip install -r requirements.txt
```

### Raspberry Pi / Linux
```bash
python3 -m pip install -r requirements.txt
```

## Kørsel

### Windows
```bash
c:/Python/Python39/python.exe GlucoClock.py
```

### Raspberry Pi / Linux
```bash
python3 GlucoClock.py
```

## Konfiguration

Dexcom credentials er pt. hardkodet i linje 137-138 i GlucoClock.py. 
Disse bør flyttes til en separat konfigurationsfil eller miljøvariabler.

## Dependencies

- Python 3.9+
- tkinter (indbygget i Python)
- pydexcom - Dexcom Share API integration
- pygame - Cross-platform lyd afspilning
- numpy - Tone generering

## Platform Support

- Windows
- Raspberry Pi
- Linux med GUI support