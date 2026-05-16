class String:
    @staticmethod
    def generate_name(prefix: str, count: int) -> str:
        return f'{prefix} {count + 1}'
