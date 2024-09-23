from bson import ObjectId


def make_json_serializable(data):
    """
    Recursively convert MongoDB ObjectId instances in a dict or list into strings
    to make it JSON serializable.

    Args:
    - data (dict or list): The data structure (MongoDB document or list of documents).

    Returns:
    - dict or list: The modified data structure with ObjectId instances converted to strings.
    """

    if isinstance(data, dict):
        # If it's a dict, iterate through its keys
        for key, value in data.items():
            if isinstance(value, ObjectId):
                # Convert ObjectId to string
                data[key] = str(value)
            elif isinstance(value, (dict, list)):
                # Recursively process nested dicts or lists
                data[key] = make_json_serializable(value)

    elif isinstance(data, list):
        # If it's a list, iterate through each element
        for i in range(len(data)):
            if isinstance(data[i], ObjectId):
                # Convert ObjectId to string
                data[i] = str(data[i])
            elif isinstance(data[i], (dict, list)):
                # Recursively process nested dicts or lists
                data[i] = make_json_serializable(data[i])

    return data
