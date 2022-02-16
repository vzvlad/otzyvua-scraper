from tqdm import tqdm
from langdetect import detect

from otzyvua_review_scrapler import reviews


def append_without_duplicates(source, storage_path):
    get_storage_path = storage_path if callable(storage_path) else lambda x: storage_path

    storage_image = {}

    non_stored_counter = 0
    for source_counter, item in enumerate(source):
        item_storagePath = get_storage_path(item)

        if item_storagePath not in storage_image:
            with open(item_storagePath, 'r+', encoding='utf-8') as inp:
                storage_image[item_storagePath] = [item.rstrip() for item in inp]

        if item not in storage_image[item_storagePath]:
            non_stored_counter += 1
            with open(item_storagePath, 'a+', encoding='utf-8') as out:
                out.write(f"{item}\n")
            storage_image[item_storagePath].append(item)

    total_stored = sum(len(items) for items in storage_image.values())
    print(f"{total_stored} = "
          f"{total_stored - non_stored_counter} already stored + "
          f"{non_stored_counter} added")


def filename_by_review(review):
    try:
        filename = f"reviews/{detect(review)}.txt"
        with open(filename, 'a+'):
            pass
        return filename
    except Exception:
        return "reviews/unknown.txt"


def load_reviews(urls_file='review-urls.txt', start=None, end=None):
    with open(urls_file) as inp:
        review_urls = [line.rstrip() for line in inp]

    start = start or 0
    if end is not None:
        review_urls = review_urls[start:max(end, len(review_urls))]
    else:
        review_urls = review_urls[start:]

    append_without_duplicates(
        tqdm(reviews(review_urls), total=end-start, position=0, leave=True),
        filename_by_review
    )
