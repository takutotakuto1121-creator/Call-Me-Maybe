from src.check_json import JsonChecker

checker = JsonChecker()

print(f"initial mode: {checker.state.mode}, in_string={checker.state.in_string}")
print()

# ログから実際に生成された文字列を再現する
text_so_far = 'fn_add_numbers",'

for c in text_so_far:
    ok = checker.check_char(c)
    print(f"{c!r:6} -> {ok}, mode={checker.state.mode}, in_string={checker.state.in_string}, "
          f"exist_comma={checker.state.exist_comma}, exist_space={checker.state.exist_space}")
    if not ok:
        print(">>> STOPPED HERE <<<")
        break

print()
print(f"=== final state ===")
print(f"mode={checker.state.mode}")
print(f"in_string={checker.state.in_string}")

print()
print("--- now trying '\\n' ---")
ok = checker.check_char("\n")
print(f"'\\n' -> {ok}, mode={checker.state.mode}")
