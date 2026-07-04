

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0001_initial'),
        ('enrollment', '0001_initial_empty'),
    ]

    operations = [
        
        migrations.RunSQL(
            sql='ALTER TABLE courses_courseenrollment RENAME TO enrollment_courseenrollment;',
            reverse_sql='ALTER TABLE enrollment_courseenrollment RENAME TO courses_courseenrollment;',
        ),

        
        migrations.RunSQL(
            sql='ALTER INDEX idx_courseenrollment_user_status RENAME TO idx_enrollment_user_status;',
            reverse_sql='ALTER INDEX idx_enrollment_user_status RENAME TO idx_courseenrollment_user_status;',
        ),
        migrations.RunSQL(
            sql='ALTER INDEX idx_courseenrollment_course_status RENAME TO idx_enrollment_course_status;',
            reverse_sql='ALTER INDEX idx_enrollment_course_status RENAME TO idx_courseenrollment_course_status;',
        ),

        
        migrations.RunSQL(
            sql='''
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_courseenrollment_user_course') THEN
                    ALTER TABLE enrollment_courseenrollment RENAME CONSTRAINT uq_courseenrollment_user_course TO uq_enrollment_user_course;
                END IF;

                -- chk_enrollment_status и chk_enrollment_delivery_format уже имеют правильные имена
                -- Ничего не делаем, если constraint уже существует
            END $$;
            ''',
            reverse_sql='',
        ),

        
        migrations.RunSQL(
            sql='''
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'courses_courseenrollment_course_id_fkey'
                    AND conrelid = 'enrollment_courseenrollment'::regclass
                ) THEN
                    ALTER TABLE enrollment_courseenrollment DROP CONSTRAINT courses_courseenrollment_course_id_fkey;
                END IF;
            END $$;
            ''',
            reverse_sql='',  
        ),

        
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='CourseEnrollment'),
            ],
            database_operations=[],
        ),
    ]
