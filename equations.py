"""
equations.py — 이차/삼차 방정식 해 (복소수 포함)
"""
import cmath

def solve_quadratic(a, b, c):
    """ax^2 + bx + c = 0"""
    if a == 0:
        raise ValueError("quadratic에서 a는 0이 될 수 없습니다.")
    d = b*b - 4*a*c
    s = cmath.sqrt(d)
    return ((-b + s)/(2*a), (-b - s)/(2*a))

def solve_cubic(a, b, c, d):
    """ax^3 + bx^2 + cx + d = 0 (Cardano, 복소 안전)"""
    if a == 0:
        raise ValueError("cubic에서 a는 0이 될 수 없습니다.")
    # 우 depressed cubic: t^3 + p t + q = 0,  x = t - b/(3a)
    p = (3*a*c - b*b) / (3*a*a)
    q = (2*b*b*b - 9*a*b*c + 27*a*a*d) / (27*a*a*a)
    shift = -b / (3*a)

    disc = (q/2)**2 + (p/3)**3  # 판별식
    u_c = -q/2 + cmath.sqrt(disc)
    v_c = -q/2 - cmath.sqrt(disc)
    u = u_c ** (1/3) if u_c != 0 else 0
    v = v_c ** (1/3) if v_c != 0 else 0

    # 세 근
    t1 = u + v
    omega = complex(-0.5, 3**0.5/2)  # 원시 3제곱근
    t2 = u*omega + v*omega.conjugate()
    t3 = u*omega.conjugate() + v*omega

    return (t1 + shift, t2 + shift, t3 + shift)