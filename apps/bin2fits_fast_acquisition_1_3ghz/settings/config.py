from apps.bin2fits_fast_acquisition_1_3ghz.logging.error_tracker import ErrorTracker
from apps.bin2fits_fast_acquisition_1_3ghz.logging.logger_configurator import LoggerConfigurator
from apps.bin2fits_fast_acquisition_1_3ghz.settings.settings_loader import SettingsLoader
from ratan_600_data_analyzer.common.project_info import ProjectInfo

project_root = ProjectInfo.find_project_root()
CONFIG_FILE = project_root / "configs/bin2fits_fast_acq_1_3ghz_config.toml"

# set application configuration
loader = SettingsLoader(CONFIG_FILE)
app_settings = loader.load()

# set logger configuration
_logger_configurator = LoggerConfigurator(app_settings.logging)
_logger_configurator.configure()

# set fail files tracker
error_tracker = ErrorTracker(app_settings)

# set parsers
# parser = argparse.ArgumentParser(description="Инструмент для обработки .bin файлов в .fits.")
# subparsers = parser.add_subparsers(dest="command", required=True, help="Доступные команды")
#
# # Команда "watch"
# subparsers.add_parser("watch", help="Запустить в режиме отслеживания новых файлов.")
#
# # Команда "run"
# parser_run = subparsers.add_parser("run", help="Обработать файлы в директории.")
# parser_run.add_argument("--directory", type=str, default=config.get("paths.bin_archive"),
#                         help="Директория для сканирования.")
# parser_run.add_argument("--force", action="store_true", help="Перезаписать существующие FITS файлы.")
# parser_run.add_argument("--ignore-errors", action="store_true", help="Обрабатывать файлы из списка ошибок.")
#
# # Команда "process-file"
# parser_process = subparsers.add_parser("process-file", help="Обработать один конкретный файл.")
# parser_process.add_argument("filepath", type=str, help="Путь к .bin файлу.")
# parser_process.add_argument("--force", action="store_true", help="Перезаписать существующий FITS файл.")
# parser_process.add_argument("--ignore-errors", action="store_true",
#                             help="Обрабатывать файл, даже если он в списке ошибок.")
#
# args = parser.parse_args()

