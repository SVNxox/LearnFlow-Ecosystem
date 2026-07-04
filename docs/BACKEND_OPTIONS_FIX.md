

**Date:** 2026-06-15  
**Status:** ✅ COMPLETED

---



Added `options` array to Assessment Attempt Detail API response. This was a **CRITICAL MVP blocker** — frontend Quiz UI couldn't display answer choices without this data.



Frontend `FRONTEND_ANALYSIS.md` identified:

```
❌ Backend doesn't return `options` array in `AssessmentItemResponse`
- Needed for rendering quiz choices during attempt
- **Impact:** Quiz UI can't display options (CRITICAL)
```

**Before fix:**
```json
{
  "items": [
    {
      "item_id": "uuid",
      "item_type": "single_choice",
      "item_title": "What is Python?",
      "order": 1,
      "max_points": 10.00,
      "selected_option_ids": ["uuid"],
      // ❌ NO OPTIONS — Quiz UI can't render choices!
    }
  ]
}
```

**After fix:**
```json
{
  "items": [
    {
      "item_id": "uuid",
      "item_type": "single_choice",
      "item_title": "What is Python?",
      "order": 1,
      "max_points": 10.00,
      "options": [  // ✅ NOW AVAILABLE
        {"id": "uuid1", "text": "Programming language", "order": 1},
        {"id": "uuid2", "text": "Snake", "order": 2},
        {"id": "uuid3", "text": "Music genre", "order": 3}
      ],
      "selected_option_ids": ["uuid1"]
    }
  ]
}
```

---





**Added `ItemOption` dataclass:**
```python
@dataclass
class ItemOption:
    """Option for choice-type items."""
    id: UUID
    text: str
    order: int
```

**Updated `AttemptItemResult`:**
```python
@dataclass
class AttemptItemResult:
    item_id: UUID
    item_type: str
    item_title: str
    order: int
    max_points: Decimal
    
    
    options: Optional[List[ItemOption]]
    
    
```

**Updated `execute()` method:**
```python

responses = AssessmentResponse.objects.filter(
    attempt=attempt
).select_related('item').prefetch_related('item__options').order_by('item__order')

for response in responses:
    
    options = None
    if response.item.type in ['single_choice', 'multiple_choice']:
        options = [
            ItemOption(
                id=opt.id,
                text=opt.text,
                order=opt.order
            )
            for opt in response.item.options.all()
        ]
    
    items.append(AttemptItemResult(
        
        options=options,  
    ))
```

