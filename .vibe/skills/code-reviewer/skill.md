# Code Reviewer Skill

**Auto-triggered Skill for Code Review and Quality Analysis**

This skill is automatically triggered when the user requests code reviews, mentions pull requests, or discusses code quality. It provides specialized assistance for analyzing code, identifying issues, and suggesting improvements.

---

## 🎯 Purpose

The `code-reviewer` skill provides specialized assistance for:
- Analyzing code for quality, security, and performance issues
- Reviewing pull requests and changesets
- Identifying code smells and anti-patterns
- Suggesting improvements and refactoring opportunities
- Enforcing project conventions and best practices
- Automating code review workflows
- Providing educational feedback on code quality

---

## 🔍 Trigger Patterns

This skill activates when the user message contains:

### Primary Triggers (High Confidence)
- "code review"
- "review my code"
- "pull request"
- "PR"
- "review changes"
- "check my code"
- "analyze code"
- "code quality"
- "lint"
- "linter"
- "best practices"
- "improve code"
- "refactor"

### Secondary Triggers (Medium Confidence)
- "merge"
- "commit"
- "changes"
- "diff"
- "patch"
- "bug"
- "issue"
- "fix"
- "improve"
- "optimize"
- "clean code"

### Contextual Triggers
- User shares code snippets
- User mentions specific files with changes
- User asks about code structure or architecture
- User discusses testing or test coverage

---

## 🚀 Capabilities

### Static Analysis
- Identify syntax errors and potential bugs
- Detect security vulnerabilities (SQL injection, XSS, etc.)
- Find performance bottlenecks
- Check for memory leaks and resource issues
- Analyze code complexity (cyclomatic, cognitive)
- Identify code smells and anti-patterns

### Code Quality
- Enforce project coding conventions
- Check for consistent code style
- Identify duplication (DRY violations)
- Suggest better naming conventions
- Improve code readability
- Check for proper error handling

### Security Analysis
- Detect hardcoded secrets and credentials
- Identify authentication/authorization issues
- Find input validation vulnerabilities
- Check for proper sanitization
- Analyze dependency vulnerabilities
- Review permission and access control

### Performance Analysis
- Identify inefficient algorithms
- Find N+1 query problems
- Detect unnecessary computations
- Suggest caching opportunities
- Analyze database query efficiency
- Review memory and resource usage

### Architecture Review
- Evaluate code organization and structure
- Check for proper separation of concerns
- Analyze dependency graphs
- Review API design and contracts
- Evaluate design pattern usage
- Assess scalability considerations

### Testing Review
- Check for proper test coverage
- Review test structure and organization
- Identify missing test cases
- Suggest test improvements
- Verify test assertions
- Check for test isolation

### Documentation Review
- Verify code has proper documentation
- Check for missing docstrings
- Review documentation accuracy
- Suggest documentation improvements
- Verify examples in docs work

---

## 📋 Review Workflows

### Workflow 1: Pull Request Review

**Trigger:** User says "review this PR" or shares a pull request link

**Steps:**
1. Fetch pull request details and diff
2. Analyze changed files
3. Identify potential issues and concerns
4. Check for convention violations
5. Review test coverage for changes
6. Provide structured feedback
7. Suggest improvements

