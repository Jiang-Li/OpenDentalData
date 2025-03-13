/*
 * APPOINTMENT LEVEL QUERY
 * This query retrieves appointment information along with related financial data at the appointment level.
 * It provides a comprehensive view of appointments, their status, associated procedures, and payment information.
 * 
 * Table relationships:
 * - appointment (a): Main appointment table with scheduling information
 * - appointmenttype (at): Contains appointment type definitions
 * - procedurelog (pl): Dental procedures linked to appointments
 * - paysplit (ps): Patient payments applied to procedures
 * - payment (pay): Payment transactions that contain paysplits
 * - claimproc (cp): Insurance payments and estimates for procedures
 */
SELECT 
    -- Identifiers
    a.AptNum,                   -- Primary appointment identifier
    a.PatNum,                   -- Patient identifier the appointment is for
    a.AptDateTime,              -- Date and time of the appointment
    
    -- Non-PII Appointment Information
    a.AptStatus,                -- Status of appointment (1=Scheduled, 2=Complete, 3=UnschedList, 5=Broken, etc.)
    at.AppointmentTypeName as AppointmentType,  -- Type of appointment (e.g., "Cleaning", "Crown", "Exam")
    
    -- Financial Information (non-PII)
    -- Count of distinct procedures associated with this appointment
    COUNT(DISTINCT pl.ProcNum) as ProcedureCount,
    
    -- Total fees for all procedures associated with this appointment
    SUM(pl.ProcFee) as TotalProcedureFees,
    
    -- Total amount paid by patient for procedures in this appointment
    SUM(ps.SplitAmt) as PatientPaidAmount,
    
    -- Total amount paid by insurance for procedures in this appointment
    SUM(cp.InsPayAmt) as InsurancePaidAmount,
    
    -- Date tracking for payments
    MIN(pay.PayDate) as FirstPaymentDate,       -- Date of first payment received
    MAX(pay.PayDate) as LastPaymentDate,        -- Date of most recent payment
    DATEDIFF(MIN(pay.PayDate), a.AptDateTime) as DaysToFirstPayment,  -- Days between appointment and first payment
    
    -- Payment Status (non-PII)
    -- Determine if appointment is fully paid, partially paid, or not paid
    CASE 
        -- If sum of patient payments + insurance payments equals the total fees, it's fully paid
        WHEN SUM(pl.ProcFee) = SUM(COALESCE(ps.SplitAmt, 0)) + SUM(COALESCE(cp.InsPayAmt, 0)) 
        THEN 'Fully Paid'
        -- If there are any payments (patient or insurance) but not fully paid, it's partially paid
        WHEN SUM(COALESCE(ps.SplitAmt, 0)) + SUM(COALESCE(cp.InsPayAmt, 0)) > 0 
        THEN 'Partially Paid'
        -- If no payments have been made, it's not paid
        ELSE 'Not Paid'
    END as PaymentStatus,
    
    -- Balance Information (non-PII)
    -- Calculate remaining balance by subtracting all payments from total fees
    SUM(pl.ProcFee) - 
    SUM(COALESCE(ps.SplitAmt, 0)) - 
    SUM(COALESCE(cp.InsPayAmt, 0)) as RemainingBalance

FROM appointment a
-- Join to get appointment type information
LEFT JOIN appointmenttype at ON a.AppointmentTypeNum = at.AppointmentTypeNum
-- Join to get procedures associated with this appointment
LEFT JOIN procedurelog pl ON a.AptNum = pl.AptNum
-- Join to get patient payments for these procedures
LEFT JOIN paysplit ps ON pl.ProcNum = ps.ProcNum
-- Join to get payment information for the paysplits
LEFT JOIN payment pay ON ps.PayNum = pay.PayNum
-- Join to get insurance payments for these procedures
LEFT JOIN claimproc cp ON pl.ProcNum = cp.ProcNum

-- Group by appointment to get one row per appointment
GROUP BY a.AptNum
-- Order by patient and appointment date/time
ORDER BY a.PatNum, a.AptDateTime;