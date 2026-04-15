"""
main.py  –  Ứng dụng từ điển tiếng Anh (CLI)
==============================================
Sử dụng: python main.py

Thao tác hỗ trợ:
  1. Thêm từ
  2. Xóa từ
  3. Tìm nghĩa
  4. Xem toàn bộ từ điển
  5. Hiển thị cấu trúc Radix-Trie
  6. Dọn sạch (purge) từ đã xóa
  0. Thoát
"""

import os
import sys
from radix_trie import RadixTrie

# ─── ANSI color codes ───────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
DIM    = "\033[2m"

def clr(text, color): return f"{color}{text}{RESET}"


# ─── Banner ──────────────────────────────────────────────────────────────────
BANNER = f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════╗
║   📖  TỪ ĐIỂN TIẾNG ANH  –  Radix-Trie     ║
╚══════════════════════════════════════════════╝{RESET}
"""

MENU = f"""{DIM}─────────────────────────────────────────────{RESET}
  {clr('[1]', CYAN)} Thêm từ          {clr('[2]', CYAN)} Xóa từ
  {clr('[3]', CYAN)} Tìm nghĩa        {clr('[4]', CYAN)} Xem toàn bộ từ điển
  {clr('[5]', CYAN)} Cấu trúc Trie    {clr('[6]', CYAN)} Dọn sạch từ đã xóa
  {clr('[0]', RED )} Thoát
{DIM}─────────────────────────────────────────────{RESET}"""


# ─── Helpers ────────────────────────────────────────────────────────────────
def hr():
    print(clr("─" * 46, DIM))

def print_snapshot(trie: RadixTrie, title: str = "Trạng thái sau thao tác"):
    """In snapshot toàn bộ từ điển sau mỗi thao tác."""
    words = trie.get_all_words(include_deleted=False)
    print(f"\n{clr('📋 ' + title + f'  ({trie.word_count} từ)', YELLOW)}")
    if not words:
        print(clr("  (từ điển đang trống)", DIM))
    else:
        for i, entry in enumerate(words, 1):
            bullet = clr(f"  {i:2}.", DIM)
            word   = clr(entry['word'], BOLD)
            defn   = entry['definition']
            # Cắt bớt nếu quá dài để terminal đẹp
            if len(defn) > 60:
                defn = defn[:57] + "..."
            print(f"{bullet} {word}  →  {defn}")


# ─── Operations ─────────────────────────────────────────────────────────────
def op_add(trie: RadixTrie):
    hr()
    print(clr("➕ THÊM TỪ", BOLD))
    word = input("  Nhập từ tiếng Anh : ").strip()
    if not word:
        print(clr("  ⚠ Bỏ qua (không nhập gì).", YELLOW))
        return

    print("  Nhập nghĩa (Enter 2 lần để kết thúc nếu nhiều dòng):")
    lines = []
    while True:
        line = input("    > ")
        if line == "" and lines:
            break
        lines.append(line)
    definition = " ".join(lines).strip()

    # ── Trạng thái TRƯỚC ──
    print(clr("\n  [TRƯỚC KHI THÊM]", DIM))
    print_snapshot(trie, "Trie hiện tại")

    # ── Thực hiện ──
    ok, msg = trie.insert(word, definition)

    # ── Kết quả ──
    if ok:
        print(f"\n  {clr(msg, GREEN)}")
    else:
        print(f"\n  {clr(msg, RED)}")

    # ── Trạng thái SAU ──
    print(clr("\n  [SAU KHI THÊM]", DIM))
    print_snapshot(trie, "Trie sau thao tác")


def op_delete(trie: RadixTrie):
    hr()
    print(clr("🗑  XÓA TỪ", BOLD))
    word = input("  Nhập từ cần xóa : ").strip()

    # ── Trạng thái TRƯỚC ──
    print(clr("\n  [TRƯỚC KHI XÓA]", DIM))
    print_snapshot(trie, "Trie hiện tại")

    # ── Thực hiện ──
    ok, msg = trie.delete(word)

    # ── Kết quả ──
    if ok:
        print(f"\n  {clr(msg, GREEN)}")
    else:
        print(f"\n  {clr(msg, RED)}")

    # ── Trạng thái SAU ──
    print(clr("\n  [SAU KHI XÓA]", DIM))
    print_snapshot(trie, "Trie sau thao tác")


def op_search(trie: RadixTrie):
    hr()
    print(clr("🔍 TÌM NGHĨA", BOLD))
    word = input("  Nhập từ cần tìm : ").strip()
    ok, result = trie.search(word)
    if ok:
        print(f"\n  {clr('Từ:', BOLD)} {clr(word.lower(), CYAN)}")
        print(f"  {clr('Nghĩa:', BOLD)} {result}")
    else:
        print(f"\n  {clr(result, RED)}")


def op_list_all(trie: RadixTrie):
    hr()
    print(clr("📚 TOÀN BỘ TỪ ĐIỂN", BOLD))
    words = trie.get_all_words(include_deleted=False)
    if not words:
        print(clr("  Từ điển đang trống.", DIM))
        return
    print(f"  Tổng cộng: {clr(str(len(words)), YELLOW)} từ\n")
    for i, entry in enumerate(words, 1):
        print(f"  {clr(f'{i:3}.', DIM)} {clr(entry['word'], BOLD)}")
        print(f"       {entry['definition']}")
        print()


def op_show_trie(trie: RadixTrie):
    hr()
    print(clr("🌳 CẤU TRÚC RADIX-TRIE", BOLD))
    print(clr("  (Node có ★ = từ đầy đủ, [DELETED] = đã xóa mềm)\n", DIM))
    print(trie.visualize(max_depth=20))


def op_purge(trie: RadixTrie):
    hr()
    print(clr("🧹 DỌN SẠCH (PURGE)", BOLD))
    deleted_before = [e for e in trie.get_all_words(include_deleted=True) if e["deleted"]]
    if not deleted_before:
        print(clr("  Không có từ nào cần dọn.", DIM))
        return

    print(clr("  Các từ sẽ bị xóa vĩnh viễn:", YELLOW))
    for e in deleted_before:
        print(f"    - {clr(e['word'], RED)}")

    confirm = input(clr("\n  Xác nhận? (y/n): ", YELLOW))
    if confirm.lower() != "y":
        print(clr("  Đã hủy.", DIM))
        return

    n = trie.purge_deleted()
    print(f"\n  {clr(f'✓ Đã dọn sạch {n} node.', GREEN)}")
    print_snapshot(trie, "Trie sau khi purge")


# ─── Seed data ──────────────────────────────────────────────────────────────
SEED_DATA = [
    ("apple",   "a round fruit with red or green skin and white flesh"),
    ("application", "a program or piece of software designed for a specific purpose"),
    ("apply",   "to put something on a surface; to request formally"),
    ("bee",     "a flying insect that makes honey"),
    ("bear",    "a large, heavy mammal with thick fur"),
    ("bit",     "a small piece or amount of something"),
    ("cat",     "a small domesticated carnivorous mammal"),
    ("car",     "a road vehicle powered by a motor engine"),
    ("data",    "facts or information used for reference or analysis"),
    ("dog",     "a domesticated carnivorous mammal kept as a pet"),
    ("happy",   "feeling or showing pleasure or contentment"),
    ("hello",   "used as a greeting or to begin a conversation"),
]

def seed_demo(trie: RadixTrie):
    """Thêm dữ liệu mẫu nếu trie còn rỗng."""
    if trie.word_count == 0:
        print(clr("\n  (Thêm dữ liệu mẫu...)", DIM))
        for word, defn in SEED_DATA:
            trie.insert(word, defn)
        print(clr(f"  ✓ Đã thêm {len(SEED_DATA)} từ mẫu.\n", GREEN))


# ─── Main ───────────────────────────────────────────────────────────────────
def main():
    # Phải chạy từ thư mục chứa file này
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    trie = RadixTrie()
    loaded = trie.load()

    print(BANNER)
    if loaded:
        print(clr(f"  ✓ Đã tải từ điển: {trie.word_count} từ.", GREEN))
    else:
        print(clr("  (Tạo từ điển mới...)", DIM))
        trie.save()
        seed_demo(trie)

    while True:
        print(MENU)
        print(f"  Từ điển hiện tại: {clr(str(trie.word_count), YELLOW)} từ")
        choice = input(f"\n{clr('  Chọn [0-6]: ', BOLD)}").strip()

        if   choice == "1": op_add(trie)
        elif choice == "2": op_delete(trie)
        elif choice == "3": op_search(trie)
        elif choice == "4": op_list_all(trie)
        elif choice == "5": op_show_trie(trie)
        elif choice == "6": op_purge(trie)
        elif choice == "0":
            print(clr("\n  Tạm biệt! 👋\n", CYAN))
            sys.exit(0)
        else:
            print(clr("  ⚠ Lựa chọn không hợp lệ.", YELLOW))


if __name__ == "__main__":
    main()
