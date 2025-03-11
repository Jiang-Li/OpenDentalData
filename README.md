# OpenDental Database Schema Analysis

## Overview
This project focuses on analyzing database schemas and providing SQL data preparation suggestions. The analysis includes documentation of table structures, relationships, and suggested queries based on the OpenDental database schema.

## Project Structure
```
OpenDentalData/
├── sql/                    # SQL queries and table definitions
│   ├── appointments.sql    # Appointment-related queries
│   └── patients.sql       # Patient-related queries
│
├── src/                   # Source code
│   └── schema_parser.py   # HTML to Markdown schema parser
│
├── docs/                  # Documentation
│   ├── notes.md          # Working notes and observations
│   ├── schema.md         # Comprehensive database schema
│   └── OpenDentalDocumentation24-1.xml.html  # Raw OpenDental documentation
```

## Getting Started
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Review the database schema:
   - Check `docs/schema.md` for comprehensive database structure
   - Reference `docs/OpenDentalDocumentation24-1.xml.html` for original documentation

3. Explore SQL queries:
   - `sql/appointments.sql`: Queries for appointment management
   - `sql/patients.sql`: Queries for patient data

4. Development:
   - Use `src/schema_parser.py` to update schema documentation if needed
   - Check `docs/notes.md` for implementation details and decisions
