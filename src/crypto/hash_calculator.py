from typing import List


class HashCalculator:
    
    def __init__(self, n: int):
        self.n = n
        self.initial_h = 100
    
    def calculate_hash(self, message: bytes) -> tuple[int, List[int]]:
        h = self.initial_h
        hash_sequence = []
        
        for byte in message:
            result = pow(h + byte, 2, self.n)
            h = result
            hash_sequence.append(result)
            
        return h, hash_sequence
    
    def calculate_hash_from_string(self, message: str) -> tuple[int, List[int]]:
        return self.calculate_hash(message.encode('utf-8'))
