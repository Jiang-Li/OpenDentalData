# OpenDentalData - Database Schema Analysis

This project provides tools for analyzing and visualizing the Open Dental database schema, with a focus on patient and appointment data analysis.

## Features

- **Schema Parsing**: Parse XML schema documentation to extract table structures and relationships
- **ERD Generation**: Generate Entity Relationship Diagrams (ERD) using Graphviz
- **SQL Analysis**: Includes example SQL queries for common data analysis tasks

## Project Structure

```
.
├── src/
│   ├── generate_erd.py    # ERD generation script
│   └── schema_parser.py   # XML schema parser
├── sql/
│   ├── patients.sql       # Patient-level analysis queries
│   └── appointments.sql   # Appointment-level analysis queries
└── docs/
    ├── schema.md          # Markdown documentation of schema
    ├── database_erd.png   # Generated ERD diagram
    └── database_erd.dot   # DOT source for ERD
```

## Prerequisites

- Python 3.8+
- Graphviz (for ERD generation)

### Installing Graphviz

- macOS: `brew install graphviz`
- Linux: `apt-get install graphviz`
- Windows: Download from [Graphviz Downloads](https://graphviz.org/download/)

## Usage

1. **Generate ERD**:
   ```bash
   python src/generate_erd.py
   ```
   This will create:
   - `docs/database_erd.png`: Visual ERD diagram
   - `docs/database_erd.dot`: DOT source file

2. **SQL Queries**:
   - `sql/patients.sql`: Retrieve patient demographics, insurance status, and financial data
   - `sql/appointments.sql`: Analyze appointment scheduling and related financial information

## ERD Layout

The ERD is organized into logical groups:

- **Patient Information** (Blue): Core patient data
- **Appointments** (Green): Appointment scheduling and procedures
- **Insurance** (Pink): Insurance plans and claims
- **Payments** (Orange): Payment tracking and plans

Relationship types are indicated by different line styles:
- **Blue dashed lines**: Relationships to patient table
- **Gray dotted lines**: Self-referential relationships
- **Solid black lines**: Standard foreign key relationships

## Tables Included

The ERD focuses on the most relevant tables for patient and appointment analysis:

1. **Core Tables**:
   - `patient`: Patient demographics and core information
   - `appointment`: Appointment scheduling data
   - `procedurelog`: Dental procedures

2. **Insurance Tables**:
   - `inssub`: Insurance subscriptions
   - `patplan`: Patient-insurance plan links
   - `claimproc`: Insurance claims and payments

3. **Payment Tables**:
   - `payment`: Patient payments
   - `paysplit`: Payment allocations
   - `payplan`: Payment plans

4. **Supporting Tables**:
   - `appointmenttype`: Appointment type definitions

## Contributing

Feel free to submit issues and enhancement requests!
