SELECT n.* FROM review_notes n LEFT JOIN cases c USING(complaint_id)
WHERE c.complaint_id IS NULL ORDER BY n.complaint_id;
