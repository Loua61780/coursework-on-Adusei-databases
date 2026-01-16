import shutil
import os
from datetime import datetime
from pathlib import Path
import zipfile
import schedule
import time
import threading

class BackupManager:
    """Менеджер резервного копирования базы данных"""
    
    def __init__(self, db_path='medical_clinic.db'):
        self.db_path = Path(db_path)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.remote_backup_dir = None
        self.is_scheduled = False
    
    def create_backup(self, backup_type='local'):
        """Создание резервной копии базы данных"""
        try:
            if not self.db_path.exists():
                return False, f"Файл базы данных не найден: {self.db_path}"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if backup_type == 'local':
                # Локальная копия
                backup_filename = f"backup_{timestamp}.db"
                backup_path = self.backup_dir / backup_filename
                
                shutil.copy2(self.db_path, backup_path)
                
                # Архивирование для экономии места
                zip_filename = f"backup_{timestamp}.zip"
                zip_path = self.backup_dir / zip_filename
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(backup_path, arcname=backup_filename)
                
                # Удаление нефайла после архивирования
                os.remove(backup_path)
                
                # Удаление старых резервных копий (старше 7 дней)
                self._clean_old_backups(days=7)
                
                return True, f"Локальная резервная копия создана: {zip_path}"
            
            elif backup_type == 'remote':
                # Имитация копирования на удаленный сервер
                if not self.remote_backup_dir:
                    return False, "Не указана удаленная директория для резервного копирования"
                
                remote_backup_path = self.remote_backup_dir / f"backup_{timestamp}.db"
                
                # В реальном приложении здесь было бы копирование по сети
                # Например, через FTP, SCP или облачное API
                print(f"[Имитация] Копирование {self.db_path} -> {remote_backup_path}")
                
                return True, f"Резервная копия отправлена на удаленный сервер: {remote_backup_path}"
            
            elif backup_type == 'cloud':
                # Имитация копирования в облачное хранилище
                # В реальном приложении здесь было бы использование cloud storage API
                print(f"[Имитация] Загрузка {self.db_path} в облачное хранилище")
                
                return True, f"Резервная копия загружена в облачное хранилище"
            
            else:
                return False, f"Неизвестный тип резервного копирования: {backup_type}"
        
        except Exception as e:
            return False, f"Ошибка создания резервной копии: {str(e)}"
    
    def _clean_old_backups(self, days=7):
        """Удаление старых резервных копий"""
        try:
            cutoff_time = time.time() - (days * 86400)  # дней в секундах
            
            for backup_file in self.backup_dir.glob("*.zip"):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    print(f"Удалена старая резервная копия: {backup_file}")
        except Exception as e:
            print(f"Ошибка при удалении старых резервных копий: {e}")
    
    def list_backups(self):
        """Список доступных резервных копий"""
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("*.zip"), key=os.path.getmtime, reverse=True):
            file_stat = backup_file.stat()
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size_mb': file_stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(file_stat.st_mtime).strftime("%d.%m.%Y %H:%M:%S")
            })
        
        return backups
    
    def restore_backup(self, backup_filename):
        """Восстановление из резервной копии"""
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                return False, f"Резервная копия не найдена: {backup_filename}"
            
            # Создание резервной копии текущей базы данных перед восстановлением
            current_backup_name = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            current_backup_path = self.backup_dir / current_backup_name
            shutil.copy2(self.db_path, current_backup_path)
            
            # Распаковка резервной копии
            temp_backup_path = self.backup_dir / "temp_restore.db"
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Получаем имя файла внутри архива
                zip_files = zipf.namelist()
                if not zip_files:
                    return False, "Архив пустой"
                
                # Извлекаем первый файл
                zipf.extract(zip_files[0], path=self.backup_dir)
                extracted_file = self.backup_dir / zip_files[0]
                
                # Копируем извлеченный файл как основную базу данных
                shutil.copy2(extracted_file, self.db_path)
                
                # Удаляем временный файл
                os.remove(extracted_file)
            
            return True, f"База данных восстановлена из {backup_filename}"
        
        except Exception as e:
            return False, f"Ошибка восстановления: {str(e)}"
    
    def schedule_backup(self, interval_hours=24, backup_type='local'):
        """Планирование автоматического резервного копирования"""
        def backup_job():
            success, message = self.create_backup(backup_type)
            print(f"[Планировщик] {message}")
        
        # Ежедневное резервное копирование
        schedule.every(interval_hours).hours.do(backup_job)
        
        # Запуск планировщика в отдельном потоке
        def run_scheduler():
            while self.is_scheduled:
                schedule.run_pending()
                time.sleep(60)  # Проверка каждую минуту
        
        self.is_scheduled = True
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        return True, f"Автоматическое резервное копирование запущено каждые {interval_hours} часов"
    
    def stop_scheduled_backup(self):
        """Остановка планировщика резервного копирования"""
        self.is_scheduled = False
        return True, "Автоматическое резервное копирование остановлено"