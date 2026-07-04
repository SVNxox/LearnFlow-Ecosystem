

Next.js 14 frontend for LearnFlow educational platform.



- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **State Management:** React Context API



```
src/
├── app/                    
│   ├── (auth)/            
│   ├── layout.tsx         
│   └── page.tsx           
├── components/
│   ├── ui/                
│   └── features/          
│       ├── auth/          
│       ├── courses/       
│       ├── lessons/       
│       └── dashboard/     
├── lib/
│   ├── api-client.ts      
│   ├── api.ts             
│   └── auth-context.tsx   
├── types/
│   └── api.ts             
├── utils/
│   └── helpers.ts         
└── hooks/                 
```



Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=LearnFlow
NEXT_PUBLIC_APP_URL=http://localhost:3000
```



1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run development server:**
   ```bash
   npm run dev
   ```

3. **Open browser:**
   ```
   http://localhost:3000
   ```




- Login page (`/login`)
- Register page (`/register`)
- JWT token management (access + refresh)
- Automatic token refresh on 401
- Protected routes via AuthContext


- Axios instance with interceptors
- Automatic bearer token injection
- Token refresh flow
- Error handling utilities
- Type-safe API methods for all domains


Complete type definitions for all API responses


- Date formatting, file size, status colors, etc.




- [ ] Course catalog page (`/courses`)
- [ ] Course detail page (`/courses/[id]`)
- [ ] Lesson viewer
- [ ] Student dashboard



The frontend connects to Django backend at `http://localhost:8000/api/v1`.


Make sure Django backend has CORS enabled:

```python

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```




Tokens are stored in `localStorage`:
- `access_token` — JWT access token
- `refresh_token` — JWT refresh token
- `user` — User object (JSON)
