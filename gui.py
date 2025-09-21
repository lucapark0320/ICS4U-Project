"""
gui.py — Tkinter GUI (Shift 버튼 토글 + Shift 키 바인딩)
- 숫자/사칙/괄호/= 버튼
- π↔e, √↔³√, x²↔x³, !↔x^y, log10↔log_b(팝업), sin/cos/tan↔asin/acos/atan (Shift)
- eqn 버튼: 이차/삼차 방정식 해
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import engine
import equations
import re

# 안전 평가: engine 네임스페이스만 허용
def eval_safe(expr: str):
    return eval(expr, {"__builtins__": {}}, vars(engine))

def get_text(entry: ttk.Entry) -> str:
    return entry.get()

def set_text(entry: ttk.Entry, s: str) -> None:
    entry.delete(0, tk.END); entry.insert(tk.END, s)

def insert(entry: ttk.Entry, s: str) -> None:
    entry.insert(tk.END, s)

# 마지막 "원자" 토큰(숫자, pi/e, 닫는 괄호, 함수호출 등) 범위를 찾아주는 정규식
ATOM_RE = re.compile(
    r"(?:"
    r"[A-Za-z_][A-Za-z_0-9]*\([^()]*\)"  # 함수호출 like sin(30)
    r"|[A-Za-z_][A-Za-z_0-9]*"           # 식별자 pi, e
    r"|\d+(?:\.\d+)?"                    # 숫자
    r"|\)"                               # 닫는 괄호
    r")$"
)

def wrap_last_atom(entry: ttk.Entry, prefix: str, suffix: str = ")") -> bool:
    """
    표시창의 맨 끝 '원자'를 prefix+()로 감싼다.
    예: 5 -> factorial(5),  sin(30) -> factorial(sin(30)),  (2+3) -> factorial((2+3))
    """
    s = get_text(entry)
    if not s: return False
    # 1) 닫는 괄호로 끝나는 경우: 괄호쌍 통째로 감싸기
    if s.endswith(")"):
        depth = 0
        for i in range(len(s)-1, -1, -1):
            if s[i] == ")": depth += 1
            elif s[i] == "(":
                depth -= 1
                if depth == 0:
                    j = i  # 매칭 '('
                    new = s[:j] + f"{prefix}{s[j:]}"
                    set_text(entry, new)
                    insert(entry, suffix)
                    return True
        return False
    # 2) 그 외: 마지막 원자 토큰 찾기
    m = ATOM_RE.search(s)
    if not m:
        return False
    start = m.start()
    inner = s[start:]
    new = s[:start] + f"{prefix}{inner}{suffix}"
    set_text(entry, new)
    return True

class CalcGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ICS4U Scientific Calculator")

        # Shift 상태 (토글)
        self.shift_on = False

        # 표시창
        self.display = ttk.Entry(root, font=("SF Mono", 16))
        self.display.grid(row=0, column=0, columnspan=6, sticky="nsew", padx=8, pady=8)

        # 상단 컨트롤: Shift(버튼), C, ⌫
        self.shift_btn = ttk.Button(root, text="Shift (Off)", command=self.toggle_shift)
        self.shift_btn.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4, pady=2)

        ttk.Button(root, text="C", command=self.clear).grid(row=1, column=4, sticky="nsew", padx=4, pady=2)
        ttk.Button(root, text="⌫", command=self.backspace).grid(row=1, column=5, sticky="nsew", padx=4, pady=2)

        # (기본라벨, Shift라벨, handler)
        self._buttons = []
        rows = [
            [("(", None, self.type_), (")", None, self.type_),
             ("π", "e", self.const_btn), ("log10", "log_b", self.log_btn),
             ("√", "³√", self.root_btn), ("!", "x^y", self.fact_pow_btn)],
            [("7", None, self.type_), ("8", None, self.type_), ("9", None, self.type_),
             ("÷", None, self.type_), ("sin", "asin", self.trig_btn), ("eqn", None, self.eqn_btn)],
            [("4", None, self.type_), ("5", None, self.type_), ("6", None, self.type_),
             ("×", None, self.type_), ("cos", "acos", self.trig_btn), ("x^2", "x^3", self.square_cube_btn)],
            [("1", None, self.type_), ("2", None, self.type_), ("3", None, self.type_),
             ("-", None, self.type_), ("tan", "atan", self.trig_btn), ("=", None, self.equals_btn)],
            [("0", None, self.type_), (".", None, self.type_), (",", None, self.type_),  # 콤마: log_b 수동 입력 편의
             ("+", None, self.type_), ("/", None, self.type_), ("*", None, self.type_)],
        ]

        r0 = 2
        for r, row in enumerate(rows, start=r0):
            for c, (pri, alt, handler) in enumerate(row):
                self._add_button(r, c, pri, alt, handler)

        # grid stretch
        for i in range(6):
            root.grid_columnconfigure(i, weight=1)
        for i in range(8):
            root.grid_rowconfigure(i, weight=1)

        # 키보드 Shift 키로도 토글 (편의)
        root.bind_all("<KeyPress-Shift_L>", self._kb_toggle_shift)
        root.bind_all("<KeyPress-Shift_R>", self._kb_toggle_shift)

        self._refresh_labels()

    # ---------- Shift ----------
    def toggle_shift(self, *_):
        self.shift_on = not self.shift_on
        self.shift_btn.config(text=f"Shift ({'On' if self.shift_on else 'Off'})")
        self._refresh_labels()

    def _kb_toggle_shift(self, event):
        # 키보드 Shift 눌렀을 때도 토글 (원하면 주석 처리 가능)
        self.toggle_shift()

    # ---------- UI helpers ----------
    def _add_button(self, r, c, primary, alt, handler):
        var = tk.StringVar(value=primary or "")
        btn = ttk.Button(self.root, textvariable=var)
        btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        self._buttons.append((var, primary, alt, handler))
        btn.configure(command=lambda v=var, p=primary, a=alt, h=handler: h(v.get(), p, a))

    def _refresh_labels(self):
        for var, primary, alt, _ in self._buttons:
            var.set(alt if (self.shift_on and alt) else primary)

    def clear(self):
        set_text(self.display, "")

    def backspace(self):
        s = get_text(self.display)
        if s:
            set_text(self.display, s[:-1])

    # ---------- Handlers ----------
    def type_(self, label, *_):
        # ×, ÷를 파이썬 연산자로 치환
        if label == "×": label = "*"
        if label == "÷": label = "/"
        insert(self.display, label)

    def const_btn(self, *_):
        # π ↔ e  (엔진에서 pi/e 별칭 지원)
        insert(self.display, "pi" if not self.shift_on else "e")

    def root_btn(self, *_):
        # √ ↔ ³√
        insert(self.display, "sqrt(" if not self.shift_on else "cbrt(")

    def square_cube_btn(self, *_):
        # x^2 ↔ x^3  → **2 / **3
        insert(self.display, "**2" if not self.shift_on else "**3")

    def fact_pow_btn(self, *_):
        # ! ↔ x^y
        if not self.shift_on:
            # 후위 !처럼: 마지막 원자를 factorial(...)로 감싸기
            if not wrap_last_atom(self.display, "factorial("):
                insert(self.display, "factorial(")  # fallback
        else:
            insert(self.display, "**")  # 이후 y 입력

    def trig_btn(self, label, *_):
        # sin/cos/tan ↔ asin/acos/atan
        insert(self.display, f"{label}(")

    def log_btn(self, *_):
        if not self.shift_on:
            insert(self.display, "log10(")
        else:
            # 임의 밑 로그: log_b(value, base)
            try:
                val = simpledialog.askstring("log_b", "Value x:")
                base = simpledialog.askstring("log_b", "Base b:")
                if val is None or base is None:
                    return
                float(val); float(base)
                insert(self.display, f"log_b({val}, {base})")
            except Exception:
                messagebox.showerror("Error", "숫자를 올바르게 입력하세요.")

    def equals_btn(self, *_):
        expr = get_text(self.display)
        try:
            result = eval_safe(expr)
            set_text(self.display, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eqn_btn(self, *_):
        # Quadratic? (No = Cubic)
        ans = messagebox.askquestion("eqn", "Quadratic? (No = Cubic)")
        try:
            if ans == "yes":
                a = float(simpledialog.askstring("Quadratic", "a:"))
                b = float(simpledialog.askstring("Quadratic", "b:"))
                c = float(simpledialog.askstring("Quadratic", "c:"))
                r1, r2 = equations.solve_quadratic(a, b, c)
                messagebox.showinfo("Roots", f"{r1}\n{r2}")
            else:
                a = float(simpledialog.askstring("Cubic", "a:"))
                b = float(simpledialog.askstring("Cubic", "b:"))
                c = float(simpledialog.askstring("Cubic", "c:"))
                d = float(simpledialog.askstring("Cubic", "d:"))
                r = equations.solve_cubic(a, b, c, d)
                messagebox.showinfo("Roots", f"{r[0]}\n{r[1]}\n{r[2]}")
        except (TypeError, ValueError):
            pass

def launch():
    root = tk.Tk()
    CalcGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch()