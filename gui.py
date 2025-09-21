"""
gui.py — Tkinter GUI (Phase 2, 제출용)
요구사항:
- 사칙/괄호, = 버튼
- π, e
- sqrt, cbrt(³√), x^2, x^3, x^y
- factorial(!)
- sin/cos/tan + asin/acos/atan
- log10 + log_b(임의 밑)
- Shift 토글로 위 기능들 전환
- eqn 버튼으로 이차/삼차 방정식 해 구하기
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import engine
import equations

# 안전 평가: engine 네임스페이스만 허용
def eval_safe(expr: str):
    return eval(expr, {"__builtins__": {}}, vars(engine))

def insert(entry: ttk.Entry, text: str) -> None:
    entry.insert(tk.END, text)

class CalcGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ICS4U Scientific Calculator")

        self.shift = tk.BooleanVar(value=False)

        # 표시창
        self.display = ttk.Entry(root, font=("SF Mono", 16))
        self.display.grid(row=0, column=0, columnspan=6, sticky="nsew", padx=8, pady=8)

        # 상단 컨트롤
        ttk.Checkbutton(root, text="Shift", variable=self.shift,
                        command=self._refresh_labels).grid(row=1, column=0, sticky="ew", padx=4, pady=2)
        ttk.Button(root, text="C", command=self.clear).grid(row=1, column=4, sticky="ew", padx=4, pady=2)
        ttk.Button(root, text="⌫", command=self.backspace).grid(row=1, column=5, sticky="ew", padx=4, pady=2)

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

        self._refresh_labels()

    # ---------- UI helpers ----------
    def _add_button(self, r, c, primary, alt, handler):
        var = tk.StringVar(value=primary or "")
        btn = ttk.Button(self.root, textvariable=var)
        btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        self._buttons.append((var, primary, alt, handler))
        btn.configure(command=lambda v=var, p=primary, a=alt, h=handler: h(v.get(), p, a))

    def _refresh_labels(self):
        for var, primary, alt, _ in self._buttons:
            var.set(alt if (self.shift.get() and alt) else primary)

    def clear(self):
        self.display.delete(0, tk.END)

    def backspace(self):
        s = self.display.get()
        if s:
            self.display.delete(len(s)-1, tk.END)

    # ---------- Handlers ----------
    def type_(self, label, *_):
        # ×, ÷를 파이썬 연산자로 치환
        if label == "×": label = "*"
        if label == "÷": label = "/"
        insert(self.display, label)

    def const_btn(self, *_):
        # π ↔ e  (엔진에서 pi/e 별칭 지원)
        insert(self.display, "pi" if not self.shift.get() else "e")

    def root_btn(self, *_):
        # √ ↔ ³√
        insert(self.display, "sqrt(" if not self.shift.get() else "cbrt(")

    def square_cube_btn(self, *_):
        # x^2 ↔ x^3  → **2 / **3
        insert(self.display, "**2" if not self.shift.get() else "**3")

    def fact_pow_btn(self, *_):
        # ! ↔ x^y  (파이썬은 후위 !가 없으므로 factorial( 로 입력)
        if not self.shift.get():
            insert(self.display, "factorial(")
        else:
            insert(self.display, "**")  # y를 이어서 입력

    def trig_btn(self, label, *_):
        # sin/cos/tan ↔ asin/acos/atan
        insert(self.display, f"{label}(")

    def log_btn(self, *_):
        if not self.shift.get():
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
        expr = self.display.get()
        try:
            result = eval_safe(expr)
            self.clear()
            insert(self.display, str(result))
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