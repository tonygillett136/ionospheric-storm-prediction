"""
Database models for Alert System
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    """User model for alert recipients"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class Alert(Base):
    """Alert configuration model"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    alert_type = Column(String(50), nullable=False)  # 'threshold', 'regional', 'impact'

    # Threshold settings
    threshold_probability = Column(Float, nullable=True)
    threshold_horizon = Column(String(10), nullable=True)  # '24h', '48h'

    # Regional settings
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    location_name = Column(String(255), nullable=True)

    # Notification settings
    notification_methods = Column(String(255), nullable=False)  # JSON string: ['email', 'webhook']
    webhook_url = Column(String(500), nullable=True)

    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")


class AlertHistory(Base):
    """Alert trigger history"""
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Prediction data at trigger time
    probability_24h = Column(Float, nullable=False)
    probability_48h = Column(Float, nullable=True)
    risk_level_24h = Column(String(50), nullable=False)

    # Notification status
    notification_sent = Column(Boolean, default=False, nullable=False)
    notification_error = Column(String(500), nullable=True)

    # Relationships
    alert = relationship("Alert", back_populates="history")
