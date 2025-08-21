# Space Shooter with Boss

## Overview
**Space Shooter with Boss** is a 2D arcade-style game built with Python and Pygame. Control your spaceship, shoot enemies, collect power-ups, and battle a powerful boss.  

Features:
- Dynamic starry background
- Multiple enemy types (normal, fast, big)
- Player upgrades and power-ups
- Boss battles with health bar and bullet attacks
- Explosions and sound effects
- Score tracking, levels, and HUD
- Pause and restart functionality

---

## Requirements
- Python 3.10+
- Pygame library

Install Pygame using:

```bash
pip install pygame
````

---

## File Structure

Place the following sound files in the same directory as the main Python script for full audio support:

```
shoot.wav          # Player shooting sound
explosion.wav      # Explosion sound
powerup.wav        # Power-up pickup sound
game_over.wav      # Game over sound
boss_spawn.wav     # Boss spawn sound
boss_hit.wav       # Boss hit sound
background_music.mp3  # Background music (looped)
```

The game will run with placeholder sounds if files are missing.

---

## How to Run

Run the game script:

```bash
python space_shooter.py
```

---

## Controls

| Key         | Action                         |
| ----------- | ------------------------------ |
| Left Arrow  | Move spaceship left            |
| Right Arrow | Move spaceship right           |
| Space       | Shoot bullets                  |
| P           | Pause / Unpause game           |
| R           | Restart game (after game over) |
| Q           | Quit game (after game over)    |

---

## Gameplay Mechanics

### Enemies

* **Normal:** Standard speed and health
* **Fast:** Moves faster, smaller in size
* **Big:** Slower but bigger, harder to destroy

### Bullets

* Player fires bullets with normal or powered-up stats based on upgrades
* Higher player levels shoot multiple bullets at once

### Boss

* Spawns periodically
* Fires bullets in a spread pattern
* Has a health bar at the top

### Power-ups

* **Health:** Restores player health
* **Rapid:** Reduces bullet cooldown (fires faster)
* **Power:** Increases bullet damage
* **Upgrade:** Increases ship level, bullet power, and max health

### Score and Leveling

* Score increases when destroying enemies and boss
* Player levels up every 50 points, enhancing ship capabilities

### Explosions

* Visual effects appear when enemies or the boss are destroyed

---

## Notes

* Runs at **60 FPS**
* Pausing the game also pauses background music
* Game Over screen shows when player health reaches zero, with score and restart options

---

## License

You can freely modify and distribute this game. Respect original licensing for external sounds or assets.

```

If you want, I can also **add a “Screenshots” and “Gameplay GIF” section** for GitHub so it looks more professional.  

Do you want me to add that?
```
