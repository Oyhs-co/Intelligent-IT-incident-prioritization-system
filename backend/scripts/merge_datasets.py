"""
Script para fusionar datasets de tickets IT (migrado desde IA-module).

Combina dos datasets CSV en uno solo, normalizando prioridades y limpiando datos.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.ml._utils import Config, logger


def main() -> int:
    logger.info("=" * 60)
    logger.info("FUSIÓN DE DATASETS DE TICKETS IT")
    logger.info("=" * 60)

    Config.ensure_dirs()
    data_dir = Config.DATA_DIR

    files = {
        "Dataset 1 (multilang)": data_dir / "aa_dataset-tickets-multi-lang-5-2-50-version.csv",
        "Dataset 2 (IT Support)": data_dir / "IT Support Ticket Data.csv",
    }

    for name, path in files.items():
        if not path.exists():
            logger.error(f"Dataset no encontrado: {name} en {path}")
            return 1
        logger.info(f"✓ {name}: {path}")

    df1 = pd.read_csv(files["Dataset 1 (multilang)"])
    logger.info(f"\nDataset 1 (multilang): {df1.shape[0]} filas")

    text_col = None
    for col in ["text_body", "text", "description", "body", "Body", "ticket_body"]:
        if col in df1.columns:
            text_col = col
            break

    priority_col = None
    for col in ["priority", "Priority", "ticket_priority", "severity", "Severity"]:
        if col in df1.columns:
            priority_col = col
            break

    if text_col is None or priority_col is None:
        logger.error(f"No se encontraron columnas requeridas en Dataset 1. Columnas: {df1.columns.tolist()}")
        return 1

    df1a = df1[df1["language"] == "en"] if "language" in df1.columns else df1
    logger.info(f"  Filas en inglés: {df1a.shape[0]}")

    df1_clean = pd.DataFrame()
    df1_clean["text"] = df1a[text_col].astype(str)
    priority_map_1 = {"high": 1, "medium": 2, "low": 3, "critical": 1}
    df1_clean["priority"] = df1a[priority_col].astype(str).str.lower().map(priority_map_1)
    df1_clean = df1_clean.dropna(subset=["priority"])
    df1_clean["priority"] = df1_clean["priority"].astype(int)
    df1_clean["source"] = "multilang"
    df1_clean["department"] = df1a.get("department", "")
    df1_clean["type"] = df1a.get("type", "")
    tags_col_1 = None
    for col in ["tags", "Tags", "tag", "categories"]:
        if col in df1a.columns:
            tags_col_1 = col
            break
    df1_clean["tags"] = df1a.get(tags_col_1, "").astype(str) if tags_col_1 else ""

    df2 = pd.read_csv(files["Dataset 2 (IT Support)"])
    logger.info(f"Dataset 2 (IT Support): {df2.shape[0]} filas")

    df2_clean = pd.DataFrame()

    text_col_2 = None
    for col in ["Body", "body", "text", "description"]:
        if col in df2.columns:
            text_col_2 = col
            break

    if text_col_2 is None:
        logger.error(f"No se encontró columna de texto en Dataset 2. Columnas: {df2.columns.tolist()}")
        return 1

    df2_clean["text"] = df2[text_col_2].astype(str)

    priority_col_2 = None
    for col in ["Priority", "priority"]:
        if col in df2.columns:
            priority_col_2 = col
            break

    if priority_col_2:
        priority_map_2 = {"high": 1, "medium": 2, "low": 3, "critical": 1}
        df2_clean["priority"] = df2[priority_col_2].astype(str).str.lower().map(priority_map_2)
    df2_clean = df2_clean.dropna(subset=["priority"])
    df2_clean["priority"] = df2_clean["priority"].astype(int)

    df2_clean["source"] = "it_support"
    df2_clean["department"] = df2.get("Department", "")
    df2_clean["type"] = df2.get("Type", "")
    tags_col_2 = None
    for col in ["Tags", "tags"]:
        if col in df2.columns:
            tags_col_2 = col
            break
    df2_clean["tags"] = df2.get(tags_col_2, "").astype(str) if tags_col_2 else ""

    merged = pd.concat([df1_clean, df2_clean], ignore_index=True)
    merged = merged.drop_duplicates(subset=["text"], keep="first")

    merged = merged[merged["text"].notna() & (merged["text"].str.strip() != "")]
    merged = merged[merged["priority"].isin([1, 2, 3])]

    output_path = Config.get_data_path("it_tickets_merged.csv")
    merged.to_csv(output_path, index=False)

    logger.info(f"\n{'=' * 60}")
    logger.info("RESUMEN DE FUSIÓN")
    logger.info(f"{'=' * 60}")
    logger.info(f"  Total combinado: {len(merged)} tickets")
    logger.info(f"  Fuentes: {merged['source'].value_counts().to_dict()}")
    logger.info("  Distribución prioridades:")
    for p, count in sorted(merged["priority"].value_counts().items()):
        logger.info(f"    P{p}: {count}")
    logger.info(f"  Guardado en: {output_path}")
    logger.info(f"{'=' * 60}")



if __name__ == "__main__":
    sys.exit(main())
