from sqlalchemy import create_engine, inspect, text

from ratan_600_data_analyzer.logging.logger_configurator import get_logger

logger = get_logger(__name__)

def check_db(app_settings):
    db_url = app_settings.database_settings.db_url

    logger.debug(f"Connection: {app_settings.database_settings.host}:{app_settings.database_settings.port}")

    try:
        engine = create_engine(db_url)

        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.debug(f"Found tables: {tables}")

        target_table = "fast_acquisition_1_3ghz_raw"
        if target_table in tables:
            with engine.connect() as connection:
                query = text(f"SELECT * FROM {target_table} LIMIT 3;")
                result = connection.execute(query)
                rows = result.fetchall()
                if not rows:
                    logger.debug(f"Table '{target_table}' is empty")
                else:
                    logger.debug(f"Content '{target_table}':")
                    for row in rows:
                        logger.debug(f"   {row}")
    except Exception as e:
        logger.debug(f"Error: {e}")