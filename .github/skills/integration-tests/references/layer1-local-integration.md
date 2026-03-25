# Layer 1: Local Integration Tests

**Goal:** "Let the layer1 Integration Tests be successfully compiled and passed locally"

1. **DO integration tests** to verify that different components interact correctly, focusing on data exchange and interface connections. 
2. **DO write** comprehensive integration tests using containers to simulate all migrated dependencies, **especially Azure services**. 
3. **DO prepare** the local environemnt for IT
4. **DO run** these tests to check the pass result.
5. **DO fix all errors** till all of the added integration tests passed.
6. **NEVER modify application source code** to fix TestContainers or Docker compatibility issues.
7. **DO generate** standardized runner scripts following the convention in the main skill file.

**Principle:**
1. **Test application code, not the SDK.** Always instantiate and invoke the project's own classes. Never call third-party library APIs directly in the test.

2. **Make untestable code testable with minimal, safe source changes.** If production code cannot be invoked from a test, introduce the smallest possible change (e.g., adding a method, widening visibility, extracting a parameter) to enable it. Never alter existing behavior, signatures, or control flow. Never work around untestable code by re-implementing its logic in the test.

3. **Wire the full execution path and test the coordinator layer that combines multiple components with real dependencies.** Tests must exercise the end-to-end flow from input through business logic to output, not individual layers in isolation. Verify the multi-step integration delivers the business outcome, not just that SDK methods execute.

4. **Assert on behavior, not structure.** Verify correct values, side effects, and state transitions — not just that a result is non-null or non-empty, nor rely on string containment or format checks alone. 

5. **Only set up what the test uses.** Every configured property, container, or singleton in setUp must be exercised by the test. Remove dead setup.

6. **Test error handling at the application level.** Verify the application's catch blocks, fallbacks, and graceful degradation — not just that the SDK throws exceptions.

7. **Cover downstream consumers.** If the migrated code produces output consumed by other components (config generators, report builders), test those consumers too. Verify output is consumable by the next component in the pipeline — write then read back through the real consumer API to confirm round-trip correctness.

8. **Only label tests as IT if they integrate external systems.** Tests with no containers, network, or filesystem dependencies are unit tests, which is not within the IT scope. Do not generate it alongside integration tests.

9. **Stay scoped to the migration target.** Only generate tests for code that uses the migrated service. Do not generate unrelated tests for general project utilities.

10. **DO use `L1IT` as the class name suffix** for all Layer 1 test classes (e.g., `BlobStorageL1IT`, `OrderServiceL1IT`).

11. **DO annotate every test class with a `Layer1` tag/category** so runner scripts can filter precisely. See the Test Isolation Convention in the main skill file for the exact annotation per language/framework.

## Prerequisites

- Docker installed and running
- TestContainers library available for the project's language

## Workflow

### 1. Analyze Application Dependencies

Scan the application to identify ALL components that need containers:

| Component Type | TestContainers Module | Priority |
|---------------|----------------------|----------|
| Azure Storage | `testcontainers-azure` | High |
| Azure Service Bus | `testcontainers-azure` | High |
| Azure Event Hubs | `testcontainers-azure` | High |
| Azure Cosmos DB| `testcontainers-azure` | High |
| SQL Server | `testcontainers-mssql` | High |
| PostgreSQL | `testcontainers-postgresql` | High |
| MySQL | `testcontainers-mysql` | High |
| MongoDB | `testcontainers-mongodb` | High |
| Redis | `testcontainers-redis` | Medium |
| RabbitMQ | `testcontainers-rabbitmq` | Medium |
| Kafka | `testcontainers-kafka` | Medium |
| Elasticsearch | `testcontainers-elasticsearch` | Medium |
| SMTP | MailHog/Papercut container | Low |


#### Code References

Service Bus **is supported** by test containers. Code reference see [./serverbus-testcontainers.md](./servicebus-testcontainers-java.md) 

### 2. Set Up TestContainers

1. Add the `org.testcontainers:testcontainers-azure` dependency with proper version that match the project dependency and the local operation system.
2. Set up test containers before testing

### 3. Create Multi-Scenario Tests

For each endpoint/feature, create tests covering:

| Scenario Type | Description | Example |
|--------------|-------------|---------|
| Happy path | Normal successful operation | Create user with valid data |
| Validation errors | Invalid input handling | Missing required fields |
| Edge cases | Boundary conditions | Empty lists, max values |
| Error conditions | Expected failures | Duplicate keys, not found |
| Concurrent access | Race conditions | Simultaneous updates |

### 4. Run Tests

Execute the newly added integration tests using the appropriate test command for your project type and build system:

- **Identify the test runner**: Use the project's standard test execution command (e.g., `dotnet test` for .NET, `mvn test` for Maven, `./gradlew test` for Gradle)
- **Target Layer 1 tests specifically**: Use the `Layer1` tag/category filter (e.g., `mvn verify -Dgroups=Layer1`, `dotnet test --filter Category=Layer1`, `pytest -m layer1`) to ensure only Layer 1 tests are executed and no other layer's tests are triggered
- **Ensure Docker is running**: Verify that Docker is accessible since TestContainers requires it for spinning up dependency containers
- **Run in the correct directory**: Execute from the project root or the specific test project directory where integration tests were created
- **Generate runner scripts**: Follow the Standardized Runner Scripts section in the main skill file to generate `run-layer1-tests.sh` and `run-layer1-tests.ps1` in the `{modernization-work-folder}` directory.

### 5. Analyze Results

Apply the **Test vs Source Code Decision Framework** from the main skill file to determine appropriate fixes:

| Result | Analysis | Action |
|--------|----------|--------|
| All pass | Tests successful | Proceed to Layer 2 |
| Test failures | Apply decision framework | Fix source code OR test code based on analysis |
| Container failures | Infrastructure issue | Check Docker, fix container config |
| Timeout errors | Resource/timing issue | Increase timeouts, check resource limits, or fix source code performance |

## Pass Criteria

- Setup necessary local environment prerequisites to run the integration tests
- All integration tests run successfully and all pass
- Each endpoint has at least 3 test scenarios
- All external dependencies are containerized
- No hardcoded connection strings or configs
- Tests are repeatable and isolated
- Runner scripts generated per the Standardized Runner Scripts convention in the main skill file