SELECT month,COUNT(*) cases,SUM(timely='Yes') timely_yes,SUM(timely='No') timely_no,
 SUM(timely='Unknown') timely_unknown,SUM(intake_days>=0) valid_intervals,
 SUM(intake_days>:review_days) over_review_days,SUM(intake_days<0) negative_intervals,
 SUM(intake_days IS NULL) invalid_dates
FROM cases GROUP BY month ORDER BY month;
