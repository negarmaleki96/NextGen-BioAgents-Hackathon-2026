from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    fda_510k_db_path: Path = PROJECT_ROOT / "storage" / "sqlite" / "510k.db"
    fda_510k_json_path: Path = PROJECT_ROOT / "device-510k-0001-of-0001.json"
    upload_dir: Path = PROJECT_ROOT / "storage" / "uploads"
    output_dir: Path = PROJECT_ROOT / "storage" / "outputs"
    data_dir: Path = PROJECT_ROOT / "data"

    enable_ocr: bool = False
    max_chunks_per_pass: int = 12
    predicate_top_k: int = 5

    draft_watermark: str = "DRAFT — REQUIRES REGULATORY REVIEW"


settings = Settings()