**Example Interaction:**
```
User: "Review this pull request: https://github.com/user/repo/pull/123"

AI (code-reviewer skill active):
Fetching PR #123: "Add user authentication endpoint"

📊 **Summary:**
- Changed files: 5
- Lines added: +150
- Lines removed: -20
- Total changes: 130 lines

📁 **Changed Files:**
1. api/main.py (+50 lines)
2. api/schemas.py (+30 lines)
3. api/crud.py (+40 lines)
4. tests/test_auth.py (+30 lines, new file)
5. api/models.py (+20 lines)

🔍 **Detailed Review:**

**api/main.py:**
✅ **Good:**
- Proper route structure
- Good use of dependency injection
- Type hints on all functions

⚠️ **Suggestions:**
- Line 42: Consider adding rate limiting to /auth endpoint
- Line 55: Add input validation for password strength
- Line 68: Use constant for JWT secret instead of hardcoded string

🚨 **Issues:**
- Line 35: SQL injection vulnerability in user lookup
  ```python
  # Current (vulnerable)
  user = db.query(User).filter(f"username = '{username}'").first()
  
  # Suggested (safe)
  user = db.query(User).filter(User.username == username).first()
  ```

**api/schemas.py:**
✅ **Good:**
- Proper Pydantic models
- Good field validation
- Clear documentation

⚠️ **Suggestions:**
- Add example values for documentation
- Consider adding regex pattern for email validation

**tests/test_auth.py:**
✅ **Good:**
- Tests cover main functionality
- Good test structure
- Clear test names

⚠️ **Suggestions:**
- Add tests for edge cases (empty input, invalid email)
- Add integration test for full auth flow
- Check test coverage (currently 75% - aim for 90%)

📝 **Overall Assessment:**
- **Quality:** Good (B+)
- **Security:** Needs attention (C+)
- **Tests:** Satisfactory (B)
- **Documentation:** Adequate (B-)

🎯 **Recommendations:**
1. Fix SQL injection vulnerability (Critical)
2. Add input validation for passwords
3. Move JWT secret to environment variable
4. Add more edge case tests

Would you like me to:
- Generate a detailed review report?
- Suggest fixes for the issues?
- Create a PR comment with feedback?
```

### Workflow 2: Code Snippet Review

**Trigger:** User shares a code snippet for review

**Steps:**
1. Parse the code snippet
2. Identify the language and framework
3. Analyze for issues and improvements
4. Check against project conventions
5. Provide specific feedback
6. Suggest alternative implementations

**Example Interaction:**
```
User: "Review this Python function:
```python
def get_user_by_email(email):
    users = get_all_users()
    for user in users:
        if user.email == email:
            return user
    return None
```"

AI (code-reviewer skill active):
🔍 **Code Analysis:**

**Language:** Python 3.x
**Complexity:** Low (Cyclomatic: 1, Cognitive: 2)

✅ **Good:**
- Clear function name
- Simple and readable logic
- Returns None for not found (Pythonic)

⚠️ **Concerns:**

1. **Performance:** N+1 query problem
   - Current: Loads ALL users, then filters in memory
   - Impact: O(n) memory and time complexity
   - Fix: Use database query filtering
   ```python
   def get_user_by_email(email):
       return db.query(User).filter(User.email == email).first()
   ```

2. **Error Handling:** No error handling for database issues
   - Add try/except for database errors
   ```python
   try:
       return db.query(User).filter(User.email == email).first()
   except DatabaseError as e:
       logger.error(f"Database error: {e}")
       raise
   ```

3. **Type Hints:** Missing type annotations
   - Add for better IDE support and clarity
   ```python
   def get_user_by_email(email: str) -> User | None:
       ...
   ```

📊 **Improved Version:**
```python
def get_user_by_email(email: str) -> User | None:
    """Get user by email address.
    
    Args:
        email: The email address to search for
        
    Returns:
        User object if found, None otherwise
        
    Raises:
        DatabaseError: If there's a database connection issue
    """
    try:
        return db.query(User).filter(User.email == email).first()
    except DatabaseError as e:
        logger.error(f"Database error while fetching user by email: {e}")
        raise
```

Would you like me to:
- Explain any of these suggestions in more detail?
- Review another snippet?
- Check this against project conventions?
```

### Workflow 3: Convention Check

**Trigger:** User says "check conventions" or "lint this code"

**Steps:**
1. Identify project conventions from CONVENTIONS.md
2. Analyze code against conventions
3. Identify violations
4. Suggest fixes
5. Provide compliance report

**Example Interaction:**
```
User: "Check if this code follows project conventions:
```python
import os, sys
from fastapi import *

def GetUser(id):
    pass
