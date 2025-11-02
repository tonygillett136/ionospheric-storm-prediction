"""
Alert Service

Manages user alerts for ionospheric storm predictions.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models_alerts import User, Alert, AlertHistory

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing ionospheric storm alerts."""

    async def create_or_get_user(self, db: AsyncSession, email: str, name: Optional[str] = None) -> User:
        """Create or get existing user by email."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            user = User(email=email, name=name)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created new user: {email}")

        return user

    async def create_alert(
        self,
        db: AsyncSession,
        user_email: str,
        name: str,
        alert_type: str,
        threshold_probability: Optional[float] = None,
        threshold_horizon: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
        location_name: Optional[str] = None,
        notification_methods: str = '["email"]',
        webhook_url: Optional[str] = None
    ) -> Alert:
        """Create a new alert."""
        # Get or create user
        user = await self.create_or_get_user(db, user_email)

        # Create alert
        alert = Alert(
            user_id=user.id,
            name=name,
            alert_type=alert_type,
            threshold_probability=threshold_probability,
            threshold_horizon=threshold_horizon,
            location_lat=location_lat,
            location_lon=location_lon,
            location_name=location_name,
            notification_methods=notification_methods,
            webhook_url=webhook_url,
            enabled=True
        )

        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        logger.info(f"Created alert '{name}' for user {user_email}")
        return alert

    async def get_user_alerts(self, db: AsyncSession, user_email: str) -> List[Alert]:
        """Get all alerts for a user."""
        result = await db.execute(
            select(Alert)
            .join(User)
            .where(User.email == user_email)
            .order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_alert(self, db: AsyncSession, alert_id: int, user_email: str) -> bool:
        """Delete an alert (only if it belongs to the user)."""
        result = await db.execute(
            select(Alert)
            .join(User)
            .where(and_(Alert.id == alert_id, User.email == user_email))
        )
        alert = result.scalar_one_or_none()

        if not alert:
            return False

        await db.delete(alert)
        await db.commit()

        logger.info(f"Deleted alert {alert_id} for user {user_email}")
        return True

    async def check_alerts(
        self,
        db: AsyncSession,
        current_prediction: Dict
    ) -> List[Dict]:
        """
        Check all active alerts against current prediction.

        Returns list of triggered alerts (MVP: just checks thresholds, doesn't send notifications yet).
        """
        # Get all enabled alerts
        result = await db.execute(
            select(Alert).where(Alert.enabled == True)
        )
        alerts = list(result.scalars().all())

        triggered_alerts = []

        for alert in alerts:
            triggered = False
            trigger_reason = None

            if alert.alert_type == 'threshold':
                # Check if threshold exceeded
                prob_key = f'storm_probability_{alert.threshold_horizon}' if alert.threshold_horizon else 'storm_probability_24h'
                current_prob = current_prediction.get(prob_key, 0) * 100  # Convert to percentage

                if current_prob >= alert.threshold_probability:
                    triggered = True
                    trigger_reason = f"Storm probability ({current_prob:.1f}%) exceeded threshold ({alert.threshold_probability}%)"

            if triggered:
                triggered_alerts.append({
                    'alert_id': alert.id,
                    'alert_name': alert.name,
                    'user_id': alert.user_id,
                    'trigger_reason': trigger_reason,
                    'current_probability': current_prob if alert.alert_type == 'threshold' else None
                })

                # Log to alert history
                history = AlertHistory(
                    alert_id=alert.id,
                    triggered_at=datetime.utcnow(),
                    probability_24h=current_prediction.get('storm_probability_24h', 0) * 100,
                    probability_48h=current_prediction.get('storm_probability_48h', 0) * 100,
                    risk_level_24h=current_prediction.get('risk_level_24h', 'unknown'),
                    notification_sent=False,  # MVP: not actually sending yet
                    notification_error=None
                )
                db.add(history)

        if triggered_alerts:
            await db.commit()
            logger.info(f"Triggered {len(triggered_alerts)} alerts")

        return triggered_alerts

    async def get_alert_history(
        self,
        db: AsyncSession,
        user_email: str,
        limit: int = 50
    ) -> List[AlertHistory]:
        """Get alert history for a user."""
        result = await db.execute(
            select(AlertHistory)
            .join(Alert)
            .join(User)
            .where(User.email == user_email)
            .order_by(AlertHistory.triggered_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
