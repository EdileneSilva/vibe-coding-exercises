# language: en
Feature: Frontend Sub-tasks and Dependencies
  As a todo application user
  I want to manage subtasks with dependencies in the UI
  So I can break down complex tasks and track dependencies

  Background:
    Given the frontend application is running

  Scenario: View subtasks for a todo
    Given I have a todo titled "Complete project"
    And I have added subtasks "Design database, Implement API, Write tests" to the todo
    When I expand the todo
    Then I should see 3 subtasks listed
    And the subtasks should be "Design database", "Implement API", "Write tests"

  Scenario: Add a subtask via UI
    Given I have a todo titled "Complete project"
    When I click on the todo
    And I click "Add Subtask"
    And I enter title "Design database"
    And I click "Save"
    Then the todo should have 1 subtask
    And the subtask should have title "Design database"

  Scenario: Mark subtask as completed
    Given I have a todo titled "Complete project"
    And I have added subtask "Design database" to the todo
    When I click the checkbox for subtask "Design database"
    Then subtask "Design database" should have status "completed"
    And the todo should show progress "1/1 subtasks completed"

  Scenario: Parent todo status reflects subtask completion
    Given I have a todo titled "Complete project"
    And I have added subtasks "Task A, Task B" to the todo
    When I mark subtask "Task A" as completed
    Then the todo should have status "in_progress"
    And the progress should show "1/2 subtasks completed"
    When I mark subtask "Task B" as completed
    Then the todo should have status "completed"
    And the progress should show "2/2 subtasks completed"

  Scenario: Create dependency between subtasks
    Given I have a todo titled "Complete project"
    And I have added subtask "Design database" to the todo
    And I have added subtask "Implement API" to the todo
    When I click the dependency icon for subtask "Implement API"
    And I select "Blocked by"
    And I select "Design database"
    Then subtask "Implement API" should show "Blocked by: Design database"
    And subtask "Design database" should show "Blocks: Implement API"

  Scenario: Cannot complete blocked subtask
    Given I have a todo titled "Complete project"
    And I have added subtask "Design database" to the todo
    And I have added subtask "Implement API" to the todo
    And subtask "Implement API" is blocked by "Design database"
    When I try to mark subtask "Implement API" as completed
    Then I should see an error message
    And the error should say "Cannot complete: blocked by incomplete subtask 'Design database'"
    And subtask "Implement API" should remain "pending"

  Scenario: View dependency graph visualization
    Given I have a todo titled "Complete project"
    And I have added subtask "A" to the todo
    And I have added subtask "B" to the todo
    And I have added subtask "C" to the todo
    And subtask "B" is blocked by "A"
    And subtask "C" is blocked by "B"
    When I click "View Dependencies" for the todo
    Then I should see a dependency graph
    And the graph should show "A -> B -> C"

  Scenario: Delete a subtask
    Given I have a todo titled "Complete project"
    And I have added subtasks "Task A, Task B" to the todo
    When I click the delete button for subtask "Task A"
    And I confirm the deletion
    Then the todo should have 1 subtask
    And the remaining subtask should be "Task B"

  Scenario: Update subtask details
    Given I have a todo titled "Complete project"
    And I have added subtask "Task A" to the todo
    When I click the edit button for subtask "Task A"
    And I change the title to "Updated Task A"
    And I change the description to "New description"
    And I click "Save"
    Then subtask "Updated Task A" should have title "Updated Task A"
    And subtask "Updated Task A" should have description "New description"

  Scenario: View subtask details in a modal
    Given I have a todo titled "Complete project"
    And I have added subtask "Design database" with description "Create schema" to the todo
    When I click on subtask "Design database"
    Then I should see a modal with subtask details
    And the modal should show title "Design database"
    And the modal should show description "Create schema"
