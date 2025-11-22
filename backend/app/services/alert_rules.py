"""Custom alert rules engine for station-specific and advanced alerting."""
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import Station, Forecast, AlertRule

logger = get_logger(__name__)


# Default global thresholds (fallback if no custom rules)
DEFAULT_THRESHOLDS = {
    "info": 800,
    "warning": 1200,
    "severe": 1600,
    "extreme": 2000,
}


class AlertRulesEngine:
    """Engine for evaluating custom alert rules."""

    async def evaluate_station_rules(
        self,
        station: Station,
        forecasts: List[Forecast],
        db: AsyncSession
    ) -> Optional[Tuple[str, float, str]]:
        """
        Evaluate all active rules for a station and determine alert level.
        
        Args:
            station: The station to evaluate
            forecasts: Recent forecasts for the station
            db: Database session
            
        Returns:
            Tuple of (alert_level, probability, reason) or None if no alert
        """
        if not forecasts:
            return None
        
        # Get active rules for this station
        result = await db.execute(
            select(AlertRule)
            .where(AlertRule.station_id == station.id)
            .where(AlertRule.is_active == True)  # noqa: E712
            .order_by(AlertRule.priority.desc())
        )
        rules = result.scalars().all()
        
        # If no custom rules, use default thresholds
        if not rules:
            return self._evaluate_default_thresholds(forecasts)
        
        # Evaluate each rule in priority order
        alerts = []
        for rule in rules:
            result = await self._evaluate_rule(rule, station, forecasts, db)
            if result:
                alerts.append(result)
        
        # Return highest severity alert
        if alerts:
            return self._select_highest_alert(alerts)
        
        return None

    def _evaluate_default_thresholds(
        self,
        forecasts: List[Forecast]
    ) -> Optional[Tuple[str, float, str]]:
        """Evaluate using default discharge thresholds."""
        max_forecast = max(forecasts, key=lambda f: f.discharge_m3s)
        max_discharge = max_forecast.discharge_m3s
        lead_hours = max_forecast.lead_hours
        
        # Determine alert level
        alert_level = None
        if max_discharge >= DEFAULT_THRESHOLDS["extreme"]:
            alert_level = "extreme"
        elif max_discharge >= DEFAULT_THRESHOLDS["severe"]:
            alert_level = "severe"
        elif max_discharge >= DEFAULT_THRESHOLDS["warning"]:
            alert_level = "warning"
        elif max_discharge >= DEFAULT_THRESHOLDS["info"]:
            alert_level = "info"
        
        if not alert_level:
            return None
        
        # Calculate probability based on lead time
        if lead_hours <= 24:
            probability = 0.85
        elif lead_hours <= 48:
            probability = 0.70
        else:
            probability = 0.55
        
        reason = f"Default threshold: {max_discharge:.1f} m³/s (lead: {lead_hours}h)"
        
        return (alert_level, probability, reason)

    async def _evaluate_rule(
        self,
        rule: AlertRule,
        station: Station,
        forecasts: List[Forecast],
        db: AsyncSession
    ) -> Optional[Tuple[str, float, str]]:
        """Evaluate a specific rule."""
        if rule.rule_type == "threshold":
            return self._evaluate_threshold_rule(rule, forecasts)
        elif rule.rule_type == "rate_of_rise":
            return self._evaluate_rate_of_rise_rule(rule, forecasts)
        elif rule.rule_type == "time_window":
            return self._evaluate_time_window_rule(rule, forecasts)
        elif rule.rule_type == "multi_station":
            return await self._evaluate_multi_station_rule(rule, station, forecasts, db)
        else:
            logger.warning(f"Unknown rule type: {rule.rule_type}")
            return None

    def _evaluate_threshold_rule(
        self,
        rule: AlertRule,
        forecasts: List[Forecast]
    ) -> Optional[Tuple[str, float, str]]:
        """
        Evaluate threshold rule.
        
        Config example:
        {
            "thresholds": {"info": 500, "warning": 800, "severe": 1200, "extreme": 1500},
            "lead_time_adjustments": {"24": 0.9, "48": 0.8, "72": 0.7}
        }
        """
        config = rule.config
        thresholds = config.get("thresholds", DEFAULT_THRESHOLDS)
        lead_time_adjustments = config.get("lead_time_adjustments", {})
        
        max_forecast = max(forecasts, key=lambda f: f.discharge_m3s)
        max_discharge = max_forecast.discharge_m3s
        lead_hours = max_forecast.lead_hours
        
        # Determine alert level
        alert_level = None
        if max_discharge >= thresholds.get("extreme", float('inf')):
            alert_level = "extreme"
        elif max_discharge >= thresholds.get("severe", float('inf')):
            alert_level = "severe"
        elif max_discharge >= thresholds.get("warning", float('inf')):
            alert_level = "warning"
        elif max_discharge >= thresholds.get("info", float('inf')):
            alert_level = "info"
        
        if not alert_level:
            return None
        
        # Calculate probability with lead time adjustment
        base_probability = 0.85 if lead_hours <= 24 else 0.70 if lead_hours <= 48 else 0.55
        
        # Apply lead time adjustment if configured
        adjustment_key = str(lead_hours)
        if adjustment_key in lead_time_adjustments:
            base_probability *= lead_time_adjustments[adjustment_key]
        
        reason = f"Custom threshold ({rule.name}): {max_discharge:.1f} m³/s (lead: {lead_hours}h)"
        
        return (alert_level, base_probability, reason)

    def _evaluate_rate_of_rise_rule(
        self,
        rule: AlertRule,
        forecasts: List[Forecast]
    ) -> Optional[Tuple[str, float, str]]:
        """
        Evaluate rate of rise rule.
        
        Config example:
        {
            "threshold_m3s_per_hour": 50,
            "min_hours": 6,
            "alert_level": "warning"
        }
        """
        config = rule.config
        threshold_rate = config.get("threshold_m3s_per_hour", 50)
        min_hours = config.get("min_hours", 6)
        alert_level = config.get("alert_level", "warning")
        
        if len(forecasts) < 2:
            return None
        
        # Sort by forecast time
        sorted_forecasts = sorted(forecasts, key=lambda f: f.ts)
        
        # Check rate of rise between consecutive forecasts
        for i in range(len(sorted_forecasts) - 1):
            f1 = sorted_forecasts[i]
            f2 = sorted_forecasts[i + 1]
            
            time_diff_hours = (f2.ts - f1.ts).total_seconds() / 3600
            
            if time_diff_hours < min_hours:
                continue
            
            discharge_diff = f2.discharge_m3s - f1.discharge_m3s
            rate_of_rise = discharge_diff / time_diff_hours
            
            if rate_of_rise >= threshold_rate:
                reason = (
                    f"Rapid rise detected ({rule.name}): "
                    f"{rate_of_rise:.1f} m³/s/h over {time_diff_hours:.1f}h"
                )
                return (alert_level, 0.80, reason)
        
        return None

    def _evaluate_time_window_rule(
        self,
        rule: AlertRule,
        forecasts: List[Forecast]
    ) -> Optional[Tuple[str, float, str]]:
        """
        Evaluate time window rule (e.g., nighttime hours are more critical).
        
        Config example:
        {
            "start_hour": 22,
            "end_hour": 6,
            "level_boost": 1,  # Upgrade alert level by 1 step
            "probability_boost": 0.1
        }
        """
        config = rule.config
        start_hour = config.get("start_hour", 22)
        end_hour = config.get("end_hour", 6)
        level_boost = config.get("level_boost", 1)
        probability_boost = config.get("probability_boost", 0.1)
        
        # Check if any forecast falls within the critical time window
        now = datetime.now(timezone.utc)
        current_hour = now.hour
        
        in_window = False
        if start_hour > end_hour:  # Window crosses midnight
            in_window = current_hour >= start_hour or current_hour < end_hour
        else:
            in_window = start_hour <= current_hour < end_hour
        
        if not in_window:
            return None
        
        # Get base alert from thresholds
        base_result = self._evaluate_default_thresholds(forecasts)
        if not base_result:
            return None
        
        base_level, base_prob, base_reason = base_result
        
        # Boost alert level
        level_order = ["info", "warning", "severe", "extreme"]
        base_index = level_order.index(base_level)
        boosted_index = min(base_index + level_boost, len(level_order) - 1)
        boosted_level = level_order[boosted_index]
        
        # Boost probability
        boosted_prob = min(base_prob + probability_boost, 1.0)
        
        reason = f"Time-sensitive period ({rule.name}): {base_reason}"
        
        return (boosted_level, boosted_prob, reason)

    async def _evaluate_multi_station_rule(
        self,
        rule: AlertRule,
        station: Station,
        forecasts: List[Forecast],
        db: AsyncSession
    ) -> Optional[Tuple[str, float, str]]:
        """
        Evaluate multi-station correlation rule.
        
        Config example:
        {
            "related_station_ids": [2, 3, 4],
            "min_stations_alerted": 2,
            "min_discharge": 1000,
            "alert_level": "severe"
        }
        """
        config = rule.config
        related_station_ids = config.get("related_station_ids", [])
        min_stations_alerted = config.get("min_stations_alerted", 2)
        min_discharge = config.get("min_discharge", 1000)
        alert_level = config.get("alert_level", "severe")
        
        if not related_station_ids:
            return None
        
        # Check if current station exceeds threshold
        max_forecast = max(forecasts, key=lambda f: f.discharge_m3s)
        if max_forecast.discharge_m3s < min_discharge:
            return None
        
        # Check related stations
        alerted_count = 1  # Current station
        
        for related_id in related_station_ids:
            # Get recent forecasts for related station
            result = await db.execute(
                select(Forecast)
                .where(Forecast.station_id == related_id)
                .where(Forecast.model_run >= max_forecast.model_run)
                .order_by(Forecast.discharge_m3s.desc())
                .limit(5)
            )
            related_forecasts = result.scalars().all()
            
            if related_forecasts:
                max_related = max(related_forecasts, key=lambda f: f.discharge_m3s)
                if max_related.discharge_m3s >= min_discharge:
                    alerted_count += 1
        
        if alerted_count >= min_stations_alerted:
            reason = (
                f"Multi-station correlation ({rule.name}): "
                f"{alerted_count} stations exceed {min_discharge} m³/s"
            )
            return (alert_level, 0.90, reason)
        
        return None

    def _select_highest_alert(
        self,
        alerts: List[Tuple[str, float, str]]
    ) -> Tuple[str, float, str]:
        """Select the highest severity alert from multiple rule results."""
        level_order = ["info", "warning", "severe", "extreme"]
        
        # Sort by level (descending) then probability (descending)
        sorted_alerts = sorted(
            alerts,
            key=lambda a: (level_order.index(a[0]), a[1]),
            reverse=True
        )
        
        return sorted_alerts[0]


# Global instance
alert_rules_engine = AlertRulesEngine()



