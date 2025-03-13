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
│   └── schema_parser.py   # XML to Markdown schema parser
│
├── docs/                  # Documentation
│   ├── notes.md          # Working notes and observations
│   ├── schema.md         # Comprehensive database schema
│   └── OpenDentalDocumentation24-3.xml  # Raw OpenDental documentation
```

## Getting Started
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Review the database schema:
   - Check `docs/schema.md` for comprehensive database structure
   - Reference `docs/OpenDentalDocumentation24-3.xml` for original documentation

3. Explore SQL queries:
   - `sql/appointments.sql`: Queries for appointment management
   - `sql/patients.sql`: Queries for patient data

4. Development:
   - Use `src/schema_parser.py` to update schema documentation if needed
   - Check `docs/notes.md` for implementation details and decisions

## Updating the Schema

### When to Update
- When a new version of OpenDental documentation is released
- When you need to analyze schema changes between versions
- When you discover the current schema documentation is outdated

### How to Update
1. Obtain the new OpenDental documentation XML file (e.g., `OpenDentalDocumentation24-3.xml`)
2. Place the XML file in the `docs/` directory
3. Run the schema parser:
   ```bash
   python src/schema_parser.py docs/OpenDentalDocumentation24-3.xml docs/schema.md
   ```
4. Verify the update by:
   - Checking the generated `schema.md` file
   - Reviewing the table of contents
   - Confirming table definitions are complete
   - Validating foreign key relationships
