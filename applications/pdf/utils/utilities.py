from math import ceil


def paginate(collection, query, page, page_size, sort_by=None, order=None):
    # Calculate how many documents to skip
    skip_count = (page - 1) * page_size

    # Sorting logic (sort_by and order: 1 for ascending, -1 for descending)
    sort_criteria = None
    if sort_by:
        sort_criteria = [(sort_by, 1 if order == "asc" else -1)]

    # Query MongoDB with the filter, skip, and limit
    cursor = collection.find(query).skip(skip_count).limit(page_size)

    # Apply sorting if specified
    if sort_criteria:
        cursor = cursor.sort(sort_criteria)

    files = list(cursor)

    # Get total number of documents for calculating total pages
    total_files = collection.count_documents(query)
    total_pages = ceil(total_files / page_size)

    return files, total_files, total_pages
