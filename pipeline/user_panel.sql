CREATE OR REPLACE TABLE `playperfect-432410.game_events.user_panel`
AS
WITH raw_data AS (
    SELECT
        player_id,
        timestamp_utc,
        country,
        deposit_amount,
        tournament_score
    FROM
        `playperfect-432410.game_events.raw_events`
),

-- Calculate the last country the player was seen in
last_country AS (
    SELECT
        player_id,
        country,
        ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY timestamp_utc DESC) as row_num
    FROM
        raw_data
    WHERE
        country IS NOT NULL
),

-- Calculate the average of the last 10 deposit amounts
avg_price_10 AS (
    SELECT
        player_id,
        AVG(deposit_amount) AS avg_price_10
    FROM (
        SELECT
            player_id,
            deposit_amount,
            ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY timestamp_utc DESC) as row_num
        FROM
            raw_data
        WHERE
            deposit_amount IS NOT NULL
    )
    WHERE
        row_num <= 10
    GROUP BY
        player_id
),

-- Calculate the weighted daily tournament score for the last 10 active days
weighted_daily_matches AS (
    SELECT
        player_id,
        SUM(matches_count * weight) / SUM(weight) AS last_weighted_daily_matches_count_10_played_days
    FROM (
        SELECT
            player_id,
            COUNT(*) AS matches_count,
            DENSE_RANK() OVER (PARTITION BY player_id ORDER BY event_date DESC) AS day_rank,
            ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY event_date DESC) AS day_row_num,
            11 - DENSE_RANK() OVER (PARTITION BY player_id ORDER BY event_date DESC) AS weight
        FROM (
            SELECT
                player_id,
                DATE(timestamp_utc) AS event_date
            FROM
                raw_data
            WHERE
                tournament_score IS NOT NULL
        ) AS sub_query1
        GROUP BY
            player_id,
            event_date
    ) AS sub_query2
    WHERE
        day_rank <= 10
    GROUP BY
        player_id
),

-- Calculate the number of active days since the last deposit
active_days_since_last_purchase AS (
    SELECT
        player_id,
        COUNT(DISTINCT DATE(timestamp_utc)) - 1 AS active_days_since_last_purchase
    FROM
        raw_data rd
    WHERE
        DATE(timestamp_utc) > (
            SELECT
                MAX(DATE(timestamp_utc))
            FROM
                raw_data
            WHERE
                deposit_amount IS NOT NULL
                AND player_id = rd.player_id
        )
    GROUP BY
        player_id
),

-- Calculate the median tournament score over the last 5 calendar days
score_perc_50_last_5_days AS (
    SELECT
        player_id,
        APPROX_QUANTILES(tournament_score, 2)[OFFSET(1)] AS score_perc_50_last_5_days
    FROM (
        SELECT
            player_id,
            tournament_score,
            DENSE_RANK() OVER (PARTITION BY player_id ORDER BY DATE(timestamp_utc) DESC) AS day_rank
        FROM
            raw_data
        WHERE
            tournament_score IS NOT NULL
    )
    WHERE
        day_rank <= 5
    GROUP BY
        player_id
)

-- Final table combining all calculated metrics
SELECT
    lc.player_id,
    lc.country,
    ap.avg_price_10,
    wdm.last_weighted_daily_matches_count_10_played_days,
    adslp.active_days_since_last_purchase,
    sp.score_perc_50_last_5_days
FROM
    last_country lc
LEFT JOIN
    avg_price_10 ap ON lc.player_id = ap.player_id
LEFT JOIN
    weighted_daily_matches wdm ON lc.player_id = wdm.player_id
LEFT JOIN
    active_days_since_last_purchase adslp ON lc.player_id = adslp.player_id
LEFT JOIN
    score_perc_50_last_5_days sp ON lc.player_id = sp.player_id
GROUP BY
    lc.player_id,
    lc.country,
    ap.avg_price_10,
    wdm.last_weighted_daily_matches_count_10_played_days,
    adslp.active_days_since_last_purchase,
    sp.score_perc_50_last_5_days;
