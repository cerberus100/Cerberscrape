"""SQLAlchemy models for DataForge."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from core.db import Base


class BusinessRecord(Base):
    __tablename__ = "business_records"

    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    domain = Column(String(255))
    phone = Column(String(32))
    email = Column(String(255))
    address_line1 = Column(String(255))
    city = Column(String(128))
    state = Column(String(2), nullable=False)
    postal_code = Column(String(16))
    country = Column(String(64), default="US")
    county = Column(String(128))
    county_fips = Column(String(5))
    naics_code = Column(String(32))
    industry = Column(String(255))
    founded_year = Column(Integer)
    years_in_business = Column(Integer)
    employee_count = Column(Integer)
    annual_revenue_usd = Column(Integer)
    business_size = Column(String(32))  # micro, small, medium, large
    is_small_business = Column(Boolean)
    source = Column(String(255), nullable=False)
    last_verified = Column(DateTime, default=dt.datetime.utcnow)
    quality_score = Column(Integer, default=0)


class RFPRecord(Base):
    __tablename__ = "rfp_records"

    id = Column(Integer, primary_key=True)
    notice_id = Column(String(128), unique=True, nullable=False)
    title = Column(String(255))
    agency = Column(String(255))
    naics = Column(String(64))
    solicitation_number = Column(String(128))
    notice_type = Column(String(128))
    posted_date = Column(DateTime)
    close_date = Column(DateTime)
    place_of_performance_state = Column(String(2))
    description = Column(Text)
    url = Column(String(512))
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    estimated_value = Column(String(64))
    source = Column(String(255), nullable=False)
    last_checked = Column(DateTime, default=dt.datetime.utcnow)