```"

AI (code-reviewer skill active):
📖 **Checking against project conventions...**

🚨 **Convention Violations Found:**

1. **Import Formatting** (CONVENTIONS.md: Line 35-45)
   - Current: `import os, sys`
   - Issue: Multiple imports on one line
   - Convention: One import per line
   - Fix:
     ```python
     import os
     import sys
     ```

2. **Wildcard Imports** (CONVENTIONS.md: Line 45)
   - Current: `from fastapi import *`
   - Issue: Wildcard import
   - Convention: Explicit imports only
   - Fix:
     ```python
     from fastapi import FastAPI, Depends, HTTPException
     ```

3. **Function Naming** (CONVENTIONS.md: Line 18-20)
   - Current: `GetUser`
   - Issue: PascalCase function name
   - Convention: snake_case for functions
   - Fix:
     ```python
     def get_user(id: int):
         ...
     ```

4. **Missing Type Hints** (CONVENTIONS.md: Line 63)
   - Current: `def GetUser(id):`
   - Issue: No type hints
   - Convention: All functions must have type hints
   - Fix:
     ```python
     def get_user(id: int) -> User | None:
         ...
     ```

✅ **Compliant:**
- File encoding (UTF-8)
- Line length (within limits)
- Indentation (4 spaces)

📊 **Compliance Score: 0/4 (0%)**

Would you like me to:
- Auto-fix these violations?
- Check another file?
- Generate a convention compliance report?
```

### Workflow 4: Security Review

**Trigger:** User says "security review" or "check for vulnerabilities"

**Steps:**
1. Scan code for security patterns
2. Identify vulnerabilities
3. Assess risk levels
4. Provide remediation guidance
5. Suggest secure alternatives

**Example Interaction:**
```
User: "Do a security review of this API endpoint:
```python
@app.post("/login")
def login(username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and user.password == password:
        return {"token": create_token(user.id)}
    return {"error": "Invalid credentials"}
```"

AI (code-reviewer skill active):
🔒 **Security Review Report**

🚨 **Critical Issues:**

1. **Plain Text Password Comparison** (CVSS: 9.8 - Critical)
   - Issue: Passwords stored and compared in plain text
   - Risk: If database is compromised, all passwords are exposed
   - Fix: Use proper password hashing
   ```python
   from passlib.context import CryptContext
   
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])
   
   def verify_password(plain_password, hashed_password):
       return pwd_context.verify(plain_password, hashed_password)
   
   # In login endpoint:
   if user and verify_password(password, user.password):
       ...
   ```

2. **Missing Input Validation** (CVSS: 7.5 - High)
   - Issue: No validation of username/password input
   - Risk: SQL injection, XSS, buffer overflow
   - Fix: Add input validation
   ```python
   from pydantic import BaseModel, constr
   
   class LoginRequest(BaseModel):
       username: constr(min_length=1, max_length=50, strip_whitespace=True)
       password: constr(min_length=8, max_length=128)
   
   @app.post("/login")
   def login(request: LoginRequest):
       ...
   ```

3. **Timing Attack Vulnerability** (CVSS: 5.3 - Medium)
   - Issue: Different response times for valid/invalid users
   - Risk: Enumeration of valid usernames
   - Fix: Use constant-time comparison
   ```python
   import hmac
   
   if user and hmac.compare_digest(
       str(user.id), 
       str(user.expected_id)  # Always check something
   ):
       # Use verify_password with constant time
       ...
   ```

4. **Missing Rate Limiting** (CVSS: 5.3 - Medium)
   - Issue: No protection against brute force attacks
   - Risk: Account lockout via brute force
   - Fix: Add rate limiting
   ```python
   from fastapi import Request
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/login")
   @limiter.limit("5/minute")
   async def login(request: Request, ...):
       ...
   ```

5. **Error Message Leakage** (CVSS: 3.7 - Low)
   - Issue: Generic error message doesn't reveal which field is wrong
   - Risk: Minimal, but better UX to be specific
   - Fix: Use specific error messages
   ```python
   if not user:
       return {"error": "User not found"}
   if not verify_password(password, user.password):
       return {"error": "Incorrect password"}
   ```

✅ **Good Practices:**
- Uses parameterized queries (prevents SQL injection)
- Returns consistent response structure
- Uses POST method for sensitive data

📊 **Security Score: D (Critical issues found)**

🎯 **Action Items:**
1. [CRITICAL] Implement password hashing
2. [HIGH] Add input validation
3. [MEDIUM] Add rate limiting
4. [MEDIUM] Fix timing attack vulnerability
5. [LOW] Improve error messages

Would you like me to:
- Generate a secure version of this endpoint?
- Explain any vulnerability in more detail?
- Check for other security issues in the codebase?
```

