# Project Requirements and Queries

This project aims to analyze the OpenDental database for predictive models for assessing patient payment risk.

### 1. Schema Review

Need a Python script that will:

1. Parse an HTML file containing database schema definitions
2. Extract the following information:
   - Table names
   - Column definitions for each table including:
     * Column name
     * Data type
     * Constraints
     * Column summary/description
   - Primary keys, foreign keys, and other constraints

3. Convert the extracted information into Markdown format with this structure:
   ```markdown
   # Database Schema

   ## Table: [table_name]
   | Column Name | Data Type | Constraints | Description |
   |------------|-----------|-------------|-------------|
   | column1    | type1     | constraints | This column stores... |
   | column2    | type2     | constraints | This field represents... |

   ```

4. Save the generated Markdown to a file named 'schema.md'

Technical Requirements:
- Use BeautifulSoup4 for HTML parsing
- Handle common HTML table structures (<table>, <tr>, <td> elements)
- Extract column descriptions/summaries from the HTML
- Preserve any existing relationships between tables
- Include error handling for malformed HTML
- Add comments explaining the parsing logic

5. Other

- Need all columns,such as Order in the table column definition




### 2. SQL 

For a project to predict if a patient will come back and pay in their next appointments, compose queries to pull patient and appointment level data.

- If information can be derived from appointments, it should not be included in the patient-level queries.