**Key decisions:**
- ✅ Options only loaded for `single_choice` and `multiple_choice` types
- ✅ Using `prefetch_related('item__options')` to avoid N+1 queries
- ✅ Options ordered by `order` field (from model's `ordering`)
- ✅ Returns `None` for non-choice types (text_answer, coding, etc.)

---



**Updated response serialization:**
```python
'items': [
    {
        'item_id': str(item.item_id),
        'item_type': item.item_type,
        'item_title': item.item_title,
        'order': item.order,
        'max_points': float(item.max_points),
        
        
        'options': [
            {
                'id': str(opt.id),
                'text': opt.text,
                'order': opt.order
            }
            for opt in item.options
        ] if item.options else None,  
        
        'selected_option_ids': [str(oid) for oid in item.selected_option_ids],
        
    }
    for item in result.items
]
```

---



**Updated `AssessmentItemResponse`:**
```typescript
export interface AssessmentItemResponse {
  item_id: string;
  item_type: 'single_choice' | 'multiple_choice' | 'text_answer' | 'coding' | 'project' | 'interview';
  item_title: string;
  order: number;
  max_points: number;
  
  // NEW: Options array for choice types
  options?: Array<{ id: string; text: string; order: number }>;
  
  selected_option_ids: string[];
  // ... rest of fields
}
```

---



**Updated QuestionCard rendering:**
```typescript
<QuestionCard
  key={item.item_id}
  itemId={item.item_id}
  type={item.item_type as any}
  title={item.item_title}
  description={undefined}
  options={item.options}  // ✅ Now passed from backend
  maxPoints={item.max_points}
  order={index + 1}
  currentAnswer={responses[item.item_id]}
  onAnswerChange={(answer) => handleAnswerChange(item.item_id, answer)}
/>
```

---





**Before (N+1 problem):**
```python

responses = AssessmentResponse.objects.filter(attempt=attempt).select_related('item')

for response in responses:
    options = response.item.options.all()  
```

**After (optimized):**
```python

responses = AssessmentResponse.objects.filter(
    attempt=attempt
).select_related('item').prefetch_related('item__options')  

for response in responses:
    options = response.item.options.all()  
```

**Query count for 10-item assessment:**
- Before: 1 (attempt) + 1 (responses) + 10 (options per item) = **12 queries**
- After: 1 (attempt) + 1 (responses) + 1 (all options prefetched) = **3 queries**

---





**Options DO NOT expose:**
- ❌ `is_correct` flag — students can't see correct answers during attempt
- ❌ `explanation` field — only shown after grading
- ❌ Other students' responses

**What IS exposed:**
- ✅ `id` — needed for response submission
- ✅ `text` — the option text (public during attempt)
- ✅ `order` — display order

**Security is enforced by:**
1. View checks `attempt.user_id == request.user.id` (only own attempts)
2. Options model has separate fields for instructor data (`is_correct`, `explanation`)
3. Serialization explicitly excludes sensitive fields

---





**Response (items array):**
```json
{
  "items": [
    {
      "item_id": "uuid",
      "item_type": "single_choice",
      "item_title": "What is Python?",
      "order": 1,
      "max_points": 10.00,
      "options": [
        {"id": "uuid1", "text": "A programming language", "order": 1},
        {"id": "uuid2", "text": "A type of snake", "order": 2},
        {"id": "uuid3", "text": "A web framework", "order": 3}
      ],
      "selected_option_ids": [],
      "text_response": null,
      "submitted_code": null,
      "is_graded": false,
      "auto_points": null,
      "mentor_points": null,
      "final_points": null,
      "is_correct": null,
      "review_comment": null
    },
    {
      "item_id": "uuid2",
      "item_type": "text_answer",
      "item_title": "Explain closures in JavaScript",
      "order": 2,
      "max_points": 20.00,
      "options": null,  // ✅ null for non-choice types
      "selected_option_ids": [],
      "text_response": "",
      "submitted_code": null,
      // ... rest
    }
  ]
}
```

**Rules:**
- `options` is `null` for: `text_answer`, `coding`, `project`, `interview`
- `options` is array for: `single_choice`, `multiple_choice`
- Options are ordered by `order` field
- Options DO NOT contain `is_correct` or `explanation`

---





✅ **Unit test (query layer):**
```python
def test_attempt_detail_includes_options():
    
    item = AssessmentItem.objects.create(
        assessment=assessment,
        type='single_choice',
        title='Test question',
        order=1,
        max_points=10
    )
    
    
    opt1 = AssessmentOption.objects.create(item=item, text='Option A', order=1, is_correct=True)
    opt2 = AssessmentOption.objects.create(item=item, text='Option B', order=2, is_correct=False)
    
    
    attempt = start_attempt(enrollment_id, assessment_id, user_id)
    
    
    query = GetAttemptDetailQuery(attempt_id=attempt.id)
    result = query.execute()
    
    
    assert len(result.items) == 1
    assert result.items[0].options is not None
    assert len(result.items[0].options) == 2
    assert result.items[0].options[0].text == 'Option A'
```

✅ **Integration test (API endpoint):**
```bash

POST /api/v1/assessment/attempts/
{
  "enrollment_id": "uuid",
  "assessment_id": "uuid"
}


GET /api/v1/assessment/attempts/{attempt_id}/


assert response['items'][0]['options'] is not None
assert len(response['items'][0]['options']) > 0
```

✅ **Frontend test:**
- Quiz UI renders options correctly
- Student can select answers
- Selected answers persist on page reload

---



1. **Backend:**
   - `src/backend/assessment/application/queries/get_attempt_detail.py` — query logic
   - `src/backend/assessment/presentation/rest/v1/attempts/detail.py` — API serialization

2. **Frontend:**
   - `src/frontend/src/types/api.ts` — TypeScript types
   - `src/frontend/src/app/assessments/[id]/attempt/[attemptId]/page.tsx` — Quiz UI

---



**Before fix:**
- ❌ Quiz UI showed questions without answer choices
- ❌ Students couldn't complete single_choice/multiple_choice assessments
- ❌ **CRITICAL MVP BLOCKER**

**After fix:**
- ✅ Quiz UI displays all answer options
- ✅ Students can select and submit answers
- ✅ Assessment flow is now functional end-to-end
- ✅ **MVP BLOCKER REMOVED**

---



**Database queries per attempt detail request:**
- Before: 12 queries (for 10-item assessment)
- After: 3 queries (for 10-item assessment)
- **Improvement: 75% reduction in queries**

**Response size increase:**
- Minimal (~200-500 bytes per item with options)
- Acceptable tradeoff for functionality

---



**Estimated:** 1 hour  
**Actual:** 30 minutes

---



✅ **COMPLETED** — Assessment Quiz UI now fully functional



According to `FRONTEND_ANALYSIS.md`, remaining P0 blockers:
1. ✅ Fix Assessment API — DONE
2. ✅ Add options to attempt detail — DONE
3. ❌ Implement Submissions UI (6-8 hours)
4. ❌ Implement Mentor Dashboard (4-6 hours)
5. ❌ Fix Progress tracking (2 hours)
