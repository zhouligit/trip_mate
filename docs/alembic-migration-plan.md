# Alembic Migration Plan (MVP)

## Goal
Keep schema evolution stable while MVP is changing quickly.

## Current migration
- `20260414_0001_init_core_tables.py`
  - users
  - user_profiles
  - groups
  - group_members
  - votes
  - vote_options
  - vote_records
  - orders
  - payments

## Planned next migrations
1. `0002_fleet_and_assignment`
   - fleets, buses, drivers, trip_assignments
2. `0003_ticket_and_verify`
   - tickets, verify logs
3. `0004_refund_and_settlement`
   - refunds, settlement records
4. `0005_rating_and_risk`
   - ratings, risk event logs, operation logs

## Commands
- Initialize DB revision:
  - `alembic upgrade head`
- Create next migration:
  - `alembic revision -m "add ticket tables"`
- Rollback one step:
  - `alembic downgrade -1`

## Team rules
- One PR should contain at most one migration file.
- Never edit an existing migration that has been applied in staging or production.
- Any nullable-to-not-null change must include data backfill migration.
