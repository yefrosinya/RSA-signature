import shutil
from typing import Tuple, Optional


class FileManager:
    
    @staticmethod
    def read_file_bytes(filepath: str) -> bytes:
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {filepath}")
        except IOError as e:
            raise IOError(f"Ошибка чтения файла: {e}")
    
    @staticmethod
    def read_file_text(filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {filepath}")
        except IOError as e:
            raise IOError(f"Ошибка чтения файла: {e}")
    
    @staticmethod
    def save_signed_file(original_filepath: str, output_filepath: str, signature: int) -> None:
        try:
            shutil.copyfile(original_filepath, output_filepath)
            
            with open(output_filepath, 'a', encoding='utf-8') as file:
                file.write("\r\n\r\n\r\n\r\n")
                file.write(str(signature))
        except IOError as e:
            raise IOError(f"Ошибка сохранения файла: {e}")
    
    @staticmethod
    def parse_signed_file(filepath: str) -> Tuple[str, int]:
        try:
            with open(filepath, 'rb') as f:
                content_bytes = f.read()
        except IOError as e:
            raise IOError(f"Ошибка чтения файла: {e}")
        
        separator = b'\r\n\r\n\r\n\r\n'
        sep_pos = content_bytes.find(separator)
        
        if sep_pos == -1:
            for alt_sep in [b'\n\n', b'\r\r']:
                sep_pos = content_bytes.find(alt_sep)
                if sep_pos != -1:
                    separator = alt_sep
                    break
            else:
                debug_content = content_bytes.decode('utf-8', errors='replace')[:100]
                raise ValueError(
                    f"Не найден разделитель подписи. Начало файла: {debug_content}...\n"
                    f"Ожидаемый разделитель: '\\r\\n\\r\\n\\r\\n\\r\\n'"
                )
        
        original_data = content_bytes[:sep_pos].decode('utf-8')
        signature_part = content_bytes[sep_pos + len(separator):]
        
        try:
            signature_str = signature_part.decode('utf-8').strip()
            signature = int(signature_str)
        except (UnicodeDecodeError, ValueError) as e:
            raise ValueError(f"Некорректный формат подписи: {e}")
        
        return original_data, signature
    
    @staticmethod
    def format_file_content_for_display(content: bytes, max_bytes: int = 150) -> str:
        if len(content) > 10240:
            first_part = ' '.join(map(str, content[:max_bytes]))
            last_part = ' '.join(map(str, content[-max_bytes:]))
            return f"Файл слишком большой. Показаны первые и последние {max_bytes} байт:\n{first_part}\n...\n{last_part}"
        else:
            return ' '.join(map(str, content))
