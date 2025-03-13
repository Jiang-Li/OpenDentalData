#!/usr/bin/env python3

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import logging
from typing import Dict, List, TypedDict
import sys
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Type definitions
class Column(TypedDict):
    order: str
    name: str
    data_type: str
    constraints: str
    description: str
    enum_values: List[str]

class Table(TypedDict):
    name: str
    description: str
    columns: List[Column]
    primary_keys: List[str]
    foreign_keys: Dict[str, str]

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and newlines."""
    if not text:
        return ""
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()

def escape_markdown(text: str) -> str:
    """Escape special markdown characters in text."""
    if not text:
        return ""
    # Characters to escape: \ ` * _ { } [ ] ( ) # + - . !
    chars_to_escape = r'\\`*_{}[]()#+-.!'
    return re.sub(f'([{chars_to_escape}])', r'\\\1', text)

def parse_enum_values(column_elem) -> List[str]:
    """Parse enum values from a column element."""
    enum_values = []
    enum_elem = column_elem.find('Enumeration')
    if enum_elem is not None:
        for enum_value in enum_elem.findall('EnumValue'):
            name = enum_value.get('name')
            value = enum_value.text
            enum_values.append(f"{name} ({value})")
    return enum_values

def parse_column(column_elem) -> Column:
    """Parse a single column element into a column definition."""
    name = column_elem.get('name', '')
    if not name:
        return None
        
    summary_elem = column_elem.find('summary')
    description = clean_text(summary_elem.text) if summary_elem is not None else ''
    
    # Check for foreign key in description
    fk_attr = column_elem.get('fk', '')
    if fk_attr:
        description = f"FK to {fk_attr}. {description}"
    
    return {
        'order': column_elem.get('order', ''),
        'name': name,
        'data_type': column_elem.get('type', ''),
        'constraints': '',
        'description': description,
        'enum_values': parse_enum_values(column_elem)
    }

def parse_table(table_elem) -> tuple[str, Table]:
    """Parse a complete table element including name, description, and columns."""
    table_name = table_elem.get('name', '')
    if not table_name:
        return None, None
    
    summary_elem = table_elem.find('summary')
    description = clean_text(summary_elem.text) if summary_elem is not None else ''
    
    columns = []
    primary_keys = []
    foreign_keys = {}
    
    for column_elem in table_elem.findall('column'):
        column = parse_column(column_elem)
        if column:
            if 'primary key' in column['description'].lower():
                primary_keys.append(column['name'])
            
            fk_attr = column_elem.get('fk', '')
            if fk_attr:
                foreign_keys[column['name']] = fk_attr
            
            columns.append(column)
    
    return table_name, {
        'name': table_name,
        'description': description,
        'columns': columns,
        'primary_keys': primary_keys,
        'foreign_keys': foreign_keys
    }

def parse_schema(xml_file: str) -> Dict[str, Table]:
    """Parse the XML file and extract schema information."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tables = {}
        
        for table_elem in root.findall('table'):
            try:
                table_name, table = parse_table(table_elem)
                if table_name and table:
                    tables[table_name] = table
            except Exception as e:
                logging.error(f"Error parsing table element: {e}")
                
        return tables
                
    except Exception as e:
        logging.error(f"Error reading or parsing XML file: {e}")
        raise

def format_description_for_table(description: str, enum_values: List[str]) -> str:
    """Format description and enum values for markdown table cell."""
    if not enum_values:
        return escape_markdown(description)
        
    # Format enum values as a list within the cell
    enum_text = "<br><br>**Enum values:**<br>" + "<br>".join(f"• {escape_markdown(value)}" for value in enum_values)
    return escape_markdown(description) + enum_text

def write_table_markdown(f, table_name: str, table: Table) -> None:
    """Write a single table's markdown representation to a file."""
    # Create markdown-style anchor
    f.write(f"## Table: {escape_markdown(table_name)}\n\n")
    
    if table['description']:
        f.write(f"{escape_markdown(table['description'])}\n\n")
    
    f.write("| Order | Column Name | Data Type | Constraints | Description |\n")
    f.write("|-------|-------------|-----------|-------------|-------------|\n")
    
    for column in table['columns']:
        description = format_description_for_table(column['description'], column['enum_values'])
        f.write(f"| {escape_markdown(column['order'])} | {escape_markdown(column['name'])} | {escape_markdown(column['data_type'])} | {escape_markdown(column['constraints'])} | {description} |\n")
    
    if table['primary_keys']:
        f.write("\n### Primary Keys\n")
        for pk in table['primary_keys']:
            f.write(f"- {escape_markdown(pk)}\n")
    
    if table['foreign_keys']:
        f.write("\n### Foreign Keys\n")
        for column, reference in table['foreign_keys'].items():
            # Use markdown-style anchor for foreign key references
            ref_anchor = f"table-{reference.lower()}"
            f.write(f"- {escape_markdown(column)} → [{escape_markdown(reference)}](#{ref_anchor})\n")
    
    f.write("\n")

def generate_markdown(tables: Dict[str, Table], output_file: str) -> None:
    """Generate Markdown documentation from the parsed schema."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Database Schema\n\n")
            
            # Write table of contents
            f.write("## Table of Contents\n\n")
            
            # Group tables by first letter
            grouped_tables = {}
            for table_name in sorted(tables.keys()):
                first_letter = table_name[0].upper()
                if first_letter not in grouped_tables:
                    grouped_tables[first_letter] = []
                grouped_tables[first_letter].append(table_name)
            
            # Write TOC with groups
            for letter in sorted(grouped_tables.keys()):
                f.write(f"### {letter}\n")
                for table_name in sorted(grouped_tables[letter]):
                    # Use markdown-style anchor
                    anchor = f"table-{table_name.lower()}"
                    f.write(f"- [{escape_markdown(table_name)}](#{anchor})\n")
                f.write("\n")
            
            f.write("---\n\n")  # Add a horizontal line to separate TOC from content
            
            # Write each table's documentation
            for table_name, table in sorted(tables.items()):
                write_table_markdown(f, table_name, table)
                
        logging.info(f"Successfully generated Markdown schema at {output_file}")
        
    except Exception as e:
        logging.error(f"Error generating Markdown: {e}")
        raise

def main():
    if len(sys.argv) != 3:
        print("Usage: python schema_parser.py <input_xml_file> <output_markdown_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        tables = parse_schema(input_file)
        generate_markdown(tables, output_file)
    except Exception as e:
        logging.error(f"Schema parsing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 