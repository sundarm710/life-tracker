import yaml
from datetime import datetime, timedelta

class BudgetManager:
    def __init__(self, config_path='config/time-goals.yaml'):
        self.config_path = config_path
        self.budgets = self.load_budgets()

    def load_budgets(self):
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)['budgets']

    def get_budget(self, name):
        return next((budget for budget in self.budgets if budget['name'] == name), None)

    def get_all_budgets(self):
        return self.budgets

    def add_budget(self, budget):
        self.budgets.append(budget)
        self.save_budgets()

    def update_budget(self, name, new_data):
        budget = self.get_budget(name)
        if budget:
            budget.update(new_data)
            self.save_budgets()

    def delete_budget(self, name):
        self.budgets = [b for b in self.budgets if b['name'] != name]
        self.save_budgets()

    def save_budgets(self):
        with open(self.config_path, 'w') as file:
            yaml.dump({'budgets': self.budgets}, file)

    def get_active_budgets(self, date=None):
        if date is None:
            date = datetime.now().date()
        return [
            budget for budget in self.budgets
            if datetime.strptime(budget['start_date'], "%Y-%m-%d").date() <= date <= datetime.strptime(budget['end_date'], "%Y-%m-%d").date()
        ]

    def calculate_progress(self, name, actual_value, date=None):
        budget = self.get_budget(name)
        if not budget:
            return None

        if date is None:
            date = datetime.now().date()

        start_date = datetime.strptime(budget['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(budget['end_date'], "%Y-%m-%d").date()

        if date < start_date or date > end_date:
            return None

        total_days = (end_date - start_date).days + 1
        days_passed = (date - start_date).days + 1

        print(f"Total days: {total_days}, Days passed: {days_passed}")

        if not budget.get('include_weekends', True):
            total_days = sum(1 for d in range(total_days) if (start_date + timedelta(d)).weekday() < 5)
            days_passed = sum(1 for d in range(days_passed) if (start_date + timedelta(d)).weekday() < 5)

        expected_progress = (budget['target'] / total_days) * days_passed
        actual_progress = actual_value

        if budget['direction'] == 'less':
            progress_percentage = (expected_progress / actual_progress) * 100 if actual_progress > 0 else 100
        else:
            progress_percentage = (actual_progress / expected_progress) * 100 if expected_progress > 0 else 0

        return {
            'name': budget['name'],
            'target': budget['target'],
            'actual': actual_progress,
            'expected': expected_progress,
            'progress_percentage': progress_percentage,
            'is_on_track': (progress_percentage >= 100) if budget['direction'] == 'greater' else (progress_percentage <= 100)
        }

# Usage example
if __name__ == "__main__":
    manager = BudgetManager()
    # print(manager.get_all_budgets())
    print(manager.get_active_budgets())
    print(manager.calculate_progress("Chess Sep 2024", 10)) #  datetime(2024, 9, 15).date()