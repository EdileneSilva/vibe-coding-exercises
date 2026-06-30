# language: en
Feature: Frontend Reminder System
  As a todo application user
  I want to interact with reminders in the UI
  So I can manage my task deadlines effectively

  Background:
    Given the frontend application is running

  Scenario: View reminders on a todo
    Given I have a todo with id 1 titled "Submit report"
    And todo 1 has a deadline reminder for "2026-07-01T10:00:00"
    When I view the todo list
    Then I should see todo 1 with a reminder badge
    And the badge should display "Jul 1, 10:00 AM"

  Scenario: Add a deadline reminder via UI
    Given I have a todo with id 1 titled "Submit report"
    When I click on the reminder icon for todo 1
    And I select "Add Deadline Reminder"
    And I set the date to "2026-07-01"
    And I set the time to "10:00"
    And I select notification channels "email, in_app"
    And I click "Save"
    Then todo 1 should have a deadline reminder
    And the reminder should have deadline "2026-07-01T10:00:00"

  Scenario: Add a recurring reminder via UI
    Given I have a todo with id 1 titled "Weekly review"
    When I click on the reminder icon for todo 1
    And I select "Add Recurring Reminder"
    And I select frequency "weekly"
    And I select notification channel "in_app"
    And I click "Save"
    Then todo 1 should have a recurring reminder
    And the reminder should have frequency "weekly"

  Scenario: View approaching reminders
    Given I have a todo with id 1 titled "Task A" with deadline "2026-06-27T10:00:00"
    And I have a todo with id 2 titled "Task B" with deadline "2026-07-01T10:00:00"
    And I have a todo with id 3 titled "Task C" with no reminder
    When I filter todos by "Approaching"
    Then I should see todo 1 in the filtered list
    And I should not see todo 2 in the filtered list
    And I should not see todo 3 in the filtered list

  Scenario: View overdue reminders
    Given I have a todo with id 1 titled "Task A" with deadline "2026-06-25T10:00:00"
    And I have a todo with id 2 titled "Task B" with deadline "2026-07-01T10:00:00"
    When I filter todos by "Overdue"
    Then I should see todo 1 marked as "overdue"
    And I should not see todo 2 in the filtered list

  Scenario: Snooze a reminder via UI
    Given I have a todo with id 1 titled "Submit report"
    And todo 1 has a deadline reminder for "2026-06-26T15:00:00"
    When I click the snooze button for todo 1's reminder
    And I select "1 hour"
    Then the reminder deadline should be updated to "2026-06-26T16:00:00"

  Scenario: Delete a reminder via UI
    Given I have a todo with id 1 titled "Submit report"
    And todo 1 has a deadline reminder
    When I click the delete button for todo 1's reminder
    And I confirm the deletion
    Then todo 1 should have no reminders

  Scenario: See reminder notification in UI
    Given I have a todo with id 1 titled "Important meeting"
    And todo 1 has a deadline reminder for "2026-06-26T15:00:00"
    And the current time is "2026-06-26T14:30:00"
    When the reminder triggers
    Then I should see a notification in the UI
    And the notification should say "Reminder: Important meeting is due in 30 minutes"
