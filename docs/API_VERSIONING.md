

> **Status:** Active (ADR-034)  
> **Last Updated:** 2026-06-08

Этот документ описывает стратегию версионирования API LearnFlow.

---





```
/api/{version}/{domain}/{feature}/{action}/
```



```

POST   /api/v1/identity/auth/login/
POST   /api/v1/identity/auth/register/
GET    /api/v1/identity/profile/me/
PATCH  /api/v1/identity/profile/me/


GET    /api/v1/learning/courses/
GET    /api/v1/learning/courses/{id}/
POST   /api/v1/learning/courses/


POST   /api/v1/enrollment/enroll/
GET    /api/v1/enrollment/my-enrollments/
```

---



✅ **Chosen:** Version in URL path (`/api/v1/`, `/api/v2/`)

❌ **Rejected:** Accept Header versioning (`Accept: application/json; version=v1`)



| Criterion              | URL-Based         | Accept Header      |
|------------------------|-------------------|--------------------|
| **Debuggability**      | ✅ Visible in logs | ❌ Hidden in headers|
| **Caching (CDN)**      | ✅ Works          | ❌ Breaks          |
| **Browser testing**    | ✅ Easy           | ❌ Requires tools  |
| **API documentation**  | ✅ Clear          | ⚠️ Confusing       |
| **Client simplicity**  | ✅ Simple         | ❌ Custom headers  |
| **Industry standard**  | ✅ Stripe, GitHub | ❌ Rare            |



- **Stripe:** `https://api.stripe.com/v1/charges`
- **GitHub:** `https://api.github.com/repos/{owner}/{repo}`
- **Twitter:** `https://api.twitter.com/2/tweets`

---





| State        | Description                                  | Support Level        |
|--------------|----------------------------------------------|----------------------|
| **Current**  | Latest stable version                        | Full support         |
| **Stable**   | Previous version, still maintained           | Bug fixes only       |
| **Deprecated** | Scheduled for removal                      | Critical fixes only  |
| **Sunset**   | Removed, returns 410 Gone                    | Not supported        |



```
v1 Released ──────────────────────────────> Current (full support)
              │
              └─ 6 months ─> v2 Released ──> v1 = Stable (bug fixes)
                              │
                              └─ 6 months ─> v1 = Deprecated (critical fixes)
                                              │
                                              └─ 6 months ─> v1 = Sunset (removed)
```

**Total lifetime:** 18 months minimum per major version.

---





**Breaking changes (require new version):**
- ❌ Removing an endpoint
- ❌ Removing a field from response
- ❌ Changing field type (`string` → `integer`)
- ❌ Making an optional field required
- ❌ Changing authentication method
- ❌ Renaming fields
- ❌ Changing error response structure

**Non-breaking changes (same version):**
- ✅ Adding new endpoints
- ✅ Adding new optional fields to request
- ✅ Adding new fields to response
- ✅ Adding new error codes (with fallback)
- ✅ Making a required field optional
- ✅ Bug fixes



1. **Announce** (6 months before removal):
   ```http
   HTTP/1.1 200 OK
   Deprecation: true
   Sunset: Sat, 01 Dec 2026 00:00:00 GMT
   Link: </api/v2/identity/auth/login/>; rel="successor-version"
   ```

2. **Document** in API changelog and release notes

3. **Monitor** usage via logs/analytics

4. **Remove** after sunset date (return `410 Gone`)

---





```

GET /api/v1/schema/


GET /api/v1/schema/swagger/


GET /api/v1/schema/redoc/
```



Tags are grouped by domain:

```yaml
tags:
  - name: Identity — Auth
    description: Authentication & registration
  - name: Identity — Profile
    description: User profile management
  - name: Identity — Sessions
    description: Active session management
  - name: Learning — Courses
    description: Course catalog & content
  - name: Enrollment — Enrollments
    description: Course enrollment management
```

---





**Step 1: Check deprecation headers**

```bash
curl -I https://api.learnflow.com/api/v1/identity/auth/login/

HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Dec 2026 00:00:00 GMT
Link: </api/v2/identity/auth/login/>; rel="successor-version"
```

**Step 2: Test against v2 in staging**

```python

response = requests.post('https://api.learnflow.com/api/v1/identity/auth/login/', ...)


response = requests.post('https://api.learnflow.com/api/v2/identity/auth/login/', ...)
```

**Step 3: Update base URL**

```python

API_BASE = os.getenv('LEARNFLOW_API_BASE', 'https://api.learnflow.com/api/v1')


response = requests.post(f'{API_BASE}/identity/auth/login/', ...)
```

**Step 4: Deploy and monitor**

- Deploy to production
- Monitor error rates
- Rollback if issues

---





❌ **Bad:** Hardcoded URLs everywhere
```python
requests.post('https://api.learnflow.com/api/v1/identity/auth/login/', ...)
requests.get('https://api.learnflow.com/api/v1/identity/profile/me/', ...)
```

✅ **Good:** Centralized configuration
```python
class LearnFlowClient:
    def __init__(self, base_url='https://api.learnflow.com/api/v1'):
        self.base = base_url
    
    def login(self, email, password):
        return requests.post(f'{self.base}/identity/auth/login/', ...)
```



```python
response = requests.get(url)

if 'Deprecation' in response.headers:
    logger.warning(
        f"API endpoint {url} is deprecated. "
        f"Sunset date: {response.headers.get('Sunset')}. "
        f"Migrate to: {response.headers.get('Link')}"
    )
```



```python
import openapi_core


schema = requests.get('https://api.learnflow.com/api/v1/schema/').json()


validator = openapi_core.create_spec(schema)
result = validator.validate_request(request)
```



```yaml

LEARNFLOW_API_VERSION=v1


LEARNFLOW_API_VERSION=v2  
```

---





- [ ] Copy `accounts/presentation/rest/v1/` → `v2/`
- [ ] Update `api/v1/urls.py` → `api/v2/urls.py`
- [ ] Update `SPECTACULAR_SETTINGS['VERSION']` in settings
- [ ] Add deprecation headers to v1 endpoints
- [ ] Update `docs/CHANGELOG.md`
- [ ] Announce in release notes
- [ ] Monitor v1 usage for 6 months
- [ ] Remove v1 after sunset date



```python

from django.urls import path, include

urlpatterns = [
    path('identity/', include('identity.presentation.rest.v2.urls')),
    path('learning/', include('learning.presentation.rest.v2.urls')),
    
]


urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
    path('api/v2/', include('api.v2.urls')),  
]
```

---



- **ADR-034:** API URL Structure & Versioning Strategy
- **ADR-033:** Feature-Sliced Modular Monolith
- **docs/API.md:** API Design Guidelines
- **docs/ARCHITECTURE.md:** System Architecture

---



- [Stripe API Versioning](https://stripe.com/docs/api/versioning)
- [GitHub API Versioning](https://docs.github.com/en/rest/overview/api-versions)
- [REST API Versioning Best Practices](https://restfulapi.net/versioning/)
- [RFC 8594: Sunset HTTP Header](https://www.rfc-editor.org/rfc/rfc8594.html)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
