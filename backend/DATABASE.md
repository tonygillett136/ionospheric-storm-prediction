# Database Documentation

## Overview

The Ionospheric Storm Prediction System uses **SQLite** with **SQLAlchemy ORM** and **Alembic** for database migrations. The database stores 10 years of historical ionospheric and space weather measurements for trend analysis and research.

## Database Schema

### HistoricalMeasurement Table

Stores hourly measurements of ionospheric conditions and space weather parameters.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key |
| `timestamp` | DateTime | Measurement timestamp (indexed, unique) |
| `kp_index` | Float | Geomagnetic activity index (0-9 scale) |
| `dst_index` | Float | Disturbance Storm Time index (nT) |
| `solar_wind_speed` | Float | Solar wind velocity (km/s) |
| `solar_wind_density` | Float | Proton density (particles/cm³) |
| `solar_wind_temperature` | Float | Solar wind temperature (K) |
| `imf_bz` | Float | Interplanetary magnetic field Bz component (nT) |
| `f107_flux` | Float | Solar flux at 10.7 cm (sfu) |
| `tec_mean` | Float | Mean Total Electron Content (TECU) |
| `tec_std` | Float | TEC standard deviation (TECU) |
| `tec_max` | Float | Maximum TEC value (TECU) |
| `tec_min` | Float | Minimum TEC value (TECU) |
| `storm_probability` | Float | 24-hour storm probability (0-100) |
| `risk_level` | Integer | Risk classification (0-4) |
| `created_at` | DateTime | Record creation timestamp |

### Indexes

- `idx_timestamp_desc` - Descending timestamp for efficient latest queries
- `idx_timestamp_storm` - Composite index on timestamp and storm_probability
- `ix_historical_measurements_id` - Primary key index
- `ix_historical_measurements_timestamp` - Timestamp index for range queries

## Database Location

```
backend/data/ionospheric.db
```

The database file is automatically created when the application starts or when seeding data.

## Seeding Historical Data

### Running the Seeder

Generate 10 years (87,600 hours) of realistic historical data:

```bash
cd backend
source venv/bin/activate
python seed_historical_data.py
```

**Duration:** ~30 seconds
**Records Created:** 87,600 hourly measurements

### Data Characteristics

The seeder generates realistic synthetic data with:

1. **Solar Cycle Variations** (11-year cycle)
   - Modulates solar activity and F10.7 flux
   - Affects baseline TEC levels

2. **Seasonal Variations**
   - Higher activity near equinoxes (March, September)
   - Lower activity near solstices (June, December)

3. **Daily Variations**
   - Peak TEC around 14:00 local time
   - Minimum TEC during night hours

4. **Storm Events**
   - ~200 storm events over 10 years (~20 per year)
   - Duration: 6-72 hours each
   - Elevated Kp index, negative IMF Bz, enhanced TEC

5. **Parameter Correlations**
   - High Kp → negative Dst
   - Negative IMF Bz → increased storm probability
   - Fast solar wind → higher storm risk
   - Solar cycle phase → baseline activity level

### Data Time Range

By default, data spans from **10 years ago to present**:
- Start: Current date - 10 years
- End: Current date
- Interval: 1 hour

## Database Migrations

The project uses **Alembic** for database schema version control.

### Initialize Migrations (Already Done)

```bash
alembic init alembic
```

### Create a Migration

After modifying models in `app/db/models.py`:

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Querying the Database

### Using the Repository

```python
from app.db.database import AsyncSessionLocal
from app.db.repository import HistoricalDataRepository
from datetime import datetime, timedelta

async def example():
    async with AsyncSessionLocal() as session:
        # Get last 24 hours
        measurements = await HistoricalDataRepository.get_measurements_last_n_hours(
            session, 24
        )

        # Get specific time range
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        measurements = await HistoricalDataRepository.get_measurements_by_time_range(
            session, start, end
        )

        # Get latest measurements
        latest = await HistoricalDataRepository.get_latest_measurements(
            session, limit=100
        )
```

