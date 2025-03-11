
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
