"""
数据库模型定义
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import config

Base = declarative_base()

# 创建数据库引擎
engine = create_engine(f'sqlite:///{config.DATABASE_PATH}', echo=False)
Session = sessionmaker(bind=engine)


class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    role = Column(String(20), default='user')  # user, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime, nullable=True)
    
    # 关联权限
    permissions = relationship('Permission', back_populates='user', cascade='all, delete-orphan', foreign_keys='Permission.user_id', lazy='joined')
    # 关联操作日志
    audit_logs = relationship('AuditLog', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }


class Permission(Base):
    """权限表 - 用户与目录的权限关系"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    directory_path = Column(String(500), nullable=False, index=True)
    directory_name = Column(String(100), nullable=False)  # 目录显示名称
    permission_level = Column(String(10), nullable=False)  # read, write
    granted_at = Column(DateTime, default=datetime.now)
    granted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # 关联用户
    user = relationship('User', back_populates='permissions', foreign_keys='Permission.user_id')
    
    def __repr__(self):
        return f'<Permission user_id={self.user_id} path={self.directory_path}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'directory_path': self.directory_path,
            'directory_name': self.directory_name,
            'permission_level': self.permission_level,
            'granted_at': self.granted_at.strftime('%Y-%m-%d %H:%M:%S') if self.granted_at else None
        }


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    username = Column(String(50), nullable=True)  # 冗余存储，防止用户删除后无法追溯
    action = Column(String(50), nullable=False, index=True)  # login, upload, download, delete, etc.
    target_path = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), default='success')  # success, failed
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    # 关联用户
    user = relationship('User', back_populates='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'target_path': self.target_path,
            'ip_address': self.ip_address,
            'status': self.status,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'details': self.details
        }


class RegisteredPath(Base):
    """已注册路径表 - 管理员预注册的路径"""
    __tablename__ = 'registered_paths'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(500), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)  # 显示名称
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<RegisteredPath {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'path': self.path,
            'name': self.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(engine)
    return Session()


def get_session():
    """获取数据库会话"""
    return Session()


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    print('数据库初始化完成！')
