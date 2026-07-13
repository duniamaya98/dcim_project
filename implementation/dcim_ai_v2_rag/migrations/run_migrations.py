#!/usr/bin/env python3
"""
Database Migration Runner for DCIM Analytics & AI Engine

Usage:
    python run_migrations.py
    python run_migrations.py --host 10.70.0.56 --port 5433 --database dcim_analytics --user ai_team
"""

import os
import sys
import argparse
import psycopg2
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migration(conn, migration_file: Path):
    """Run a single migration file"""
    logger.info(f"Running migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        sql = f.read()

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        logger.info(f"✓ Migration {migration_file.name} completed successfully")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"✗ Migration {migration_file.name} failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Run database migrations')
    parser.add_argument('--host', default=os.getenv('TIMESCALEDB_HOST', '10.70.0.56'))
    parser.add_argument('--port', type=int, default=int(os.getenv('TIMESCALEDB_PORT', '5433')))
    parser.add_argument('--database', default=os.getenv('TIMESCALEDB_DATABASE', 'dcim_analytics'))
    parser.add_argument('--user', default=os.getenv('TIMESCALEDB_USER', 'ai_team'))
    parser.add_argument('--password', default=os.getenv('TIMESCALEDB_PASSWORD'))
    parser.add_argument('--dry-run', action='store_true', help='Print SQL without executing')

    args = parser.parse_args()

    # Get migration files
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob('*.sql'))

    if not migration_files:
        logger.warning("No migration files found")
        return 1

    logger.info(f"Found {len(migration_files)} migration(s)")

    if args.dry_run:
        for mf in migration_files:
            logger.info(f"Would run: {mf.name}")
        return 0

    # Connect to database
    try:
        conn = psycopg2.connect(
            host=args.host,
            port=args.port,
            database=args.database,
            user=args.user,
            password=args.password
        )
        logger.info(f"Connected to {args.host}:{args.port}/{args.database}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return 1

    # Run migrations
    failed = []
    for migration_file in migration_files:
        success = run_migration(conn, migration_file)
        if not success:
            failed.append(migration_file.name)

    conn.close()

    # Summary
    if failed:
        logger.error(f"✗ {len(failed)} migration(s) failed: {', '.join(failed)}")
        return 1
    else:
        logger.info(f"✓ All {len(migration_files)} migration(s) completed successfully")
        return 0


if __name__ == '__main__':
    sys.exit(main())
