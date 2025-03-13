/*
 * PATIENT LEVEL QUERY
 * This query retrieves patient demographic information along with insurance status,
 * payment plan information, and billing data at the patient level.
 * 
 * Table relationships:
 * - patient (p): Main patient table with demographic information
 * - patplan (pp): Links patients to insurance subscriptions
 * - inssub (ins): Links insurance subscriptions to insurance plans
 * - payplan (pplan): Payment plans for patients
 * - procedurelog (pl): Dental procedures performed on patients
 * - paysplit (ps): Patient payments applied to procedures
 * - claimproc (cp): Insurance payments and estimates for procedures
 */
SELECT 
    -- Basic patient identifiers and demographics
    p.PatNum,                   -- Primary patient identifier
    p.LName,                    -- Last name
    
    -- Converting birthdate to middle of the year (June 30) for privacy/de-identification
    STR_TO_DATE(
        CONCAT(
            YEAR(p.Birthdate),  -- Keep the year
            '-06-30'            -- Set to June 30
        ),
        '%Y-%m-%d'
    ) as Birthdate,    
    p.Gender,                   -- Patient gender
    p.Zip,                      -- ZIP/Postal code
    
    -- Insurance information
    -- patplan → inssub → insplan relationship chain to get insurance plans
    COUNT(DISTINCT ins.PlanNum) as CurrentInsurancePlans,  -- Count of distinct insurance plans
    MAX(CASE WHEN ins.PlanNum IS NOT NULL THEN 1 ELSE 0 END) as HasInsurance,  -- Boolean flag (0/1) if patient has any insurance
    
    -- Payment plan information
    COUNT(DISTINCT pplan.PayPlanNum) as ActivePaymentPlans,  -- Count of payment plans for the patient
    
    -- Financial calculations
    -- Total bill amount (sum of all completed procedure fees)
    SUM(CASE WHEN pl.ProcStatus = 2 THEN pl.ProcFee ELSE 0 END) as TotalBillAmount,
    
    -- Insurance portion (sum of insurance payments and expected payments)
    SUM(COALESCE(CASE WHEN cp.Status = 1 THEN cp.InsPayAmt ELSE 0 END, 0)) as InsurancePaidAmount

FROM patient p
-- Join to get insurance information through the proper relationship chain
LEFT JOIN patplan pp ON p.PatNum = pp.PatNum                -- Link patient to insurance subscription
LEFT JOIN inssub ins ON pp.InsSubNum = ins.InsSubNum        -- Link subscription to insurance plan

-- Join to get payment plans
LEFT JOIN payplan pplan ON p.PatNum = pplan.PatNum          -- Link patient to payment plans

-- Join to get procedures and financial information
LEFT JOIN procedurelog pl ON p.PatNum = pl.PatNum 
    AND pl.ProcStatus = 2                                   -- Only include completed procedures (status = 2)
LEFT JOIN paysplit ps ON pl.ProcNum = ps.ProcNum            -- Link procedures to patient payments
LEFT JOIN claimproc cp ON pl.ProcNum = cp.ProcNum           -- Link procedures to insurance payments

-- Group by patient to get one row per patient
GROUP BY p.PatNum;
