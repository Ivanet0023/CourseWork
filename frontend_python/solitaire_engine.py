import ctypes
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)

lib_name = "Solitaire.dll"
lib_path = resource_path(lib_name)

try:
    lib = ctypes.CDLL(lib_path)
except FileNotFoundError:
    print(f"ПОМИЛКА: Не знайдено {lib_name} у папці {os.path.dirname(__file__)}")
    sys.exit(1)


lib.Game_Create.restype = ctypes.c_void_p

lib.Game_Start.argtypes = [ctypes.c_void_p]
lib.Game_DrawFromStock.argtypes = [ctypes.c_void_p]

lib.Game_RestartCurrent.argtypes = [ctypes.c_void_p]

lib.Game_Move.restype = ctypes.c_bool
lib.Game_Move.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

lib.Game_GetPileSize.restype = ctypes.c_int
lib.Game_GetPileSize.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

lib.Game_GetCard.restype = ctypes.c_bool
lib.Game_GetCard.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_bool)
]

lib.Game_GetMoves.restype = ctypes.c_int
lib.Game_GetMoves.argtypes = [ctypes.c_void_p]

lib.Game_IsWin.restype = ctypes.c_bool
lib.Game_IsWin.argtypes = [ctypes.c_void_p]

lib.Game_Delete.argtypes = [ctypes.c_void_p]

lib.Game_Undo.restype = ctypes.c_bool
lib.Game_Undo.argtypes = [ctypes.c_void_p]

class SolitaireEngine:
    def __init__(self):
        self.obj = lib.Game_Create()
        self.start_game()

    def start_game(self):
        lib.Game_Start(self.obj)

    def draw_stock(self):
        lib.Game_DrawFromStock(self.obj)

    def move(self, from_zone, from_idx, to_zone, to_idx, num_cards=1):
        return lib.Game_Move(self.obj, from_zone, from_idx, to_zone, to_idx, num_cards)

    def get_pile_size(self, zone_type, zone_idx=0):
        return lib.Game_GetPileSize(self.obj, zone_type, zone_idx)

    def get_card_info(self, zone_type, zone_idx, card_idx):
        s = ctypes.c_int()
        r = ctypes.c_int()
        f = ctypes.c_bool()

        success = lib.Game_GetCard(self.obj, zone_type, zone_idx, card_idx,
                                   ctypes.byref(s), ctypes.byref(r), ctypes.byref(f))

        if success:
            return {"suit": s.value, "rank": r.value, "face_up": f.value}
        return None

    def get_moves_count(self):
        return lib.Game_GetMoves(self.obj)

    def is_win(self):
        return lib.Game_IsWin(self.obj)

    def __del__(self):
        if hasattr(self, 'obj'):
            lib.Game_Delete(self.obj)

    def undo(self):
        return lib.Game_Undo(self.obj)

    def restart_current(self):
        lib.Game_RestartCurrent(self.obj)