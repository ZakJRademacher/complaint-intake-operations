SELECT c.complaint_id,c.product,c.received,c.sent,c.intake_days,
 trim(CASE WHEN c.intake_days<0 THEN 'Date order; ' WHEN c.intake_days IS NULL THEN 'Invalid date; ' ELSE '' END ||
 CASE WHEN c.intake_days>:review_days THEN 'Routing review; ' ELSE '' END ||
 CASE WHEN c.timely='No' THEN 'Source timely=No; ' WHEN c.timely='Unknown' THEN 'Unknown timely flag; ' ELSE '' END,'; ') review_reason,
 COALESCE(n.owner,'') owner,COALESCE(n.review_status,'Not started') review_status,COALESCE(n.notes,'') notes
FROM cases c LEFT JOIN review_notes n USING(complaint_id)
WHERE c.intake_days<0 OR c.intake_days IS NULL OR c.intake_days>:review_days OR c.timely!='Yes'
ORDER BY CASE WHEN c.intake_days>=0 THEN 0 ELSE 1 END,c.intake_days DESC,c.complaint_id;
