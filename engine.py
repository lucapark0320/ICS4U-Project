import math

def factorial(n: int) -> int:
    if n < 0 or int(n) != n:
        raise ValueError("factorial is only defined for non-negative integers.")
    return math.factorial(int(n))

def square(x: float) -> float:
    """x^2"""
    return x * x

def cube(x: float) -> float:
    """x^3"""
    return x * x * x

def power(x: float, y: float) -> float:
    """x^y"""
    return x ** y

def sqrt(x: float) -> float:
    """√x"""
    return math.sqrt(x)

def cbrt(x: float) -> float:
    """³√x (부호 보존)"""
    return math.copysign(abs(x) ** (1/3), x)


def _deg2rad(x: float) -> float: return math.radians(x)
def _rad2deg(x: float) -> float: return math.degrees(x)


def _deg2rad(x: float) -> float: return math.radians(x)
def _rad2deg(x: float) -> float: return math.degrees(x)



def sin(x: float) -> float: return math.sin(_deg2rad(x))
def cos(x: float) -> float: return math.cos(_deg2rad(x))
def tan(x: float) -> float: return math.tan(_deg2rad(x))

def asin(x: float) -> float: return _rad2deg(math.asin(x))
def acos(x: float) -> float: return _rad2deg(math.acos(x))
def atan(x: float) -> float: return _rad2deg(math.atan(x))


def log10(x: float) -> float:
    """log10(x)"""
    return math.log10(x)

def log_b(x: float, b: float) -> float:
    """밑 b의 로그: log_b(x)"""
    return math.log(x, b)


PI = math.pi
E  = math.e

pi = PI
e = E

