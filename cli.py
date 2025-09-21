"""
cli.py — 콘솔 계산기 (Phase 1)
사용 예:
  python cli.py eval "engine.sin(30)+engine.sqrt(9)+engine.PI"
  python cli.py quad 1 -3 2
  python cli.py cubic 1 0 -1 0
"""
import argparse
import engine
import equations

def main():
    p = argparse.ArgumentParser(description="ICS4U Scientific Calculator (Console)")
    sub = p.add_subparsers(dest="cmd")

    p_eval = sub.add_parser("eval", help="표현식 평가")
    p_eval.add_argument("expr", help="예: 'engine.sin(30)+engine.sqrt(9)+engine.PI'")

    p_quad = sub.add_parser("quad", help="ax^2+bx+c=0")
    for k in ("a","b","c"): p_quad.add_argument(k, type=float)

    p_cub = sub.add_parser("cubic", help="ax^3+bx^2+cx+d=0")
    for k in ("a","b","c","d"): p_cub.add_argument(k, type=float)

    args = p.parse_args()
    if args.cmd == "eval":
        # 안전을 위해 __builtins__ 제거, engine 네임스페이스만 허용
        val = eval(args.expr, {"__builtins__": {}}, vars(engine))
        print("=", val)
    elif args.cmd == "quad":
        print(equations.solve_quadratic(args.a, args.b, args.c))
    elif args.cmd == "cubic":
        print(equations.solve_cubic(args.a, args.b, args.c, args.d))
    else:
        p.print_help()

if __name__ == "__main__":
    main()