import time

def merge_sort(data, key):
    if len(data) <= 1:
        return data
    mid = len(data) // 2
    left = merge_sort(data[:mid], key)
    right = merge_sort(data[mid:], key)
    return _merge(left, right, key)

def _merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if str(left[i][key]) <= str(right[j][key]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def bubble_sort(data, key):
    data = data.copy()
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            if str(data[j][key]) > str(data[j + 1][key]):
                data[j], data[j + 1] = data[j + 1], data[j]
    return data

def compare_sorts(data, key):
    data1 = data.copy()
    data2 = data.copy()

    start = time.perf_counter()
    merge_result = merge_sort(data1, key)
    merge_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    bubble_result = bubble_sort(data2, key)
    bubble_time = (time.perf_counter() - start) * 1000

    return {
        "merge_sort_ms": round(merge_time, 4),
        "bubble_sort_ms": round(bubble_time, 4),
        "faster": "Merge Sort" if merge_time < bubble_time else "Bubble Sort",
        "merge_result": merge_result,
        "bubble_result": bubble_result
    }