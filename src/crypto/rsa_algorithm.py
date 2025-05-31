from typing import Tuple
from src.utils.math_utils import MathUtils


class RSAAlgorithm:
    
    def __init__(self, p: int, q: int):
        if not MathUtils.is_prime(p) or not MathUtils.is_prime(q):
            raise ValueError("p и q должны быть простыми числами")
            
        self.p = p
        self.q = q
        self.n = p * q
        self.phi_n = (p - 1) * (q - 1)
        self.e = None
        self.d = None
    
    def generate_key_pair(self, e: int) -> Tuple[int, int]:
        if e <= 1 or e >= self.phi_n:
            raise ValueError("e должно быть больше 1 и меньше φ(n)")
            
        if MathUtils.greatest_common_divisor(e, self.phi_n) != 1:
            raise ValueError("НОД(e, φ(n)) должен быть равен 1")
            
        self.e = e
        self.d = MathUtils.mod_inverse(e, self.phi_n)
        
        return self.e, self.d
    
    def encrypt(self, message: int) -> int:
        if self.e is None:
            raise ValueError("Сначала сгенерируйте ключи")
            
        return MathUtils.fast_pow(message, self.e, self.n)
    
    def decrypt(self, encrypted_message: int) -> int:
        if self.d is None:
            raise ValueError("Сначала сгенерируйте ключи")
            
        return MathUtils.fast_pow(encrypted_message, self.d, self.n)
    
    def sign(self, message_hash: int) -> int:
        if self.d is None:
            raise ValueError("Сначала сгенерируйте ключи")
            
        return MathUtils.fast_pow(message_hash, self.d, self.n)
    
    def verify_signature(self, message_hash: int, signature: int) -> bool:
        if self.e is None:
            raise ValueError("Сначала сгенерируйте ключи")
            
        decrypted_hash = MathUtils.fast_pow(signature, self.e, self.n)
        return message_hash == decrypted_hash
    
    def get_public_key(self) -> Tuple[int, int]:
        if self.e is None:
            raise ValueError("Сначала сгенерируйте ключи")
            
        return self.n, self.e
    
    def get_private_key(self) -> Tuple[int, int]:
        if self.d is None:
            raise ValueError("Сначала сгенерируйте ключи")
            
        return self.n, self.d
