

Last updated: 2026-06-18



```
src/components/
├── ui/                  
│   ├── Navbar.tsx       
│   ├── LoadingSpinner.tsx
│   ├── EmptyState.tsx
│   ├── StatusBadge.tsx  
│   ├── ProgressBar.tsx
│   ├── ConfirmModal.tsx 
│   ├── Button.tsx / Card.tsx / Badge.tsx / Input.tsx / Progress.tsx / Spinner.tsx
│   └── index.ts
│
├── course/              
│   ├── CourseCard.tsx
│   └── EnrollModal.tsx
│
├── lesson/               
│   ├── ContentViewer.tsx    
│   ├── HomeworkSection.tsx
│   ├── PracticeSection.tsx
│   └── QuizSection.tsx
│
├── submission/           
│   ├── SubmissionForm.tsx   
│   └── FileUploadZone.tsx   
│
├── mentor/                
│   └── WorkQueueList.tsx    
│
├── admin/                  
│   ├── AdminLayout.tsx        
│   ├── AdminSidebar.tsx       
│   ├── RequireRole.tsx        
│   ├── SortableList.tsx       
│   ├── PublishToggle.tsx      
│   ├── NotImplementedBanner.tsx 
│   ├── CourseEditor/
│   │   └── CurriculumTab.tsx    
│   └── LessonEditor/
│       ├── ContentTab.tsx       
│       ├── QuizTab.tsx          
│       ├── HomeworkTab.tsx      
│       └── PracticeTab.tsx      
│
└── layouts/
    └── DashboardLayout.tsx  
```


- `lib/admin-api.ts` wraps every admin endpoint. A handful of endpoints documented in the
  admin implementation prompt don't exist on the backend yet (content items, quiz, practice,
  payments, certificate templates/generate/revoke, categories — see code comments in
  `admin-api.ts` for the full list). Those calls are caught with `isNotImplemented(err)` and
  the UI renders `<NotImplementedBanner />` instead of crashing.
- `AdminLayout` accepts `roles={['admin']}` or `roles={['admin','staff']}` per page — course/lesson
  editing is shared between admin and staff, while user/payment/certificate/analytics management
  is admin-only, matching the prompt's permission matrix.


- Tailwind only, following the design tokens in the implementation prompt
  (blue-600 primary, gray-50 page background, `rounded-xl border border-gray-200 shadow-sm` cards).
- Each folder has an `index.ts` barrel export.
- Domain types live in `src/types/api.ts` (identity/progress/assessment/submissions/certificates)
  and `src/types/learning.ts` (courses/modules/lessons — matches the Learning domain REST shapes).
