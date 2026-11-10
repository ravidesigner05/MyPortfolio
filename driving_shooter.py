import random
import time
import tkinter as tk


WIDTH = 900
HEIGHT = 650
ROAD_LEFT = 150
ROAD_RIGHT = 750
LANE_COUNT = 3
PLAYER_Y = 535


class DrivingShooter:
    def __init__(self, root):
        self.root = root
        self.root.title("Road Blaster — Driving Shooter")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            background="#17251e",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.keys = set()
        self.mode = "menu"
        self.last_frame = time.perf_counter()
        self.reset_game()
        self.draw()
        self.root.after(16, self.tick)

    def reset_game(self):
        self.keys.clear()
        self.player_x = (ROAD_LEFT + ROAD_RIGHT) / 2
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.lives = 3
        self.road_offset = 0
        self.spawn_timer = 0.5
        self.shot_timer = 0
        self.damage_timer = 0

    def start_game(self):
        self.reset_game()
        self.mode = "playing"
        self.last_frame = time.perf_counter()

    def close(self):
        self.root.destroy()

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in self.keys:
            return
        self.keys.add(key)

        if self.mode == "menu" and key in ("return", "space"):
            self.start_game()
        elif self.mode == "game_over" and key in ("return", "r"):
            self.start_game()
        elif key == "escape":
            self.close()
        elif key == "p" and self.mode in ("playing", "paused"):
            self.mode = "paused" if self.mode == "playing" else "playing"
            self.last_frame = time.perf_counter()

    def on_key_release(self, event):
        self.keys.discard(event.keysym.lower())

    def spawn_enemy(self):
        lane_width = (ROAD_RIGHT - ROAD_LEFT) / LANE_COUNT
        lane = random.randrange(LANE_COUNT)
        self.enemies.append(
            {
                "x": ROAD_LEFT + lane_width * (lane + 0.5),
                "y": -70,
                "speed": random.uniform(190, 245) + min(self.score * 0.12, 150),
                "color": random.choice(("#e26455", "#e7ae4b", "#9d83c7", "#55a8a0")),
                "hit": False,
            }
        )

    def update(self, dt):
        speed = 330
        lane_width = (ROAD_RIGHT - ROAD_LEFT) / LANE_COUNT
        minimum_x = ROAD_LEFT + lane_width * 0.5
        maximum_x = ROAD_RIGHT - lane_width * 0.5
        direction = int("right" in self.keys or "d" in self.keys) - int(
            "left" in self.keys or "a" in self.keys
        )
        self.player_x = max(
            minimum_x,
            min(maximum_x, self.player_x + direction * speed * dt),
        )

        self.road_offset = (self.road_offset + 360 * dt) % 80
        self.shot_timer -= dt
        self.damage_timer = max(0, self.damage_timer - dt)
        if ("space" in self.keys or "w" in self.keys or "up" in self.keys) and self.shot_timer <= 0:
            self.bullets.append({"x": self.player_x, "y": PLAYER_Y - 36})
            self.shot_timer = 0.24

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = max(0.48, 1.05 - self.score / 1800) * random.uniform(0.78, 1.18)

        for bullet in self.bullets:
            bullet["y"] -= 610 * dt
        self.bullets = [bullet for bullet in self.bullets if bullet["y"] > -20]

        for enemy in self.enemies:
            enemy["y"] += enemy["speed"] * dt
            if (
                not enemy["hit"]
                and abs(enemy["x"] - self.player_x) < 48
                and abs(enemy["y"] - PLAYER_Y) < 58
                and self.damage_timer <= 0
            ):
                enemy["hit"] = True
                self.lives -= 1
                self.damage_timer = 1.15
                if self.lives <= 0:
                    self.mode = "game_over"

            for bullet in self.bullets:
                if (
                    not enemy["hit"]
                    and abs(bullet["x"] - enemy["x"]) < 42
                    and abs(bullet["y"] - enemy["y"]) < 52
                ):
                    enemy["hit"] = True
                    bullet["y"] = -100
                    self.score += 100
                    break

        self.bullets = [bullet for bullet in self.bullets if bullet["y"] > -20]
        self.enemies = [
            enemy for enemy in self.enemies
            if not enemy["hit"] and enemy["y"] < HEIGHT + 80
        ]

    def draw_car(self, x, y, color, player=False):
        canvas = self.canvas
        canvas.create_oval(x - 31, y - 28, x + 31, y + 34, fill="#101612", outline="")
        canvas.create_polygon(
            x - 25, y + 27, x - 30, y + 10, x - 27, y - 20,
            x - 16, y - 31, x + 16, y - 31, x + 27, y - 20,
            x + 30, y + 10, x + 25, y + 27,
            fill=color, outline="#fff3d4", width=2,
        )
        canvas.create_polygon(
            x - 18, y - 9, x - 13, y - 23, x + 13, y - 23,
            x + 18, y - 9, fill="#a8d7ce", outline="#e9f4e4", width=2,
        )
        canvas.create_line(x - 19, y + 3, x + 19, y + 3, fill="#462e2d", width=3)
        canvas.create_rectangle(x - 21, y + 18, x - 14, y + 23, fill="#fff1a8", outline="")
        canvas.create_rectangle(x + 14, y + 18, x + 21, y + 23, fill="#fff1a8", outline="")
        canvas.create_rectangle(x - 29, y - 17, x - 23, y - 5, fill="#171c18", outline="")
        canvas.create_rectangle(x + 23, y - 17, x + 29, y - 5, fill="#171c18", outline="")
        if player:
            canvas.create_rectangle(x - 5, y - 32, x + 5, y - 45, fill="#f3d16b", outline="")
            canvas.create_oval(x - 7, y - 51, x + 7, y - 38, fill="#ffe59a", outline="")

    def draw_background(self):
        canvas = self.canvas
        canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#244330", outline="")
        canvas.create_rectangle(ROAD_LEFT - 12, 0, ROAD_RIGHT + 12, HEIGHT, fill="#c6b995", outline="")
        canvas.create_rectangle(ROAD_LEFT, 0, ROAD_RIGHT, HEIGHT, fill="#343a3b", outline="")

        for y in range(-80, HEIGHT + 80, 80):
            marker_y = y + self.road_offset
            canvas.create_rectangle(ROAD_LEFT + 5, marker_y, ROAD_LEFT + 11, marker_y + 38, fill="#f2e3b2", outline="")
            canvas.create_rectangle(ROAD_RIGHT - 11, marker_y, ROAD_RIGHT - 5, marker_y + 38, fill="#f2e3b2", outline="")
            for divider in range(1, LANE_COUNT):
                x = ROAD_LEFT + (ROAD_RIGHT - ROAD_LEFT) * divider / LANE_COUNT
                canvas.create_rectangle(x - 3, marker_y, x + 3, marker_y + 38, fill="#d9d3bb", outline="")

        for side in (42, 838):
            for y in range(-30, HEIGHT + 50, 125):
                tree_y = (y + self.road_offset * 0.7) % (HEIGHT + 80) - 40
                canvas.create_oval(side - 18, tree_y - 10, side + 18, tree_y + 25, fill="#356443", outline="")
                canvas.create_oval(side - 12, tree_y - 17, side + 12, tree_y + 12, fill="#477c4f", outline="")

    def draw_hud(self):
        canvas = self.canvas
        canvas.create_rectangle(0, 0, WIDTH, 58, fill="#17251e", outline="")
        canvas.create_text(24, 28, anchor="w", text="ROAD BLASTER", fill="#f3d16b", font=("Segoe UI", 16, "bold"))
        canvas.create_text(450, 28, text=f"SCORE  {self.score:05d}", fill="#f6f1dc", font=("Segoe UI", 16, "bold"))
        canvas.create_text(872, 28, anchor="e", text=f"LIVES  {'♥ ' * self.lives}", fill="#f08e78", font=("Segoe UI", 16, "bold"))

    def draw_overlay(self, title, subtitle, hint):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#101913", stipple="gray50", outline="")
        self.canvas.create_text(WIDTH / 2, 245, text=title, fill="#f3d16b", font=("Segoe UI", 38, "bold"))
        self.canvas.create_text(WIDTH / 2, 305, text=subtitle, fill="#f6f1dc", font=("Segoe UI", 16))
        self.canvas.create_text(WIDTH / 2, 370, text=hint, fill="#c6d1c5", font=("Segoe UI", 13))

    def draw(self):
        self.canvas.delete("all")
        self.draw_background()

        for bullet in self.bullets:
            self.canvas.create_oval(
                bullet["x"] - 5, bullet["y"] - 13,
                bullet["x"] + 5, bullet["y"] + 13,
                fill="#ffe37c", outline="#fff7cf", width=2,
            )

        for enemy in self.enemies:
            self.draw_car(enemy["x"], enemy["y"], enemy["color"])

        if self.damage_timer <= 0 or int(self.damage_timer * 12) % 2 == 0:
            self.draw_car(self.player_x, PLAYER_Y, "#4eb4a3", player=True)

        self.draw_hud()

        if self.mode == "menu":
            self.draw_overlay("ROAD BLASTER", "Drive fast. Aim true. Clear the road!", "ENTER / SPACE  to start")
            self.canvas.create_text(WIDTH / 2, 415, text="← → or A / D  drive     SPACE  shoot     P  pause     ESC  quit", fill="#c6d1c5", font=("Segoe UI", 12))
        elif self.mode == "paused":
            self.draw_overlay("PAUSED", "Take a breather.", "Press P to continue")
        elif self.mode == "game_over":
            self.draw_overlay("GAME OVER", f"Final score: {self.score}", "Press R or ENTER to race again")

    def tick(self):
        now = time.perf_counter()
        dt = min(now - self.last_frame, 0.05)
        self.last_frame = now

        if self.mode == "playing":
            self.update(dt)

        self.draw()
        self.root.after(16, self.tick)


def main():
    root = tk.Tk()
    DrivingShooter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
