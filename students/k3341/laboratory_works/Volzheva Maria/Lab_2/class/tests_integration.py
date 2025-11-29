from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Class, Subject, Homework, Submission
from datetime import date

User = get_user_model()


class IntegrationTests(TestCase):

    def setUp(self):
        """Подготовка данных для всех тестов."""
        self.test_class = Class.objects.create(name="10-A")

        self.student = User.objects.create_user(
            username='student1',
            password='studentpass123',
            role='student',
            student_class=self.test_class
        )
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='teacherpass123',
            role='teacher'
        )

        self.subject = Subject.objects.create(name="Mathematics")
        self.subject.teachers.add(self.teacher)

        self.homework = Homework.objects.create(
            subject=self.subject,
            date_from=date.today(),
            date_to=date.today(),
            description="Solve problems 1-10 from the textbook"
        )
        self.homework.classes.add(self.test_class)

        self.client = Client()

    def test_student_can_create_submission(self):
        self.client.login(username='student1', password='studentpass123')

        url = reverse('create_submission_', kwargs={'pk': self.homework.pk})
        response = self.client.post(url, {'submitted_text': 'My solution is...'})

        self.assertRedirects(response, reverse('home'))

        self.assertEqual(Submission.objects.count(), 1)
        submission = Submission.objects.first()
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.homework, self.homework)
        self.assertEqual(submission.submitted_text, 'My solution is...')
        self.assertIsNone(submission.grade)  # Оценка должна быть пустой

    def test_teacher_can_grade_submission(self):
        submission = Submission.objects.create(
            homework=self.homework,
            student=self.student,
            submitted_text="My answer"
        )

        self.client.login(username='teacher1', password='teacherpass123')

        url = reverse('grade_submission', kwargs={'pk': submission.pk})
        response = self.client.post(url, {'grade': '5'})

        self.assertRedirects(response, reverse('submissions_without_grades'))

        submission.refresh_from_db()
        self.assertEqual(submission.grade, 5)

    def test_teacher_sees_ungraded_submissions(self):
        Submission.objects.create(
            homework=self.homework,
            student=self.student,
            submitted_text="Ungraded work",
            grade=None
        )
        Submission.objects.create(
            homework=self.homework,
            student=self.student,
            submitted_text="Graded work",
            grade=4
        )

        self.client.login(username='teacher1', password='teacherpass123')

        response = self.client.get(reverse('submissions_without_grades'))

        self.assertEqual(response.status_code, 200)

        ungraded_submissions = response.context['data']['Mathematics']
        self.assertEqual(len(ungraded_submissions), 1)
        self.assertIsNone(ungraded_submissions[0].grade)
        self.assertEqual(ungraded_submissions[0].submitted_text, "Ungraded work")

    def test_student_cannot_grade_submission(self):
        submission = Submission.objects.create(
            homework=self.homework,
            student=self.student,
            submitted_text="Student's work"
        )

        self.client.login(username='student1', password='studentpass123')

        url = reverse('grade_submission', kwargs={'pk': submission.pk})
        response = self.client.post(url, {'grade': '5'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'not_available.html')

        submission.refresh_from_db()
        self.assertIsNone(submission.grade)

    def test_grades_by_subject_per_class_structure(self):
        Submission.objects.create(
            homework=self.homework,
            student=self.student,
            submitted_text="Test work",
            grade=5
        )

        self.client.login(username='teacher1', password='teacherpass123')

        response = self.client.get(reverse('grades_by_subject_per_class'))

        self.assertEqual(response.status_code, 200)

        data = response.context['data']
        self.assertIn("10-A", data)
        self.assertIn("Mathematics", data["10-A"])
        submissions_list = data["10-A"]["Mathematics"]
        self.assertEqual(len(submissions_list), 1)
        submission_data = submissions_list[0]
        self.assertEqual(submission_data['student'], 'student1')
        self.assertEqual(submission_data['grade'], 5)