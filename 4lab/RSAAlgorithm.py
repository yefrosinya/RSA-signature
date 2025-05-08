import random
import math

def isPrime(p): # Миллера-Рабина
    rounds = 5 # количество проверок с разными a
    # p - 1 = 2^r * d
    # d  нечетное, r - максимально возможная степень 2
    d = p - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for j in range(rounds):
        a = random.randint(2, p - 2)
        x = pow(a, d, p)
        # print(j, ") a= ", a, " x = ", x)
        if x == 1 or x == p - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, p)
            if x == p - 1:
                break
        else:
            return False
    return True

def greatestCommonDivisor(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def findPrimeDividers(p):
    dividers = []
    while p % 2 == 0:
        dividers.append(2)
        p //= 2
    for i in range(3, int(math.sqrt(p)) + 1, 2):
        while p % i == 0:
            dividers.append(i)
            p //= i
    if p > 2:
        dividers.append(p)
    return dividers

def fastPow(base, exponent, modulus):
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    return result

def modinv(a, m):
    def extended_gcd(a, b):
        if b == 0:
            return a, 1, 0
        g, x1, y1 = extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return g, x, y
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Обратного элемента не существует")
    return x % m

def getHash(h, m, n):
    return pow(h + m, 2, n)