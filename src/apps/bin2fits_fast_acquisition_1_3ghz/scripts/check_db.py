import logging

from sqlalchemy import create_engine, inspect, text, select
from sqlalchemy.orm import sessionmaker

from apps.bin2fits_fast_acquisition_1_3ghz.infrastructure.database import FastAcquisition1To3GHzRaw, ProcessingStatus

logger = logging.getLogger(__name__)

def _get_session(db_url: str):
    """Вспомогательная функция для создания сессии БД"""
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    return session_factory()

# def check_db(app_settings):
#     db_url = app_settings.database_settings.db_url
#
#     logger.debug(f"Connection: {app_settings.database_settings.host}:{app_settings.database_settings.port}")
#
#     try:
#         engine = create_engine(db_url)
#
#         inspector = inspect(engine)
#         tables = inspector.get_table_names()
#         logger.debug(f"Found tables: {tables}")
#
#         target_table = "fast_acquisition_1_3ghz_raw"
#         if target_table in tables:
#             with engine.connect() as connection:
#                 query = text(f"SELECT * FROM {target_table} LIMIT 3;")
#                 result = connection.execute(query)
#                 rows = result.fetchall()
#                 if not rows:
#                     logger.debug(f"Table '{target_table}' is empty")
#                 else:
#                     logger.debug(f"Content '{target_table}':")
#                     for row in rows:
#                         logger.debug(f"   {row}")
#     except Exception as e:
#         logger.debug(f"Error: {e}")

def check_database(app_settings):

    db_url = app_settings.database_settings.db_url
    target_table = "fast_acquisition_1_3ghz_raw"

    logger.debug(f"Connection to: {app_settings.database_settings.host}")

    try:
        engine = create_engine(db_url)

        with engine.connect() as connection:
            check_query = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :t_name);")
            table_exists = connection.execute(check_query, {"t_name": target_table}).scalar()

            if not table_exists:
                logger.warning(f"Table '{target_table}' not exists")
                return

            # Общая статистика по статусам
            stats_query = text(f"""
                SELECT status, COUNT(*) 
                FROM {target_table} 
                GROUP BY status;
            """)

            logger.debug(f"--- Table '{target_table}' statistics ---")
            total = 0
            for row in connection.execute(stats_query):
                logger.debug(f"  {row[0]}: {row[1]}")
                total += row[1]
            logger.debug(f"  Total entries: {total}")

    except Exception as e:
        logger.error(f"Error: {e}")


def show_processing_files(app_settings):
    """
    Показывает все файлы со статусом PROCESSING (Активные или зависшие).
    """
    session = _get_session(app_settings.database_settings.db_url)
    try:
        stmt = select(FastAcquisition1To3GHzRaw).where(
            FastAcquisition1To3GHzRaw.status == ProcessingStatus.PROCESSING
        ).order_by(FastAcquisition1To3GHzRaw.updated_at.asc())  # Сортируем от старых к новым

        records = session.scalars(stmt).all()

        if not records:
            logger.debug("No entries with PROCESSING status")
            return

        logger.debug(f"Found {len(records)} entries with PROCESSING status")
        for r in records:
            # Выводим время обновления, чтобы было видно, не завис ли файл
            time_str = r.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            logger.debug(f"  [Updated: {time_str}] {r.bin_filename}")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        session.close()


def show_failed_files(app_settings, limit: int = 10):
    """
    Показывает последние N файлов со статусом FAILED и текстом ошибки.
    """
    session = _get_session(app_settings.database_settings.db_url)
    try:
        stmt = select(FastAcquisition1To3GHzRaw).where(
            FastAcquisition1To3GHzRaw.status == ProcessingStatus.FAILED
        ).order_by(FastAcquisition1To3GHzRaw.updated_at.desc())#.limit(limit)  # Берем самые свежие ошибки

        records = session.scalars(stmt).all()

        if not records:
            logger.debug("No entries with FAILED status")
            return

        logger.debug(f"Found {len(records)} entries with FAILED status")
        # for r in records:
        #     time_str = r.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        #     # Показываем только первые 100 символов ошибки, чтобы не засорять консоль
        #     short_error = r.comment[:200] + "..." if r.comment and len(r.comment) > 100 else r.comment
        #
        #     logger.debug(f"  [{time_str}] {r.bin_filename}")
        #     logger.debug(f"     Error: {short_error}")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        session.close()