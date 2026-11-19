import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


class QuestionIndexViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        time = timezone.now()
        Question.objects.create(
            question_text="Past question 1.",
            pub_date=time - datetime.timedelta(days=5),
        )
        Question.objects.create(
            question_text="Past question 2.",
            pub_date=time - datetime.timedelta(days=5, seconds=1),
        )
        Question.objects.create(
            question_text="Future question.",
            pub_date=time + datetime.timedelta(days=5),
        )

    def test_no_questions(self):
        Question.objects.all().delete()
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            ["Past question 1.", "Past question 2."],
            transform=str,
        )

    def test_future_question(self):
        response = self.client.get(reverse("polls:index"))
        self.assertNotContains(response, "Future question.")

    def test_future_and_past_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Past question 1.")
        self.assertContains(response, "Past question 2.")
        self.assertNotContains(response, "Future question.")

    def test_two_past_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            ["Past question 1.", "Past question 2."],
            transform=str,
        )


class QuestionDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.past_question = Question.objects.create(
            question_text="Past question.",
            pub_date=timezone.now() - datetime.timedelta(days=5),
        )
        cls.future_question = Question.objects.create(
            question_text="Future question.",
            pub_date=timezone.now() + datetime.timedelta(days=5),
        )

    def test_future_question(self):
        response = self.client.get(
            reverse("polls:detail", args=(self.future_question.pk,))
        )
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        response = self.client.get(
            reverse("polls:detail", args=(self.past_question.pk,))
        )
        self.assertContains(response, "Past question.")


class QuestionResultsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.question = Question.objects.create(
            question_text="Question with results.",
            pub_date=timezone.now() - datetime.timedelta(days=1),
        )

    def test_results_page(self):
        response = self.client.get(
            reverse("polls:results", args=(self.question.pk,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Question with results.")
