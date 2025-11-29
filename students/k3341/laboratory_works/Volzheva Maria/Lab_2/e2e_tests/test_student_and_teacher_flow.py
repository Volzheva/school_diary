import sys
import os
import django
import importlib
import re
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_2.settings')
django.setup()

models = importlib.import_module('class.models')
from django.contrib.auth import get_user_model
User = get_user_model()

BASE_URL = "http://127.0.0.1:8000"
STUDENT_USERNAME = "e2e_student"
STUDENT_PASSWORD = "secure_password_123"
TEACHER_USERNAME = "e2e_teacher"
TEACHER_PASSWORD = "secure_password_123"


def setup_test_data():
    models.Submission.objects.filter(
        homework__description="Solve E2E test problem"
    ).delete()
    models.Homework.objects.filter(description="Solve E2E test problem").delete()
    models.Subject.objects.filter(name="E2E Testing").delete()
    User.objects.filter(username__in=[STUDENT_USERNAME, TEACHER_USERNAME]).delete()
    models.Class.objects.filter(name="10-E2E").delete()

    test_class = models.Class.objects.create(name="10-E2E")
    student = User.objects.create_user(
        username=STUDENT_USERNAME,
        password=STUDENT_PASSWORD,
        role="student",
        student_class=test_class
    )
    teacher = User.objects.create_user(
        username=TEACHER_USERNAME,
        password=TEACHER_PASSWORD,
        role="teacher"
    )
    subject = models.Subject.objects.create(name="E2E Testing")
    subject.teachers.add(teacher)
    homework = models.Homework.objects.create(
        subject=subject,
        date_from="2025-11-30",
        date_to="2025-12-01",
        description="Solve E2E test problem"
    )
    homework.classes.add(test_class)


def test_student_submission_flow():
    homework_id = models.Homework.objects.get(description="Solve E2E test problem").id

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"{BASE_URL}/login/")
        page.fill('input[name="username"]', STUDENT_USERNAME)
        page.fill('input[name="password"]', STUDENT_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_url(f"{BASE_URL}/home/")

        submission_url = f"{BASE_URL}/homework/{homework_id}/new_submission/"
        page.goto(submission_url)
        page.wait_for_url(f"{BASE_URL}/homework/{homework_id}/new_submission/")

        page.fill('input[name="submitted_text"]', "My E2E test solution")
        page.click('button:has-text("Отправить моё дз")')
        page.wait_for_url(f"{BASE_URL}/home/")

        assert page.is_visible('text=Solve E2E test problem'), "Сданное ДЗ не отображается в списке"

        browser.close()


def test_teacher_grade_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"{BASE_URL}/login/")
        page.fill('input[name="username"]', TEACHER_USERNAME)
        page.fill('input[name="password"]', TEACHER_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_url(f"{BASE_URL}/home/")

        page.click('a[href="/submissions/without-grades/"]')
        page.wait_for_url(f"{BASE_URL}/submissions/without-grades/")

        page.click('a:has-text("Оценить")')
        page.wait_for_url(re.compile(r"/submissions/grade/\d+/"))

        page.fill('input[name="grade"]', "5")
        page.click('button:has-text("Сохранить оценку")')
        page.wait_for_url(f"{BASE_URL}/submissions/without-grades/")

        try:
            page.wait_for_selector('text=Solve E2E test problem', timeout=2000)
            assert False, "Работа всё ещё отображается как неоценнённая"
        except:
            pass

        browser.close()


if __name__ == "__main__":
    print("Подготовка тестовых данных...")
    setup_test_data()

    print("Запуск E2E тестов...")
    test_student_submission_flow()
    print("test_student_submission_flow пройден")

    test_teacher_grade_flow()
    print("test_teacher_grade_flow пройден")

    print("Все E2E тесты успешно завершены!")