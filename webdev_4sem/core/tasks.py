from django.db.models import Avg

from celery import shared_task

from core.models import Driver


@shared_task
def recalculate_driver_ratings() -> dict[str, int]:
    """
    Пересчитывает рейтинги водителей по средним оценкам отзывов.

    Args:
        None: Задача не принимает аргументы.
    Returns:
        dict[str, int]: Количество проверенных и обновлённых водителей.
    """
    checked_count = 0
    updated_count = 0

    drivers = Driver.objects.annotate(
        average_review_rating=Avg('order__review__rating'),
    )

    for driver in drivers:
        checked_count += 1
        average_rating = driver.average_review_rating

        if average_rating is None:
            continue

        rounded_rating = round(float(average_rating), 2)

        if driver.rating != rounded_rating:
            driver.rating = rounded_rating
            driver.save(update_fields=['rating'])
            updated_count += 1

    return {
        'checked_count': checked_count,
        'updated_count': updated_count,
    }