---

## 📊 Review Checklists

### Python Code Review Checklist

- [ ] **Functionality**
  - [ ] Code works as intended
  - [ ] Edge cases handled
  - [ ] Error conditions handled
  - [ ] Input validation present

- [ ] **Code Quality**
  - [ ] Follows PEP 8 guidelines
  - [ ] Type hints on all functions
  - [ ] Clear, descriptive names
  - [ ] Single responsibility principle
  - [ ] DRY principle followed
  - [ ] Proper docstrings

- [ ] **Performance**
  - [ ] No N+1 query problems
  - [ ] Efficient algorithms
  - [ ] Proper caching
  - [ ] No unnecessary computations

- [ ] **Security**
  - [ ] No SQL injection vulnerabilities
  - [ ] No XSS vulnerabilities
  - [ ] No hardcoded secrets
  - [ ] Proper authentication/authorization
  - [ ] Input sanitization

- [ ] **Testing**
  - [ ] Unit tests present
  - [ ] Integration tests for complex flows
  - [ ] Edge cases tested
  - [ ] Test coverage > 80%

### TypeScript/Svelte Code Review Checklist

- [ ] **Functionality**
  - [ ] Code works as intended
  - [ ] Reactivity works correctly
  - [ ] Event handlers properly defined

- [ ] **Code Quality**
  - [ ] Uses Svelte 5 runes (no legacy `$:` syntax)
  - [ ] TypeScript strict mode
  - [ ] Explicit types at boundaries
  - [ ] Clear component structure
  - [ ] Proper error handling

- [ ] **Performance**
  - [ ] No unnecessary re-renders
  - [ ] Efficient data fetching
  - [ ] Proper memoization
  - [ ] No memory leaks

- [ ] **Security**
  - [ ] No XSS vulnerabilities
  - [ ] Input sanitization
  - [ ] No sensitive data in client code
  - [ ] Proper CORS configuration

- [ ] **Testing**
  - [ ] Component tests present
  - [ ] User interaction tests
  - [ ] API client tests

### General Code Review Checklist

- [ ] **Documentation**
  - [ ] Code is well-commented
  - [ ] Docstrings present
  - [ ] README updated if needed
  - [ ] Examples in docs work

- [ ] **Conventions**
  - [ ] Follows project conventions
  - [ ] Consistent with existing code
  - [ ] Proper file organization
  - [ ] Appropriate file names

- [ ] **Dependencies**
  - [ ] All dependencies listed
  - [ ] No unused dependencies
  - [ ] Compatible versions
  - [ ] License compliance

- [ ] **Compatibility**
  - [ ] Cross-browser compatible (frontend)
  - [ ] Cross-platform compatible
  - [ ] Backward compatible (if applicable)

---

## 🎯 Best Practices by Language

### Python Best Practices

1. **Type Hints**
   ```python
   # Good
   def get_user(user_id: int) -> User | None:
       ...
   
   # Bad
   def get_user(user_id):
       ...
   ```

2. **Error Handling**
   ```python
   # Good
   try:
       user = get_user(user_id)
   except UserNotFoundError as e:
       logger.error(f"User not found: {e}")
       raise HTTPException(status_code=404, detail="User not found")
   
   # Bad
   try:
       user = get_user(user_id)
   except:
       pass
   ```

3. **Context Managers**
   ```python
   # Good
   with open("file.txt", "r") as f:
       content = f.read()
   
   # Bad
   f = open("file.txt", "r")
   content = f.read()
   f.close()
   ```

4. **List Comprehensions**
   ```python
   # Good
   even_numbers = [x for x in range(10) if x % 2 == 0]
   
   # Bad
   even_numbers = []
   for x in range(10):
       if x % 2 == 0:
           even_numbers.append(x)
   ```

