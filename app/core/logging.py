"""Logging partilhado: uma configuração, um formato, todo o projeto."""

import logging
import sys

_configured = False


def get_logger(name: str = "app") -> logging.Logger:
    """Devolve um logger com saída estruturada para stdout (formato amigável a agregadores)."""
    global _configured
    logger = logging.getLogger(name)
    if not _configured:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        _configured = True
    return logger