### Direct SQL Queries

```bash
# Open database
sqlite3 backend/data/ionospheric.db

# Count total records
SELECT COUNT(*) FROM historical_measurements;

# Get latest 10 measurements
SELECT timestamp, kp_index, storm_probability
FROM historical_measurements
ORDER BY timestamp DESC
LIMIT 10;

# Average storm probability by year
SELECT
    strftime('%Y', timestamp) as year,
    AVG(storm_probability) as avg_prob
FROM historical_measurements
GROUP BY year;

# Storm events (probability > 40%)
SELECT timestamp, storm_probability, kp_index
FROM historical_measurements
WHERE storm_probability > 40
ORDER BY storm_probability DESC;
```

## API Endpoints

### Get Historical Trends

```bash
# 24 hours
curl http://localhost:8000/api/v1/trends/24

# 1 week (168 hours)
curl http://localhost:8000/api/v1/trends/168

# 1 month (720 hours)
curl http://localhost:8000/api/v1/trends/720

# 1 year (8,760 hours)
curl http://localhost:8000/api/v1/trends/8760

# 10 years (87,600 hours)
curl http://localhost:8000/api/v1/trends/87600
```

## Performance

### Query Performance

- **24 hours**: <10ms
- **1 week**: <20ms
- **1 month**: <50ms
- **1 year**: <200ms
- **10 years**: <1 second

### Storage

- **Database Size**: ~50-100 MB for 87,600 records
- **Index Size**: ~5-10 MB
- **Total**: ~60-110 MB

## Backup

### Create Backup

```bash
# SQLite backup
cp backend/data/ionospheric.db backend/data/ionospheric_backup_$(date +%Y%m%d).db

# Or use SQLite's backup command
sqlite3 backend/data/ionospheric.db ".backup backend/data/backup.db"
```

### Restore Backup

```bash
cp backend/data/ionospheric_backup_20250125.db backend/data/ionospheric.db
```

## Maintenance

### Vacuum Database

Optimize database file size:

```bash
sqlite3 backend/data/ionospheric.db "VACUUM;"
```

### Analyze Query Performance

```bash
sqlite3 backend/data/ionospheric.db "ANALYZE;"
```

### Check Database Integrity

```bash
sqlite3 backend/data/ionospheric.db "PRAGMA integrity_check;"
```

## Production Considerations

For production deployments with larger scale:

1. **PostgreSQL Migration**
   - Better concurrent write performance
   - More advanced indexing options
   - Better for multi-user scenarios

2. **TimescaleDB Extension**
   - Optimized for time-series data
   - Automatic data partitioning
   - Continuous aggregates for analytics

3. **Redis Caching**
   - Cache frequently accessed queries
   - Reduce database load
   - Faster response times

## Troubleshooting

### Database Locked Error

SQLite locks on concurrent writes:

```python
# Solution: Use connection pooling and retry logic
# Already configured in database.py with pool_pre_ping=True
```

### Migration Conflicts

```bash
# Reset migrations (CAUTION: loses data)
rm -rf alembic/versions/*.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Regenerate Seed Data

```bash
# Delete existing database
rm backend/data/ionospheric.db

# Re-run migrations
alembic upgrade head

# Reseed
python seed_historical_data.py
```

## Development

### Adding New Fields

1. Modify `app/db/models.py`
2. Create migration: `alembic revision --autogenerate -m "Add field description"`
3. Review generated migration in `alembic/versions/`
4. Apply: `alembic upgrade head`
5. Update repository methods if needed

### Testing Queries

```python
# Test query performance
import time
from app.db.database import AsyncSessionLocal
from app.db.repository import HistoricalDataRepository

async def benchmark():
    async with AsyncSessionLocal() as session:
        start = time.time()
        data = await HistoricalDataRepository.get_measurements_last_n_hours(
            session, 87600
        )
        elapsed = time.time() - start
        print(f"Query time: {elapsed:.3f}s, Records: {len(data)}")
```

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Async SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
