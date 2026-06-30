# language: en
Feature: Sub-tasks and Dependencies
  As a todo application user
  I want to break down tasks into subtasks with dependencies
  So I can better organize and track complex work

  Background:
    Given the API is running at "http://localhost:8000"

  Scenario: Create a todo with subtasks
    Given I have a todo titled "Complete project"
    When I add a subtask "Design database" to the todo
    And I add a subtask "Implement API" to the todo
    And I add a subtask "Write tests" to the todo
    Then the todo should have 3 subtasks
    And the subtasks should be "Design database", "Implement API", "Write tests"

  Scenario: Subtask has status independent of parent
    Given I have a todo titled "Complete project"
    And I have added subtasks "Task A, Task B" to the todo
    When I mark subtask "Task A" as completed
    Then subtask "Task A" should have status "completed"
    And subtask "Task B" should have status "pending"
    And the todo should have status "in_progress" (1 of 2 subtasks completed)

  Scenario: Parent todo completion depends on all subtasks
    Given I have a todo titled "Complete project"
    And I have added subtasks "Task A, Task B" to the todo
    When I mark subtask "Task A" as completed
    And I mark subtask "Task B" as completed
    Then the todo should have status "completed"

  Scenario: Create subtask with dependency
    Given I have a todo titled "Complete project"
    And I have added subtask "Design database" to the todo
    And I have added subtask "Implement API" to the todo
    When I set subtask "Implement API" to depend on "Design database" (blocked by)
    Then subtask "Implement API" should have dependency "blocked_by" pointing to "Design database"
    And subtask "Design database" should have dependency "blocks" pointing to "Implement API"

  Scenario: Cannot complete subtask with unmet dependencies
    Given I have a todo titled "Complete project"
    And I have added subtask "Design database" to the todo
    And I have added subtask "Implement API" to the todo
    And subtask "Implement API" is blocked by "Design database"
    When I try to mark subtask "Implement API" as completed
    Then the operation should fail with error "Cannot complete: blocked by incomplete subtask 'Design database'"

  Scenario: View dependency graph
    Given I have a todo titled "Complete project"
    And I have added subtask "A" to the todo
    And I have added subtask "B" to the todo
    And I have added subtask "C" to the todo
    And subtask "B" is blocked by "A"
    And subtask "C" is blocked by "B"
    When I request the dependency graph for the todo
    Then the graph should show "A" -> "B" -> "C"

  Scenario: Delete subtask
    Given I have a todo titled "Complete project"
    And I have added subtasks "Task A, Task B" to the todo
    When I delete subtask "Task A"
    Then the todo should have 1 subtask
    And the remaining subtask should be "Task B"

  Scenario: Update subtask details
    Given I have a todo titled "Complete project"
    And I add a subtask "Task A" to the todo
    When I set subtask "Task A" description to "Original description"
    And I update subtask "Task A" with new title "Updated Task A" and description "New description"
    Then subtask "Updated Task A" should have title "Updated Task A"
    And subtask "Updated Task A" should have description "New description"
