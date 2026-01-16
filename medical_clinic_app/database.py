from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self, db_path='medical_clinic.db'):
        self.db_path = db_path
        self.engine = None
        self.Session = None
        
    def init_database(self):
        """Инициализация базы данных"""
        # Создаем подключение к SQLite
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        
        # Создаем таблицы
        Base.metadata.create_all(self.engine)
        
        # Создаем фабрику сессий
        self.Session = sessionmaker(bind=self.engine)
        
        print(f"База данных инициализирована: {self.db_path}")
        return self.Session
    
    def get_session(self):
        """Получение сессии базы данных"""
        if self.Session is None:
            self.init_database()
        return self.Session()
    
    def close_session(self, session):
        """Закрытие сессии"""
        if session:
            session.close()
    
    def database_exists(self):
        """Проверка существования базы данных"""
        return os.path.exists(self.db_path)