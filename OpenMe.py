
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import engine
import equations
import re

# Safe eval: allow only names from engine
def eval_safe(expr: str):
    return eval(expr, {"__builtins__": {}}, vars(engine))

def get_text(entry: ttk.Entry) -> str:
    return entry.get()

def set_text(entry: ttk.Entry, s: str) -> None:
    entry.delete(0, tk.END); entry.insert(tk.END, s)

def insert(entry: ttk.Entry, s: str) -> None:
    entry.insert(tk.END, s)

# Last "atom" at the end (number, identifier, call, or ')')
ATOM_RE = re.compile(
    r"(?:"
    r"[A-Za-z_][A-Za-z_0-9]*\([^()]*\)"  # function call like sin(30)
    r"|[A-Za-z_][A-Za-z_0-9]*"           # identifier like pi, e
    r"|\d+(?:\.\d+)?"                    # number
    r"|\)"                               # closing paren
    r")$"
)

def wrap_last_atom(entry: ttk.Entry, prefix: str, suffix: str = ")") -> bool:
    """Wrap the trailing atom as prefix(atom)."""
    s = get_text(entry)
    if not s: return False
    if s.endswith(")"):
        depth = 0
        for i in range(len(s)-1, -1, -1):
            if s[i] == ")": depth += 1
            elif s[i] == "(":
                depth -= 1
                if depth == 0:
                    j = i
                    new = s[:j] + f"{prefix}{s[j:]}"
                    set_text(entry, new)
                    insert(entry, suffix)
                    return True
        return False
    m = ATOM_RE.search(s)
    if not m: return False
    start = m.start()
    inner = s[start:]
    new = s[:start] + f"{prefix}{inner}{suffix}"
    set_text(entry, new)
    return True

class CalcGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ICS4U Scientific Calculator")

        self.shift_held = False
        self._mouse_shift_active = False

        self.display = ttk.Entry(root, font=("SF Mono", 16))
        self.display.grid(row=0, column=0, columnspan=6, sticky="nsew", padx=8, pady=8)

        # Top controls
        self.shift_btn = ttk.Button(root, text="Shift")
        self.shift_btn.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4, pady=2)
        self.shift_btn.bind("<ButtonPress-1>", self._on_shift_mouse_down)
        self.shift_btn.bind("<ButtonRelease-1>", self._on_shift_mouse_up)
        root.bind_all("<ButtonRelease-1>", self._global_mouse_up, add="+")  # release outside

        ttk.Button(root, text="C", command=self.clear).grid(row=1, column=4, sticky="nsew", padx=4, pady=2)
        ttk.Button(root, text="⌫", command=self.backspace).grid(row=1, column=5, sticky="nsew", padx=4, pady=2)

        # (primary, alt, handler)
        self._buttons = []
        rows = [
            [("(", None, self.type_), (")", None, self.type_),
             ("π", "e", self.const_btn), ("log₁₀()", "logₓ()", self.log_btn),
             ("√", "³√", self.root_btn), ("!", "xʸ", self.fact_pow_btn)],
            [("7", None, self.type_), ("8", None, self.type_), ("9", None, self.type_),
             ("÷", None, self.type_), ("sin", "sin⁻¹", self.trig_btn), ("eqn", None, self.eqn_btn)],
            [("4", None, self.type_), ("5", None, self.type_), ("6", None, self.type_),
             ("×", None, self.type_), ("cos", "cos⁻¹", self.trig_btn), ("x²", "x³", self.square_cube_btn)],
            [("1", None, self.type_), ("2", None, self.type_), ("3", None, self.type_),
             ("-", None, self.type_), ("tan", "tan⁻¹", self.trig_btn), ("=", None, self.equals_btn)],
            [("0", None, self.type_), (".", None, self.type_), (",", None, self.type_),
             ("+", None, self.type_), ("/", None, self.type_), ("*", None, self.type_)],
        ]
        r0 = 2
        for r, row in enumerate(rows, start=r0):
            for c, (pri, alt, handler) in enumerate(row):
                self._add_button(r, c, pri, alt, handler)

        for i in range(6):
            root.grid_columnconfigure(i, weight=1)
        for i in range(8):
            root.grid_rowconfigure(i, weight=1)

        # Keyboard Shift
        root.bind_all("<KeyPress-Shift_L>", self._on_kb_shift_down)
        root.bind_all("<KeyPress-Shift_R>", self._on_kb_shift_down)
        root.bind_all("<KeyRelease-Shift_L>", self._on_kb_shift_up)
        root.bind_all("<KeyRelease-Shift_R>", self._on_kb_shift_up)

        self._refresh_labels()

    # Shift (hold)
    def _set_shift(self, held: bool):
        if self.shift_held != held:
            self.shift_held = held
            self.shift_btn.config(text=f"Shift{' (held)' if held else ''}")
            self._refresh_labels()

    def _on_shift_mouse_down(self, _):
        self._mouse_shift_active = True
        self._set_shift(True)

    def _on_shift_mouse_up(self, _):
        self._mouse_shift_active = False
        self._set_shift(False)

    def _global_mouse_up(self, _):
        if self._mouse_shift_active:
            self._mouse_shift_active = False
            self._set_shift(False)

    def _on_kb_shift_down(self, _):
        self._set_shift(True)

    def _on_kb_shift_up(self, _):
        self._set_shift(False)

    # UI helpers
    def _add_button(self, r, c, primary, alt, handler):
        var = tk.StringVar(value=primary or "")
        btn = ttk.Button(self.root, textvariable=var)
        btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        self._buttons.append((var, primary, alt, handler))
        btn.configure(command=lambda v=var, p=primary, a=alt, h=handler: h(v.get(), p, a))

    def _refresh_labels(self):
        for var, primary, alt, _ in self._buttons:
            var.set(alt if (self.shift_held and alt) else primary)

    def clear(self):
        set_text(self.display, "")

    def backspace(self):
        s = get_text(self.display)
        if s:
            set_text(self.display, s[:-1])

    # Handlers
    def type_(self, label, *_):
        if label == "×": label = "*"
        if label == "÷": label = "/"
        insert(self.display, label)

    def const_btn(self, *_):
        insert(self.display, "pi" if not self.shift_held else "e")

    def root_btn(self, *_):
        insert(self.display, "sqrt(" if not self.shift_held else "cbrt(")

    def square_cube_btn(self, *_):
        insert(self.display, "²" if not self.shift_held else "³")

    def fact_pow_btn(self, *_):
        if not self.shift_held:
            if not wrap_last_atom(self.display, "factorial("):
                insert(self.display, "factorial(")
        else:
            insert(self.display, "ʸ")

    def trig_btn(self, label, *_):
        insert(self.display, f"{label}(")

    def log_btn(self, *_):
        if not self.shift_held:
            insert(self.display, "log10(")
        else:
            try:
                val = simpledialog.askstring("logx()", "Value x:")
                base = simpledialog.askstring("logx()", "Base b:")
                if val is None or base is None:
                    return
                float(val); float(base)
                insert(self.display, f"log_b({val}, {base})")
            except Exception:
                messagebox.showerror("Error", "Enter valid numbers.")
# edit
    def equals_btn(self, *_):
        expr = get_text(self.display)
        expr = expr.replace("²", "**2").replace("³", "**3").replace("ʸ", "**")
        try:
            result = eval_safe(expr)
            set_text(self.display, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eqn_btn(self, *_):
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