"""
Конфигурация для парсера расписания.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


def load_env_file(path: Path) -> None:
    with path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"\''))


@dataclass
class Config:
    """Конфигурация приложения."""
    
    # База данных
    database_url: str
    
    # HTTP клиент
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_exponential_base: float = 2.0
    
    # Парсинг
    max_concurrent_parses: int = 5
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Логирование
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Создать конфигурацию из переменных окружения."""
        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            load_env_file(env_path)

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        return cls(
            database_url=database_url,
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("RETRY_DELAY", "1.0")),
            retry_exponential_base=float(os.getenv("RETRY_EXPONENTIAL_BASE", "2.0")),
            max_concurrent_parses=int(os.getenv("MAX_CONCURRENT_PARSES", "5")),
            user_agent=os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# Глобальный экземпляр конфигурации
config: Optional[Config] = None


def get_config() -> Config:
    """Получить глобальную конфигурацию."""
    global config
    if config is None:
        config = Config.from_env()
    return config
