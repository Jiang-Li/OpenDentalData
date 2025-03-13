import xml.etree.ElementTree as ET
from typing import Dict, List, Set, Tuple, NamedTuple, Optional
from pathlib import Path
import subprocess
from dataclasses import dataclass, field

@dataclass
class TableInfo:
    """Information about a database table"""
    name: str
    description: str
    columns: List[Tuple[str, str, bool]]  # (name, type, is_pk)
    foreign_keys: List[Tuple[str, str]]  # (column, referenced_table)
    primary_key: Optional[str] = None
    relationships: List[str] = field(default_factory=list)  # list of relationship strings

def get_used_columns() -> Dict[str, Set[str]]:
    """
    Extract tables and their columns used in SQL queries
    Returns:
        Dictionary mapping table aliases to sets of used columns
    """
    used_columns = {
        'patient': {'PatNum', 'LName', 'FName', 'Birthdate', 'Gender', 'Zip'},
        'patplan': {'PatNum', 'InsSubNum'},
        'inssub': {'InsSubNum', 'PlanNum'},
        'payplan': {'PatNum', 'PayPlanNum'},
        'procedurelog': {'PatNum', 'ProcNum', 'ProcStatus', 'ProcFee', 'AptNum'},
        'paysplit': {'ProcNum', 'SplitAmt', 'PayNum'},
        'claimproc': {'ProcNum', 'InsPayAmt'},
        'appointment': {'AptNum', 'PatNum', 'AptDateTime', 'AptStatus', 'AppointmentTypeNum'},
        'appointmenttype': {'AppointmentTypeNum', 'AppointmentTypeName'},
        'payment': {'PayNum', 'PayDate'}
    }
    return used_columns

def parse_schema_xml(xml_file: str) -> List[TableInfo]:
    """
    Parse the XML schema file to extract table information for tables and columns used in SQL queries
    Args:
        xml_file: Path to the XML schema file
    Returns:
        List of TableInfo objects
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Get tables and columns used in queries
    used_columns = get_used_columns()
    sql_tables = set(used_columns.keys())
    
    # First pass: collect table information
    table_info_map = {}
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
        primary_key = None
        
        # Process columns
        for column in table.findall('column'):
            col_name = column.get('name', '')
            col_type = column.get('type', '')
            if not col_name or not col_type:
                continue
                
            # Only include columns that are used in queries or are primary/foreign keys
            if col_name not in used_columns[table_name]:
                # Check if it's a primary key
                summary = column.find('summary')
                summary_text = summary.text if summary is not None else ''
                is_pk = bool(summary_text and 'Primary key' in summary_text)
                
                # Check if it's a foreign key to a used table
                fk = column.get('fk', '')
                is_used_fk = bool(fk and fk in sql_tables)
                
                # Skip if not primary key or used foreign key
                if not (is_pk or is_used_fk):
                    continue
            
            # Check if primary key
            summary = column.find('summary')
            summary_text = summary.text if summary is not None else ''
            is_pk = bool(summary_text and 'Primary key' in summary_text)
            
            # Store primary key
            if is_pk:
                primary_key = col_name
                
            # Add column
            columns.append((col_name, col_type, is_pk))
            
            # Check for foreign key
            fk = column.get('fk', '')
            if fk and fk in sql_tables:
                foreign_keys.append((col_name, fk))
        
        table_info = TableInfo(
            name=table_name,
            description=description,
            columns=columns,
            foreign_keys=foreign_keys,
            primary_key=primary_key
        )
        table_info_map[table_name] = table_info
    
    # Second pass: resolve relationships
    for table_name, table_info in table_info_map.items():
        # Add relationships based on foreign keys
        for fk_col, fk_table in table_info.foreign_keys:
            if fk_table in table_info_map:
                referenced_table = table_info_map[fk_table]
                if referenced_table.primary_key:
                    # Add relationship details
                    relationship = f"{table_name}.{fk_col} -> {fk_table}.{referenced_table.primary_key}"
                    table_info.relationships.append(relationship)
    
    return list(table_info_map.values())

def generate_dot_erd(tables: List[TableInfo]) -> str:
    """
    Generate DOT format ERD with table grouping and improved relationships
    """
    dot_content = [
        'digraph G {',
        '  rankdir="TB";',
        '  node [shape=none, margin=0];',
        '  edge [fontsize=9, len=1.5];',
        '  splines=polyline;',
        '  concentrate=true;',
        
        # Define subgraphs for logical grouping
        '  subgraph cluster_patient {',
        '    style="filled";',
        '    color=lightblue;',
        '    label="Patient Information";',
        '    node [style=filled, fillcolor=white];',
        '    patient; patplan; inssub;',
        '  }',
        
        '  subgraph cluster_appointments {',
        '    style="filled";',
        '    color=lightgreen;',
        '    label="Appointments";',
        '    node [style=filled, fillcolor=white];',
        '    appointment; appointmenttype; procedurelog;',
        '  }',
        
        '  subgraph cluster_payments {',
        '    style="filled";',
        '    color=lightsalmon;',
        '    label="Payments";',
        '    node [style=filled, fillcolor=white];',
        '    payment; paysplit; payplan; claimproc;',
        '  }'
    ]
    
    # Add nodes (tables)
    for table in tables:
        # Format columns as HTML-like label
        columns = []
        for col_name, col_type, is_pk in table.columns:
            # Format column with type and PK indicator
            if is_pk:
                columns.append(f'<TR><TD PORT="{col_name}" ALIGN="LEFT"><B>{col_name} (PK)</B></TD><TD ALIGN="LEFT">{col_type}</TD></TR>')
            else:
                columns.append(f'<TR><TD PORT="{col_name}" ALIGN="LEFT">{col_name}</TD><TD ALIGN="LEFT">{col_type}</TD></TR>')
            
        # Create HTML-like table label
        label = [
            '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">',
            f'<TR><TD COLSPAN="2" BGCOLOR="lightgrey"><B>{table.name}</B></TD></TR>',
            *columns,
            '</TABLE>>'
        ]
        
        # Add node definition
        dot_content.append(f'  {table.name} [label={" ".join(label)}];')
    
    # Add edges (relationships)
    for table in tables:
        for rel in table.relationships:
            # Parse relationship string
            source, target = rel.split(' -> ')
            source_table, source_col = source.split('.')
            target_table, target_col = target.split('.')
            
            # Style edges based on relationship type
            if source_col.endswith('PatNum') or target_col.endswith('PatNum'):
                # Patient relationships in blue dashed lines
                edge_style = '[color=blue, style=dashed]'
            elif source_table == target_table:
                # Self-referential relationships in gray dotted lines
                edge_style = '[color=gray, style=dotted]'
            else:
                # Regular relationships in black solid lines
                edge_style = '[color=black]'
            
            dot_content.append(f'  {source_table}:{source_col} -> {target_table}:{target_col} {edge_style};')
    
    dot_content.append('}')
    return '\n'.join(dot_content)

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