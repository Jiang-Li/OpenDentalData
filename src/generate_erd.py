import xml.etree.ElementTree as ET
from typing import Dict, List, Set, Tuple, NamedTuple
from pathlib import Path
import subprocess

class TableInfo(NamedTuple):
    """Information about a database table"""
    name: str
    description: str
    columns: List[Tuple[str, str, bool]]  # (name, type, is_pk)
    foreign_keys: List[Tuple[str, str]]  # (column, referenced_table)

def parse_schema_xml(xml_file: str) -> List[TableInfo]:
    """
    Parse the XML schema file to extract table information for tables used in SQL queries
    Args:
        xml_file: Path to the XML schema file
    Returns:
        List of TableInfo objects
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    tables: List[TableInfo] = []
    
    # Tables used in SQL queries
    sql_tables = {
        'patient', 'patplan', 'inssub', 'payplan', 'procedurelog', 'paysplit', 
        'claimproc', 'appointment', 'appointmenttype', 'payment'
    }
    
    # Collect information for SQL tables
    for table in root.findall('.//table'):
        table_name = table.get('name', '')
        if not table_name or table_name not in sql_tables:
            continue
            
        # Get table description
        summary = table.find('summary')
        description = summary.text if summary is not None and summary.text else ''
        description = description.split('.')[0] if description else ''  # Take first sentence only
        
        columns = []
        foreign_keys = []
        
        # Process columns
        for column in table.findall('.//column'):
            col_name = column.get('name', '')
            col_type = column.get('type', '')
            if not col_name or not col_type:
                continue
                
            # Check if primary key
            summary = column.find('summary')
            summary_text = summary.text if summary is not None else ''
            is_pk = bool(summary_text and 'Primary key' in summary_text)
            
            # Only include primary keys and foreign keys
            fk = column.get('fk', '')
            if is_pk or (fk and fk in sql_tables):
                columns.append((col_name, col_type, is_pk))
            
            # Check for foreign key
            if fk and fk in sql_tables:
                foreign_keys.append((col_name, fk))
        
        tables.append(TableInfo(
            name=table_name,
            description=description,
            columns=columns,
            foreign_keys=foreign_keys
        ))
    
    return tables

def generate_dot_erd(tables: List[TableInfo]) -> str:
    """Generate DOT syntax for Graphviz ERD diagram"""
    
    dot = [
        'digraph ERD {',
        '    rankdir=TB;',  # Top to bottom layout
        '    compound=true;',  # Enable connections to subgraphs
        '    splines=polyline;',  # Use polyline edges for better label placement
        '    concentrate=true;',  # Merge edges going to the same destination
        '    node [shape=record, fontname="Arial", fontsize=10, margin="0.2,0.1"];',
        '    edge [fontname="Arial", fontsize=8, len=1.2];',
        '',
        '    # Define node groups',
        '    subgraph cluster_patient {',
        '        label="Patient Information";',
        '        style=rounded;',
        '        bgcolor="#f0f8ff";',  # Light blue background',
        '        color="#a0c8ff";',  # Darker blue border
        '        patient;  # Core patient table',
        '    }',
        '',
        '    subgraph cluster_appointments {',
        '        label="Appointments";',
        '        style=rounded;',
        '        bgcolor="#f0fff0";',  # Light green background
        '        color="#a0ffa0";',  # Darker green border
        '        appointment;',
        '        appointmenttype;',
        '        procedurelog;',
        '    }',
        '',
        '    subgraph cluster_insurance {',
        '        label="Insurance";',
        '        style=rounded;',
        '        bgcolor="#fff0f8";',  # Light pink background
        '        color="#ffa0c8";',  # Darker pink border
        '        inssub;',
        '        patplan;',
        '        claimproc;',
        '    }',
        '',
        '    subgraph cluster_payments {',
        '        label="Payments";',
        '        style=rounded;',
        '        bgcolor="#fff8f0";',  # Light orange background
        '        color="#ffd0a0";',  # Darker orange border
        '        payment;',
        '        payplan;',
        '        paysplit;',
        '    }',
        ''
    ]
    
    # Add table nodes
    for table in tables:
        # Format columns for the table label
        columns = []
        if table.description:
            desc = table.description.replace('"', '\\"').replace('\n', ' ').strip()
            columns.append(f'<desc>{desc}')
        
        for col_name, col_type, is_pk in table.columns:
            col_str = f'<{col_name}> {col_name}'
            if is_pk:
                col_str += ' (PK)'
            col_str += f'\\n{col_type}'
            columns.append(col_str)
        
        # Create table node with HTML-like label for better formatting
        node_def = f'    {table.name} [label="{{{table.name}|{"|".join(columns)}}}"];'
        dot.append(node_def)
    
    dot.append('\n    # Relationships')
    
    # Add relationships with improved edge routing
    for table in tables:
        for column, referenced_table in table.foreign_keys:
            # Only add relationship if both tables are in our limited set
            if referenced_table in {t.name for t in tables}:
                # Use different edge styles based on relationship type
                if referenced_table == 'patient':
                    # Patient relationships are dashed and blue
                    edge = f'    {table.name}:{column} -> {referenced_table} [label="{column}" style=dashed color="#4040ff" fontcolor="#4040ff"];'
                elif table.name == referenced_table:
                    # Self-referential relationships are dotted and gray
                    edge = f'    {table.name}:{column} -> {referenced_table} [label="{column}" style=dotted color="#808080" fontcolor="#808080"];'
                else:
                    # Regular relationships are solid black
                    edge = f'    {table.name}:{column} -> {referenced_table} [label="{column}"];'
                dot.append(edge)
    
    dot.append('}')
    return '\n'.join(dot)

def main():
    # Create docs directory if it doesn't exist
    Path("docs").mkdir(exist_ok=True)
    
    # Parse schema
    xml_file = "docs/OpenDentalDocumentation24-3.xml"
    tables = parse_schema_xml(xml_file)
    
    # Generate DOT code
    dot_code = generate_dot_erd(tables)
    
    # Save DOT file
    dot_file = "docs/database_erd.dot"
    with open(dot_file, "w") as f:
        f.write(dot_code)
    
    # Generate PNG using Graphviz
    output_file = "docs/database_erd.png"
    try:
        subprocess.run(['dot', '-Tpng', dot_file, '-o', output_file], check=True)
        print(f"ERD generated and saved to {output_file}")
        
        # Also save DOT source for reference
        print(f"DOT source saved to {dot_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating ERD: {e}")
    except FileNotFoundError:
        print("Error: Graphviz 'dot' command not found. Please ensure Graphviz is installed.")

if __name__ == "__main__":
    main() 