-- 2.1 Знаходження моди
-- Варіант 1. Сумісний із MySQL і шукає всі можливі моди
    WITH count_freq AS (
		SELECT 
			spend,
            COUNT(*) as frequency
		FROM facebook_ad_data
		WHERE MONTH(date)=7
		GROUP BY spend)
	SELECT
		spend
	FROM count_freq
    WHERE frequency = (SELECT MAX(frequency) FROM count_freq)
    
-- Варіант 2. Не сумісний із MySQL, а працює наприклад в Postgesql, але є недолік, що знаходить тільки одну моду
	SELECT 
		MODE() WITHIN GROUP (ORDER BY spend) AS mode_spend
	FROM facebook_ad_data
	WHERE EXTRACT(MONTH FROM date) = 7;

-- 2.1 Знаходження медіани    
-- Варіант 1. Працює в Mysql із вбудованими функціями
	WITH ordered AS (
    SELECT spend,
           ROW_NUMBER() OVER (ORDER BY spend) AS rn,
           COUNT(*) OVER () AS total_count
    FROM facebook_ad_data
    WHERE MONTH(date) = 7
	)
	SELECT AVG(spend) AS median_spend
	FROM ordered
	WHERE rn IN (FLOOR((total_count + 1) / 2), CEIL((total_count + 1) / 2));
    
    -- Варіант 2. Без вбудованих функцій

	SET @r = 0;
	SET @total_count = (SELECT COUNT(*) 
						FROM facebook_ad_data 
						WHERE MONTH(date) = 7);
	SELECT 
		AVG(spend) AS median_spend
	FROM (
		SELECT 
			spend,
			@r := @r + 1 AS row_num
		FROM facebook_ad_data
		WHERE MONTH(date) = 7
		ORDER BY spend
	) AS sorted_data
	WHERE row_num IN (FLOOR((@total_count + 1) / 2), CEIL((@total_count + 1) / 2));
    
    -- 2.2 Користувачі із платною підпискою
    SELECT
		u.id AS user_id,
		u.email,
		s.original_purchase_date,
		s.subscription_name
	FROM user u
	JOIN subscription s ON u.id = s.user_id
	WHERE YEAR(u.created_at) = 2020	AND s.is_trial = 0;

    
    
    
	