5. **Database Queries**
   ```python
   # Good - Parameterized query
   user = db.query(User).filter(User.id == user_id).first()
   
   # Bad - String concatenation (SQL injection risk)
   user = db.query(User).filter(f"id = {user_id}").first()
   ```

### TypeScript Best Practices

1. **Type Safety**
   ```typescript
   // Good
   interface User {
       id: number;
       name: string;
       email: string;
   }
   
   // Bad
   const user: any = { id: 1, name: "John" };
   ```

2. **Svelte Runes**
   ```svelte
   <!-- Good -->
   <script>
       let count = $state(0);
       let doubled = $derived(count * 2);
   </script>
   
   <!-- Bad - Legacy syntax -->
   <script>
       let count = 0;
       $: doubled = count * 2;
   </script>
   ```

3. **Async/Await**
   ```typescript
   // Good
   async function fetchData() {
       try {
           const response = await fetch("/api/data");
           return await response.json();
       } catch (error) {
           console.error("Fetch error:", error);
           throw error;
       }
   }
   
   // Bad
   function fetchData() {
       fetch("/api/data").then(response => response.json());
   }
   ```

4. **Component Props**
   ```svelte
   <!-- Good -->
   <script>
       interface Props {
           user: User;
           onEdit: (user: User) => void;
       }
       let { user, onEdit }: Props = $props();
   </script>
   
   <!-- Bad -->
   <script>
       export let user;
       export let onEdit;
   </script>
   ```

5. **Error Boundaries**
   ```svelte
   <!-- Good -->
   <script>
       import { onError } from "svelte/event";
       
       onError((event) => {
           console.error("Error in component:", event.error);
           // Handle error gracefully
       });
   </script>
   ```

---

## 🛠️ Tools Integration

### Static Analysis Tools
- **Python**: Ruff, Pyright, Bandit, Safety
- **TypeScript**: ESLint, TypeScript compiler, Prettier
- **General**: SonarQube, CodeClimate, Semgrep

### Security Tools
- **Python**: Bandit, Safety, semgrep
- **TypeScript**: ESLint security plugins, npm audit
- **Docker**: Docker Scout, Trivy, Grype
- **Dependencies**: Dependabot, Renovate, Snyk

### Testing Tools
- **Python**: pytest, pytest-cov, tox
- **TypeScript**: Vitest, Jest, Cypress
- **E2E**: Playwright, Selenium

---

## 📊 Scoring System

The skill uses a scoring system to assess code quality:

| Aspect | Weight | Score Range | Description |
|--------|--------|-------------|-------------|
| Functionality | 30% | 0-100 | Code works correctly |
| Code Quality | 25% | 0-100 | Readability, maintainability |
| Security | 20% | 0-100 | Vulnerability assessment |
| Performance | 15% | 0-100 | Efficiency and optimization |
| Testing | 10% | 0-100 | Test coverage and quality |

**Overall Score:** Weighted average of all aspects

| Score Range | Grade | Description |
|-------------|-------|-------------|
| 90-100 | A+ | Excellent - Production ready |
| 80-89 | A | Very Good - Minor improvements |
| 70-79 | B | Good - Some issues to address |
| 60-69 | C | Satisfactory - Needs work |
| 50-59 | D | Poor - Significant issues |
| 0-49 | F | Failing - Critical issues |

---

## 📝 Examples

