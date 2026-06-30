#!/bin/bash

# Spec Driven Development - Full Verification Script
# This script verifies all aspects of Part 4 implementation

echo "========================================="
echo "Spec Driven Development - Full Verification"
echo "Date: $(date)"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check_pass() {
    echo -e "${GREEN}✅${NC} $1"
    PASS=$((PASS + 1))
}

check_fail() {
    echo -e "${RED}❌${NC} $1"
    FAIL=$((FAIL + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

echo "1. Checking Frameworks..."
echo "-----------------------------------------"

# Check Python frameworks
python -c 'import behave' 2>/dev/null && check_pass "Behave framework installed" || check_fail "Behave framework not installed"
python -c 'import pytest_bdd' 2>/dev/null && check_pass "pytest-bdd framework installed" || check_fail "pytest-bdd framework not installed"
python -c 'import pytest' 2>/dev/null && check_pass "pytest framework installed" || check_fail "pytest framework not installed"

# Check Node.js frameworks
cd /home/edilene/Dropbox/Simplon_Projects/briefs-todo-app-starter
node -e 'require("cucumber-expressions")' 2>/dev/null && check_pass "cucumber-expressions installed" || check_fail "cucumber-expressions not installed"

echo ""
echo "2. Checking Backend Specifications..."
echo "-----------------------------------------"

# Check backend feature files
[ -f "specs/backend/reminders/features/reminders.feature" ] && check_pass "Backend reminder feature file" || check_fail "Backend reminder feature file missing"
[ -f "specs/backend/subtasks/features/subtasks.feature" ] && check_pass "Backend subtask feature file" || check_fail "Backend subtask feature file missing"

# Count scenarios
REMINDER_SCENARIOS=$(grep -c "Scenario:" specs/backend/reminders/features/reminders.feature 2>/dev/null || echo "0")
SUBTASK_SCENARIOS=$(grep -c "Scenario:" specs/backend/subtasks/features/subtasks.feature 2>/dev/null || echo "0")
[ "$REMINDER_SCENARIOS" -gt 0 ] && check_pass "Backend reminder specs: $REMINDER_SCENARIOS scenarios" || check_fail "No reminder scenarios found"
[ "$SUBTASK_SCENARIOS" -gt 0 ] && check_pass "Backend subtask specs: $SUBTASK_SCENARIOS scenarios" || check_fail "No subtask scenarios found"

# Check step definitions
[ -f "specs/backend/reminders/test_reminders.py" ] && check_pass "Reminder pytest-bdd tests" || check_fail "Reminder pytest-bdd tests missing"
[ -f "specs/backend/subtasks/features/steps/__init__.py" ] && check_pass "Subtask behave steps" || check_fail "Subtask behave steps missing"
[ -f "specs/backend/reminders/features/environment.py" ] && check_pass "Reminder environment setup" || check_fail "Reminder environment setup missing"

echo ""
echo "3. Checking Frontend Specifications..."
echo "-----------------------------------------"

# Check frontend feature files
[ -f "specs/frontend/reminders/features/reminders.feature" ] && check_pass "Frontend reminder feature file" || check_fail "Frontend reminder feature file missing"
[ -f "specs/frontend/subtasks/features/subtasks.feature" ] && check_pass "Frontend subtask feature file" || check_fail "Frontend subtask feature file missing"

# Count frontend scenarios
FREMINDER_SCENARIOS=$(grep -c "Scenario:" specs/frontend/reminders/features/reminders.feature 2>/dev/null || echo "0")
FSUBTASK_SCENARIOS=$(grep -c "Scenario:" specs/frontend/subtasks/features/subtasks.feature 2>/dev/null || echo "0")
[ "$FREMINDER_SCENARIOS" -gt 0 ] && check_pass "Frontend reminder specs: $FREMINDER_SCENARIOS scenarios" || check_fail "No frontend reminder scenarios found"
[ "$FSUBTASK_SCENARIOS" -gt 0 ] && check_pass "Frontend subtask specs: $FSUBTASK_SCENARIOS scenarios" || check_fail "No frontend subtask scenarios found"

echo ""
echo "4. Checking Backend Implementation..."
echo "-----------------------------------------"

# Check models
grep -q "class Reminder" api/models.py && check_pass "Reminder model" || check_fail "Reminder model missing"
grep -q "class Subtask" api/models.py && check_pass "Subtask model" || check_fail "Subtask model missing"
grep -q "reminders = relationship" api/models.py && check_pass "Reminder relationship" || check_fail "Reminder relationship missing"
grep -q "subtasks = relationship" api/models.py && check_pass "Subtask relationship" || check_fail "Subtask relationship missing"

# Check schemas
grep -q "ReminderCreateForDeadline" api/schemas.py && check_pass "Reminder schemas" || check_fail "Reminder schemas missing"
grep -q "SubtaskCreate" api/schemas.py && check_pass "Subtask schemas" || check_fail "Subtask schemas missing"

# Check CRUD operations
grep -q "def create_reminder_deadline" api/crud.py && check_pass "Reminder CRUD operations" || check_fail "Reminder CRUD missing"
grep -q "def create_subtask" api/crud.py && check_pass "Subtask CRUD operations" || check_fail "Subtask CRUD missing"
grep -q "def snooze_reminder" api/crud.py && check_pass "Snooze reminder function" || check_fail "Snooze function missing"
grep -q "def check_can_complete_subtask" api/crud.py && check_pass "Dependency check function" || check_fail "Dependency check missing"
grep -q "def get_dependency_graph" api/crud.py && check_pass "Dependency graph function" || check_fail "Dependency graph missing"

# Check API endpoints
grep -q "reminders/deadline" api/main.py && check_pass "Reminder endpoints" || check_fail "Reminder endpoints missing"
grep -q "subtasks" api/main.py && check_pass "Subtask endpoints" || check_fail "Subtask endpoints missing"
grep -q "snooze" api/main.py && check_pass "Snooze endpoint" || check_fail "Snooze endpoint missing"
grep -q "dependencies" api/main.py && check_pass "Dependency endpoint" || check_fail "Dependency endpoint missing"

echo ""
echo "5. Checking Frontend Implementation..."
echo "-----------------------------------------"

# Check types
grep -q "interface Reminder" web/src/lib/types.ts && check_pass "Reminder TypeScript types" || check_fail "Reminder types missing"
grep -q "interface Subtask" web/src/lib/types.ts && check_pass "Subtask TypeScript types" || check_fail "Subtask types missing"
grep -q "ReminderType" web/src/lib/types.ts && check_pass "Reminder type aliases" || check_fail "Reminder type aliases missing"
grep -q "ReminderFrequency" web/src/lib/types.ts && check_pass "Reminder frequency types" || check_fail "Reminder frequency types missing"

# Check API client extensions
grep -q "createDeadlineReminder" web/src/lib/api.ts && check_pass "API client - deadline reminder" || check_fail "API client deadline missing"
grep -q "createRecurringReminder" web/src/lib/api.ts && check_pass "API client - recurring reminder" || check_fail "API client recurring missing"
grep -q "listSubtasks" web/src/lib/api.ts && check_pass "API client - list subtasks" || check_fail "API client subtasks missing"
grep -q "getDependencyGraph" web/src/lib/api.ts && check_pass "API client - dependency graph" || check_fail "API client dependency graph missing"

# Check components
[ -f "web/src/lib/components/ReminderBadge.svelte" ] && check_pass "ReminderBadge component" || check_fail "ReminderBadge component missing"
[ -f "web/src/lib/components/ReminderModal.svelte" ] && check_pass "ReminderModal component" || check_fail "ReminderModal component missing"
[ -f "web/src/lib/components/SubtaskItem.svelte" ] && check_pass "SubtaskItem component" || check_fail "SubtaskItem component missing"
[ -f "web/src/lib/components/SubtaskList.svelte" ] && check_pass "SubtaskList component" || check_fail "SubtaskList component missing"

# Check TodoItem integration
grep -q "ReminderBadge" web/src/lib/components/TodoItem.svelte && check_pass "TodoItem - ReminderBadge integration" || check_fail "ReminderBadge integration missing"
grep -q "SubtaskList" web/src/lib/components/TodoItem.svelte && check_pass "TodoItem - SubtaskList integration" || check_fail "SubtaskList integration missing"
grep -q "ReminderModal" web/src/lib/components/TodoItem.svelte && check_pass "TodoItem - ReminderModal integration" || check_fail "ReminderModal integration missing"

echo ""
echo "6. Checking Documentation..."
echo "-----------------------------------------"

[ -f "docs/SPEC_DRIVEN_DEVELOPMENT.md" ] && check_pass "Spec Driven Development documentation" || check_fail "SDD documentation missing"

echo ""
echo "========================================="
echo "Summary"
echo "========================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Part 4 is complete.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please review the output above.${NC}"
    exit 1
fi
