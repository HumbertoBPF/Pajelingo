import random

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

from languageschool.models import AppUser, Game, Language, Score


@pytest.mark.django_db
def test_mobile_test_setup():
    """
    Tests the setup step for mobile tests.
    """
    call_command("mobile_tests", "--setup")
    # Verify if all test users were created
    assert User.objects.filter(email="test-android@test.com", username="test-android").exists()
    assert User.objects.filter(email="update-test-android0@test.com", username="update-test-android0").exists()
    assert User.objects.filter(email="update-test-android1@test.com", username="update-test-android1").exists()
    assert User.objects.filter(email="update-test-android2@test.com", username="update-test-android2").exists()
    assert User.objects.filter(email="update-test-android3@test.com", username="update-test-android3").exists()
    assert User.objects.filter(email="update-test-android4@test.com", username="update-test-android4").exists()
    assert User.objects.filter(email="test-android-delete@test.com", username="test-android-delete").exists()

    assert AppUser.objects.filter(user__email="test-android@test.com", user__username="test-android").exists()
    assert AppUser.objects.filter(user__email="update-test-android0@test.com",
                                  user__username="update-test-android0").exists()
    assert AppUser.objects.filter(user__email="update-test-android1@test.com",
                                  user__username="update-test-android1").exists()
    assert AppUser.objects.filter(user__email="update-test-android2@test.com",
                                  user__username="update-test-android2").exists()
    assert AppUser.objects.filter(user__email="update-test-android3@test.com",
                                  user__username="update-test-android3").exists()
    assert AppUser.objects.filter(user__email="update-test-android4@test.com",
                                  user__username="update-test-android4").exists()
    assert AppUser.objects.filter(user__email="test-android-delete@test.com",
                                  user__username="test-android-delete").exists()

    test_user = User.objects.filter(email="test-android@test.com", username="test-android").first()

    for game in Game.objects.all():
        for language in Language.objects.all():
            assert Score.objects.filter(user=test_user, game=game, language=language).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "has_new_test_android", [True, False]
)
def test_mobile_test_teardown(account, has_new_test_android):
    """
    Tests the teardown step for mobile tests.
    """
    accounts = account(n=random.randint(5, 10))

    test_mobile_test_setup()
    # Create, if necessary, the new-test-android user
    if has_new_test_android:
        User.objects.create_user(email="new-test-android@test.com", username="new-test-android")
        assert User.objects.filter(email="new-test-android@test.com", username="new-test-android").exists()
        assert AppUser.objects.filter(user__email="new-test-android@test.com",
                                      user__username="new-test-android").exists()

    user_0 = User.objects.filter(email="test-android@test.com", username="test-android").first()
    user_1 = User.objects.filter(email="update-test-android0@test.com", username="update-test-android0").first()
    user_2 = User.objects.filter(email="update-test-android1@test.com", username="update-test-android1").first()
    user_3 = User.objects.filter(email="update-test-android2@test.com", username="update-test-android2").first()
    user_4 = User.objects.filter(email="update-test-android3@test.com", username="update-test-android3").first()
    user_5 = User.objects.filter(email="update-test-android4@test.com", username="update-test-android4").first()
    user_6 = User.objects.filter(email="test-android-delete@test.com", username="test-android-delete").first()

    call_command("mobile_tests", "--teardown", user_0.id, user_1.id, user_2.id, user_3.id, user_4.id, user_5.id, user_6.id)
    # Verify that only test users were deleted
    assert User.objects.count() == len(accounts)
    assert not User.objects.filter(email="test-android@test.com", username="test-android").exists()
    assert not User.objects.filter(email="update-test-android0@test.com", username="update-test-android0").exists()
    assert not User.objects.filter(email="update-test-android1@test.com", username="update-test-android1").exists()
    assert not User.objects.filter(email="update-test-android2@test.com", username="update-test-android2").exists()
    assert not User.objects.filter(email="update-test-android3@test.com", username="update-test-android3").exists()
    assert not User.objects.filter(email="update-test-android4@test.com", username="update-test-android4").exists()
    assert not User.objects.filter(email="test-android-delete@test.com", username="test-android-delete").exists()
    assert not User.objects.filter(email="new-test-android@test.com", username="new-test-android").exists()

    assert not AppUser.objects.filter(user__email="test-android@test.com", user__username="test-android").exists()
    assert not AppUser.objects.filter(user__email="update-test-android0@test.com",
                                  user__username="update-test-android0").exists()
    assert not AppUser.objects.filter(user__email="update-test-android1@test.com",
                                  user__username="update-test-android1").exists()
    assert not AppUser.objects.filter(user__email="update-test-android2@test.com",
                                  user__username="update-test-android2").exists()
    assert not AppUser.objects.filter(user__email="update-test-android3@test.com",
                                  user__username="update-test-android3").exists()
    assert not AppUser.objects.filter(user__email="update-test-android4@test.com",
                                  user__username="update-test-android4").exists()
    assert not AppUser.objects.filter(user__email="test-android-delete@test.com",
                                  user__username="test-android-delete").exists()

    assert not Score.objects.filter(user__email="test-android@test.com", user__username="test-android").exists()