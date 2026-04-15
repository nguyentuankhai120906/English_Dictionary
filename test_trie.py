"""
test_trie.py  –  Kiểm tra tự động các thao tác Radix-Trie
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from radix_trie import RadixTrie

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"

def check(cond, msg):
    print(f"  {'  ' + PASS if cond else '  ' + FAIL}  {msg}")
    return cond

all_ok = True

print("\n══════════════════════════════════════════")
print("  RADIX-TRIE UNIT TEST")
print("══════════════════════════════════════════\n")

trie = RadixTrie()
# Xóa file cũ nếu có để test sạch
import shutil
if os.path.exists("data"):
    shutil.rmtree("data")

# ─── 1. INSERT ────────────────────────────────
print("[1] INSERT – Thêm từ")
ok1, _ = trie.insert("apple",   "a round fruit")
ok2, _ = trie.insert("application", "a software program")
ok3, _ = trie.insert("apply",   "to request formally")
ok4, _ = trie.insert("bee",     "a flying insect")
ok5, _ = trie.insert("bear",    "a large mammal")
ok6, _ = trie.insert("cat",     "a small pet")

all_ok &= check(ok1 and ok2 and ok3 and ok4 and ok5 and ok6,
                "Thêm 6 từ thành công")
all_ok &= check(trie.word_count == 6, f"word_count = 6 (actual={trie.word_count})")

# Duplicate
ok_dup, msg_dup = trie.insert("apple", "another meaning")
all_ok &= check(not ok_dup, f"Từ trùng bị từ chối: {msg_dup}")

# Invalid char
ok_inv, msg_inv = trie.insert("hel1o", "invalid")
all_ok &= check(not ok_inv, f"Ký tự không hợp lệ bị từ chối: {msg_inv}")

print()

# ─── 2. SEARCH ────────────────────────────────
print("[2] SEARCH – Tìm nghĩa")
ok, defn = trie.search("apple")
all_ok &= check(ok and defn == "a round fruit", f"Tìm 'apple': {defn}")

ok, defn = trie.search("application")
all_ok &= check(ok, f"Tìm 'application': {defn}")

ok, _ = trie.search("xyz")
all_ok &= check(not ok, "Tìm 'xyz' → không tìm thấy (đúng)")

ok, _ = trie.search("app")
all_ok &= check(not ok, "Tìm 'app' (không phải từ đầy đủ) → không tìm thấy (đúng)")

# Case insensitive
ok, defn = trie.search("APPLE")
all_ok &= check(ok and defn == "a round fruit", "Search không phân biệt hoa thường")

print()

# ─── 3. DELETE ────────────────────────────────
print("[3] DELETE – Xóa từ (soft delete)")

ok_d, msg_d = trie.delete("bee")
all_ok &= check(ok_d, f"Xóa 'bee': {msg_d}")
all_ok &= check(trie.word_count == 5, f"word_count = 5 (actual={trie.word_count})")

# Tìm lại từ đã xóa → phải trả về False
ok, _ = trie.search("bee")
all_ok &= check(not ok, "Search 'bee' sau khi xóa → không tìm thấy (đúng)")

# Xóa lần 2 → phải từ chối
ok_d2, msg_d2 = trie.delete("bee")
all_ok &= check(not ok_d2, f"Xóa 'bee' lần 2 → từ chối: {msg_d2}")

# Xóa từ không tồn tại
ok_d3, msg_d3 = trie.delete("xyz")
all_ok &= check(not ok_d3, f"Xóa 'xyz' → từ chối: {msg_d3}")

print()

# ─── 4. LIST ALL ──────────────────────────────
print("[4] GET ALL WORDS")
words = trie.get_all_words(include_deleted=False)
all_ok &= check(len(words) == 5, f"Có 5 từ (sau khi xóa 'bee'): {[w['word'] for w in words]}")

words_with_del = trie.get_all_words(include_deleted=True)
all_ok &= check(len(words_with_del) == 6, f"Có 6 từ khi include_deleted=True")

print()

# ─── 5. TRIE STRUCTURE ────────────────────────
print("[5] TRIE STRUCTURE")
viz = trie.visualize()
all_ok &= check("[ROOT]" in viz, "Cấu trúc trie hiển thị được")
all_ok &= check("apple" in viz or '"appl"' in viz or '"apple"' in viz,
                "Node 'apple' có trong cấu trúc")
print("  Trie structure:")
for line in viz.split("\n"):
    print("    " + line)

print()

# ─── 6. PERSISTENCE ───────────────────────────
print("[6] PERSISTENCE – Lưu & Tải")
trie.save()
trie2 = RadixTrie()
loaded = trie2.load()
all_ok &= check(loaded, "Load từ file thành công")
all_ok &= check(trie2.word_count == 5, f"word_count khớp sau load: {trie2.word_count}")
ok, defn = trie2.search("apple")
all_ok &= check(ok and defn == "a round fruit", f"Dữ liệu còn nguyên sau load: {defn}")

print()

# ─── 7. PURGE ─────────────────────────────────
print("[7] PURGE – Dọn sạch node đã xóa")
n_purged = trie.purge_deleted()
all_ok &= check(n_purged >= 1, f"Đã purge {n_purged} node")
words_after_purge = trie.get_all_words(include_deleted=True)
all_ok &= check(all(not w["deleted"] for w in words_after_purge),
                "Không còn từ deleted sau purge")

print()
print("══════════════════════════════════════════")
if all_ok:
    print("\033[92m  TẤT CẢ TEST ĐỀU PASS ✓\033[0m")
else:
    print("\033[91m  CÓ TEST FAIL!\033[0m")
print("══════════════════════════════════════════\n")

# Cleanup
if os.path.exists("data"):
    shutil.rmtree("data")
