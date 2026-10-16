-- P90 = nearest rank, using only nonnegative, parsed date intervals.
WITH ranked AS (
 SELECT channel,intake_days,
 ROW_NUMBER() OVER(PARTITION BY channel ORDER BY intake_days) rn,
 COUNT(*) OVER(PARTITION BY channel) n
 FROM cases WHERE intake_days>=0
), p90 AS (
 SELECT channel,intake_days p90_days FROM ranked WHERE rn=(9*n+9)/10
), summary AS (
 SELECT channel,COUNT(*) cases,SUM(timely='Yes') timely_yes,SUM(timely='No') timely_no,
 SUM(timely='Unknown') timely_unknown,SUM(intake_days>=0) valid_intervals,
 SUM(intake_days<0) negative_intervals,SUM(intake_days IS NULL) invalid_dates,
 SUM(intake_days>:review_days) over_review_days,
 SUM(CASE WHEN intake_days>=0 THEN intake_days ELSE 0 END) total_intake_days
 FROM cases GROUP BY channel
) SELECT summary.*,p90.p90_days FROM summary LEFT JOIN p90 USING(channel)
ORDER BY cases DESC,channel;
