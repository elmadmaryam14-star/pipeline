import gzip
import logging
import os

logger = logging.getLogger(__name__)


def ingest(path: str) -> list[str]:
    """Read auth log files in a directory and return all their lines."""
    rows = []

    try:
        filenames = sorted(os.listdir(path))
    except OSError:
        logger.exception("Could not list log directory: %s", path)
        raise

    auth_files = []

    for filename in filenames:
        is_auth_log = filename == "auth" or filename.startswith("auth.log")

        if not is_auth_log:
            continue

        file_path = os.path.join(path, filename)

        if os.path.isfile(file_path):
            auth_files.append(file_path)

    if not auth_files:
        logger.warning("No auth log files found in %s", path)
        return rows

    for file_path in auth_files:
        try:
            if file_path.endswith(".gz"):
                opener = gzip.open
            else:
                opener = open

            with opener(
                file_path,
                mode="rt",
                encoding="utf-8",
                errors="replace",
            ) as log_file:
                file_rows = log_file.readlines()
                rows.extend(file_rows)

            logger.info("Read %d lines from %s", len(file_rows), file_path)

        except (OSError, EOFError):
            logger.exception("Could not read log file: %s", file_path)

    logger.info("Read %d total lines from auth logs", len(rows))
    return rows