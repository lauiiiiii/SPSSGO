-- 按文件名清理重复数据集
-- 用法：在 Docker MySQL 容器中执行
--   docker compose exec mysql mysql -u root -p spssgo < /var/lib/spssgo/scripts/cleanup_datasets_by_filename.sql
--
-- 默认清理 category_summary_sample.csv，如需清理其他文件请修改 WHERE 条件

-- 1. 先查看待清理的数据分布（只读，安全）
SELECT
    d.original_filename AS filename,
    d.owner_id,
    u.username,
    COUNT(*) AS dataset_count,
    MIN(FROM_UNIXTIME(d.created_at)) AS earliest,
    MAX(FROM_UNIXTIME(d.created_at)) AS latest
FROM datasets d
JOIN users u ON u.id = d.owner_id
WHERE d.original_filename = 'category_summary_sample.csv'
GROUP BY d.owner_id, d.original_filename;

-- 2. 查看对应的 session 数量（确认级联删除范围）
SELECT COUNT(DISTINCT s.id) AS session_count
FROM sessions s
JOIN datasets d ON d.session_id = s.id
WHERE d.original_filename = 'category_summary_sample.csv';

-- 3. 【危险操作】删除这些 session，级联删除所有关联表
--    外键级联：sessions -> datasets -> dataset_versions / dataset_folder_items
--             sessions -> results / variable_metadata
--    文件目录不会自动清理（但截图显示这些文件已经丢失，无影响）
--    执行前请务必确认上面的查询结果是你想要的！
-- DELETE FROM sessions WHERE id IN (
--     SELECT session_id FROM datasets WHERE original_filename = 'category_summary_sample.csv'
-- );
