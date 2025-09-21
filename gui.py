"""
gui.py — Tkinter GUI (Phase 2)
요구사항:
- 사칙, 괄호
- π, e
- sqrt, cbrt(³√), x^2, x^3, x^y
- factorial(!)
- sin/cos/tan + asin/acos/atan
- log10 + log_b(임의 밑)
- Shift 버튼으로 위 기능들 토글
- eqn 버튼으로 이차/삼차 방정식 해 구하기
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import engine
import equations

# 유틸: 표시창 문자열에 추가
def insert(entry: ttk.Entry, text: str) -> None:
    entry.insert(tk.END, text)

def evaluate_expression(expr: str):
    """
    Entry의 식을 평가.
    - 위험 방지: __builtins__ 제거
    - engine 모듈의 함수/상수만 허용(sin, sqrt, PI, E, factorial, log_b, ...)
    """
    return eval(expr, {"__builtins__": {}}, vars(engine))

class CalcGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ICS4U Scientific Calculator")

        self.shift = tk.BooleanVar(value=False)

        # ── 표시창
        self.display = ttk.Entry(root, font=("SF Mono", 16))
        self.display.grid(row=0, column=0, columnspan=6, sticky="nsew", padx=8, pady=8)

        # ── 상단 컨트롤
        ttk.Checkbutton(root, text="Shift", variable=self.shift,
                        command=self._refresh_labels).grid(row=1, column=0, sticky="ew", padx=4, pady=2)
        ttk.Button(root, text="C", command=self.clear).grid(row=1, column=4, sticky="ew", padx=4, pady=2)
        ttk.Button(root, text="⌫", command=self.backspace).grid(row=1, column=5, sticky="ew", padx=4, pady=2)

        # ── 버튼 정의: (기본라벨, Shift라벨, 핸들러)
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
            [("0", None, self.type_), (".", None, self.type_), (",", None, self.type_),  # 콤마는 log_b 수동 입력용
             ("+", None, self.type_), ("/", None, self.type_), ("*", None, self.type_)],
        ]

        # ── 배치
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

    # ── 버튼 생성/업데이트
    def _add_button(self, r, c, primary, alt, handler):
        var = tk.StringVar(value=primary or "")
        btn = ttk.Button(self.root, textvariable=var)
        btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        self._buttons.append((var, primary, alt, handler))
        btn.configure(command=lambda v=var, p=primary, a=alt, h=handler: h(v.get(), p, a))

    def _refresh_labels(self):
        for var, primary, alt, _ in self._buttons:
            var.set(alt if (self.shift.get() and alt) else primary)

    # ── 공통 동작
    def type_(self, label, *_):
        # ×, ÷를 파이썬 연산자로 치환
        if label == "×": label = "*"
        if label == "÷": label = "/"
        insert(self.display, label)

    def clear(self):
        self.display.delete(0, tk.END)

    def backspace(self):
        s = self.display.get()
        if s:
            self.display.delete(len(s)-1, tk.END)

    # ── 기능 핸들러
    def const_btn(self, label, *_):
        # π ⇄ e
        insert(self.display, "PI" if not self.shift.get() else "E")

    def root_btn(self, label, *_):
        # √ ⇄ ³√
        insert(self.display, "sqrt(" if not self.shift.get() else "cbrt(")

    def square_cube_btn(self, label, *_):
        # x^2 ⇄ x^3  → 파이썬 지수연산자는 **
        insert(self.display, "**2" if not self.shift.get() else "**3")

    def fact_pow_btn(self, label, *_):
        # ! ⇄ x^y
        if not self.shift.get():
            insert(self.display, "factorial(")
        else:
            insert(self.display, "**")  # 사용자가 y를 이어서 입력

    def trig_btn(self, label, *_):
        # sin/cos/tan ⇄ asin/acos/atan (DEG 기준, engine에 구현됨)
        insert(self.display, f"{label}(")

    def log_btn(self, label, *_):
        if not self.shift.get():
            insert(self.display, "log10(")
        else:
            # log_b(value, base) 를 바로 구성해 넣을 수도 있고,
            # 팝업으로 입력 받아 완성해 줄 수도 있음.
            try:
                val = simpledialog.askstring("log_b", "Value x:")
                base = simpledialog.askstring("log_b", "Base b:")
                if val is None or base is None:
                    return
                float(val); float(base)  # 형식 체크
                insert(self.display, f"log_b({val}, {base})")
            except Exception:
                messagebox.showerror("Error", "숫자를 올바르게 입력하세요.")

    def equals_btn(self, *_):
        expr = self.display.get()
        try:
            result = evaluate_expression(expr)
            self.clear()
            insert(self.display, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eqn_btn(self, *_):
        # 이차/삼차 중 선택
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