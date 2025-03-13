# OpenDentalData - Database Schema Analysis

A Python-based tool for analyzing and visualizing the Open Dental database schema, focusing on patient and appointment data management. The project generates Entity Relationship Diagrams (ERDs) that highlight the relationships between key tables in the database.

## Features

- **Schema Parsing**: Parses XML schema documentation to extract table structures and relationships
- **ERD Generation**: Creates visual Entity Relationship Diagrams using Graphviz
- **SQL Analysis**: Focuses on tables and columns used in patient and appointment queries
- **Smart Visualization**: Groups related tables and color-codes different types of relationships

## Project Structure

```
.
├── src/
│   └── generate_erd.py      # Main script for ERD generation
├── docs/
│   ├── schema.md           # Schema documentation
│   ├── database_erd.png    # Generated ERD image
│   └── database_erd.dot    # Generated DOT source file
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- Graphviz (for ERD generation)

### Installing Graphviz

- **macOS**: `brew install graphviz`
- **Ubuntu/Debian**: `sudo apt-get install graphviz`
- **Windows**: Download installer from [Graphviz Downloads](https://graphviz.org/download/)

## Usage

1. Generate the ERD:
   ```bash
   python src/generate_erd.py
   ```
   This will create:
   - `docs/database_erd.png`: The visual ERD
   - `docs/database_erd.dot`: The DOT source file

## ERD Layout

The ERD is organized into logical groups:

1. **Patient Information** (Light Blue)
   - `patient`: Core patient demographics
   - `patplan`: Patient insurance plans
   - `inssub`: Insurance subscriptions

2. **Appointments** (Light Green)
   - `appointment`: Appointment details
   - `appointmenttype`: Types of appointments
   - `procedurelog`: Dental procedures

3. **Payments** (Light Salmon)
   - `payment`: Payment records
   - `paysplit`: Payment splits
   - `payplan`: Payment plans
   - `claimproc`: Insurance claims

### Relationship Types

- **Blue Dashed Lines**: Patient-related relationships
- **Gray Dotted Lines**: Self-referential relationships
- **Black Solid Lines**: Standard relationships

## Tables Overview

### Core Tables
- `patient`: Patient demographic information (PatNum, LName, FName, etc.)
- `appointment`: Appointment scheduling and status
- `procedurelog`: Dental procedures and treatments

### Insurance Tables
- `patplan`: Links patients to insurance plans
- `inssub`: Insurance subscription details
- `claimproc`: Insurance claim processing

### Payment Tables
- `payment`: Payment transactions
- `paysplit`: Payment distribution
- `payplan`: Payment plan arrangements

## Contributing

Feel free to submit issues and enhancement requests. We welcome your feedback to improve the visualization and analysis of the Open Dental database schema.
