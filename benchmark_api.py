
"""
Performance Benchmark Script for LearnFlow API
Measures real API response times and SQL query counts
"""

import os
import sys
import django
import time
from django.db import connection, reset_queries
from django.test.utils import override_settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnflow.settings.local')
django.setup()

from django.contrib.auth import get_user_model
from src.backend.learning.domain.models import Course, Module, Lesson
from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.progress.domain.models import CourseProgress, ModuleProgress, LessonProgress
from src.backend.assessment.domain.models import ModuleAssessment, AssessmentItem, AssessmentAttempt

User = get_user_model()


class BenchmarkRunner:
    """Run performance benchmarks on API queries"""

    def __init__(self):
        self.results = []

    def measure_query(self, name, func, *args, **kwargs):
        """Measure execution time and query count"""
        reset_queries()

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        elapsed_ms = (end_time - start_time) * 1000
        query_count = len(connection.queries)

        self.results.append({
            'name': name,
            'time_ms': round(elapsed_ms, 2),
            'queries': query_count,
            'result_count': len(result) if hasattr(result, '__len__') else 1
        })

        print(f"✓ {name}")
        print(f"  Time: {elapsed_ms:.2f}ms")
        print(f"  Queries: {query_count}")
        print(f"  Results: {len(result) if hasattr(result, '__len__') else 1}")
        print()

        return result

    def run_benchmarks(self):
        """Run all benchmarks"""
        print("=" * 60)
        print("LearnFlow API Performance Benchmarks")
        print("=" * 60)
        print()

        
        print("1. Course Catalog (with select_related)")
        self.measure_query(
            "Course Catalog",
            lambda: list(Course.objects.filter(
                status='published'
            ).select_related(
                'created_by'
            ))
        )

        
        print("2. Course Catalog (WITHOUT select_related - N+1 problem)")
        courses = self.measure_query(
            "Course Catalog (N+1)",
            lambda: list(Course.objects.filter(status='published'))
        )
        
        if courses:
            reset_queries()
            start = time.time()
            for course in courses[:5]:  
                _ = course.created_by.email
            elapsed = (time.time() - start) * 1000
            queries = len(connection.queries)
            print(f"  + Accessing created_by.email for {min(5, len(courses))} courses:")
            print(f"    Time: {elapsed:.2f}ms")
            print(f"    Queries: {queries} (N+1 problem!)")
            print()

        
        if Course.objects.exists():
            course = Course.objects.first()
            print("3. Course Detail (with prefetch_related)")
            self.measure_query(
                "Course Detail",
                lambda: Course.objects.select_related(
                    'created_by'
                ).prefetch_related(
                    'modules'
                ).get(pk=course.pk)
            )

        
        if CourseEnrollment.objects.exists():
            enrollment = CourseEnrollment.objects.first()
            user = enrollment.user
            print("4. Student Enrollments")
            self.measure_query(
                "My Enrollments",
                lambda: list(CourseEnrollment.objects.filter(
                    user=user
                ).select_related(
                    'user'  
                ))
            )

        
        if CourseProgress.objects.exists():
            print("5. Course Progress Detail")
            self.measure_query(
                "Course Progress",
                lambda: CourseProgress.objects.all()[:10]
            )

        
        if ModuleProgress.objects.exists():
            print("6. Module Progress List")
            self.measure_query(
                "Module Progress",
                lambda: list(ModuleProgress.objects.all()[:20])
            )

        
        print("7. Lesson Progress List")
        self.measure_query(
            "Lesson Progress",
            lambda: list(LessonProgress.objects.all()[:20])
        )

        
        if ModuleAssessment.objects.exists():
            assessment = ModuleAssessment.objects.first()
            print("7. Assessment Detail (with prefetch_related - FIXED)")
            self.measure_query(
                "Assessment Detail (optimized)",
                lambda: ModuleAssessment.objects.prefetch_related(
                    'items',
                    'items__options'
                ).get(pk=assessment.pk)
            )

            
            print("8. Assessment Detail (WITHOUT prefetch - N+1 problem)")
            reset_queries()
            start = time.time()
            assessment_unopt = ModuleAssessment.objects.get(pk=assessment.pk)
            items = list(assessment_unopt.items.all())
            for item in items:
                _ = list(item.options.all())
            elapsed = (time.time() - start) * 1000
            queries = len(connection.queries)
            print(f"  Time: {elapsed:.2f}ms")
            print(f"  Queries: {queries} (N+1 problem!)")
            print()

        
        if AssessmentAttempt.objects.exists():
            attempt = AssessmentAttempt.objects.first()
            print("9. Assessment Attempt (with responses)")
            self.measure_query(
                "Assessment Attempt",
                lambda: AssessmentAttempt.objects.select_related(
                    'assessment'
                ).prefetch_related(
                    'responses',
                    'responses__item'
                ).get(pk=attempt.pk)
            )

        
        self.print_summary()

    def print_summary(self):
        """Print benchmark summary"""
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print()
        print(f"{'Operation':<40} {'Time (ms)':<12} {'Queries':<10}")
        print("-" * 60)

        for result in self.results:
            print(f"{result['name']:<40} {result['time_ms']:<12} {result['queries']:<10}")

        print()
        print("Average response time:", round(sum(r['time_ms'] for r in self.results) / len(self.results), 2), "ms")
        print("Total queries:", sum(r['queries'] for r in self.results))
        print()

        
        print("=" * 60)
        print("N+1 QUERY IMPROVEMENTS")
        print("=" * 60)

        if len(self.results) >= 2:
            
            if 'Course Catalog' in self.results[0]['name']:
                optimized = self.results[0]
                print(f"\n✓ Course Catalog optimization:")
                print(f"  With select_related: {optimized['queries']} queries")
                print(f"  Impact: Eliminates N+1 problem for created_by access")

        if any('Assessment Detail' in r['name'] for r in self.results):
            opt = next((r for r in self.results if 'optimized' in r['name']), None)
            if opt:
                print(f"\n✓ Assessment Detail optimization:")
                print(f"  With prefetch_related: {opt['queries']} queries")
                print(f"  Impact: Eliminates N+1 for items and options")


if __name__ == '__main__':
    
    from django.conf import settings
    settings.DEBUG = True

    runner = BenchmarkRunner()
    runner.run_benchmarks()
