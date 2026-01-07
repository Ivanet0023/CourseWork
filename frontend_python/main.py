import tkinter as tk
from tkinter import messagebox, colorchooser
from solitaire_engine import SolitaireEngine
import time

CARD_WIDTH = 80
CARD_HEIGHT = 120
MARGIN = 20
GAP = 20
VERTICAL_OFFSET_FACE_UP = 35
VERTICAL_OFFSET_FACE_DOWN = 10
COLOR_OUTLINE = "black"
COLOR_SELECTED = "yellow"

class SolitaireApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solitaire Coursework")
        self.root.geometry("900x750")

        self.color_bg = "#006400"
        self.color_card_back = "#4169E1"

        self.root.configure(bg=self.color_bg)

        self.container = tk.Frame(root, bg=self.color_bg)
        self.container.pack(fill="both", expand=True)

        self.engine = None
        self.selected_zone = None
        self.selected_cards_count = 0

        self.start_time = 0
        self.timer_running = False
        self.elapsed_time_str = "00:00"

        self.create_menu_screen()
        self.create_game_screen()
        self.show_menu()

    def create_menu_screen(self):
        self.menu_frame = tk.Frame(self.container, bg=self.color_bg)

        title = tk.Label(self.menu_frame, text="SOLITAIRE", font=("Arial", 40, "bold"), bg=self.color_bg, fg="white")
        title.pack(pady=80)

        btn_style = {"font": ("Arial", 16), "width": 20, "pady": 10}

        tk.Button(self.menu_frame, text="Почати гру", command=self.start_new_game, **btn_style).pack(pady=10)
        tk.Button(self.menu_frame, text="Налаштування", command=self.show_settings_window, **btn_style).pack(pady=10)
        tk.Button(self.menu_frame, text="Вихід", command=self.root.quit, **btn_style).pack(pady=10)

    def create_game_screen(self):
        self.game_frame = tk.Frame(self.container, bg=self.color_bg)

        control_panel = tk.Frame(self.game_frame, bg="#004d00", height=50)
        control_panel.pack(fill="x", side="top")

        pack_opts = {"side": "left", "padx": 5, "pady": 5}

        tk.Button(control_panel, text="Меню", command=self.return_to_menu).pack(**pack_opts)
        tk.Button(control_panel, text="Скасувати хід", command=self.undo_move).pack(**pack_opts)
        tk.Button(control_panel, text="Повторити роздачу", command=self.restart_current_deal).pack(**pack_opts)
        tk.Button(control_panel, text="Нова роздача", command=self.start_new_game).pack(**pack_opts)

        self.lbl_timer = tk.Label(control_panel, text="Час: 00:00", bg="#004d00", fg="white", font=("Arial", 12))
        self.lbl_timer.pack(side="right", padx=15)

        self.lbl_moves = tk.Label(control_panel, text="Ходів: 0", bg="#004d00", fg="white", font=("Arial", 12))
        self.lbl_moves.pack(side="right", padx=15)

        self.canvas = tk.Canvas(self.game_frame, bg=self.color_bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            self.elapsed_time_str = f"{mins:02}:{secs:02}"
            self.lbl_timer.config(text=f"Час: {self.elapsed_time_str}")
            self.root.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False

    def show_menu(self):
        self.stop_timer()
        self.game_frame.pack_forget()
        self.update_colors()
        self.menu_frame.pack(fill="both", expand=True)

    def return_to_menu(self):
        self.engine = None
        was_running = self.timer_running
        self.timer_running = False

        if messagebox.askyesno("Вихід", "Перервати гру і вийти в меню?"):
            self.show_menu()
        else:
            if was_running:
                self.timer_running = True
                self.update_timer()

    def start_new_game(self):
        if self.engine:
            if not messagebox.askyesno("Нова гра", "Почати нову гру? Поточний прогрес буде втрачено."):
                return
        try:
            self.engine = SolitaireEngine()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.setup_game_ui()

    def restart_current_deal(self):
        if self.engine:
            if messagebox.askyesno("Рестарт", "Почати цю роздачу спочатку?"):
                self.engine.restart_current()
                self.setup_game_ui()

    def setup_game_ui(self):
        self.selected_zone = None
        self.menu_frame.pack_forget()
        self.update_colors()
        self.game_frame.pack(fill="both", expand=True)
        self.draw_game()
        self.start_timer()

    def undo_move(self):
        if self.engine and self.engine.undo():
            self.selected_zone = None
            self.draw_game()

    def show_settings_window(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Налаштування")
        settings_win.geometry("300x200")
        settings_win.transient(self.root)
        settings_win.grab_set()

        tk.Label(settings_win, text="Зміна кольорів", font=("Arial", 12, "bold")).pack(pady=10)

        def choose_bg():
            color = colorchooser.askcolor(title="Колір фону", color=self.color_bg)[1]
            if color:
                self.color_bg = color
                self.update_colors()

        def choose_back():
            color = colorchooser.askcolor(title="Колір сорочки карт", color=self.color_card_back)[1]
            if color:
                self.color_card_back = color
                if self.game_frame.winfo_ismapped():
                    self.draw_game()

        tk.Button(settings_win, text="Змінити фон столу", command=choose_bg).pack(pady=5, fill="x", padx=20)
        tk.Button(settings_win, text="Змінити сорочку карт", command=choose_back).pack(pady=5, fill="x", padx=20)
        tk.Button(settings_win, text="Закрити", command=settings_win.destroy).pack(pady=15)

    def update_colors(self):
        self.root.configure(bg=self.color_bg)
        self.container.configure(bg=self.color_bg)
        self.menu_frame.configure(bg=self.color_bg)
        self.game_frame.configure(bg=self.color_bg)
        self.canvas.configure(bg=self.color_bg)

        for widget in self.menu_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.color_bg)

    def draw_game(self):
        self.canvas.delete("all")
        if not self.engine: return

        # Stock
        stock_size = self.engine.get_pile_size(3, 0)
        if stock_size > 0: self.draw_card_back(MARGIN, MARGIN, "stock")
        else: self.draw_placeholder(MARGIN, MARGIN, "stock")

        # Waste
        waste_size = self.engine.get_pile_size(2, 0)
        waste_x = MARGIN + CARD_WIDTH + GAP
        if waste_size > 0:
            c = self.engine.get_card_info(2, 0, waste_size - 1)
            self.draw_card_face(waste_x, MARGIN, c, "waste", selected=(self.selected_zone == (2, 0)))
        else:
            self.draw_placeholder(waste_x, MARGIN, "waste")

        # Foundations
        for i in range(4):
            x = MARGIN + (3 + i) * (CARD_WIDTH + GAP)
            size = self.engine.get_pile_size(1, i)
            tag = f"found_{i}"
            if size > 0:
                c = self.engine.get_card_info(1, i, size - 1)
                self.draw_card_face(x, MARGIN, c, tag, selected=(self.selected_zone == (1, i)))
            else:
                self.draw_placeholder(x, MARGIN, tag, "A")

        # Tableau
        start_y = MARGIN + CARD_HEIGHT + GAP
        for i in range(7):
            x = MARGIN + i * (CARD_WIDTH + GAP)
            size = self.engine.get_pile_size(0, i)
            tag_base = f"tab_{i}"

            if size == 0:
                self.draw_placeholder(x, start_y, tag_base)
            else:
                curr_y = start_y
                for j in range(size):
                    c = self.engine.get_card_info(0, i, j)
                    is_selected = False
                    if self.selected_zone == (0, i) and j >= size - self.selected_cards_count:
                        is_selected = True

                    if c['face_up']:
                        self.draw_card_face(x, curr_y, c, f"{tag_base}_{j}", selected=is_selected)
                        curr_y += VERTICAL_OFFSET_FACE_UP
                    else:
                        self.draw_card_back(x, curr_y, f"{tag_base}_{j}")
                        curr_y += VERTICAL_OFFSET_FACE_DOWN

        self.lbl_moves.config(text=f"Ходів: {self.engine.get_moves_count()}")
        if self.engine.is_win():
            self.stop_timer()
            messagebox.showinfo("Перемога", f"Виграно за {self.elapsed_time_str}!")

    def draw_card_face(self, x, y, card_info, tag, selected=False):
        color = "red" if card_info['suit'] in [0, 1] else "black"
        suit_sym = ["♥", "♦", "♣", "♠"][card_info['suit']]
        rank_sym = ["?", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"][card_info['rank']]
        outline = COLOR_SELECTED if selected else COLOR_OUTLINE
        width = 3 if selected else 1

        self.canvas.create_rectangle(x, y, x + CARD_WIDTH, y + CARD_HEIGHT,
                                     fill="white", outline=outline, width=width, tags=tag)
        self.canvas.create_text(x + 5, y + 5, text=f"{rank_sym}\n{suit_sym}",
                                fill=color, font=("Arial", 12, "bold"), anchor="nw", tags=tag)
        self.canvas.create_text(x + CARD_WIDTH/2, y + CARD_HEIGHT/2,
                                text=suit_sym, fill=color, font=("Arial", 30), tags=tag)

    def draw_card_back(self, x, y, tag):
        self.canvas.create_rectangle(x, y, x + CARD_WIDTH, y + CARD_HEIGHT,
                                     fill=self.color_card_back, outline="white", tags=tag)
        self.canvas.create_line(x, y, x+CARD_WIDTH, y+CARD_HEIGHT, fill="white", tags=tag)
        self.canvas.create_line(x+CARD_WIDTH, y, x, y+CARD_HEIGHT, fill="white", tags=tag)

    def draw_placeholder(self, x, y, tag, text=""):
        self.canvas.create_rectangle(x, y, x + CARD_WIDTH, y + CARD_HEIGHT,
                                     outline="#00FF00", width=2, tags=tag) # Яскраво-зелений контур
        if text:
            self.canvas.create_text(x + CARD_WIDTH/2, y + CARD_HEIGHT/2, text=text, fill="#00FF00", tags=tag)

    def on_click(self, event):
        x, y = event.x, event.y
        if MARGIN <= x <= MARGIN + CARD_WIDTH and MARGIN <= y <= MARGIN + CARD_HEIGHT:
            self.engine.draw_stock()
            self.selected_zone = None
            self.draw_game()
            return
        clicked = self.get_zone_at(x, y)
        if not clicked:
            self.selected_zone = None
            self.draw_game()
            return
        z_type, z_idx, c_idx = clicked
        if self.selected_zone is None:
            valid = False
            count = 1
            if z_type == 2 and self.engine.get_pile_size(2, 0) > 0: valid = True
            elif z_type == 1 and self.engine.get_pile_size(1, z_idx) > 0: valid = True
            elif z_type == 0:
                size = self.engine.get_pile_size(0, z_idx)
                if size > 0:
                    c = self.engine.get_card_info(0, z_idx, c_idx)
                    if c['face_up']:
                        valid = True
                        count = size - c_idx
            if valid:
                self.selected_zone = (z_type, z_idx)
                self.selected_cards_count = count
        else:
            from_type, from_idx = self.selected_zone
            if (from_type, from_idx) != (z_type, z_idx):
                self.engine.move(from_type, from_idx, z_type, z_idx, self.selected_cards_count)
            self.selected_zone = None
        self.draw_game()

    def get_zone_at(self, x, y):
        # Waste
        wx = MARGIN + CARD_WIDTH + GAP
        if wx <= x <= wx + CARD_WIDTH and MARGIN <= y <= MARGIN + CARD_HEIGHT:
            return (2, 0, self.engine.get_pile_size(2, 0)-1)
        # Foundations
        for i in range(4):
            fx = MARGIN + (3 + i) * (CARD_WIDTH + GAP)
            if fx <= x <= fx + CARD_WIDTH and MARGIN <= y <= MARGIN + CARD_HEIGHT:
                return (1, i, self.engine.get_pile_size(1, i)-1)
        # Tableau
        start_y = MARGIN + CARD_HEIGHT + GAP
        for i in range(7):
            tx = MARGIN + i * (CARD_WIDTH + GAP)
            if tx <= x <= tx + CARD_WIDTH:
                size = self.engine.get_pile_size(0, i)
                if size == 0:
                    if start_y <= y <= start_y + CARD_HEIGHT: return (0, i, -1)
                else:
                    curr_y = start_y
                    for j in range(size):
                        c = self.engine.get_card_info(0, i, j)
                        next_y = curr_y + (VERTICAL_OFFSET_FACE_UP if c['face_up'] else VERTICAL_OFFSET_FACE_DOWN)
                        if j == size - 1:
                            if curr_y <= y <= curr_y + CARD_HEIGHT: return (0, i, j)
                        else:
                            if curr_y <= y < next_y: return (0, i, j)
                        curr_y = next_y
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireApp(root)
    root.mainloop()