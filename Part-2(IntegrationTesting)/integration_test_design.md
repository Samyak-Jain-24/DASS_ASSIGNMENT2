# Integration Test Design

Each test case includes scenario, modules involved, expected result, actual result, and issues found.

## IT-01 Register driver then enter race
- Scenario: Register a crew member, assign role DRIVER, add a car, create race.
- Modules: Registration, Crew Management, Inventory, Race Management
- Expected: Race created with driver and car.
- Actual: PASS — Race created successfully
- Errors/Issues: None
- Rationale: Validates cross-module flow from registration → role assignment → car inventory → race creation.

## IT-02 Attempt race without registered driver
- Scenario: Create race with unregistered driver ID.
- Modules: Race Management, Registration
- Expected: Rejected; driver must exist.
- Actual: PASS — Rejected with "Driver must be registered"
- Errors/Issues: None
- Rationale: Ensures race management enforces registration dependency.

## IT-03 Complete race and verify cash updates
- Scenario: Create race, record result with prize money.
- Modules: Race Management, Results, Inventory
- Expected: Inventory cash increases by prize money.
- Actual: PASS — Cash increased by prize money
- Errors/Issues: None
- Rationale: Confirms results module updates inventory cash as required.

## IT-04 Assign mission and verify required roles
- Scenario: Assign mission requiring DRIVER + MECHANIC with only DRIVER present.
- Modules: Mission Planning, Crew Management
- Expected: Mission rejected due to missing role.
- Actual: PASS — Rejected with missing role error
- Errors/Issues: None
- Rationale: Validates mission planning enforces role availability.

## IT-05 Damaged car + mechanic required
- Scenario: Mark car damaged after race, create mission requiring mechanic.
- Modules: Results, Maintenance, Mission Planning
- Expected: Mission proceeds only if mechanic available.
- Actual: PASS — Mission created when mechanic available
- Errors/Issues: None
- Rationale: Ensures damaged-car workflows enforce mechanic presence.

## IT-06 Repair damaged car consumes spare parts
- Scenario: Damage a car, add spare parts, then repair using mechanic.
- Modules: Maintenance, Inventory, Crew Management
- Expected: Repair succeeds and spare parts decrement by 1.
- Actual: PASS — Repair completed and spare parts reduced
- Errors/Issues: None
- Rationale: Validates repair process integrates inventory and mechanic role.

## IT-07 Reputation updates after race success
- Scenario: Record race result and increase reputation for the driver.
- Modules: Results, Reputation
- Expected: Driver reputation increases by delta.
- Actual: PASS — Reputation increased
- Errors/Issues: None
- Rationale: Confirms cross-module update to rankings after results.
