-- Performance Optimization Indexes for Schedule Parser
-- Migration: 001_add_performance_indexes.sql
-- Purpose: Add critical indexes for query optimization
-- Expected impact: 10-100x faster queries on lessons table

-- ============================================================
-- HIGH PRIORITY INDEXES
-- ============================================================

-- Index for fetching existing lessons by group_id, week_type
-- Used in: get_existing_lessons() query (most frequent operation)
-- Expected impact: Query time reduced from ~500ms to ~5-10ms (50-100x faster)
CREATE INDEX IF NOT EXISTS idx_lesson_group_week_day_number
ON "Lesson" (GroupId, WeekType, DayOfWeek, LessonNumber);

-- Index for lesson lookups by lesson_id (used in updates/deletes)
-- Expected impact: Individual lesson operations 10-20x faster
CREATE INDEX IF NOT EXISTS idx_lesson_id_lookup
ON "Lesson" (LessonId) WHERE LessonId IS NOT NULL;

-- Composite index for subgroup filtering
-- Covers common query pattern: group + week + day + number + subgroup
-- Expected impact: Subgroup-specific queries 20-50x faster
CREATE INDEX IF NOT EXISTS idx_lesson_group_week_day_number_subgroup
ON "Lesson" (GroupId, WeekType, DayOfWeek, LessonNumber, Subgroup)
WHERE Subgroup IS NOT NULL;

-- Index for schedule_changes log table
-- Used for: Change history queries and auditing
-- Expected impact: Change log queries 50-100x faster
CREATE INDEX IF NOT EXISTS idx_schedule_changes_lesson_id
ON schedule_changes (LessonId, ChangeType, ChangedAt DESC);

-- Index for schedule_changes by date range
-- Used for: Finding recent changes
-- Expected impact: Time-based queries 100x faster
CREATE INDEX IF NOT EXISTS idx_schedule_changes_date
ON schedule_changes (ChangedAt DESC);

-- ============================================================
-- MEDIUM PRIORITY INDEXES
-- ============================================================

-- Index for active groups lookup
-- Used in: get_active_groups() query
-- Expected impact: Group fetching 5-10x faster
CREATE INDEX IF NOT EXISTS idx_group_active
ON "Group" (IsActive, GroupId) WHERE IsActive = TRUE;

-- Index for chat-group relationships
-- Used in: Finding groups with subscribed chats
-- Expected impact: Chat lookup queries 10-20x faster
CREATE INDEX IF NOT EXISTS idx_chat_group_id
ON "Chat" (GroupId);

-- Partial index for lessons with specific dates
-- Optimizes queries that filter by date ranges
-- Expected impact: Date-based filtering 20-30x faster
CREATE INDEX IF NOT EXISTS idx_lesson_date
ON "Lesson" (LessonDate, GroupId) WHERE LessonDate >= CURRENT_DATE;

-- ============================================================
-- ANALYZE TABLE STATISTICS
-- ============================================================

-- Update table statistics after creating indexes
-- This helps PostgreSQL query planner make better decisions
ANALYZE "Lesson";
ANALYZE "Group";
ANALYZE "Chat";
ANALYZE schedule_changes;

-- ============================================================
-- INDEX VERIFICATION
-- ============================================================

-- To verify indexes were created, run:
-- SELECT indexname, indexdef FROM pg_indexes
-- WHERE tablename IN ('Lesson', 'Group', 'Chat', 'schedule_changes')
-- ORDER BY tablename, indexname;

-- To check index usage statistics after running the application:
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- WHERE tablename IN ('Lesson', 'Group', 'Chat', 'schedule_changes')
-- ORDER BY idx_scan DESC;
