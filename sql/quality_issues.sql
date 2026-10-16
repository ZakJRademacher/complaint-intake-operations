SELECT source_row,complaint_id,'Invalid complaint ID' issue FROM selected WHERE complaint_id IS NULL
UNION ALL
SELECT source_row,complaint_id,'Conflicting complaint ID' issue FROM selected WHERE complaint_id IN
 (SELECT complaint_id FROM selected WHERE complaint_id IS NOT NULL GROUP BY complaint_id HAVING COUNT(DISTINCT fingerprint)>1)
UNION ALL
SELECT source_row,complaint_id,CASE WHEN intake_days<0 THEN 'Sent before received' ELSE 'Unparseable date' END
FROM cases WHERE intake_days<0 OR intake_days IS NULL;
