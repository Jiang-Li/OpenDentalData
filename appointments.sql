
-- APPOINTMENT LEVEL QUERY
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