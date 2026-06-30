# language: en
Feature: Reminder System
  As a todo application user
  I want to set reminders on my todos
  So I don't forget important deadlines

  Background:
    Given the API is running

  Scenario: Set a deadline reminder on a todo
    Given I have a todo with id 1 titled "Submit report"
    When I set a deadline reminder for "2026-07-01T10:00:00" on todo 1
    Then todo 1 should have a reminder with deadline "2026-07-01T10:00:00"
    And the reminder type should be "deadline"

  Scenario: Set a recurring reminder
    Given I have a todo with id 1 titled "Weekly review"
    When I set a recurring reminder with frequency "weekly" on todo 1
    Then todo 1 should have a reminder with frequency "weekly"
    And the reminder should repeat every 7 days

  Scenario: Set reminder with notification channel
    Given I have a todo with id 1 titled "Important meeting"
    When I set a reminder with channel "email" on todo 1
    And I set a reminder with channel "in_app" on todo 1
    Then todo 1 should have 2 reminder notifications
    And the channels should be "email, in_app"

  Scenario: Trigger reminder when deadline is approaching
    Given I have a todo with id 1 titled "Submit report"
    And todo 1 has a deadline reminder for "2026-07-01T10:00:00"
    When the current time is "2026-06-30T09:00:00"
    Then the reminder should be in "approaching" state
    And the time remaining should be "25 hours"

  Scenario: Trigger reminder when deadline is passed
    Given I have a todo with id 1 titled "Submit report"
    And todo 1 has a deadline reminder for "2026-06-25T10:00:00"
    When the current time is "2026-06-30T10:00:00"
    Then the reminder should be in "overdue" state
    And the todo should be marked as "overdue"

  Scenario: Recurring reminder creates new instances
    Given I have a todo with id 1 titled "Weekly review"
    And todo 1 has a recurring reminder with frequency "daily"
    When I check reminders for the next 3 days
    Then there should be 3 reminder instances
    And each instance should be 1 day apart

  Scenario: Remove a reminder
    Given I have a todo with id 1 titled "Submit report"
    And todo 1 has a deadline reminder for "2026-07-01T10:00:00"
    When I remove the reminder from todo 1
    Then todo 1 should have 0 reminders

  Scenario: Update reminder settings
    Given I have a todo with id 1 titled "Submit report"
    And todo 1 has a deadline reminder for "2026-07-01T10:00:00"
    When I update the reminder deadline to "2026-07-02T15:00:00"
    Then todo 1 should have a reminder with deadline "2026-07-02T15:00:00"

  Scenario: Snooze a reminder
    Given I have a todo with id 1 titled "Submit report"
    And todo 1 has a deadline reminder for "2026-06-26T15:00:00"
    When I snooze the reminder for 1 hour
    Then the reminder deadline should be "2026-06-26T16:00:00"

  Scenario: Get all todos with approaching reminders
    Given I have a todo with id 1 titled "Task A" with deadline "2026-06-27T10:00:00"
    And I have a todo with id 2 titled "Task B" with deadline "2026-07-01T10:00:00"
    And I have a todo with id 3 titled "Task C" with no reminder
    When I request todos with reminders due within 48 hours
    Then the result should include todo 1
    And the result should not include todo 2
    And the result should not include todo 3
