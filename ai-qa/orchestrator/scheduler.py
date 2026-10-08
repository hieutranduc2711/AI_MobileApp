class Scheduler:
    def __init__(self, test_cases):
        self.test_cases = test_cases

    def order_execution(self):
        # Có thể sắp xếp theo độ ưu tiên: Critical -> High -> Medium
        return self.test_cases
