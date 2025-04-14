from locust import HttpUser, task, between

class PerformanceTest(HttpUser):
    wait_time = between(1, 5)  # Users wait 1-5 seconds between requests

    @task
    def load_homepage(self):
        self.client.get("/")  # Replace with the endpoint you want to test

    @task
    def load_dashboard(self):
        self.client.get("/dashboard")  # Example: Testing dashboard load time

