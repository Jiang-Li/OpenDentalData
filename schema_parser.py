#!/usr/bin/env python3

from bs4 import BeautifulSoup
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
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()

def escape_markdown(text: str) -> str:
    """Escape special markdown characters in text."""
    # Characters to escape: \ ` * _ { } [ ] ( ) # + - . !
    chars_to_escape = r'\\`*_{}[]()#+-.!'
    return re.sub(f'([{chars_to_escape}])', r'\\\1', text)

def parse_column(row) -> Column:
    """Parse a single table row into a column definition."""
    cells = row.find_all('td')
    if len(cells) >= 4:
        name = cells[1].text.strip()
        # Skip rows that don't have a column name (enum value rows)
        if not name:
            return None
            
        description = clean_text(cells[3].text)
        
        # Check if this is an enum definition
        enum_values = []
        if 'enum:' in description.lower():
            # Extract enum values from following rows
            next_row = row.find_next_siblings('tr')
            for enum_row in next_row:
                enum_cells = enum_row.find_all('td')
                if len(enum_cells) >= 4 and not enum_cells[1].text.strip():
                    enum_value = clean_text(enum_cells[3].text)
                    if enum_value:
                        enum_values.append(enum_value)
                else:
                    break
        
        return {
            'order': cells[0].text.strip(),
            'name': name,
            'data_type': cells[2].text.strip(),
            'constraints': '',
            'description': description,
            'enum_values': enum_values
        }
    return None

def extract_table_name_and_desc(section: BeautifulSoup) -> tuple[str, str]:
    """Extract table name and description from the table header section."""
    header_table = section.find('table')
    if not header_table:
        return None, None
        
    # The table name is in the first row, first cell, in a <b> tag
    name_cell = header_table.find('b')
    if not name_cell:
        return None, None
    
    table_name = name_cell.text.strip()
    
    # The description is in the second row, first cell
    desc_row = header_table.find_all('tr')[1] if len(header_table.find_all('tr')) > 1 else None
    description = clean_text(desc_row.find('td').text) if desc_row else ''
    
    return table_name, description

def extract_foreign_key_reference(description: str) -> str:
    """Extract the referenced table name from a foreign key description."""
    desc = description.lower()
    if 'fk to' in desc:
        # Find the referenced table between 'fk to' and the next period or space
        match = re.search(r'fk to\s+([a-z0-9_]+)', desc)
        if match:
            return match.group(1)
    return None

def parse_table_section(section: BeautifulSoup) -> tuple[str, Table]:
    """Parse a complete table section including name, description, and columns."""
    table_name, description = extract_table_name_and_desc(section)
    if not table_name:
        return None, None
    
    column_table = section.find_all('table')[1] if len(section.find_all('table')) > 1 else None
    if not column_table:
        return None, None
    
    columns = []
    primary_keys = []
    foreign_keys = {}
    
    for row in column_table.find_all('tr')[1:]:  # Skip header row
        column = parse_column(row)
        if column:
            if 'primary key' in column['description'].lower():
                primary_keys.append(column['name'])
            
            referenced_table = extract_foreign_key_reference(column['description'])
            if referenced_table:
                foreign_keys[column['name']] = referenced_table
            
            columns.append(column)
    
    return table_name, {
        'name': table_name,
        'description': description,
        'columns': columns,
        'primary_keys': primary_keys,
        'foreign_keys': foreign_keys
    }

def parse_schema(html_file: str) -> Dict[str, Table]:
    """Parse the HTML file and extract schema information."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        tables = {}
        
        # Find all table sections - they are wrapped in <p> tags
        table_sections = soup.find_all('p')
        
        for section in table_sections:
            try:
                # Each valid table section should have at least 2 tables
                if len(section.find_all('table')) >= 2:
                    table_name, table = parse_table_section(section)
                    if table_name and table:
                        tables[table_name] = table
            except Exception as e:
                logging.error(f"Error parsing table section: {e}")
                
        return tables
                
    except Exception as e:
        logging.error(f"Error reading or parsing HTML file: {e}")
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
        print("Usage: python schema_parser.py <input_html_file> <output_markdown_file>")
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