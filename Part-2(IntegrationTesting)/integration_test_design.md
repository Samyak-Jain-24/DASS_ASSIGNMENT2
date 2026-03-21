# Integration Test Design

Each test case includes scenario, modules involved, expected result, actual result, and issues found.

## IT-01 Register driver then enter race
- Scenario: Register a crew member, assign role DRIVER, add a car, create race.
- Modules: Registration, Crew Management, Inventory, Race Management
- Expected: Race created with driver and car.
- Actual: PASS — Race created successfully
- Errors/Issues: None

## IT-02 Attempt race without registered driver
- Scenario: Create race with unregistered driver ID.
- Modules: Race Management, Registration
- Expected: Rejected; driver must exist.
- Actual: PASS — Rejected with "Driver must be registered"
- Errors/Issues: None

## IT-03 Complete race and verify cash updates
- Scenario: Create race, record result with prize money.
- Modules: Race Management, Results, Inventory
- Expected: Inventory cash increases by prize money.
- Actual: PASS — Cash increased by prize money
- Errors/Issues: None

## IT-04 Assign mission and verify required roles
- Scenario: Assign mission requiring DRIVER + MECHANIC with only DRIVER present.
- Modules: Mission Planning, Crew Management
- Expected: Mission rejected due to missing role.
- Actual: PASS — Rejected with missing role error
- Errors/Issues: None

## IT-05 Damaged car + mechanic required
- Scenario: Mark car damaged after race, create mission requiring mechanic.
- Modules: Results, Maintenance, Mission Planning
- Expected: Mission proceeds only if mechanic available.
- Actual: PASS — Mission created when mechanic available
- Errors/Issues: None
