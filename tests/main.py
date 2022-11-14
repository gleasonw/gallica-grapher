# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math

def solution(area):
    result = []
    if not area:
        return result

    def recurse_solution(area):
        if math.sqrt(area) - int(math.sqrt(area)) == 0:
            result.append(area)
            return
        largestSquare = int(math.sqrt(area))
        result.append(largestSquare * largestSquare)
        recurse_solution(area - (largestSquare * largestSquare))

    recurse_solution(area)
    return result


if __name__ == '__main__':
    print(solution(12))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