### Example 1: Complete Code Review
```
User: "Review this entire file: api/crud.py"

AI Response:
📄 **File: api/crud.py**
📊 **Language: Python** | **Lines: 150** | **Functions: 8**

🔍 **Overall Assessment:**
- **Quality Score: 85/100 (B+)**
- **Security: 90/100 (A-)**
- **Performance: 80/100 (B)**
- **Testing: 75/100 (C+)**

✅ **Strengths:**
- All functions have type hints
- Proper error handling with custom exceptions
- Good use of SQLAlchemy ORM
- Consistent code style
- Functions are small and focused

⚠️ **Improvements:**
1. Line 25: Add docstring to `get_todos` function
2. Line 42: Consider adding caching for frequently accessed todos
3. Line 68: Add validation for `todo_id` parameter
4. Line 85: Use bulk update for better performance
5. Line 110: Add tests for edge cases (null inputs)

🚨 **Issues:**
- Line 30: Potential race condition in concurrent updates
  - Fix: Use database-level locking

📊 **Function Breakdown:**
| Function | Lines | Complexity | Issues | Score |
|----------|-------|------------|--------|-------|
| get_todos | 15 | Low | 0 | 95 |
| get_todo | 10 | Low | 0 | 90 |
| create_todo | 20 | Medium | 0 | 85 |
| update_todo | 25 | Medium | 1 | 80 |
| delete_todo | 12 | Low | 0 | 90 |

Would you like me to:
- Generate a detailed report?
- Suggest fixes for the issues?
- Check another file?
```

### Example 2: Quick Code Snippet Check
```
User: "Is this code good?
```python
def process_data(data):
    result = []
    for item in data:
        if item.is_valid:
            result.append(process_item(item))
    return result
```"

AI Response:
🔍 **Quick Assessment:**

✅ **Good:**
- Clear function name
- Simple, readable logic
- List comprehension could be used

⚠️ **Could Improve:**
1. Missing type hints
2. Missing docstring
3. Could use list comprehension

📊 **Score: 75/100 (C+)**

💡 **Improved Version:**
```python
def process_data(data: list[Item]) -> list[ProcessedItem]:
    """Process a list of items, filtering by validity.
    
    Args:
        data: List of items to process
        
    Returns:
        List of processed items that are valid
    """
    return [process_item(item) for item in data if item.is_valid]
```

Score: 95/100 (A)
```

---

## 🎯 Recommendations Template

When providing code review feedback, use this template:

```markdown
## Code Review: [File/Feature Name]

### Summary
- **Files Reviewed:** X
- **Lines Changed:** +Y, -Z
- **Overall Score:** [Grade]
- **Estimated Review Time:** [Time]

### Strengths ✅
1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

### Suggestions ⚠️
1. [Suggestion 1] - [Location] - [Priority]
   - Current: [Current code]
   - Suggested: [Improved code]
   - Reason: [Why this is better]

2. [Suggestion 2] - [Location] - [Priority]
   - Current: [Current code]
   - Suggested: [Improved code]
   - Reason: [Why this is better]

### Issues 🚨
1. [Issue 1] - [Location] - [Severity] - [Priority]
   - Problem: [Description]
   - Impact: [What could go wrong]
   - Fix: [How to fix]

2. [Issue 2] - [Location] - [Severity] - [Priority]
   - Problem: [Description]
   - Impact: [What could go wrong]
   - Fix: [How to fix]

### Testing Notes 🧪
- Test Coverage: [X]%
- Missing Tests: [List areas]
- Suggested Tests: [List suggestions]

### Performance Notes ⚡
- Bottlenecks: [List]
- Optimizations: [List suggestions]
- Complexity: [Big-O analysis]

### Security Notes 🔒
- Vulnerabilities: [List]
- Risk Level: [High/Medium/Low]
- Recommendations: [List]

### Documentation Notes 📝
- Missing Docs: [List]
- Inaccuracies: [List]
- Suggestions: [List]

### Approval Status
- [ ] Approved
- [ ] Approved with comments
- [ ] Changes requested
- [ ] Not approved

### Next Steps
1. [Action 1]
2. [Action 2]
3. [Action 3]
```

---

## 🔍 Related Files

- [Root AGENTS.md](../../../AGENTS.md) - Main AI assistant guide
- [api/AGENTS.md](../../../api/AGENTS.md) - API-specific context
- [web/AGENTS.md](../../../web/AGENTS.md) - Frontend-specific context
- [docs/CONVENTIONS.md](../../../docs/CONVENTIONS.md) - Coding conventions
- [docs/TECHNICAL_GUIDE.md](../../../docs/TECHNICAL_GUIDE.md) - Technical implementation

---

*Last updated: 2026-06-23*
*Generated by Mistral Vibe - Code Reviewer Skill*