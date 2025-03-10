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

For a project to predict if a patient will come back and pay in the next appointments, the following queries pull patient and appointment level data. 


```sql
-- 1. PATIENT LEVEL QUERY
SELECT 
    p.PatNum,
    p.LName,          
    -- Converting birthdate to middle of the year (June 30)
    STR_TO_DATE(
        CONCAT(
            YEAR(p.Birthdate),  -- Keep the year
            '-06-30'            -- Set to June 30
        ),
        '%Y-%m-%d'
    ) as Birthdate,    
    p.Gender,
    p.State,
    p.Zip,           
    
    COUNT(DISTINCT pp.PlanNum) as CurrentInsurancePlans,
    MAX(CASE WHEN pp.PlanNum IS NOT NULL THEN 1 ELSE 0 END) as HasInsurance,
    COUNT(DISTINCT pplan.PayPlanNum) as ActivePaymentPlans,
    SUM(pl.ProcFee) - SUM(COALESCE(ps.SplitAmt, 0)) as CurrentOutstandingBalance

FROM patient p
LEFT JOIN patplan pp ON p.PatNum = pp.PatNum
LEFT JOIN payplan pplan ON p.PatNum = pplan.PatNum
LEFT JOIN procedurelog pl ON p.PatNum = pl.PatNum
LEFT JOIN paysplit ps ON pl.ProcNum = ps.ProcNum
GROUP BY p.PatNum;

-- 2. APPOINTMENT LEVEL QUERY
SELECT 
    -- Identifiers
    a.AptNum,
    a.PatNum,
    a.AptDateTime,
    
    -- Non-PII Appointment Information
    a.AptStatus,
    at.Description as AppointmentType,
    
    -- Financial Information (non-PII)
    COUNT(DISTINCT pl.ProcNum) as ProcedureCount,
    SUM(pl.ProcFee) as TotalProcedureFees,
    SUM(ps.SplitAmt) as PatientPaidAmount,
    SUM(cp.InsPayAmt) as InsurancePaidAmount,
    MIN(pay.PayDate) as FirstPaymentDate,
    MAX(pay.PayDate) as LastPaymentDate,
    DATEDIFF(MIN(pay.PayDate), a.AptDateTime) as DaysToFirstPayment,
    
    -- Payment Status (non-PII)
    CASE 
        WHEN SUM(pl.ProcFee) = SUM(COALESCE(ps.SplitAmt, 0)) + SUM(COALESCE(cp.InsPayAmt, 0)) 
        THEN 'Fully Paid'
        WHEN SUM(COALESCE(ps.SplitAmt, 0)) + SUM(COALESCE(cp.InsPayAmt, 0)) > 0 
        THEN 'Partially Paid'
        ELSE 'Not Paid'
    END as PaymentStatus,
    
    -- Balance Information (non-PII)
    SUM(pl.ProcFee) - 
    SUM(COALESCE(ps.SplitAmt, 0)) - 
    SUM(COALESCE(cp.InsPayAmt, 0)) as RemainingBalance

FROM appointment a
LEFT JOIN appointmenttype at ON a.AppointmentTypeNum = at.AppointmentTypeNum
LEFT JOIN procedurelog pl ON a.AptNum = pl.AptNum
LEFT JOIN paysplit ps ON pl.ProcNum = ps.ProcNum
LEFT JOIN payment pay ON ps.PayNum = pay.PayNum
LEFT JOIN claimproc cp ON pl.ProcNum = cp.ProcNum

GROUP BY a.AptNum
ORDER BY a.PatNum, a.AptDateTime;
```